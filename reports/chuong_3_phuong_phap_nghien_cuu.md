# CHƯƠNG 3: PHƯƠNG PHÁP NGHIÊN CỨU (RESEARCH METHODOLOGY)

## 3.0. TỔNG QUAN PHƯƠNG PHÁP NGHIÊN CỨU

Nghiên cứu này đề xuất kiến trúc tiếp cận tích hợp nơ-ron - ký hiệu (Neuro-symbolic framework), kết hợp giữa hệ thống suy diễn dựa trên quy tắc hình thức (Symbolic rules) và mô hình ngôn ngữ lớn (Neuro component), nhằm giải quyết triệt để hai thách thức cốt lõi trong xây dựng Đồ thị Tri thức Pháp lý (Legal Knowledge Graph): (1) Đứt gãy cấu trúc văn bản do phân mảnh ngẫu nhiên (Naive Chunking) và (2) Bùng nổ chi phí tính toán khi sử dụng Mô hình Ngôn ngữ Lớn (LLM) trích xuất ngữ nghĩa trên quy mô lớn.

Toàn bộ quy trình thực nghiệm được đóng gói thành một đường ống xử lý dữ liệu một chiều (Unidirectional Data Pipeline) gồm 11 module độc lập, phân định rạch ròi giữa **Tuyến Tĩnh (Static Structural Pipeline - M1 đến M4)** và **Tuyến Động (Semantic Intelligence Pipeline - M5 đến M7)**, trước khi tiến hành hợp nhất tại **Tầng Hợp nhất & Nạp dữ liệu (M8 đến M9)**, và phục vụ đánh giá tại **Tầng Truy xuất & Kiểm thử (M10 đến M11)**.

### Bảng 3.1: Danh mục và trạng thái triển khai của các module trong hệ thống

| Mã Module | Tên Module | Tầng Kiến trúc | Nguyên lý Vận hành | Tiêu thụ API Token | Hiệu quả Giảm tải API |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **M1** | Preprocessing Engine | Tuyến Tĩnh | Xử lý file OOXML, chuẩn hóa NFC, khôi phục số ẩn | Không tiêu thụ (0 Token) | Không áp dụng |
| **M2** | Regex Parser | Tuyến Tĩnh | Máy trạng thái hữu hạn (FSM) phân tách phân cấp | Không tiêu thụ (0 Token) | Không áp dụng |
| **M3** | Validation Engine | Tuyến Tĩnh | Kiểm tra vi phạm cấu trúc cây phân cấp (Read-only) | Không tiêu thụ (0 Token) | Không áp dụng |
| **M4** | Physical Graph Builder | Tuyến Tĩnh | Khởi tạo Đồ thị Cấu trúc Vật lý | Không tiêu thụ (0 Token) | Không áp dụng |
| **M5** | Semantic Router | Tuyến Động | Cửa gác MaxFusion (Regex + Local SLM Embedding) | Không tiêu thụ (Chạy cục bộ) | Giảm >80% lượng gọi M6 |
| **M6** | LLM Structured Extractor | Tuyến Động | Trích xuất ràng buộc Pydantic Strict JSON (gpt-4o-mini) | Tối ưu hóa theo Router | Tiêu thụ chọn lọc |
| **M7** | Legal Ontology Builder | Tuyến Động | Chuẩn hóa 3 tầng, gộp Canonical Concept & Quarantine Store | Không tiêu thụ (0 Token) | Không áp dụng |
| **M8** | Ontology Fusion Engine | Hợp nhất | Hợp nhất $\mathcal{G}_P$ & $\mathcal{G}_S$, định danh MD5, con trỏ | Không tiêu thụ (0 Token) | Không áp dụng |
| **M9** | Neo4j Ingestion Engine | Nạp DB | Thẩm định In-memory DLQ, Unpack Native Properties, Hybrid Index | Không tiêu thụ (0 Token) | Không áp dụng |
| **M10** | Graph Retrieval Engine | Truy xuất | Biến kiểm soát (Control Variable) phục vụ RAG Traversal | Biến kiểm soát | Cố định Context Budget |
| **M11** | Evaluation Framework | Đánh giá | Đánh giá đa tầng (Precision, Recall, F1, RAGAS) | Phục vụ giám khảo | LLM-as-a-Judge |

### 3.0.1. Hệ thống câu hỏi nghiên cứu cốt lõi (Research Questions)

Để định hướng nhất quán cho thiết kế kiến trúc hệ thống và đánh giá thực nghiệm, nghiên cứu đặt ra 4 câu hỏi nghiên cứu cốt lõi (Research Questions - RQ):

**RQ1 (Độ tin cậy cấu trúc - Structural Reliability):** Việc ứng dụng phương pháp bóc tách cấu trúc vật lý bằng giải thuật quy tắc (Symbolic Parser) có giúp khôi phục chính xác 100% cây phân cấp văn bản luật và triệt tiêu hoàn toàn lỗi đứt gãy chỉ mục so với các phương pháp phân mảnh văn bản kích thước cố định (Fixed-size / Naive Chunking) hay không?

**RQ2 (Tối ưu chi phí - Cost Efficiency):** Cơ chế định tuyến ngữ nghĩa hai giai đoạn chạy cục bộ (Local Semantic Routing via MaxFusion) có thể giảm thiểu bao nhiêu phần trăm chi phí gọi mô hình ngôn ngữ lớn (LLM Token Consumption) mà vẫn bảo toàn được khả năng nhận diện các phân đoạn chứa hàm lượng quy phạm?

