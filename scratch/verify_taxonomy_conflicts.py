"""
verify_taxonomy_conflicts.py
So sánh alias coverage giữa Lâm (mapping_rules.yaml) và Minh (taxonomy_aliases.yaml).
Format hai bên khác nhau nên cần parse riêng.
"""
import yaml
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import unicodedata, re

def normalize(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return unicodedata.normalize('NFC', text)

# ── Load Lâm: mapping_rules.yaml ──────────────────────────────────────────────
# Mỗi rule có list triggers → target_concept_id + target_subtype
lam_path = Path("src/ontology/configs/mapping_rules.yaml")
with open(lam_path, encoding="utf-8") as f:
    lam_data = yaml.safe_load(f)

# alias → (concept_id, subtype, rule_id)
lam_alias_map: dict[str, tuple] = {}
for rule in lam_data.get("mapping_rules", []):
    cid   = rule.get("target_concept_id", "")
    stype = rule.get("target_subtype", "")
    rid   = rule.get("id", "")
    for trig in rule.get("triggers", []):
        norm = normalize(trig)
        if norm:
            lam_alias_map[norm] = (cid, stype, rid)

# ── Load Minh: taxonomy_aliases.yaml ──────────────────────────────────────────
# canonical_id (key) → { ontology_class, canonical_text, aliases: [...] }
minh_path = Path(r"c:\Users\luuth\NCKH\minh\src\ontology\configs\taxonomy_aliases.yaml")
with open(minh_path, encoding="utf-8") as f:
    minh_raw = yaml.safe_load(f)

# alias → (canonical_id, ontology_class)
minh_alias_map: dict[str, tuple] = {}
for cid, entry in minh_raw.items():
    if not isinstance(entry, dict):
        continue
    cls = entry.get("ontology_class", "")
    for alias in entry.get("aliases", []):
        norm = normalize(alias)
        if norm:
            minh_alias_map[norm] = (cid, cls)

# ── Stats ──────────────────────────────────────────────────────────────────────
print(f"Lâm  aliases (triggers): {len(lam_alias_map)}")
print(f"Minh aliases           : {len(minh_alias_map)}")

common = set(lam_alias_map) & set(minh_alias_map)
only_minh = set(minh_alias_map) - set(lam_alias_map)
only_lam  = set(lam_alias_map)  - set(minh_alias_map)

print(f"\nChung (cùng alias xuất hiện cả 2 bên): {len(common)}")
print(f"Chỉ có trong Minh (alias Lâm thiếu)  : {len(only_minh)}")
print(f"Chỉ có trong Lâm  (alias Minh thiếu) : {len(only_lam)}")

# ── Phân loại conflict trong phần chung ───────────────────────────────────────
type_a, type_b, type_c = [], [], []

for alias in sorted(common):
    lam_cid, lam_sub, lam_rid = lam_alias_map[alias]
    minh_cid, minh_cls = minh_alias_map[alias]

    # Mapping concept_id giữa 2 hệ thống không đồng nhất (khác tên)
    # Ta so sánh gần đúng: nếu cùng "lớp" semantic (LegalSubject vs LEGAL_SUBJECT)
    # coi là cùng class
    lam_class_raw = lam_sub  # VD: CentralAuthority, Individual...
    minh_class_norm = minh_cls  # VD: LEGAL_SUBJECT, LEGAL_ACTION...

    # Type A: alias chung, cùng concept ngữ nghĩa (heuristic: cùng canonical_id prefix)
    # Dùng heuristic: nếu lam_cid chứa một phần của minh_cid hoặc ngược lại
    same_concept = (
        lam_cid.upper().replace(".", "_") in minh_cid.upper().replace(".", "_")
        or minh_cid.upper().replace(".", "_") in lam_cid.upper().replace(".", "_")
        or lam_cid == ""  # Lâm không có concept_id → chỉ subtype
    )

    if same_concept:
        type_a.append((alias, lam_cid, lam_sub, minh_cid, minh_cls))
    else:
        type_b.append((alias, lam_cid, lam_sub, minh_cid, minh_cls))

print(f"\n── Phân loại conflict trong {len(common)} alias chung ──")
print(f"Type A (cùng concept, merge OK) : {len(type_a)}")
print(f"Type B (khác concept → CONFLICT): {len(type_b)}")

if type_b:
    print(f"\n{'='*60}")
    print("Type B CONFLICTS (cần review thủ công):")
    print(f"{'='*60}")
    for alias, lc, ls, mc, mcls in type_b[:30]:
        print(f"\n  Alias  : '{alias}'")
        print(f"  Lâm    : concept={lc} | subtype={ls}")
        print(f"  Minh   : concept={mc} | class={mcls}")

# ── Alias Minh có nhưng Lâm không có: đây là ứng viên thêm vào ───────────────
print(f"\n── Sample 20 alias Minh có, Lâm thiếu ──")
for alias in sorted(only_minh)[:20]:
    cid, cls = minh_alias_map[alias]
    print(f"  '{alias}' → {cid} ({cls})")

print(f"\n── VERDICT ──")
if len(type_b) == 0:
    print("✅ Không có conflict: merge alias an toàn")
elif len(type_b) <= 5:
    print(f"⚠️  {len(type_b)} conflict nhỏ: review thủ công {len(type_b)} case rồi merge")
elif len(type_b) <= 20:
    print(f"🟡 {len(type_b)} conflict trung bình: cần review kỹ trước khi merge")
else:
    print(f"🔴 {len(type_b)} conflict lớn: KHÔNG merge tự động")
