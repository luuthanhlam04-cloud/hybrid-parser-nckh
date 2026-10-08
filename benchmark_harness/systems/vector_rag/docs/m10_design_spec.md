# M10: Graph Retrieval Layer (Text-to-Cypher & Graph Traversal) - Design Spec

## 1. Mục Tiêu (Goal)
Tầng M10 chịu trách nhiệm nhận câu hỏi từ người dùng bằng ngôn ngữ tự nhiên (Vd: "Việt kiều có được nhận chuyển nhượng đất khu công nghiệp không?"), tìm kiếm các thông tin pháp lý liên quan trong Neo4j UKG, và giao cho LLM sinh câu trả lời. 

Để phục vụ nghiên cứu, M10 sẽ được thiết kế với **2 chế độ truy xuất (Modes)** chạy song song nhằm chứng minh sức mạnh của mô hình `NormAssertion`.

---

## 2. Luồng Thực Thi 5 Bước (The 5-Step Pipeline)

### Bước 1: Anchor Search (Tìm kiếm Neo bằng Vector)
- **Input:** Câu hỏi người dùng (Query).
- **Process:** 
  1. Embed câu hỏi thành vector (1024-D / 896-D).
  2. Bắn lệnh `db.index.vector.queryNodes` vào Vector Index của Neo4j.
  3. Lấy ra Top-K `PhysicalNode` (các Điều, Khoản, Điểm) có nội dung gần nghĩa nhất.
- **Output:** Mảng ID của các `PhysicalNode` (Anchor Nodes).

### Bước 2: Semantic Traversal (Duyệt Đồ Thị Ngữ Nghĩa)
Từ các Anchor Nodes, truy xuất thông tin ngữ nghĩa. Đây là bước phân nhánh để thi đấu (Ablation Study):

#### 🔴 Mode B: Simple Subgraph Retrieval (Baseline k-hop)
- Coi đồ thị như RAG thông thường. 
- Mở rộng $K$-hop từ Anchor Node để lấy mọi Node xung quanh mà **không quan tâm** đến logic `modality` (ALLOW/PROHIBIT) hay tổ chức của `NormAssertion`.

#### 🟢 Mode A: NormAssertion-Aware Retrieval (Proposed)
- Viết Cypher thông minh khai thác triệt để cấu trúc M8.
- Nhờ cạnh `MENTIONS` trỏ trực tiếp đến `LEGAL_SUBJECT`, `LEGAL_ACTION`, `GLOBAL_NORM`, hệ thống sẽ:
  1. Nhặt tất cả các `GLOBAL_NORM` liên quan.
  2. Lấy được `modality` (Quyền / Nghĩa vụ / Lệnh cấm).
  3. Lấy `HAS_CONDITION`, `HAS_EXCEPTION` để gom đủ điều kiện.
  4. Lấy `HAS_SUBJECT` để gom đúng chủ thể.
- Đảm bảo gom **trọn vẹn một quy phạm pháp lý (Norm)** không thừa, không thiếu.

### Bước 3: Context Assembly (Lắp ráp Ngữ cảnh)
- Biến các kết quả JSON từ Bước 2 thành một chuỗi văn bản (String) dễ hiểu cho LLM.
- **Mode A** sẽ có format rõ ràng: `Quy tắc 1: Chủ thể [X] bị CẤM thực hiện [Y] với Điều kiện [Z] (Căn cứ Khoản 1 Điều 2)`.

### Bước 4: LLM Generation (Sinh Câu Trả Lời)
- Bơm Context (từ Mode A hoặc Mode B) và Câu hỏi vào System Prompt của GPT-4o.
- Ép mô hình chỉ được phép trả lời dựa trên Context (Strict Grounding).

### Bước 5: Định tuyến sang M11 (Evaluation)
- Câu trả lời của hệ thống sẽ được lưu lại để M11 (LLM-as-a-Judge) dùng RAGAS metric chấm điểm (Faithfulness, Answer Relevance, Legal Accuracy).

---

## 3. Bản Nháp Cypher (Draft) cho Mode A
```cypher
// Bắt đầu từ Anchor Node
MATCH (p:UKG_NODE {id: $anchor_id})-[:MENTIONS]->(norm:GLOBAL_NORM)
// Khai phá trọn vẹn Quy phạm
OPTIONAL MATCH (norm)-[:HAS_SUBJECT]->(subj:SemanticEntity)
OPTIONAL MATCH (norm)-[:HAS_ACTION]->(act:SemanticEntity)
OPTIONAL MATCH (norm)-[:HAS_CONDITION]->(cond:SemanticEntity)
RETURN norm.modality AS modality, 
       collect(subj.search_text) AS subjects, 
       collect(act.search_text) AS actions, 
       collect(cond.search_text) AS conditions
```