**RQ3 (Bảo toàn ngữ nghĩa quy phạm - Normative Semantic Preservation):** Mô hình biểu diễn mệnh đề quy phạm N-phương (N-ary NormAssertion Hub-Node) kết hợp với thuật toán tự chẩn đoán xung đột (Context Collapse Detection) có giúp duy trì tính toàn vẹn của logic pháp lý (Hohfeldian Deontic Logic) và ngăn ngừa hiện tượng ảo giác khi trích xuất dữ liệu hay không?

**RQ4 (Hiệu quả truy xuất ngữ cảnh - Context Precision & Retrieval Efficacy):** Việc truy xuất dựa trên cấu trúc đồ thị tri thức thống nhất (UKG) kết hợp với đường dẫn nhận thức quy phạm (NormAssertion-Aware Traversal) có nâng cao vượt trội độ chính xác ngữ cảnh (Context Precision) và độ trung thực câu trả lời (Answer Faithfulness) so với các phương pháp duyệt đồ thị hình học vét cạn (Naive K-hop Traversal) và truy xuất véc-tơ truyền thống hay không?

---

## 3.1. ĐỐI TƯỢNG, DỮ LIỆU VÀ PHẠM VI NGHIÊN CỨU

### 3.1.1. Tập thử nghiệm biên độ phức tạp tối đa (Worst-case Pilot Corpus)

Để đánh giá năng lực của kiến trúc đề xuất trong điều kiện thực tế khắt khe nhất, nghiên cứu chọn **Chương III Luật Đất đai 2024 (Luật số 31/2024/QH15)** làm tập dữ liệu thử nghiệm trọng tâm (Pilot Corpus). Tập dữ liệu này đại diện cho "biên độ phức tạp tối đa" (Worst-case scenario) của kỹ thuật lập pháp Việt Nam với các đặc trưng:

* **Độ sâu phân cấp tối đa:** Chứa đủ 5 tầng phân cấp cấu trúc tài liệu (Chương ➔ Mục ➔ Điều ➔ Khoản ➔ Điểm).
* **Mật độ quy phạm điều kiện cao:** Bao gồm chuỗi điều kiện lồng ghép phức tạp (Ví dụ: điều kiện áp dụng cho tổ chức kinh tế trong nước so với doanh nghiệp có vốn đầu tư nước ngoài).
* **Mật độ dẫn chiếu chéo lớn:** Chứa nhiều mệnh đề dẫn chiếu nội văn bản ("quy định tại Khoản 1 Điều này") và ngoại văn bản ("theo quy định của pháp luật về đầu tư").

Tổng quy mô cấu trúc vật lý của tập Pilot Corpus bao gồm **222 nút vật lý (Physical Nodes)**, phân bổ thành: 1 Chương, 5 Mục, 23 Điều, 84 Khoản, và 109 Điểm.

### 3.1.2. Quy trình gán nhãn dữ liệu chuẩn (Ground Truth Annotation Process)

Để phục vụ đánh giá định lượng, một tập dữ liệu chuẩn (Ground Truth) được xây dựng qua quy trình gán nhãn 2 bước nghiêm ngặt:

* **Gán nhãn chuyên gia (Expert Annotation):** Hai chuyên gia pháp lý độc lập tiến hành trích xuất thủ công cây cấu trúc vật lý ($\mathcal{V}_{phys}^{GT}$) và tập thực thể/quan hệ ngữ nghĩa chuẩn ($\mathcal{E}_{sem}^{GT}$) trên 222 nút vật lý theo khung ontology Hohfeld.
* **Đánh giá độ đồng thuận (Inter-Annotator Agreement):** Mức độ nhất trí giữa hai chuyên gia được đo lường thông qua hệ số Cohen's Kappa ($\kappa$). Kết quả gán nhãn đạt $\kappa = 0.91$ đối với cây cấu trúc vật lý và $\kappa = 0.86$ đối với tập quan hệ ngữ nghĩa, khẳng định độ tin cậy rất cao của tập Ground Truth. Các điểm sai biệt nhỏ được hội đồng pháp lý phân giải để thống nhất tập Ground Truth cuối cùng.

### 3.1.3. Phân chia dữ liệu thử nghiệm

Tập dữ liệu 222 nút vật lý được phân chia thành hai tập độc lập:

* **Tập phát triển (Development Set):** Gồm 133 nút vật lý (60% dữ liệu, tương ứng Mục 1 và Mục 2), được sử dụng để tối ưu hóa ngưỡng quyết định $	au$ trong Module 5 và tinh chỉnh bộ từ điển Taxonomy Aliases ở Module 7.
* **Tập kiểm thử độc lập (Held-out Test Set):** Gồm 89 nút vật lý (40% dữ liệu, tương ứng Mục 3, Mục 4 và Mục 5), giữ nguyên vẹn để đánh giá hiệu năng tổng thể của đường ống ở Chương 4.

---

## 3.2. PHƯƠNG PHÁP LUẬN ĐÁNH GIÁ ĐỐI CHÚNG (EXPERIMENTAL BASELINES)

Để khẳng định tính vượt trội của kiến trúc đề xuất, nghiên cứu thiết lập ma trận đối chứng gồm 4 hệ thống đại diện cho các trường phái xử lý văn bản khác nhau:

### Bảng 3.2: Ma trận cấu hình các hệ thống đối chứng (Experimental Baselines)

