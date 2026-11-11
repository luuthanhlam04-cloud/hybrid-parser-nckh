# PHỤ LỤC A. THỰC NGHIỆM ĐỐI SÁNH VÀ TỐI ƯU HÓA MODULE 5 (SEMANTIC ROUTER)

---

### A.1. Mục tiêu định tuyến và chiến lược kết hợp tín hiệu cú pháp - ngữ nghĩa
Module 5 phân loại các nút từ đồ thị vật lý (Physical Graph) thành ba nhánh xử lý: `LLM_CANDIDATE` (chuyển sang Module 6 để bóc tách thực thể và quan hệ), `RULE_ONLY` (duy trì cấu trúc phả hệ) và `REJECT` (văn bản thuần thủ tục hành chính). Do việc bỏ sót căn cứ pháp lý (sai số âm tính giả - FN) dẫn đến nguy cơ đứt gãy quan hệ logic vĩnh viễn trên đồ thị tri thức (UKG), hệ thống thiết lập bài toán tối ưu hóa chi phí có ràng buộc với hàm phạt sai số bất đối xứng ($c_{\text{FN}} \gg c_{\text{FP}}$):

$$\min \text{Cost} \quad \text{với điều kiện} \quad \text{Recall} \ge 95\%$$

Hệ thống kết hợp tín hiệu hình thức cú pháp $S_{\text{regex}}$ (biểu thức chính quy) và tín hiệu không gian ngữ nghĩa $S_{\text{semantic}}$ (độ tương đồng cosine cực đại với 10 phát ngôn mỏ neo pháp lý). Thực nghiệm ghi nhận hiện tượng phạt điểm của hàm trung bình (Average Penalty Trap): Nếu sử dụng phép lấy trung bình cộng $S_{\text{avg}} = 0,5 \cdot S_{\text{regex}} + 0,5 \cdot S_{\text{semantic}}$, khi một điều luật chứa quy phạm ngầm định không xuất hiện từ khóa cứng ($S_{\text{regex}} = 0$), dù mô hình nhúng nhận diện được tính quy phạm ($S_{\text{semantic}} = 0,94$), điểm tổng hợp vẫn bị kéo xuống mức $0,47$, khiến nút bị phân loại nhầm vào `REJECT`. Để khắc phục, hệ thống áp dụng toán tử Max-Fusion theo nguyên lý tuyển logic (cổng OR):

$$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{semantic}})$$

Toán tử này bảo đảm các nút chứa từ khóa tường minh được bảo toàn tuyệt đối, đồng thời cho phép tín hiệu vector bổ khuyết các quy phạm tiềm ẩn mà không bị giảm điểm do sự vắng mặt của từ khóa.

---

### A.2. Kết quả đối sánh mô hình biểu diễn ngữ nghĩa và cơ sở lựa chọn Qwen2.5-0.5B
Để đánh giá độc lập năng lực của tầng vector, nhóm nghiên cứu thực hiện khảo sát theo chiến lược Embed-Only (loại bỏ hoàn toàn tín hiệu biểu thức chính quy) trên tập kiểm chuẩn Golden Set v2 gồm 193 nút pháp lý (trong đó có 127 nút dương tính chứa quy phạm cần bóc tách). Kết quả đối sánh được trình bày tại Bảng A.1.

**Bảng A.1. So sánh năng lực biểu diễn ngữ nghĩa độc lập (chiến lược Embed-Only)**

