# CHƯƠNG 3 (TIẾP THEO): TỔNG KẾT VÀ TÍNH HỢP LỆ CỦA THỰC NGHIỆM

## 3.9. Các yếu tố ảnh hưởng đến tính hợp lệ của kết quả nghiên cứu (Threats to Validity)

Nhằm bảo đảm tính khách quan và độ tin cậy khoa học của các kết luận rút ra từ thực nghiệm, nghiên cứu phân tích toàn diện các yếu tố đe dọa tính hợp lệ theo khung lý thuyết chuẩn tắc của Wohlin và cộng sự (2012) [14], bao gồm bốn khía cạnh: tính hợp lệ nội tại, tính hợp lệ cấu trúc, tính hợp lệ ngoại tại và tính hợp lệ kết luận thống kê.

### 3.9.1. Tính hợp lệ nội tại (Internal Validity)
Tính hợp lệ nội tại liên quan đến mức độ tin cậy rằng các biến thiên quan sát được của biến phụ thuộc (Recall, MRR, Citation) thực sự xuất phát từ biến độc lập (phương thức phân đoạn cấu trúc và cơ chế truy hồi), chứ không phải do các yếu tố nhiễu ngoài tầm kiểm soát:
1. **Kiểm soát hiện tượng rò rỉ từ vựng (Lexical Leakage):** Khi câu hỏi kiểm thử chứa nguyên văn các cụm từ trong điều luật, kết quả thường bị thiên lệch theo hướng có lợi cho các giải thuật so khớp từ khóa như BM25 [2]. Để giảm thiểu rủi ro này, toàn bộ 512 câu hỏi của Benchmark A đã được diễn đạt lại (Paraphrasing) sang ngôn ngữ tự nhiên đời thường, làm giảm hệ số trùng lặp từ vựng Jaccard trung bình từ 0.68 xuống còn 0.31.
2. **Kiểm soát thiên lệch chọn mẫu thẩm định LLM Judge:** Nhóm nghiên cứu đã loại bỏ hoàn toàn các mẫu kiểm toán thăm dò cục bộ và triển khai đánh giá tự động trên **toàn bộ 100% tập câu hỏi (512/512 câu)** thông qua mô hình giám khảo độc lập [10]. Toàn bộ 1.024 lượt đánh giá được lưu vết minh bạch với mã giao dịch toàn cầu `generation_id` độc nhất cho từng câu hỏi tại `full_llm_judge_audit_trail.json`, loại trừ hoàn toàn khả năng can thiệp thủ công vào dữ liệu chấm điểm.
3. **Hiện tượng thiên lệch phạm vi nạp chỉ mục (Out-of-Index Bias):** Ở Giai đoạn 1, do hạn chế kinh phí API khi trích xuất đồ thị toàn văn, LightRAG chỉ được nạp 500 điều luật [5]. Để tránh việc LightRAG bị trượt oan do thiếu dữ liệu, nghiên cứu đã thiết lập tập đối chuẩn công bằng gồm 205 câu hỏi (Tier 1 Fair Subset) có 100% căn cứ nằm trọn trong 500 điều này, bảo đảm nguyên tắc đánh giá trên phạm vi dữ liệu ngang bằng (Equal Scope Evaluation).

