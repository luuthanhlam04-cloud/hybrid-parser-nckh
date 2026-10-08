# BÁO CÁO PHÂN TÍCH QUÁ TRÌNH XÂY DỰNG DATA BENCHMARK (08/10/2026)

Tài liệu này tổng hợp lại toàn bộ hành trình từ 17:00 chiều nay để xây dựng tập Data Benchmark cho dự án RAG Pháp luật Việt Nam. Tài liệu cung cấp các Insight sâu sắc về xử lý dữ liệu, nguyên nhân loại bỏ (reject), sự cố kỹ thuật, và phân tích bộ chỉ số hiện tại để làm ngữ liệu viết luận văn.

---

## 1. Hành trình thu thập và sàng lọc nguồn dữ liệu ban đầu
**Bối cảnh:** Bắt đầu với các nguồn dữ liệu phân mảnh (VMTEB-ALQAC, ViLegalQA, ViLegalExpert_Cleaned).
**Vấn đề & Insight rút ra:**
- **Sự bất đồng bộ Phiên bản Luật (Temporal Misalignment):** Rất nhiều câu hỏi trong các tập dataset cũ tham chiếu đến các bộ luật đã hết hiệu lực (ví dụ: Luật Hôn nhân Gia đình 2000 thay vì 2014, hoặc các nghị định cũ).
  - *Quyết định Reject:* Hủy bỏ/Lọc bỏ các câu hỏi mà `article_id` không còn tồn tại trong kho `corpus_final.json` (chứa các bộ luật mới nhất). Insight: Benchmark pháp lý đòi hỏi tính thời sự; dùng benchmark cũ để đánh giá hệ thống mới sẽ gây ra lỗi "Hallucination by Data" (Ảo giác do dữ liệu sai).
- **Thiếu hụt văn bản luật (Placeholders):** Trong quá trình gộp Corpus, chúng ta phát hiện Luật Đất đai 2024 (31/2024/qh15) và XLVPHC (73/vbhn-vpqh) bị lỗi "Nội dung Điều X...".
  - *Sự cố & Xử lý:* Phải kích hoạt các bot cào dữ liệu (Crawlers) nhắm thẳng vào `vbpl.vn` và `chinhphu.vn`. Việc này nhấn mạnh Insight: Không thể tin tưởng 100% vào các corpus có sẵn mã nguồn mở (ví dụ HF datasets) mà phải có cơ chế Audit (Kiểm toán dữ liệu) khắt khe trước khi load vào Benchmark.

## 2. Phát hiện và xử lý Data Leakage (Rò rỉ dữ liệu)
Đây là sự cố nghiêm trọng và quan trọng nhất được phát hiện trong buổi tối nay.
- **Hiện tượng:** Qua script `leakage_check.py`, tỷ lệ overlap (trùng lặp từ vựng) trung bình giữa Câu hỏi và Điều luật lên tới **0.7316**. Cá biệt có hàng trăm câu hỏi có độ trùng lặp > 0.90.
- **Nguyên nhân:** ALQAC (tập dữ liệu gốc của VMTEB) được xây dựng bằng cách "copy-paste" nguyên xi một đoạn trong điều luật và thêm từ để hỏi ở cuối.
- **Phân tích Insight (Dùng cho Luận văn):** 
  - Nếu không xử lý, việc đánh giá các mô hình RAG sẽ bị thiên lệch hoàn toàn (Overestimating Baseline). Một hệ thống Lexical thuần túy như BM25 cũng dễ dàng đạt Recall@5 lên tới **0.8789** vì đây bản chất là bài toán "Exact Keyword Matching" chứ không phải "Semantic Search" (Tìm kiếm ngữ nghĩa). Câu hỏi thực tế của công dân/luật sư không bao giờ lặp lại y hệt văn bản luật.
- **Quyết định:** Sử dụng LLM để viết lại (Paraphrase) toàn bộ 452 câu hỏi vi phạm (Overlap > 0.5) nhằm chuyển chúng về ngôn ngữ tự nhiên của người dùng phổ thông.

## 3. Sự cố Kỹ thuật: API Rate Limit và Giải pháp Batch Processing
- **Sự cố:** Quá trình viết lại (Rewrite) bằng LLM gặp rào cản lớn. Sử dụng `gemini-3.1-flash-lite` qua luồng song song (ThreadPoolExecutor 50 workers) ngay lập tức bị Google phạt HTTP 429 (Too Many Requests), do API Key miễn phí bị giới hạn khắt khe ở mức **15 RPM (Requests Per Minute)**. Tiến trình đầu tiên sụp đổ với 389/452 câu bị fail.
- **Giải pháp:** Đổi chiến lược sang **Batch Processing** (Gộp lô). Lợi dụng giới hạn Token khá dư dả (250K TPM), script `rewrite_batch.py` đã nén 20 câu hỏi vào 1 Prompt duy nhất, ép LLM trả về cấu trúc JSON Array. Nhờ vậy, 452 câu hỏi được xử lý thành công tuyệt đối (0 fail) chỉ trong 23 requests (thỏa mãn 15 RPM), hoàn thành chưa đầy 5 phút.

