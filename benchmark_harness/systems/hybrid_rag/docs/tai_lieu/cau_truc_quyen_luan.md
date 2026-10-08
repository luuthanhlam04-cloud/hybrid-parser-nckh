# CẤU TRÚC QUYỂN BÁO CÁO NCKH CHUẨN 5 CHƯƠNG (~100 TRANG) — KÈM CITATION MAP

**Đề tài:** Nghiên cứu và xây dựng hệ thống tiền xử lý dữ liệu lai (Hybrid Parser) nhằm tối ưu hóa chi phí và hiệu năng GraphRAG trong truy vấn văn bản quy chuẩn pháp lý Việt Nam.

---

## 📚 LEGEND — BẢNG MÃ TÀI LIỆU THAM KHẢO (31 TÀI LIỆU)

### Nhóm 1: Nền tảng RAG & GraphRAG (9 bài)
- **[RAG_ORIG]**: Lewis et al. (2020) — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (Khái niệm RAG gốc)
- **[RAG_SURV]**: Gao et al. (2023) — *RAG for Large Language Models: A Survey* (Tổng quan RAG hiện đại)
- **[HALLUC]**: Ji et al. (2023) — *Survey of Hallucination in Natural Language Generation* (Chứng minh RAG bị ảo giác)
- **[LOST_MID]**: Liu et al. (2023) — *Lost in the Middle: How LMs Use Long Contexts* (Nhược điểm chunking thô)
- **[FP7]**: Barnett et al. (2024) — *Seven Failure Points When Engineering a RAG System* (7 điểm nghẽn RAG)
- **[STRCHK]**: Yepes et al. (2024) — *Financial Report Chunking for Effective RAG* (Cắt theo cấu trúc vật lý)
- **[KG_SURV]**: Hogan et al. (2021) — *Knowledge Graphs* (Định nghĩa nền tảng KG)
- **[GRAG_SURV]**: Peng et al. (2024) — *Graph Retrieval-Augmented Generation: A Survey* (Tổng quan GraphRAG)
- **[GRAG]**: Edge et al. (2024) — *From Local to Global: A Graph RAG Approach* (MS GraphRAG, Baseline 3, bài toán chi phí)

### Nhóm 2: Legal Ontology & Legal KR (9 tài liệu)
- **[KRR_BOOK]**: Brachman & Levesque (2004) — *Knowledge Representation and Reasoning* (Giáo trình gốc KR, Phổ Ontology)
- **[HOHFELD]**: Hohfeld (1913) — *Some Fundamental Legal Conceptions...* (Lý luận phân loại quyền/nghĩa vụ pháp lý)
- **[LEGAL_AI]**: Ashley (2017) — *Artificial Intelligence and Legal Analytics* (Sách giáo khoa nền tảng AI trong Luật)
- **[FOLAW]**: Valente & Breuker (1994) — *A functional ontology of law* (Kiến trúc Legal Ontology kinh điển)
- **[LKIFC]**: Hoekstra et al. (2007) — *The LKIF Core Ontology of Basic Legal Concepts* (Chuẩn hóa khái niệm luật cơ bản)
- **[CASANOVAS]**: Casanovas et al. (2016) — *Semantic Web for the Legal Domain* (Nút thắt cổ chai xây dựng Ontology thủ công)
- **[ViLO]**: Nguyen et al. (2022) — *ViLO: A Core Ontology of Vietnamese Legal Documents* (Core Ontology cho pháp luật Việt Nam)
- **[LONTO]**: Pham et al. (2026) — *Ontology-Based KG Approach for Legal Queries* (Mô hình Ontology-KG Layered)
- **[VNKG]**: (2023) — *Constructing a KG for Vietnamese Legal Cases* (Bức tranh KG pháp lý VN)
- **[JST]**: *A practical approach to building legal KGs from legal texts* (Tiếng Việt) (Bức tranh KG pháp lý trong nước)

