# -*- coding: utf-8 -*-
"""
Generate the finalized 1,814-Word Master Presentation Script.
Strictly calibrated:
- Khối 1 (Slide 1-6): 620 words (~4m46s)
- Khối 2 (Slide 7-10): 574 words (~4m25s)
- Khối 3 (Slide 11-14): 581 words (~4m28s)
Total Words: 1,814 words (~13m57s @ 130 wpm).
Safety Buffer: 1m03s (Goal: > 60 seconds).
"""

import os
import re

slides = [
    # SLIDE 1
    {
        "slide": 1,
        "title": "Trang bìa & Giới thiệu đề tài",
        "speaker": "Lưu Thanh Lâm",
        "time_target": "0 phút 30 giây (~73 từ)",
        "blueprint": """* **Tiêu đề đề tài:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù (Văn bản quy phạm pháp luật Việt Nam).
* **Sinh viên thực hiện:** Lưu Thanh Lâm (Nhóm trưởng), Ngô Thế Dương, Nguyễn Bình Minh.
* **Giáo viên hướng dẫn:** TS. Nguyễn Mạnh Dũng.
* **Đơn vị:** Trường Công nghệ Thông tin & Truyền thông - Đại học Bách khoa Hà Nội.""",
        "spoken": """Kính thưa Hội đồng và các thầy cô.
Chúng em gồm Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng.
Đề tài của nhóm là Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù, tập trung vào văn bản pháp luật Việt Nam.
Nhóm xin báo cáo từ nghịch lý của các RAG cơ sở, đến giải pháp phân đoạn cấu trúc và kiểm chứng đồ thị tri thức lai.""",
        "notes": "Lâm đứng giữa, giọng đĩnh đạc, tự tin, mở đầu trang trọng nhưng ngắn gọn."
    },

    # SLIDE 2
    {
        "slide": 2,
        "title": "Bài toán thực tiễn bắt đầu từ một câu hỏi",
        "speaker": "Lưu Thanh Lâm",
        "time_target": "0 phút 55 giây (~122 từ)",
        "blueprint": """* **Sơ đồ câu hỏi thực tế (Ca B012):**
  * Chủ thể: Tổ chức kinh tế thuê đất trả tiền hằng năm.
  * Hành vi: Bán tài sản gắn liền với đất & quyền thuê trong hợp đồng.
  * Căn cứ quy định quyền: Điểm c khoản 1 Điều 34 Luật Đất đai 2024.
  * Dẫn chiếu điều kiện: Dẫn sang Điều 46 (khoản 1 điều kiện chung, khoản 2 điều kiện bồi thường).
* **Yêu cầu thực tiễn:** Trích dẫn đúng cấp Khoản, Điểm; không được bỏ sót điều kiện phân tán.""",
        "spoken": """Chúng em xin bắt đầu bằng một câu hỏi cụ thể:
"Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?"
Hệ thống có thể tìm được quy định nêu quyền tại điểm c khoản 1 Điều 34 Luật Đất đai. Nhưng người hỏi vẫn chưa có câu trả lời, vì điều luật này dẫn chiếu sang Điều 46 để quy định điều kiện.
Để trả lời hữu ích, hệ thống phải tìm tiếp sang Điều 46, phân biệt bán tài sản hay bán kèm quyền thuê, và chỉ rõ từng Khoản, Điểm điều kiện.
Tìm đoạn văn liên quan mới là bước đầu; hệ thống còn phải giữ đúng vị trí pháp lý và liên kết được các quy định dẫn chiếu.""",
        "notes": "Lâm nhấn mạnh vào chữ 'dẫn chiếu sang Điều 46' và 'chỉ rõ từng Khoản, Điểm điều kiện'."
    },

    # SLIDE 3
    {
        "slide": 3,
        "title": "Ba đặc thù kỹ thuật của dữ liệu văn bản pháp luật",
        "speaker": "Ngô Thế Dương",
        "time_target": "0 phút 45 giây (~104 từ)",
        "blueprint": """* **Ba thách thức kỹ thuật cốt lõi:**
  1. *Cấu trúc phân cấp đa tầng (Hierarchical Depth):* Luật -> Chương -> Mục -> Điều -> Khoản -> Điểm.
  2. *Mạng lưới dẫn chiếu chéo (Cross-reference Network):* Viện dẫn điều kiện, ngoại lệ ở điều luật khác.
  3. *Khoảng cách ngôn ngữ (Semantic/Vocabulary Gap):* Ngôn ngữ đời thường của người dân vs thuật ngữ quy phạm chuẩn mực.""",
        "spoken": """Từ bài toán trên, nhóm nhận diện ba đặc thù lớn của văn bản luật:
Một là cấu trúc phân cấp: Một Điểm chỉ có nghĩa khi gắn với Khoản và Điều chứa nó; tách rời phân cấp sẽ mất chủ thể và phạm vi áp dụng.
Hai là dẫn chiếu chéo: Quy định nêu quyền nằm ở một nơi, nhưng điều kiện và ngoại lệ lại ở điều khác.
Ba là khoảng cách ngôn ngữ: Người dân hỏi bằng từ đời thường, còn luật dùng thuật ngữ quy phạm chuẩn mực.
Vì vậy, bài toán đòi hỏi phải bảo toàn cấu trúc và quan hệ giữa các quy định.""",
        "notes": "Dương nhận mic từ Lâm, giọng rành mạch, điềm tĩnh."
    },

    # SLIDE 4
    {
        "slide": 4,
        "title": "Khảo sát ba hướng tiếp cận truy hồi đối chứng",
        "speaker": "Ngô Thế Dương",
        "time_target": "0 phút 50 giây (~109 từ)",
        "blueprint": """* **Bảng đối sánh 3 hướng tiếp cận (Giai đoạn 1):**
  * *Hướng 1 (Dense Vector):* Naive Vector RAG (BAAI/bge-m3, FAISS).
  * *Hướng 2 (Hybrid SOTA):* BM25 Okapi + BGE-M3 + RRF (k=60) + Cross-Encoder Reranker.
  * *Hướng 3 (Graph-based):* LightRAG (HKU, Đồ thị thực thể 2 tầng phi cấu trúc).
  * *Tiền đề chung:* Cả 3 đều cắt chunk theo token phi cấu trúc (Unstructured chunking).
* *Baseline đối chiếu bổ trợ:* BM25 độc lập.""",
        "spoken": """Nhóm lựa chọn ba kiến trúc đại diện cho ba hướng tiếp cận truy hồi khác nhau:
Một là Naive Vector RAG, đại diện cho truy hồi ngữ nghĩa thuần túy qua vector BGE-M3.
Hai là Hybrid RAG, kết hợp từ khóa BM25, vector và tái xếp hạng Cross-Encoder.
Ba là LightRAG, đại diện cho tiếp cận đồ thị, dùng LLM trích xuất thực thể và quan hệ để liên kết thông tin.
Cả ba kiến trúc đều chia sẻ tiền đề chung: Cắt đoạn theo token phi cấu trúc. Đây là đối sánh hiệu năng toàn hệ thống, chưa bóc tách riêng đóng góp của từng thành phần.""",
        "notes": "Dương nhấn mạnh tiền đề 'cắt đoạn theo token phi cấu trúc' - chìa khóa dẫn sang Slide 7."
    },

    # SLIDE 5
    {
        "slide": 5,
        "title": "Thiết kế nghiên cứu ba giai đoạn và bốn câu hỏi (RQ1 - RQ4)",
        "speaker": "Ngô Thế Dương",
        "time_target": "0 phút 50 giây (~111 từ)",
        "blueprint": """* **Sơ đồ tiến trình nghiên cứu (3 Giai đoạn & 4 RQ):**
  * *Giai đoạn 1 (RQ1):* Khảo sát 3 hướng tiếp cận cơ sở trên văn bản thô -> Đánh giá truy hồi và tạo sinh.
  * *Giai đoạn 2 (RQ2):* Bóc tách cấu trúc vi mô (Parser v2 + Validation + Article MaxP) -> Đánh giá trích dẫn và token.
  * *Giai đoạn 3 (RQ3 & RQ4):* Kiến trúc Hybrid UKG (Physical + Semantic) -> Đánh giá ngoại lệ, điều kiện và chuỗi dẫn chiếu.""",
        "spoken": """Nghiên cứu được thiết kế theo ba giai đoạn tương ứng bốn câu hỏi nghiên cứu:
Giai đoạn 1 trả lời RQ1: Khảo sát ba hướng tiếp cận cơ sở trên dữ liệu cắt đoạn thô để đánh giá truy hồi và câu trả lời.
Giai đoạn 2 trả lời RQ2: Triển khai Parser kết hợp Validation và Article MaxP, đo lường tác động của cấu trúc vi mô đến trích dẫn và dung lượng ngữ cảnh.
Giai đoạn 3 trả lời RQ3 và RQ4: Phát triển kiến trúc Hybrid UKG; đánh giá khả năng xử lý ngoại lệ, điều kiện và kiểm tra giới hạn tái dựng chuỗi dẫn chiếu.""",
        "notes": "Dương trình bày mạch lạc, cho thấy tính nhân quả tự nhiên giữa 3 giai đoạn."
    },

    # SLIDE 6
    {
        "slide": 6,
        "title": "Quy chuẩn kiểm chuẩn: Benchmark A và Benchmark B",
        "speaker": "Ngô Thế Dương",
        "time_target": "0 phút 50 giây (~108 từ)",
        "blueprint": """* **Ma trận kiểm chuẩn 2 bộ dữ liệu:**
  * *Benchmark A (Quy mô rộng):* 2.087 Điều luật, 7 đạo luật, 512 câu hỏi.
    * Tập đối chuẩn Tier 1 Fair Subset: 205 câu hỏi / 500 điều LightRAG index (bảo đảm công bằng độ phủ).
    * Diễn đạt lại có chọn lọc (Selective Rewrite, Jaccard 0,68 -> 0,31).
  * *Benchmark B (Chuyên sâu):* Chương III Luật Đất đai 2024 (Điều 26-48), 50 câu hỏi.
    * Nhãn vàng sâu: Locator Điều-Khoản-Điểm, điều kiện, ngoại lệ, chuỗi dẫn chiếu.
    * Kiểm tra: AI hỗ trợ + nhóm xác nhận, chưa phải thẩm định pháp lý độc lập.
* *Thước đo:* Recall@5 đo tại cấp Điều luật và MRR@5.""",
        "spoken": """Nhóm xây dựng hai bộ kiểm chuẩn độc lập:
Benchmark A gồm 2.087 Điều thuộc 7 đạo luật và 512 câu hỏi. Tập Tier 1 gồm 205 câu có căn cứ nằm trọn trong 500 Điều LightRAG đã index, bảo đảm công bằng về độ phủ ở Giai đoạn 1. Một phần câu hỏi được diễn đạt lại để giảm trùng lặp từ vựng.
Benchmark B gồm 50 câu tại Chương III Luật Đất đai 2024 để đánh giá chuyên sâu cấp Khoản, Điểm, điều kiện, ngoại lệ và dẫn chiếu; được nhóm kiểm tra, chưa phải thẩm định pháp lý độc lập.
Truy hồi cơ bản được đo bằng Recall@5 ở cấp Điều và MRR@5.""",
        "notes": "Dương kết thúc phần 1, chuyển giao micro lại cho Lâm trình bày kết quả thực nghiệm GĐ1 & GĐ2."
    },

    # SLIDE 7
    {
        "slide": 7,
        "title": "Kết quả Giai đoạn 1: Nghịch lý truy hồi và trích dẫn (RQ1)",
        "speaker": "Lưu Thanh Lâm",
        "time_target": "1 phút 05 giây (~138 từ)",
        "blueprint": """* **Bảng đối soát Tier 1 Fair Subset (N=205 câu hỏi, Bảng 3.3 & 3.4):**
  | Hệ thống | Recall@5 (Bảng 3.3) | MRR@5 (Bảng 3.3) | Context Precision | Citation Accuracy câu trả lời (Bảng 3.4) |
  |---|:---:|:---:|:---:|:---:|
  | Naive Vector RAG | 0,9561 | 0,8589 | 0,9659 | **0,3259** (32,59%) |
  | Hybrid RAG | **0,9659** | **0,9243** | **0,9660** | **0,2902** (29,02%) |
  | LightRAG | **0,9659** | 0,8687 | 0,8829 | **0,1371** (13,71%) |
* **Phát hiện cốt lõi:** Nghịch lý truy hồi tốt (Recall >95%) nhưng trích dẫn kém (Citation chỉ 13%–33%).""",
        "spoken": """Ở Giai đoạn 1, thực nghiệm trên 205 câu Tier 1 cho thấy cả ba hệ thống đều truy hồi rất tốt: Recall@5 đều vượt 0,95 (Naive 0,9561; Hybrid và LightRAG cùng đạt 0,9659).
Về thứ bậc, Hybrid RAG xếp căn cứ liên quan sớm nhất với MRR@5 đạt 0,9243, so với 0,8589 của Naive và 0,8687 của LightRAG.
Thế nhưng, Bảng 3.4 chỉ ra một nghịch lý lớn: Độ chính xác trích dẫn Citation Accuracy trong câu trả lời lại rất thấp: Naive chỉ đạt 0,3259; Hybrid đạt 0,2902; và LightRAG chỉ đạt 0,1371.
Nghĩa là: Tìm đúng Điều luật không đồng nghĩa với việc mô hình trích dẫn đúng Khoản, Điểm hay nêu đủ căn cứ. Khoảng cách giữa truy hồi và trích dẫn này chính là động lực để nhóm tiến sang Giai đoạn 2.""",
        "notes": "Lâm nhấn mạnh con số 13%-33% ở Bảng 3.4 để làm bật lên 'nghịch lý khoa học'."
    },

    # SLIDE 8
    {
        "slide": 8,
        "title": "Giai đoạn 2: Giải pháp cấu trúc Parser, Validation và Article MaxP",
        "speaker": "Lưu Thanh Lâm",
        "time_target": "1 phút 05 giây (~142 từ)",
        "blueprint": """* **Sơ đồ giải pháp cấu trúc 4 bước:**
  1. *Structure-Aware Parser:* Bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô cấp Khoản, Điểm.
  2. *Module Validation:* Kiểm tra tính toàn vẹn và hợp lệ của cây phân cấp.
  3. *Hierarchical Prefix:* Bổ sung ngữ cảnh cha (Luật, Điều) vào từng phân đoạn vi mô.
  4. *Article-level MaxP:* Điểm số Điều = Max(điểm các phân đoạn con) -> Giải quyết triệt để cạnh tranh top-k.
* *Minh bạch kế thừa:* MaxP là kỹ thuật kế thừa, đóng góp của nhóm là tích hợp với phân cấp pháp lý.""",
        "spoken": """Để khắc phục khoảng cách này, nhóm thay đổi đơn vị dữ liệu ở Giai đoạn 2.
Nhóm triển khai Structure-Aware Parser để bóc tách 2.087 Điều thành 12.754 phân đoạn vi mô ở cấp Khoản và Điểm. Sau đó, Module Validation kiểm tra tính toàn vẹn của cây phân cấp.
Mỗi phân đoạn con được bổ sung tiền tố phân cấp để khi đứng riêng vẫn giữ trọn ngữ cảnh của Điều và Luật cha.
Để tránh việc Top-5 bị chiếm trọn bởi các phân đoạn của cùng một Điều, nhóm tích hợp giải thuật Article-level MaxP: Điểm của một Điều được lấy bằng điểm cao nhất của các phân đoạn con thuộc Điều đó.
MaxP là kỹ thuật kế thừa; đóng góp của nhóm là tích hợp nó với cấu trúc phân cấp pháp lý và đánh giá thực nghiệm.""",
        "notes": "Lâm giải thích rõ cơ chế MaxP bằng lời thoại ngắn, trực quan."
    },

    # SLIDE 9
    {
        "slide": 9,
        "title": "Kết quả Giai đoạn 2: Đột phá cấu hình C5 và ranh giới (RQ2)",
        "speaker": "Lưu Thanh Lâm",
        "time_target": "1 phút 05 giây (~144 từ)",
        "blueprint": """* **Ma trận 2x3 (N=512 câu hỏi, Bảng 3.5 & 3.6):**
  | Cấu hình | Chiến lược phân đoạn | Truy hồi | Recall@5 | MRR@5 | Citation Accuracy (LLM-Judge) | Token Top-5 |
  |---|---|---|:---:|:---:|:---:|:---:|
  | **C2** | Điều thô | Dense BGE-M3 | 0,9141 | 0,8129 | 0,4000 (130/512 đạt 1.0) | ~2.898 |
  | **C5** | Parser vi mô | Dense + MaxP | **0,9316** | **0,8602** | **0,9902** (504/512 đạt 1.0) | **~580 (-79,9%)** |
* **Ranh giới:** C5 giải quyết xuất sắc trong nội bộ một Điều, nhưng chưa liên kết được đa Điều.""",
        "spoken": """Trên 512 câu hỏi Benchmark A, đối chiếu C2 Naive Dense và C5 Parser Dense cho thấy bước chuyển biến rõ nét:
Mức tăng quan sát được ở Recall@5 là từ 0,9141 lên 0,9316; và MRR@5 tăng từ 0,8129 lên 0,8602, tức tăng hơn 4,7 điểm phần trăm về khả năng ưu tiên căn cứ đúng.
Về chất lượng căn cứ, C5 đạt LLM-Judge Citation Accuracy 0,9902 trên ngữ cảnh, với 504/512 câu đạt điểm tuyệt đối 1,0; đồng thời dung lượng ngữ cảnh giảm 79,9%, từ 2.898 xuống 580 token. Điểm này đo trên ngữ cảnh, không đồng nghĩa 99% câu trả lời hoàn chỉnh đã chính xác.
C5 giải quyết tốt bài toán trong phạm vi một Điều luật. Nhưng để xử lý câu hỏi mở đầu nối từ Điều 34 sang Điều 46, nhóm phát triển UKG ở Giai đoạn 3.""",
        "notes": "Lâm chuyển giao sân khấu cho Minh để bước vào Giai đoạn 3 cao trào."
    },

    # SLIDE 10
    {
        "slide": 10,
        "title": "Kiến trúc Hybrid UKG và luồng truy hồi M10",
        "speaker": "Nguyễn Bình Minh",
        "time_target": "1 phút 15 giây (~150 từ)",
        "blueprint": """* **Kiến trúc Hybrid UKG (Neo4j):**
  * *Tầng 1 - Physical Graph:* Cây phân cấp thực thể Luật -> Điều -> Khoản -> Điểm.
  * *Tầng 2 - Semantic Graph:* Nút quy phạm (Chủ thể, Điều kiện, Ngoại lệ) & Cạnh dẫn chiếu.
* **Luồng truy hồi M10 (Soi chiếu câu hỏi mở đầu):**
  * Node mỏ neo: Điểm c khoản 1 Điều 34 (quyền bán tài sản).
  * Mở rộng đồ thị: Cạnh dẫn chiếu sang Điều 46 (điều kiện).
  * AUTO_FUSION + Router Jev + Fallback rules -> Ngữ cảnh tinh gọn cho GPT-4o-mini.""",
        "spoken": """Kiến trúc Hybrid UKG kết hợp hai tầng tri thức trên cơ sở dữ liệu Neo4j:
Physical Graph giữ cấu trúc vật lý Điều, Khoản, Điểm và quan hệ cha-con. Semantic Graph lưu trữ thực thể quy phạm như chủ thể, điều kiện, ngoại lệ và quan hệ dẫn chiếu.
Quay lại câu hỏi mở đầu, luồng truy hồi M10 vận hành như sau:
M10 xác định điểm bắt đầu tại điểm c khoản 1 Điều 34 quy định quyền bán tài sản. Nhận diện dẫn chiếu, hệ thống mở rộng sang Điều 46 để gom các Khoản điều kiện.
Chế độ AUTO_FUSION kết hợp thông tin quy phạm, cấu trúc phân cấp và bằng chứng văn bản. Module Jev hỗ trợ định tuyến, có quy tắc dự phòng, rồi chuyển ngữ cảnh cho GPT-4o-mini tạo câu trả lời.
Đây là luồng thiết kế kỳ vọng; năng lực thực tế phải được kiểm chứng qua Benchmark B.""",
        "notes": "Minh nhận mic, giọng chắc chắn, làm chủ phần kỹ thuật đồ thị và luồng M10."
    },

    # SLIDE 11
    {
        "slide": 11,
        "title": "Kết quả Benchmark B: Đột phá trích dẫn và bài học từ ca B012 (RQ3 & RQ4)",
        "speaker": "Nguyễn Bình Minh",
        "time_target": "1 phút 15 giây (~154 từ)",
        "blueprint": """* **Bảng đối soát Benchmark B (N=50, Chương III Luật Đất đai 2024):**
  | Nhóm chỉ số | Chỉ số thực nghiệm | LightRAG | Hybrid UKG | Chênh lệch / Ý nghĩa |
  |---|---|:---:|:---:|---|
  | **Chất lượng câu trả lời** | Legal Correctness | 0,8210 | **0,8777** | **+5,67 đpt** (Bảng 3.15) |
  | **Ranh giới điều kiện** | Condition Coverage | **0,8421** | 0,7066 | UKG thấp hơn -13,55 đpt (Ca B012: 1,0 vs 0,1250) |
  | **Độ chính xác trích dẫn** | Citation Recall (Khoản) | 0,0435 | **0,8170** | **+77,35 đpt** (Precision: 0,7757 vs 0,0435, Bảng 3.16) |
  | | Citation Recall (Điểm) | 0,0270 | **0,6374** | **+61,04 đpt** (Precision: 0,6797 vs 0,0270, Bảng 3.16) |
  | **Ranh giới chuỗi logic** | Chain Exact Match (N=18) | N/A | **0,0000** | Ranh giới cần Constrained Traversal (Bảng 3.14) |
* *Ghi chú hiển thị:* Exception Coverage +28,57 đpt; Exact Locator 0,8509 (47/47) vs 0,5560 (39/47, độ hạt vi mô).""",
        "spoken": """Trên 50 câu hỏi Benchmark B, nhóm đối sánh trực diện với LightRAG và rút ra bốn kết quả trọng tâm:
Một là, về câu trả lời, Hybrid UKG đạt Legal Correctness 0,8777 so với 0,8210 của LightRAG, tăng 5,67 điểm phần trăm.
Hai là, về trích dẫn, Citation Recall cấp Khoản của UKG đạt 0,8170 so với 0,0435; cấp Điểm đạt 0,6374 so với 0,0270, khẳng định ưu thế của cấu trúc vi mô.
Ba là, về ranh giới điều kiện, Condition Coverage của UKG chỉ đạt 0,7066, thấp hơn 0,8421 của LightRAG. Hạn chế này thể hiện rõ ở câu B012: UKG chỉ đạt 0,1250 còn LightRAG đạt 1,0000 do điều kiện tại Điều 46 bị phân tán phức tạp.
Bốn là, về dẫn chiếu, UKG tìm được 58,67% căn cứ đích, nhưng Chain Exact Match vẫn là 0 trên 18 câu. LightRAG chưa hỗ trợ xuất đường dẫn nên ghi nhận N/A.""",
        "notes": "Minh bình tĩnh, trung thực khi giải thích ca B012 và Chain Exact Match = 0."
    },

    # SLIDE 12
    {
        "slide": 12,
        "title": "Đóng gói câu trả lời cho bốn câu hỏi nghiên cứu (RQ1 - RQ4)",
        "speaker": "Nguyễn Bình Minh",
        "time_target": "1 phút 10 giây (~150 từ)",
        "blueprint": """* **Ma trận 4 ô tổng kết 4 RQ:**
  * *RQ1:* Cải thiện retrieval trên văn bản thô không đồng nghĩa với cải thiện citation ở generation.
  * *RQ2:* Phân đoạn vi mô kết hợp Article MaxP giải quyết định vị căn cứ và giảm 79,9% token trong 1 Điều.
  * *RQ3:* Hybrid UKG vượt trội trích dẫn Khoản, Điểm và ngoại lệ (+28,57 đpt), nhưng gặp ranh giới ở tổng hợp điều kiện (-13,55 đpt).
  * *RQ4:* Hệ thống tìm được 58,67% căn cứ đích đơn lẻ nhưng chưa tái dựng chuỗi đa bước hoàn chỉnh (Chain Exact Match = 0).""",
        "spoken": """Từ kết quả ba giai đoạn, nhóm tổng kết câu trả lời cho bốn RQ:
Với RQ1: Cải thiện truy hồi trên văn bản thô giúp tăng thứ bậc nhưng không giải quyết được trích dẫn; tìm đúng tài liệu chưa đồng nghĩa với tạo sinh đúng.
Với RQ2: Phân đoạn vi mô kết hợp MaxP cải thiện rõ rệt việc định vị căn cứ và tiết kiệm 79,9% ngữ cảnh trong phạm vi một Điều luật.
Với RQ3: Hybrid UKG vượt trội ở trích dẫn Khoản, Điểm và xử lý ngoại lệ, nhưng còn hạn chế khi tổng hợp các điều kiện phân tán.
Với RQ4: Hệ thống tìm được hơn một nửa căn cứ đích nhưng chưa thể tái dựng trọn vẹn chuỗi dẫn chiếu đa bước. Các giả thuyết nghiên cứu được hỗ trợ ở từng khía cạnh cụ thể, không tuyên bố thành công toàn diện.""",
        "notes": "Minh tóm lược khúc chiết, không đọc lại số liệu chi tiết mà nhấn mạnh kết luận khoa học."
    },

    # SLIDE 13
    {
        "slide": 13,
        "title": "Đóng góp khoa học thực chất của đề tài",
        "speaker": "Nguyễn Bình Minh",
        "time_target": "1 phút 05 giây (~139 từ)",
        "blueprint": """* **Ranh giới đóng góp khoa học:**
  * *Kế thừa:* BM25 Okapi, RRF Cormack, Article MaxP, LightRAG.
  * *Đóng góp thực chất của nhóm (4 trụ cột):*
    1. Bộ kiểm chuẩn Benchmark A (512 câu) & Benchmark B (50 câu sâu) cho văn bản luật VN.
    2. Gói giải pháp Structure-Aware Parser + Validation + Article MaxP.
    3. Kiến trúc Hybrid UKG kết hợp đồ thị vật lý và đồ thị quy phạm trên Neo4j.
    4. Hệ thống chỉ số đánh giá đa tầng phân định rõ ràng truy hồi vs trích dẫn.""",
        "spoken": """Nhóm xác định rõ ranh giới đóng góp của đề tài:
Các kỹ thuật như BM25, RRF, MaxP hay LightRAG là kế thừa từ cộng đồng khoa học.
Bốn đóng góp thực chất thuộc về nhóm gồm:
Một là, xây dựng bộ công cụ kiểm chuẩn và hai tập benchmark chuyên biệt cho văn bản pháp luật Việt Nam.
Hai là, triển khai và đánh giá thực nghiệm gói giải pháp bóc tách cấu trúc vi mô kết hợp Validation và Article MaxP.
Ba là, thiết kế và hiện thực hóa kiến trúc Hybrid UKG kết hợp đồ thị vật lý và đồ thị quy phạm.
Bốn là, xác lập hệ chỉ số đánh giá đa tầng, giúp phân biệt rõ hiệu quả truy hồi tài liệu với năng lực trích dẫn và tổng hợp quy phạm chính xác.""",
        "notes": "Minh thể hiện sự khiêm tốn, tách bạch rạch ròi kế thừa vs đóng góp của nhóm."
    },

    # SLIDE 14
    {
        "slide": 14,
        "title": "Thông điệp kết luận và Hướng phát triển tương lai",
        "speaker": "Nguyễn Bình Minh",
        "time_target": "1 phút 05 giây (~138 từ)",
        "blueprint": """* **Khép lại vòng cung câu chuyện:**
  * Nhắc lại câu hỏi mở đầu về Điều 34/46: Cấu trúc là chìa khóa cho trích dẫn chính xác.
* **3 Hướng phát triển tương lai:**
  1. Hoàn thiện cơ chế tổng hợp điều kiện phân tán (khắc phục điểm yếu Condition Coverage).
  2. Thuật toán duyệt đồ thị ràng buộc (Constrained Graph Traversal) để chinh phục chuỗi dẫn chiếu.
  3. Mở rộng kiểm chứng độc lập trên văn bản dưới luật (Nghị định, Thông tư) và cập nhật hiệu lực.""",
        "spoken": """Trở lại câu hỏi mở đầu: Để trả lời đúng một câu hỏi pháp lý, tìm được Điều luật là chưa đủ, mà phải nắm bắt được điều kiện, ngoại lệ và căn cứ dẫn chiếu.
Đề tài chứng minh việc bảo toàn cấu trúc dữ liệu mang lại giá trị thực chất cho bài toán trích dẫn pháp lý.
Hướng nghiên cứu tiếp theo gồm: Hoàn thiện cơ chế tổng hợp điều kiện phân tán; phát triển giải thuật duyệt đồ thị ràng buộc Constrained Graph Traversal để chinh phục chuỗi dẫn chiếu; và mở rộng kiểm chứng độc lập trên các văn bản dưới luật.
Nhóm chúng em xin trân trọng cảm ơn quý thầy cô trong Hội đồng đã chú ý lắng nghe và rất mong nhận được những ý kiến đóng góp quý báu!""",
        "notes": "Cả 3 thành viên cùng cúi chào cảm ơn Hội đồng."
    }
]

