# BẢN HIỆU CHÍNH TOÀN DIỆN MỤC 3.1: MODULE 5 (ĐỊNH TUYẾN NGỮ NGHĨA)
*(Tài liệu đề xuất thay thế toàn bộ Mục 3.1 trong Báo cáo nội dung 3 của tác giả Nguyễn Bình Minh)*

---

## 3.1. Module 5 - Định tuyến ngữ nghĩa (Semantic Router)

### 3.1.1. Mục tiêu và nguyên tắc thiết kế bất đối xứng

Module 5 đóng vai trò là tầng định tuyến quyết định (Decision Layer), đánh dấu điểm chuyển tiếp giữa tuyến tiền xử lý cấu trúc vật lý tĩnh (Module 1 đến Module 4) và tuyến trích xuất tri thức ngữ nghĩa động (Module 6). Nhiệm vụ của Module 5 là phân tích từng nút pháp lý và phân loại thành ba nhóm xử lý chuyên biệt:

- **`LLM_CANDIDATE`:** Những đơn vị pháp lý mang ngữ nghĩa phức tạp (chứa đựng điều kiện thi hành, trường hợp ngoại lệ, chế tài áp dụng hoặc các liên kết dẫn chiếu chéo ngầm định) cần chuyển sang Module 6 để bóc tách thực thể và quan hệ bằng mô hình ngôn ngữ lớn.
- **`RULE_ONLY`:** Những đơn vị thuần túy mang chức năng phân cấp và tiêu đề (như tiêu đề Chương, tên Mục hoặc các Điều luật khung không chứa quy phạm trực tiếp), được duy trì để phục vụ việc liên kết cấu trúc phả hệ.
- **`REJECT`:** Những đơn vị có nội dung quy phạm độc lập, không chứa các cấu trúc dẫn chiếu hoặc điều kiện phụ thuộc phức tạp, không cần thiết phải đưa vào mô hình ngôn ngữ lớn nhằm tối ưu hóa chi phí vận hành.

Quá trình thiết kế Module 5 tuân thủ nghiêm ngặt hai nguyên tắc bất biến mang tính nền tảng:

1. **Bảo toàn cấu trúc đồ thị (Immutable Graph Invariant):** Việc một nút nhận nhãn `REJECT` chỉ mang ý nghĩa từ chối chuyển nút đó sang khâu trích xuất quan hệ ngữ nghĩa ở Module 6, tuyệt đối **không xóa bỏ hoặc làm thay đổi nút đó trong đồ thị vật lý**. Toàn bộ các nút pháp lý đã được chuẩn hóa từ Module 4 vẫn tồn tại nguyên vẹn trên cơ sở dữ liệu đồ thị Neo4j nhằm bảo đảm tính toàn vẹn của dữ liệu gốc phục vụ khâu truy vấn sau này.
2. **Nguyên tắc phân loại bất đối xứng (Asymmetric Routing Principle):** Module 5 không giải quyết bài toán phân loại nhị phân đối xứng thông thường. Bản chất của Module 5 là bài toán **Tối ưu hóa có ràng buộc (Constrained Cost Optimization)**:
   $$\min \text{Cost (Số lượng ứng viên đưa vào LLM)} \quad \text{với điều kiện} \quad \text{Recall} \ge \text{Target}$$
   Trong bài toán nạp dữ liệu pháp luật, hai loại sai số có giá trị phạt hoàn toàn bất đối xứng:
   - *Dương tính giả (False Positive - FP):* Một nút văn bản đơn giản bị phân loại nhầm thành `LLM_CANDIDATE`. Hậu quả chỉ là tốn thêm một lượng nhỏ chi phí token suy luận tại Module 6; trong khi đó, Module 6 vẫn sở hữu cơ chế phòng vệ (zero-hallucination guardrail) để trả về mảng quan hệ rỗng `[]`.
   - *Âm tính giả (False Negative - FN):* Một nút chứa quy phạm ràng buộc hoặc dẫn chiếu chéo bị phân loại nhầm thành `REJECT`. Hậu quả là **chí mạng (Catastrophic Loss)** — mối liên kết pháp lý bị đứt gãy vĩnh viễn, không thể phục hồi trên đồ thị tri thức, làm sai lệch kết quả suy luận của toàn bộ hệ thống RAG ở tầng ứng dụng. Do đó, thiết kế hệ thống bắt buộc phải ưu tiên triệt tiêu tối đa âm tính giả (False Negative), chấp nhận tỷ lệ dương tính giả nhất định để bảo toàn tri thức.

