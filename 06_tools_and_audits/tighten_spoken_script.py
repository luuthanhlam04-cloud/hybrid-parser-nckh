# -*- coding: utf-8 -*-
with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Exact tightened spoken dialogues
s1_old = """> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào bài toán hỏi đáp trên văn bản quy phạm pháp luật Việt Nam."*"""
s1_new = """> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*"""

s2_old = """> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tiễn pháp lý, chỉ cần hệ thống trích dẫn đúng số Điều nhưng dẫn sai một Khoản, hoặc nhầm lẫn một ngoại lệ tại một Điểm, hệ quả pháp lý của hành vi có thể bị đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu hiệu quả tìm kiếm, vừa giúp mô hình ngôn ngữ lớn xác định chính xác căn cứ vi mô mà không làm bùng nổ dung lượng ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."*"""
s2_new = """> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, nghiên cứu của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tế, chỉ cần trích dẫn đúng số Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu tìm kiếm, vừa giúp mô hình xác định chính xác căn cứ vi mô mà không bùng nổ dung lượng ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*"""

s3_old = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Văn bản luật Việt Nam có ba đặc thù kiến trúc nổi bật: cấu trúc phân cấp đa tầng từ Luật xuống Điều, Khoản, Điểm; mạng lưới dẫn chiếu chéo phức tạp quy định điều kiện và ngoại lệ; cùng sự lệch pha từ vựng lớn giữa câu hỏi của người dân và thuật ngữ chuẩn tắc.  
> Từ những đặc thù này, nhóm tập trung vào ba vấn đề cần kiểm chứng thực nghiệm: Một là tác động của phân đoạn cấu trúc đến hiệu quả truy hồi; Hai là mức độ bảo đảm đầy đủ các thành phần quy phạm trong câu trả lời; và Ba là khả năng truy vết các quan hệ dẫn chiếu giữa những điều luật liên quan."*"""
s3_new = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Văn bản luật Việt Nam có ba đặc thù: phân cấp đa tầng từ Luật xuống Điều, Khoản, Điểm; mạng lưới dẫn chiếu chéo quy định điều kiện, ngoại lệ; và sự lệch pha từ vựng giữa câu hỏi người dân với thuật ngữ chuẩn tắc.  
> Từ đó, nhóm tập trung vào ba vấn đề kiểm chứng thực nghiệm: tác động của phân đoạn cấu trúc đến hiệu quả truy hồi; mức độ bao phủ các thành phần quy phạm trong câu trả lời; và khả năng truy vết quan hệ dẫn chiếu giữa những điều luật liên quan."*"""

s4_old = """> *"Để kiểm chứng các vấn đề trên, nhóm lựa chọn khảo sát ba trường phái RAG đại diện hiện nay làm hệ thống đối chứng:  
> Trước hết là **Naive Vector RAG** dựa trên biểu diễn vector dày đặc và độ tương đồng Cosine, rất mạnh về ngữ nghĩa khái quát.  
> Thứ hai là **Hybrid RAG** dung hợp từ khóa BM25 và Dense qua thuật toán RRF kết hợp Cross-Encoder Reranker, cải thiện khả năng bắt từ khóa định danh.  
> Thứ ba là **LightRAG** đại diện cho trào lưu GraphRAG, trích xuất đồ thị thực thể bằng mô hình ngôn ngữ lớn để kết nối tri thức hai tầng.  
> Nhóm sử dụng ba kiến trúc này làm đối chứng để khảo sát hiệu quả trên dữ liệu pháp luật Việt Nam."*"""
s4_new = """> *"Để kiểm chứng các vấn đề trên, nhóm lựa chọn khảo sát ba trường phái RAG đại diện làm hệ thống đối chứng:  
> Naive Vector RAG dựa trên nhúng vector dày đặc và độ tương đồng Cosine, mạnh về ngữ nghĩa khái quát.  
> Hybrid RAG dung hợp từ khóa BM25 và Dense qua giải thuật RRF kết hợp Cross-Encoder Reranker, cải thiện khả năng bắt từ khóa định danh.  
> LightRAG đại diện cho GraphRAG, trích xuất đồ thị thực thể – quan hệ để kết nối tri thức hai tầng.  
> Ba kiến trúc này đại diện cho ba cách tổ chức dữ liệu khác nhau để đối chuẩn trên văn bản luật Việt Nam."*"""

