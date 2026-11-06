# CHƯƠNG 2: THIẾT KẾ HỆ THỐNG VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 2.4. Thiết kế ba kiến trúc RAG cơ sở — Giai đoạn 1

Trong Giai đoạn 1 của đề tài, nghiên cứu thiết kế và triển khai ba kiến trúc RAG cơ sở nhằm khảo sát và đối soát thực nghiệm ba trường phái truy hồi thông tin điển hình trong bài toán hỏi đáp văn bản quy phạm pháp luật [9]:
1. **Truy xuất ngữ nghĩa dày (Dense Semantic Retrieval):** Đại diện bởi kiến trúc Naive Vector RAG dựa trên mô hình nhúng văn bản Bi-Encoder đa ngôn ngữ tiên tiến [1].
2. **Truy xuất lai đa tầng (Multi-stage Hybrid Retrieval):** Đại diện bởi kiến trúc Hybrid RAG kết hợp giữa đối sánh từ khóa thưa [2], truy xuất vector dày [1], giải thuật dung hợp thứ hạng Reciprocal Rank Fusion (RRF) [3] và mô hình tái xếp hạng Cross-Encoder [1].
3. **Truy xuất đồ thị tri thức phi cấu trúc (Unstructured Graph Retrieval):** Đại diện bởi kiến trúc LightRAG [5], khai thác mô hình ngôn ngữ lớn để trích xuất tự động thực thể và mối quan hệ thành mạng lưới đồ thị tri thức hai tầng [6].

Cả ba hệ thống đều được tích hợp vào khung kiểm chuẩn Benchmark Harness thông qua lớp điều hợp chuẩn tắc (`BaseRAGAdapter`), tiếp nhận cùng một tập câu hỏi kiểm thử và sử dụng chung mô hình ngôn ngữ lớn `openai/gpt-4o-mini` (thiết lập `temperature = 0.0`) để sinh câu trả lời có căn cứ.

---

### 2.4.1. Naive Vector RAG (Trường phái Bi-Encoder ngữ nghĩa dày)

Naive Vector RAG được xây dựng làm đường cơ sở thực nghiệm (Baseline) đại diện cho phương pháp tìm kiếm ngữ nghĩa thuần túy dựa trên không gian vector nhúng. 

* **Mô hình hóa biểu diễn:** Toàn bộ kho ngữ liệu gồm 2.087 Điều luật được đưa vào mô hình Bi-Encoder `BAAI/bge-m3` [1] (độ dài vector biểu diễn 1.024 chiều, kiểu dữ liệu dấu phẩy động FP16). Mô hình này sở hữu kiến trúc tự chú ý sâu (Self-Attention) với khả năng nắm bắt ngữ nghĩa đa ngữ và xử lý độ dài ngữ cảnh tối đa lên tới 8.192 tokens.
* **Cơ chế phân đoạn văn bản:** Theo chuẩn tắc của Naive RAG, mỗi tài liệu pháp lý (cấp Điều luật) được đưa vào mô hình dưới dạng khối văn bản thô nguyên trạng (Raw Text Block). Hệ thống không áp dụng các bộ phân tích cú pháp lập pháp chuyên biệt để bóc tách cấu trúc nội tại của Điều thành các Khoản và Điểm.
* **Lập chỉ mục và truy vấn:** Toàn bộ các vector nhúng của ngữ liệu sau khi được chuẩn hóa độ dài ($L_2$-normalized) được nạp vào cấu trúc chỉ mục `FAISS IndexFlatIP` [4] (Facebook AI Similarity Search - Inner Product). Khi nhận một câu hỏi $q$, hệ thống mã hóa $q$ thành vector $\vec{v}_q$, sau đó thực hiện tính tích vô hướng Cosine Similarity song song trên toàn bộ không gian vector:
  $$\text{sim}(q, d) = \langle \vec{v}_q, \vec{v}_d \rangle$$
* **Tổng hợp ngữ cảnh:** Hệ thống lựa chọn $Top\text{-}k$ ($k=5$) tài liệu có điểm tương đồng ngữ nghĩa cao nhất để ghép thành chuỗi ngữ cảnh gửi sang LLM tạo sinh câu trả lời.

*Nhận xét đặc tính:* Naive Vector RAG có ưu thế lớn về tốc độ tính toán nhờ khả năng song song hóa ma trận trên GPU. Tuy nhiên, việc coi mỗi Điều luật là một khối văn bản đồng nhất khiến hệ thống dễ bị mất mát thông tin khi xử lý các câu hỏi vi mô chỉ cần căn cứ vào một Điểm hẹp nằm sâu trong một điều luật dài.