---

### 3.1.2. Phương pháp kết hợp tín hiệu từ vựng và ngữ nghĩa (Max-Fusion)

Để hạn chế rủi ro bỏ sót thông tin pháp lý, Module 5 kết hợp đồng thời hai nguồn tín hiệu độc lập:

#### a) Tín hiệu A: Nhận diện biểu thức chính quy (Semantic Pattern Registry)
Hệ thống sử dụng tập hợp các mẫu biểu thức chính quy nhằm phát hiện các chỉ dấu từ vựng (lexical cues) đặc trưng của văn bản quy phạm pháp luật:
- Nhóm dẫn chiếu chéo (Cross-reference): `"theo quy định tại"`, `"căn cứ khoản"`, `"quy định tại Điều"`.
- Nhóm ngoại lệ (Exception): `"trừ trường hợp"`, `"ngoại trừ"`, `"trừ khi"`.
- Nhóm điều kiện (Condition): `"trong trường hợp"`, `"khi đáp ứng điều kiện"`.

Mỗi mẫu hình được định nghĩa kèm trọng số cường độ ($strength$). Theo đó, các mẫu mang tính chất dẫn chiếu và ngoại lệ tường minh được gán trọng số tuyệt đối $w = 1,0$; các mẫu điều kiện mang tính phụ trợ được gán trọng số $w = 0,4$. Điểm Regex của nút thứ $i$ là giá trị lớn nhất trong các mẫu khớp:
$$S_{\text{regex}, i} = \max \{w_p \mid p \in M_i\}$$
Nếu không phát hiện bất kỳ mẫu nào, $S_{\text{regex}, i} = 0$.

#### b) Tín hiệu B: Đo lường độ tương đồng ngữ nghĩa mỏ neo (Anchor Semantic Similarity)
Biểu thức chính quy chỉ có thể bắt được các chuỗi ký tự tường minh cố định, hoàn toàn bất lực trước các diễn ngôn pháp lý ngầm định. Để khắc phục điểm yếu này, Module 5 triển khai kỹ thuật đo khoảng cách ngữ nghĩa đến tập mỏ neo (Anchor Vectors):
- Xây dựng tập hợp 10 câu văn mỏ neo mẫu đại diện cho các hành vi pháp lý, điều kiện và dẫn chiếu đặc thù trong luật Việt Nam.
- Mã hóa nội dung văn bản của nút $i$ thành vector đặc trưng $v_i$ và tính toán độ tương đồng Cosine chuẩn hóa với từng vector mỏ neo $a_j$:
$$S_{\text{semantic}, i} = \max_j \frac{v_i \cdot a_j}{\|v_i\| \|a_j\|}$$

#### c) Chiến lược kết hợp Max-Fusion và Cạm bẫy của hàm Average
Thay vì sử dụng phép lấy trung bình cộng thường thấy trong các bài toán dung hòa đa mô thức, Module 5 bắt buộc phải áp dụng chiến lược **Max-Fusion**:
$$S_{\text{fusion}, i} = \max(S_{\text{regex}, i}, S_{\text{semantic}, i})$$