s5_old = """> *"Từ đó, nhóm xây dựng bốn câu hỏi nghiên cứu định hướng toàn bộ thực nghiệm:  
> RQ1: Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?  
> RQ2: Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện độ chính xác trích dẫn ngữ cảnh và dung lượng tài liệu ra sao?  
> RQ3: Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ phức tạp thế nào khi đối sánh trực diện với LightRAG?  
> RQ4: Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào?"*"""
s5_new = """> *"Từ đó, nhóm xây dựng bốn câu hỏi nghiên cứu định hướng:  
> RQ1: Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?  
> RQ2: Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện trích dẫn ngữ cảnh và dung lượng ra sao?  
> RQ3: Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ thế nào khi đối sánh với LightRAG?  
> RQ4: Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào?"*"""

s6_old = """> *"Để trả lời bốn RQ, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện Adapter Pattern, kiểm soát các biến thực nghiệm có thể chuẩn hóa: cùng văn bản nguồn, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, được diễn đạt lại có chọn lọc để đưa Jaccard trung bình từ 0,68 xuống 0,31 nhằm hạn chế lợi thế không mong muốn của truy hồi từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu đa điều kiện, ngoại lệ và dẫn chiếu.  
> Sau đây, xin mời bạn Lâm trình bày kết quả Giai đoạn 1 và 2."*"""
s6_new = """> *"Để trả lời bốn RQ, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện Adapter Pattern, kiểm soát các biến thực nghiệm có thể chuẩn hóa: cùng văn bản nguồn, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, được diễn đạt lại có chọn lọc giúp giảm Jaccard trung bình từ 0,68 xuống 0,31 nhằm hạn chế lợi thế của truy hồi từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu đa điều kiện, ngoại lệ và dẫn chiếu.  
> Sau đây, xin mời bạn Lâm trình bày kết quả."*"""

s7_old = """> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Khi đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm phát hiện khoảng cách đáng chú ý giữa khả năng tìm kiếm và khả năng trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm tài liệu rất tốt: Recall@5 đều vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy trên câu trả lời sụt giảm nghiêm trọng: Naive Vector chỉ đạt 32,59%, Hybrid đạt 29,02%, và LightRAG ghi nhận 13,71%.  
> Nguyên nhân kỹ thuật là việc sử dụng các khối văn bản thô thiếu cấu trúc phân cấp tường minh khiến mô hình khó xác định mối liên hệ giữa nội dung truy hồi và vị trí pháp lý cần viện dẫn.  
> Kết quả này trả lời cho RQ1: RAG cơ sở bộc lộ khoảng cách lớn ở bài toán trích dẫn nếu giữ nguyên phương thức cắt đoạn thô."*"""
s7_new = """> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Đối chuẩn ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm ghi nhận khoảng cách rõ rệt giữa tìm kiếm và trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm tốt: Recall@5 vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy câu trả lời sụt giảm sâu: Naive Vector đạt 32,59%, Hybrid đạt 29,02%, và LightRAG chỉ 13,71%.  
> Nguyên nhân là việc sử dụng văn bản thô thiếu cấu trúc phân cấp tường minh khiến mô hình khó xác định mối liên hệ giữa nội dung truy hồi và vị trí pháp lý cần viện dẫn.  
> Kết quả này trả lời cho RQ1: RAG cơ sở bộc lộ khoảng cách lớn ở bài toán trích dẫn nếu giữ nguyên cắt đoạn thô."*"""