### Nhóm 3: Đánh Giá & Benchmark Luật Việt (6 bài)
- **[VLEGAL]**: Nguyen et al. (2024) — *VLegal-Bench: Vietnamese Legal Reasoning Benchmark* (Đặc thù phân cấp luật VN, cách làm dataset)
- **[VNLI]**: Phan et al. (2025) — *ViLegalNLI: NLI for Vietnamese Legal Texts* (Tính phức tạp của quy phạm điều kiện)
- **[LLM_JUDGE]**: Zheng et al. (2023) — *Judging LLM-as-a-Judge with MT-Bench* (Phương pháp luận dùng LLM làm giám khảo)
- **[RAGAS]**: Es et al. (2023) — *Ragas: Automated Evaluation of Retrieval Augmented Generation* (Context Precision/Recall, Faithfulness)
- **[RGB]**: Chen et al. (2023) — *Benchmarking LLMs in RAG (RGB Benchmark)* (Noise robustness, information integration)
- **[IR_METR]**: Manning et al. (2008) — *Introduction to Information Retrieval* (Sách gốc F1, Precision, Recall)

### Nhóm 4: Technical & Routing (7 bài)
- **[GROUTER]**: GraphRAG-Router (2026) — *Cost-Efficient Routing over GraphRAGs* (Phương pháp định tuyến tiết kiệm chi phí)
- **[CYPHER]**: Francis et al. (2018) — *Cypher: An Evolving Query Language...* (Ngôn ngữ truy vấn Cypher)
- **[QWEN]**: Qwen Team (2024) — *Qwen2.5 Technical Report* (Cơ sở lý thuyết cho Embedding ở M5)
- **[KBQA]**: Lan et al. (2021) — *A Survey on Complex Knowledge Base QA* (Nền tảng cho truy xuất đồ thị ở M10)
- **[DOC_NEO]**: Neo4j (2024) — *Neo4j Graph Database Documentation* (Kỹ thuật Ingestion: Idempotent, MERGE)
- **[DOC_OAI]**: OpenAI (2024) — *Structured Outputs Documentation* (Kỹ thuật ép LLM nhả JSON Schema 100%)
- **[DOC_SHA]**: W3C (2017) — *SHACL Specification* (Chuẩn Validation đồ thị)

---

## CHƯƠNG 1: GIỚI THIỆU NGHIÊN CỨU (~8 TRANG)

### 1.1. Đặt vấn đề (Tính cấp thiết)
- **Đặc thù văn bản luật Việt Nam:** Cấu trúc phân cấp khắt khe (Chương -> Mục -> Điều -> Khoản -> Điểm) và hệ thống dẫn chiếu chéo dày đặc. *(Cite: [VLEGAL], [VNLI])*
- **Hạn chế của Naive Chunking:** Phá vỡ ranh giới phân cấp vật lý, làm đứt gãy liên kết ngữ nghĩa, dẫn đến mất context và ảo giác pháp lý. *(Cite: [RAG_ORIG], [FP7], [LOST_MID])*
- **Giải pháp bóc tách cấu trúc vật lý:** Khắc phục hạn chế của việc cắt token tĩnh. *(Cite: [STRCHK])*
- **Bài toán chi phí của Microsoft GraphRAG:** Chi phí indexing khổng lồ khi sử dụng LLM thuần túy làm động lực cho việc xây dựng Hybrid Parser nhằm nén chi phí. *(Cite: [GRAG])*

### 1.2. Mục tiêu nghiên cứu
- **Mục tiêu tổng quát:** Nghiên cứu và xây dựng hệ thống tiền xử lý dữ liệu lai (Hybrid Parser) nhằm tối ưu hóa chi phí và hiệu năng GraphRAG.
- **3 Mục tiêu cụ thể:**
  1. **MT1:** Xây dựng bộ Hybrid Parser bảo toàn cấu trúc phân cấp và mối quan hệ quy phạm.
  2. **MT2:** Tối ưu hóa chi phí vận hành (tiết kiệm >80% Token API LLM qua Semantic Router).
  3. **MT3:** Đánh giá định lượng đa tầng (Multi-level Evaluation) chất lượng đồ thị và hiệu năng RAG.