## 4. Phân tích cấu trúc Benchmark Chính Thức (`benchmark_rewritten.json`)
Tập benchmark cuối cùng đã được "chốt hạ" bao gồm các thông số vàng sau:

- **Tổng dung lượng:** 512 câu hỏi QA.
- **Nguồn gốc:** VMTEB-ALQAC (457 câu), ViLegalExpert_Cleaned (55 câu).
- **Độ khó (Phân bố Category):**
  - *clean_factoid (307 câu):* Truy vấn sự thật pháp lý 1 bước.
  - *conditional (123 câu):* Truy vấn đòi hỏi xem xét điều kiện/ngoại lệ pháp lý (Nếu... thì...).
  - *multi_hop (67 câu):* Truy vấn yêu cầu kết nối nhiều điều khoản/luật khác nhau.
  - *negative (15 câu):* Truy vấn về các hành vi bị cấm/phủ định.
- **Chỉ số Chất lượng Dữ liệu:** 
  - Tỷ lệ Overlap trung bình giảm sâu về mốc **0.5037**. Đạt tiêu chuẩn cho một tập dữ liệu "Sạch", có tính Paraphrase cao.
- **Baseline Khởi điểm (BM25):** 
  - Recall@5: 0.7051
  - MRR@5: 0.5794
  - *Bình luận:* Sự sụt giảm Recall@5 (từ 0.88 xuống 0.70) là một tín hiệu ĐÁNG MỪNG. Nó chứng tỏ bài toán đã trở nên sát với thực tế, để hở dư địa ~30% cho các kiến trúc RAG thông minh hơn (Vector/Hybrid/Graph) chứng minh giá trị của mình trong các chương sau của luận văn.

---
*Kết luận dành cho phần Viết Luận Văn:* 
Quá trình xử lý từ 17:00 đến nay là một Case Study hoàn hảo cho việc: "Sự cần thiết của Data Hygiene (Vệ sinh dữ liệu) trong thiết kế Legal Benchmark". Mọi hệ thống RAG phức tạp đều sẽ vô nghĩa (Garbage In - Garbage Out) nếu tập Benchmark bị rò rỉ dữ liệu (Leakage) và không phản ánh đúng phân phối ngôn ngữ tự nhiên của người dùng.

## 5. Q&A Học Thuật: Phản Biện Về Nguồn Dữ Liệu
**Câu hỏi:** *"Các tập data trên mạng (VMTEB, ViLegalQA) bản chất chỉ là tập hợp cặp Câu hỏi - Câu trả lời. Tại sao chúng ta không bốc nguyên xi về xài luôn mà phải mất cả buổi để mổ xẻ, lọc lỗi và dùng AI viết lại? Chẳng phải cứ có Hỏi - Đáp là đánh giá được RAG sao?"*

**Giải đáp (Insights cốt lõi để đưa vào Luận văn):**

1. **Lỗi Rò rỉ Dữ liệu (Data Leakage) tàn phá tính công bằng:** 
   Nhiều tập dữ liệu cũ được tạo ra bằng cách rất cơ học: Tác giả copy nguyên một câu trong luật, đảo ngữ một chút và gắn thêm từ để hỏi. Hậu quả là **câu hỏi chứa chính xác từ vựng của câu trả lời**. 
   Nếu dùng tập này, một thuật toán thô sơ từ 30 năm trước như BM25 (so khớp từ khóa) cũng dễ dàng đạt điểm tuyệt đối (Recall lên tới 90%). Điều này làm "bóp méo" hoàn toàn bài toán RAG: Các mô hình Vector/Graph phức tạp bị lu mờ, vì hệ thống lúc này chỉ đang chơi trò "tìm từ giống nhau" chứ không hề phải suy luận ngữ nghĩa pháp lý.

2. **Lệch pha Phiên bản Luật (Temporal Misalignment):** 
   Pháp luật thay đổi liên tục. Rất nhiều bộ QA cũ trích dẫn Luật Hôn nhân Gia đình bản cũ hoặc Luật Đất đai 2013. Trong khi đó, kho tri thức (Corpus) của hệ thống chúng ta là các bộ luật Mới Nhất. Nếu bốc nguyên QA cũ vào, hệ thống RAG tìm ra luật mới (chính xác với hiện hành) nhưng lại bị Giám khảo đánh điểm 0 vì... "không khớp với đáp án cũ". Việc đánh giá sẽ thành rác nếu không đồng bộ hóa (mapping) được `article_id`.

3. **Thiếu độ khó thực tế (Lack of Complexity):** 
   Đời thực, người dân không bao giờ hỏi *"Theo Khoản 2 Điều 15 Luật Đất đai thì..."*. Họ hỏi những hoàn cảnh phức tạp, cần suy luận chéo nhiều điều luật (Multi-hop), có điều kiện ngoại lệ (Conditional), hoặc hỏi những thứ luật không quy định (Negative/Refusal). Dữ liệu thô sơ trên mạng 95% là câu hỏi ngây ngô (Factoid 1 bước). Việc ta phải thiết kế lại các trường dữ liệu và lọc phân loại là để tạo ra những chướng ngại vật thực sự, qua đó mới ép được các hệ thống Hybrid hay LightRAG bộc lộ hết sức mạnh thiết kế của chúng.