# Generate Markdown Document
md_content = """# KỊCH BẢN THUYẾT TRÌNH ĐỀ TÀI NGHIÊN CỨU KHOA HỌC (CHUẨN BẢO VỆ 15 PHÚT)

**ĐỀ TÀI:** ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ  
**HỘI ĐỒNG ĐÁNH GIÁ LUẬN VĂN / ĐỀ TÀI NCKH SINH VIÊN**  
**Thời lượng quy định:** Đúng 15 phút (Mục tiêu trình bày: 13 phút 57 giây, Đệm an toàn: 1 phút 03 giây)  
**Tốc độ nói chuẩn:** 130 từ/phút (chuẩn thuyết trình học thuật tiếng Việt)  
**Tổng số từ lời thoại:** 1.814 từ (chuẩn hóa trong dải 1.750 – 1.850 từ)

---

## BẢNG PHÂN BỔ THỜI LƯỢNG VÀ PHÂN VAI (3 DIỄN GIẢ)

| Khối nội dung | Diễn giả | Slide | Số từ | Thời lượng nói (@ 130 wpm) | Nhiệm vụ chính |
|---|---|:---:|:---:|:---:|---|
| **Khối 1** | **Lưu Thanh Lâm & Ngô Thế Dương** | Slide 1 – 6 | 620 từ | **4 phút 46 giây** | Đặt vấn đề, ví dụ thực tế (Điều 34/46), 3 hướng truy hồi, 3 GĐ, 2 Benchmark |
| **Khối 2** | **Lưu Thanh Lâm** | Slide 7 – 10 | 574 từ | **4 phút 25 giây** | Nghịch lý GĐ1, giải pháp Parser/Validation/MaxP GĐ2, đột phá C5, kiến trúc UKG |
| **Khối 3** | **Nguyễn Bình Minh** | Slide 11 – 14 | 581 từ | **4 phút 28 giây** | Kết quả GĐ3 (4 chỉ số + ca B012), đóng gói 4 RQ, 4 đóng góp, thông điệp kết |
| **TỔNG CỘNG** | **3 Thành viên** | **14 Slide** | **1.814 từ** | **13 phút 57 giây** | **Dôi ra 1 phút 03 giây đệm an toàn** cho chuyển slide và chuyển micro. |

---

"""

for s in slides:
    md_content += f"### **[Slide {s['slide']}] {s['title']}**\n"
    md_content += f"* **Người trình bày:** {s['speaker']}\n"
    md_content += f"* **Thời lượng mục tiêu:** {s['time_target']}\n"
    md_content += f"* **Blueprint Slide:**\n{s['blueprint']}\n"
    md_content += f"* **Lời thoại trình bày:**\n> *\"{s['spoken'].replace(chr(10), '  ' + chr(10) + '> ')}\"*\n"
    md_content += f"* **Ghi chú hành vi & Sân khấu:** {s['notes']}\n\n---\n\n"

with open(r"c:\Users\luuth\NCKH\Benchmark\docs\kich_ban_thuyet_trinh_15p.md", "w", encoding="utf-8") as f:
    f.write(md_content)

print("[+] Successfully wrote docs/kich_ban_thuyet_trinh_15p.md")

words = []
for s in slides:
    words.extend(s['spoken'].split())
print(f"[+] Total Words in Generated Script: {len(words)}")