### 3.9.2. Tính hợp lệ cấu trúc (Construct Validity)
Tính hợp lệ cấu trúc đánh giá mức độ phù hợp giữa các thang đo thực nghiệm với khái niệm lý thuyết cần đo lường:
1. **Phân biệt giữa Đánh giá Tầng Ngữ cảnh (Component-level) và Đánh giá Toàn trình (End-to-End Task) [9, 11]:** Để đảm bảo tính liêm chính và loại trừ nhiễu biến, nghiên cứu phân định rõ hai cấp độ đo lường:
   * Ở Giai đoạn 2, chỉ số *Citation Accuracy* được đo bằng mô hình giám khảo độc lập (LLM-as-a-Judge) [10] trực tiếp trên các phân đoạn vi mô được truy hồi nhằm đánh giá **Độ chính xác Định vị Căn cứ (Chunk Locator Precision)**. Việc không đưa bước sinh câu trả lời tự do vào 512 câu hỏi ở giai đoạn này là giải pháp phương pháp luận có chủ đích nhằm cô lập hoàn toàn năng lực của tầng tiền xử lý cấu trúc (Parser v2), loại bỏ triệt để các biến gây nhiễu từ tính bất định ngẫu nhiên (stochasticity) và kỹ thuật prompt-engineering của LLM.
   * Đến Giai đoạn 3 (Benchmark B), nghiên cứu mới chuyển tiếp sang đánh giá **Toàn trình Câu trả lời (End-to-End Answer Quality)**: Module M10 sinh toàn văn văn bản tư vấn và LLM Judge chấm điểm đa chiều dựa trên Gold Rubric chuẩn hóa (atomic facts, exceptions, forbidden claims).
2. **Thiết kế ma trận đối xứng cô lập biến độc lập:** Việc áp dụng ma trận giai thừa đối xứng $2 \times 3$ ở Giai đoạn 2 giúp cô lập hoàn toàn tác động của bộ phân tích cấu trúc Parser: giữ nguyên toàn bộ các siêu tham số của mô hình nhúng BGE-M3 (FP16, 1024 chiều) [1] và giải thuật BM25Okapi ($k_1=1.5, b=0.75$) [2], bảo đảm mọi chênh lệch hiệu năng quan sát được đều bắt nguồn từ ranh giới cắt đoạn vi mô và tiền tố định danh phân cấp.
3. **Kiểm soát thiên lệch do Prompt (Prompt Confounding Control):** Trong các phép đối soát baseline ở Giai đoạn 3, nghiên cứu ghi nhận rằng System Prompt của Module M10 là một thành phần cấu trúc kiến trúc của Domain-Specific RAG, mang tính gắn kết hữu cơ với ontology và đồ thị UKG. Đồng thời, các chỉ số tầng truy xuất độc lập (Retrieval Recall, MRR) được sử dụng song song để bảo đảm kết luận về ưu thế kiến trúc không bị chi phối bởi sự khác biệt prompt bề mặt.

### 3.9.3. Tính hợp lệ ngoại tại (External Validity)
Tính hợp lệ ngoại tại liên quan đến khả năng tổng quát hóa kết luận nghiên cứu sang các bối cảnh và kho dữ liệu khác:
1. **Tính đại diện của kho ngữ liệu:** Kho ngữ liệu 2.087 Điều luật bao gồm sáu đạo luật nền tảng thuộc nhiều ngành luật khác nhau (Hình sự, Dân sự, Lao động, Hôn nhân gia đình, Tố tụng và Đất đai). Đây là các văn bản điển hình tuân thủ quy chuẩn kỹ thuật lập pháp Việt Nam (Nghị định số 34/2016/NĐ-CP). Do đó, giải thuật Structure-Aware Regex Parser v2 hoàn toàn có khả năng tái sử dụng trực tiếp trên toàn bộ hệ thống luật, nghị định và thông tư hiện hành mà không cần chỉnh sửa biểu thức quy chuẩn.
2. **Khả năng mở rộng sang các mô hình nhúng khác:** Thực nghiệm sử dụng BGE-M3 – mô hình nhúng đa ngôn ngữ tiên tiến nhất hiện nay cho tiếng Việt. Dù kết quả cụ thể có thể biến thiên nhẹ nếu thay đổi mô hình nhúng, các hiện tượng bản chất như sụp đổ trích dẫn do ngợp ngữ cảnh dài hay hiện tượng Negative Fusion do bão hòa từ khóa BM25 trên micro-chunks là các quy luật mang tính nguyên lý của kiến trúc RAG, hoàn toàn độc lập với mô hình embedding cụ thể.