| Nhóm kiến trúc | Mô hình đối chuẩn | Số tham số | Ngưỡng $\theta$ | Recall | Precision | F1-Score | Số nút chuyển M6 (Cost) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Causal LLM** | **Qwen2.5-0.5B (Causal)** | **0,5B** | **0,85** | **0,9370** | **0,6959** | **0,7987** | **171 / 193** |
| Dense Bi-encoder | BGE-M3 | 0,57B | 0,30 | 1,0000 | 0,6580 | 0,7937 | 193 / 193 (Không lọc) |
| Dense Bi-encoder | Multilingual E5-Large | 0,56B | 0,30 | 1,0000 | 0,6580 | 0,7937 | 193 / 193 (Không lọc) |
| Dense Bi-encoder | Qwen3-Embedding-0.6B | 0,6B | 0,30 | 0,4646 | 0,7195 | 0,5646 | 82 / 193 (Bỏ sót 54%) |
| Dense Bi-encoder | Qwen3-Embedding-8B | 8,0B | 0,30 | 0,3307 | 0,8077 | 0,4693 | 52 / 193 (Bỏ sót 67%) |
| Dense Bi-encoder | AITeamVN-V2 | 0,11B | 0,30 | 0,3071 | 0,6000 | 0,4062 | 65 / 193 |
| Dense Bi-encoder | BKAI-VN (Law tuned) | 0,11B | 0,30 | 0,0787 | 0,9091 | 0,1449 | 11 / 193 (Bỏ sót 92%) |

*Cơ sở khoa học giải thích kết quả:*
1. **Lệch pha mục tiêu huấn luyện và hạn chế của phép gộp trung bình (Mean Pooling):** Các mô hình Bi-encoder được tối ưu hóa bằng hàm mất mát tương phản (Contrastive Loss) cho bài toán tìm kiếm văn bản theo chủ đề (Document Retrieval). Trong phạm vi hẹp của Chương III Luật Đất đai, phần lớn các điều luật đều có độ trùng lặp từ vựng cao, dẫn đến hiện tượng vướng víu chủ đề (Topic Entanglement) và làm bão hòa điểm số. Đồng thời, phép gộp trung bình vector (Mean Pooling) làm phẳng cấu trúc ngữ pháp tuần tự, làm mất tính bất đối xứng của mệnh đề điều kiện pháp lý. Ngay cả mô hình quy mô lớn Qwen3-Embedding-8B cũng suy thoái Recall xuống mức 33,07% do các tầng biểu diễn trừu tượng làm loãng tín hiệu cú pháp vi mô.
2. **Ưu thế cấu trúc của cơ chế chú ý nhân quả (Causal Attention):** Mô hình Qwen2.5-0.5B được huấn luyện tự hồi quy dự đoán từ kế tiếp, buộc trạng thái ẩn của bộ giải mã (decoder) phải mô hình hóa trật tự phụ thuộc logic: Chủ thể $\rightarrow$ Điều kiện (Nếu/Trừ khi) $\rightarrow$ Chế tài (Thì/Phải). Khi áp dụng kỹ thuật LLM-as-Embedder, vector trích xuất từ tầng giải mã cuối nắm bắt sắc nét các mệnh đề ràng buộc trạng thái ngoại sinh (State Conditions như *"đã được thi hành án"*, *"phù hợp với pháp luật"*), giúp mô hình tự thân đạt Recall 93,70% mà không cần quy tắc từ khóa hỗ trợ.
3. **Cơ sở lựa chọn biến thể 0,5 tỷ tham số:** Thực nghiệm đối sánh mở rộng cho thấy các biến thể lớn hơn (Qwen2.5-1.5B và 3B) xuất hiện hiện tượng liên tưởng ngữ nghĩa quá rộng (Semantic Over-generalization), phân loại 192/193 nút vào nhóm cần xử lý và làm mất khả năng sàng lọc. Ngược lại, việc cắt giảm tham số trên kiến trúc Bi-encoder (như BKAI-VN 0,11B) dẫn đến suy thoái biểu diễn (Recall chỉ đạt 7,87%). Do đó, biến thể 0,5B là điểm cân bằng kỹ thuật phù hợp giữa năng lực phân tích cú pháp và độ phân hóa ranh giới phân loại.

---