*Cơ sở toán học và thực tiễn của lựa chọn này xuất phát từ việc nhận diện **Cạm bẫy của hàm Average (The Average Penalty Trap)**:*
Nếu sử dụng hàm trung bình $\text{Average}(S_{\text{regex}}, S_{\text{semantic}})$, trong trường hợp một điều luật chứa quy định dẫn chiếu tinh vi hoặc ngoại lệ ngầm định mà Regex không nhận diện được ($S_{\text{regex}} = 0,0$), dù mô hình biểu diễn ngữ nghĩa bắt được rất chuẩn xác với điểm số cao ($S_{\text{semantic}} = 0,96$), điểm tổng hợp vẫn bị kéo tụt xuống mức:
$$S_{\text{fusion}} = \frac{0,0 + 0,96}{2} = 0,48$$
Khi hệ thống áp dụng bất kỳ ngưỡng phân loại nào lớn hơn $0,50$, nút pháp lý quan trọng này sẽ lập tức bị phân loại vào nhóm `REJECT`, tạo ra một lỗi âm tính giả (False Negative) không thể cứu vãn. Ngược lại, Max-Fusion chuyển hóa cơ chế dung hòa từ phép "thỏa hiệp trung bình" thành logic "bù khuyết" mang tính bảo hiểm (OR logic):
- Nếu Regex phát hiện từ khóa cứng ($S_{\text{regex}} = 1,0$), nút đó chắc chắn được bảo vệ an toàn để chuyển sang Module 6.
- Nếu Regex bị bỏ sót, tầng ngữ nghĩa dày đặc đóng vai trò tấm lưới cứu vớt các quy phạm tiềm ẩn.

---

### 3.1.3. Cơ sở thực nghiệm lựa chọn mô hình và hiện tượng bão hòa điểm số

#### a) Đánh giá đa mô hình và Phát kiến Causal LLM as Embedder
Để xác định giải pháp biểu diễn vector tối ưu cho bài toán định tuyến pháp lý, nhóm nghiên cứu đã triển khai thực nghiệm đối sánh quy mô lớn trên nền tảng phần cứng Kaggle (NVIDIA Tesla T4x2). Quá trình thực nghiệm khảo sát 10 mô hình thuộc 4 nhóm trường phái:
1. **Nhóm Causal LLM as Embedder:** `Qwen2.5-0.5B`, `Qwen2.5-1.5B`, `Qwen2.5-3B`.
2. **Nhóm Embedding chuyên dụng thế hệ mới:** `Qwen3-Embedding-0.6B`, `Qwen3-Embedding-4B`, `Qwen3-Embedding-8B`.
3. **Nhóm Baseline đa ngôn ngữ chuẩn mực:** `BGE-M3`, `Multilingual E5-Large`.
4. **Nhóm Tối ưu hóa tiếng Việt chuyên miền:** `BKAI-VN` (fine-tune trên dữ liệu pháp luật Zalo), `AITeamVN-V2` (fine-tune trên 1,1 triệu triplets tiếng Việt).

Thực nghiệm được thực hiện trên tập kiểm thử Golden Set gồm 193 nút pháp lý đã qua quy trình làm sạch nghiêm ngặt (loại bỏ các tiêu đề chương mục, các nút lỗi phân đoạn và các nhãn trung gian chưa xác định), bao gồm 127 mẫu dương tính (cần trích xuất ngữ nghĩa) và 66 mẫu âm tính.

Trong thiết kế sơ khởi, nhóm dự kiến sử dụng mô hình embedding chuyên dụng `Qwen3-Embedding-0.6B`. Tuy nhiên, trong quá trình vận hành trên Kaggle, một phát hiện thực nghiệm mang tính bước ngoặt đã xuất hiện: Khi thư viện `sentence-transformers` nạp mô hình sinh ngôn ngữ nhân quả (Causal LLM) `Qwen2.5-0.5B`, hệ thống tự động bóc tách các trạng thái ẩn chưa gộp (unpooled hidden states) ở tầng giải mã cuối cùng và kết hợp phép tổng hợp Mean Pooling.

Kết quả đối sánh cho thấy mô hình Causal LLM siêu nhẹ `Qwen2.5-0.5B` đạt khả năng phân tách ranh giới ngữ nghĩa pháp lý vượt trội hơn tất cả các mô hình Bi-Encoder chuyên dụng khác.

*Bảng 3.1. Kết quả đối sánh các mô hình biểu diễn ngữ nghĩa với chiến lược Max-Fusion trên tập kiểm thử (193 nút).*