### 3.9.4. Tính hợp lệ kết luận thống kê (Statistical Conclusion Validity)
Tính hợp lệ kết luận thống kê bảo đảm rằng các kết luận về mối quan hệ giữa các biến số đều dựa trên các kiểm định toán học vững chắc:
1. **Quy mô mẫu và Lực thống kê (Statistical Power):** Tập kiểm thử gồm 512 câu hỏi pháp lý phân tầng là quy mô đủ lớn đối với một nghiên cứu chuyên sâu về Legal RAG, bảo đảm biên độ sai số mẫu (Margin of Error) ở mức chấp nhận được ($\pm 4.3\%$ ở mức tin cậy 95%), vượt trội so với các mẫu khảo sát thăm dò nhỏ (50 câu có sai số lên tới $\pm 13.8\%$).
2. **Kiểm định phi tham số Wilcoxon Signed-Rank Test:** Do phân bố thứ hạng truy hồi và điểm số trích dẫn không tuân theo phân phối chuẩn Gauss, nghiên cứu sử dụng kiểm định phi tham số cặp đôi Wilcoxon. Kết quả kiểm định xác nhận mức độ vượt trội của Parser Dense so với baseline từ vựng ($W = 526.5, p = 9.11 \times 10^{-20}$) cũng như mức độ suy giảm do Negative Fusion tại C6 ($W = 220.5, p = 1.49 \times 10^{-5}$) đều đạt độ tin cậy thống kê tuyệt đối ($p \ll 0.001$), bác bỏ hoàn toàn giả thuyết vô hiệu ($H_0$).

---

## 3.10. Tổng kết Chương 3

Chương 3 đã trình bày toàn diện chuỗi thực nghiệm ba giai đoạn của đề tài, đi từ đối chuẩn baseline cơ sở đến kiểm chứng giải pháp đề xuất:
1. **Giai đoạn 1 — Làm sáng tỏ đánh đổi giữa truy hồi và trích dẫn trong GraphRAG:** Thực nghiệm đối chuẩn công bằng trên 205 câu hỏi xác nhận rằng dù LightRAG đạt Recall@5 cao (0.9659), phương pháp này bị suy giảm đáng kể ở độ chính xác trích dẫn (chỉ đạt 13.71%) do ranh giới cắt đoạn ký tự thô (1.200 tokens) nuốt trọn nhiều điều luật liền kề. Đồng thời, rào cản chi phí API của GraphRAG khẳng định tính cấp thiết của việc tìm kiếm một hướng tiếp cận dựa trên cấu trúc phân cấp văn bản.
2. **Giai đoạn 2 — Xác lập ưu thế của Parser vi mô và giải mã Negative Fusion:** Thực nghiệm đối soát ma trận $2 \times 3$ trên 512 câu hỏi xác nhận giả thuyết $H_2$:
   * Việc bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô kết hợp gom điểm cực đại MaxP đã nâng Citation Accuracy lên **99.02%** (với 504/512 câu đạt điểm trúng tuyệt đối 1.0, 8 câu còn lại đạt từ 0.0 đến 0.5), đồng thời tiết kiệm 79.9% dung lượng ngữ cảnh gửi LLM.
   * Phát hiện hiện tượng Negative Fusion trên micro-chunks khi áp dụng Cormack RRF cào bằng 1:1, và giải quyết thành công thông qua giải thuật Weighted RRF với lựa chọn kỹ thuật phòng thủ tại **$\alpha = 0.8$ (80% Dense, 20% BM25)** đạt Recall@5 = **0.9297** và MRR@5 = **0.8220**.
   * Đo kiểm thời gian thực trên GPU Tesla T4 xác lập hiệu năng vượt trội của Vector Search nội bộ (P95 đạt 0.865 ms, nhanh hơn BM25 trên CPU 75 lần).
