# Tái Cấu Trúc Hệ Thống UKG Ingestion (M8-M9): Giải Quyết Bài Toán Silent Data Loss và Bảo Toàn Invariants Đồ Thị Pháp Luật

*Tài liệu này tổng hợp toàn bộ tri thức từ quá trình đánh giá (Danh Gia M9), lập kế hoạch (Ke Hoach Fix M8 M9), phản biện kỹ thuật sâu, và nghiệm thu (M8 M9 Walkthrough). Tài liệu phục vụ như một ghi chú kiến trúc hệ thống, đồng thời cung cấp bối cảnh học thuật cho quá trình viết luận văn về hệ thống Hybrid Parser GraphRAG.*

---

## 1. Giới Thiệu và Bối Cảnh Lịch Sử (Context & Motivation)

Trong kiến trúc Hybrid Parser GraphRAG, module M8 (Unified Knowledge Graph Fusion) và M9 (Neo4j Ingestion) đóng vai trò là "Cầu nối Dữ liệu" (Data Bridge). M8 chịu trách nhiệm hợp nhất (fuse) các tri thức từ M7 (Canonical Graph) và các thực thể để tạo ra một UKG hoàn chỉnh. M9 có nhiệm vụ vật lý hóa (materialize) UKG này lên hệ quản trị cơ sở dữ liệu đồ thị Neo4j.

**Sự kiện kích hoạt (Triggering Event):** Trong một đợt kiểm thử dữ liệu nội bộ, hệ thống đối mặt với một tình trạng nguy hiểm: **Silent Data Loss (Thất thoát dữ liệu thầm lặng)**. Cụ thể:
- Ở M8: Hệ thống ghi nhận 102 Norms từ M7 là hợp lệ (VALID), nhưng UKG sinh ra chỉ chứa 77 hub `GLOBAL_NORM`.
- Ở M9: Quá trình Ingest node thành công (331/331), nhưng quá trình Ingest Edge hoàn toàn thất bại (0/1142 edges) mà log hệ thống không hề ném ra bất kỳ Exception hay Error nào.

Bài toán đặt ra không chỉ là fix bug lập trình, mà là tái cấu trúc lại toàn bộ cơ chế bảo vệ, kiểm toán (accounting), và duy trì tính toàn vẹn (integrity invariants) của dữ liệu xuyên suốt pipeline.

---

## 2. Phân Tích Nguyên Nhân Cốt Lõi (Root Cause Analysis)

Việc thất thoát dữ liệu chia làm hai điểm nghẽn (bottleneck) ở hai tầng kiến trúc khác nhau, đòi hỏi những cách tiếp cận hoàn toàn trái ngược.

### 2.1. Tầng M8: Rò Rỉ Partial Norm (I5 Invariant Failure)
Đi sâu vào file `m7_adapter.py`, thuật toán Fusion ban đầu được thiết kế xung quanh một cụm vòng lặp lồng nhau (nested loops) duyệt qua tổ hợp `subject_ids` × `action_ids`.

* **Lỗ hổng Logic:** Quy phạm pháp luật chứa rất nhiều "Quy phạm khuyết hành động" (Partial Norms / Action-less Norms). Đây là các quy phạm thuần túy định danh hoặc trao quyền chung (VD: "Cơ quan Thuế là cơ quan ngang bộ"). Ở dạng này, `subject_ids` có giá trị nhưng `action_ids` là rỗng (`[]`). Vòng lặp `for action_id in action_ids` không bao giờ được kích hoạt, kéo theo việc toàn bộ Subject bị "rớt" khỏi đồ thị mà không để lại dấu vết.
* **Tác hại:** GraphRAG sau này sẽ hoàn toàn bị mù thông tin về các nút "Thẩm quyền" do các liên kết `HAS_SUBJECT` bị đứt gãy từ gốc.

### 2.2. Tầng M9: Silent Drop Qua Cơ Chế Cypher MERGE
Ở tầng Database, file `cypher_generator.py` sinh ra câu lệnh `EDGE_BATCH` sử dụng mệnh đề `MATCH` để bind hai đầu endpoint trước khi dùng `MERGE` tạo cạnh.

* **Bản chất của MATCH:** Trong Neo4j, `MATCH` hoạt động như một bộ lọc (Filter), không phải là một bộ kích hoạt ngoại lệ (Exception trigger). Nếu một trong hai endpoint không tồn tại trong DB, hệ quả Descartes (Cartesian product) sẽ trả về rỗng, khiến row dữ liệu đang duyệt bị âm thầm hủy bỏ khỏi transaction.
* **Bất cập của Neo4j ResultSummary:** Dữ liệu trả về từ Neo4j (như `relationships_created`) chỉ là các Metric Tổng hợp (Aggregate Counters). Hệ thống chỉ biết "đã tạo thành công X cạnh", nhưng hoàn toàn bất lực trong việc trả lời câu hỏi: *"Trong Y cạnh đầu vào, bao nhiêu cạnh thất bại do trùng lặp (Already Exists), bao nhiêu cạnh thất bại do thiếu Source/Target?"*

