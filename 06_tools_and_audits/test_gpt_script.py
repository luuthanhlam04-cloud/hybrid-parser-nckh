# -*- coding: utf-8 -*-
slides = [
    # Slide 1
    """Kính thưa Hội đồng, kính thưa các thầy cô và các bạn.
Chúng em là nhóm nghiên cứu gồm Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng.
Đề tài của nhóm là "Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù", với phạm vi thực nghiệm tập trung vào dữ liệu văn bản quy phạm pháp luật Việt Nam.
Trong phần trình bày hôm nay, nhóm sẽ đi từ những hạn chế của các kiến trúc RAG cơ sở, đến việc tổ chức lại dữ liệu theo cấu trúc pháp lý và cuối cùng là đánh giá một kiến trúc kết hợp cấu trúc với đồ thị tri thức.""",

    # Slide 2
    """Để bắt đầu, nhóm xin đưa ra một câu hỏi pháp lý cụ thể:
Một tổ chức kinh tế được Nhà nước cho thuê đất và trả tiền thuê đất hằng năm có được bán tài sản gắn liền với đất hay không? Và trong trường hợp bán kèm quyền thuê trong hợp đồng thuê đất thì cần đáp ứng những điều kiện gì?
Đây không đơn thuần là câu hỏi tìm kiếm một điều luật chứa từ khóa liên quan.
Để trả lời đầy đủ, hệ thống cần xác định đúng quyền của chủ thể, tìm được quy định về điều kiện bán tài sản, đồng thời phân biệt trường hợp bán tài sản với trường hợp bán cả tài sản và quyền thuê trong hợp đồng.
Trong Luật Đất đai, câu hỏi này liên quan đến điểm c khoản 1 Điều 34 và các điều kiện được dẫn chiếu tại Điều 46.
Đây là ví dụ cho thấy với dữ liệu pháp luật, việc tìm được một đoạn văn bản có vẻ liên quan chưa đủ. Hệ thống còn phải xác định được vị trí pháp lý, quan hệ giữa các quy định và tổng hợp đúng các điều kiện áp dụng.""",

    # Slide 3
    """Từ bài toán trên, nhóm xác định ba đặc thù chính của dữ liệu pháp luật.
Thứ nhất là cấu trúc phân cấp. Văn bản pháp luật được tổ chức theo nhiều cấp như chương, mục, điều, khoản và điểm. Một khoản hoặc điểm có thể không đủ ý nghĩa nếu bị tách khỏi điều luật cấp cha.
Thứ hai là quan hệ dẫn chiếu chéo. Một quy định có thể viện dẫn đến điều luật khác để bổ sung điều kiện, ngoại lệ hoặc phạm vi áp dụng. Vì vậy, hệ thống không chỉ cần tìm đoạn chứa câu trả lời trực tiếp mà còn cần nhận diện những căn cứ liên quan.
Thứ ba là khoảng cách ngôn ngữ. Người dùng thường đặt câu hỏi bằng ngôn ngữ tự nhiên, trong khi văn bản pháp luật sử dụng thuật ngữ và cách diễn đạt mang tính quy phạm. Hai cách diễn đạt có thể khác nhau đáng kể dù cùng nói về một vấn đề.
Ba đặc điểm này khiến bài toán RAG trên dữ liệu pháp luật không chỉ là tìm kiếm đoạn văn tương đồng, mà còn là bảo toàn cấu trúc và quan hệ giữa các đơn vị thông tin.""",

    # Slide 4
    """Để khảo sát vấn đề, nhóm lựa chọn ba kiến trúc RAG cơ sở đại diện cho ba hướng truy hồi khác nhau.
Thứ nhất là Naive Vector RAG, sử dụng embedding và tìm kiếm ngữ nghĩa để truy xuất những đơn vị văn bản gần với câu hỏi.
Thứ hai là Hybrid RAG, kết hợp truy hồi từ vựng BM25 với truy hồi ngữ nghĩa, sau đó dung hợp thứ hạng bằng RRF và tái xếp hạng bằng Cross-Encoder.
Thứ ba là LightRAG, một hướng tiếp cận dựa trên đồ thị, sử dụng thông tin thực thể và quan hệ để hỗ trợ tổ chức và truy hồi tri thức.
Việc lựa chọn ba kiến trúc này nhằm đối chiếu các hướng truy hồi ngữ nghĩa, truy hồi lai và truy hồi dựa trên đồ thị. Đây là phạm vi đối chứng của nghiên cứu, không phải một bảng xếp hạng toàn diện cho mọi kiến trúc RAG hiện có.
Ngoài ra, nhóm cũng có sử dụng BM25 độc lập như một baseline từ vựng hỗ trợ đối chiếu.""",

    # Slide 5
    """Nghiên cứu được tổ chức thành ba giai đoạn có mục tiêu riêng.
Giai đoạn 1, nhóm triển khai ba kiến trúc RAG cơ sở để đánh giá khả năng truy hồi và chất lượng câu trả lời trên dữ liệu pháp luật. Giai đoạn này tập trung trả lời RQ1: các kiến trúc khác nhau như thế nào về hiệu quả truy hồi và chất lượng câu trả lời?
Giai đoạn 2, nhóm bổ sung Regex Parser và Validation để phân đoạn văn bản theo cấu trúc Điều - Khoản - Điểm, kết hợp thông tin phân cấp và cơ chế Article-level MaxP. Mục tiêu là khảo sát tác động của cách tổ chức dữ liệu đối với truy hồi, trích dẫn và dung lượng ngữ cảnh. Đây là RQ2.
Giai đoạn 3, nhóm phát triển Hybrid Parser/UKG, kết hợp cấu trúc vật lý của văn bản với thông tin ngữ nghĩa trong đồ thị tri thức. Giai đoạn này tập trung vào khả năng xử lý căn cứ pháp lý chi tiết, điều kiện, ngoại lệ, chủ thể và dẫn chiếu chéo, tương ứng với RQ3 và RQ4.
Như vậy, ba giai đoạn lần lượt khảo sát baseline, tác động của cấu trúc phân đoạn và khả năng tích hợp cấu trúc với quan hệ tri thức.""",

    # Slide 6
    """Nhóm sử dụng hai bộ dữ liệu kiểm thử với mục tiêu khác nhau.
Benchmark A gồm 2.087 điều luật thuộc 7 văn bản pháp luật và 512 câu hỏi. Các câu hỏi được phân thành những nhóm như factoid, câu hỏi có điều kiện, câu hỏi nhiều bước và câu hỏi phủ định.
Trong đó, nhóm xây dựng một tập đối chuẩn Tier 1 gồm 205 câu hỏi, được lựa chọn sao cho toàn bộ căn cứ cần thiết nằm trong 500 điều luật đã được LightRAG lập chỉ mục. Việc này nhằm hạn chế ảnh hưởng của độ phủ dữ liệu khi đối sánh ba kiến trúc ở giai đoạn 1.
Một phần câu hỏi cũng được diễn đạt lại dựa trên mức độ trùng lặp từ vựng với văn bản nguồn. Đây là thao tác trên một phần dữ liệu được lựa chọn, không phải toàn bộ 512 câu hỏi.
Benchmark B gồm 50 câu hỏi trong phạm vi Chương III Luật Đất đai 2024, từ Điều 26 đến Điều 48. Trong đó có 47 câu có thể trả lời từ corpus và 3 câu không đủ căn cứ trong phạm vi dữ liệu.
Hai benchmark được sử dụng cho các mục tiêu đánh giá khác nhau, vì vậy nhóm không gộp kết quả của chúng thành một bảng xếp hạng chung.
Về chỉ số, nhóm sử dụng Recall@5 và MRR@5 để đánh giá truy hồi. Với Benchmark B, nhóm mở rộng đánh giá sang locator Điều - Khoản - Điểm, độ bao phủ điều kiện và ngoại lệ, phạm vi chủ thể, độ chính xác trích dẫn và khả năng xử lý chuỗi dẫn chiếu.
Sau đây, nhóm xin chuyển sang kết quả thực nghiệm của hai giai đoạn đầu.""",

    # Slide 7
    """Trước tiên, ở giai đoạn 1, nhóm đánh giá ba kiến trúc trên tập Tier 1 gồm 205 câu hỏi.
Về Recall@5, Naive Vector RAG đạt 0,9561, Hybrid RAG đạt 0,9659 và LightRAG cũng đạt 0,9659.
Về MRR@5, Hybrid RAG đạt 0,9243, cao hơn Naive Vector RAG ở mức 0,8589 và LightRAG ở mức 0,8687. Kết quả cho thấy Hybrid RAG có khả năng đưa căn cứ liên quan lên vị trí ưu tiên tốt hơn trong cấu hình được khảo sát.
Tuy nhiên, khi chuyển sang đánh giá độ chính xác trích dẫn trong câu trả lời, kết quả lại khác biệt đáng chú ý.
Naive Vector RAG đạt 0,3259, Hybrid RAG đạt 0,2902, trong khi LightRAG đạt 0,1371.
Điều này cho thấy việc truy hồi đúng điều luật ở cấp tài liệu không đồng nghĩa với việc mô hình sẽ trích dẫn đúng đến cấp Khoản hoặc Điểm trong câu trả lời.
Nói cách khác, nhóm quan sát được một khoảng cách giữa khả năng truy hồi tài liệu liên quan và khả năng xác định chính xác căn cứ pháp lý khi tạo sinh.
Đây là cơ sở để nhóm chuyển sang khảo sát cách tổ chức dữ liệu chi tiết hơn ở giai đoạn 2.""",

    # Slide 8
    """Ở giai đoạn 2, nhóm tập trung xử lý vấn đề về cấu trúc dữ liệu.
Thay vì sử dụng nguyên một điều luật làm đơn vị tìm kiếm, nhóm triển khai Regex Parser để nhận diện các đơn vị pháp lý và tách văn bản thành những phân đoạn vi mô ở cấp Khoản và Điểm.
Sau bước phân tích, toàn bộ 2.087 điều luật được chuyển đổi thành 12.754 phân đoạn vi mô chuẩn hóa.
Tiếp theo, Module Validation kiểm tra tính toàn vẹn của cấu trúc phân cấp, nhằm hạn chế sai lệch trong quá trình nhận diện và tổ chức các đơn vị pháp lý.
Một vấn đề phát sinh là khi số lượng đơn vị tìm kiếm tăng lên, Top-5 kết quả có thể tập trung vào nhiều khoản của cùng một điều luật. Điều này gây bất lợi nếu mục tiêu đánh giá vẫn là truy hồi ở cấp Điều.
Vì vậy, nhóm sử dụng Article-level MaxP, tức là tổng hợp điểm của các phân đoạn con lên cấp Điều theo điểm lớn nhất. Đồng thời, các phân đoạn được bổ sung tiền tố phân cấp để giữ lại thông tin về điều luật cấp cha.""",

    # Slide 9
    """Để đánh giá tác động của gói xử lý cấu trúc, nhóm đối chiếu C2 - Naive Dense với C5 - Parser Dense trên toàn bộ 512 câu hỏi.
Về Recall@5, kết quả tăng từ 0,9141 lên 0,9316, tương đương tăng 1,75 điểm phần trăm.
Về MRR@5, kết quả tăng từ 0,8129 lên 0,8602, tương đương tăng 4,73 điểm phần trăm.
Đây là những chênh lệch quan sát được trong thực nghiệm; nhóm chưa sử dụng kết quả hiện có để kết luận rằng chênh lệch C2-C5 có ý nghĩa thống kê.
Điểm đáng chú ý tiếp theo là kết quả LLM-Judge Citation Accuracy của cấu hình C5 đạt 0,9902 theo giao thức đánh giá ngữ cảnh của giai đoạn 2. Trong phân bố điểm, có 504 trên 512 câu hỏi được chấm mức tối đa 1,0.
Cần lưu ý, đây là điểm đánh giá theo giao thức LLM-Judge của giai đoạn 2, không đồng nghĩa với việc 99% câu trả lời pháp lý cuối cùng đã chính xác.
Bên cạnh đó, dung lượng ngữ cảnh trung bình giảm từ khoảng 2.898 token xuống 580 token, tương đương giảm khoảng 79,9%.
Kết quả cho thấy việc tổ chức dữ liệu theo cấu trúc phân cấp có tiềm năng cải thiện hiệu quả sử dụng ngữ cảnh. Tuy nhiên, C2 và C5 khác nhau ở cả gói xử lý phân đoạn, tiền tố phân cấp và MaxP, nên chưa thể quy toàn bộ mức cải thiện cho riêng một thành phần.""",

    # Slide 10
    """Từ hai giai đoạn trước, nhóm tiếp tục phát triển kiến trúc Hybrid Parser/UKG nhằm kết hợp hai loại thông tin.
Thứ nhất là Physical Graph, biểu diễn cấu trúc vật lý của văn bản pháp luật, bao gồm quan hệ phân cấp giữa Luật, Điều, Khoản và Điểm, cùng thông tin định vị và truy nguyên về văn bản gốc.
Thứ hai là Semantic Graph, biểu diễn những thông tin ngữ nghĩa như chủ thể pháp lý, hành vi, đối tượng, điều kiện, ngoại lệ và các quan hệ quy phạm.
Hai thành phần này được chuẩn hóa và hợp nhất thành Unified Knowledge Graph - UKG, sau đó lưu trữ trên Neo4j.
Ở bước truy hồi M10, hệ thống trước tiên xác định những node pháp lý mỏ neo liên quan đến câu hỏi. Sau đó, hệ thống mở rộng bằng chứng thông qua quan hệ phân cấp, quan hệ quy phạm, điều kiện, ngoại lệ và những dẫn chiếu có thể xác định được.
Trong Benchmark B, nhóm sử dụng chế độ AUTO_FUSION để kết hợp các hướng thu thập bằng chứng này. Mô hình Jev hỗ trợ định tuyến và đánh giá mức độ liên quan, đầy đủ của bằng chứng. Nếu kết quả không hợp lệ, hệ thống có cơ chế dự phòng dựa trên quy tắc. Sau khi chuẩn hóa locator và loại bỏ trùng lặp, ngữ cảnh được chuyển cho GPT-4o-mini để tạo câu trả lời.
Một điểm cần lưu ý là không phải mọi dẫn chiếu pháp lý đều đã được phân giải thành cạnh trong Neo4j. Một số dẫn chiếu tường minh được phát hiện bổ sung từ văn bản nguồn ngay trong quá trình truy hồi.
Với câu hỏi ở Slide 2, luồng xử lý dự kiến là tìm quy định tại Điều 34, nhận diện dẫn chiếu đến Điều 46, sau đó thu thập các điều kiện liên quan và giữ lại vị trí pháp lý của từng bằng chứng.
Đây là ví dụ minh họa cho luồng thiết kế của hệ thống, chưa phải bằng chứng rằng hệ thống đã trả lời hoàn chỉnh câu hỏi đó. Kết quả kiểm thử ở giai đoạn tiếp theo sẽ cho thấy rõ hơn cả ưu điểm lẫn giới hạn này.
Sau đây, nhóm xin trình bày kết quả đối sánh chuyên sâu trên Benchmark B.""",

    # Slide 11
    """Trên Benchmark B, nhóm đối sánh LightRAG và Hybrid Parser/UKG trong cùng phạm vi văn bản, tập câu hỏi và giao thức đánh giá. Tuy nhiên, hai hệ thống vẫn giữ phương pháp phân đoạn, lập chỉ mục và truy hồi riêng.
Về chất lượng câu trả lời, Hybrid Parser/UKG đạt Legal Correctness 0,8777, cao hơn LightRAG ở mức 0,8210, tức tăng 5,67 điểm phần trăm.
Atomic Fact Coverage tăng nhẹ từ 0,8551 lên 0,8686.
Tuy nhiên, kết quả không đồng đều giữa các tiêu chí.
Đối với Condition Coverage, Hybrid Parser/UKG chỉ đạt 0,7066, thấp hơn LightRAG ở mức 0,8421.
Ngược lại, Exception Coverage tăng từ 0,3929 lên 0,6786, và Subject-Scope Accuracy tăng từ 0,7639 lên 0,8889.
Điều này cho thấy kiến trúc UKG có kết quả tốt hơn ở một số khía cạnh như nhận diện ngoại lệ, phạm vi chủ thể và trích dẫn chi tiết, nhưng chưa thể hiện ưu thế toàn diện trong việc tổng hợp mọi điều kiện pháp lý.
Về trích dẫn, khi đối sánh locator trong câu trả lời với nhãn vàng, Hybrid Parser/UKG có Citation Precision và Recall cao hơn LightRAG ở cả ba cấp Điều, Khoản và Điểm.
Ví dụ, ở cấp Khoản, Citation Recall của Hybrid Parser/UKG đạt 0,8170, trong khi LightRAG đạt 0,0435. Ở cấp Điểm, hai hệ thống lần lượt đạt 0,6374 và 0,0270.
Tuy nhiên, nhóm cũng cần lưu ý một giới hạn khi đọc chỉ số Exact Locator Recall@5. LightRAG đạt 0,8509, còn Hybrid Parser/UKG đạt 0,5560 nhưng chỉ có 39 trên 47 câu được đo. Hai hệ thống sử dụng đơn vị truy hồi có độ hạt khác nhau: một bên là chunk 1.200 token có thể bao phủ trung bình nhiều locator, bên còn lại là phân đoạn vi mô gắn với một locator. Vì vậy, không thể dựa riêng vào chỉ số này để kết luận hệ thống nào định vị chính xác hơn.
Đối với khả năng xử lý chuỗi dẫn chiếu, Hybrid Parser/UKG đạt Reference-target Recall 0,5867, Chain-step Precision 0,3241, Chain-step Recall 0,5080, nhưng Chain Exact Match bằng 0 trên 18 câu hỏi.
Điều này cho thấy hệ thống đã xác định được một phần các đơn vị pháp lý đích, nhưng chưa tái dựng chính xác toàn bộ chuỗi quan hệ theo nhãn vàng. LightRAG không xuất dữ liệu reference_paths theo giao thức đánh giá, vì vậy các chỉ số tương ứng được ghi nhận là N/A, không phải bằng 0.
Đáng chú ý, câu hỏi B012 cũng chính là dạng tình huống nhóm sử dụng ở Slide 2. Với câu hỏi này, Condition Coverage của LightRAG đạt 1,0, trong khi Hybrid Parser/UKG chỉ đạt 0,125.
Đây là một trường hợp giới hạn rõ ràng của hệ thống đề xuất: việc có cấu trúc và truy hồi được các căn cứ liên quan chưa bảo đảm mô hình tổng hợp đầy đủ mọi điều kiện và ngoại lệ cần thiết.""",

    # Slide 12
    """Từ kết quả của ba giai đoạn, nhóm có thể tổng hợp như sau.
Với RQ1, Hybrid RAG có kết quả tốt về thứ hạng truy hồi trong tập đối chuẩn, nhưng chất lượng trích dẫn trong câu trả lời vẫn còn hạn chế. Do đó, cải thiện retrieval chưa đồng nghĩa với cải thiện tương ứng ở generation.
Với RQ2, việc bổ sung Parser, Validation, tiền tố phân cấp và MaxP cho kết quả tích cực về truy hồi, chất lượng ngữ cảnh theo giao thức đánh giá và dung lượng token. Tuy nhiên, chưa thể tách riêng đóng góp của từng thành phần.
Với RQ3, Hybrid Parser/UKG thể hiện kết quả tốt hơn ở một số chỉ số về trích dẫn, ngoại lệ và phạm vi chủ thể, nhưng vẫn kém hơn LightRAG ở Condition Coverage. Vì vậy, chưa thể kết luận hệ thống vượt trội toàn diện.
Với RQ4, hệ thống có thể xác định một phần các đích dẫn chiếu, nhưng chưa tái dựng được chuỗi dẫn chiếu hoàn chỉnh theo giao thức đánh giá.
Như vậy, các giả thuyết nghiên cứu chỉ được hỗ trợ ở một số khía cạnh, thay vì được xác nhận toàn diện.""",

    # Slide 13
    """Từ quá trình triển khai và thực nghiệm, nhóm xác định bốn nhóm đóng góp chính.
Thứ nhất, xây dựng Benchmark Harness cùng hai bộ dữ liệu đánh giá có mục tiêu riêng, trong đó Benchmark B tập trung vào locator pháp lý, điều kiện, ngoại lệ, chủ thể và dẫn chiếu chéo.
Thứ hai, triển khai và đánh giá bộ Regex Parser kết hợp Validation, phân đoạn dữ liệu thành 12.754 đơn vị vi mô và sử dụng Article-level MaxP để duy trì khả năng truy hồi ở cấp Điều.
Thứ ba, thiết kế kiến trúc Hybrid Parser/UKG theo hướng tích hợp cấu trúc pháp lý với biểu diễn ngữ nghĩa, đồng thời triển khai pipeline truy hồi và mở rộng bằng chứng trên đồ thị.
Thứ tư, xây dựng bộ chỉ số đánh giá chi tiết hơn cho bài toán RAG pháp luật, giúp phân biệt hiệu quả truy hồi tài liệu với khả năng định vị căn cứ, bao phủ điều kiện và tái dựng quan hệ dẫn chiếu.
Nhóm không đặt đóng góp ở việc giới thiệu lần đầu các kỹ thuật như Graph RAG, ontology hay parser, mà ở cách tích hợp, thiết kế thực nghiệm và đánh giá các thành phần đó trên dữ liệu pháp luật Việt Nam.""",

    # Slide 14
    """Qua nghiên cứu, nhóm nhận thấy việc bảo toàn cấu trúc pháp lý và kết hợp thông tin ngữ nghĩa có thể hỗ trợ truy hồi cũng như định vị căn cứ chi tiết hơn.
Tuy nhiên, hiệu quả truy hồi tốt chưa tự động bảo đảm câu trả lời đầy đủ. Hai vấn đề còn cần tiếp tục cải thiện là khả năng tổng hợp toàn bộ điều kiện, ngoại lệ và khả năng tái dựng chính xác chuỗi dẫn chiếu giữa các quy định.
Trong thời gian tới, nhóm định hướng mở rộng kiểm thử, hoàn thiện cơ chế mở rộng và tổng hợp bằng chứng, đồng thời đánh giá sâu hơn độ chính xác pháp lý của câu trả lời.
Đó là toàn bộ nội dung nghiên cứu của nhóm. Chúng em xin cảm ơn Hội đồng và các thầy cô đã lắng nghe."""
]

print(f"{'Slide':<10}{'Words':<10}{'Est. Sec (130wpm)':<20}{'Est. Sec (140wpm)':<20}")
total_words = 0
for i, s in enumerate(slides):
    w = len(s.split())
    total_words += w
    sec130 = w / (130/60)
    sec140 = w / (140/60)
    print(f"Slide {i+1:<5}{w:<10}{sec130:<20.1f}{sec140:<20.1f}")

total_min130 = total_words / 130
total_min140 = total_words / 140
print("-" * 60)
print(f"TOTAL WORDS: {total_words}")
print(f"Total time @ 130 wpm: {total_min130:.2f} mins ({total_words/(130/60):.1f} s)")
print(f"Total time @ 140 wpm: {total_min140:.2f} mins ({total_words/(140/60):.1f} s)")