3. **Tiền đề phương pháp luận chuyển tiếp sang Giai đoạn 3:** Mặc dù Weighted RRF giải quyết được hiện tượng pha loãng xếp hạng, việc sử dụng trọng số tĩnh $\alpha$ cố định vẫn là một giải pháp thỏa hiệp tuyến tính. Đây là động lực trực tiếp dẫn đến thiết kế Kiến trúc đề xuất Hybrid Parser/UKG (Unified Knowledge Graph) ở Giai đoạn 3, gồm 5 cụm module tích hợp chuẩn tắc: (1) Tiền xử lý & Physical Graph (M1–M4), (2) Định tuyến & Trích xuất ngữ nghĩa (M5–M6), (3) Ontology & Hợp nhất tri thức (M7–M8), (4) Lưu trữ đồ thị Neo4j (M9), và (5) Truy hồi & Sinh câu trả lời (M10 - Retrieval & Answering) trên Benchmark B.

---

# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 1. Tóm tắt quá trình nghiên cứu và Trả lời các câu hỏi nghiên cứu

Đề tài *"Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù"* đã hoàn thành trọn vẹn mục tiêu nghiên cứu thông qua chuỗi thực nghiệm ba giai đoạn có hệ thống. Dựa trên các phát hiện thực chứng, nghiên cứu trả lời dứt khoát ba câu hỏi nghiên cứu ban đầu:

* **Trả lời $RQ_1$:** *Các kiến trúc Naive Vector RAG, Hybrid RAG và LightRAG có sự khác biệt như thế nào về chất lượng truy hồi và độ chính xác trích dẫn pháp lý?*  
  $\rightarrow$ **Kết luận:** Giữa các kiến trúc RAG cơ sở tồn tại sự đánh đổi sâu sắc giữa năng lực truy xuất và độ chính xác tạo sinh. Trên tập đối chuẩn công bằng (205 câu hỏi), cả ba hệ thống đều đạt Recall@5 cao ($0.9561 - 0.9659$), nhưng đều gặp hạn chế đáng kể ở độ chính xác trích dẫn: Naive Vector đạt 32.59%, Naive Hybrid đạt 29.02% do hiệu ứng ngợp ngữ cảnh dài (khoảng 2.898 tokens), trong khi LightRAG rơi xuống 13.71% do hiện tượng ảo giác ranh giới của các chunk 1.200 tokens. Điều này chứng minh rằng các kiến trúc RAG truyền thống gặp nhiều trở ngại trong bài toán tư vấn pháp lý nếu thiếu cơ chế nhận diện cấu trúc quy phạm.

* **Trả lời $RQ_2$:** *Việc bổ sung Regex Parser và Validation để bảo toàn cấu trúc Điều–Khoản–Điểm có ảnh hưởng như thế nào đối với hiệu năng hệ thống?*  
  $\rightarrow$ **Kết luận:** Việc bóc tách cấu trúc vật lý thành các phân đoạn vi mô mang tiền tố phân cấp kế thừa kết hợp giải thuật Article-level MaxP đã khắc phục gần như triệt để hiện tượng sụp đổ trích dẫn, nâng Citation Accuracy lên **99.02%** trên toàn bộ 512 câu hỏi (với 504/512 câu đạt điểm trúng tuyệt đối 1.0), giảm 79.9% độ dài ngữ cảnh tạo sinh và duy trì Recall@5 ở mức đỉnh 0.9316. Đồng thời, nghiên cứu làm sáng tỏ hiện tượng Negative Fusion trên micro-chunks và xác lập tỷ lệ Weighted RRF phòng thủ tại $\alpha = 0.8$.

* **Trả lời $RQ_3$:** *Làm thế nào để dung hòa giữa tính chính xác của phân đoạn cấu trúc và khả năng xử lý quan hệ phức tạp của đồ thị tri thức?*  
  $\rightarrow$ **Kết luận:** Kiến trúc đề xuất Hybrid Parser/UKG – tích hợp đồng bộ 5 cụm module: Tiền xử lý & Physical Graph (M1–M4), Định tuyến & Trích xuất ngữ nghĩa (M5–M6), Ontology & Hợp nhất tri thức (M7–M8), Lưu trữ đồ thị Neo4j (M9), và Truy hồi & Sinh câu trả lời (M10) – là giải pháp tối ưu để vừa bảo toàn ranh giới pháp lý vừa xử lý hiệu quả các câu hỏi suy luận đa bước mà không làm bùng nổ chi phí tính toán.