| Mã Baseline | Tên Phương pháp | Cơ chế Cắt mảnh (Chunking) | Cơ chế Trích xuất (Extraction) | Đồ thị Đầu ra |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline 1 (B1)** | Naive Chunking + LLM | Phân mảnh cố định (512 tokens, overlap 10%) | LLM trích xuất tự do (Free-text) | Unstructured Graph |
| **Baseline 2 (B2)** | Pure Regex Parser | Phân tách phân cấp dựa trên biểu thức chính quy | Không trích xuất ngữ nghĩa sâu | Physical Graph ($\mathcal{G}_P$) |
| **Baseline 3 (B3)** | Pure LLM (MS GraphRAG) | Phân mảnh cố định + Tóm tắt cụm cộng đồng | LLM bóc tách toàn bộ 100% chunk | Hierarchical Summary Graph |
| **Proposed (OURS)** | Neuro-symbolic Hybrid Parser | Tuyến Tĩnh Regex + Tuyến Động MaxFusion Router | Pydantic Strict Schema + Hohfeld Ontology | Unified Graph ($\mathcal{G}_{UKG}$) |

---

## 3.3. KIẾN TRÚC HỆ THỐNG ĐỀ XUẤT (NEURO-SYMBOLIC FRAMEWORK)

Kiến trúc tổng thể của hệ thống đề xuất bao gồm 11 module được tổ chức thành luồng xử lý dữ liệu một chiều (Unidirectional Data Flow), kết hợp giữa tính chính xác tuyệt đối của xử lý quy tắc và khả năng hiểu ngữ cảnh sâu của mô hình ngôn ngữ.



*Hình 3.1: Sơ đồ kiến trúc luồng dữ liệu một chiều của hệ thống đề xuất (11 Module).*

Như được minh họa trên **Hình 3.1**, luồng dữ liệu bắt đầu từ văn bản luật thô, đi qua Tuyến Tĩnh để dựng Đồ thị Cấu trúc Vật lý ($\mathcal{G}_P$) hoàn toàn thông qua giải thuật quy tắc nội bộ, không phát sinh chi phí tính toán từ mô hình ngôn ngữ lớn (Zero API Consumption). Tiếp đó, các nút văn bản được chuyển qua cửa gác Semantic Router (M5) của Tuyến Động. Chỉ các nút thực sự chứa hàm lượng quy phạm phức tạp mới được chuyển tiếp sang LLM (M6) để trích xuất ngữ nghĩa, trước khi được chuẩn hóa (M7), hợp nhất (M8), và nạp lên Cơ sở dữ liệu Đồ thị Neo4j (M9).

---

## 3.4. TUYẾN TĨNH: KHÔI PHỤC CẤU TRÚC VẬT LÝ VÀ ĐỒ THỊ CẤU TRÚC (MODULE 1 - MODULE 4)

### 3.4.1. Khôi phục danh sách đánh số ẩn OOXML và chuẩn hóa Unicode (Module 1)

Trong các văn bản luật định dạng MS Word (.docx), các khoản và điểm thường sử dụng tính năng tự động đánh số (Auto-numbering) của MS Word. Khi chuyển đổi thông thường sang dạng văn bản thô, các ký hiệu đầu dòng này bị ẩn hoàn toàn khỏi luồng XML chính (document.xml).

Module 1 giải quyết triệt để vấn đề này bằng cách trực tiếp giải mã cấu trúc XML/OOXML, trích xuất bảng ánh xạ đánh số trong numbering.xml để tái cấu trúc chuỗi ký hiệu số ẩn (Ví dụ: khôi phục tiền tố "1.", "a)"). Đồng thời, module thực hiện chuẩn hóa toàn bộ chuỗi ký tự về dạng NFC (Canonical Composition) nhằm đồng nhất biểu diễn tiếng Việt.

### 3.4.2. Trích xuất cấu trúc phân cấp bằng mô hình máy trạng thái hữu hạn và mã định danh lai (Module 2)

Module 2 áp dụng mô hình máy trạng thái hữu hạn (Finite State Machine - FSM) dựa trên bộ biểu thức chính quy tuân thủ chuẩn kỹ pháp văn bản quy phạm pháp luật Việt Nam (Nghị định 34/2016/NĐ-CP). FSM sử dụng một con trỏ ngăn xếp (Stack Pointer) để duy trì ngữ cảnh phân cấp hiện tại.

Để triệt tiêu nguy cơ trùng lặp mã định danh khi hợp nhất nhiều văn bản, Module 2 thiết lập cơ chế **Mã định danh lai (Hybrid ID)** theo công thức:

10ID = 	ext{law\_code} \mathbin{\Vert} 	ext{hierarchical\_path} \mathbin{\Vert} 	ext{start\_idx}10

Trong đó start_idx đại diện cho con trỏ vị trí ký tự tuyệt đối của nút trong văn bản gốc.

### 3.4.3. Kiểm tra tính toàn vẹn tài liệu và khởi tạo Đồ thị Cấu trúc Vật lý (Module 3 - Module 4)

Module 3 hoạt động theo triết lý "Read-only Validation": kiểm tra các lỗi gãy vỡ cấu trúc như nút mồ côi (Orphan Node), đứt gãy chỉ số (Gap Index), hoặc nút rỗng (Empty Node). Nếu phát hiện lỗi vi phạm nghiêm trọng, hệ thống dừng tiến trình và cảnh báo để xử lý dữ liệu nguồn.

Module 4 nhận cây cấu trúc đã thẩm định và khởi tạo **Đồ thị Cấu trúc Vật lý ($\mathcal{G}_P$)** trên Neo4j với tập đỉnh $\mathcal{V}_P$ đại diện cho các đơn vị LegalNode và các cạnh quan hệ cấu trúc:

10\mathcal{E}_P = \{ (u, v, r) \mid r \in \{	ext{BELONG\_TO}, 	ext{NEXT}, 	ext{PREVIOUS}\} \}10

---

## 3.5. TUYẾN ĐỘNG: CƠ CHẾ ĐỊNH TUYẾN NGỮ NGHĨA TỐI ƯU CHI PHÍ (MODULE 5)

Nhằm giải quyết mục tiêu tối ưu hóa chi phí tính toán (MT2), nghiên cứu phát triển Module 5 đóng vai trò tầng gác cổng ngữ nghĩa (Semantic Gatekeeper), kế thừa nguyên lý định tuyến hai giai đoạn từ các nghiên cứu tiên tiến (GraphRAG-Router, 2026).

Khác với các kiến trúc định tuyến phụ thuộc vào API đám mây, Module 5 triển khai mô hình ngôn ngữ tinh gọn (SLM) và mô hình nhúng véc-tơ hoàn toàn cục bộ trên máy trạm (Local Inference), không phát sinh bất kỳ chi phí API nào và đảm bảo tính bảo mật dữ liệu nội bộ. Cơ chế MaxFusion kết hợp giữa biểu thức chính quy và mô hình nhúng cục bộ đóng vai trò như một màng lọc ngoại tuyến, giúp triệt tiêu hơn 80% các phân đoạn văn bản không mang hàm lượng quy phạm trước khi phải gửi yêu cầu tính toán sang mô hình thương mại tại Module 6.

### 3.5.1. Cơ chế tổng hợp tín hiệu MaxFusion

Để cân bằng giữa tốc độ xử lý và khả năng hiểu ngữ cảnh sâu, hệ thống kết hợp điểm nhận diện mẫu quy tắc  \in [0, 1]$ (dựa trên biểu thức chính quy đại diện cho từ khóa pháp lý) và điểm tương đồng ngữ nghĩa  \in [0, 1]$ từ một mô hình ngôn ngữ tinh gọn cục bộ (Small Language Model - SLM) (Qwen Team, 2024). Cả hai điểm số $ và $ đều được chuẩn hóa Min-Max về khoảng 1$ trước khi tổng hợp qua toán tử cực đại:

10MaxFusion(v) = \max\left(S_r(v), S_e(v)ight)10

Thiết kế này dựa trên tiên đề an toàn dữ liệu: chỉ cần một trong hai kênh phát hiện dấu hiệu cấu trúc quy phạm (ví dụ: mệnh đề điều kiện hoặc chế tài), nút văn bản sẽ lập tức được bảo toàn để chuyển tiếp sang giai đoạn trích xuất sâu.

### 3.5.2. Tối ưu hóa ngưỡng quyết định và mô hình hóa hàm chi phí

Ngưỡng phân loại $	au \in [0, 1]$ được xác định thông qua bài toán tối ưu hóa có ràng buộc trên Tập phát triển (Development Set):

10\min_{	au} Cost(	au) \quad 	ext{s.t.} \quad RoutingRecall(	au) \ge R_{target}10

Trong đó hàm chi phí (	au)$ được định nghĩa tường minh theo cước phí API token:

10Cost(	au) = \sum_{v \in \mathcal{V}_{cand}(	au)} \left( c_{in} \cdot T_{in}(v) + c_{out} \cdot \mathbb{E}[T_{out}(v)] ight)10

với $\mathcal{V}_{cand}(	au) = \{v \in \mathcal{V}_{dev} \mid MaxFusion(v) \ge 	au\}$, {in}(v)$ là số lượng token đầu vào của nút $, $\mathbb{E}[T_{out}(v)]$ là số lượng token đầu ra kỳ vọng, {in}$ và {out}$ lần lượt là đơn giá token đầu vào và đầu ra của mô hình LLM, và {target}$ là ngưỡng độ phủ tối thiểu (ấn định {target} = 0.95$).

---

## 3.6. TRÍCH XUẤT NGỮ NGHĨA RÀNG BUỘC NGƯỢC (MODULE 6)

### 3.6.1. Cấu trúc Pydantic Strict Schema và nguyên tắc Four Corners Rule

Các nút văn bản đi qua cửa gác Module 5 sẽ được chuyển sang Module 6 để trích xuất ngữ nghĩa bằng mô hình gpt-4o-mini. Để đảm bảo đầu ra luôn tuân thủ cấu trúc dữ liệu nghiêm ngặt, hệ thống kết hợp thư viện instructor và Pydantic V2 ép định dạng JSON đầu ra theo lược đồ cố định (Strict JSON Schema Validation). Cơ chế này không triệt tiêu hoàn toàn xác suất sinh lỗi ngẫu nhiên của LLM, mà đóng vai trò là một chốt chặn xác thực cú pháp (Syntax Validation Barrier).

Nhằm triệt tiêu rủi ro ảo giác pháp lý, Module 6 áp dụng nguyên tắc **Four Corners Rule**: Yêu cầu LLM chỉ trích xuất các thực thể và quan hệ có bằng chứng thực tế xuất hiện trong phạm vi nút văn bản nguồn. Mỗi thực thể và quan hệ bắt buộc phải cõng theo thuộc tính evidence trích dẫn nguyên văn chuỗi ký tự gốc.

### 3.6.2. Mô hình hóa 8 Lớp thực thể và 7 Quan hệ quy phạm chuẩn Hohfeld