### 1.3. Đối tượng và Phạm vi nghiên cứu
- **Đối tượng:** Hệ thống trích xuất và truy xuất văn bản quy phạm pháp luật (GraphRAG).
- **Phạm vi (Scope):** Pilot corpus trên **Chương III Luật Đất đai 2024** (Quyền và nghĩa vụ của người sử dụng đất) — bao gồm 1 Chương, 5 Mục, 23 Điều, 84 Khoản, 109 Điểm (222 physical nodes) với mật độ dẫn chiếu chéo và cấu trúc lồng ghép phức tạp nhất.
- **Tính tổng quát:** Nhóm kiến trúc vật lý M1-M4 không phụ thuộc domain; nhóm kiến trúc ngữ nghĩa M5-M7 mở rộng linh hoạt qua Registry.

### 1.4. Phương pháp nghiên cứu
- Kết hợp phương pháp thực nghiệm, định lượng (Information Extraction & RAGAS metrics) và đánh giá chuyên gia (Expert Blind Review / LLM-as-a-Judge).

### 1.5. Ý nghĩa khoa học và thực tiễn (Đóng góp nghiên cứu)
- Giải quyết "nút thắt cổ chai" giữa hai thái cực: Ontology truyền thống thủ công tốn sức và GraphRAG hiện đại sử dụng Schema phẳng bị phá vỡ logic điều kiện. *(Cite: [FOLAW], [LKIFC], [CASANOVAS])*
- Đề xuất mô hình **NormAssertion** được tự động hóa trích xuất bằng LLM ép chuẩn JSON Schema.

### 1.6. Kết cấu báo cáo
- Tổng quan cấu trúc 5 chương.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT (~18 TRANG)

### 2.1. Tổng quan về RAG
- Định nghĩa kiến trúc RAG chuẩn. *(Cite: [RAG_ORIG], [RAG_SURV])*
- Hiện tượng ảo giác pháp lý trong RAG truyền thống khi gặp thông tin mâu thuẫn hoặc thiếu ngữ cảnh. *(Cite: [HALLUC])*

### 2.2. GraphRAG — Kiến trúc RAG dựa trên Đồ thị Tri thức
- Tiến trình từ Knowledge Graph đến GraphRAG. *(Cite: [KG_SURV], [GRAG_SURV])*
- Kiến trúc Microsoft GraphRAG (Baseline 3) và các giới hạn: Schema phẳng không tương thích với logic pháp lý, định tuyến tĩnh tốn kém. *(Cite: [GRAG], [VLEGAL], [VNLI], [GROUTER])*

### 2.3. Biểu diễn tri thức pháp lý (Legal Knowledge Representation - KR)
- Lý thuyết quy phạm pháp luật (Deontic Logic, Frame-based KR, Hohfeldian Semantics). *(Cite: [HOHFELD], [LEGAL_AI])*
- Định vị Phổ Ontology (Ontology Spectrum) từ Vocabulary -> Taxonomy -> Frame-based -> Formal Logic. *(Cite: [KRR_BOOK])*
- Định vị mô hình **NormAssertion** nằm ở mức Frame-based KR: Đủ chặt chẽ để query đồ thị, đủ linh hoạt để LLM trích xuất tự động qua JSON Schema.

### 2.4. Semantic Routing & Tối ưu hóa trong RAG Pipeline
- Cơ chế Semantic Routing dựa trên Embedding nhúng siêu nhẹ và Regex filter để phân luồng dữ liệu, cắt giảm chi phí API.

### 2.5. Phương pháp luận Đánh giá Hệ thống Legal RAG
- Khung đánh giá đa tầng (Multi-level Evaluation Protocol) và công cụ kỹ thuật *(Cite: [DOC_OAI], [CYPHER], [DOC_NEO], [DOC_SHA])*.

---

## CHƯƠNG 3: PHƯƠNG PHÁP NGHIÊN CỨU (~32 TRANG)

### 3.0. Tổng quan phương pháp nghiên cứu
- **Sơ đồ luồng phương pháp luận:** Thiết kế (MT1, MT2) -> Cài đặt Pipeline 11 Modules -> Đánh giá thực nghiệm (MT3).
- **Tính chất 1 chiều:** Unidirectional Data Flow giữa các tầng.

### 3.1. Phương pháp cho MT1 — Xây dựng Hybrid Parser
- Thiết kế kiến trúc **Neuro-symbolic**: Kết hợp Rule-based Symbolic Parsing (độ chính xác 100%, 0 đồng) và LLM Structured Extraction.

