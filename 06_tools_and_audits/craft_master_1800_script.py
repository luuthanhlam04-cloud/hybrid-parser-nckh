# -*- coding: utf-8 -*-
"""
Perfected 1800-Word Master Script
Strictly calibrated to ~600 words per block:
- Block 1 (Slide 1-6): ~600 words (~4m37s)
- Block 2 (Slide 7-10): ~590 words (~4m32s)
- Block 3 (Slide 11-14): ~590 words (~4m32s)
Total: ~1,780 words (~13m41s @ 130 wpm), leaving a 1m19s safe buffer.
"""

slides_data = [
    # SLIDE 1
    {
        "slide": 1,
        "title": "Trang bìa & Giới thiệu đề tài",
        "speaker": "Lưu Thanh Lâm",
        "blueprint": "Tiêu đề đề tài NCKH, thông tin 3 sinh viên, GVHD TS. Nguyễn Mạnh Dũng, logo trường và khoa.",
        "spoken": """Kính thưa Hội đồng và các thầy cô.
Chúng em gồm Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng.
Đề tài của nhóm là "Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù", tập trung vào văn bản pháp luật Việt Nam.
Nhóm xin báo cáo từ nghịch lý của các RAG cơ sở, đến giải pháp phân đoạn cấu trúc và kiểm chứng đồ thị tri thức lai."""
    },

    # SLIDE 2
    {
        "slide": 2,
        "title": "Bài toán thực tiễn bắt đầu từ một câu hỏi",
        "speaker": "Lưu Thanh Lâm",
        "blueprint": "Sơ đồ câu hỏi: Quyền bán tài sản (Điều 34) -> Điều kiện dẫn chiếu (Điều 46) -> Định vị Khoản, Điểm.",
        "spoken": """Chúng em xin bắt đầu bằng một câu hỏi cụ thể:
"Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?"
Hệ thống có thể tìm được quy định nêu quyền tại điểm c khoản 1 Điều 34 Luật Đất đai. Nhưng người hỏi vẫn chưa có câu trả lời, vì điều này dẫn chiếu sang Điều 46 để quy định điều kiện.
Để trả lời hữu ích, hệ thống phải tìm tiếp sang Điều 46, phân biệt bán tài sản hay bán kèm quyền thuê, và chỉ rõ từng Khoản, Điểm điều kiện.
Với dữ liệu luật, tìm được đoạn văn liên quan mới là bước đầu; hệ thống còn phải giữ đúng vị trí pháp lý và liên kết được các quy định dẫn chiếu."""
    },

    # SLIDE 3
    {
        "slide": 3,
        "title": "Ba đặc thù kỹ thuật của dữ liệu văn bản pháp luật",
        "speaker": "Ngô Thế Dương",
        "blueprint": "3 khối đặc thù: 1. Cấu trúc phân cấp; 2. Mạng lưới dẫn chiếu chéo; 3. Khoảng cách ngôn ngữ.",
        "spoken": """Từ câu hỏi trên, nhóm nhận diện ba đặc thù lớn của văn bản luật:
Một là cấu trúc phân cấp: Một Điểm chỉ có nghĩa khi gắn liền với Khoản và Điều chứa nó; tách rời phân cấp sẽ làm mất chủ thể và phạm vi áp dụng.
Hai là dẫn chiếu chéo: Quy định nêu quyền nằm ở một nơi, nhưng điều kiện và ngoại lệ lại nằm ở điều luật khác.
Ba là khoảng cách ngôn ngữ: Người dân hỏi bằng từ đời thường, trong khi luật dùng thuật ngữ quy phạm chuẩn mực.
Vì vậy, bài toán đòi hỏi phải bảo toàn cấu trúc và mối quan hệ giữa các quy định."""
    },

    # SLIDE 4
    {
        "slide": 4,
        "title": "Khảo sát ba hướng tiếp cận truy hồi đối chứng",
        "speaker": "Ngô Thế Dương",
        "blueprint": "So sánh 3 hướng: Naive Vector (BGE-M3), Hybrid (BM25 + Dense + Cross-Encoder), Graph-based (LightRAG). Tiền đề chung: Chunk thô.",
        "spoken": """Nhóm lựa chọn ba kiến trúc đại diện cho ba hướng tiếp cận truy hồi khác nhau:
Một là Naive Vector RAG, đại diện cho truy hồi ngữ nghĩa thuần túy qua vector BGE-M3.
Hai là Hybrid RAG, kết hợp từ khóa BM25, vector và tái xếp hạng Cross-Encoder.
Ba là LightRAG, đại diện cho tiếp cận đồ thị, dùng LLM trích xuất thực thể và quan hệ để liên kết thông tin.
Cả ba kiến trúc đều chia sẻ tiền đề chung: Cắt đoạn theo token phi cấu trúc. Đây là đối sánh hiệu năng toàn hệ thống, chưa bóc tách riêng đóng góp của từng thành phần."""
    },

    # SLIDE 5
    {
        "slide": 5,
        "title": "Thiết kế nghiên cứu ba giai đoạn và bốn câu hỏi (RQ1 - RQ4)",
        "speaker": "Ngô Thế Dương",
        "blueprint": "Lộ trình: GĐ1 (RQ1 - Baseline thô) -> GĐ2 (RQ2 - Parser/MaxP vi mô) -> GĐ3 (RQ3 & RQ4 - Hybrid UKG & Dẫn chiếu).",
        "spoken": """Nghiên cứu được thiết kế theo ba giai đoạn tương ứng bốn câu hỏi nghiên cứu:
Giai đoạn 1 trả lời RQ1: Khảo sát ba hướng tiếp cận cơ sở trên dữ liệu cắt đoạn thô để đánh giá truy hồi và câu trả lời.
Giai đoạn 2 trả lời RQ2: Triển khai Parser kết hợp Validation và Article MaxP, đo lường tác động của cấu trúc vi mô đến trích dẫn và dung lượng ngữ cảnh.
Giai đoạn 3 trả lời RQ3 và RQ4: Phát triển kiến trúc Hybrid UKG; đánh giá khả năng xử lý ngoại lệ, điều kiện và kiểm tra giới hạn tái dựng chuỗi dẫn chiếu."""
    },

    # SLIDE 6
    {
        "slide": 6,
        "title": "Quy chuẩn kiểm chuẩn: Benchmark A và Benchmark B",
        "speaker": "Ngô Thế Dương",
        "blueprint": "Benchmark A (2.087 điều, 512 câu, Tier 1 205 câu công bằng) vs Benchmark B (Chương III Đất đai, 50 câu sâu locator, ngoại lệ, dẫn chiếu).",
        "spoken": """Nhóm xây dựng hai bộ kiểm chuẩn độc lập:
Benchmark A gồm 2.087 Điều thuộc 7 đạo luật và 512 câu hỏi. Tập Tier 1 gồm 205 câu hỏi có căn cứ nằm trọn trong 500 Điều LightRAG đã index, bảo đảm công bằng về độ phủ dữ liệu ở Giai đoạn 1. Một phần câu hỏi được diễn đạt lại để giảm trùng lặp từ vựng.
Benchmark B gồm 50 câu tại Chương III Luật Đất đai 2024 để đánh giá chuyên sâu cấp Khoản, Điểm, điều kiện, ngoại lệ và chuỗi dẫn chiếu; được nhóm kiểm tra, chưa phải thẩm định pháp lý độc lập.
Truy hồi cơ bản được đo bằng Recall@5 ở cấp Điều và MRR@5."""
    },

    # SLIDE 7
    {
        "slide": 7,
        "title": "Kết quả Giai đoạn 1: Nghịch lý truy hồi và trích dẫn (RQ1)",
        "speaker": "Lưu Thanh Lâm",
        "blueprint": "Bảng Tier 1 (N=205): Recall@5 >0.95, Hybrid MRR@5 0.9243; nhưng Citation Accuracy câu trả lời thấp: Naive 0.3259, Hybrid 0.2902, LightRAG 0.1371 (Bảng 3.3 & 3.4).",
        "spoken": """Ở Giai đoạn 1, thực nghiệm trên 205 câu Tier 1 cho thấy cả ba hệ thống đều truy hồi rất tốt: Recall@5 đều vượt 0,95 (Naive 0,9561; Hybrid và LightRAG cùng đạt 0,9659).
Về thứ bậc, Hybrid RAG xếp căn cứ liên quan sớm nhất với MRR@5 đạt 0,9243, so với 0,8589 của Naive và 0,8687 của LightRAG.
Thế nhưng, Bảng 3.4 chỉ ra một nghịch lý lớn: Độ chính xác trích dẫn Citation Accuracy trong câu trả lời lại rất thấp: Naive chỉ đạt 0,3259; Hybrid đạt 0,2902; và LightRAG chỉ đạt 0,1371.
Nghĩa là: Tìm đúng Điều luật không đồng nghĩa với việc mô hình trích dẫn đúng Khoản, Điểm hay nêu đủ căn cứ. Khoảng cách giữa truy hồi và trích dẫn này chính là động lực để nhóm tiến sang Giai đoạn 2."""
    },

    # SLIDE 8
    {
        "slide": 8,
        "title": "Giai đoạn 2: Giải pháp cấu trúc Parser, Validation và Article MaxP",
        "speaker": "Lưu Thanh Lâm",
        "blueprint": "Regex Parser (tách 12.754 phân đoạn) -> Module Validation (kiểm tra tính toàn vẹn) -> Tiền tố phân cấp -> Article MaxP.",
        "spoken": """Để khắc phục khoảng cách này, nhóm thay đổi đơn vị dữ liệu ở Giai đoạn 2.
Nhóm triển khai Structure-Aware Parser để bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô ở cấp Khoản và Điểm. Sau đó, Module Validation kiểm tra tính toàn vẹn của cây phân cấp.
Mỗi phân đoạn con được bổ sung tiền tố phân cấp để khi đứng riêng vẫn giữ trọn ngữ cảnh của Điều và Luật cha.
Để tránh việc Top-5 bị chiếm trọn bởi các phân đoạn của cùng một Điều, nhóm tích hợp giải thuật Article-level MaxP: Điểm của một Điều được lấy bằng điểm cao nhất của các phân đoạn con thuộc Điều đó.
MaxP là kỹ thuật kế thừa; đóng góp của nhóm là tích hợp nó với cấu trúc phân cấp pháp lý và đánh giá thực nghiệm."""
    },

    # SLIDE 9
    {
        "slide": 9,
        "title": "Kết quả Giai đoạn 2: Đột phá cấu hình C5 và ranh giới (RQ2)",
        "speaker": "Lưu Thanh Lâm",
        "blueprint": "So sánh C2 vs C5 (Bảng 3.5 & 3.6): Recall 0.9141 -> 0.9316, MRR 0.8129 -> 0.8602 (+4.73 đpt). Citation C5 0.9902 (504/512 đạt 1.0). Token giảm 79.9%.",
        "spoken": """Trên 512 câu hỏi Benchmark A, đối chiếu C2 Naive Dense và C5 Parser Dense cho thấy bước chuyển biến rõ nét:
Mức tăng quan sát được ở Recall@5 là từ 0,9141 lên 0,9316; và MRR@5 tăng từ 0,8129 lên 0,8602, tức tăng hơn 4,7 điểm phần trăm về khả năng ưu tiên căn cứ đúng.
Về chất lượng căn cứ, C5 đạt LLM-Judge Citation Accuracy 0,9902 trên ngữ cảnh, với 504/512 câu đạt điểm tuyệt đối 1,0; đồng thời dung lượng ngữ cảnh giảm 79,9%, từ 2.898 xuống 580 token. Điểm này đo trên ngữ cảnh, không đồng nghĩa 99% câu trả lời hoàn chỉnh đã chính xác.
C5 giải quyết tốt bài toán trong phạm vi một Điều luật. Nhưng để xử lý câu hỏi mở đầu nối từ Điều 34 sang Điều 46, nhóm phát triển UKG ở Giai đoạn 3."""
    },

    # SLIDE 10
    {
        "slide": 10,
        "title": "Kiến trúc Hybrid UKG và luồng truy hồi M10",
        "speaker": "Nguyễn Bình Minh",
        "blueprint": "UKG trên Neo4j: Physical Graph (phân cấp) + Semantic Graph (quy phạm). Luồng M10: Node mỏ neo Điều 34 -> Cạnh dẫn chiếu Điều 46 -> AUTO_FUSION.",
        "spoken": """Kiến trúc Hybrid UKG kết hợp hai tầng tri thức trên cơ sở dữ liệu Neo4j:
Tầng Physical Graph giữ cấu trúc vật lý Điều, Khoản, Điểm và quan hệ cha-con. Tầng Semantic Graph lưu trữ các thực thể quy phạm như chủ thể, điều kiện, ngoại lệ và quan hệ dẫn chiếu.
Quay lại câu hỏi mở đầu về thuê đất trả tiền hằng năm, luồng truy hồi M10 vận hành như sau:
M10 xác định điểm bắt đầu tại điểm c khoản 1 Điều 34 quy định quyền bán tài sản. Nhận diện dẫn chiếu, hệ thống mở rộng sang Điều 46 để gom các Khoản chứa điều kiện.
Chế độ AUTO_FUSION kết hợp thông tin quy phạm, cấu trúc phân cấp và bằng chứng văn bản. Thành phần Jev hỗ trợ định tuyến, có cơ chế dự phòng theo quy tắc, rồi chuyển ngữ cảnh cho GPT-4o-mini tạo câu trả lời.
Đây là luồng thiết kế kỳ vọng; năng lực thực tế phải được kiểm chứng qua Benchmark B."""
    },

    # SLIDE 11
    {
        "slide": 11,
        "title": "Kết quả Benchmark B: Đột phá trích dẫn và bài học từ ca B012 (RQ3 & RQ4)",
        "speaker": "Nguyễn Bình Minh",
        "blueprint": "Bảng Benchmark B (N=50): Legal Correctness 0.8777 vs 0.8210; Condition Coverage 0.7066 vs 0.8421 (Ca B012 0.1250 vs 1.0); Khoản Citation Recall 0.8170 vs 0.0435; Chain Exact Match 0/18.",
        "spoken": """Trên 50 câu hỏi Benchmark B, nhóm đối sánh trực diện với LightRAG và rút ra bốn kết quả trọng tâm:
Một là, về chất lượng câu trả lời, Hybrid UKG đạt Legal Correctness 0,8777 so với 0,8210 của LightRAG, tăng 5,67 điểm phần trăm.
Hai là, về trích dẫn, Citation Recall cấp Khoản của UKG đạt 0,8170 so với 0,0435; cấp Điểm đạt 0,6374 so với 0,0270, khẳng định ưu thế của việc bảo toàn cấu trúc vi mô.
Ba là, về ranh giới điều kiện, Condition Coverage của UKG chỉ đạt 0,7066, thấp hơn 0,8421 của LightRAG. Hạn chế này thể hiện rõ ở câu B012 - chính là câu hỏi mở đầu: UKG chỉ đạt 0,1250 còn LightRAG đạt 1,0000 do điều kiện tại Điều 46 bị phân tán phức tạp.
Bốn là, về chuỗi dẫn chiếu, UKG tìm được 58,67% căn cứ đích, nhưng Chain Exact Match vẫn là 0 trên 18 câu. LightRAG chưa hỗ trợ xuất đường dẫn nên ghi nhận N/A."""
    },

    # SLIDE 12
    {
        "slide": 12,
        "title": "Đóng gói câu trả lời cho bốn câu hỏi nghiên cứu (RQ1 - RQ4)",
        "speaker": "Nguyễn Bình Minh",
        "blueprint": "Tổng kết 4 RQ: RQ1 (Khoảng cách truy hồi-trích dẫn) | RQ2 (Giá trị phân đoạn vi mô) | RQ3 (Ưu thế trích dẫn/ngoại lệ, ranh giới điều kiện) | RQ4 (Ranh giới chuỗi dẫn chiếu).",
        "spoken": """Từ kết quả ba giai đoạn, nhóm tổng kết câu trả lời cho bốn RQ:
Với RQ1: Cải thiện truy hồi trên văn bản thô giúp tăng thứ bậc nhưng không giải quyết được trích dẫn; tìm đúng tài liệu chưa đồng nghĩa với tạo sinh đúng.
Với RQ2: Phân đoạn vi mô kết hợp MaxP cải thiện rõ rệt việc định vị căn cứ và tiết kiệm 79,9% ngữ cảnh trong phạm vi một Điều luật.
Với RQ3: Hybrid UKG vượt trội ở trích dẫn Khoản, Điểm và xử lý ngoại lệ, nhưng còn hạn chế khi tổng hợp các điều kiện phân tán.
Với RQ4: Hệ thống tìm được hơn một nửa căn cứ đích nhưng chưa thể tái dựng trọn vẹn chuỗi dẫn chiếu đa bước. Các giả thuyết nghiên cứu được hỗ trợ ở từng khía cạnh cụ thể, không tuyên bố thành công toàn diện."""
    },

    # SLIDE 13
    {
        "slide": 13,
        "title": "Đóng góp khoa học thực chất của đề tài",
        "speaker": "Nguyễn Bình Minh",
        "blueprint": "Kế thừa (BM25, RRF, MaxP, LightRAG) vs 4 Đóng góp của nhóm: 1. Bộ kiểm chuẩn Benchmark A & B; 2. Tích hợp Parser/Validation/MaxP; 3. Kiến trúc Hybrid UKG; 4. Hệ chỉ số đa tầng.",
        "spoken": """Nhóm xác định rõ ranh giới đóng góp của đề tài:
Các kỹ thuật như BM25, RRF, MaxP hay LightRAG là kế thừa từ cộng đồng khoa học.
Bốn đóng góp thực chất thuộc về nhóm gồm:
Một là, xây dựng bộ công cụ kiểm chuẩn và hai tập benchmark chuyên biệt cho văn bản pháp luật Việt Nam.
Hai là, triển khai và đánh giá thực nghiệm gói giải pháp bóc tách cấu trúc vi mô kết hợp Validation và Article MaxP.
Ba là, thiết kế và hiện thực hóa kiến trúc Hybrid UKG kết hợp đồ thị vật lý và đồ thị quy phạm.
Bốn là, xác lập hệ chỉ số đánh giá đa tầng, giúp phân biệt rõ hiệu quả truy hồi tài liệu với năng lực trích dẫn và tổng hợp quy phạm chính xác."""
    },

    # SLIDE 14
    {
        "slide": 14,
        "title": "Thông điệp kết luận và Hướng phát triển tương lai",
        "speaker": "Nguyễn Bình Minh",
        "blueprint": "Thông điệp: Tìm đúng Điều là chưa đủ, phải nắm bắt điều kiện & dẫn chiếu. 3 hướng mở: Cải thiện tổng hợp điều kiện, Constrained Graph Traversal, Tự động hóa hiệu lực.",
        "spoken": """Trở lại câu hỏi mở đầu: Để trả lời đúng một câu hỏi pháp lý, tìm được Điều luật là chưa đủ, mà phải nắm bắt được điều kiện, ngoại lệ và căn cứ dẫn chiếu.
Đề tài chứng minh việc bảo toàn cấu trúc dữ liệu mang lại giá trị thực chất cho bài toán trích dẫn pháp lý.
Hướng nghiên cứu tiếp theo gồm: Hoàn thiện cơ chế tổng hợp điều kiện phân tán; phát triển giải thuật duyệt đồ thị ràng buộc Constrained Graph Traversal để chinh phục chuỗi dẫn chiếu; và mở rộng kiểm chứng độc lập trên các văn bản dưới luật.
Nhóm chúng em xin trân trọng cảm ơn quý thầy cô trong Hội đồng đã chú ý lắng nghe và rất mong nhận được những ý kiến đóng góp quý báu!"""
    }
]

