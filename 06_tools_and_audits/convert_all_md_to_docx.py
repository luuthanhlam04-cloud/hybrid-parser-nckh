# -*- coding: utf-8 -*-
"""
convert_all_md_to_docx.py
Chuyển đổi 5 file báo cáo Markdown sang tài liệu Word (.docx) chuẩn mực học thuật,
mô phỏng chính xác 100% định dạng, cấu trúc và văn phong của tác giả Minh (hochoi.docx):
- Khổ giấy A4 chuẩn TCVN: Lề Trên 2.0cm, Dưới 2.0cm, Trái 3.0cm, Phải 2.0cm.
- Font chữ: 100% Times New Roman, cỡ 13pt cho nội dung thường (12pt cho bảng và tài liệu tham khảo).
- Giãn dòng: 1.5 lines, thụt đầu dòng 1.27cm (0.5 inch), căn đều hai bên (Justified).
- Tiêu đề các cấp: Heading 1 (14pt Bold All Caps), Heading 2 (13pt Bold), Heading 3 (13pt Bold/Italic).
- Bảng biểu chuẩn mực học thuật: Có tiêu đề bảng bên trên, viền đơn đen, padding ô thoáng đãng, lặp header.
- Công thức toán học: Chuyển đổi ký hiệu LaTeX sang Unicode tự nhiên, căn giữa dòng.
- Tài liệu tham khảo: Thụt lề treo (Hanging Indent) chuẩn IEEE, có link DOI rõ ràng.
- Triệt tiêu hoàn toàn các dấu hiệu định dạng tự động của AI (không có raw markdown, không có --- thô thiển).
"""

import os
import re
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn


def clean_math_syntax(tex: str) -> str:
    """Chuyển đổi cú pháp LaTeX thô sang văn phong toán học Unicode tự nhiên."""
    s = tex.strip()
    s = s.replace(r'\text{-}', '-')
    s = s.replace(r'\text{temp}', 'temp')
    s = s.replace(r'\text{MaxP}', 'MaxP')
    s = s.replace(r'\text{weighted}', 'weighted')
    s = s.replace(r'\text{Weighted}', 'Weighted')
    s = s.replace(r'\text{dense}', 'dense')
    s = s.replace(r'\text{Dense}', 'Dense')
    s = s.replace(r'\text{bm25}', 'bm25')
    s = s.replace(r'\text{BM25}', 'BM25')
    s = s.replace(r'\text{RRF}', 'RRF')
    s = s.replace(r'\text{Score}', 'Score')
    s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
    s = s.replace(r'\alpha', 'α')
    s = s.replace(r'\beta', 'β')
    s = s.replace(r'\cdot', ' · ')
    s = s.replace(r'\times', ' × ')
    s = s.replace(r'\sum_{m \in M}', '∑_(m ∈ M)')
    s = s.replace(r'\sum', '∑')
    s = s.replace(r'\max_{p \in A}', 'max_(p ∈ A)')
    s = s.replace(r'\max', 'max')
    s = s.replace(r'\min', 'min')
    s = s.replace(r'\in', '∈')
    s = s.replace(r'\approx', '≈')
    s = s.replace(r'\le', '≤')
    s = s.replace(r'\ge', '≥')
    s = s.replace(r'\to', '→')
    s = s.replace(r'W^+', 'W⁺')
    s = s.replace(r'W^-', 'W⁻')
    
    # fractions: \frac{a}{b} -> (a / b)
    s = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1 / \2)', s)
    
    # subscripts: r_{dense}(A) -> r_dense(A)
    s = re.sub(r'_\{([^}]+)\}', r'_\1', s)
    s = re.sub(r'\^\{([^}]+)\}', r'^\1', s)
    
    # remove residual backslashes
    s = s.replace('\\', '')
    return s.strip()


def setup_document_styles(doc: docx.Document):
    """Cấu hình trang và styles cốt lõi theo đúng chuẩn luận văn NCKH (hochoi.docx)."""
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)

    # Style Normal
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(6)


