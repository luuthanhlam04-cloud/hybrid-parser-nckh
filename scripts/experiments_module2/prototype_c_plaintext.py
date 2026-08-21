# -*- coding: utf-8 -*-
"""
prototype_c_plaintext.py
Prototype C: So sanh DOCX vs Plain Text parsing.
Khong co Style signal - chi dung Regex + Context (Lop 2 + Lop 3).
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/regex_parser')))

from parser import LegalParser
from collections import Counter

# --- Baseline da biet: DOCX (Prototype B)
BASELINE_DOCX = {
    "CHAPTER": 1,
    "SECTION": 5,
    "ARTICLE": 23,
    "CLAUSE":  185,
    "POINT":   8,
    "total":   222,
}

# --- Chay plain text mode
print("=" * 56)
print("PROTOTYPE C: Plain Text Mode (khong co Style signal)")
print("=" * 56)

txt_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'luat_ch3_output.txt')
p = LegalParser(
    law_prefix="ldd-2024-txt",
    law_code="59/2024/QH15",
    source_doc="luat_ch3_output.txt"
)
result = p.parse_text(txt_path)

type_counts = Counter(n["type"] for n in result.nodes)

print(f"\n{'Node Type':<12} | {'TXT':>6} | {'DOCX (B)':>8} | {'Delta':>8} | {'Status'}")
print("-" * 56)

all_types = ["CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT"]
for t in all_types:
    txt_n  = type_counts.get(t, 0)
    docx_n = BASELINE_DOCX.get(t, 0)
    delta  = txt_n - docx_n
    if docx_n == 0:
        pct = "N/A"
    else:
        pct = f"{txt_n/docx_n*100:.0f}%"
    status = "OK" if delta == 0 else ("OVER" if delta > 0 else "MISS")
    print(f"{t:<12} | {txt_n:>6} | {docx_n:>8} | {delta:>+8} | {pct} {status}")

print("-" * 56)
txt_total  = len(result.nodes)
docx_total = BASELINE_DOCX["total"]
print(f"{'TOTAL':<12} | {txt_total:>6} | {docx_total:>8} | {txt_total-docx_total:>+8}")
print(f"\northan_count : {len(result.orphans)}")
print(f"gap_count    : {len(result.gaps)}")

# --- Sample CLAUSE
print("\n=== CLAUSE sample (first 5) ===")
clauses = [n for n in result.nodes if n["type"] == "CLAUSE"]
for n in clauses[:5]:
    print(f"  [{n['id']}]")
    print(f"  text={repr(n['text'][:80])}")

# --- Sample POINT
print("\n=== POINT sample (all) ===")
points = [n for n in result.nodes if n["type"] == "POINT"]
if not points:
    print("  [NONE DETECTED]")
for n in points:
    print(f"  [{n['id']}] text={repr(n['text'][:80])}")

# --- FP analysis: CLAUSE co the bi bao nhieu dang FP?
print("\n=== FP RISK: CLAUSE detected in TXT ===")
print("CLAUSE trong plain text se bi FP cao vi khong co List Paragraph style.")
print(f"Total CLAUSE TXT = {type_counts.get('CLAUSE', 0)}")
print(f"Baseline DOCX    = {BASELINE_DOCX['CLAUSE']}")

# --- Luu output
out_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'legal_nodes_ch3_txt.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result.nodes, f, ensure_ascii=False, indent=2)
print(f"\nSaved -> legal_nodes_ch3_txt.json ({len(result.nodes)} nodes)")
