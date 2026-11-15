# -*- coding: utf-8 -*-
slides_tight = [
    # SLIDE 1 (Lâm) ~40 words
    """Kính thưa quý thầy cô trong Hội đồng!
Chúng em gồm Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng.
Đề tài của nhóm là "Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù", tập trung vào văn bản pháp luật Việt Nam.""",

    # SLIDE 2 (Lâm) ~90 words
    """Chúng em xin bắt đầu bằng một ví dụ thực tế:
Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?
Theo điểm c khoản 1 Điều 34 Luật Đất đai 2024, chủ thể này có quyền bán tài sản của mình. Nhưng trường hợp bán kèm quyền thuê trong hợp đồng, luật dẫn chiếu sang Điều 46 để ràng buộc điều kiện.
Nếu chỉ tìm được Điều 34, câu trả lời sẽ thiếu điều kiện cốt tử. Hệ thống bắt buộc phải truy hồi sang Điều 46, tổng hợp điều kiện và viện dẫn chính xác từng Khoản, Điểm.""",

    # SLIDE 3 (Dương) ~70 words
    """Văn bản pháp luật có ba đặc thù lớn ảnh hưởng đến truy hồi:
Một là cấu trúc phân cấp: Một Điểm chỉ có nghĩa khi gắn liền với Khoản và Điều chứa nó; tách rời phân cấp sẽ làm mất chủ thể và phạm vi áp dụng.
Hai là dẫn chiếu chéo: Quy định nêu quyền ở một nơi, nhưng điều kiện lại ở điều khác.
Ba là khoảng cách giữa ngôn ngữ đời thường và thuật ngữ quy phạm.""",

    # SLIDE 4 (Dương) ~75 words
    """Nhóm khảo sát ba kiến trúc đại diện cho ba hướng tiếp cận:
Naive Vector RAG dùng độ tương đồng ngữ nghĩa qua vector BGE-M3.
Hybrid RAG kết hợp BM25, Dense Retrieval, dung hợp thứ hạng RRF và tái xếp hạng Cross-Encoder.
LightRAG tiếp cận theo hướng đồ thị thực thể phi cấu trúc.
Cả ba kiến trúc đều chia sẻ tiền đề chung: Cắt đoạn theo token phi cấu trúc. Đây là đối sánh cấp hệ thống, chưa tách riêng đóng góp từng thành phần.""",

    # SLIDE 5 (Dương) ~55 words
    """Nghiên cứu được thiết kế theo ba giai đoạn:
Giai đoạn một đánh giá ba kiến trúc RAG cơ sở trên văn bản thô, tương ứng RQ1.
Giai đoạn hai khảo sát phân đoạn cấu trúc bằng Parser, Validation và MaxP, tương ứng RQ2.
Giai đoạn ba phát triển Hybrid Parser/UKG, đánh giá khả năng xử lý điều kiện, ngoại lệ và chuỗi dẫn chiếu, tương ứng RQ3 và RQ4.""",

    # SLIDE 6 (Dương) ~95 words
    """Nhóm xây dựng hai bộ benchmark độc lập:
Benchmark A gồm 2.087 Điều thuộc 7 đạo luật và 512 câu hỏi. Tập Tier 1 gồm 205 câu có căn cứ nằm trọn trong 500 Điều LightRAG index, bảo đảm công bằng về độ phủ dữ liệu ở Giai đoạn 1. Một phần câu hỏi được diễn đạt lại để giảm trùng lặp từ vựng.
Benchmark B gồm 50 câu tại Chương III Luật Đất đai 2024, được gán nhãn chi tiết đến Khoản, Điểm, điều kiện, ngoại lệ và dẫn chiếu.
Truy hồi cơ bản được đo bằng Recall@5 ở cấp Điều và MRR@5.""",

    # SLIDE 7 (Lâm) ~85 words
    """Trên 205 câu Tier 1, cả ba hệ thống đều truy hồi rất tốt: Recall@5 đều vượt 0,95; Hybrid RAG xếp ưu tiên tốt nhất với MRR@5 đạt 0,9243.
Thế nhưng, Bảng 3.4 chỉ ra một nghịch lý: Citation Accuracy trong câu trả lời lại rất thấp: Naive đạt 0,3259; Hybrid đạt 0,2902; và LightRAG chỉ đạt 0,1371.
Truy hồi đúng Điều luật chưa đồng nghĩa với việc mô hình trích dẫn đúng Khoản, Điểm hay nêu đủ căn cứ. Khoảng cách này mở đường cho Giai đoạn 2.""",

    # SLIDE 8 (Lâm) ~80 words
    """Ở Giai đoạn 2, nhóm thay đổi đơn vị dữ liệu:
Triển khai Regex Parser để bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô cấp Khoản, Điểm. Sau đó, Validation kiểm tra tính toàn vẹn của cây phân cấp.
Mỗi phân đoạn được bổ sung tiền tố phân cấp để giữ trọn vị trí nguồn.
Để tránh Top-5 bị chiếm trọn bởi một Điều, nhóm tích hợp Article-level MaxP: Điểm của Điều lấy theo điểm cao nhất của các phân đoạn con. MaxP là kỹ thuật kế thừa, nhóm tích hợp và kiểm chứng thực nghiệm.""",

    # SLIDE 9 (Lâm) ~95 words
    """Trên 512 câu hỏi Benchmark A, đối chiếu C2 Naive Dense và C5 Parser Dense cho thấy:
Mức tăng quan sát được ở Recall@5 là từ 0,9141 lên 0,9316; và MRR@5 tăng từ 0,8129 lên 0,8602 (+4,73 điểm phần trăm).
C5 đạt LLM-Judge Citation Accuracy 0,9902 trên ngữ cảnh (504/512 câu đạt 1,0); đồng thời dung lượng ngữ cảnh giảm 79,9%, từ 2.898 xuống 580 token. Đây là điểm thẩm định ngữ cảnh, chưa phải câu trả lời hoàn chỉnh chính xác 99%.
C5 giải quyết tốt bài toán trong một Điều. Để xử lý liên Điều, nhóm xây dựng UKG ở Giai đoạn 3.""",

    # SLIDE 10 (Minh) ~85 words
    """Kiến trúc Hybrid UKG kết hợp hai tầng tri thức trên Neo4j:
Physical Graph lưu cấu trúc phân cấp Điều, Khoản, Điểm. Semantic Graph lưu thực thể quy phạm như chủ thể, điều kiện, ngoại lệ và quan hệ dẫn chiếu.
Quay lại câu hỏi mở đầu, luồng truy hồi M10 vận hành như sau:
M10 xuất phát từ điểm c khoản 1 Điều 34 quy định quyền bán tài sản. Nhận diện dẫn chiếu, hệ thống mở rộng sang Điều 46 để gom các Khoản điều kiện. Chế độ AUTO_FUSION kết hợp thông tin cấu trúc và ngữ nghĩa, rồi chuyển ngữ cảnh cho GPT-4o-mini tạo câu trả lời.""",

    # SLIDE 11 (Minh) ~140 words
    """Trên Benchmark B, nhóm đối sánh trực diện với LightRAG theo ba tầng:
Một là, về truy hồi ở cấp Điều: Trên 47 câu đủ căn cứ, Hybrid UKG đạt Recall@5 bằng 0,9184 (so với 0,7358) và MRR@5 đạt 0,8848 (so với 0,5539).
Hai là, về câu trả lời: Hybrid UKG đạt Legal Correctness 0,8777 (so với 0,8210) và Exception Coverage 0,6786 (so với 0,3929). Ở cấp Khoản, Citation Precision đạt 0,7757 và Recall đạt 0,8170 (LightRAG đều là 0,0435).
Ba là, về ranh giới điều kiện: Condition Coverage của UKG chỉ đạt 0,7066, thấp hơn LightRAG ở mức 0,8421. Hạn chế này thể hiện rõ ở câu B012: UKG chỉ đạt 0,1250 còn LightRAG đạt 1,0000 do điều kiện tại Điều 46 bị phân tán.
Về dẫn chiếu, UKG tìm được 58,67% căn cứ đích, nhưng Chain Exact Match là 0/18 (LightRAG ghi nhận N/A).""",

    # SLIDE 12 (Minh) ~75 words
    """Từ ba giai đoạn, nhóm rút ra kết luận cho bốn RQ:
Với RQ1: Cải thiện truy hồi trên văn bản thô giúp tăng thứ bậc nhưng không giải quyết được chất lượng trích dẫn; tìm đúng tài liệu chưa đồng nghĩa với tạo sinh đúng.
Với RQ2: Phân đoạn vi mô kết hợp MaxP cải thiện rõ rệt việc định vị căn cứ và tiết kiệm 79,9% token ngữ cảnh.
Với RQ3: Hybrid UKG vượt trội ở trích dẫn Khoản, Điểm và ngoại lệ, nhưng còn hạn chế khi tổng hợp các điều kiện phân tán.
Với RQ4: Hệ thống tìm được hơn một nửa căn cứ đích nhưng chưa thể tái dựng chuỗi dẫn chiếu hoàn chỉnh.""",

    # SLIDE 13 (Minh) ~65 words
    """Nhóm xác định rõ ba đóng góp chính:
Thứ nhất, xây dựng Benchmark A, Benchmark B cùng khung đánh giá chuyên biệt để đối sánh các hệ thống RAG trên dữ liệu luật Việt Nam.
Thứ hai, triển khai và đánh giá thực nghiệm gói phân đoạn cấu trúc bằng Regex Parser, Validation và Article MaxP.
Thứ ba, thiết kế và hiện thực hóa kiến trúc Hybrid UKG kết hợp đồ thị cấu trúc với dữ liệu ngữ nghĩa.
Các thuật toán nền tảng là kế thừa; đóng góp tập trung vào tích hợp và kiểm chứng thực nghiệm.""",

    # SLIDE 14 (Minh) ~50 words
    """Trở lại câu hỏi mở đầu: Để trả lời đúng một câu hỏi pháp lý, tìm được Điều luật là chưa đủ, mà phải nắm bắt được điều kiện, ngoại lệ và căn cứ dẫn chiếu.
Hướng nghiên cứu tiếp theo gồm: Nâng cao khả năng tổng hợp điều kiện, tái dựng chuỗi dẫn chiếu; mở rộng Parser sang văn bản dưới luật và quản lý hiệu lực văn bản.
Chúng em xin trân trọng cảm ơn quý thầy cô trong Hội đồng đã lắng nghe!"""
]

total = 0
for i, s in enumerate(slides_tight):
    w = len(s.split())
    total += w
    print(f"Slide {i+1:02d}: {w:3d} words")
print("-" * 30)
print(f"TOTAL WORDS: {total}")
time_min = total / 130
print(f"Time @ 130 wpm: {time_min:.2f} mins ({total/(130/60):.0f}s)")
print(f"Buffer in 10 mins: {600 - total/(130/60):.0f}s")