### 3.2. Phương pháp cho MT2 — Tối ưu chi phí (Cost Optimization)
- Thiết kế **Semantic Router** (Decision Layer): Kết hợp Regex Pre-filter và Embedding Model Qwen2.5-0.5B (MaxFusion Strategy) để sàng lọc >80% node đơn giản trước khi gửi sang LLM.

### 3.3. Phương pháp cho MT3 — Đánh giá hệ thống
- Mẫu thực nghiệm **Multi-baseline Benchmark**: So sánh Đề xuất (Hybrid Parser) với Baseline 1 (Naive Chunking), Baseline 2 (Pure Regex), và Baseline 3 (Microsoft GraphRAG).
- Phương pháp QA End-to-End: Kết hợp **LLM-as-a-Judge (GPT-4o)** và **Expert Blind Review**.

### 3.4. Phương pháp ước lượng (Công thức toán)
- Công thức đo lường trích xuất: Node/Edge Precision, Recall, F1-Score. *(Cite: [IR_METR])*
- Công thức đo lường RAGAS: Context Precision, Context Recall, Faithfulness, Answer Relevance. *(Cite: [RAGAS])*
- Đo lường hiệu năng: Token Savings Rate (%), Latency (s), Memory Footprint.

### 3.5. Dữ liệu nghiên cứu
- Pilot Corpus: **Chương III Luật Đất đai 2024** (222 physical nodes). *(Cite: [VLEGAL])*
- Xây dựng **Golden Graph** (gán nhãn chuẩn) và **Golden QA Dataset** (50-100 câu hỏi inspired by VLegal-Bench).

### 3.6. Thiết kế Tuyến Tĩnh (Modules 1 – 4)
- **Module 1 (Preprocessing):** Phục hồi Word Auto-numbering qua XML/OOXML (`numbering.xml`), Chuẩn hóa Unicode NFC.
- **Module 2 (Regex Parser):** Mẫu Regex chuẩn (Nghị định 34/2016/NĐ-CP), Boundary Detector, Stack-based Hierarchy Builder, Hybrid ID (`law_code` + `parent_id` + `char_start`). *(Cite: [STRCHK])*
- **Module 3 (Validation Engine):** Triết lý "Read-only & Log" (No Auto-repair), kiểm tra Orphan Node, Gap Index, Broken Parent, Empty Node.
- **Module 4 (Physical Graph Builder):** Schema `LegalNode`, khởi tạo các cạnh cấu trúc `BELONG_TO`, `NEXT`, `PREVIOUS`.

### 3.7. Thiết kế Tuyến Động (Modules 5 – 7)
- **Module 5 (Semantic Router):** Routing Engine kết hợp Regex + Qwen2.5-0.5B Embedding. *(Cite: [GROUTER], [QWEN])*
- **Module 6 (LLM Structured Extraction):** Khung `gpt-4o-mini` + Pydantic + Instructor Strict JSON. 8 Core Entity Classes & 7 Hohfeldian Relation Types. Four Corners Rule & Zero-Hallucination. *(Cite: [DOC_OAI], [VLEGAL])*
- **Module 7 (Legal Ontology Builder):**
  - Mô hình **NormAssertion** kế thừa từ FOLAW/LKIFC. *(Cite: [ViLO], [LKIFC], [FOLAW])*
  - 3-tier Entity Matching (Normalized Match + Fuzzy/Embedding Fallback).
  - Cấu trúc 3 tầng: `LocalMention` --DENOTES--> `CanonicalConcept`.
  - **Quarantine Store (Semantic Quality Gate):** Cách ly dữ liệu vi phạm schema chống sập graph. *(Cite: [RGB])*
  - Triết lý **Edge-Level Provenance** (Entity siêu nhẹ, bằng chứng lưu ở Edge).

### 3.8. Thiết kế Hợp nhất và Lưu trữ (Modules 8 – 9)
- **Module 8 (Ontology Fusion Engine):** Physical First Merge Policy, con trỏ `source_node_ids` (tiết kiệm >80% Token), `conflict_resolver.py`, `ReferenceResolver` (phân giải dẫn chiếu chéo `PENDING_M8`).
- **Module 9 (Neo4j Ingestion Engine):**
  - Kiến trúc **M9 V3.0 (Fast-Path Ingestion)**: Native Unpacked Properties, Hybrid Indexing (B-Tree + Vector Index), Idempotence (`MERGE` + Namespace Clear by `law_code`), Lightweight Audit (`graph_checker.py`).

