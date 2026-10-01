import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from src.preprocessing.document_loader import DocxLoader
loader = DocxLoader()
paras = loader.load_structured('datasets/raw_laws/Luat_dat_dai_chuong_3.docx')
for p in paras:
    if 'Tổ chức trong nước là pháp nhân mới được hình thành' in p.text or 'Cho thuê lại quyền sử dụng đất theo hình thức trả' in p.text:
        print(f"{p.index}: numId={p.num_id}, ilvl={p.ilvl}, marker='{p.marker}' - {p.text[:30]}...")
