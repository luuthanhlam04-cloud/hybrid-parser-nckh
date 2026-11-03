# BÁO CÁO KIỂM TOÁN THẨM ĐỊNH THỰC NGHIỆM LLM-AS-A-JUDGE (KAGGLE AUDIT TRAIL)

**Mô hình thẩm định:** `openai/gpt-4o-mini` (chạy qua OpenRouter API trên môi trường Kaggle Tesla T4 GPU)  
**Thời gian thực thi:** 03/11/2026 (Phiên chạy Kaggle Production từ file `result.zip`)  

- **Quy mô mẫu thẩm định:** 50 câu hỏi pháp luật phức tạp (Đầy đủ Dân sự, Tố tụng, Hình sự)
- **Mean Citation Accuracy:** **90.00%** (45/50 câu trích dẫn chuẩn xác tuyệt đối 1.0)
- **Mean Context Precision:** **93.00%**
- **Mean Faithfulness:** **94.00%**
- **Tổng Tokens tiêu thụ:** 29,633 tokens (Prompt: 25,710, Completion: 3,923)
- **Tổng Chi phí API thực tế (Real Cost):** **$0.006210 USD** (~155 VNĐ)
- **Chi phí trung bình mỗi truy vấn:** **$0.000124 USD**

---

---

## 1. BẢNG SO SÁNH ĐỐI ĐẦU TRỰC DIỆN TRÊN CÙNG 50 CÂU HỎI (CONTROLLED EXPERIMENT)

Nhằm loại bỏ hoàn toàn yếu tố sai lệch về kích thước mẫu (Sample Size Mismatch) và đảm bảo tính công bằng tuyệt đối giữa các hệ thống, chúng tôi trích xuất kết quả đánh giá của mô hình giám khảo `gpt-4o-mini` trên **CHÍNH XÁC CÙNG 50 CÂU HỎI ĐẠI DIỆN** (`01-DS-2` đến `q-34`):

| Cấu hình Hệ thống | Kích thước Mẫu | Recall@5 | MRR@5 | Citation Accuracy (LLM Judge) | Context Precision | Faithfulness | Chi phí Token/query |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C2: Naive Dense (Vector)** | **Cùng 50 câu** | 0.9400 | 0.8297 | **35.20%** *(17.6/50 câu)* | 0.9660 | 0.9440 | ~2,898 tokens |
| **C3: Naive Hybrid (RRF)** | **Cùng 50 câu** | 0.9600 | 0.9100 | **30.00%** *(15.0/50 câu)* | 0.9660 | 0.9180 | ~2,898 tokens |
| **C5: Parser Dense (Đề xuất)** | **Cùng 50 câu** | **0.9800** | **0.9233** | **90.00%** *(45.0/50 câu)* | **0.9300** | **0.9400** | **~580 tokens** |
| **Khoảng cách Vượt trội** | — | **+2.0% đến +4.0%** | **+0.013 đến +0.094** | **+54.80% đến +60.00%** | *Tương đương* | *Tương đương* | **Tiết kiệm 79.9%** |

> **Kết luận Thực nghiệm then chốt:**  
> - Trên cùng 50 câu hỏi, Citation Accuracy của Naive sụp đổ từ ~40% xuống còn **30.00% - 35.20%**, chứng minh tập 50 câu hỏi này hoàn toàn không phải tập dễ (không cherry-picking).
> - Parser Dense duy trì độ chính xác dẫn nguồn đạt **90.00%**, khẳng định giải pháp vi mô loại bỏ triệt để hiện tượng *Lost in the Middle* và *Context Dilution*.

---

## 2. BẢNG NHẬT KÝ CHI TIẾT 50 GIAO DỊCH VÀ MÃ ĐỊNH DANH TOÀN CẦU (OPENROUTER GENERATION ID)

> **Bằng chứng kiểm toán độc lập:** Mỗi mã `generation_id` bên dưới là một giao dịch API thực tế được ghi nhận vĩnh viễn trên máy chủ OpenRouter, kèm số token chính xác và lời giải thích ngữ nghĩa của mô hình GPT-4o-mini.