---

### 2.4.2. Hybrid RAG (Trường phái Dung hợp Thứ hạng Đa tầng)

Nhằm khắc phục hiện tượng mất mát từ khóa chính xác (chẳng hạn như tên tội danh, mức phạt tiền cụ thể, mốc thời gian luật định) của phương pháp vector thuần túy, kiến trúc Hybrid RAG kết hợp hai nhánh truy xuất bổ trợ lẫn nhau, sau đó tiến hành dung hợp thứ hạng và tái sắp xếp:

* **Nhánh truy xuất từ vựng (Sparse Lexical Retrieval):** Sử dụng giải thuật Okapi BM25 (`rank_bm25`) [2]. Trước khi lập chỉ mục chỉ mục nghịch đảo (Inverted Index), toàn bộ câu hỏi và văn bản điều luật được chuẩn hóa và tách từ tiếng Việt tự động thông qua thư viện `pyvi.ViTokenizer` [12]. Việc phân tách từ ngữ pháp lý chuẩn (ví dụ: *"hôn_nhân_thực_tế"*, *"chiếm_hữu_ngay_tình"*) giúp giải thuật Okapi BM25 bắt chính xác các cụm thuật ngữ đặc thù mà mô hình nhúng vector có xu hướng làm mờ.
* **Nhánh truy xuất ngữ nghĩa (Dense Semantic Retrieval):** Sử dụng mô hình `BAAI/bge-m3` [1] và chỉ mục `FAISS IndexFlatIP` [4] hoàn toàn tương đồng với Naive Vector RAG để bảo đảm tính đối chuẩn công bằng.
* **Cơ chế dung hợp thứ hạng Reciprocal Rank Fusion (RRF):** Với mỗi câu hỏi, hệ thống trích xuất danh sách $N = 50$ ứng viên hàng đầu từ nhánh BM25 và $N = 50$ ứng viên từ nhánh Dense. Hai danh sách này được hợp nhất bằng giải thuật Cormack RRF tiêu chuẩn [3] với tham số làm mịn $k = 60$:
  $$\text{RRF\_Score}(d) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{k + r_m(d)}$$
  Trong đó, $r_m(d)$ là thứ vị xếp hạng của tài liệu $d$ trong danh sách $m$ (với quy ước xếp hạng từ 1 đến 50). Tài liệu nào xuất hiện đồng thời ở thứ hạng cao trên cả hai nhánh sẽ nhận điểm số tích lũy vượt trội.
* **Tầng tái xếp hạng bằng Cross-Encoder (Reranking):** Lấy $Top\text{-}50$ ứng viên có điểm RRF cao nhất để chuyển vào mô hình Cross-Encoder `BAAI/bge-reranker-v2-m3` [1] (thư viện `FlagEmbedding`). Khác với Bi-Encoder chỉ so khớp các vector nhúng độc lập, Cross-Encoder đưa trực tiếp cặp chuỗi $(q, d)$ qua các lớp Transformer đa tầng để tính toán trực tiếp điểm tương tác ngữ nghĩa chéo (Cross-Attention). Toàn bộ 50 ứng viên được sắp xếp lại theo điểm số của Reranker, và $Top\text{-}5$ tài liệu tinh hoa nhất được lựa chọn làm ngữ cảnh nạp vào LLM.

---

### 2.4.3. LightRAG (Trường phái Đồ thị Tri thức Phi cấu trúc)

LightRAG đại diện cho hướng tiếp cận kết hợp đồ thị tri thức hiện đại (Graph-based RAG) [5, 6] nhằm giải quyết bài toán truy hồi các mối liên kết phức tạp mà tìm kiếm phân đoạn thông thường dễ bỏ sót.

* **Cơ chế xây dựng đồ thị hai tầng:** Trong giai đoạn lập chỉ mục (Indexing), nội dung văn bản được nạp vào LightRAG và xử lý tự động bởi mô hình ngôn ngữ lớn `openai/gpt-4o-mini`. Mô hình phân tích văn bản để bóc tách:
  1. *Thực thể cục bộ (Low-level Entities):* Nhận diện các danh từ riêng, thuật ngữ pháp lý cụ thể và mối quan hệ trực tiếp giữa chúng.
  2. *Chủ đề khái quát (High-level Themes):* Gom nhóm các cụm thực thể thành các chủ đề lớn mang tính tổng quan.
  Toàn bộ các thực thể, quan hệ và đoạn tóm tắt cộng đồng được lưu trữ vào không gian vector thông qua mô hình nhúng `BAAI/bge-m3` [1].