---

## 3. Kiến Trúc Giải Pháp & Quy Trình Triển Khai (Implementation & Trade-offs)

Hệ thống đã trải qua 6 Phase tái cấu trúc, áp dụng triệt để nguyên lý "Phòng vệ chiều sâu" (Defense-in-depth) và xử lý cặn kẽ các phản biện kỹ thuật.

### 3.1. Phục Hồi Partial Norm và Xác Lập Ánh Xạ 1:N (Phase 1)
- **Thiết kế lại luồng Adapter:** Bổ sung nhánh rẽ (branching) riêng biệt trong `m7_adapter.py` để "bắt" các trường hợp `subject_ids != []` và `action_ids == []`. Các norm này được gán nhãn `PARTIAL` và đưa vào hệ thống với cấu trúc nội bộ `target=None`.
- **Trade-off nội bộ:** Giá trị `None` này thuần túy là một "placeholder" trong bộ nhớ Python để vượt qua thuật toán Hash-Fusion của M8, hoàn toàn không được dịch thành một Null-Endpoint Edge vô nghĩa trên Neo4j.
- **Sửa sai kiến trúc Cardinality:** Một điểm nghẽn nhận thức ban đầu là ánh xạ 1:1 giữa M7 Norm và M8 `GLOBAL_NORM`. Thực tế, cơ chế Deduplication (băm MD5 các thuộc tính) biến ánh xạ này thành **1:N**. Rất nhiều norm ID từ M7 có thể chia sẻ chung một node `GLOBAL_NORM` trên UKG.

### 3.2. Per-Row Edge Accounting & Mutually Exclusive States (Phase 2)
Để giải quyết bài toán Silent Drop, toàn bộ triết lý Ingestion đã được thay đổi.
- **Giải pháp Cypher:** Chuyển từ `MATCH` sang `OPTIONAL MATCH` kết hợp subquery `CALL { ... } UNION` của Neo4j 5.x. Kỹ thuật này ép Cypher phải tính toán và trả về (yield) tình trạng của TỪNG DÒNG (Per-row status) thay vì chỉ trả summary tổng.
- **Toán học hóa Accounting:** Thu thập dữ liệu thành 6 trạng thái độc lập (`created`, `already_exists`, `missing_source`, `missing_target`, `missing_both`, `execution_failed`).
- **Assertion Code-level (Phản biện thực thi):** Để biến "Ghi log chi tiết" thành "Hệ thống tự kiểm chứng", một câu lệnh `assert` cứng đã được nhúng vào `neo4j_ingestor.py`.
  > `Invariant: attempted == SUM(6_trang_thai_mutually_exclusive)`
  Nếu sự kiện mất mát xảy ra khiến phương trình này mất cân bằng, toàn bộ pipeline sẽ bị bẻ gãy (`RuntimeError`) ngay lập tức, ngăn chặn việc leo thang dữ liệu hỏng.

### 3.3. Xây Dựng Cổng Kiểm Duyệt Completeness Gate (Phase 3)
Cổng kiểm duyệt được chèn vào trước bước Ingestion để khóa lại dữ liệu.
- **Deep Tracking (Phản biện Kỹ thuật):** Việc đếm tổng số node vật lý (`source_node_ids`) không đảm bảo tính toàn vẹn, vì 1 Điều Luật (Physical Node) có thể sinh ra 3 Norms. Nếu M8 làm rớt 1 Norm, phép đếm physical node vẫn không đổi.
- **Cơ chế:** Kỹ thuật mapping truy ngược (`prov_to_norms`) được sử dụng để phân rã `provenance_node_id` về đúng cấp độ `norm_id` duy nhất. Completeness Gate chỉ PASSED khi 100% `norm_id` VALID từ M7 đều nằm gọn trong các túi `source_node_ids` của UKG.