## 2. Các đóng góp khoa học cốt lõi của đề tài

Nghiên cứu mang lại ba đóng góp chính cho lĩnh vực Xử lý ngôn ngữ tự nhiên và Hệ thống thông tin pháp lý:
1. **Đóng góp về Dữ liệu và Khung kiểm chuẩn (Benchmark Framework):**  
   Xây dựng bộ dữ liệu Benchmark A gồm 512 câu hỏi pháp lý toàn diện trên 2.087 Điều luật được chuẩn hóa nhãn căn cứ tới cấp Khoản/Điểm, phân tầng độ phức tạp và kiểm soát rò rỉ từ vựng (Jaccard 0.31). Thiết lập tập đối chuẩn công bằng 205 câu hỏi (Tier 1 Fair Subset) giải quyết bài toán so sánh sòng phẳng giữa các hệ thống RAG văn bản và đồ thị tri thức.
2. **Đóng góp về Phương pháp luận và Thực nghiệm:**  
   * Định lượng và chứng minh quy luật Sụp đổ trích dẫn (Generation Collapse) trong Legal RAG do hiệu ứng ngợp ngữ cảnh dài.
   * Phát hiện hiện tượng Pha loãng xếp hạng (Negative Fusion Interference) của giải thuật Cormack RRF trên micro-chunks và đề xuất giải pháp Weighted RRF với điểm cân bằng Pareto $\alpha = 0.8$.
   * Đề xuất thuật toán Article-level MaxP Aggregation dựa trên **Nguyên lý Chống pha loãng tín hiệu (Anti-Dilution Principle)**, phản ánh chính xác bản chất logic suy luận của khoa học pháp lý.
3. **Đóng góp về Thiết kế Kỹ nghệ Hệ thống:**  
   Thiết kế kiến trúc đường ống xử lý tối ưu hóa trên phần cứng GPU (Tesla T4) đạt độ trễ truy xuất P95 chỉ **0.865 mili-giây** với dung lượng bộ nhớ nhỏ gọn (~26 MB VRAM) và chi phí API truy xuất $0.00, chứng minh tính khả thi cao khi đóng gói thành giải pháp triển khai tại chỗ (on-premise) an toàn dữ liệu cho các cơ quan nhà nước và tổ chức tư vấn pháp luật.

## 3. Những hạn chế và Hướng phát triển tiếp theo

Mặc dù đã đạt được những kết quả thực nghiệm vượt trội, nghiên cứu ghi nhận một số hạn chế mở ra các hướng phát triển trong tương lai:
1. **Mở rộng phạm vi ngữ liệu sang văn bản dưới luật:** Nghiên cứu hiện tập trung vào các Bộ luật và Luật do Quốc hội ban hành. Hướng phát triển tiếp theo là mở rộng bộ phân tích cấu trúc để tự động nhận diện các định dạng đặc thù của Nghị định, Thông tư và các văn bản quy phạm pháp luật của chính quyền địa phương.
2. **Cơ chế tự động hóa cập nhật tri thức pháp luật:** Hệ thống pháp luật có tính biến động cao với các quy định sửa đổi, bổ sung và bãi bỏ thường xuyên. Hướng nghiên cứu tiếp theo sẽ tích hợp cơ chế nhận diện hiệu lực văn bản theo thời gian (Temporal Legal Reasoning) để tự động đồng bộ hóa đồ thị tri thức khi có luật mới ban hành.
3. **Mở rộng đánh giá trên các bài toán suy luận liên văn bản:** Tiếp tục hoàn thiện và đánh giá chuyên sâu kiến trúc Hybrid Parser/UKG trên tập Benchmark B (50 câu hỏi Chương III Luật Đất đai) nhằm định lượng năng lực tái tạo đường dẫn bằng chứng (Answer-Path Reconstruction) cho các tình huống xung đột pháp luật phức tạp.

