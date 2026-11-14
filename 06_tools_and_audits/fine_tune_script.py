# -*- coding: utf-8 -*-
"""
Fine-tune update script to bring exact spoken words to ~1.850 words.
"""
with open('c:/Users/luuth/NCKH/Benchmark/06_tools_and_audits/update_kich_ban_15p.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace specific slide texts in Part 2
s1_old = """> *"Kính thưa Quý Thầy Cô trong Hội đồng khoa học!  
> Em xin đại diện nhóm nghiên cứu gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của Thầy TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào bài toán hỏi đáp pháp luật Việt Nam."*"""

s1_new = """> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm nghiên cứu gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*"""

s2_old = """> *"Kính thưa Hội đồng,  
> Tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tiễn pháp lý, chỉ cần trích dẫn đúng số Điều nhưng dẫn sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu truy hồi, vừa giúp LLM xác định chính xác căn cứ vi mô mà không bùng nổ chi phí tính toán?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."*"""

s2_new = """> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tế, chỉ cần trích dẫn đúng số Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu truy hồi, vừa giúp LLM xác định chính xác căn cứ vi mô mà không bùng nổ chi phí tính toán?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*"""

s9_old = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2 với ba kết quả cốt lõi:  
> Thứ nhất, cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902, tức tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Thứ hai, nhờ phân đoạn vi mô và MaxP, dung lượng token ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống chỉ còn 580 token, giảm đáng kể chi phí API và độ trễ.  
> Thứ ba, tại Bảng 3.7 qua quét toàn diện 11 giá trị alpha từ 0,0 đến 1,0, nhóm xác định điểm cân bằng Weighted RRF tại alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, khắc phục hiện tượng cào bằng ở C6.  
> Ở đây, nhóm nhấn mạnh nguyên tắc Cô lập biến số (Isolation of Variables): Con số 32,59% ở GĐ1 đo trên câu trả lời, còn 0,9902 ở GĐ2 đo độc lập trên ngữ cảnh truy hồi để kiểm chứng thuần túy hiệu năng của Parser mà không bị nhiễu bởi tính ngẫu nhiên của LLM. Phép đo toàn trình trên câu trả lời được dành trọn vẹn cho GĐ3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày kiến trúc UKG và kết quả Giai đoạn 3."*"""

s9_new = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2 với ba điểm cốt lõi:  
> Thứ nhất, cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902 (+59,02 đpt), với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Thứ hai, nhờ phân đoạn vi mô và MaxP, dung lượng token ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống chỉ còn 580 token, giảm mạnh chi phí API và độ trễ.  
> Thứ ba, tại Bảng 3.7 qua quét 11 giá trị alpha, nhóm xác định điểm cân bằng Weighted RRF tại alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, khắc phục hiện tượng cào bằng ở C6.  
> Nhóm nhấn mạnh nguyên tắc Cô lập biến số (Isolation of Variables): Con số 32,59% ở GĐ1 đo trên câu trả lời, còn 0,9902 ở GĐ2 đo trên ngữ cảnh truy hồi để kiểm chứng thuần túy hiệu năng của Parser mà không bị nhiễu bởi tính ngẫu nhiên của LLM.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*"""

s10_old = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — khóa cứng bất biến 100% phả hệ văn bản luật bằng bộ phân tích tất định.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Xây dựng đồ thị là tác vụ Offline Indexing chạy một lần duy nhất; khi truy vấn online, hệ thống duyệt đồ thị trong mili-giây.  
> Điểm nhấn là Module 5 Semantic Router: Ứng dụng mô hình nhân quả Qwen2.5-0.5B kết hợp toán tử Max-Fusion (Logic OR) giữa Regex và Vector. Causal Attention bảo toàn trật tự logic chủ thể - điều kiện - chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder. Tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục trước khi trích xuất."*"""

s10_new = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — khóa cứng bất biến 100% phả hệ văn bản luật bằng bộ phân tích tất định.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Xây dựng đồ thị là tác vụ Offline Indexing chạy một lần duy nhất; khi truy vấn online, hệ thống duyệt đồ thị trong mili-giây.  
> Điểm nhấn là Module 5 Semantic Router: Ứng dụng mô hình nhân quả Qwen2.5-0.5B kết hợp toán tử Max-Fusion logic OR giữa Regex và Vector. Causal Attention bảo toàn logic chủ thể - điều kiện - chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder. Tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục."*"""

s11_old = """> *"Kính thưa Hội đồng, kết quả thực nghiệm trên Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 tại các Bảng 3.9, 3.11, 3.15 và 3.16 đã làm sáng tỏ RQ3 và RQ4:  
> Về RQ3 — năng lực định vị và xử lý quy phạm:  
> Ở tầng truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 so với 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 so với 0,5539 (vượt +33,09 đpt).  
> Ở tầng trích dẫn câu trả lời (Bảng 3.16), UKG vượt trội: Citation Precision cấp Điều đạt 0,8369 so với 0,3333 của LightRAG (gấp 2,5 lần); cấp Khoản đạt 0,7757 so với 0,0435 (gấp 18 lần).  
> Ở tầng nội dung (Bảng 3.15), UKG đạt Legal Correctness 0,8777 và đặc biệt Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách chính xác mệnh đề ngoại lệ.  
> Về mặt trade-off, nhóm minh bạch ghi nhận: Condition Coverage của UKG đạt 0,7066 so với 0,8421 của LightRAG do chunk 1.200 token lớn vô tình gom nhiều điều kiện; và Exact Locator Recall@5 tại Bảng 3.11 LightRAG cao hơn (0,8509 vs 0,5560) do đo trùng khớp chuỗi ký tự cục bộ, trong khi UKG ưu tiên tính toàn vẹn thực thể cấp Điều.  
> Về RQ4: UKG định vị tốt node đích với Reference-target Recall đạt 58,67%. Tái dựng chuỗi có thứ tự cần thêm giải thuật Constrained Graph Traversal (Chain Exact Match đạt 0,0000 trên 18 câu), xác lập ranh giới cho giai đoạn tiếp theo."*"""

s11_new = """> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4:  
> Về RQ3 — năng lực định vị và xử lý quy phạm:  
> Ở tầng truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Ở tầng trích dẫn câu trả lời (Bảng 3.16), Citation Precision cấp Điều đạt 0,8369 vs 0,3333 của LightRAG (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp 18 lần).  
> Ở tầng nội dung (Bảng 3.15), Legal Correctness đạt 0,8777 và đặc biệt Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách chính xác mệnh đề ngoại lệ.  
> Về mặt trade-off: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do chunk lớn vô tình gom nhiều điều kiện; và Exact Locator Recall@5 tại Bảng 3.11 LightRAG cao hơn (0,8509 vs 0,5560) do đo khớp chuỗi ký tự cục bộ, trong khi UKG ưu tiên toàn vẹn thực thể cấp Điều.  
> Về RQ4: UKG định vị tốt node đích với Reference-target Recall 58,67%. Tái dựng chuỗi thứ tự cần thêm giải thuật Constrained Graph Traversal (Chain Exact Match đạt 0,0000 trên 18 câu)."*"""

s13_old = """> *"Từ các kết quả trên, đề tài đóng góp ba giá trị cốt lõi:  
> Một là Khung kiểm chuẩn Benchmark A và B cùng Adapter Pattern loại bỏ thiên lệch thực nghiệm.  
> Hai là Giải pháp phân đoạn vi mô phối hợp Parser v2 và MaxP, giải quyết triệt để sụt giảm trích dẫn và tối ưu chi phí.  
> Ba là Kiến trúc đồ thị hai tầng Hybrid UKG, chứng minh hiệu quả của việc phân tách cấu trúc vật lý và ngữ nghĩa động trong xử lý quy phạm ngoại lệ.  
> Thông điệp cốt lõi của đề tài là: Trong pháp luật, cấu trúc không phải là chi tiết triển khai — nó là điều kiện tiên quyết để AI có thể trích dẫn đúng."*"""

s13_new = """> *"Từ các kết quả trên, đề tài đóng góp ba giá trị cốt lõi:  
> Một là Khung kiểm chuẩn Benchmark A và B cùng Adapter Pattern loại bỏ thiên lệch thực nghiệm.  
> Hai là Giải pháp phân đoạn vi mô phối hợp Parser v2 và MaxP, giải quyết triệt để sụt giảm trích dẫn và tối ưu chi phí.  
> Ba là Kiến trúc đồ thị hai tầng Hybrid UKG, chứng minh hiệu quả phân tách cấu trúc vật lý và ngữ nghĩa động trong xử lý quy phạm ngoại lệ.  
> Thông điệp cốt lõi của đề tài là: Trong pháp luật, cấu trúc không phải là chi tiết triển khai — nó là điều kiện tiên quyết để AI trích dẫn đúng."*"""

for o, n in [(s1_old, s1_new), (s2_old, s2_new), (s9_old, s9_new), (s10_old, s10_new), (s11_old, s11_new), (s13_old, s13_new)]:
    if o in text:
        text = text.replace(o, n)
    else:
        print('Warning: target not found!')

with open('c:/Users/luuth/NCKH/Benchmark/06_tools_and_audits/update_kich_ban_15p.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated update_kich_ban_15p.py successfully.')

