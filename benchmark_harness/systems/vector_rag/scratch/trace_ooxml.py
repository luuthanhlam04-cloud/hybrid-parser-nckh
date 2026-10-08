import os
import json
import zipfile
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from xml.etree import ElementTree as ET

NS = {
    "w":  "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r":  "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

docx_path = "datasets/raw_laws/Luat_dat_dai_chuong_3.docx"

with zipfile.ZipFile(docx_path, "r") as zf:
    doc_xml = zf.read("word/document.xml")
    num_xml = zf.read("word/numbering.xml") if "word/numbering.xml" in zf.namelist() else None

root = ET.fromstring(doc_xml)
body = root.find(".//w:body", NS)

print("=== INSPECTING DOCUMENT.XML ===")
for idx, para in enumerate(body.findall("w:p", NS)):
    # Text
    text_parts = []
    for run in para.findall(".//w:r", NS):
        for t_el in run.findall("w:t", NS):
            text_parts.append(t_el.text or "")
    text = "".join(text_parts).strip()
    
    if not text:
        continue
        
    # Numbering
    ppr = para.find("w:pPr", NS)
    numPr = ppr.find("w:numPr", NS) if ppr is not None else None
    
    if numPr is not None:
        numId_el = numPr.find("w:numId", NS)
        ilvl_el = numPr.find("w:ilvl", NS)
        
        numId = int(numId_el.attrib.get(f"{{{NS['w']}}}val", 0)) if numId_el is not None else 0
        ilvl = int(ilvl_el.attrib.get(f"{{{NS['w']}}}val", 0)) if ilvl_el is not None else 0
        
        if "Tổ chức trong nước là pháp nhân mới được hình thành thông qua việc chia" in text:
            print(f"FOUND DIEU 28 (p6776) [idx={idx}]:")
            print(f"  numId={numId}, ilvl={ilvl}")
            print(f"  text='{text[:50]}...'")
            
        if "Cho thuê lại quyền sử dụng đất theo hình thức trả tiền thuê đất hằng năm" in text:
            print(f"FOUND DIEU 34 / 41 (đ/e) [idx={idx}]:")
            print(f"  numId={numId}, ilvl={ilvl}")
            print(f"  text='{text[:50]}...'")

if num_xml is not None:
    print("\n=== INSPECTING NUMBERING.XML ===")
    num_root = ET.fromstring(num_xml)
    
    # 1. Map numId -> abstractNumId
    num_to_abstract = {}
    for num in num_root.findall(".//w:num", NS):
        num_id = num.attrib.get(f"{{{NS['w']}}}numId")
        ab_id_el = num.find("w:abstractNumId", NS)
        if ab_id_el is not None:
            ab_id = ab_id_el.attrib.get(f"{{{NS['w']}}}val")
            num_to_abstract[num_id] = ab_id
            
    # 2. Extract abstractNum definitions
    abstract_nums = {}
    for ab in num_root.findall(".//w:abstractNum", NS):
        ab_id = ab.attrib.get(f"{{{NS['w']}}}abstractNumId")
        levels = {}
        for lvl in ab.findall("w:lvl", NS):
            ilvl = lvl.attrib.get(f"{{{NS['w']}}}ilvl")
            
            start_el = lvl.find("w:start", NS)
            numfmt_el = lvl.find("w:numFmt", NS)
            lvltext_el = lvl.find("w:lvlText", NS)
            lvlrestart_el = lvl.find("w:lvlRestart", NS)
            
            levels[ilvl] = {
                "start": start_el.attrib.get(f"{{{NS['w']}}}val") if start_el is not None else None,
                "numFmt": numfmt_el.attrib.get(f"{{{NS['w']}}}val") if numfmt_el is not None else None,
                "lvlText": lvltext_el.attrib.get(f"{{{NS['w']}}}val") if lvltext_el is not None else None,
                "lvlRestart": lvlrestart_el.attrib.get(f"{{{NS['w']}}}val") if lvlrestart_el is not None else "Not Set"
            }
        abstract_nums[ab_id] = levels
        
    print("Num ID -> Abstract Num ID mappings:")
    for nid, abid in num_to_abstract.items():
        if nid in ['7', '15', '21']: # specific numIds we found
            print(f"  numId={nid} -> abstractNumId={abid}")
            print(f"    levels={abstract_nums.get(abid)}")
            
    # Print num overrides
    print("\nNum Overrides (w:num > w:lvlOverride):")
    for num in num_root.findall(".//w:num", NS):
        num_id = num.attrib.get(f"{{{NS['w']}}}numId")
        if num_id not in ['7', '15', '21']: continue
        for lvl_over in num.findall("w:lvlOverride", NS):
            ilvl = lvl_over.attrib.get(f"{{{NS['w']}}}ilvl")
            start_override = lvl_over.find("w:startOverride", NS)
            val = start_override.attrib.get(f"{{{NS['w']}}}val") if start_override is not None else None
            print(f"  numId={num_id} ilvl={ilvl} -> startOverride={val}")
            
    # Finally, simulate the numbering counting!
    counters = {}
    print("\nSimulating Counter for numId=21 (Dieu 28):")
    for idx, para in enumerate(body.findall("w:p", NS)):
        text_parts = []
        for run in para.findall(".//w:r", NS):
            for t_el in run.findall("w:t", NS):
                text_parts.append(t_el.text or "")
        text = "".join(text_parts).strip()
        if not text: continue
        ppr = para.find("w:pPr", NS)
        numPr = ppr.find("w:numPr", NS) if ppr is not None else None
        if numPr is not None:
            numId_el = numPr.find("w:numId", NS)
            ilvl_el = numPr.find("w:ilvl", NS)
            numId = int(numId_el.attrib.get(f"{{{NS['w']}}}val", 0)) if numId_el is not None else 0
            ilvl = int(ilvl_el.attrib.get(f"{{{NS['w']}}}val", 0)) if ilvl_el is not None else 0
            
            if numId in [7, 15, 21]:
                if numId not in counters: counters[numId] = {}
                if ilvl not in counters[numId]: counters[numId][ilvl] = 0
                counters[numId][ilvl] += 1
                count = counters[numId][ilvl]
                print(f"  [idx={idx}] numId={numId} ilvl={ilvl} -> count={count}, text='{text[:30]}...'")