* **Cơ chế truy vấn Hybrid Graph Retrieval:** Khi nhận câu hỏi, LightRAG thực hiện tìm kiếm song song ở cả hai cấp độ: cấp độ thực thể chi tiết (Low-level) để bắt trúng các thực thể trọng tâm của câu hỏi, và cấp độ đồ thị khái quát (High-level) để mở rộng các mối quan hệ liên kết trong vùng lân cận. Sau đó, hệ thống tích hợp các chuỗi thông tin này để gửi sang `gpt-4o-mini` sinh câu trả lời.
* **Hạn chế cố hữu trong lĩnh vực pháp điển:** 
  * *Thiếu vắng cấu trúc phả hệ lập pháp:* Do LightRAG dựa trên cơ chế trích xuất thực thể mở (Open Entity Extraction) mà không có ràng buộc luật học [6], các quan hệ được sinh ra thường mang tính khái quát ngữ nghĩa tự do (ví dụ: *"liên quan đến"*, *"chịu sự quản lý của"*), không phản ánh được các quan hệ quy phạm chuẩn tắc như *Căn cứ, Ngoại lệ, Trách nhiệm, Thủ tục*.
  * *Mất mát toạ độ pháp lý vi mô:* LightRAG phân đoạn văn bản theo cửa sổ token của thư viện mà không gắn tiền tố phân cấp Chương-Điều-Khoản-Điểm, dẫn đến việc các đoạn tri thức trong đồ thị không chứa định danh locator chuẩn để trích dẫn nguồn luật.

---

### 2.4.4. Bảng đối chiếu đặc tính kỹ thuật ba hệ thống cơ sở

Bảng 2.1 tổng hợp các thông số kỹ thuật cốt lõi và điều kiện biên vận hành của ba hệ thống RAG cơ sở trong Giai đoạn 1:

**Bảng 2.1. Đối chiếu đặc tính kỹ thuật của ba kiến trúc RAG cơ sở (Giai đoạn 1)**

| Đặc tính Kỹ thuật | Naive Vector RAG | Hybrid RAG | LightRAG |
| :--- | :--- | :--- | :--- |
| **Trường phái tiếp cận** | Bi-Encoder ngữ nghĩa dày [1] | Dung hợp thứ hạng đa tầng (RRF + Reranker) [1, 3] | Đồ thị tri thức hai tầng (Dual-level Graph) [5] |
| **Đơn vị văn bản nạp vào** | Khối điều luật thô nguyên trạng | Khối điều luật thô nguyên trạng | Phân đoạn theo kích thước cửa sổ của thư viện |
| **Mô hình nhúng (Embedding)** | `BAAI/bge-m3` (1024 dims, FP16) [1] | `BAAI/bge-m3` (1024 dims, FP16) [1] | `BAAI/bge-m3` (1024 dims, FP16) [1] |
| **Chỉ mục vector** | `FAISS IndexFlatIP` [4] | `FAISS IndexFlatIP` [4] | Vector store nội bộ của LightRAG |
| **Kênh truy xuất từ vựng** | Không áp dụng | Okapi BM25 (`pyvi.ViTokenizer`) [2, 12] | Không tách nhánh từ vựng độc lập |
| **Thuật toán dung hợp** | Không áp dụng | Cormack RRF ($k=60$, Top-50 BM25 + Top-50 Dense) [3] | Cơ chế truy vấn Hybrid Graph nội bộ [5] |
| **Mô hình tái xếp hạng** | Không áp dụng | Cross-Encoder `BAAI/bge-reranker-v2-m3` [1] | Không áp dụng |
| **Quy mô ngữ cảnh gửi LLM** | $Top\text{-}5$ Điều luật (~2.898 tokens) | $Top\text{-}5$ Điều luật sau Rerank (~2.898 tokens) | Chuỗi thực thể và tóm tắt do đồ thị tổng hợp |
| **Mô hình tạo sinh câu trả lời** | `openai/gpt-4o-mini` ($\text{temp} = 0.0$) | `openai/gpt-4o-mini` ($\text{temp} = 0.0$) | `openai/gpt-4o-mini` ($\text{temp} = 0.0$) |
| **Khả năng xuất định danh Article** | Xuất danh sách `article_id` tường minh | Xuất danh sách `article_id` tường minh | Không xuất danh sách ID nguyên bản |

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


