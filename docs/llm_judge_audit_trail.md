# BÁO CÁO KIỂM TOÁN THẨM ĐỊNH ĐỘC LẬP LLM-AS-A-JUDGE (AUDIT TRAIL)

**Mô hình thẩm định:** `openai/gpt-4o-mini` (qua OpenRouter API endpoint)

**Thời gian thực thi:** 03/11/2026

- **Quy mô mẫu:** 50 câu hỏi đại diện
- **Mean Citation Accuracy:** **92.00%** (46/50 câu đạt tuyệt đối 1.0)
- **Mean Context Precision:** **94.40%**
- **Mean Faithfulness:** **95.60%**
- **Tổng Tokens tiêu thụ:** 29,640 tokens (Prompt: 25,710, Completion: 3,930)
- **Tổng Chi phí API thực tế:** **$0.006214 USD** (~155 VNĐ)

---

## BẢNG NHẬT KÝ CHI TIẾT 50 GIAO DỊCH VÀ MÃ ĐỊNH DANH TOÀN CẦU (OPENROUTER GENERATION ID)

> **Ghi chú tra cứu:** Mỗi mã `generation_id` bên dưới là một giao dịch độc nhất được lưu vĩnh viễn trên máy chủ OpenRouter, có thể tra cứu trực tiếp trên hệ thống để chứng minh tính trung thực khoa học tuyệt đối.