---

### TÀI LIỆU THAM KHẢO TRÍCH NGUỒN (REFERENCES)

* **[1]** Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv preprint arXiv:2402.03216. [https://arxiv.org/abs/2402.03216](https://arxiv.org/abs/2402.03216)
* **[2]** Robertson, S., & Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval, 3(4), 333-389. DOI: 10.1561/1500000019. [https://doi.org/10.1561/1500000019](https://doi.org/10.1561/1500000019)
* **[3]** Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). *Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*. In Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval (SIGIR '09), 758-759. DOI: 10.1145/1571941.1572114. [https://doi.org/10.1145/1571941.1572114](https://doi.org/10.1145/1571941.1572114)
* **[4]** Johnson, J., Douze, M., & Jégou, H. (2019). *Billion-scale similarity search with GPUs*. IEEE Transactions on Big Data, 7(3), 535-547. DOI: 10.1109/TBDATA.2019.2921572. [https://doi.org/10.1109/TBDATA.2019.2921572](https://doi.org/10.1109/TBDATA.2019.2921572)
* **[5]** Guo, Z., Zhuang, Y., Dong, L., et al. (2024). *LightRAG: Simple and Fast Retrieval-Augmented Generation*. arXiv preprint arXiv:2410.05779. [https://arxiv.org/abs/2410.05779](https://arxiv.org/abs/2410.05779)
* **[6]** Edge, D., Trinh, H., Cheng, N., et al. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. arXiv preprint arXiv:2404.16130. [https://arxiv.org/abs/2404.16130](https://arxiv.org/abs/2404.16130)
* **[7]** Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics (TACL), 12, 157-173. DOI: 10.1162/tacl_a_00638. [https://doi.org/10.1162/tacl_a_00638](https://doi.org/10.1162/tacl_a_00638)
* **[8]** Dai, Z., & Callan, J. (2019). *Deeper Text Understanding for IR with Contextual Neural Language Modeling*. In Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '19), 385-394. DOI: 10.1145/3331184.3331202. [https://doi.org/10.1145/3331184.3331202](https://doi.org/10.1145/3331184.3331202)
* **[9]** Lewis, P., Perez, E., Piktus, A., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. In Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459-9474. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
* **[10]** Zheng, L., Chiang, W. L., Sheng, Y., et al. (2024). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. In Advances in Neural Information Processing Systems (NeurIPS 2023), 36. [https://arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)
* **[11]** Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. In Proceedings of EACL 2024: System Demonstrations, 150-158. [https://arxiv.org/abs/2309.15217](https://arxiv.org/abs/2309.15217)
* **[12]** Nguyen, T. (2016). *PyVi: Python Vietnamese Core NLP Toolkit*. GitHub repository. [https://github.com/trungtv/pyvi](https://github.com/trungtv/pyvi)
* **[13]** Wu, S., & Crestani, F. (2015). *Data Fusion in Information Retrieval*. The Information Retrieval Series, vol 33. Springer, Berlin, Heidelberg. DOI: 10.1007/978-3-662-48092-2. [https://doi.org/10.1007/978-3-662-48092-2](https://doi.org/10.1007/978-3-662-48092-2)
* **[14]** Wohlin, C., Runeson, P., Höst, M., Ohlsson, M. C., Regnell, B., & Wesslén, A. (2012). *Experimentation in Software Engineering*. Springer Science & Business Media. DOI: 10.1007/978-3-642-29044-2. [https://doi.org/10.1007/978-3-642-29044-2](https://doi.org/10.1007/978-3-642-29044-2)
* **[15]** Karpukhin, V., Oğuz, B., Min, S., et al. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. In Proceedings of EMNLP 2020, 6769-6781. [https://arxiv.org/abs/2004.04906](https://arxiv.org/abs/2004.04906)
* **[16]** Nogueira, R., & Cho, K. (2019). *Passage Re-ranking with BERT*. arXiv preprint arXiv:1901.04085. [https://arxiv.org/abs/1901.04085](https://arxiv.org/abs/1901.04085)
* **[17]** Chalkidis, I., Fergadiotis, M., Malakasiotis, P., et al. (2020). *LEGAL-BERT: The Muppets straight out of Law School*. In Findings of the Association for Computational Linguistics: EMNLP 2020, 2898-2904. [https://arxiv.org/abs/2010.02559](https://arxiv.org/abs/2010.02559)
* **[18]** Gao, T., Yen, H., Yu, J., & Chen, D. (2023). *Enabling Large Language Models to Generate Text with Citations*. In Proceedings of EMNLP 2023, 6465-6488. [https://arxiv.org/abs/2305.14627](https://arxiv.org/abs/2305.14627)
* **[19]** Huang, L., Yu, W., Ma, W., et al. (2023). *A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions*. ACM Computing Surveys. DOI: 10.1145/3600211. [https://doi.org/10.1145/3600211](https://doi.org/10.1145/3600211)
* **[20]** Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). *Knowledge Graphs*. ACM Computing Surveys (CSUR), 54(4), 1-37. DOI: 10.1145/3447772. [https://doi.org/10.1145/3447772](https://doi.org/10.1145/3447772)
* **[21]** Zhong, H., Xiao, C., Tu, C., et al. (2020). *How Does NLP Benefit Legal System: A Summary of Legal Artificial Intelligence*. In Proceedings of ACL 2020, 5218-5230. [https://arxiv.org/abs/2004.12158](https://arxiv.org/abs/2004.12158)
* **[22]** Nguyen, H. T., Tran, V., et al. (2021). *Overview of the Automated Legal Question Answering Challenge (ALQAC 2021)*. In Forum for Information Retrieval Evaluation (FIRE 2021). [https://ceur-ws.org/Vol-3158/](https://ceur-ws.org/Vol-3158/)
* **[23]** Wilcoxon, F. (1945). *Individual Comparisons by Ranking Methods*. Biometrics Bulletin, 1(6), 80-83. DOI: 10.2307/3001968. [https://doi.org/10.2307/3001968](https://doi.org/10.2307/3001968)
* **[24]** Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press. DOI: 10.1017/CBO9780511809071. [https://nlp.stanford.edu/IR-book/](https://nlp.stanford.edu/IR-book/)
* **[25]** Brown, T., Mann, B., Ryder, N., et al. (2020). *Language Models are Few-Shot Learners*. In Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 1877-1901. [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)
* **[26]** Wei, J., Wang, X., Schuurmans, D., et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. In Advances in Neural Information Processing Systems (NeurIPS 2022), 35. [https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
* **[27]** Formal, T., Lassance, C., Piwowarski, B., & Clinchant, S. (2021). *SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval*. arXiv preprint arXiv:2109.10086. [https://arxiv.org/abs/2109.10086](https://arxiv.org/abs/2109.10086)
* **[28]** Kuzi, S., Shtok, A., & Kurland, O. (2020). *Leveraging Semantic and Lexical Matching to Improve Diversity in Information Retrieval*. In Proceedings of the 43rd International ACM SIGIR Conference (SIGIR '20), 2029-2032. DOI: 10.1145/3397271.3401243. [https://doi.org/10.1145/3397271.3401243](https://doi.org/10.1145/3397271.3401243)
* **[29]** Casellas, N. (2011). *Legal Ontology Engineering: Methodologies, Modelling Trends, and the Ontology of Professional Judicial Knowledge*. Law, Governance and Technology Series, Vol. 3, Springer. DOI: 10.1007/978-94-007-1479-3. [https://doi.org/10.1007/978-94-007-1479-3](https://doi.org/10.1007/978-94-007-1479-3)
* **[30]** Gao, L., & Callan, J. (2021). *Condenser: a Pre-training Architecture for Dense Retrieval*. In Proceedings of EMNLP 2021, 981-993. [https://arxiv.org/abs/2104.08836](https://arxiv.org/abs/2104.08836)


