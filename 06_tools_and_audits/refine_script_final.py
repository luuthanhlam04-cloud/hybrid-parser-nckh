# -*- coding: utf-8 -*-
with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

s2_cur = """> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, nghiên cứu của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tế, chỉ cần trích dẫn đúng số Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu tìm kiếm, vừa giúp mô hình xác định chính xác căn cứ vi mô mà không bùng nổ dung lượng ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*"""

s2_tar = """> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Nghiên cứu của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra các AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tế, chỉ cần trích dẫn đúng Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn từ hợp pháp sang vi phạm.  
> Nhóm đặt bài toán cốt lõi: Làm sao tối ưu tìm kiếm và giúp mô hình định vị đúng căn cứ vi mô mà không làm bùng nổ ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*"""

s8_cur = """> *"Để khắc phục khoảng cách trên, bước sang Giai đoạn 2, nhóm đề xuất gói giải pháp cấu trúc:  
> Bộ phân tích Structure-Aware Parser v2 bóc tách đệ quy văn bản luật thành 12.754 phân đoạn vi mô theo từng cấp Khoản, Điểm, gắn tiền tố cấu trúc bất biến chứa đầy đủ phả hệ từ tên Luật, Chương đến Điều, giúp duy trì thông tin định vị và quan hệ phân cấp.  
> Đồng thời, để xử lý việc phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng một Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling. Hệ thống gom cụm phân đoạn theo Điều, lấy điểm cực đại để xếp hạng cấp Điều; sau đó lựa chọn các phân đoạn vi mô liên quan để xây dựng ngữ cảnh đưa vào mô hình ngôn ngữ.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*"""

s8_tar = """> *"Để giải quyết khoảng cách trên, ở Giai đoạn 2, nhóm đề xuất giải pháp cấu trúc:  
> Bộ phân tích Structure-Aware Parser v2 bóc tách đệ quy văn bản thành 12.754 phân đoạn vi mô cấp Khoản, Điểm; gắn tiền tố phả hệ bất biến từ Luật, Chương đến Điều, bảo toàn thông tin định vị phân cấp.  
> Nhằm tránh bão hòa Top-K bởi nhiều Khoản cùng Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling: gom cụm phân đoạn theo Điều, lấy điểm cực đại để xếp hạng cấp Điều; sau đó chọn lọc phân đoạn vi mô liên quan đưa vào mô hình.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*"""

s9_cur = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2:  
> Cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902, tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, nhờ phân đoạn vi mô và MaxP, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống còn 580 token.  
> Khảo sát tại Bảng 3.7 ghi nhận cấu hình cân bằng alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, cải thiện so với cấu hình cào bằng ở C6.  
> Nhóm lưu ý: Giai đoạn 2 đánh giá riêng chất lượng căn cứ trong ngữ cảnh truy hồi bằng LLM-Judge, thay vì chấm câu trả lời hoàn chỉnh. Kết quả C2 và C5 phản ánh tác động tích cực của gói xử lý cấu trúc trong điều kiện Dense Retrieval, tạo tiền đề để đánh giá toàn trình ở Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*"""

s9_tar = """> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt đánh giá LLM-Judge, Bảng 3.6 làm sáng tỏ RQ2:  
> Cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 lên 0,9902, tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống còn 580 token.  
> Bảng 3.7 ghi nhận cấu hình cân bằng alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, cải thiện rõ rệt so với C6.  
> Nhóm lưu ý: Giai đoạn 2 đánh giá riêng căn cứ trong ngữ cảnh bằng LLM-Judge, chưa chấm câu trả lời hoàn chỉnh. Kết quả C2 và C5 phản ánh tác động tích cực của cấu trúc trong Dense Retrieval, làm tiền đề cho Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày tiếp."*"""

s10_cur = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý — sử dụng các quy tắc xác định trước để xây dựng cấu trúc phân cấp, Module 3 Validation cách ly các node lỗi nghiêm trọng.  
> Tầng 2 là Đồ thị ngữ nghĩa — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Các bước xử lý tri thức thực hiện trong quá trình lập chỉ mục; khi truy vấn, hệ thống duyệt đồ thị đã dựng để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng mô hình Qwen2.5-0.5B kết hợp toán tử Max-Fusion giữa Regex và Vector. Tại ngưỡng theta = 0,85 trên Golden Set 193 node, hệ thống đạt Recall 96,85%, F1 0,8146, loại 9,33% phân đoạn thủ tục, chấp nhận ranh giới đánh đổi 4 node quy phạm bị bỏ sót."*"""

s10_tar = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG hai tầng:  
> Tầng 1 là Đồ thị vật lý — dùng quy tắc tất định dựng phân cấp, Module 3 Validation cách ly các node lỗi.  
> Tầng 2 là Đồ thị ngữ nghĩa — trích xuất động quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Quá trình xử lý tri thức thực hiện lúc lập chỉ mục; khi truy vấn, hệ thống duyệt đồ thị để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: kết hợp mô hình Qwen2.5-0.5B và toán tử Max-Fusion giữa Regex và Vector. Tại ngưỡng theta = 0,85 trên Golden Set 193 node, hệ thống đạt Recall 96,85%, F1 0,8146, loại 9,33% phân đoạn thủ tục, chấp nhận ranh giới 4 node quy phạm bị bỏ sót."*"""

s11_cur = """> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4:  
> Về truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Về chất lượng trích dẫn và nội dung, Citation Precision cấp Điều đạt 0,8369 vs 0,3333 (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp 18 lần). Ở tầng nội dung, Legal Correctness đạt 0,8777 và Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách mệnh đề ngoại lệ.  
> Về ranh giới kỹ thuật: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do phân đoạn vi mô cần thêm cơ chế lan truyền điều kiện diện rộng. Về RQ4, UKG định vị được 58,67% node đích, nhưng việc tái dựng chuỗi thứ tự cần thêm giải thuật duyệt đồ thị có ràng buộc khi Chain Exact Match ghi nhận 0,0000 trên 18 câu.  
> Chỉ số Exact Locator Recall@5 đạt 0,5560 vs 0,8509 do khác biệt độ hạt: chunk LightRAG chứa trung bình ~15 locator trong khi phân đoạn UKG chỉ mang 1 locator."*"""

s11_tar = """> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4:  
> Về truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Về chất lượng trích dẫn, Citation Precision cấp Điều đạt 0,8369 vs 0,3333 (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp 18 lần). Ở tầng nội dung, Legal Correctness đạt 0,8777 và Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 đpt nhờ bóc tách ngoại lệ.  
> Về ranh giới kỹ thuật: Condition Coverage đạt 0,7066 vs 0,8421 do phân đoạn vi mô cần thêm cơ chế lan truyền diện rộng. Về RQ4, UKG định vị 58,67% node đích, nhưng việc tái dựng chuỗi cần thêm giải thuật duyệt đồ thị khi Chain Exact Match đạt 0,0000 trên 18 câu.  
> Chỉ số Exact Locator Recall@5 đạt 0,5560 vs 0,8509 do khác biệt độ hạt: chunk LightRAG chứa trung bình ~15 locator trong khi phân đoạn UKG chỉ mang 1 locator."*"""

for cur, tar, name in [(s2_cur, s2_tar, 'Slide 2'), (s8_cur, s8_tar, 'Slide 8'), (s9_cur, s9_tar, 'Slide 9'), (s10_cur, s10_tar, 'Slide 10'), (s11_cur, s11_tar, 'Slide 11')]:
    if cur in text:
        text = text.replace(cur, tar)
        print(f'Replaced {name} successfully')
    else:
        print(f'Match failed for {name}')

with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done writing updated markdown.')