s8_old = """> *"Để khắc phục hiện tượng trên, bước sang Giai đoạn 2, nhóm đề xuất giải pháp cấu trúc gồm hai thành phần cốt lõi:  
> Trước hết là bộ phân tích cấu trúc Structure-Aware Parser v2. Parser bóc tách đệ quy văn bản luật thành 12.754 phân đoạn vi mô theo từng cấp Khoản, Điểm, đồng thời gắn tiền tố cấu trúc bất biến chứa đầy đủ phả hệ từ tên Luật, Chương đến Điều vào từng phân đoạn, giúp duy trì thông tin định vị và quan hệ phân cấp.  
> Tiếp đó, để xử lý việc phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng một Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling (MaxP). Hệ thống gom cụm các phân đoạn theo Điều và lấy điểm cực đại của phân đoạn đại diện để xếp hạng Top-K cấp Điều; sau đó lựa chọn các phân đoạn vi mô liên quan để xây dựng ngữ cảnh đưa vào mô hình ngôn ngữ.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*"""
s8_new = """> *"Để khắc phục khoảng cách trên, bước sang Giai đoạn 2, nhóm đề xuất gói giải pháp cấu trúc:  
> Bộ phân tích Structure-Aware Parser v2 bóc tách đệ quy văn bản luật thành 12.754 phân đoạn vi mô theo từng cấp Khoản, Điểm, gắn tiền tố cấu trúc bất biến chứa đầy đủ phả hệ từ tên Luật, Chương đến Điều, giúp duy trì thông tin định vị và quan hệ phân cấp.  
> Đồng thời, để xử lý việc phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng một Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling. Hệ thống gom cụm phân đoạn theo Điều, lấy điểm cực đại để xếp hạng cấp Điều; sau đó lựa chọn các phân đoạn vi mô liên quan để xây dựng ngữ cảnh đưa vào mô hình ngôn ngữ.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*"""

s9_old = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2 với ba điểm đáng chú ý:  
> Điểm nổi bật nhất, cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902, tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, nhờ phân đoạn vi mô và MaxP, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống chỉ còn 580 token.  
> Qua khảo sát 11 giá trị trọng số tại Bảng 3.7, nhóm xác định cấu hình cân bằng tại alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, cải thiện rõ rệt so với cấu hình cào bằng ở C6.  
> Ở đây, nhóm lưu ý về phương pháp luận: Giai đoạn 2 đánh giá riêng chất lượng căn cứ xuất hiện trong ngữ cảnh truy hồi bằng LLM-Judge, thay vì chấm câu trả lời hoàn chỉnh. Kết quả C2 và C5 phản ánh tác động tích cực của gói xử lý cấu trúc trong điều kiện Dense Retrieval, tạo tiền đề để đánh giá câu trả lời toàn trình ở Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*"""
s9_new = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2:  
> Cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902, tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, nhờ phân đoạn vi mô và MaxP, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống còn 580 token.  
> Khảo sát tại Bảng 3.7 ghi nhận cấu hình cân bằng alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, cải thiện so với cấu hình cào bằng ở C6.  
> Nhóm lưu ý: Giai đoạn 2 đánh giá riêng chất lượng căn cứ trong ngữ cảnh truy hồi bằng LLM-Judge, thay vì chấm câu trả lời hoàn chỉnh. Kết quả C2 và C5 phản ánh tác động tích cực của gói xử lý cấu trúc trong điều kiện Dense Retrieval, tạo tiền đề để đánh giá toàn trình ở Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*"""