### 3.4. Sự Phân Lập Invariants Đồ Thị & Semantic Logic (Phase 4)
Bộ máy `GraphChecker` được cấu trúc lại, phân rạch ròi 2 dạng Invariant:
1. **Structural Invariants:** (`BELONG_TO`, `NEXT`). Cấu trúc không gian của văn bản bắt buộc phải là DAG. Bài test consistency chiều ngược lại (A NEXT B $\Leftrightarrow$ B PREVIOUS A) được bổ sung.
2. **Norm Context Invariants:** (`HAS_CONDITION`, `HAS_EXCEPTION`). *Insight Học Thuật:* Ta không khẳng định logic pháp lý ngoài đời thực cấm chu trình (vì văn bản luật vẫn có thể có mâu thuẫn chéo). Tuy nhiên, ta khẳng định **Graph Schema Invariant**: Trong giới hạn của mô hình biểu diễn này, việc tạo ra chu trình ngữ cảnh được coi là "Lỗi Trích Xuất" (Extraction Error) từ LLM và cần phải bị chặn. Biến số `SEMANTIC_ACYCLIC_EDGES` đã được đổi tên chính xác thành `NORM_CONTEXT_ACYCLIC_EDGES` để phản ánh đúng tư duy này.

### 3.5. Graceful Downgrade cho Tương Thích Cypher Labels (Phase 5)
- **Kiểm định Factual:** Neo4j hỗ trợ tính năng dynamic label `SET n:$(...)` bắt đầu từ phiên bản 5.24. Tuy nhiên, môi trường Cloud hiện tại (AuraDB 5.x) chưa hoàn toàn tương thích/cập nhật phiên bản này.
- **Giải pháp:** Áp dụng mô hình Python-Allowlist. Thay vì ép Cypher chạy dynamic query, script Python đối chiếu label đầu vào với Ontology Schema nội bộ, sau đó generate ra query cứng (Hard-coded node label). Điều này vừa tạo ra tính tương thích ngược (Backward Compatibility) vĩnh viễn, vừa loại trừ rủi ro Cypher Injection khi Label được chiết xuất tự do từ AI.

---

## 4. Giá Trị Học Thuật & Đóng Góp Hệ Thống (Academic Insights)

Toàn bộ quy trình tái thiết M8-M9 mang lại 2 giá trị học thuật lõi để tích hợp vào báo cáo luận văn:

### 4.1. Sự Dịch Chuyển Sang "Self-Verifying ETL Pipeline"
Các hệ thống Knowledge Graph truyền thống thường áp dụng Ingestion theo dạng "Mù" (Fire-and-forget). Hệ thống hiện tại đã tiến hóa thành "Đóng vòng kiểm chứng" (Closed-loop Validation). Bằng việc đẩy `GraphChecker` lên thành Gatekeeper ở mọi Phase, kết hợp với toán học hóa Per-row Accounting, pipeline đảm bảo dữ liệu đưa vào GraphRAG là tinh khiết 100% về mặt cấu trúc, triệt tiêu mọi khả năng gây Hallucination do "đứt gãy đồ thị".

### 4.2. Tính Lũy Đẳng (Idempotency) Ở Cấp Độ Đồ Thị (Phase 6)
Kết quả E2E Ingestion Test (Test số 7) đã chứng minh vững chắc tính lũy đẳng của workload hiện tại:
- **Run 1:** Attempted 1142, Created 1142.
- **Run 2:** Attempted 1142, Created 0, Already Exists 1142.

**Luận điểm:** Quá trình Ingestion của hệ thống giờ đây hoạt động như một hàm số đơn điệu (Monotonic Function). Trạng thái của Graph không phụ thuộc vào số lần chạy lại của pipeline. Điều này cung cấp khả năng Chịu lỗi (Fault-tolerance) vô cùng mạnh mẽ: Nếu quá trình batching gặp sự cố đứt kết nối mạng giữa chừng, hệ thống có thể an tâm Retry toàn bộ luồng dữ liệu mà không sợ làm ô nhiễm đồ thị bởi các Edge hay Node bị nhân bản (Duplicate Ghost Entities). Pipeline đạt trạng thái hoàn thiện tuyệt đối để làm bệ phóng cho lớp Tri thức GraphRAG phía trên.

## 5. Hạn Chế Kiến Trúc & Định Hướng Tương Lai (Limitations & Future Work)

Bên cạnh những giải pháp đã được chứng minh tính đúng đắn, cấu trúc hiện hành vẫn bộc lộ những điểm "Trade-off" (đánh đổi) mang tính chiến lược. Các vấn đề này được cô lập có chủ đích (By-Design) để ưu tiên tính toàn vẹn dữ liệu cho mô hình nghiên cứu ở giai đoạn hiện tại.

