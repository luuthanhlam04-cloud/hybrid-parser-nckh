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
    
    # Left border via XML
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
    # Regex parse bold, code, math
    # Split by bold **text**
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
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_table = False
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\r\n')
        
        # Check table
        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_lines.append(line.strip())
            i += 1
            continue
        elif table_lines:
            # Process table
            render_table(doc, table_lines)
            table_lines = []
            
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
            
        if stripped == '---':
            # Horizontal divider
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run("―" * 55)
            run.font.name = "Times New Roman"
            run.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE0)
            run.font.size = Pt(9)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1
            continue
            
        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[2:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)
            i += 1
            continue
            
        if stripped.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[3:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
            i += 1
            continue
            
        if stripped.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[4:])
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)
            i += 1
            continue
            
        if stripped.startswith('> '):
            callout_text = stripped[2:]
            # Gather consecutive quote lines
            while i + 1 < len(lines) and lines[i+1].strip().startswith('> '):
                i += 1
                callout_text += "\n" + lines[i].strip()[2:]
            add_callout(doc, callout_text)
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
            content = re.sub(r'^\d+\.\s', '', stripped)
            format_run_text(p, content)
            i += 1
            continue
            
        # Normal paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        # Check if it's spoken text in quotes
        is_spoken = stripped.startswith('*"') and stripped.endswith('*"')
        clean_text = stripped
        if is_spoken:
            p.paragraph_format.left_indent = Inches(0.15)
            format_run_text(p, clean_text, default_size=11, is_italic=True, default_color=RGBColor(0x1A, 0x36, 0x5D))
        else:
            format_run_text(p, clean_text, default_size=11)
            
        i += 1
        
    if table_lines:
        render_table(doc, table_lines)
        
    doc.save(docx_path)
    print(f"[+] Successfully saved Word document to: {docx_path}")

def render_table(doc, lines):
    # Parse markdown table
    rows = []
    for l in lines:
        if re.match(r'^\|[\s\-:|]+\|$', l):
            continue # separator line
        cells = [c.strip() for c in l.strip('|').split('|')]
        rows.append(cells)
        
    if not rows:
        return
        
    num_cols = max(len(r) for r in rows)
    num_rows = len(rows)
    
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    col_widths = [Inches(0.7), Inches(0.9), Inches(0.7), Inches(2.2), Inches(1.8), Inches(1.7)]
    
    for r_idx, row in enumerate(rows):
        is_header = (r_idx == 0)
        table_row = tbl.rows[r_idx]
        
        # CantSplit row
        trPr = table_row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            
        for c_idx, cell_value in enumerate(row):
            if c_idx >= num_cols:
                continue
            cell = table_row.cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            
            # Widths
            if c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
                
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            
            # Replace <br> with newline
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
                if c_idx in [0, 1, 2]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                format_run_text(p, clean_cell, default_size=9.5)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

if __name__ == "__main__":
    md_file = r"c:\Users\luuth\NCKH\Benchmark\docs\kich_ban_thuyet_trinh_15p.md"
    docx_file1 = r"c:\Users\luuth\NCKH\Benchmark\kichbanthuyettrinh.docx"
    docx_file2 = r"c:\Users\luuth\NCKH\Benchmark\kichbanthuyettrinh_storytelling.docx"
    docx_file3 = r"c:\Users\luuth\NCKH\Benchmark\kichbanthuyettrinh_chuan_bao_ve.docx"
    
    build_docx_from_md(md_file, docx_file2)
    build_docx_from_md(md_file, docx_file3)
    try:
        build_docx_from_md(md_file, docx_file1)
    except Exception as e:
        print(f"[*] Note: kichbanthuyettrinh.docx is currently open in Word ({e}), successfully saved to kichbanthuyettrinh_storytelling.docx and kichbanthuyettrinh_chuan_bao_ve.docx.")


