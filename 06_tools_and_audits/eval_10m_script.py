# -*- coding: utf-8 -*-
"""
Prototype 1,200-Word Script for 10-Minute Defense
Strictly incorporating all 4 fixes from GPT:
1. Slide 2: Phân biệt bán tài sản vs bán tài sản kèm quyền thuê (Điều 34 c khoản 1 -> Điều 46).
2. Slide 7: Khôi phục Citation Accuracy (Naive 0.3259, Hybrid 0.2902, LightRAG 0.1371).
3. Slide 8: Tách bạch Parser (bóc tách) vs Validation (kiểm tra tính toàn vẹn).
4. Slide 11: Ghi rõ Recall@5 đo tại cấp Điều; bổ sung Citation Precision cấp Khoản (0.7757 vs 0.0435); đưa ca B012 (Condition Coverage 0.1250 vs 1.0000).
"""

slides_10m = [
    # SLIDE 1 (Lâm) ~45 words
    """Kính thưa quý thầy cô trong Hội đồng!
Chúng em gồm Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng.
Đề tài của nhóm là "Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù", tập trung vào văn bản pháp luật Việt Nam.""",

    # SLIDE 2 (Lâm) ~95 words
    """Chúng em xin bắt đầu bằng một ví dụ thực tế:
Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?
Theo điểm c khoản 1 Điều 34 Luật Đất đai 2024, chủ thể này có quyền bán tài sản thuộc sở hữu của mình. Nhưng với trường hợp bán kèm quyền thuê trong hợp đồng, quy định lại dẫn chiếu sang Điều 46 để ràng buộc các điều kiện cụ thể.
Nếu chỉ tìm được Điều 34, câu trả lời sẽ thiếu điều kiện cốt tử. Hệ thống bắt buộc phải truy hồi sang Điều 46, tổng hợp điều kiện và viện dẫn chính xác từng Khoản, Điểm.""",

    # SLIDE 3 (Dương) ~75 words
    """Văn bản pháp luật có ba đặc thù lớn ảnh hưởng đến truy hồi:
Một là cấu trúc phân cấp: Một Điểm chỉ có nghĩa khi gắn liền với Khoản và Điều chứa nó; tách rời phân cấp sẽ làm mất chủ thể và phạm vi áp dụng.
Hai là quan hệ dẫn chiếu chéo: Quy định nêu quyền ở một nơi, nhưng điều kiện và ngoại lệ lại ở điều luật khác.
Ba là khoảng cách ngôn ngữ giữa câu hỏi đời thường và thuật ngữ quy phạm.
Vì vậy, bài toán đòi hỏi phải bảo toàn cấu trúc và quan hệ giữa các quy định.""",

    # SLIDE 4 (Dương) ~85 words
    """Nhóm khảo sát ba kiến trúc đại diện cho ba hướng tiếp cận truy hồi khác nhau:
Naive Vector RAG dùng độ tương đồng ngữ nghĩa qua vector BGE-M3.
Hybrid RAG kết hợp BM25, Dense Retrieval, dung hợp thứ hạng bằng RRF và tái xếp hạng bằng Cross-Encoder.
LightRAG tiếp cận theo hướng đồ thị, dùng LLM trích xuất thực thể và quan hệ để liên kết thông tin.
Cả ba kiến trúc đều chia sẻ một tiền đề chung: Cắt đoạn theo token phi cấu trúc. Đây là đối sánh cấp hệ thống, chưa tách riêng mức đóng góp của từng thuật toán.""",

    # SLIDE 5 (Dương) ~65 words
    """Nghiên cứu được thiết kế theo ba giai đoạn:
Giai đoạn một đánh giá ba kiến trúc RAG cơ sở trên văn bản cắt đoạn thô, tương ứng RQ1.
Giai đoạn hai khảo sát phương án phân đoạn cấu trúc bằng Parser, Validation và Article MaxP, tương ứng RQ2.
Giai đoạn ba phát triển Hybrid Parser/UKG, đánh giá khả năng xử lý điều kiện, ngoại lệ và tái dựng chuỗi dẫn chiếu, tương ứng RQ3 và RQ4.""",

    # SLIDE 6 (Dương) ~105 words
    """Nhóm xây dựng hai bộ benchmark độc lập:
Benchmark A gồm 2.087 Điều thuộc 7 đạo luật và 512 câu hỏi. Nhóm thiết lập tập Tier 1 gồm 205 câu có căn cứ nằm trọn trong 500 Điều LightRAG đã index, bảo đảm công bằng về độ phủ dữ liệu ở Giai đoạn 1. Một phần câu hỏi được diễn đạt lại để giảm trùng lặp từ vựng.
Benchmark B gồm 50 câu tại Chương III Luật Đất đai 2024, được gán nhãn chi tiết đến Khoản, Điểm, điều kiện, ngoại lệ và chuỗi dẫn chiếu; được nhóm kiểm tra, chưa phải thẩm định pháp lý độc lập.
Hiệu năng truy hồi cơ bản được đo bằng Recall@5 ở cấp Điều và MRR@5.""",

    # SLIDE 7 (Lâm) ~95 words
    """Trên 205 câu Tier 1, cả ba hệ thống đều truy hồi tài liệu rất tốt: Recall@5 đều vượt 0,95 (Naive 0,9561; Hybrid và LightRAG cùng đạt 0,9659). Về thứ bậc, Hybrid RAG ưu tiên căn cứ tốt nhất với MRR@5 đạt 0,9243.
Thế nhưng, Bảng 3.4 chỉ ra một nghịch lý lớn: Độ chính xác trích dẫn Citation Accuracy trong câu trả lời lại rất thấp: Naive chỉ đạt 0,3259; Hybrid đạt 0,2902; và LightRAG chỉ đạt 0,1371.
Truy hồi đúng Điều luật không đồng nghĩa với việc mô hình trích dẫn đúng Khoản, Điểm hay nêu đủ căn cứ. Khoảng cách này là động lực để nhóm tiến sang Giai đoạn 2.""",

    # SLIDE 8 (Lâm) ~85 words
    """Để khắc phục khoảng cách này, nhóm thay đổi đơn vị dữ liệu ở Giai đoạn 2.
Nhóm triển khai Regex Parser để bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô ở cấp Khoản và Điểm. Sau đó, Module Validation kiểm tra tính toàn vẹn của cây phân cấp.
Mỗi phân đoạn con được bổ sung tiền tố phân cấp để giữ trọn vị trí trong văn bản gốc.
Để tránh Top-5 bị chiếm trọn bởi các phân đoạn của cùng một Điều, nhóm tích hợp Article-level MaxP: Điểm của một Điều được lấy bằng điểm cao nhất của các phân đoạn con thuộc Điều đó. MaxP là kỹ thuật kế thừa, đóng góp của nhóm là tích hợp với cấu trúc phân cấp pháp lý.""",

    # SLIDE 9 (Lâm) ~105 words
    """Trên 512 câu hỏi Benchmark A, đối chiếu C2 Naive Dense và C5 Parser Dense cho thấy bước chuyển biến rõ nét:
Mức tăng quan sát được ở Recall@5 là từ 0,9141 lên 0,9316; và MRR@5 tăng từ 0,8129 lên 0,8602, tức tăng hơn 4,7 điểm phần trăm về khả năng ưu tiên căn cứ.
C5 đạt điểm LLM-Judge Citation Accuracy trung bình 0,9902 trên ngữ cảnh (504/512 câu đạt 1,0); đồng thời dung lượng ngữ cảnh trung bình giảm từ 2.898 xuống 580 token, tương đương giảm 79,9%. Đây là điểm đánh giá tự động trên ngữ cảnh, chưa phải tỷ lệ câu trả lời hoàn chỉnh chính xác 99%.
C5 giải quyết tốt bài toán trong phạm vi một Điều. Để khai thác quan hệ liên Điều, nhóm xây dựng UKG ở Giai đoạn 3.""",

    # SLIDE 10 (Minh) ~95 words
    """Kiến trúc Hybrid UKG gồm mười module, kết hợp hai tầng tri thức trên Neo4j:
Physical Graph lưu giữ cấu trúc phân cấp Luật, Điều, Khoản, Điểm. Semantic Graph lưu các thực thể quy phạm như chủ thể, điều kiện, ngoại lệ và quan hệ dẫn chiếu.
Quay lại câu hỏi mở đầu, luồng truy hồi M10 vận hành như sau:
M10 xuất phát từ điểm c khoản 1 Điều 34 quy định quyền bán tài sản. Nhận diện dẫn chiếu, hệ thống mở rộng sang Điều 46 để gom các Khoản điều kiện. Chế độ AUTO_FUSION kết hợp thông tin cấu trúc và ngữ nghĩa, rồi chuyển ngữ cảnh tinh gọn cho GPT-4o-mini tạo câu trả lời. Năng lực thực tế phải được kiểm chứng qua Benchmark B.""",

    # SLIDE 11 (Minh) ~155 words
    """Trên Benchmark B, nhóm đối sánh trực diện với LightRAG theo ba tầng:
Thứ nhất, về truy hồi ở cấp Điều: Trên 47 câu đủ căn cứ, Hybrid UKG đạt Recall@5 bằng 0,9184 (so với 0,7358) và MRR@5 đạt 0,8848 (so với 0,5539).
Thứ hai, về câu trả lời: Hybrid UKG đạt Legal Correctness 0,8777 (so với 0,8210) và Exception Coverage 0,6786 (so với 0,3929). Ở cấp Khoản, Citation Precision đạt 0,7757 và Recall đạt 0,8170, trong khi LightRAG đều là 0,0435.
Tuy nhiên, Condition Coverage của UKG chỉ đạt 0,7066, thấp hơn LightRAG ở mức 0,8421. Hạn chế này thể hiện rõ ngay ở câu B012 có nội dung như ví dụ mở đầu: UKG chỉ đạt 0,1250 trong khi LightRAG đạt 1,0000 do điều kiện tại Điều 46 bị phân tán phức tạp.
Ở phép đo Exact Locator Recall@5, LightRAG đạt 0,8509 trên 47 câu, UKG đạt 0,5560 trên 39 câu đo được do khác biệt về độ hạt phân đoạn.
Thứ ba, về dẫn chiếu: UKG tìm được 58,67% căn cứ đích, nhưng Chain Exact Match là 0/18 (LightRAG ghi nhận N/A).""",

    # SLIDE 12 (Minh) ~75 words
    """Từ ba giai đoạn, nhóm rút ra kết luận cho bốn RQ:
Với RQ1: Cải thiện truy hồi trên văn bản thô giúp tăng thứ bậc nhưng không giải quyết được chất lượng trích dẫn; tìm đúng tài liệu chưa đồng nghĩa với tạo sinh đúng.
Với RQ2: Phân đoạn vi mô kết hợp MaxP cải thiện rõ rệt việc định vị căn cứ và tiết kiệm 79,9% token ngữ cảnh.
Với RQ3: Hybrid UKG vượt trội ở trích dẫn Khoản, Điểm và ngoại lệ, nhưng còn hạn chế khi tổng hợp các điều kiện phân tán.
Với RQ4: Hệ thống tìm được hơn một nửa căn cứ đích nhưng chưa thể tái dựng chuỗi dẫn chiếu hoàn chỉnh.""",

    # SLIDE 13 (Minh) ~70 words
    """Nhóm tổng hợp ba nhóm đóng góp chính:
Thứ nhất, xây dựng Benchmark A, Benchmark B cùng khung đánh giá chuyên biệt để đối sánh các hệ thống RAG trên dữ liệu luật Việt Nam.
Thứ hai, triển khai và đánh giá thực nghiệm gói phân đoạn cấu trúc bằng Regex Parser, Validation và Article MaxP.
Thứ ba, thiết kế và hiện thực hóa kiến trúc Hybrid UKG kết hợp đồ thị cấu trúc với dữ liệu ngữ nghĩa.
Các thuật toán nền tảng là kế thừa; đóng góp của nhóm tập trung vào thiết kế, tích hợp và kiểm chứng thực nghiệm.""",

    # SLIDE 14 (Minh) ~55 words
    """Trở lại câu hỏi mở đầu: Để trả lời đúng một câu hỏi pháp lý, tìm được Điều luật là chưa đủ, mà phải nắm bắt được điều kiện, ngoại lệ và căn cứ dẫn chiếu.
Hướng nghiên cứu tiếp theo gồm: Mở rộng Parser sang nghị định, thông tư; nâng cao khả năng tổng hợp điều kiện và tái dựng chuỗi dẫn chiếu; cùng cơ chế quản lý hiệu lực văn bản.
Chúng em xin trân trọng cảm ơn các thầy cô trong Hội đồng đã lắng nghe!"""
]

total = 0
for i, s in enumerate(slides_10m):
    w = len(s.split())
    total += w
    print(f"Slide {i+1:02d}: {w:3d} words")
print("-" * 30)
print(f"TOTAL WORDS: {total}")
time_min = total / 130
print(f"Time @ 130 wpm: {time_min:.2f} mins ({total/(130/60):.0f}s)")
print(f"Buffer: {600 - total/(130/60):.0f}s")