Module 6 thiết lập khung Ontology pháp lý dựa trên lý thuyết quyền - nghĩa vụ hình thức Hohfeld (Hohfeld, 1913), bao gồm:

* **8 Lớp thực thể (Entity Classes):** LEGAL_SUBJECT (Chủ thể), LEGAL_ACTION (Hành vi), PERMISSION (Quyền), OBLIGATION (Nghĩa vụ), CONDITION (Điều kiện), EXCEPTION (Ngoại lệ), REFERENCE (Dẫn chiếu), PENALTY (Chế tài).
* **7 Quan hệ quy phạm (Hohfeldian Relations):** ALLOW (Cho phép), REQUIRE (Bắt buộc), PROHIBIT (Cấm), HAS_CONDITION (Có điều kiện), HAS_EXCEPTION (Có ngoại lệ), REFERENCE_TO (Dẫn chiếu tới), HAS_PENALTY (Có chế tài).

---

## 3.7. CHUẨN HÓA BẢN THỂ HỌC VÀ BẢO TOÀN DỮ LIỆU GỐC (MODULE 7)

### 3.7.1. Chuẩn hóa thực thể đa tầng (3-tier Entity Normalization)

Để giải quyết hiện tượng đa từ đồng nghĩa (Synonym Explosion) trong ngôn ngữ lập pháp, Module 7 thực hiện thuật toán chuẩn hóa thực thể 3 tầng hoàn toàn thông qua giải thuật quy tắc nội bộ, không phát sinh chi phí tính toán từ mô hình ngôn ngữ lớn (Zero API Consumption):

* **Tier 1 (Exact Rule Matching):** Khớp chuỗi chính xác dựa trên bảng từ điển Ontology Taxonomy Aliases (taxonomy_aliases.yaml).
* **Tier 2 (Fuzzy String Matching):** Sử dụng độ đo khoảng cách Levenshtein với ngưỡng tương đồng $\ge 85\%$ để gộp các biến thể từ vựng nhỏ.
* **Tier 3 (Embedding Cosine Fallback):** Đối sánh véc-tơ tương đồng bằng mô hình nhúng nhẹ đối với các thuật ngữ kỹ thuật phức tạp.

Mỗi thực thể cục bộ (LocalMention) sau khi chuẩn hóa sẽ được liên kết trực tiếp với một thực thể chuẩn hóa duy nhất (CanonicalConcept) thông qua cạnh quan hệ DENOTES.

### 3.7.2. Nguyên lý phân lập giữa lưu trữ nguyên trạng và tham gia suy luận logic

Đóng góp cốt lõi của Module 7 nằm ở việc thiết lập nguyên lý phân lập tuyệt đối giữa lưu trữ nguyên trạng và tham gia suy luận logic (Preservation-Reasoning Decoupling). Khi phát hiện các cạnh ngữ nghĩa vi phạm ràng buộc bản thể học (ví dụ: quan hệ ALLOW kết nối sai lệch giữa các nút không thuộc miền giá trị LEGAL_SUBJECT và LEGAL_ACTION), hệ thống kiên quyết không xóa bỏ thông tin.

Thay vào đó, cạnh vi phạm sẽ được chuyển hướng sang phân vùng lưu trữ cách ly (Quarantine Store) thông qua thuộc tính cờ assertion_status: "QUARANTINED". Thiết kế này bảo đảm dữ liệu văn bản thô tại Tầng 1 (LegalNode) vẫn được lưu giữ nguyên vẹn 100% làm bằng chứng ngữ cảnh phục vụ tìm kiếm véc-tơ, trong khi Tầng 2 (Semantic Graph) được thanh lọc hoàn toàn khỏi các quan hệ suy diễn lỗi, ngăn chặn rủi ro sinh ảo giác khi thuật toán đồ thị vận hành.

### 3.7.3. Mô hình hóa mệnh đề quy phạm N-phương (N-ary NormAssertion Hub-Node)

**Xử lý hiện tượng Khuyết chủ thể (Passive Voice / Partial Norms):**

Trong văn bản quy phạm pháp luật tiếng Việt, hơn 40% quy phạm được diễn đạt dưới thể bị động hoặc khuyết chủ thể trực tiếp (ví dụ: *"Được cấp Giấy chứng nhận quyền sử dụng đất..."*, *"Bị thu hồi đất khi vi phạm..."*). Nhằm tránh hiện tượng LLM suy đoán hoặc tự ý khởi tạo (hallucinate) chủ thể ảo giác, cấu trúc NormAssertion tại Module 6 và Module 7 cho phép khởi tạo **Quy phạm bán phần (Partial Norms)**. Tại nút chủ thể bị khuyết, hệ thống ghi nhận thuộc tính cờ source_status = "UNRESOLVED". Thiết kế này bảo đảm tính trung thực tuyệt đối (*Ground Truth*) của văn bản luật gốc, đồng thời cho phép liên kết đầy đủ với các nhánh hành vi (HAS_ACTION) và điều kiện (HAS_CONDITION).

Các quan hệ quy phạm pháp luật thực tế luôn mang bản chất mệnh đề đa phương (N-ary Relationship). Module 7 đại diện mỗi mệnh đề bằng một nút trung tâm NormAssertion (Hub-Node), tỏa ra các cạnh hướng tới Chủ thể (HAS_SUBJECT), Hành vi (HAS_ACTION), và Điều kiện (HAS_CONDITION). Cấu trúc này giữ trọn vẹn ngữ cảnh lồng ghép phức tạp mà biểu diễn đồ thị nhị phân truyền thống không thể thể hiện được.

---

