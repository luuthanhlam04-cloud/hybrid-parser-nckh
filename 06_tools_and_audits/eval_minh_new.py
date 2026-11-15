# -*- coding: utf-8 -*-
minh_text = """
Kính thưa quý thầy cô trong Hội đồng!
Chúng em là Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh. Dưới sự hướng dẫn của thầy Nguyễn Mạnh Dũng, nhóm thực hiện đề tài "Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù", với đối tượng nghiên cứu là văn bản pháp luật Việt Nam.

Chúng em xin bắt đầu bằng một ví dụ:
Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?
Để trả lời, hệ thống có thể tìm được quy định về quyền bán tài sản tại Điều 34 Luật Đất đai 2024. Tuy nhiên, quy định này còn dẫn chiếu đến Điều 46 về các điều kiện liên quan.
Nếu chỉ tìm được Điều 34, câu trả lời có thể chưa đầy đủ.
Vì vậy, hệ thống cần tiếp tục truy hồi các quy định được dẫn chiếu, tổng hợp điều kiện và viện dẫn đúng vị trí Điều-Khoản-Điểm.
Từ đó, nhóm tập trung nghiên cứu cách tổ chức dữ liệu, truy hồi và cung cấp căn cứ pháp lý cho RAG.

Kính thưa Hội đồng,
Văn bản pháp luật có ba đặc điểm ảnh hưởng đến quá trình truy hồi.
Thứ nhất là cấu trúc phân cấp Điều-Khoản-Điểm. Thứ hai là các quan hệ dẫn chiếu giữa những quy định. Thứ ba là sự khác biệt giữa cách người dùng đặt câu hỏi và ngôn ngữ chuyên môn của văn bản luật.
Do đó, tìm được một đoạn văn bản liên quan chưa đủ. Hệ thống còn cần xác định đúng vị trí, phạm vi áp dụng và các quy định có liên quan.

Ở giai đoạn đầu, nhóm lựa chọn ba kiến trúc đại diện cho ba hướng tiếp cận.
Naive Vector RAG sử dụng độ tương đồng ngữ nghĩa để tìm tài liệu liên quan.
Hybrid RAG kết hợp BM25, Dense Retrieval và Cross-Encoder, nhằm khảo sát hiệu quả của việc kết hợp nhiều tín hiệu truy hồi và tái xếp hạng.
LightRAG khai thác thực thể và quan hệ trong đồ thị để hỗ trợ truy hồi thông tin.
Việc lựa chọn ba kiến trúc này giúp nhóm so sánh hiệu năng giữa những cách tổ chức và truy hồi dữ liệu khác nhau.
Tuy nhiên, đây là đối sánh ở cấp hệ thống, chưa tách riêng mức đóng góp của từng thuật toán hay thành phần.

Quá trình nghiên cứu được chia thành ba giai đoạn.
Giai đoạn một đánh giá ba kiến trúc RAG cơ sở, tương ứng RQ1.
Giai đoạn hai khảo sát phương án phân đoạn cấu trúc bằng Parser, Validation và MaxP, tương ứng RQ2.
Giai đoạn ba phát triển Hybrid Parser/UKG, đánh giá khả năng truy hồi, xử lý nội dung pháp lý và tái dựng chuỗi dẫn chiếu, tương ứng RQ3 và RQ4.

Để kiểm chứng các phương án, nhóm xây dựng hai bộ benchmark và một khung đánh giá chung.
Benchmark A gồm 512 câu hỏi trên 2.087 điều luật thuộc bảy văn bản. Ở giai đoạn một, do LightRAG chỉ lập chỉ mục khoảng 500 điều luật, nhóm sử dụng tập Tier 1 gồm 205 câu có toàn bộ căn cứ nằm trong phạm vi này để đối sánh.
Sang giai đoạn hai, nhóm sử dụng toàn bộ 512 câu để đánh giá sáu cấu hình.
Benchmark B gồm 50 câu hỏi thuộc Chương III Luật Đất đai 2024, được gắn nhãn chi tiết về căn cứ, điều kiện, ngoại lệ và dẫn chiếu.
Quy trình đánh giá gồm ba bước: chuẩn bị câu hỏi và căn cứ tham chiếu, chạy các hệ thống để lưu kết quả, sau đó tính toán các chỉ số.
Ở tầng truy hồi, nhóm sử dụng Recall@5 và MRR@5. Ở tầng câu trả lời, nhóm sử dụng các tiêu chí về chất lượng nội dung, trích dẫn và quan hệ dẫn chiếu, trong đó có đánh giá bằng GPT-4o-mini.

Trên tập Tier 1 gồm 205 câu hỏi, cả ba hệ thống đều đạt Recall@5 trên 0,95.
Cụ thể, Naive Vector đạt 0,9561, còn Hybrid RAG và LightRAG cùng đạt 0,9659.
Tuy nhiên, ở chỉ số MRR@5, Hybrid RAG đạt 0,9243, cao hơn hai hệ thống còn lại.
Điều này cho thấy Hybrid RAG có khả năng đưa căn cứ liên quan lên vị trí ưu tiên cao hơn trong tập kiểm thử.
Tuy vậy, kết quả truy hồi tốt chưa bảo đảm hệ thống viện dẫn đúng Khoản-Điểm hoặc cung cấp đầy đủ các điều kiện.
Từ đó, nhóm tiếp tục khảo sát ảnh hưởng của việc phân đoạn dữ liệu theo cấu trúc pháp lý.

Ở giai đoạn hai, nhóm triển khai Parser và Validation để tách 2.087 điều luật thành 12.754 phân đoạn, chủ yếu ở cấp Khoản và Điểm.
Mỗi phân đoạn được bổ sung thông tin cấp cha để giữ được vị trí trong văn bản gốc.
Tuy nhiên, khi tách nhỏ, nhiều kết quả Top-5 có thể thuộc cùng một Điều luật.
Vì vậy, nhóm sử dụng Article-level MaxP, lấy điểm cao nhất của các phân đoạn thuộc cùng một Điều để đại diện cho Điều đó.
Cách này giúp hệ thống xếp hạng ở cấp Điều nhưng vẫn giữ được phân đoạn chi tiết làm căn cứ.

Để kiểm chứng phương án trên, nhóm khảo sát sáu cấu hình gồm hai cách tổ chức dữ liệu và ba phương thức truy hồi: BM25, Dense và Hybrid.
Đáng chú ý, khi chuyển từ C2 sang C5, Recall@5 tăng từ 0,9141 lên 0,9316, còn MRR@5 tăng từ 0,8129 lên 0,8602.
C5 cũng đạt điểm LLM-Judge Citation Accuracy trung bình 0,9902, đồng thời giảm gần 79,9% độ dài ngữ cảnh.
Đây là điểm đánh giá tự động theo giao thức thực nghiệm, chưa phải tỷ lệ câu trả lời được xác nhận chính xác tuyệt đối.
Kết quả cho thấy phương án Parser kết hợp ngữ cảnh cấp cha và MaxP mang lại những cải thiện nhất định.
Tuy nhiên, phương án này chủ yếu xử lý việc tìm từng đơn vị văn bản. Để khai thác quan hệ giữa các quy định, nhóm tiếp tục xây dựng Hybrid Parser/UKG.

Kính thưa Hội đồng,
Hybrid Parser/UKG gồm mười module, được chia thành năm nhóm xử lý như trên sơ đồ.
Đầu tiên, M1 đến M4 thực hiện tiền xử lý, phân tích cấu trúc và xây dựng Physical Graph để lưu giữ các đơn vị Điều-Khoản-Điểm.
Tiếp theo, M5 và M6 định tuyến các phân đoạn cần xử lý và sử dụng LLM để trích xuất thông tin ngữ nghĩa.
M7 và M8 chuẩn hóa, hợp nhất dữ liệu vật lý với dữ liệu ngữ nghĩa thành Unified Knowledge Graph.
M9 lưu trữ đồ thị trên Neo4j.
Cuối cùng, M10 thực hiện truy hồi, mở rộng căn cứ liên quan, lựa chọn ngữ cảnh và sinh câu trả lời có trích dẫn nguồn.
Điểm chính của kiến trúc là kết hợp thông tin cấu trúc và ngữ nghĩa, đồng thời giữ liên kết với văn bản pháp lý gốc.

Để đánh giá kiến trúc đề xuất, nhóm sử dụng Benchmark B và đối sánh Hybrid Parser/UKG với LightRAG.
Kết quả được chia thành ba tầng.
Thứ nhất, về truy hồi: Trên 47 câu hỏi đủ căn cứ, Hybrid Parser/UKG đạt Recall@5 bằng 0,9184, cao hơn LightRAG ở mức 0,7358. MRR@5 cũng cao hơn, lần lượt là 0,8848 và 0,5539.
Thứ hai, về chất lượng câu trả lời: Hybrid Parser/UKG đạt Legal Correctness bằng 0,8777 và Exception Coverage bằng 0,6786, đều cao hơn LightRAG.
Citation Recall cấp Khoản cũng đạt 0,8170, so với 0,0435 của LightRAG.
Tuy nhiên, Condition Coverage của Hybrid Parser/UKG chỉ đạt 0,7066, thấp hơn LightRAG ở mức 0,8421. Điều này cho thấy hệ thống vẫn còn hạn chế trong việc tổng hợp đầy đủ các điều kiện pháp lý.
Ở phép đo Exact Locator Recall@5, LightRAG có điểm cao hơn, nhưng hai hệ thống có đơn vị truy hồi và số mẫu hợp lệ khác nhau, nên nhóm chưa đưa ra kết luận bên nào định vị chính xác hơn từ chỉ số này.
Thứ ba, về dẫn chiếu: Trên 18 câu có nhãn chuỗi, Reference-target Recall đạt 0,5867, nhưng Chain Exact Match bằng 0/18.
Như vậy, hệ thống có kết quả tích cực ở truy hồi và một số tiêu chí câu trả lời, nhưng chưa giải quyết đầy đủ bài toán tổng hợp điều kiện và tái dựng chuỗi dẫn chiếu.

Từ ba giai đoạn, nhóm rút ra các kết quả chính.
Với RQ1, Hybrid RAG cải thiện thứ hạng truy hồi nhưng chất lượng trích dẫn vẫn còn hạn chế.
Với RQ2, phương án Parser, Validation và MaxP mang lại kết quả tích cực ở cấu hình Dense.
Với RQ3, Hybrid Parser/UKG cải thiện một số chỉ số, nhưng chưa vượt LightRAG ở tất cả tiêu chí.
Còn với RQ4, hệ thống tìm được một phần căn cứ đích, nhưng chưa tái dựng được chuỗi dẫn chiếu hoàn chỉnh.

Nhóm tổng hợp ba đóng góp chính.
Thứ nhất, xây dựng và tổ chức Benchmark A, Benchmark B cùng khung đánh giá để đối sánh các hệ thống RAG.
Thứ hai, triển khai và khảo sát phương án phân đoạn cấu trúc bằng Parser, Validation và MaxP.
Thứ ba, thiết kế và tích hợp kiến trúc Hybrid Parser/UKG, kết hợp đồ thị cấu trúc với dữ liệu ngữ nghĩa.
Các thuật toán nền tảng được nhóm kế thừa; đóng góp tập trung vào thiết kế, tích hợp và kiểm chứng thực nghiệm.

Trong thời gian tới, nhóm định hướng mở rộng đánh giá trên dữ liệu độc lập, nghiên cứu quản lý hiệu lực văn bản và cải thiện khả năng tổng hợp điều kiện, tái dựng dẫn chiếu nhiều bước.
Nhóm nhận thấy truy hồi đúng căn cứ là cần thiết, nhưng chưa đủ để bảo đảm câu trả lời pháp lý đầy đủ và chính xác.
Chúng em xin trân trọng cảm ơn các thầy trong Hội đồng đã lắng nghe!
"""

paragraphs = [p.strip() for p in minh_text.strip().split('\n\n') if p.strip()]
print(f"Total sections: {len(paragraphs)}")
total_w = 0
for i, p in enumerate(paragraphs):
    w = len(p.split())
    total_w += w
    print(f"Slide {i+1:02d}: {w:3d} words")

print("-" * 30)
print(f"TOTAL WORDS: {total_w}")
print(f"Time @ 130 wpm: {total_w/130:.2f} mins ({total_w/(130/60):.0f}s)")

