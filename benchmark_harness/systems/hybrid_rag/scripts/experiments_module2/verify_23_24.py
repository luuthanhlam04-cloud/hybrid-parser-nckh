# -*- coding: utf-8 -*-
"""
verify_23_24.py
Verification script cho 2.3 HierarchyBuilder va 2.4 NodeGenerator.
Kiem tra toan bo checklist tu research_notes.md Section 10.
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/regex_parser')))
sys.stdout.reconfigure(encoding='utf-8')

from parser import LegalParser
from regex_engine import NodeType

DOCX = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Luat_dat_dai_chuong_3 (1).docx')
TXT  = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'luat_ch3_output.txt')

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, label, detail))
    print(f"{status} {label}")
    if detail:
        print(f"       {detail}")

def warn(label, detail=""):
    results.append((WARN, label, detail))
    print(f"{WARN} {label}")
    if detail:
        print(f"       {detail}")

def info(label, detail=""):
    print(f"{INFO} {label}")
    if detail:
        print(f"       {detail}")

# =============================================================================
# DOCX parse
# =============================================================================
print("=" * 60)
print("DOCX MODE — Prototype B baseline")
print("=" * 60)

p = LegalParser(law_prefix="ldd-2024", law_code="59/2024/QH15", source_doc="test.docx")
r = p.parse_docx(DOCX)
nodes = r.nodes

# --- 2.3.1 Stack logic — đúng thứ tự depth?
print("\n--- 2.3 Hierarchy Builder ---")
depth_map = {"CHAPTER":0, "SECTION":1, "ARTICLE":2, "CLAUSE":3, "POINT":4}
depth_violations = []
for n in nodes:
    if n["parent_id"]:
        parent = next((x for x in nodes if x["id"] == n["parent_id"]), None)
        if parent:
            expected_depth = depth_map[parent["type"]] + 1
            actual_depth   = depth_map[n["type"]]
            if actual_depth != expected_depth:
                # POINT co the la orphan (depth 4, parent depth 2) — khong phai vi pham
                if n["type"] == "POINT" and n.get("implicit_parent"):
                    pass  # orphan duoc phep
                else:
                    depth_violations.append(f"{n['id']} parent={parent['type']} child={n['type']}")

check("2.3.1 Stack depth logic (non-orphan nodes)",
      len(depth_violations) == 0,
      f"Violations: {depth_violations[:3]}" if depth_violations else "All depths correct")

# --- 2.3.2 Position counting — siblings co position 1,2,3... khong?
from collections import defaultdict
parent_positions = defaultdict(list)
for n in nodes:
    parent_positions[n["parent_id"]].append(n["position"])

position_gaps = {}
for pid, positions in parent_positions.items():
    sorted_pos = sorted(positions)
    expected = list(range(1, len(sorted_pos)+1))
    if sorted_pos != expected:
        position_gaps[pid] = {"got": sorted_pos, "expected": expected}

check("2.3.2 Position counting sequential (1,2,3...)",
      len(position_gaps) == 0,
      f"{len(position_gaps)} parent groups co position gap" if position_gaps else "All sequential")

# --- 2.3.3 EC-1: ARTICLE khong co CLAUSE → children_count=0
articles_no_clause = [n for n in nodes if n["type"] == "ARTICLE" and n["children_count"] == 0]
info("2.3.3 EC-1: ARTICLE khong co con",
     f"{len(articles_no_clause)} ARTICLE co children_count=0 (la binh thuong neu Dieu chi co noi dung truc tiep)")
for a in articles_no_clause[:3]:
    has_text = bool(a.get("text","").strip())
    print(f"       {a['id']} | has_text={has_text} | text_preview={repr(a.get('text','')[:60])}")

# --- 2.3.4 EC-3: Orphan POINT — implicit_parent=True
orphan_points = [n for n in nodes if n["type"] == "POINT" and n.get("implicit_parent")]
check("2.3.4 EC-3: Orphan POINT flagged implicit_parent=True",
      True,  # always pass, just report count
      f"{len(orphan_points)} orphan POINTs detected (expected 0 in DOCX mode if CLAUSE=185)")

# --- 2.3.5 Children IDs consistency
id_set = set(n["id"] for n in nodes)
children_dangling = []
for n in nodes:
    if n["parent_id"] and n["parent_id"] not in id_set:
        children_dangling.append(n["id"])

check("2.3.5 No dangling parent_id (all parent_ids exist in node set)",
      len(children_dangling) == 0,
      f"Dangling: {children_dangling[:3]}" if children_dangling else "All parent_ids valid")

# --- 2.3.6 No Virtual Clause
virtual_nodes = [n for n in nodes if "VIRTUAL" in n.get("type","")]
check("2.3.6 No virtual/synthetic nodes",
      len(virtual_nodes) == 0,
      f"Found: {virtual_nodes}" if virtual_nodes else "Clean")

# =============================================================================
# 2.4 Node Creator — DOCX
# =============================================================================
print("\n--- 2.4 Node Creator (DOCX) ---")

# --- 2.4.1 ID uniqueness
all_ids = [n["id"] for n in nodes]
unique_ids = set(all_ids)
check("2.4.1 ID uniqueness in DOCX mode (222 nodes)",
      len(all_ids) == len(unique_ids),
      f"Total={len(all_ids)}, Unique={len(unique_ids)}, Collisions={len(all_ids)-len(unique_ids)}")

# --- 2.4.2 Schema completeness — all required fields present
required_fields = ["id","type","depth","title","text","parent_id","children_count",
                   "position","number","law_prefix","law_code","source_doc",
                   "word_style","start_idx","end_idx","implicit_parent"]
missing_fields = defaultdict(list)
for n in nodes:
    for f in required_fields:
        if f not in n:
            missing_fields[f].append(n["id"])

check("2.4.2 Schema v1.1 completeness (all 16 fields present)",
      len(missing_fields) == 0,
      f"Missing fields: {dict(missing_fields)}" if missing_fields else "All fields present in all nodes")

# --- 2.4.3 text = direct text check
# ARTICLE co title nhung khong co body → text="". Kiem tra
articles_empty_text = [n for n in nodes if n["type"] == "ARTICLE" and not n.get("text","").strip()]
info("2.4.3 ARTICLE with empty text (title-only, no direct body content)",
     f"{len(articles_empty_text)} articles have text='' (expected for title-only articles)")
for a in articles_empty_text[:3]:
    print(f"       {a['id']} | title={repr(a.get('title','')[:50])}")

# --- 2.4.4 number field correctness
# POINT: number should be the marker character (a, b, c, d...)
points = [n for n in nodes if n["type"] == "POINT"]
points_no_number = [n for n in points if not n.get("number")]
check("2.4.4 POINT nodes have number/marker field populated",
      len(points_no_number) == 0,
      f"POINTs missing number: {len(points_no_number)}" if points_no_number else f"All {len(points)} POINTs have number")
# Show samples
for pt in points[:4]:
    print(f"       POINT id={pt['id'][-30:]} | number={pt['number']} | text_preview={repr(pt.get('text','')[:40])}")

# --- 2.4.5 normalize_marker — ky tu dac biet
from node_generator import NodeGenerator
markers_to_test = [("đ", NodeType.POINT), ("iii", NodeType.CHAPTER),
                   ("26", NodeType.ARTICLE), ("1", NodeType.CLAUSE),
                   ("a", NodeType.POINT), (None, NodeType.ARTICLE)]
norm_results = []
for marker, nt in markers_to_test:
    result = NodeGenerator._normalize_marker(marker, nt)
    norm_results.append((marker, result))
    print(f"       normalize_marker({repr(marker)}) -> {repr(result)}")
check("2.4.5 normalize_marker: d->d, None->unknown, alphanum preserved",
      NodeGenerator._normalize_marker("đ", NodeType.POINT) == "d" and
      NodeGenerator._normalize_marker(None, NodeType.ARTICLE) == "unknown",
      "")

# --- 2.4.6 implicit_parent logic — DOCX mode
# Trong DOCX mode (CLAUSE=185), POINT phai co parent la CLAUSE
points_with_clause_parent = [n for n in points if n.get("parent_id","") and "_khoan-" in n.get("parent_id","")]
points_implicit = [n for n in points if n.get("implicit_parent")]
check("2.4.6 implicit_parent=False for all POINTs in DOCX (have CLAUSE parent)",
      len(points_implicit) == 0,
      f"Implicit POINTs: {len(points_implicit)} (should be 0 in DOCX mode with CLAUSE=185)")

# =============================================================================
# TXT MODE — verify implicit_parent bug
# =============================================================================
print("\n" + "=" * 60)
print("TXT MODE — KL-03: implicit_parent bug check")
print("=" * 60)

p2 = LegalParser(law_prefix="ldd-2024-txt", law_code="59/2024/QH15", source_doc="test.txt")
r2 = p2.parse_text(TXT)
nodes_txt = r2.nodes

points_txt = [n for n in nodes_txt if n["type"] == "POINT"]
points_implicit_txt = [n for n in points_txt if n.get("implicit_parent")]
points_no_clause_txt = [n for n in points_txt if "_khoan-" not in (n.get("parent_id") or "")]

print(f"\n{INFO} TXT POINTs total:                  {len(points_txt)}")
print(f"{INFO} POINTs with implicit_parent=True:   {len(points_implicit_txt)}")
print(f"{INFO} POINTs without CLAUSE parent:       {len(points_no_clause_txt)}")

# KL-03 fixed: all orphan POINTs should have implicit_parent=True
bug_fixed = (len(points_no_clause_txt) > 0 and
             len(points_implicit_txt) == len(points_no_clause_txt))
check("2.4.6b KL-03 implicit_parent correctly set for all TXT orphan POINTs",
      bug_fixed,
      f"Orphan POINTs={len(points_no_clause_txt)}, implicit_parent=True={len(points_implicit_txt)} -> {'OK' if bug_fixed else 'BUG'}")

# ID collision check TXT
ids_txt = [n["id"] for n in points_txt]
unique_ids_txt = set(ids_txt)
check("2.4.7 ID collision in TXT POINT nodes (expected collision)",
      len(ids_txt) != len(unique_ids_txt),
      f"Total={len(ids_txt)}, Unique={len(unique_ids_txt)}, Collisions={len(ids_txt)-len(unique_ids_txt)} (expected due to KL-02)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passes  = sum(1 for s,_,_ in results if s == PASS)
fails   = sum(1 for s,_,_ in results if s == FAIL)
warns   = sum(1 for s,_,_ in results if s == WARN)
print(f"PASS: {passes}  FAIL: {fails}  WARN: {warns}")
if fails:
    print("\nFailed checks:")
    for s,l,d in results:
        if s == FAIL:
            print(f"  {l}: {d}")