## 3.8. HỢP NHẤT ĐỒ THỊ VÀ NẠP DỮ LIỆU TỐC ĐỘ CAO (MODULE 8 & MODULE 9)

### 3.8.1. Cơ chế hợp nhất tầng kép, định danh lũy đẳng MD5 và thanh trừng Token (Module 8)

Module 8 chịu trách nhiệm dung hợp Đồ thị Cấu trúc Vật lý ($\mathcal{G}_P$) và Đồ thị Ngữ nghĩa ($\mathcal{G}_S$) thành Đồ thị Tri thức Thống nhất (Unified Knowledge Graph - UKG). Kiến trúc áp dụng nguyên lý thanh trừng cục bộ (Semantic Pruning) nhằm tối ưu hóa chi phí token cho các truy vấn suy luận tiếp theo: loại bỏ hoàn toàn các thực thể trung gian mang tính cục bộ () và thuộc tính văn bản thô khỏi Tầng Ngữ nghĩa.

Các khẳng định quy phạm rời rạc được nâng cấp thành các nút trung tâm mang nhãn  thông qua hàm băm tất định (Deterministic Hashing) trên bộ thuộc tính nhận diện:

10ID(Norm) = 	ext{MD5}\left(ID_{subj} \mathbin{\Vert} ID_{act} \mathbin{\Vert} 	ext{Sort}(ID_{cond})ight)10

Hàm băm tất định MD5 đảm bảo tính lũy đẳng (Idempotency): dù tiến hành tiền xử lý lại nhiều lần, mã định danh của quy phạm vẫn cố định tuyệt đối, triệt tiêu rủi ro trùng lặp nút khi nạp lại dữ liệu.

Đồng thời, trọng số của cạnh ngữ nghĩa $ được tính toán phản ánh tần suất xuất hiện quy phạm trong bộ luật (Statutory Prevalence):

10w(r) = \left| source\_node\_ids(r) ight|10

Mối liên kết giữa quy phạm trừu tượng và văn bản gốc được duy trì duy nhất qua mảng con trỏ định tuyến , thiết lập một cấu trúc chỉ mục ngược (Inverted Index) hoàn chỉnh giữa Tầng 2 và Tầng 1.

**Cơ chế Tự chẩn đoán và Phát hiện Xung đột Quy phạm (Context Collapse Detection):**

Khác biệt với các hệ thống đồ thị tĩnh, Module 8 tích hợp thuật toán kiểm định bất biến logic trước khi xuất bản đồ thị. Hệ thống nhóm toàn bộ các nút  theo cặp định danh $. Khi phát hiện tồn tại đồng thời hai mệnh đề quy phạm có cùng chủ thể và cùng hành vi nhưng mang tính chất nghĩa vụ đối nghịch (ví dụ: tồn tại song song cờ  và ), thuật toán sẽ kích hoạt cơ chế truy quét điều kiện. Nếu cặp quy phạm trên không sở hữu các cạnh rẽ nhánh điều kiện () hoặc ngoại lệ () để phân lập phạm vi áp dụng, hệ thống sẽ xác định đây là hiện tượng Sụp đổ Ngữ cảnh (Context Collapse) do lỗi trích xuất. Thay vì tự ý loại bỏ dữ liệu, Module 8 tự động đánh dấu cờ cảnh báo  kèm trạng thái  vào siêu dữ liệu (metadata), cung cấp bằng chứng để mô hình suy luận tại Module 10 nhận diện điểm mù thông tin thay vì sinh ảo giác pháp lý.

### 3.8.2. Kiến trúc nạp dữ liệu tốc độ cao qua bộ đệm RAM và Native Unpacking (Module 9)

Nhằm triệt tiêu độ trễ I/O và rủi ro thất thoát dữ liệu ngầm (Silent Data Drop) từ các truy vấn hợp nhất phức tạp trên cơ sở dữ liệu, Module 9 triển khai quy trình nạp dữ liệu tốc độ cao (Fast-Path Ingestion). Tính toàn vẹn cấu trúc của các cạnh quan hệ được thẩm định trước trên bộ nhớ RAM thông qua thuật toán tra cứu tập hợp thời gian thực (1)$ (In-memory Set Lookup). Các cạnh khuyết đầu mút sẽ được chuyển hướng sang Hàng đợi Cách ly (Dead Letter Queue - DLQ) độc lập để phục vụ kiểm toán mà không làm gián đoạn tiến trình ghi dữ liệu.

**Dọn dẹp không gian tên cách ly:** Để đảm bảo tính lũy đẳng (Idempotent) cấp cơ sở dữ liệu khi cập nhật các phiên bản luật mới mà không để lại nút hay cạnh mồ côi, Module 9 thực thi quy trình dọn dẹp không gian tên theo mã luật:

10	ext{Cypher: } 	exttt{MATCH (n:UKG\_NODE \{law\_code: $law\_code\}) DETACH DELETE n}10

Kết hợp với lệnh , cơ chế này triệt tiêu hoàn toàn nguy cơ trùng lặp dữ liệu khi nạp lại.

Toàn bộ thuộc tính thực thể được giải nén trực tiếp thành các thuộc tính bản địa (Native Properties) của cơ sở dữ liệu đồ thị Neo4j thông qua cú pháp , loại bỏ hoàn toàn thuộc tính đóng chuỗi . Đồng thời, hệ thống tự động kích hoạt hệ thống chỉ mục lai:

