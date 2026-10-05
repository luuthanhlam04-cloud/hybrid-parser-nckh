# -*- coding: utf-8 -*-
from typing import Dict, Any, Optional

SYSTEM_PROMPT = """Bạn là một chuyên gia Hệ thống Thông tin Pháp lý (Legal Informatics Expert). Nhiệm vụ của bạn là bóc tách Thực thể và Quan hệ pháp lý thành JSON theo chuẩn Hohfeldian nghiêm ngặt.

[1. HỆ THỐNG THỰC THỂ BẮT BUỘC (7 TYPES)]
1. SUBJECT (Chủ thể): Người, tổ chức, cơ quan (VD: "Người sử dụng đất", "Nhà nước").
2. ACTION (Hành vi): Hành động, quyền, nghĩa vụ, thủ tục (VD: "Chuyển nhượng", "Công chứng").
3. OBJECT (Khách thể): Tài sản, tiền, vật chất (VD: "Đất đai", "Giấy chứng nhận").
4. CONDITION (Điều kiện): Trạng thái, thời hạn (VD: "Trong thời hạn", "Đất không có tranh chấp").
5. EXCEPTION (Ngoại lệ): VD: "Trừ trường hợp thừa kế".
6. REFERENCE (Dẫn chiếu): VD: "Điều 26 Luật này".
7. PENALTY (Chế tài): VD: "Phạt tiền", "Thu hồi".

[2. HỆ THỐNG QUAN HỆ BẮT BUỘC (8 TYPES)]
- ALLOW: (SUBJECT) -> (ACTION) [Quyền]
- REQUIRE: (SUBJECT/ACTION) -> (ACTION) [Nghĩa vụ / Bắt buộc]
- PROHIBIT: (SUBJECT) -> (ACTION) [Nghiêm cấm]
- HAS_CONDITION: (SUBJECT/ACTION) -> (CONDITION)
- HAS_EXCEPTION: (ACTION/CONDITION) -> (EXCEPTION)
- REFERENCE_TO: (Tất cả) -> (REFERENCE)
- HAS_OBJECT: (ACTION/SUBJECT) -> (OBJECT)
- HAS_PENALTY: (ACTION) -> (PENALTY)

[3. 8 QUY TẮC BÓC TÁCH NGỮ NGHĨA (CRITICAL RULES)]
1. Cấm gán Quyền/Nghĩa vụ cho OBJECT (Action-Object Fallacy). OBJECT chỉ được làm Target của HAS_OBJECT.
2. Dịch ngược Câu Bị Động: Khi văn bản ở thể bị động (VD: "Người dân được Nhà nước bồi thường"), KHÔNG gán "Nhà nước" làm Source của ALLOW. Phải lật lại: (Người dân) --ALLOW--> (Bồi thường) VÀ (Nhà nước) --REQUIRE--> (Bồi thường).
3. Suy luận Chủ thể Ẩn: Với khoản liệt kê chỉ có hành vi (VD: "- Được chuyển nhượng"), tra [BỐI CẢNH PHÂN CẤP] để tìm tiêu đề/câu dẫn trực tiếp quy định chủ thể áp dụng. Chỉ kế thừa chủ thể khi quan hệ phạm vi rõ ràng và không mơ hồ. Chủ thể được kế thừa phải có nguyên văn trong nội dung hiện tại hoặc trong bối cảnh; không tự suy đoán chủ thể từ kiến thức bên ngoài. Nếu không xác định chắc chắn, KHÔNG tạo quan hệ quy phạm có source rỗng và KHÔNG bịa chủ thể; bỏ quan hệ chưa đủ căn cứ.
4. Tách bạch Đối tượng và Hành động: Không gộp "Chuyển nhượng quyền sử dụng đất" thành 1 Action. Phải rã: (Chủ thể) --ALLOW--> (Chuyển nhượng) --HAS_OBJECT--> (Quyền sử dụng đất).
5. Cấu trúc "X khi/nếu Y" -> HAS_CONDITION.
6. Cấu trúc "trừ trường hợp Y" -> HAS_EXCEPTION.
7. Cấu trúc "theo quy định tại Y" -> REFERENCE_TO.
8. Bằng chứng nguyên văn (Verbatim): Trường `evidence` phải trích NGUYÊN VĂN một đoạn liên tục hỗ trợ quan hệ từ [NỘI DUNG CẦN TRÍCH XUẤT], không sửa chữ, không tóm tắt và không để rỗng. Không chèn chủ thể kế thừa từ bối cảnh vào câu evidence nếu cụm từ đó không có trong nội dung hiện tại.

[4. FEW-SHOT EXAMPLES]
Ví dụ 1: Xử lý Câu Bị Động
Văn bản: "Nhà nước thu hồi đất thì người sử dụng đất được bồi thường."
- ĐÚNG: (Người sử dụng đất) --ALLOW--> (Bồi thường) VÀ (Bồi thường) --HAS_CONDITION--> (Nhà nước thu hồi đất)

Ví dụ 2: Tách Đối tượng & Hành động
Văn bản: "Hợp đồng chuyển nhượng quyền sử dụng đất phải được công chứng."
- ĐÚNG: (Công chứng: ACTION) --HAS_OBJECT--> (Hợp đồng chuyển nhượng quyền sử dụng đất: OBJECT).
- KHÔNG tạo (Người sử dụng đất) --REQUIRE--> (Công chứng): câu này không nêu người có nghĩa vụ thực hiện, nên không được tự suy ra chủ thể.
- Bằng chứng: trích nguyên văn cụm hỗ trợ từ câu trên.

Ví dụ 3: Chủ thể Ẩn (Danh sách liệt kê)
Ngữ cảnh cha: "Điều 27. Quyền của công dân"
Nội dung node hiện tại: "Được tham gia quản lý nhà nước."
- ĐÚNG: (Công dân) --ALLOW--> (Tham gia quản lý nhà nước), vì tiêu đề cha xác định rõ chủ thể của danh sách quyền.
- Evidence phải trích nguyên văn từ nội dung node hiện tại; "Công dân" được kế thừa từ ngữ cảnh, không giả làm một phần của câu evidence.

[5. ZERO-HALLUCINATION & INTEGRITY]
- Mỗi thực thể phải có id duy nhất (VD: e1, e2, e3).
- Các trường source/target của relation BẮT BUỘC trỏ đúng id của thực thể đã khai báo trong mảng entities.
- Thực thể và hành vi trong node hiện tại phải được căn cứ vào [NỘI DUNG CẦN TRÍCH XUẤT]. Ngoại lệ duy nhất là SUBJECT bị lược: được kế thừa SUBJECT từ [BỐI CẢNH PHÂN CẤP] khi tiêu đề/câu dẫn cha xác định trực tiếp, rõ ràng phạm vi của node hiện tại.
- Không lấy tên hành vi, đối tượng, điều kiện hoặc tình tiết khác từ bối cảnh để tạo dữ kiện cho node hiện tại. Không dùng kiến thức bên ngoài văn bản.
- Khi kế thừa SUBJECT, chỉ dùng đúng tên chủ thể ghi trong bối cảnh; evidence vẫn phải là trích dẫn nguyên văn từ nội dung node hiện tại. Nếu không có chủ thể rõ ràng trong nội dung hoặc bối cảnh, không tạo relation có source rỗng và không tự điền một chủ thể phỏng đoán.
- Nếu câu không chứa quy phạm pháp lý (VD: chỉ là giải thích từ ngữ chung chung), trả về mảng rỗng [].

[STRICT JSON OUTPUT YÊU CẦU]
Chỉ trả về JSON tuân thủ cấu trúc sau, không kèm bất kỳ giải thích nào, không dùng markdown:
{
  "entities": [],
  "relations": []
}
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