def parse_inline_formatting(paragraph, text: str, font_size=Pt(13), font_name='Times New Roman', is_bold_override=None, is_italic_override=None):
    """Phân tách chuỗi markdown thành các Runs với định dạng phong phú."""
    # Xử lý an toàn các ký tự escape trong markdown (dùng placeholder unicode để tránh đụng độ token)
    clean_src = text.replace(r'\*', '∗').replace(r'\_', '_').replace(r'\[', '[').replace(r'\]', ']')
    
    # Pattern nhận diện: bold italic, bold, italic, code, math, markdown links
    pattern = re.compile(r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*[^*]+?\*|`[^`]+`|\$[^$]+\$|\[[^\]]+\]\([^)]+\))')
    tokens = pattern.split(clean_src)

    for token in tokens:
        if not token:
            continue
        
        is_bold = is_bold_override if is_bold_override is not None else False
        is_italic = is_italic_override if is_italic_override is not None else False
        font_family = font_name
        current_size = font_size
        run_text = token

        if token.startswith('***') and token.endswith('***'):
            run_text = token[3:-3]
            is_bold = True
            is_italic = True
        elif token.startswith('**') and token.endswith('**'):
            run_text = token[2:-2]
            is_bold = True
        elif token.startswith('*') and token.endswith('*'):
            run_text = token[1:-1]
            is_italic = True
        elif token.startswith('`') and token.endswith('`'):
            run_text = token[1:-1]
            font_family = 'Consolas'
            current_size = Pt(11.5) if font_size.pt > 12 else Pt(11)
        elif token.startswith('$') and token.endswith('$'):
            run_text = clean_math_syntax(token[1:-1])
            is_italic = True
        elif token.startswith('[') and '](' in token and token.endswith(')'):
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', token)
            if m:
                label = m.group(1)
                url = m.group(2)
                # Nếu là URL trích dẫn trùng lặp, chỉ hiển thị label sạch sẽ
                run_text = label if label != url else url

        # Phục hồi ký tự dấu sao chuẩn
        run_text = run_text.replace('∗', '*')

        run = paragraph.add_run(run_text)
        run.font.name = font_family
        run.font.size = current_size
        run.bold = is_bold
        run.italic = is_italic
        run.font.color.rgb = RGBColor(0, 0, 0)


def add_heading_styled(doc: docx.Document, text: str, level: int):
    """Thêm tiêu đề với định dạng chuẩn mực học thuật, không thụt đầu dòng."""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing = 1.3
    
    # Dọn sạch các ký tự markdown thô trong tiêu đề
    clean_text = text.strip()
    clean_text = re.sub(r'^\#+\s*', '', clean_text)
    clean_text = clean_text.replace('**', '').replace('`', '')
    
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(clean_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    elif level == 2:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(clean_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    elif level == 3:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(clean_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(clean_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.bold = True
        run.italic = True
        run.font.color.rgb = RGBColor(0, 0, 0)


def calculate_col_widths(num_cols: int) -> list:
    """Tính toán chiều rộng cột phù hợp với khổ giấy 16.0cm khả dụng."""
    total_w = 16.0  # cm
    if num_cols == 3:
        return [Cm(4.5), Cm(6.0), Cm(5.5)]
    elif num_cols == 4:
        return [Cm(3.8), Cm(4.0), Cm(4.2), Cm(4.0)]
    elif num_cols == 5:
        return [Cm(3.5), Cm(3.5), Cm(2.2), Cm(2.2), Cm(4.6)]
    elif num_cols == 6:
        return [Cm(1.8), Cm(3.2), Cm(3.2), Cm(2.4), Cm(2.4), Cm(3.0)]
    elif num_cols == 8:
        return [Cm(1.1), Cm(2.7), Cm(2.7), Cm(1.9), Cm(1.9), Cm(1.9), Cm(1.9), Cm(1.9)]
    else:
        w_each = total_w / num_cols
        return [Cm(w_each)] * num_cols


def add_table_styled(doc: docx.Document, header: list, rows: list, caption: str = None):
    """Xây dựng bảng học thuật chuẩn mực: caption phía trên, viền đơn đen, padding rộng rãi."""
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cp.paragraph_format.space_before = Pt(12)
        cp.paragraph_format.space_after = Pt(4)
        cp.paragraph_format.first_line_indent = Inches(0)
        
        caption_clean = caption.replace('**', '').replace(r'\*', '*').strip()
        c_run = cp.add_run(caption_clean)
        c_run.font.name = 'Times New Roman'
        c_run.font.size = Pt(13)
        c_run.bold = True
        c_run.font.color.rgb = RGBColor(0, 0, 0)

    num_cols = len(header)
    col_widths = calculate_col_widths(num_cols)

    table = doc.add_table(rows=len(rows) + 1, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Thiết lập đường viền đơn đen mỏng chuẩn mực (sz=6 ~ 0.75pt)
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

    # Padding nội bộ của ô (trên/dưới 120 dxa ~ 6pt, trái/phải 150 dxa ~ 7.5pt)
    tblCellMar = parse_xml(
        f'<w:tblCellMar {nsdecls("w")}>'
        f'<w:top w:w="120" w:type="dxa"/>'
        f'<w:bottom w:w="120" w:type="dxa"/>'
        f'<w:left w:w="150" w:type="dxa"/>'
        f'<w:right w:w="150" w:type="dxa"/>'
        f'</w:tblCellMar>'
    )
    tblPr.append(tblCellMar)

    # Header Row
    hdr_cells = table.rows[0].cells
    hdr_tr = table.rows[0]._tr.get_or_add_trPr()
    hdr_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_tr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for col_idx, col_name in enumerate(header):
        cell = hdr_cells[col_idx]
        cell.width = col_widths[col_idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        # Shading nhẹ cho hàng tiêu đề (#F2F2F2)
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="F2F2F2"/>')
        cell._tc.get_or_add_tcPr().append(shd)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        
        parse_inline_formatting(p, col_name, font_size=Pt(12), is_bold_override=True)

    # Data Rows
    for row_idx, row_data in enumerate(rows):
        row_cells = table.rows[row_idx + 1].cells
        r_tr = table.rows[row_idx + 1]._tr.get_or_add_trPr()
        r_tr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for col_idx, cell_value in enumerate(row_data):
            if col_idx < len(row_cells):
                cell = row_cells[col_idx]
                cell.width = col_widths[col_idx]
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
                
                # Căn giữa nếu là số liệu/chỉ số, căn đều/trái nếu là văn bản
                clean_check = cell_value.replace('**', '').replace(r'\*', '*').strip()
                if (len(clean_check) < 18 and any(c.isdigit() for c in clean_check)) or clean_check in ['N/A*', 'N/A', '—', '---', 'True', 'False', 'Hoàn thành']:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                parse_inline_formatting(p, cell_value, font_size=Pt(12))

    # Spacing sau bảng
    after_p = doc.add_paragraph()
    after_p.paragraph_format.space_before = Pt(0)
    after_p.paragraph_format.space_after = Pt(4)
    after_p.paragraph_format.first_line_indent = Inches(0)


def convert_lines_to_document(lines: list, doc: docx.Document, is_combined: bool = False):
    """Xử lý danh sách các dòng markdown và gắn vào Document docx."""
    in_table = False
    table_header = []
    table_rows = []
    pending_table_caption = None

    in_code_block = False
    code_block_lines = []

    in_references_section = False

    i = 0
    num_lines = len(lines)

    while i < num_lines:
        line = lines[i].rstrip('\r\n')
        line_stripped = line.strip()

        # 1. Bỏ qua dòng kẻ ngang markdown
        if line_stripped in ['---', '***', '___']:
            i += 1
            continue

        # 2. Xử lý khối Code block
        if line_stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                cp = doc.add_paragraph()
                cp.paragraph_format.left_indent = Inches(0.4)
                cp.paragraph_format.right_indent = Inches(0.2)
                cp.paragraph_format.first_line_indent = Inches(0)
                cp.paragraph_format.line_spacing = 1.15
                cp.paragraph_format.space_before = Pt(4)
                cp.paragraph_format.space_after = Pt(6)
                
                pPr = cp._p.get_or_add_pPr()
                pPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="F8F9FA"/>'))
                
                code_text = "\n".join(code_block_lines)
                c_run = cp.add_run(code_text)
                c_run.font.name = 'Consolas'
                c_run.font.size = Pt(10.5)
                code_block_lines = []
            else:
                in_code_block = True
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # 3. Xử lý Bảng Markdown
        if line_stripped.startswith('|') and '|' in line_stripped[1:]:
            if re.match(r'^\|[\s\:\-\|]+$', line_stripped):
                i += 1
                continue
            
            cells = [c.strip() for c in line_stripped.split('|')[1:-1]]
            
            if not in_table:
                in_table = True
                table_header = cells
                table_rows = []
            else:
                table_rows.append(cells)
            
            i += 1
            continue
        else:
            if in_table:
                add_table_styled(doc, table_header, table_rows, pending_table_caption)
                in_table = False
                table_header = []
                table_rows = []
                pending_table_caption = None

        # 4. Nhận diện Caption bảng tiềm năng ở dòng trước
        if (line_stripped.startswith('**Bảng') or line_stripped.startswith('Bảng')) and ('**' in line_stripped or ':' in line_stripped or '.' in line_stripped):
            nxt = i + 1
            while nxt < num_lines and not lines[nxt].strip():
                nxt += 1
            if nxt < num_lines and lines[nxt].strip().startswith('|'):
                pending_table_caption = line_stripped
                i += 1
                continue

        # 5. Dòng trống
        if not line_stripped:
            i += 1
            continue

        # 6. Khối công thức toán học độc lập $$ ... $$
        if line_stripped.startswith('$$') and line_stripped.endswith('$$') and len(line_stripped) > 4:
            math_content = clean_math_syntax(line_stripped[2:-2])
            mp = doc.add_paragraph()
            mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            mp.paragraph_format.first_line_indent = Inches(0)
            mp.paragraph_format.space_before = Pt(6)
            mp.paragraph_format.space_after = Pt(6)
            m_run = mp.add_run(math_content)
            m_run.font.name = 'Times New Roman'
            m_run.font.size = Pt(13)
            m_run.italic = True
            i += 1
            continue

        # 7. Nhận diện phần TÀI LIỆU THAM KHẢO
        if 'TÀI LIỆU THAM KHẢO' in line_stripped.upper():
            in_references_section = True
            add_heading_styled(doc, "TÀI LIỆU THAM KHẢO", level=1)
            i += 1
            continue

        # 8. Xử lý các mục trong phần Tài liệu tham khảo
        if in_references_section and (line_stripped.startswith('* **[') or line_stripped.startswith('[') or re.match(r'^\*?\s*\[\d+\]', line_stripped)):
            rp = doc.add_paragraph()
            rp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            rp.paragraph_format.left_indent = Inches(0.4)
            rp.paragraph_format.first_line_indent = Inches(-0.4)
            rp.paragraph_format.space_before = Pt(2)
            rp.paragraph_format.space_after = Pt(4)
            rp.paragraph_format.line_spacing = 1.3
            
            clean_ref = re.sub(r'^\*\s*', '', line_stripped)
            parse_inline_formatting(rp, clean_ref, font_size=Pt(12))
            i += 1
            continue

        # 9. Tiêu đề (Headings)
        if line_stripped.startswith('#'):
            heading_match = re.match(r'^(#+)\s*(.*)$', line_stripped)
            if heading_match:
                level = len(heading_match.group(1))
                h_text = heading_match.group(2)
                add_heading_styled(doc, h_text, level=level)
                i += 1
                continue

        # 10. Danh sách gạch đầu dòng (Bullet lists: *, -)
        if line_stripped.startswith('* ') or line_stripped.startswith('- '):
            bp = doc.add_paragraph()
            bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            bp.paragraph_format.left_indent = Inches(0.35)
            bp.paragraph_format.first_line_indent = Inches(-0.2)
            bp.paragraph_format.space_before = Pt(1)
            bp.paragraph_format.space_after = Pt(3)
            bp.paragraph_format.line_spacing = 1.5

            b_symbol = bp.add_run("• ")
            b_symbol.font.name = 'Times New Roman'
            b_symbol.font.size = Pt(13)
            b_symbol.bold = True

            item_text = line_stripped[2:].strip()
            parse_inline_formatting(bp, item_text, font_size=Pt(13))
            i += 1
            continue

        # 11. Danh sách có thứ tự (Numbered lists: 1., 2., ...)
        num_match = re.match(r'^(\d+[\.\)])\s*(.*)$', line_stripped)
        if num_match:
            np = doc.add_paragraph()
            np.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            np.paragraph_format.left_indent = Inches(0.35)
            np.paragraph_format.first_line_indent = Inches(-0.2)
            np.paragraph_format.space_before = Pt(1)
            np.paragraph_format.space_after = Pt(3)
            np.paragraph_format.line_spacing = 1.5

            prefix = num_match.group(1) + " "
            n_symbol = np.add_run(prefix)
            n_symbol.font.name = 'Times New Roman'
            n_symbol.font.size = Pt(13)
            n_symbol.bold = True

            item_text = num_match.group(2).strip()
            parse_inline_formatting(np, item_text, font_size=Pt(13))
            i += 1
            continue

        # 12. Blockquotes (Ghi chú / Alert: > )
        if line_stripped.startswith('>'):
            qp = doc.add_paragraph()
            qp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            qp.paragraph_format.left_indent = Inches(0.4)
            qp.paragraph_format.first_line_indent = Inches(0)
            qp.paragraph_format.space_before = Pt(4)
            qp.paragraph_format.space_after = Pt(6)
            qp.paragraph_format.line_spacing = 1.3
            
            quote_text = line_stripped.lstrip('>').strip()
            quote_text = re.sub(r'^\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*', 'Ghi chú: ', quote_text)
            
            parse_inline_formatting(qp, quote_text, font_size=Pt(12.5), is_italic_override=True)
            i += 1
            continue

        # 13. Đoạn văn thông thường (Normal Body Paragraph)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Inches(0.5)  # Thụt đầu dòng 1.27cm
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        
        parse_inline_formatting(p, line_stripped, font_size=Pt(13))
        i += 1

    if in_table:
        add_table_styled(doc, table_header, table_rows, pending_table_caption)


def convert_markdown_to_docx(md_path: str, docx_path: str):
    """Chuyển đổi một file markdown riêng lẻ sang docx."""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = docx.Document()
    setup_document_styles(doc)
    convert_lines_to_document(lines, doc)
    doc.save(docx_path)
    print(f"-> Xuất bản thành công: {docx_path}")


def create_combined_docx(md_files: list, combined_docx_path: str):
    """Tạo file docx hợp nhất toàn bộ Chương 2 và Chương 3 theo đúng thứ tự logic."""
    doc = docx.Document()
    setup_document_styles(doc)

    for idx, md_path in enumerate(md_files):
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Nếu không phải file cuối cùng, loại bỏ phần TÀI LIỆU THAM KHẢO để tránh lặp lại
        if idx < len(md_files) - 1:
            filtered_lines = []
            skip_ref = False
            for l in lines:
                if 'TÀI LIỆU THAM KHẢO' in l.upper():
                    skip_ref = True
                    continue
                if skip_ref and l.strip().startswith('#'):
                    skip_ref = False
                if not skip_ref:
                    filtered_lines.append(l)
            lines_to_add = filtered_lines
        else:
            lines_to_add = lines

        convert_lines_to_document(lines_to_add, doc, is_combined=True)

    doc.save(combined_docx_path)
    print(f"-> Xuất bản file HỢP NHẤT thành công: {combined_docx_path}")


def main():
    base_docs_dir = r"c:\Users\luuth\NCKH\Benchmark\docs"
    
    tasks = [
        ("paper_section_2_2_2_3_2_5.md", "paper_section_2_2_2_3_2_5.docx"),
        ("paper_section_2_4.md", "paper_section_2_4.docx"),
        ("paper_section_3_1_3_2.md", "paper_section_3_1_3_2.docx"),
        ("paper_section_3_3.md", "paper_section_3_3.docx"),
        ("paper_section_3_9_3_10_conclusion.md", "paper_section_3_9_3_10_conclusion.docx")
    ]

    print("==========================================================")
    print("TIẾN HÀNH CHUYỂN ĐỔI 5 FILE MARKDOWN SANG DOCX CHUẨN MINH:")
    print("==========================================================")

    md_file_paths = []
    for md_name, docx_name in tasks:
        md_file = os.path.join(base_docs_dir, md_name)
        docx_file = os.path.join(base_docs_dir, docx_name)
        
        if not os.path.exists(md_file):
            print(f"LỖI: Không tìm thấy file nguồn {md_file}")
            continue
            
        md_file_paths.append(md_file)
        print(f"Đang xử lý: {md_name} ...")
        convert_markdown_to_docx(md_file, docx_file)

    # Tạo thêm file hợp nhất toàn văn để thuận tiện cho tác giả đọc liền mạch
    combined_file = os.path.join(base_docs_dir, "paper_sections_combined_ch2_ch3.docx")
    print(f"\nĐang tạo file tài liệu HỢP NHẤT Chương 2 & 3: {os.path.basename(combined_file)} ...")
    create_combined_docx(md_file_paths, combined_file)

    print("==========================================================")
    print("HOÀN TẤT CHUYỂN ĐỔI TOÀN BỘ 5 FILE DOCX VÀ 1 FILE HỢP NHẤT!")
    print("==========================================================")


if __name__ == "__main__":
    main()