### A.3. Phân tích điểm gãy và giới hạn phạm vi của ngưỡng θ = 0,85
Do không gian biểu diễn decoder-only có mức độ tập trung điểm số cao (phần lớn điểm tương đồng cosine phân bố trong dải $[0,75; 0,98]$), ranh giới quyết định thực tế của mô hình tập trung trong khoảng $[0,80; 0,95]$.

**Bảng A.2. Diễn tiến chỉ số của Qwen2.5-0.5B (Max-Fusion) qua các ngưỡng quyết định**

| Ngưỡng $\theta$ | Số nút chuyển (Cost) | Recall | Precision | F1-Score | TP | FP | TN | FN | Đánh giá trạng thái vận hành |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0,80 | 192 | 1,0000 | 0,6615 | 0,7962 | 127 | 65 | 1 | 0 | Dải ngưỡng thấp: Giữ nguyên độ phủ nhưng tỷ lệ lọc thấp (chỉ loại 1 nút) |
| **0,85** | **175** | **0,9685** | **0,7029** | **0,8146** | **123** | **52** | **14** | **4** | **Điểm cân bằng tối ưu: Recall 96,85%, F1 đạt đỉnh, giảm 9,33% lượng phân đoạn** |
| 0,90 | 122 | 0,7165 | 0,7459 | 0,7309 | 91 | 31 | 35 | 36 | Dải suy giảm mạnh: Recall giảm 25,2 điểm phần trăm (bỏ sót 36 nút) |
| 0,95 | 69 | 0,5433 | 1,0000 | 0,7041 | 69 | 0 | 66 | 58 | Dải thoái hóa: Mất hiệu lực của tầng vector, bỏ sót 58 nút quy phạm |

*Cơ sở lựa chọn ngưỡng và giới hạn phạm vi nghiên cứu:*
* **Cơ sở lựa chọn:** Tại ngưỡng $\theta = 0,80$, hệ thống gần như không giảm tải (chuyển tiếp 192/193 nút). Khi nâng lên $\theta = 0,85$, hệ thống đạt điểm cân bằng tối ưu: F1-score đạt đỉnh 0,8146, giảm 18 nút chuyển sang Module 6 (tương đương giảm 9,33% khối lượng xử lý, loại bỏ 14 nút thủ tục) trong khi vẫn duy trì Recall ở mức 96,85% (bảo toàn 123/127 nút quy phạm, chỉ bỏ sót 4 trường hợp biên không trọng yếu). Khi nâng ngưỡng lên $\theta = 0,90$, Recall suy giảm đột ngột xuống 71,65% (bỏ sót 36 nút quy phạm), vi phạm mục tiêu an toàn tri thức.
* **Giới hạn phạm vi nghiên cứu (Scope Limitation):** Ngưỡng vận hành $\theta = 0,85$ được xác lập dựa trên phân phối thực nghiệm cụ thể của Chương III Luật Đất đai 2024. Báo cáo không khẳng định cấu hình này áp dụng đồng nhất cho mọi văn bản pháp luật. Khi mở rộng sang các ngữ liệu đa ngành luật có văn phong khác biệt (như Luật Hình sự hoặc Luật Doanh nghiệp), phân phối điểm tương đồng có thể dịch chuyển (hiện tượng trôi ngưỡng - Threshold Drift) và hệ thống cần thực hiện lại quy trình quét ngưỡng tương ứng.

---

### A.4. Nguyên tắc bảo toàn cấu trúc đồ thị vật lý (Immutable Graph Invariant)
Toàn bộ các nút mang nhãn `REJECT` chỉ bị từ chối chuyển sang Module 6 nhằm tối ưu hóa chi phí suy luận, hoàn toàn không bị loại bỏ khỏi hệ thống. Dữ liệu văn bản gốc của các nút này vẫn được lưu trữ nguyên vẹn trong đồ thị vật lý và cơ sở dữ liệu Neo4j nhằm phục vụ công tác truy hồi dự phòng tại Module 10 khi người dùng truy vấn các nội dung mang tính quy trình, thủ tục hành chính.