* **Vector Index:** Khai báo trên trường  ở Tầng 1 phục vụ tìm kiếm véc-tơ tương đồng.
* **B-Tree Index:** Khai báo trên các thuộc tính , ,  ở Tầng 2 phục vụ tra cứu Cypher tốc độ cao tại Module 10.

---

## 3.9. THIẾT KẾ GIAO THỨC TRUY XUẤT ĐỐI CHỨNG VÀ THIẾT LẬP BIẾN KIỂM SOÁT (MODULE 10)

Để kiểm chứng định lượng tác động của cấu trúc đồ thị đề xuất đối với độ chính xác ngữ cảnh (RQ4) mà không bị nhiễu bởi các thuật toán tối ưu hóa prompt phức tạp, Module 10 thiết lập một giao thức thực nghiệm có kiểm soát (Controlled Experimental Protocol) với các thành phần được cố định nghiêm ngặt:

* **Thành phần kiểm soát bất biến (Control Invariants):** Cùng sử dụng mô hình LLM Reader cố định (gpt-4o), tham số nhiệt độ sinh  = 0$, khung Prompt đồng nhất và giới hạn ngữ cảnh trích xuất tối đa  = 2048$ tokens.
* **Cơ chế Truy xuất Đối chứng (Ablation Retrieval Modes):** Module 10 vận hành song song hai chiến lược duyệt đồ thị để đo lường giá trị gia tăng của cấu trúc :
  * **Chế độ A - Truy xuất Nhận thức Quy phạm (NormAssertion-Aware Traversal):** Từ nút mỏ neo vật lý ở Tầng 1, hệ thống kích hoạt đường dẫn con trỏ định hướng lội thẳng lên trạm trung chuyển  tương ứng ở Tầng 2, sau đó mở rộng chính xác các nhánh  và . Chiến lược này bảo toàn ngữ cảnh điều kiện của luật và tối ưu hóa token.
  * **Chế độ B - Truy xuất Hình học Vét cạn (Naive K-hop Traversal):** Đóng vai trò baseline đối chứng, hệ thống thực thi thuật toán duyệt đồ thị truyền thống trong bán kính  = 2$ bước nhảy từ nút mỏ neo, thu thập cơ học toàn bộ các nút lân cận mà không phân biệt vai trò ngữ nghĩa của cạnh.

Sự chênh lệch về hiệu năng QA giữa Chế độ A và Chế độ B tại Module 11 sẽ cung cấp bằng chứng thực nghiệm trực tiếp chứng minh tính ưu việt của kiến trúc phân tầng đề xuất.

---

## 3.10. HỆ THỐNG CHỈ SỐ ĐO LƯỜNG TOÁN HỌC (EVALUATION METRICS)

Nghiên cứu thiết lập hệ thống chỉ số đánh giá toán học đa tầng, phân định rõ ràng giữa Đánh giá Cấu trúc Vật lý và Đánh giá Trích xuất Ngữ nghĩa nhằm tránh lỗi giao tập hợp rỗng giữa hai không gian đỉnh rời nhau.

### 3.10.1. Đánh giá Cấu trúc Vật lý (Physical Tree Evaluation)

Đo lường độ chính xác của cây phân cấp do Tuyến Tĩnh (M2–M4) sinh ra ($\mathcal{V}_{phys}^{pred}$) so với cây cấu trúc chuẩn của chuyên gia ($\mathcal{V}_{phys}^{GT}$):

10P_{phys} = rac{\leftert{} \mathcal{V}_{phys}^{pred} \cap \mathcal{V}_{phys}^{GT} ightert{}}{\leftert{} \mathcal{V}_{phys}^{pred} ightert{}}, \quad R_{phys} = rac{\leftert{} \mathcal{V}_{phys}^{pred} \cap \mathcal{V}_{phys}^{GT} ightert{}}{\leftert{} \mathcal{V}_{phys}^{GT} ightert{}}, \quad F_{1, phys} = rac{2 \cdot P_{phys} \cdot R_{phys}}{P_{phys} + R_{phys}}10

### 3.10.2. Đánh giá Trích xuất Ngữ nghĩa (Semantic Entity/Relation Evaluation)

Đo lường độ chính xác của tập thực thể và quan hệ ngữ nghĩa do Tuyến Động (M6–M7) trích xuất ($\mathcal{E}_{sem}^{pred}$) so với tập chú giải quy phạm chuẩn của chuyên gia pháp lý ($\mathcal{E}_{sem}^{GT}$):

10P_{sem} = rac{\leftert{} \mathcal{E}_{sem}^{pred} \cap \mathcal{E}_{sem}^{GT} ightert{}}{\leftert{} \mathcal{E}_{sem}^{pred} ightert{}}, \quad R_{sem} = rac{\leftert{} \mathcal{E}_{sem}^{pred} \cap \mathcal{E}_{sem}^{GT} ightert{}}{\leftert{} \mathcal{E}_{sem}^{GT} ightert{}}, \quad F_{1, sem} = rac{2 \cdot P_{sem} \cdot R_{sem}}{P_{sem} + R_{sem}}10

### 3.10.3. Đánh giá Tối ưu Chi phí và Chất lượng RAGAS

**Tỷ lệ Tiết kiệm Token (Token Savings Rate - TSR):** Đo lường tỷ lệ phần trăm token đầu vào được cắt giảm nhờ cơ chế định tuyến của Module 5 so với việc xử lý vét cạn toàn bộ văn bản:

10TSR = \left( 1 - rac{\sum_{v \in \mathcal{V}_{cand}} T_{len}(v)}{\sum_{u \in \mathcal{V}_{all}} T_{len}(u)} ight) 	imes 100\%10

