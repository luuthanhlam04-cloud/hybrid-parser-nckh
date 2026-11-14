# -*- coding: utf-8 -*-
with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Question 3
q3_old = """**Câu 3 (Dương): "Các em dùng GPT-4o-mini vừa sinh câu trả lời vừa làm giám khảo. Kết quả có bị thiên lệch tự thân không?"**
> *"Dạ đây là một rủi ro phương pháp luận mà nhóm đã chủ động kiểm soát qua quy trình thẩm định kép tại Mục 2.3.6.  
> Thước đo trích dẫn là một kiểm tra tất định: căn cứ do hệ thống sinh ra được so khớp trực tiếp với Golden Citation định danh trong bộ dữ liệu chuẩn, không phụ thuộc vào cảm tính của LLM.  
> Đối với các thước đo định tính như Legal Correctness, nhóm sử dụng giao thức chuẩn hóa với tiêu chí chấm điểm khắt khe và ghi nhận mức độ đồng thuận cao giữa các lượt chấm."*"""

q3_new = """**Câu 3 (Dương): "Các em dùng GPT-4o-mini vừa sinh câu trả lời vừa làm giám khảo. Kết quả có bị thiên lệch tự thân không?"**
> *"Dạ thưa Thầy/Cô, đây là một hạn chế phương pháp luận đã được nhóm ghi nhận trung thực tại Mục 3.8.3. Ở Giai đoạn 1 và 2, Citation Accuracy được chấm bằng LLM-as-a-Judge (GPT-4o-mini) — cùng họ mô hình với mô hình sinh, nên chưa đạt tính độc lập tuyệt đối về mô hình. Nhóm đã giảm thiểu bằng cách tách biệt hoàn toàn prompt thẩm định, bắt buộc kiểm tra JSON schema, ghi log kiểm toán và thiết lập cơ chế thử lại tối đa 3 lần khi định dạng không hợp lệ.  
> Đặc biệt sang Giai đoạn 3, các chỉ số Citation Precision và Recall tại Bảng 3.16 đã được chuyển đổi hoàn toàn sang phương pháp tính toán tất định dựa trên quy tắc (Rule-based Locator Matching), không còn phụ thuộc vào LLM chấm. Hướng hoàn thiện tiếp theo là sử dụng mô hình thẩm định độc lập từ nhà phát triển khác hoặc mời chuyên gia pháp lý chấm mẫu để hiệu chuẩn."*"""

# 2. Update Question 4
q4_old = """**Câu 4 (Dương): "Việc viết lại 512 câu hỏi ở Benchmark A có làm biến đổi ngữ nghĩa pháp lý gốc không?"**
> *"Dạ không ạ. Quy trình viết lại tại Mục 2.3.5 được thiết kế với nguyên tắc bất biến ngữ nghĩa: chỉ thay đổi từ ngữ diễn đạt thông thường và cách đặt câu hỏi của người dân, trong khi giữ nguyên 100% căn cứ pháp lý đích.  
> Nhóm chỉ thực hiện viết lại có chọn lọc trên các câu có độ trùng lặp từ vựng Jaccard vượt ngưỡng 0,5, đưa chỉ số trùng lặp trung bình từ 0,68 xuống 0,31 để loại bỏ hiện tượng học vẹt từ khóa mà không làm suy chuyển bản chất câu hỏi."*"""

q4_new = """**Câu 4 (Dương): "Việc viết lại 512 câu hỏi ở Benchmark A có làm biến đổi ngữ nghĩa pháp lý gốc không?"**
> *"Dạ quy trình viết lại tại Mục 2.3.5 được thiết kế với nguyên tắc bất biến ngữ nghĩa: chỉ thay đổi từ ngữ diễn đạt của người dân, giữ nguyên căn cứ pháp lý đích. Nhóm thực hiện viết lại có chọn lọc trên các câu có độ trùng lặp từ vựng Jaccard vượt ngưỡng 0,5, đưa chỉ số trùng lặp trung bình từ 0,68 xuống 0,31 để loại bỏ hiện tượng học vẹt từ khóa.  
> Báo cáo cũng ghi nhận hạn chế là chưa có nhật ký xác nhận toàn bộ 512 câu đều viết lại thành công, và việc xây dựng pipeline kiểm tra ngữ nghĩa tự động cho toàn bộ tập dữ liệu là hướng nghiên cứu hoàn thiện tiếp theo."*"""

# 3. Add note about N in Table 3.16 into Slide 11 blueprint
s11_note_old = """  * *Footnote hiển thị dưới chân slide:*  
    `(*) Exact Locator đo mức trùng khớp chuỗi ký tự cục bộ; UKG ưu tiên tính toàn vẹn của thực thể quy phạm cấp Điều (Citation Precision cấp Điều đạt 0,8369 so với 0,3333 của LightRAG).`"""

s11_note_new = """  * *Footnote hiển thị dưới chân slide:*  
    `(*) Exact Locator đo mức trùng khớp chuỗi ký tự cục bộ; UKG ưu tiên tính toàn vẹn của thực thể quy phạm cấp Điều (Citation Precision cấp Điều đạt 0,8369 so với 0,3333 của LightRAG).`  
    `(**) Quy mô mẫu phân tầng theo Bảng 3.16: Cấp Điều có N = 47; Cấp Khoản có N = 46 (1 câu không có nhãn Khoản); Cấp Điểm có N = 37 (10 câu căn cứ dừng ở cấp Khoản, không có Điểm). Không gán điểm 0 cho trường hợp không áp dụng.`"""

# 4. Add cheat note in Part 3 Slide 11
s11_cheat_old = """• RQ3: Recall 0,9184 (+18,26 đpt), Citation Precision Điều 0,8369 vs 0,3333, Exception Coverage 0,6786 (+28,57 đpt)<br>• Trade-off Condition Coverage & Exact Locator; RQ4 ranh giới chuỗi"""
s11_cheat_new = """• RQ3: Recall 0,9184 (+18,26 đpt), Citation Precision Điều 0,8369 vs 0,3333, Exception Coverage 0,6786 (+28,57 đpt)<br>• Trade-off Condition Coverage & Exact Locator; RQ4 ranh giới chuỗi<br>• [Phao N]: Cấp Điều N=47, Khoản N=46, Điểm N=37 (nhãn dừng ở cấp trên)"""

for o, n in [(q3_old, q3_new), (q4_old, q4_new), (s11_note_old, s11_note_new), (s11_cheat_old, s11_cheat_new)]:
    if o in text:
        text = text.replace(o, n)
    else:
        print('Warning: string replacement target not found!')

# Clean any control characters if present
text = text.replace('\x07', 'alpha')

with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated kich_ban_thuyet_trinh_15p.md with the 2 Q&A fixes and N=47/46/37 sample note.')