s10_old = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — sử dụng các quy tắc xác định trước để xây dựng cấu trúc phân cấp Chương-Mục-Điều-Khoản-Điểm, Module 3 Validation cách ly các node lỗi nghiêm trọng.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Các bước xử lý tri thức được thực hiện trong quá trình lập chỉ mục; khi truy vấn trực tuyến, hệ thống khai thác cấu trúc và quan hệ đã dựng để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng mô hình ngôn ngữ nhân quả Qwen2.5-0.5B kết hợp toán tử Max-Fusion logic OR giữa Regex và Vector. Cơ chế Causal Attention bảo toàn trật tự logic chủ thể - điều kiện - chế tài. Tại ngưỡng theta = 0,85 trên Golden Set 193 node, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục, chấp nhận ranh giới đánh đổi 4 node quy phạm bị bỏ sót."*"""
s10_new = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý — sử dụng các quy tắc xác định trước để xây dựng cấu trúc phân cấp, Module 3 Validation cách ly các node lỗi nghiêm trọng.  
> Tầng 2 là Đồ thị ngữ nghĩa — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Các bước xử lý tri thức thực hiện trong quá trình lập chỉ mục; khi truy vấn, hệ thống duyệt đồ thị đã dựng để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng mô hình Qwen2.5-0.5B kết hợp toán tử Max-Fusion giữa Regex và Vector. Tại ngưỡng theta = 0,85 trên Golden Set 193 node, hệ thống đạt Recall 96,85%, F1 0,8146, loại 9,33% phân đoạn thủ tục, chấp nhận ranh giới đánh đổi 4 node quy phạm bị bỏ sót."*"""

s11_old = """> *"Kính thưa Hội đồng, kết quả thực nghiệm trên Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4 qua ba khối thông tin:  
> Về năng lực truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Về chất lượng trích dẫn và nội dung câu trả lời, UKG thể hiện ưu thế vượt trội: Citation Precision cấp Điều đạt 0,8369 vs 0,3333 của LightRAG (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp gần 18 lần). Ở tầng nội dung, Legal Correctness đạt 0,8777 và đặc biệt Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách chính xác các mệnh đề ngoại lệ.  
> Về hai ranh giới kỹ thuật cần hoàn thiện: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do phân đoạn vi mô tập trung vào quy phạm lõi, cần thêm cơ chế lan truyền điều kiện diện rộng. Về RQ4, UKG định vị được 58,67% node đích, nhưng việc tái dựng chuỗi có thứ tự cần thêm giải thuật duyệt đồ thị có ràng buộc khi Chain Exact Match ghi nhận 0,0000 trên 18 câu.  
> Riêng chỉ số Exact Locator Recall@5 đạt 0,5560 vs 0,8509 do khác biệt lớn về độ hạt: chunk LightRAG chứa trung bình khoảng 15 locator trong khi phân đoạn UKG chỉ mang 1 locator."*"""
s11_new = """> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4:  
> Về truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Về chất lượng trích dẫn và nội dung, Citation Precision cấp Điều đạt 0,8369 vs 0,3333 (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp 18 lần). Ở tầng nội dung, Legal Correctness đạt 0,8777 và Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách mệnh đề ngoại lệ.  
> Về ranh giới kỹ thuật: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do phân đoạn vi mô cần thêm cơ chế lan truyền điều kiện diện rộng. Về RQ4, UKG định vị được 58,67% node đích, nhưng việc tái dựng chuỗi thứ tự cần thêm giải thuật duyệt đồ thị có ràng buộc khi Chain Exact Match ghi nhận 0,0000 trên 18 câu.  
> Chỉ số Exact Locator Recall@5 đạt 0,5560 vs 0,8509 do khác biệt độ hạt: chunk LightRAG chứa trung bình ~15 locator trong khi phân đoạn UKG chỉ mang 1 locator."*"""