### 3.9. Thiết kế tầng Truy xuất và Đánh giá (Modules 10 – 11) [Biến số kiểm soát]
- **Module 10 (Graph Retrieval):** Đóng vai trò Black Box Control Variable. Quy trình 5 bước: Anchor Search -> Semantic Traversal -> Context Assembly -> LLM Reader. *(Cite: [KBQA])*
- **Module 11 (Evaluation Engine):** Pipeline tự động chấm điểm theo LLM-as-a-Judge và RAGAS.

---

## CHƯƠNG 4: KẾT QUẢ NGHIÊN CỨU (~30 TRANG)

### 4.1. Thực trạng vấn đề nghiên cứu
- Bức tranh GraphRAG tại Việt Nam và tính cần thiết của Hybrid Parser.

### 4.2. Thống kê mô tả mẫu nghiên cứu
- Thống kê chi tiết Pilot Corpus Chương III Luật Đất đai 2024: 222 physical nodes, số lượng Edges, Entities, NormAssertions.

### 4.3. Kết quả cho MT1 — Chất lượng đồ thị Parser (F1-Score)
- So sánh Node/Edge F1-Score của Hybrid Parser với Pure Regex và Naive Chunking. *(Cite: [VNKG], [STRCHK])*

### 4.4. Kết quả cho MT2 — Hiệu quả tối ưu chi phí Token
- Đo lường tỷ lệ tiết kiệm Token API (đạt >80% reduction) và Latency thông qua Semantic Router (M5).

### 4.5. Kết quả cho MT3 — Hiệu năng RAG End-to-End & RAGAS Metrics
- Bảng so sánh 4 kịch bản (Baseline 1, Baseline 2, Baseline 3 MS GraphRAG, và Hybrid Parser Proposal) trên các chỉ số RAGAS (Context Precision, Context Recall, Faithfulness, Answer Relevance).
- Phân tích ưu thế chuyên biệt của NormAssertion trong domain pháp lý so với kiến trúc phổ quát của Microsoft GraphRAG.

### 4.6. Thảo luận và Đánh giá chuyên gia (Discussion & Expert Review)
- Kết quả Blind Review từ chuyên gia pháp lý và phân tích các trường hợp lỗi (Error Analysis).

---

## CHƯƠNG 5: KẾT LUẬN VÀ HÀM Ý (~6 TRANG)

### 5.1. Kết luận chính
- Tóm tắt 3 đóng góp lớn: Tự động hóa trích xuất NormAssertion qua LLM, cắt giảm >80% chi phí API bằng Semantic Router, và giải quyết nút thắt cổ chai thu nhận tri thức (Knowledge Acquisition Bottleneck). *(Cite: [ViLO], [GROUTER])*

### 5.2. Hàm ý khoa học và thực tiễn
- Đóng góp vào hướng tiếp cận "Legal-as-Code" và ứng dụng cho trợ lý pháp lý doanh nghiệp tại Việt Nam.

### 5.3. Hạn chế và Hướng nghiên cứu tiếp theo
- Hạn chế về quy mô pilot corpus (Chương III - 222 nodes) và các dạng văn bản đặc thù (bảng biểu, phụ lục). *(Cite: [FP7])*
- Hướng phát triển: Hoàn thiện NormAssertion-aware retrieval ở M10 và mở rộng đa văn bản luật.

---

## 📊 TỔNG KẾT ƯỚC LƯỢNG TRANG

| Chương | Tiêu đề | Trang dự kiến |
| :---: | :--- | :---: |
| **Chương 1** | Giới thiệu nghiên cứu | ~8 |
| **Chương 2** | Cơ sở lý thuyết | ~18 |
| **Chương 3** | Phương pháp nghiên cứu | ~32 |
| **Chương 4** | Kết quả nghiên cứu | ~30 |
| **Chương 5** | Kết luận và hàm ý | ~6 |
| **TỔNG CỘNG** | **Cấu trúc Báo cáo NCKH 5 Chương** | **~94 trang** |