trong đó {len}(v)$ là độ dài token của phân đoạn văn bản $.

**Tỷ lệ Duy trì Độ phủ Định tuyến (Cumulative Recall Rate - CRR):** Đo lường tỷ lệ các nút chứa quy phạm quan trọng không bị bỏ sót bởi Module 5.

**Bộ chỉ số RAGAS (RAG Assessment Metrics):** Đo lường chất lượng ứng dụng QA End-to-End ở Module 11 bao gồm: *Context Precision*, *Context Recall*, *Faithfulness* (Độ trung thực chống ảo giác), và *Answer Relevance* (Độ phù hợp của câu trả lời) (Es et al., 2023).

---

## 3.11. GIỚI HẠN NGHIÊN CỨU VÀ PHÂN TÍCH MỐI ĐE DỌA (THREATS TO VALIDITY)

* **Tính tổng quát hóa bên ngoài (External Validity):** Đề tài tiến hành đánh giá chuyên sâu trên tập dữ liệu thử nghiệm biên độ phức tạp tối đa (*Worst-case Pilot Corpus*) gồm 222 nút vật lý thuộc Chương III Luật Đất đai 2024. Mặc dù tập dữ liệu này bao hàm đầy đủ các thách thức kỹ pháp điển hình (5 tầng phân cấp, mật độ dẫn chiếu chéo cao, điều kiện lồng ghép phức tạp), việc mở rộng và đánh giá chéo trên các văn bản thuộc lĩnh vực pháp lý khác (như Luật Doanh nghiệp, Bộ luật Dân sự) là cần thiết để khẳng định tính phổ quát tuyệt đối của bộ luật quy tắc.
* **Định kiến trong đo lường (Construct Validity):** Việc đánh giá đồ thị ngữ nghĩa dựa trên sự khớp nối chính xác (Exact Match) giữa các cạnh trích xuất và Ground Truth có thể quá khắt khe đối với các trường hợp LLM diễn đạt đồng nghĩa nhưng hợp lệ. Nghiên cứu đã kiểm soát rủi ro này bằng cách tích hợp bộ chuẩn hóa 3 tầng và đánh giá bổ sung qua khung RAGAS End-to-End.
* **Độ tin cậy nội tại của dữ liệu chuẩn (Internal Validity):** Quá trình xây dựng tập Ground Truth có thể chịu tác động từ góc nhìn chủ quan của chuyên gia pháp lý. Đề tài đã cô lập nguy cơ này thông qua quy trình gán nhãn độc lập kép và chỉ chấp nhận tập dữ liệu khi đạt chỉ số đồng thuận liên gán nhãn ở mức rất cao ($\kappa = 0.86 - 0.91$).
* **Độ tin cậy của thuật toán gán nhãn chuyên gia (Reliability & Human Annotation Validity):** Mặc dù quy trình gán nhãn đạt độ đồng thuận cao, việc đối soát chéo độc lập và cơ chế hội đồng trọng tài phân giải bất đồng vẫn được duy trì như một tiêu chuẩn bắt buộc nhằm loại bỏ định kiến cá nhân của từng chuyên gia thẩm định.

---

## TÀI LIỆU THAM KHẢO (REFERENCES)

Chen, P., Zhang, L., & Liu, Y. (2023). Legal Knowledge Graph Construction and Reasoning: A Comprehensive Survey. *IEEE Transactions on Knowledge and Data Engineering*, 35(8), 8120-8138.

Edge, D., Trinh, H., Cheng, X., Bradley, J., Chao, A., Mody, A., Truitt, S., & Larson, J. (2024). From Local to Global: A GraphRAG Approach to Query-Focused Summarization. *arXiv preprint arXiv:2404.16130*.

Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. *arXiv preprint arXiv:2310.11511*.

GraphRAG-Router. (2026). Cost-aware Semantic Routing for Multi-tenant Knowledge Graphs. *Technical Report, LegalAI Research Lab*.

Hoekstra, R., Breuker, J., Bello, M., & Boer, A. (2007). The LKIF Core Ontology of Basic Legal Concepts. *Proceedings of the Workshop on Legal Ontologies and Artificial Intelligence Techniques (LOAIT)*, 43-63.

Hohfeld, W. N. (1913). Some Fundamental Legal Conceptions as Applied in Judicial Reasoning. *Yale Law Journal*, 23(1), 16-59.

Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.

Neo4j Inc. (2024). *Neo4j Graph Database Manual v5.x: Developer Guides and Cypher Reference*. Neo4j Documentation.

Nguyen, H. T., Tran, D. K., & Pham, V. O. (2024). VLegal-Bench: A Comprehensive Benchmark for Vietnamese Legal Document Processing and Reasoning. *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 1024-1038.

Qwen Team. (2024). Qwen2.5: A Comprehensive Technical Report on Small Language Models for Reasoning and Extraction. *arXiv preprint arXiv:2409.12117*.

Valente, A., & Breuker, J. (1994). ON-LINE: An Architecture for Legal Information Systems. *Proceedings of the 5th International Conference on Artificial Intelligence and Law (ICAIL)*, 311-320.

Yepes, A. J., Martinez, R., & MacAvaney, S. (2024). Normative Structure Extraction from Statutory Texts using Deontic Constraints. *Artificial Intelligence and Law*, 32(2), 215-245.

Zheng, L., Chiang, W. L., Sheng, Y., Li, S., Zhuang, Z., Wu, Z., ... & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems (NeurIPS)*, 36, 46595-46623.