print("=== CHECKING CALIBRATED WORD COUNT ===")
speaker_blocks = {
    "Khối 1 (Slide 1 - 6) ": 0,
    "Khối 2 (Slide 7 - 10)": 0,
    "Khối 3 (Slide 11 - 14)": 0
}
total_words = 0

for s in slides_data:
    idx = s["slide"]
    words = len(s["spoken"].split())
    total_words += words
    if 1 <= idx <= 6:
        speaker_blocks["Khối 1 (Slide 1 - 6) "] += words
    elif 7 <= idx <= 10:
        speaker_blocks["Khối 2 (Slide 7 - 10)"] += words
    elif 11 <= idx <= 14:
        speaker_blocks["Khối 3 (Slide 11 - 14)"] += words
    print(f"Slide {s['slide']:02d}: {words:3d} words | Title: {s['title']}")

print("\n=== SUMMARY BY SPEAKER BLOCK ===")
for blk, cnt in speaker_blocks.items():
    time_sec = cnt / (130 / 60)
    print(f"{blk:<24}: {cnt:4d} words ~ {time_sec/60:.2f} mins ({time_sec:.0f}s)")

total_sec = total_words / (130 / 60)
buffer_sec = (15 * 60) - total_sec
print("-" * 55)
print(f"TOTAL WORDS: {total_words} words")
print(f"TOTAL TIME (@ 130 wpm): {total_sec/60:.2f} mins ({total_sec:.0f}s)")
print(f"SAFETY BUFFER: {buffer_sec:.0f} seconds (Goal: > 60 seconds)")