### 5.1. Vấn đề "Nút Thắt Cổ Chai" Hiệu năng (Performance Bottleneck)
* **Thành tựu:** Per-row Accounting và Python-Fallback Labels mang lại độ an toàn tuyệt đối và khả năng log chi tiết trạng thái của từng cạnh.
* **Mặt trái:** Khi scale lên đồ thị hàng triệu node, việc duyệt subquery `CALL { UNION }` cho từng row và vòng lặp gán Label từ Python (N+1 query problem) sẽ tạo ra gánh nặng I/O khổng lồ cho database.
* **Lý do không tối ưu hóa lúc này:** Tối ưu hóa (như dùng `apoc.periodic.iterate`) sẽ đánh đổi bằng việc mất đi bảng log "Per-row Accounting" cực kỳ chi tiết. Đối với quy mô NCKH hiện tại (vài vạn nodes), khả năng Audit và Debug có giá trị cao hơn gấp nhiều lần so với tối ưu tốc độ (Premature Optimization).
* **Hướng giải quyết:** Khi hệ thống thực sự chạm ngưỡng scale, cần dịch chuyển tầng Validation ra khỏi Cypher, xử lý bằng Pandas trên RAM trước khi đưa vào DB, đồng thời áp dụng Neo4j Data Importer cho luồng bulk-load.

### 5.2. Pipeline "Tất cả hoặc Không gì cả" (Brittle Pipeline)
* **Thành tựu:** Completeness Gate chặn đứng mọi rò rỉ dữ liệu thông qua lệnh `RuntimeError`, đảm bảo dữ liệu đưa vào DB luôn là 100% tinh khiết.
* **Mặt trái:** Việc sập toàn bộ luồng Ingestion chỉ vì 1 Norm bị lệch khiến hệ thống trở nên mong manh (thiếu fault-tolerance) trước dữ liệu nhiễu thực tế.
* **Lý do duy trì trạng thái "Mong manh":** Ở giai đoạn tinh chỉnh Parser (M7) và Fusion (M8), tính năng "Fail-fast" (sập ngay lập tức khi có lỗi) là một tấm khiên bảo vệ. Nếu hệ thống âm thầm dung túng lỗi, nhà phát triển sẽ bị ảo tưởng rằng AI đang parse đúng và bỏ sót rác dữ liệu.
* **Hướng giải quyết:** Sau khi M7-M8 đã ổn định hoàn toàn ở môi trường Production, áp dụng kiến trúc **Dead Letter Queue (Hàng đợi cách ly)** để 99.9% dữ liệu đúng được Ingest bình thường, 0.1% dữ liệu lỗi bị đẩy vào Quarantine.

### 5.3. Tính Lũy Đẳng Chỉ Bao Phủ Chiều Tịnh Tiến (Append-Only)
* **Thành tựu:** Đồ thị không sinh ra rác (Duplicate nodes/edges) khi chạy Ingestion lại nhiều lần.
* **Mặt trái:** Hệ thống mù tịt về chiều "Xóa" (Ví dụ: một Điều luật bị bãi bỏ khỏi tập dữ liệu nguồn sẽ không tự động biến mất trên DB). 
* **Lý do không triển khai True Delta Update:** Việc xây dựng cơ chế này đòi hỏi phải tái cấu trúc toàn bộ Schema sang dạng Đồ thị Thời gian (Temporal Graph) với các cờ `valid_from`, `valid_to`, làm phình to scope dự án lên quá mức cần thiết. Với dataset tĩnh hiện tại, việc chạy lại toàn bộ (`--replace`) là phương án tiết kiệm chi phí và an toàn nhất.
* **Hướng giải quyết:** Xây dựng module Delta Management (Hỗ trợ Upsert & Soft-delete) kết hợp lưu vết thời gian.

### 5.4. Xung Đột Giữa Schema Đồ Thị Và Thực Tế Lập Pháp
* **Thành tựu:** GraphChecker cô lập các chu trình ngữ cảnh (`HAS_CONDITION`, `HAS_EXCEPTION`), ngăn ảo giác từ LLM.
* **Mặt trái:** Nếu văn bản luật gốc thực sự có lỗi tự mâu thuẫn chéo, việc ép đồ thị phải Acyclic (DAG) sẽ vô tình làm méo mó Ground Truth (chân lý gốc).
* **Lý do ép buộc Acyclic:** Nếu cho phép đồ thị chứa chu trình, thuật toán duyệt đồ thị (Traversal) của module GraphRAG phía sau có thể bị rơi vào vòng lặp vô hạn (Infinite Loop). Việc "cắt gọt" này là hy sinh Ground Truth để cứu tính ổn định của hệ thống suy luận.
* **Hướng giải quyết:** Thay vì ném lỗi, `GraphChecker` có thể gán cờ `Anomaly` (Bất thường) cho cụm node để GraphRAG nhận diện vùng rủi ro mà không cần xóa bỏ chúng.