| Nhóm mô hình | Tên mô hình khảo sát | Số lượng tham số | Recall tại biên tối ưu | Precision tại biên | F1-score cực đại |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Causal LLM** | **Qwen2.5-0.5B (Causal)** | **0,5 tỷ** | **96,85%** | **70,29%** | **0,8146** |
| Multilingual | BGE-M3 | 0,57 tỷ | 100,00% | 65,80% | 0,7938\* |
| Multilingual | E5-Large | 0,56 tỷ | 100,00% | 65,80% | 0,7938\* |
| Causal LLM | Qwen2.5-1.5B (Causal) | 1,5 tỷ | 100,00% | 65,80% | 0,7938\* |
| Causal LLM | Qwen2.5-3B (Causal) | 3,0 tỷ | 100,00% | 65,80% | 0,7938\* |
| Tiếng Việt | AITeamVN-V2 | 0,57 tỷ | 94,49% | 66,67% | 0,7809 |
| Embedding | Qwen3-Embedding-8B | 8,0 tỷ | 92,91% | 66,29% | 0,7713 |
| Embedding | Qwen3-Embedding-0.6B | 0,6 tỷ | 92,13% | 66,48% | 0,7705 |
| Embedding | Qwen3-Embedding-4B | 4,0 tỷ | 90,55% | 65,71% | 0,7606 |
| Tiếng Việt | BKAI-VN | 0,11 tỷ | 82,68% | 61,76% | 0,7071 |

*\*Ghi chú: Giá trị F1-score 0,7938 trùng lặp giữa các mô hình xuất phát từ hiện tượng bão hòa nâng điểm Regex tại ngưỡng 0,80.*

#### b) Giải mã hiện tượng bão hòa nâng điểm của Regex (Regex Elevation Saturation)
Số liệu tại Bảng 3.1 ghi nhận hiện tượng 4 mô hình khác biệt về quy mô và cấu trúc (`BGE-M3`, `E5-Large`, `Qwen2.5-1.5B`, `Qwen2.5-3B`) cùng cho ra một giá trị F1-score cực đại duy nhất là `0,7938`. 

Hiện tượng này được giải thích bởi cơ chế toán học của Max-Fusion: Tại dải ngưỡng thấp ($0,75 - 0,80$), tín hiệu Regex ($w = 1,0$) đã tự động kéo toàn bộ các nút chứa từ khóa pháp lý lên mức điểm tuyệt đối, bảo đảm thu hồi hầu hết mẫu dương tính nhưng đồng thời cũng kéo theo một lượng mẫu âm tính chứa từ khóa tương tự. Do đó, điểm số của các mô hình này bị bão hòa tại cùng một tập điểm True Positive và False Positive.

Chỉ duy nhất `Qwen2.5-0.5B` duy trì được khả năng phân hóa ngữ nghĩa sắc nét ở dải ngưỡng cao hơn ($0,85$), giúp hệ thống loại bỏ được thêm 17 mẫu dương tính giả mà chỉ làm rơi rớt 4 mẫu dương, bứt phá lên mức F1-score $0,8146$. Năng lực này đến từ khả năng nén ngữ cảnh sâu sắc của kiến trúc sinh nhân quả (Causal Language Model), hạn chế được hiện tượng bão hòa khoảng cách Cosine vốn thường xảy ra trên các kiến trúc Bi-Encoder truyền thống khi tiếp xúc với các văn bản quy phạm có độ tương đồng từ vựng cao.

Kết hợp yếu tố chất lượng phân tách và hiệu năng tài nguyên (chỉ 0,5 tỷ tham số, cho phép suy luận cục bộ cực nhanh trên phần cứng phổ thông), `Qwen2.5-0.5B` được lựa chọn làm mô hình biểu diễn ngữ nghĩa chính thức cho Module 5.

---

### 3.1.4. Lựa chọn ngưỡng vận hành dựa trên Biên Pareto (Cost-Recall Frontier)

#### a) Bác bỏ phương pháp luận tối đa hóa F1-score đối xứng
Trong nhiều hệ thống học máy truyền thống, ngưỡng quyết định thường được chọn tại vị trí đạt F1-score cực đại. Tuy nhiên, như đã phân tích tại Mục 3.1.1, bài toán định tuyến Module 5 không cho phép đánh đổi mất mát tri thức để lấy độ tinh gọn token một cách cơ học. 

