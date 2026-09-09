# -*- coding: utf-8 -*-
from typing import Dict, Any, Optional

SYSTEM_PROMPT = """Bạn là một chuyên gia Hệ thống Thông tin Pháp lý (Legal Informatics Expert). Nhiệm vụ của bạn là bóc tách Thực thể và Quan hệ thành JSON.

[TIÊU CHUẨN BÓC TÁCH BẮT BUỘC - CRITICAL]
1. NGUYÊN TẮC "FOUR CORNERS RULE" (Chống rò rỉ ngữ cảnh): 
   - Phần [BỐI CẢNH PHÂN CẤP] CHỈ dùng để bạn hiểu ngữ nghĩa đại từ (VD: "Luật này", "Khoản này"). 
   - Bạn CHỈ ĐƯỢC PHÉP tạo thực thể từ các từ ngữ xuất hiện trực tiếp bên trong đoạn [NỘI DUNG CẦN TRÍCH XUẤT (NODE HIỆN TẠI)]. Tuyệt đối không lấy danh từ từ Node cha bỏ vào Node con.
   - Phải trích xuất NGUYÊN VĂN. Từ ngữ không được thay đổi, không được tóm tắt. Khớp nối chuỗi phải chính xác 100%.
2. TÍNH NGUYÊN TỬ CỦA THỰC THỂ (Entity Atomicity):
   - KHÔNG gộp cụm. Nếu câu ghi "Tổ chức kinh tế, cá nhân", hãy bóc thành 2 thực thể SUBJECT riêng biệt: "Tổ chức kinh tế" và "cá nhân".
3. NGUYÊN TẮC HOHFELD CHO QUAN HỆ (Normative Semantics):
   - Dùng "ALLOW" nếu pháp luật quy định "Được phép", "Có quyền".
   - Dùng "REQUIRE" nếu pháp luật quy định "Phải", "Có nghĩa vụ", "Bắt buộc".
   - Dùng "PROHIBIT" nếu pháp luật quy định "Không được", "Nghiêm cấm".
   - Dùng "HAS_CONDITION" nếu đi kèm điều kiện; "HAS_EXCEPTION" nếu có ngoại lệ; "REFERENCE_TO" nếu có dẫn chiếu; "APPLY_TO" nếu quy định đối tượng áp dụng.
4. TRUY VẾT BẰNG CHỨNG (Strict Grounding):
   - Trường `evidence` BẮT BUỘC PHẢI CÓ cho cả thực thể và quan hệ. Nó là một substring copy/paste chính xác từng chữ cái từ nội dung văn bản gốc của Node hiện tại, TUYỆT ĐỐI KHÔNG ĐỂ RỖNG.
5. CẤP MÃ ĐỊNH DANH CỤC BỘ (Unique Local ID & Referential Integrity):
   - Mỗi thực thể phải có một id duy nhất trong node (VD: e1, e2, e3). TUYỆT ĐỐI KHÔNG sinh trùng lặp id.
   - Các trường `source` và `target` của relation BẮT BUỘC phải trỏ đúng vào `id` của entity đã khai báo trong mảng entities.
6. XỬ LÝ RỖNG (Zero-Hallucination):
   - Nếu câu chỉ là định nghĩa thủ tục hành chính chung chung hoặc không chứa quy phạm pháp lý rõ ràng, không sinh thực thể. Trả về mảng rỗng []. KHÔNG BỊA ĐẶT.
"""

class PromptBuilder:
    def __init__(self, physical_graph: Dict[str, Any]):
        """
        Khởi tạo PromptBuilder với Đồ thị vật lý (Physical Graph).
        Dựng từ điển lookup theo ID để dễ dàng tra ngược node cha.
        """
        self.node_lookup: Dict[str, Dict[str, Any]] = {}
        nodes = physical_graph.get("nodes", [])
        for node in nodes:
            node_id = node.get("id")
            if node_id:
                self.node_lookup[node_id] = node
                
        # Dựng lookup parent mapping từ edges (nếu physical_graph lưu BELONG_TO)
        # hoặc nếu node có sẵn thuộc tính parent_id trong properties, ta sẽ lấy từ đó.
        self.parent_map: Dict[str, str] = {}
        edges = physical_graph.get("edges", [])
        for edge in edges:
            if edge.get("type") == "BELONG_TO":
                source = edge.get("source")
                target = edge.get("target")
                if source and target:
                    self.parent_map[source] = target

    def _get_parent_id(self, node_id: str) -> Optional[str]:
        """
        Lấy parent_id của một node_id.
        Ưu tiên lấy từ edges (BELONG_TO), nếu không có thì thử lookup trong properties.
        """
        if node_id in self.parent_map:
            return self.parent_map[node_id]
            
        node = self.node_lookup.get(node_id)
        if node:
            props = node.get("properties", {})
            return props.get("parent_id")
            
        return None

    def build_hierarchical_context(self, node_id: str) -> str:
        """
        Tra ngược an toàn để lấy bối cảnh phân cấp (từ node hiện tại lên cấp cao nhất như ARTICLE).
        """
        if node_id not in self.node_lookup:
            return ""
            
        context_lines = []
        current_id = node_id
        
        # Ngăn chặn vòng lặp vô hạn bằng mảng visited
        visited = set()
        
        # Traverse lên các node cha
        while current_id and current_id not in visited:
            visited.add(current_id)
            node = self.node_lookup.get(current_id)
            if not node:
                break
                
            labels = node.get("labels", [])
            node_type = labels[1] if len(labels) > 1 else "UNKNOWN"
            props = node.get("properties", {})
            
            # Không lấy title hoặc text trống nếu không có
            text = props.get("text")
            title = props.get("title")
            
            content = ""
            if title and text:
                content = f"{title} - {text}"
            elif text:
                content = text
            elif title:
                content = title
                
            if current_id != node_id and content:
                context_lines.append(f"- {node_type}: {content}")
                
            # Stop tra ngược khi tới cấp ARTICLE
            if node_type == "ARTICLE":
                break
                
            current_id = self._get_parent_id(current_id)
            
        # context_lines lưu từ con lên cha, nên cần đảo ngược lại
        context_lines.reverse()
        return "\n".join(context_lines)

    def build_prompt(self, target_node_id: str) -> str:
        """
        Tạo prompt hoàn chỉnh cho một node nhất định.
        """
        target_node = self.node_lookup.get(target_node_id)
        if not target_node:
            return "Node không tồn tại trong Physical Graph."
            
        labels = target_node.get("labels", [])
        node_type = labels[1] if len(labels) > 1 else "UNKNOWN"
        props = target_node.get("properties", {})
        
        text = props.get("text")
        title = props.get("title")
        node_content = text if text else title
        
        context_str = self.build_hierarchical_context(target_node_id)
        
        prompt = "[BỐI CẢNH PHÂN CẤP]\n"
        if context_str.strip():
            prompt += context_str + "\n"
        else:
            prompt += "(Không có bối cảnh cha)\n"
            
        prompt += "\n[NỘI DUNG CẦN TRÍCH XUẤT (NODE HIỆN TẠI)]\n"
        prompt += f"- {node_type}: {node_content}"
        
        return prompt