s12_old = """> *"Tổng hợp lại từ ba giai đoạn, nhóm đã đóng gói lời giải cho bốn bài toán nghiên cứu ban đầu:  
> Với RQ1: Xác lập thực nghiệm khoảng cách giữa truy hồi và trích dẫn, chỉ ra hạn chế của việc sử dụng văn bản thô thiếu cấu trúc phân cấp.  
> Với RQ2: Cung cấp bằng chứng thực nghiệm cho thấy Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 79,9% dung lượng ngữ cảnh.  
> Với RQ3: Hybrid UKG đạt kết quả cao hơn LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần, và độ bao phủ ngoại lệ (+28,57 đpt); tuy nhiên hiệu quả chưa đồng đều ở thành phần điều kiện.  
> Với RQ4: Hệ thống xác định được một phần căn cứ đích (58,67%), làm rõ ranh giới cần giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi dẫn chiếu."*"""
s12_new = """> *"Từ ba giai đoạn thực nghiệm, nhóm đối chiếu lại bốn câu hỏi nghiên cứu ban đầu:  
> RQ1: Xác lập thực nghiệm khoảng cách giữa truy hồi và trích dẫn, chỉ ra hạn chế của việc sử dụng văn bản thô thiếu cấu trúc phân cấp.  
> RQ2: Cung cấp bằng chứng cho thấy Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 79,9% dung lượng ngữ cảnh.  
> RQ3: Hybrid UKG đạt kết quả cao hơn LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần, và độ bao phủ ngoại lệ (+28,57 đpt); tuy nhiên hiệu quả chưa đồng đều ở thành phần điều kiện.  
> RQ4: Hệ thống xác định được một phần căn cứ đích (58,67%), làm rõ ranh giới cần giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi dẫn chiếu."*"""

s13_old = """> *"Từ các kết quả trên, đề tài xác định ba đóng góp khoa học cốt lõi:  
> Một là Khung dữ liệu và phương pháp kiểm chuẩn gồm Benchmark A, Benchmark B và hạ tầng Adapter Pattern phục vụ đối sánh các kiến trúc RAG trên dữ liệu luật Việt Nam.  
> Hai là Phương pháp tổ chức và truy hồi cấu trúc vi mô kết hợp Article-level MaxP, cải thiện đáng kể chất lượng đánh giá căn cứ và tối ưu hóa dung lượng đầu vào.  
> Ba là Kiến trúc hệ thống đồ thị hai tầng Hybrid UKG, kết hợp đồ thị cấu trúc vật lý với lớp ngữ nghĩa pháp lý để nâng cao khả năng truy hồi và xử lý quy phạm ngoại lệ.  
> Thông điệp đúc kết của nhóm là: Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."*"""
s13_new = """> *"Từ các kết quả trên, đề tài xác định ba đóng góp cốt lõi:  
> Khung dữ liệu và kiểm chuẩn Benchmark A, Benchmark B cùng Adapter Pattern phục vụ đối sánh các kiến trúc RAG trên dữ liệu luật Việt Nam.  
> Phương pháp phân đoạn cấu trúc vi mô kết hợp Article MaxP, cải thiện chất lượng căn cứ ngữ cảnh và tối ưu dung lượng đầu vào.  
> Kiến trúc đồ thị hai tầng Hybrid UKG, kết hợp đồ thị cấu trúc vật lý với lớp ngữ nghĩa pháp lý để xử lý quy phạm ngoại lệ.  
> Thông điệp đúc kết của nhóm là: Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."*"""

s14_old = """> *"Trong thời gian tới, nhóm hướng đến mở rộng bộ bóc tách cấu trúc sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực văn bản; và hoàn thiện giải thuật constrained graph traversal để khép kín chuỗi dẫn chiếu.  
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô trong Hội đồng đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*"""
s14_new = """> *"Thời gian tới, nhóm hướng đến mở rộng sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực văn bản; và hoàn thiện giải thuật duyệt đồ thị có ràng buộc.  
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*"""

pairs = [
    (s1_old, s1_new), (s2_old, s2_new), (s3_old, s3_new), (s4_old, s4_new),
    (s5_old, s5_new), (s6_old, s6_new), (s7_old, s7_new), (s8_old, s8_new),
    (s9_old, s9_new), (s10_old, s10_new), (s11_old, s11_new), (s12_old, s12_new),
    (s13_old, s13_new), (s14_old, s14_new)
]

for o, n in pairs:
    if o in text:
        text = text.replace(o, n)
    else:
        print('Warning: old string not found!')

# Ensure XML safety
text = text.replace('\x07', 'alpha')

with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated kich_ban_thuyet_trinh_15p.md with tightened spoken dialogues.')

