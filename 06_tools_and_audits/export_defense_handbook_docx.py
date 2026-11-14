# -*- coding: utf-8 -*-
import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_callout(doc, text_content):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text_content)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
    
    pPr = p._p.get_or_add_pPr()
    pbdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:left w:val="single" w:sz="18" w:space="12" w:color="0A2540"/>
        </w:pBdr>
    ''')
    pPr.append(pbdr)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F7FAFC"/>')
    pPr.append(shd)

def format_run_text(p, text_segment, default_size=11, is_italic=False, default_color=None):
    text_segment = text_segment.replace('\x07', 'alpha')
    parts = re.split(r'(\*\*.*?\*\*)', text_segment)
    for part in parts:
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            subparts = re.split(r'(`.*?`)', part[2:-2])
            for sp in subparts:
                run = p.add_run()
                run.font.name = "Times New Roman"
                run.font.size = Pt(default_size)
                run.font.bold = True
                run.font.italic = is_italic
                if sp.startswith('`') and sp.endswith('`') and len(sp) >= 2:
                    run.text = sp[1:-1]
                    run.font.name = "Consolas"
                    run.font.color.rgb = RGBColor(0x9B, 0x2C, 0x2C)
                else:
                    run.text = sp
                    if default_color:
                        run.font.color.rgb = default_color
        else:
            subparts = re.split(r'(`.*?`)', part)
            for sp in subparts:
                run = p.add_run()
                run.font.name = "Times New Roman"
                run.font.size = Pt(default_size)
                run.font.italic = is_italic
                if sp.startswith('`') and sp.endswith('`') and len(sp) >= 2:
                    run.text = sp[1:-1]
                    run.font.name = "Consolas"
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0x9B, 0x2C, 0x2C)
                else:
                    run.text = sp
                    if default_color:
                        run.font.color.rgb = default_color

def build_docx_from_md(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = docx.Document()
    
    # Page Setup: Normal Margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    lines = md_text.splitlines()
    
    i = 0
    in_callout = False
    callout_lines = []
    
    table_lines = []
    in_table = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check callout block >
        if stripped.startswith('>'):
            in_callout = True
            c_text = re.sub(r'^>\s?', '', stripped)
            callout_lines.append(c_text)
            i += 1
            continue
        else:
            if in_callout:
                add_callout(doc, "\n".join(callout_lines))
                in_callout = False
                callout_lines = []
                
        # Check table line |
        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            table_lines.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                render_table(doc, table_lines)
                in_table = False
                table_lines = []
                
        if not stripped:
            i += 1
            continue
            
        if stripped.startswith('# '):
            h = doc.add_heading(level=1)
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(8)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(stripped[2:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)
            i += 1
            continue
            
        if stripped.startswith('## '):
            h = doc.add_heading(level=2)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(stripped[3:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
            i += 1
            continue
            
        if stripped.startswith('### '):
            h = doc.add_heading(level=3)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(stripped[4:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
            i += 1
            continue

        if stripped.startswith('#### '):
            h = doc.add_heading(level=4)
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(3)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(stripped[5:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
            i += 1
            continue
            
        if stripped == '---':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            pPr = p._p.get_or_add_pPr()
            pbdr = parse_xml(f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="6" w:space="1" w:color="CBD5E0"/>
                </w:pBdr>
            ''')
            pPr.append(pbdr)
            i += 1
            continue
            
        if stripped.startswith('* ') or stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            format_run_text(p, stripped[2:])
            i += 1
            continue
            
        if re.match(r'^\d+\.\s', stripped):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            content_str = re.sub(r'^\d+\.\s', '', stripped)
            format_run_text(p, content_str)
            i += 1
            continue
            
        # Normal paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        is_spoken = stripped.startswith('*"') and stripped.endswith('*"')
        clean_text = stripped
        if is_spoken:
            p.paragraph_format.left_indent = Inches(0.2)
            format_run_text(p, clean_text, default_size=11, is_italic=True, default_color=RGBColor(0x1A, 0x36, 0x5D))
        else:
            format_run_text(p, clean_text, default_size=11)
            
        i += 1
        
    if table_lines:
        render_table(doc, table_lines)
        
    doc.save(docx_path)
    print(f"[+] Successfully saved Word handbook to: {docx_path}")

def render_table(doc, lines):
    rows = []
    for l in lines:
        if re.match(r'^\|[\s\-:|]+\|$', l):
            continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        rows.append(cells)
        
    if not rows:
        return
        
    num_cols = max(len(r) for r in rows)
    num_rows = len(rows)
    
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    for r_idx, row in enumerate(rows):
        is_header = (r_idx == 0)
        table_row = tbl.rows[r_idx]
        
        trPr = table_row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            
        for c_idx, cell_value in enumerate(row):
            if c_idx >= num_cols:
                continue
            cell = table_row.cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            
            clean_cell = cell_value.replace('<br>', '\n')
            
            if is_header:
                set_cell_background(cell, "0A2540")
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(clean_cell)
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
                set_cell_background(cell, bg)
                if c_idx in [0, 1]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                format_run_text(p, clean_cell, default_size=9.5)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

if __name__ == "__main__":
    md_file = r"c:\Users\luuth\NCKH\Benchmark\docs\cam_nang_chuyen_sau_chuan_bi_phan_bien.md"
    docx_file = r"c:\Users\luuth\NCKH\Benchmark\cam_nang_chuyen_sau_chuan_bi_phan_bien.docx"
    build_docx_from_md(md_file, docx_file)