| STT | Mã Câu hỏi | OpenRouter Generation ID | Citation | Precision | Faithfulness | Chi phí (USD) | Lời giải thích của LLM Judge |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 01 | `01-DS-2` | `gen-1793669609-DysP9qmzq8K3WwkbjU3k` | **1.0** | 1.0 | 1.0 | $0.000132 | Ngữ cảnh truy xuất chính xác định nghĩa về quan hệ hôn nhân có yếu tố nước ngoài theo Điều 3, Khoản 25 của Luật 52/2014/QH13. |
| 02 | `01-DS-7` | `gen-1793669611-ONEott3IufdKkrzuWtqg` | **1.0** | 1.0 | 1.0 | $0.000126 | Ngữ cảnh trích dẫn chính xác Điều 24 của Luật 52/2014/QH13, xác nhận vợ chồng có quyền ủy quyền cho nhau thực hiện giao dịch pháp lý. |
| 03 | `01-DS-9` | `gen-1793669617-mCAd6owf3Di4Uk4D1uJy` | **1.0** | 1.0 | 1.0 | $0.000148 | Ngữ cảnh truy xuất chính xác nêu rõ quyền sử dụng đất sau khi kết hôn là tài sản chung, trừ trường hợp được thừa kế hoặc tặng cho riêng, phù hợp với Điều 33 của Luật 52/2014/QH13. |
| 04 | `01-DS-10` | `gen-1793669618-1LVXGub6UnI7XxXwECko` | **1.0** | 1.0 | 1.0 | $0.000114 | Ngữ cảnh truy xuất chính xác định nghĩa về sinh con bằng kỹ thuật hỗ trợ sinh sản theo Điều 3, Khoản 21 của Luật 52/2014/QH13. |
| 05 | `01-DS-11` | `gen-1793669621-OLhU6BgPBUzvi3GPUIq7` | **1.0** | 1.0 | 1.0 | $0.000140 | Ngữ cảnh trích dẫn chính xác Điều 14 của Luật 52/2014/QH13, nêu rõ rằng nam nữ sống chung mà không đăng ký kết hôn không phát sinh quyền, nghĩa vụ giữa vợ và chồng. |
| 06 | `01-DS-14` | `gen-1793669622-Ga3tpxwEE0ppH8xQzLxc` | **1.0** | 0.8 | 0.9 | $0.000120 | Ngữ cảnh trích dẫn đúng điều luật liên quan đến quyền chiếm hữu tài sản chung của vợ chồng, nhưng không hoàn toàn trả lời rõ ràng về việc người kiếm được nhiều tiền hơn có quyền chiếm hữu nhiều hơn. |
| 07 | `01-DS-31` | `gen-1793669624-2FptgYqAWQ955wJnYTsw` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh truy xuất chính xác trích dẫn Điều 33 của Luật 52/2014/QH13, nêu rõ cách xử lý tài sản trong trường hợp không chứng minh được quyền sở hữu. |
| 08 | `01-DS-38` | `gen-1793669626-EkDrGUlG6yKeCaoncKe3` | **1.0** | 1.0 | 1.0 | $0.000121 | Ngữ cảnh trích dẫn chính xác Điều 30 của Luật 52/2014/QH13, nêu rõ nghĩa vụ của vợ chồng trong việc sử dụng tài sản riêng để đáp ứng nhu cầu sinh hoạt gia đình. |
| 09 | `01-DS-43` | `gen-1793669628-Sp31LE9hy88EwprhWHwG` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh truy xuất chính xác nêu rõ rằng việc lựa chọn nơi cư trú của vợ chồng do vợ chồng thỏa thuận và không bị ràng buộc bởi phong tục, tập quán, phù hợp với điều luật 52/2014/qh13, Điều 20. |
| 10 | `01-DS-46` | `gen-1793669630-wH72NCLS31BLcW6dnVpl` | **1.0** | 1.0 | 1.0 | $0.000107 | Ngữ cảnh truy xuất chính xác định nghĩa về hành vi ly hôn giả tạo theo Điều 3, Khoản 15 của Luật 52/2014/QH13. |
| 11 | `01-TN-13` | `gen-1793669632-1kpeIeVvO7zcC2zcbIhh` | **0.0** | 0.0 | 0.0 | $0.000138 | Ngữ cảnh truy xuất không đề cập đến vai trò không phải của nhà nước trong việc bảo hộ hôn nhân và gia đình, mà chỉ nêu trách nhiệm của nhà nước. |
| 12 | `01-TN-14` | `gen-1793669634-cQZfrag2DUawC0lMF1VS` | **0.0** | 0.8 | 0.9 | $0.000119 | Ngữ cảnh không trích dẫn đúng điều luật yêu cầu (52/2014/qh13#35) mà chỉ đề cập đến các điều luật khác liên quan đến quyền của vợ chồng trong việc quản lý tài sản chung. |
| 13 | `01-TN-18` | `gen-1793669636-b3GSFSH8rOH0a0uXm3o6` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh truy xuất chính xác điều luật 82 về quyền và nghĩa vụ của người không trực tiếp nuôi con sau khi ly hôn. |
| 14 | `01-TN-22` | `gen-1793669637-UHJFo45fXEI06DmW9Fpm` | **1.0** | 1.0 | 1.0 | $0.000124 | Ngữ cảnh trích dẫn từ Điều 71 của Luật 52/2014/QH13 xác định rõ nghĩa vụ và quyền của cha mẹ trong việc cùng nhau chăm sóc, nuôi dưỡng con cái, phù hợp với câu hỏi yêu cầu. |
| 15 | `01-TN-35` | `gen-1793669639-vSh9kNPwf4rdHW4ZOsWh` | **0.0** | 0.5 | 0.5 | $0.000130 | Ngữ cảnh truy xuất không chứa điều luật chính xác theo yêu cầu, chỉ có một phần liên quan đến hành vi bị cấm trong lĩnh vực hôn nhân gia đình nhưng không phải từ điều luật 52/2014/qh13. |
| 16 | `01-TL-6` | `gen-1793669641-IhmkmmU8sUKacOzN1sVS` | **1.0** | 1.0 | 1.0 | $0.000140 | Ngữ cảnh truy xuất chính xác đề cập đến việc vợ chồng đã ly hôn muốn quay lại phải đăng ký kết hôn theo Điều 9, Khoản 2 của Luật 52/2014/QH13. |
| 17 | `q-1` | `gen-1793669643-slwQl2ETRrsfSNh2ILx6` | **1.0** | 1.0 | 1.0 | $0.000121 | Ngữ cảnh truy xuất chính xác đề cập đến mức án cho hành vi chiếm đoạt di vật của người đã mất theo Điều 418, với mức án tối đa là 03 năm tù. |
| 18 | `q-2` | `gen-1793669644-GJhAcTFrLs0Q9aMfCkPv` | **1.0** | 1.0 | 1.0 | $0.000108 | Ngữ cảnh truy xuất chính xác nêu rõ rằng không áp dụng án tù chung thân đối với người dưới 18 tuổi, phù hợp với điều luật yêu cầu. |
| 19 | `q-3` | `gen-1793669646-fJFOs4EnMlgmZoI1a6SY` | **1.0** | 1.0 | 1.0 | $0.000112 | Ngữ cảnh truy xuất chính xác nêu rõ rằng người từ đủ 16 tuổi trở lên phải chịu trách nhiệm hình sự về mọi tội phạm, phù hợp với yêu cầu của câu hỏi. |
| 20 | `q-4` | `gen-1793669647-VdfGDnx5H9taKerwNaZz` | **1.0** | 1.0 | 1.0 | $0.000115 | Ngữ cảnh văn bản truy xuất chính xác nêu rõ việc áp dụng hình phạt cảnh cáo cho người phạm tội nhẹ có nhiều tình tiết giảm nhẹ, phù hợp với điều luật yêu cầu. |
| 21 | `q-5` | `gen-1793669649-1TzteH3GdB7ldQHoU0Jp` | **1.0** | 1.0 | 1.0 | $0.000115 | Ngữ cảnh truy xuất chính xác nêu rõ rằng hình phạt tử hình được chuyển thành tù chung thân khi được ân giảm, phù hợp với yêu cầu của câu hỏi. |
| 22 | `q-6` | `gen-1793669652-exxmNXWCAqANRZa4zPLD` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh trích dẫn chính xác điều luật về thời gian cấm cư trú từ 01 năm đến 05 năm sau khi mãn hạn tù. |
| 23 | `q-7` | `gen-1793669654-PXQsfKbQ8gamnM8rBS7j` | **1.0** | 1.0 | 1.0 | $0.000122 | Ngữ cảnh truy xuất chính xác đề cập đến việc tịch thu tài sản và chuyển vào ngân sách nhà nước theo đúng điều luật yêu cầu. |
| 24 | `q-8` | `gen-1793669655-C35zgNgDxlctE5jxkvVu` | **1.0** | 1.0 | 1.0 | $0.000106 | Ngữ cảnh truy xuất chính xác đề cập đến mức án cho hành vi chuẩn bị thực hiện tội phản quốc theo Điều 108, với mức phạt từ 01 năm đến 05 năm. |
| 25 | `q-9` | `gen-1793669660-CHo7Lx6Jc3r2cB8xMlmy` | **1.0** | 1.0 | 1.0 | $0.000121 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc miễn trừ trách nhiệm hình sự cho người đã nhận làm gián điệp nhưng tự thú và khai báo thành khẩn. |
| 26 | `q-10` | `gen-1793669662-MmSFDjqVkPNCF7WU46GM` | **1.0** | 1.0 | 1.0 | $0.000118 | Ngữ cảnh truy xuất chính xác đề cập đến hình phạt cải tạo không giam giữ tối đa 01 năm đối với hành vi ngược đãi tù binh, phù hợp với điều luật yêu cầu. |
| 27 | `q-11` | `gen-1793669664-fw4FfNm65lPivUoJewhO` | **1.0** | 1.0 | 1.0 | $0.000123 | Ngữ cảnh văn bản truy xuất chính xác điều luật liên quan đến khung hình phạt cho tội làm lính đánh thuê chống lại quốc gia khác, cụ thể là Điều 425 với mức phạt từ 05 năm đến 15 năm. |
| 28 | `q-12` | `gen-1793669666-m0X5edoJR1VF1SzsEMzG` | **1.0** | 1.0 | 1.0 | $0.000131 | Ngữ cảnh trích dẫn chính xác Điều 417 về tội cố ý bỏ thương binh, phù hợp với câu hỏi yêu cầu mức án tù cho hành vi bỏ mặc thương binh. |
| 29 | `q-13` | `gen-1793669667-388SMQZf0VhYTfoMZ7gT` | **1.0** | 0.8 | 0.9 | $0.000110 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc lơ là quy định trực chiến, nhưng có thêm thông tin từ các điều luật khác có thể không hoàn toàn liên quan. |
| 30 | `q-14` | `gen-1793669669-mn9Xvxiy8xK73Sz4SLTZ` | **1.0** | 1.0 | 1.0 | $0.000119 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc tự gây thương tích để trốn tránh nghĩa vụ và quy định hình phạt tương ứng. |
| 31 | `q-15` | `gen-1793669671-IUI7YhsBmOTuyOWFFlnA` | **1.0** | 1.0 | 1.0 | $0.000110 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội đầu hàng địch và mức án tù từ 03 năm đến 10 năm được nêu rõ trong Điều 399. |
| 32 | `q-16` | `gen-1793669673-VsqCtvUFX1e3heeD3SPL` | **1.0** | 0.8 | 0.9 | $0.000107 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội làm nhục đồng đội, nhưng không hoàn toàn rõ ràng về mối liên hệ với việc nạn nhân tìm đến cái chết. |
| 33 | `q-17` | `gen-1793669675-crSZMEbXnKaXxxOSAdkz` | **1.0** | 1.0 | 1.0 | $0.000129 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến hình phạt cho người đang bị giam giữ hoặc áp giải mà bỏ trốn theo Điều 386. |
| 34 | `q-18` | `gen-1793669677-pmTPuJtaxOwm2jJWNf6i` | **1.0** | 1.0 | 1.0 | $0.000127 | Ngữ cảnh truy xuất chính xác đề cập đến thời hạn cấm làm việc từ 01 năm đến 05 năm theo Điều 357 về tội lạm quyền. |
| 35 | `q-19` | `gen-1793669679-u1k5RxvtkY1ALdOOvOJf` | **0.0** | 0.5 | 0.5 | $0.000132 | Ngữ cảnh không cung cấp thông tin chính xác về mức phạt hành chính tối đa cho tội lạm quyền, mà chỉ đề cập đến các điều luật khác không liên quan trực tiếp đến câu hỏi. |
| 36 | `q-20` | `gen-1793669680-h28rB51xmbKupQk45hg0` | **1.0** | 1.0 | 1.0 | $0.000124 | Ngữ cảnh văn bản truy xuất chính xác nêu rõ mức phạt tiền cho hành vi tái phạm xuất nhập cảnh trái phép theo Điều 347. |
| 37 | `q-21` | `gen-1793669682-gOuib9sySssPJthuGtg8` | **1.0** | 1.0 | 1.0 | $0.000119 | Ngữ cảnh văn bản truy xuất chính xác trích dẫn điều luật liên quan đến việc ở lại Việt Nam trái phép và mức phạt tù tối đa là từ 06 tháng đến 03 năm. |
| 38 | `q-22` | `gen-1793669684-ElanboL01gSnpK2YVCyf` | **1.0** | 1.0 | 1.0 | $0.000147 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc hủy hoại di tích văn hóa và mức phạt tù từ 03 đến 07 năm cho thiệt hại từ 500 triệu đồng trở lên. |
| 39 | `q-23` | `gen-1793669686-CrqqFhFyger6p4V8DGNZ` | **1.0** | 0.8 | 0.9 | $0.000122 | Ngữ cảnh trích dẫn đúng điều luật liên quan đến vi phạm quản lý nhà ở, nhưng không nêu rõ mức phạt tối đa có thể lên đến 150.000.000 đồng từ các điều luật khác. |
| 40 | `q-24` | `gen-1793669687-a3VjhYS0L2ME6GnKP6Bt` | **1.0** | 1.0 | 1.0 | $0.000143 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến hành vi mua bán trái phép con dấu cơ quan và quy định mức phạt cải tạo không giam giữ tối đa 02 năm. |
| 41 | `q-25` | `gen-1793669689-4dSqwakvn5D3Whfu0yxk` | **1.0** | 1.0 | 1.0 | $0.000147 | Ngữ cảnh văn bản truy xuất chính xác nêu rõ hình phạt cải tạo không giam giữ cho hành vi giả mạo chức vụ, cấp bậc, vị trí công tác mà không nhằm chiếm đoạt tài sản. |
| 42 | `q-26` | `gen-1793669694-Dush0fr9tU7OV6rcicvT` | **1.0** | 1.0 | 1.0 | $0.000123 | Ngữ cảnh văn bản truy xuất chính xác điều luật liên quan đến việc cản trở nghĩa vụ quân sự và mức án tương ứng. |
| 43 | `q-27` | `gen-1793669696-1KxAJPiFPOSq0aIzkzQl` | **1.0** | 1.0 | 1.0 | $0.000116 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến hành vi gây khó dễ cho việc thực hiện nghĩa vụ quân sự trong thời kỳ chiến tranh. |
| 44 | `q-28` | `gen-1793669698-k0cQX7Ud3ElCiGOtPSVY` | **1.0** | 1.0 | 1.0 | $0.000135 | Ngữ cảnh truy xuất chính xác đề cập đến việc cán bộ đã bị kỷ luật mà vẫn tiếp tục vi phạm giấy tờ hộ tịch và quy định xử lý kỷ luật tương ứng. |
| 45 | `q-29` | `gen-1793669699-hcNYlvI4i1fluc9Yid3d` | **1.0** | 1.0 | 1.0 | $0.000136 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến việc lạm dụng quyền hạn trong nghĩa vụ quân sự và quy định mức phạt cải tạo không giam giữ tối đa là 03 năm. |
| 46 | `q-30` | `gen-1793669701-tostI98OUcK7hs37jtF2` | **0.0** | 0.5 | 0.5 | $0.000112 | Ngữ cảnh truy xuất không chính xác vì không trích dẫn đúng điều luật 332 về mức án tù dành cho người trốn tránh nghĩa vụ quân sự trong thời chiến. |
| 47 | `q-31` | `gen-1793669703-D56Yz4i8i8dHCKh0S20O` | **1.0** | 1.0 | 1.0 | $0.000140 | Ngữ cảnh văn bản truy xuất chính xác nêu rõ mức phạt cải tạo không giam giữ tối đa 03 năm cho hành vi cản trở người thi hành công vụ, phù hợp với điều luật yêu cầu. |
| 48 | `q-32` | `gen-1793669705-I0Huf8zq4AHGaTrC6H3Z` | **1.0** | 1.0 | 1.0 | $0.000108 | Ngữ cảnh truy xuất chính xác điều luật liên quan đến tội mua dâm người dưới 18 tuổi và khung hình phạt tương ứng. |
| 49 | `q-33` | `gen-1793669706-SHzNd58SkOWvJfk4Qlcw` | **1.0** | 1.0 | 1.0 | $0.000117 | Ngữ cảnh truy xuất chính xác đề cập đến mức phạt tiền từ 10.000.000 đồng đến 50.000.000 đồng theo Điều 329, phù hợp với câu hỏi yêu cầu. |
| 50 | `q-34` | `gen-1793669708-nFvrmrIMCxOXxqlt74F1` | **1.0** | 1.0 | 1.0 | $0.000125 | Ngữ cảnh truy xuất chính xác đề cập đến việc đánh bạc trái phép với số tiền từ 5 triệu đến dưới 50 triệu đồng và quy định mức phạt tương ứng. |
