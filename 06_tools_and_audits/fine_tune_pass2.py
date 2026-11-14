# -*- coding: utf-8 -*-
with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

s1_old = """> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm nghiên cứu gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*"""

s1_new = """> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*"""

s6_old = """> *"Để trả lời bốn RQ, nhóm xây dựng hạ tầng Benchmark Harness áp dụng Adapter Pattern, đóng băng toàn bộ biến ngoại lai: cùng ngữ liệu, cùng embedding BGE-M3 và cùng LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, áp dụng quy trình viết lại chọn lọc cho các câu có độ trùng lặp cao, đưa chỉ số Jaccard trung bình từ 0,68 xuống 0,31 để loại bỏ triệt để thiên lệch học vẹt từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu các tình huống đa điều kiện, ngoại lệ và dẫn chiếu chéo.  
> Sau đây, xin mời bạn Lâm trình bày kết quả Giai đoạn 1 và 2."*"""

s6_new = """> *"Để trả lời bốn RQ, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện Adapter Pattern, đóng băng toàn bộ biến ngoại lai: cùng ngữ liệu, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, viết lại chọn lọc đưa Jaccard trung bình từ 0,68 xuống 0,31 để loại bỏ triệt để thiên lệch học vẹt từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu đa điều kiện, ngoại lệ và dẫn chiếu.  
> Sau đây, xin mời bạn Lâm trình bày kết quả."*"""

s7_old = """> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Khi đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi có đáp án trọn vẹn, nhóm phát hiện nghịch lý: Khoảng cách giữa truy hồi và trích dẫn.  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm tài liệu rất tốt: Recall@5 đều vượt 95%, Context Precision của Naive và Hybrid đạt trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, khi đánh giá câu trả lời cuối cùng, Citation Accuracy sụt giảm nghiêm trọng: Naive Vector chỉ đạt 32,59%, Hybrid đạt 29,02%, và LightRAG ghi nhận mức thấp nhất là 13,71%.  
> Nguyên nhân là phương pháp cắt khối thô 1.200 token làm đứt gãy phả hệ: Điểm trích dẫn bị tách rời khỏi tên Điều và Chương, khiến mô hình ngôn ngữ không đủ thông tin xác lập căn cứ.  
> Kết quả này trả lời cho RQ1: RAG cơ sở thất bại ở bài toán trích dẫn nếu giữ nguyên phương thức cắt đoạn thô."*"""

s7_new = """> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm phát hiện khoảng cách giữa truy hồi và trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm rất tốt: Recall@5 vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy sụt giảm nghiêm trọng: Naive Vector chỉ đạt 32,59%, Hybrid đạt 29,02%, và LightRAG chỉ 13,71%.  
> Nguyên nhân: cắt khối thô 1.200 token làm đứt gãy phả hệ; Điểm trích dẫn bị tách rời tên Điều và Chương, khiến LLM mất căn cứ xác lập vị trí pháp lý.  
> Kết quả này trả lời cho RQ1: RAG cơ sở thất bại ở trích dẫn nếu giữ nguyên cắt đoạn thô."*"""

s10_old = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — khóa cứng bất biến 100% phả hệ văn bản luật bằng bộ phân tích tất định.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Xây dựng đồ thị là tác vụ Offline Indexing chạy một lần duy nhất; khi truy vấn online, hệ thống duyệt đồ thị trong mili-giây.  
> Điểm nhấn là Module 5 Semantic Router: Ứng dụng mô hình nhân quả Qwen2.5-0.5B kết hợp toán tử Max-Fusion logic OR giữa Regex và Vector. Causal Attention bảo toàn logic chủ thể - điều kiện - chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder. Tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục."*"""

s10_new = """> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng Hybrid UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — khóa cứng bất biến 100% phả hệ văn bản luật bằng bộ phân tích tất định.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Đồ thị được lập chỉ mục offline một lần; khi truy vấn online, hệ thống duyệt đồ thị trong mili-giây.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng Qwen2.5-0.5B kết hợp Max-Fusion logic OR giữa Regex và Vector. Causal Attention bảo toàn logic chủ thể - điều kiện - chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder. Tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục."*"""

s14_old = """> *"Trong thời gian tới, nhóm hướng đến mở rộng sang văn bản dưới luật như Nghị định, Thông tư; tự động hóa cập nhật hiệu lực; và hoàn thiện giải thuật constrained graph traversal.  
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*"""

s14_new = """> *"Trong thời gian tới, nhóm hướng đến mở rộng sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực; và hoàn thiện giải thuật constrained graph traversal.  
> Thay mặt nhóm, chúng em xin trân trọng cảm ơn Quý Thầy Cô đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*"""

for o, n in [(s1_old, s1_new), (s6_old, s6_new), (s7_old, s7_new), (s10_old, s10_new), (s14_old, s14_new)]:
    if o in text:
        text = text.replace(o, n)
    else:
        print('Warning: target not found!')

with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated kich_ban_thuyet_trinh_15p.md directly.')