Nếu chỉ chăm chăm tối đa hóa F1-score, hệ thống có nguy cơ hy sinh Recall tại những điểm mà Precision tăng nhẹ. Do đó, phương pháp luận thực sự được nhóm áp dụng là **Xác định điểm vận hành tối ưu trên Biên Pareto (Pareto-optimal Frontier) của Đường cong Chi phí - Độ phủ (Cost-Recall Curve)**. Trục hoành biểu thị Chi phí ($Cost$ = tổng số lượng ứng viên phải gửi sang LLM) và trục tung biểu thị Độ phủ ($Recall$ = tỷ lệ thu hồi các quy định pháp lý phức tạp).

Quá trình quét ngưỡng được thực hiện chi tiết từ $0,30$ đến $1,00$ với bước tăng $0,05$ trực tiếp trên mảng phân phối điểm kết hợp (Joint Fusion Distribution) nhằm tránh sai lầm chuyển giao ngưỡng từ nhánh đơn lẻ (Regex Elevation Trap).

*Bảng 3.2. Đánh đổi thực nghiệm giữa Chi phí và Độ phủ của Qwen2.5-0.5B kết hợp Max-Fusion.*

| Ngưỡng (Threshold) | Số ứng viên chuyển giao (Cost) | Tỷ lệ giảm tải Token | Recall | Precision | True Positive | False Negative | Đánh giá vận hành |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0,80** | 192 / 193 | 0,52% | 100,00% | 66,15% | 127 | 0 | Giữ tuyệt đối dữ liệu nhưng không giảm được chi phí |
| **0,85** | **175 / 193** | **9,33%** | **96,85%** | **70,29%** | **123** | **4** | **Điểm vận hành tối ưu trên biên Pareto** |
| **0,90** | 122 / 193 | 36,79% | 71,65% | 74,59% | 91 | 36 | Rơi vào "vực thẳm Recall", làm mất 32 mẫu dương |
| **0,95** | 69 / 193 | 64,25% | 54,33% | 100,00% | 69 | 58 | Đứt gãy nghiêm trọng tính toàn vẹn pháp lý |

#### b) Phân tích "Vực thẳm Recall" (Recall Drop-off Cliff) và Xác lập Ngưỡng 0,85
Dữ liệu thực nghiệm tại Bảng 3.2 chỉ ra ranh giới đánh đổi kỹ thuật mang tính quyết định:
- Khi vận hành ở dải ngưỡng **0,80**, hệ thống thu hồi 100% tri thức nhưng gần như không có tác dụng lọc (chỉ giảm được đúng 1 nút, chuyển tiếp 192/193 nút sang LLM).
- Khi nâng ngưỡng lên **0,85**, hệ thống giảm được 17 ứng viên (giảm tải 9,33% số nút của tập kiểm thử), trong khi vẫn duy trì mức Recall xuất sắc là **96,85%** (thu hồi trọn vẹn 123/127 nút phức tạp, chỉ bỏ lọt 4 trường hợp ranh giới).
- Tuy nhiên, khi tiếp tục nâng ngưỡng lên **0,90**, một hiện tượng đứt gãy nghiêm trọng xảy ra: **Hiện tượng "Vực thẳm Recall" (Recall Drop-off Cliff)**. Dù chi phí token giảm mạnh (chỉ còn 122 ứng viên), nhưng Recall lập tức rơi tự do từ $96,85\%$ xuống chỉ còn $71,65\%$, làm phát sinh thêm tới **32 trường hợp âm tính giả (False Negative)**. Việc đánh mất gần 30% các quy phạm có chứa điều kiện và ngoại lệ là điều tối kỵ, không thể chấp nhận được trong một hệ thống hỏi đáp căn cứ pháp lý.