| STT | Mã Câu hỏi | OpenRouter Generation ID | Citation | Precision | Faithfulness | Chi phí (USD) | Lời giải thích của LLM Judge |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 01 | `01-DS-2` | `gen-1793669210-WFVQ6oMTJxC9QJJMhsSG` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh truy xuất chính xác định nghĩa về quan hệ hôn nhân có yếu tố nước ngoài theo Điều 3, Khoản 25 của Luật 52/2014/QH13. |
| 02 | `01-DS-7` | `gen-1793669213-cf8lcj29vkKLPIzNY60P` | **1.0** | 1.0 | 1.0 | $0.000124 | Ngữ cảnh trích dẫn chính xác Điều 24 của Luật 52/2014/QH13, xác nhận quyền ủy quyền giữa vợ chồng trong các giao dịch pháp lý. |
| 03 | `01-DS-9` | `gen-1793669215-AeGs0YmRxcOoRXnYrxOn` | **1.0** | 1.0 | 1.0 | $0.000148 | Ngữ cảnh trích dẫn chính xác Điều 33 của Luật 52/2014/QH13, nêu rõ quyền sử dụng đất có được sau khi kết hôn là tài sản chung, trừ trường hợp được thừa kế hoặc tặng cho riêng. |
| 04 | `01-DS-10` | `gen-1793669218-52oSq7g4ZtvlUG6qFez1` | **1.0** | 1.0 | 1.0 | $0.000114 | Ngữ cảnh truy xuất chính xác định nghĩa về sinh con bằng kỹ thuật hỗ trợ sinh sản theo Điều 3, Khoản 21 của Luật 52/2014/QH13. |
| 05 | `01-DS-11` | `gen-1793669221-i0RloRZP39YO93dBPGUP` | **1.0** | 1.0 | 1.0 | $0.000140 | Ngữ cảnh trích dẫn chính xác Điều 14 của Luật 52/2014/QH13, nêu rõ rằng nam nữ sống chung mà không đăng ký kết hôn không phát sinh quyền, nghĩa vụ giữa vợ và chồng. |
| 06 | `01-DS-14` | `gen-1793669224-a0Y28JwBHM1CSVe4JGzC` | **1.0** | 0.8 | 0.9 | $0.000125 | Ngữ cảnh trích dẫn từ Điều 29 của Luật 52/2014/QH13 phù hợp với câu hỏi về quyền chiếm hữu tài sản chung, tuy nhiên không hoàn toàn đề cập đến việc người kiếm được nhiều tiền hơn có quyền chiếm hữu nhiều hơn. |
| 07 | `01-DS-31` | `gen-1793669227-HITdaQwpudtlSLwZ7MbO` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh truy xuất chính xác trích dẫn Điều 33 của Luật 52/2014/QH13, nêu rõ cách xử lý tài sản trong trường hợp không chứng minh được quyền sở hữu. |
| 08 | `01-DS-38` | `gen-1793669230-I6EZ1yxji3DnANRBgRhc` | **1.0** | 1.0 | 1.0 | $0.000121 | Ngữ cảnh trích dẫn chính xác Điều 30 của Luật 52/2014/QH13, nêu rõ nghĩa vụ của vợ chồng trong việc sử dụng tài sản riêng để đáp ứng nhu cầu sinh hoạt gia đình. |
| 09 | `01-DS-43` | `gen-1793669233-ntCtv08GzSMXPSx3UPWs` | **1.0** | 1.0 | 1.0 | $0.000126 | Ngữ cảnh trích dẫn chính xác Điều 20 của Luật 52/2014/qh13, khẳng định việc lựa chọn nơi cư trú của vợ chồng không bị ràng buộc bởi phong tục hay ý muốn của nhà chồng. |
| 10 | `01-DS-46` | `gen-1793669239-yMO58noF92hqk49JCdzz` | **1.0** | 1.0 | 1.0 | $0.000107 | Ngữ cảnh truy xuất chính xác định nghĩa về hành vi ly hôn giả tạo theo Điều 3, Khoản 15 của Luật 52/2014/QH13. |
| 11 | `01-TN-13` | `gen-1793669243-VSKlw7DLIZW3GDqwQC7u` | **0.0** | 0.5 | 0.5 | $0.000137 | Ngữ cảnh không đề cập đến vai trò không phải của nhà nước trong việc bảo hộ hôn nhân và gia đình, mà chỉ nêu trách nhiệm của nhà nước. |
| 12 | `01-TN-14` | `gen-1793669245-PQV7JrQl9kmKL2coOsuI` | **0.0** | 0.8 | 0.9 | $0.000120 | Ngữ cảnh truy xuất không trích dẫn đúng điều luật yêu cầu (52/2014/qh13#35) mà chỉ đề cập đến các điều luật khác liên quan đến quyền của vợ chồng trong việc quản lý tài sản chung. |
| 13 | `01-TN-18` | `gen-1793669247-zRm8gFR6bbwSqBvgSkqI` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh truy xuất chính xác điều luật 82 về quyền và nghĩa vụ của người không trực tiếp nuôi con sau khi ly hôn. |
| 14 | `01-TN-22` | `gen-1793669250-PkuntwIWRq6zvP21oxdc` | **1.0** | 1.0 | 1.0 | $0.000124 | Ngữ cảnh trích dẫn từ Điều 71 của Luật 52/2014/QH13 xác định rõ nghĩa vụ và quyền của cha mẹ trong việc cùng nhau chăm sóc, nuôi dưỡng con cái, phù hợp với câu hỏi yêu cầu. |
| 15 | `01-TN-35` | `gen-1793669253-JHsOsKDN09k9PvqcnX0R` | **1.0** | 0.8 | 0.9 | $0.000123 | Ngữ cảnh truy xuất chứa thông tin chính xác về các hành vi bị cấm trong lĩnh vực hôn nhân gia đình, nhưng không hoàn toàn đầy đủ so với điều luật chuẩn. |
| 16 | `01-TL-6` | `gen-1793669256-8FBoudqO3xg3WOTKmIZ1` | **1.0** | 1.0 | 1.0 | $0.000143 | Ngữ cảnh truy xuất chính xác đề cập đến việc vợ chồng đã ly hôn muốn quay lại với nhau phải thực hiện thủ tục đăng ký kết hôn theo Điều 9, Khoản 2 của Luật 52/2014/QH13. |
| 17 | `q-1` | `gen-1793669259-VQAOS0pnWfDCljEB9Qrw` | **1.0** | 1.0 | 1.0 | $0.000118 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội chiếm đoạt di vật của người đã mất và mức án tối đa là 03 năm tù. |
| 18 | `q-2` | `gen-1793669262-h9lHlL1O93HkdMgi0awD` | **1.0** | 1.0 | 1.0 | $0.000108 | Ngữ cảnh truy xuất chính xác nêu rõ rằng không áp dụng án tù chung thân đối với người dưới 18 tuổi, phù hợp với điều luật yêu cầu. |
| 19 | `q-3` | `gen-1793669265-SMcrXaspoHQE65SOxll5` | **1.0** | 1.0 | 1.0 | $0.000114 | Ngữ cảnh trích dẫn chính xác Điều 12, quy định rõ rằng người từ đủ 16 tuổi trở lên phải chịu trách nhiệm hình sự về mọi tội phạm, phù hợp với câu hỏi yêu cầu. |
| 20 | `q-4` | `gen-1793669267-ETgwyUdC04m21KQKA32M` | **1.0** | 1.0 | 1.0 | $0.000115 | Ngữ cảnh văn bản truy xuất chính xác nêu rõ việc áp dụng hình phạt cảnh cáo cho người phạm tội nhẹ có nhiều tình tiết giảm nhẹ, phù hợp với điều luật yêu cầu. |
| 21 | `q-5` | `gen-1793669271-KpIaOdyqN3eRwrGFdzRm` | **1.0** | 1.0 | 1.0 | $0.000115 | Ngữ cảnh truy xuất chính xác nêu rõ rằng hình phạt tử hình được chuyển thành tù chung thân khi được ân giảm, phù hợp với yêu cầu của câu hỏi. |
| 22 | `q-6` | `gen-1793669274-oxinGscAT4ZCy2bwX3GE` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh trích dẫn chính xác điều luật về thời gian cấm cư trú từ 01 năm đến 05 năm sau khi mãn hạn tù. |
| 23 | `q-7` | `gen-1793669277-jdGSUmwPNcs86ktAXZvB` | **1.0** | 0.9 | 0.9 | $0.000125 | Ngữ cảnh truy xuất chính xác đề cập đến việc tịch thu tài sản và nộp vào ngân sách nhà nước, phù hợp với yêu cầu câu hỏi. |
| 24 | `q-8` | `gen-1793669279-dXcPtEskUJdlhL2xri9e` | **1.0** | 1.0 | 1.0 | $0.000106 | Ngữ cảnh truy xuất chính xác đề cập đến mức án cho hành vi chuẩn bị thực hiện tội phản quốc theo Điều 108, với mức phạt từ 01 năm đến 05 năm. |
| 25 | `q-9` | `gen-1793669282-WGqMm53dwwcdTs3XZcoo` | **1.0** | 1.0 | 1.0 | $0.000120 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc miễn trách nhiệm hình sự cho người đã nhận làm gián điệp nhưng tự thú và khai báo thành khẩn. |
| 26 | `q-10` | `gen-1793669285-Zspx2w3VQ8nRSqVPhhzN` | **1.0** | 1.0 | 1.0 | $0.000117 | Ngữ cảnh truy xuất chính xác đề cập đến hình phạt cải tạo không giam giữ tối đa 01 năm cho hành vi ngược đãi tù binh, đúng với điều luật yêu cầu. |
| 27 | `q-11` | `gen-1793669288-zPIhxGNFY8JBaWI8OwHR` | **1.0** | 1.0 | 1.0 | $0.000112 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến khung hình phạt cho tội làm lính đánh thuê, phù hợp với yêu cầu câu hỏi. |
| 28 | `q-12` | `gen-1793669291-xdNDJXSTQOPFQMk0vRY7` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh trích dẫn chính xác Điều 417 về tội cố ý bỏ thương binh, phù hợp với câu hỏi yêu cầu mức án tù cho hành vi bỏ mặc thương binh. |
| 29 | `q-13` | `gen-1793669293-57BgBFFuZUllrer1IsrK` | **1.0** | 0.8 | 0.9 | $0.000110 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc lơ là quy định trực chiến, nhưng có thêm thông tin từ các điều luật khác có thể không hoàn toàn liên quan. |
| 30 | `q-14` | `gen-1793669296-s6hupEQ11zuaqoOcAebr` | **1.0** | 1.0 | 1.0 | $0.000119 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc tự gây thương tích để trốn tránh nghĩa vụ và quy định hình phạt cụ thể. |
| 31 | `q-15` | `gen-1793669299-9jO0BCbq9k9KzwDFbQqj` | **1.0** | 1.0 | 1.0 | $0.000110 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội đầu hàng địch và mức án tù từ 03 năm đến 10 năm được nêu rõ trong Điều 399. |
| 32 | `q-16` | `gen-1793669301-FaRjWCgxiJfk3kEe6gUG` | **1.0** | 0.8 | 0.9 | $0.000107 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội làm nhục đồng đội, nhưng không hoàn toàn rõ ràng về mối liên hệ với việc nạn nhân tìm đến cái chết. |
| 33 | `q-17` | `gen-1793669304-vjSDqevKXsqvMMx7caLG` | **1.0** | 1.0 | 1.0 | $0.000140 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến hình phạt đối với người đang bị giam giữ hoặc áp giải mà bỏ trốn, cụ thể là Điều 386 với khung hình phạt từ 06 tháng đến 03 năm. |
| 34 | `q-18` | `gen-1793669306-4fbY3DFezRfutdjlBVrN` | **1.0** | 1.0 | 1.0 | $0.000127 | Ngữ cảnh truy xuất chính xác đề cập đến thời hạn cấm làm việc từ 01 năm đến 05 năm theo Điều 357 về tội lạm quyền. |
| 35 | `q-19` | `gen-1793669309-4sTviet4H9sTySXJDvA6` | **0.0** | 0.5 | 0.5 | $0.000131 | Ngữ cảnh không trích dẫn đúng điều luật liên quan đến mức phạt hành chính cho người lạm quyền, mà chỉ đề cập đến các điều luật khác không liên quan trực tiếp đến câu hỏi. |
| 36 | `q-20` | `gen-1793669312-p3E5eeK1W7QnPJDXTmdz` | **1.0** | 1.0 | 1.0 | $0.000124 | Ngữ cảnh văn bản truy xuất chính xác đề cập đến mức phạt tiền cho hành vi tái phạm xuất nhập cảnh trái phép theo Điều 347. |
| 37 | `q-21` | `gen-1793669315-9nV1o8YxNJ2ztVXtDJdr` | **1.0** | 1.0 | 1.0 | $0.000114 | Ngữ cảnh trích dẫn chính xác điều luật liên quan đến việc ở lại Việt Nam trái phép và mức phạt tù tối đa là 03 năm. |
| 38 | `q-22` | `gen-1793669318-ncjMTTrOcn5mWiN7QIdA` | **1.0** | 1.0 | 1.0 | $0.000151 | Ngữ cảnh truy xuất chính xác đề cập đến việc hủy hoại di tích văn hóa gây thiệt hại từ 500 triệu đồng trở lên và quy định mức phạt tù từ 03 đến 07 năm, đúng với điều luật yêu cầu. |
| 39 | `q-23` | `gen-1793669321-lAZOijjlFT4rcfHDclXj` | **1.0** | 0.8 | 0.9 | $0.000121 | Ngữ cảnh trích dẫn đúng điều luật liên quan đến vi phạm quản lý nhà ở, nhưng không nêu rõ mức phạt tối đa có thể lên đến 150.000.000 đồng từ điều luật khác. |
| 40 | `q-24` | `gen-1793669324-8DdRW9haL2DZVrtUosRm` | **1.0** | 1.0 | 1.0 | $0.000143 | Ngữ cảnh trích dẫn chính xác điều luật liên quan đến hành vi mua bán trái phép con dấu cơ quan và quy định mức phạt cải tạo không giam giữ tối đa 02 năm. |
| 41 | `q-25` | `gen-1793669328-lSR5FkqVQ6K7qvUNKTgj` | **1.0** | 1.0 | 1.0 | $0.000143 | Ngữ cảnh văn bản truy xuất chính xác trích dẫn điều luật liên quan đến hành vi giả mạo chức vụ và mức xử lý cải tạo không giam giữ đúng như yêu cầu câu hỏi. |
| 42 | `q-26` | `gen-1793669331-akBHEASSjMCX4bLqXXiO` | **1.0** | 1.0 | 1.0 | $0.000129 | Ngữ cảnh văn bản truy xuất chính xác đề cập đến việc cản trở nghĩa vụ quân sự và mức án tương ứng theo Điều 335, phù hợp với câu hỏi yêu cầu. |
| 43 | `q-27` | `gen-1793669334-2rdv676xpkQaCS5L6PaD` | **1.0** | 1.0 | 1.0 | $0.000127 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến hành vi gây khó dễ cho việc thực hiện nghĩa vụ quân sự trong thời kỳ chiến tranh, cụ thể là Điều 335 với mức án tù từ 02 năm đến 05 năm. |
| 44 | `q-28` | `gen-1793669337-S119vlTJIgXhrDIVZw4Y` | **1.0** | 1.0 | 1.0 | $0.000139 | Ngữ cảnh trích dẫn chính xác điều luật liên quan đến việc xử lý cán bộ vi phạm giấy tờ hộ tịch, bao gồm cả hình phạt cảnh cáo và cải tạo không giam giữ tối đa 03 năm. |
| 45 | `q-29` | `gen-1793669340-O44hAphP7LreoM4PfdyX` | **1.0** | 1.0 | 1.0 | $0.000136 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc lạm dụng quyền hạn trong nghĩa vụ quân sự và quy định mức phạt cải tạo không giam giữ tối đa là 03 năm. |
| 46 | `q-30` | `gen-1793669344-Mm3ohQQ6RPpI9LomkwU4` | **0.0** | 0.5 | 0.5 | $0.000112 | Ngữ cảnh truy xuất không chính xác vì không trích dẫn đúng điều luật 332 về mức án tù dành cho người trốn tránh nghĩa vụ quân sự trong thời chiến. |
| 47 | `q-31` | `gen-1793669346-Xh7EfinUZ9FMj5BFfCns` | **1.0** | 1.0 | 1.0 | $0.000144 | Ngữ cảnh trích dẫn chính xác điều luật liên quan đến việc dùng vũ lực hoặc đe dọa để cản trở người thi hành công vụ và nêu rõ mức phạt cải tạo không giam giữ tối đa là 03 năm. |
| 48 | `q-32` | `gen-1793669349-faI0aonOLhE5Q3Ji2gWt` | **1.0** | 1.0 | 1.0 | $0.000108 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội mua dâm người dưới 18 tuổi và khung hình phạt tương ứng. |
| 49 | `q-33` | `gen-1793669351-K9fHgxJK5l2QhukKkIoG` | **1.0** | 1.0 | 1.0 | $0.000110 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến mức phạt tiền cho người mua dâm người dưới 18 tuổi theo Điều 329. |
| 50 | `q-34` | `gen-1793669354-ep1eMElF86JCX632Mlwm` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh truy xuất chính xác đề cập đến việc đánh bạc trái phép với số tiền từ 5 triệu đến dưới 50 triệu đồng và quy định mức phạt tương ứng. |