Do đó, điểm ngưỡng **0,85** được chính thức xác lập làm điểm vận hành (Operating Point) chuẩn mực cho toàn bộ hệ thống. Điểm vận hành này thỏa mãn đồng thời ba tiêu chí:
1. Nằm vững chắc trên biên Pareto, tối ưu hóa chi phí với ràng buộc an toàn $\text{Recall} \ge 95\%$.
2. Đứng ngay trước bờ dốc của "vực thẳm Recall", tận dụng tối đa khả năng sàng lọc mà không kích hoạt rủi ro mất mát dữ liệu quy mô lớn.
3. Bảo toàn tính đơn điệu toán học (Monotonicity Invariant), bảo đảm hệ thống vận hành có thể giải trình và tái lập hoàn toàn.

---

### 3.1.5. Tổ chức triển khai và Kết quả thực thi trên Chương III Luật Đất đai 2024

Module 5 được đóng gói thành một pipeline xử lý độc lập, phân tách trách nhiệm thông qua 5 thành phần cốt lõi:
- `semantic_router.py`: Bộ điều phối chính (Orchestrator), quản lý luồng dữ liệu từ đồ thị vật lý sang các bộ lọc.
- `routing_engine.py`: Bộ tính điểm kết hợp, chịu trách nhiệm thực thi biểu thức chính quy và phép hợp nhất Max-Fusion.
- `embedding_engine.py`: Bộ máy vector hóa, quản lý mô hình Qwen2.5-0.5B và thực hiện phép tính Cosine tương đồng với bộ mỏ neo bằng mã nguồn NumPy tối ưu hóa.
- `threshold_controller.py`: Bộ kiểm soát ngưỡng cắt, áp dụng điểm vận hành $0,85$ đã được kiểm chứng.
- `candidate_selector.py`: Đóng gói kết quả đầu ra theo đúng lược đồ hợp đồng dữ liệu Pydantic (`routing_candidates.json`) để bàn giao cho Module 6.

*Bảng 3.3. Kết quả định tuyến thực tế của Module 5 trên toàn bộ Chương III Luật Đất đai 2024.*

| Nhóm phân loại đầu ra | Số lượng nút | Tỷ lệ phần trăm | Ý nghĩa xử lý trong hệ thống |
| :--- | :---: | :---: | :--- |
| **`LLM_CANDIDATE`** | **180** | **80,72%** | Chuyển tiếp sang Module 6 để bóc tách thực thể và quan hệ bằng LLM |
| **`RULE_ONLY`** | **6** | **2,69%** | Duy trì trong đồ thị để bảo toàn liên kết phân cấp cha - con |
| **`REJECT`** | **37** | **16,59%** | Không gọi LLM; nội dung văn bản gốc vẫn lưu giữ đầy đủ trên Neo4j |
| **Tổng số nút đánh giá** | **223** | **100,00%** | **Toàn bộ 223 nút được bảo toàn nguyên vẹn trên đồ thị vật lý** |

Trên toàn bộ ngữ liệu Chương III Luật Đất đai 2024 gồm 223 nút pháp lý sau khi tiếp nhận từ Module 4, Module 5 đã định tuyến chính xác:
- **180 nút** được xác định là ứng viên mang ngữ nghĩa phức tạp cần xử lý bằng mô hình ngôn ngữ lớn.
- **43 nút** được sàng lọc thành công khỏi khâu trích xuất LLM (gồm 6 nút cấu trúc `RULE_ONLY` và 37 nút quy phạm đơn giản `REJECT`), giúp **tiết kiệm 19,28% chi phí gọi API và thời gian tính toán của Module 6**.
- Toàn bộ 223 nút pháp lý cùng hệ thống cạnh cấu trúc vẫn được nạp đầy đủ vào đồ thị Neo4j, bảo đảm hệ thống không bị mất mát bất kỳ phân đoạn văn bản nào khi người dùng thực hiện truy vấn trực tiếp.

Kết quả này khẳng định Module 5 đã hoàn thành xuất sắc vai trò làm tầng quyết định thông minh: vừa tối ưu hóa đáng kể chi phí vận hành cho các mô hình ngôn ngữ lớn ở tầng sau, vừa thiết lập một tấm lưới bảo vệ vững chắc để bảo toàn toàn vẹn tri thức pháp luật Việt Nam.

