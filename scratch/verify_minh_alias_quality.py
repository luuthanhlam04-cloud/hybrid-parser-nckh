"""
verify_minh_alias_quality.py
Sample 30 alias độc lập của Minh, check semantic mapping có đúng không.
"""
import yaml, sys, re, unicodedata, random
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

def normalize(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return unicodedata.normalize('NFC', text)

# Load Lâm aliases (triggers)
lam_path = Path("src/ontology/configs/mapping_rules.yaml")
with open(lam_path, encoding="utf-8") as f:
    lam_data = yaml.safe_load(f)
lam_triggers = set()
for rule in lam_data.get("mapping_rules", []):
    for trig in rule.get("triggers", []):
        lam_triggers.add(normalize(trig))

# Load Minh taxonomy
minh_path = Path(r"c:\Users\luuth\NCKH\minh\src\ontology\configs\taxonomy_aliases.yaml")
with open(minh_path, encoding="utf-8") as f:
    minh_raw = yaml.safe_load(f)

# Load Lâm taxonomy tree (để verify ngữ nghĩa)
tax_path = Path("src/ontology/configs/taxonomy_registry.yaml")
with open(tax_path, encoding="utf-8") as f:
    lam_taxonomy = yaml.safe_load(f)

# Build danh sách node trong taxonomy của Lâm
def collect_lam_types(tree, path=""):
    types = {}
    for name, data in tree.items():
        if not isinstance(data, dict) or name in ("description", "rationale"):
            continue
        types[name] = data.get("description", "")
        subtypes = data.get("subtypes", {})
        if subtypes:
            types.update(collect_lam_types(subtypes, path + name + "."))
    return types

lam_known_types = collect_lam_types(lam_taxonomy)

# Lớp ontology của Lâm
LAM_ONTOLOGY_CLASSES = {
    "LegalSubject": {"LEGAL_SUBJECT"},
    "LegalAction": {"LEGAL_ACTION"},
    "LegalObject": {"LEGAL_OBJECT"},
    "LegalConsequence": {"LEGAL_CONSEQUENCE", "PENALTY"},
    "Condition": {"CONDITION"},
    "Exception": {"EXCEPTION"},
    "Reference": {"REFERENCE", "LEGAL_DOCUMENT_REF"},
}
MINH_TO_LAM_CLASS = {
    "LEGAL_SUBJECT": "LegalSubject",
    "LEGAL_ACTION": "LegalAction",
    "LEGAL_OBJECT": "LegalObject",
    "LEGAL_CONSEQUENCE": "LegalConsequence",
    "PENALTY": "LegalConsequence",
    "CONDITION": "Condition",
    "EXCEPTION": "Exception",
    "LEGAL_DOCUMENT_REF": "Reference",
}

# Lấy 304 alias của Minh mà Lâm thiếu
minh_only = []
for cid, entry in minh_raw.items():
    if not isinstance(entry, dict):
        continue
    cls = entry.get("ontology_class", "")
    canonical_text = entry.get("canonical_text", "")
    for alias in entry.get("aliases", []):
        norm = normalize(alias)
        if norm and norm not in lam_triggers:
            minh_only.append({
                "alias": alias,
                "norm": norm,
                "concept_id": cid,
                "ontology_class": cls,
                "canonical_text": canonical_text,
            })

random.seed(42)
sample = random.sample(minh_only, min(30, len(minh_only)))
sample.sort(key=lambda x: x["ontology_class"])

print(f"Tổng alias chỉ có trong Minh: {len(minh_only)}")
print(f"Sample {len(sample)} alias để review:\n")
print(f"{'='*80}")

issues = []
ok = []

for item in sample:
    alias = item["alias"]
    cid = item["concept_id"]
    cls = item["ontology_class"]
    ctext = item["canonical_text"]
    lam_class = MINH_TO_LAM_CLASS.get(cls, "UNKNOWN")

    # Heuristic check: concept_id có hợp lý không?
    # Ví dụ: "cho thuê" phải là LEGAL_ACTION, không phải LEGAL_SUBJECT
    keyword_class_hints = {
        "chuyển": "LEGAL_ACTION", "thuê": "LEGAL_ACTION", "giao": "LEGAL_ACTION",
        "thu hồi": "LEGAL_ACTION", "đăng ký": "LEGAL_ACTION", "cấp": "LEGAL_ACTION",
        "nộp": "LEGAL_ACTION", "bồi": "LEGAL_ACTION", "tặng": "LEGAL_ACTION",
        "nhà nước": "LEGAL_SUBJECT", "ubnd": "LEGAL_SUBJECT", "cá nhân": "LEGAL_SUBJECT",
        "tổ chức": "LEGAL_SUBJECT", "người": "LEGAL_SUBJECT",
        "đất": "LEGAL_OBJECT", "quyền sử dụng": "LEGAL_OBJECT", "giấy": "LEGAL_OBJECT",
        "hợp đồng": "LEGAL_OBJECT", "quyết định": "LEGAL_OBJECT",
        "điều kiện": "CONDITION", "trường hợp": "CONDITION",
        "ngoại trừ": "EXCEPTION", "trừ trường hợp": "EXCEPTION",
    }

    hint = None
    for kw, expected_cls in keyword_class_hints.items():
        if kw in alias.lower():
            hint = expected_cls
            break

    is_suspicious = hint and hint != cls

    status = "⚠️ SUSPICIOUS" if is_suspicious else "✅ OK"
    marker = "ISSUE" if is_suspicious else "OK"

    print(f"[{status}] '{alias}'")
    print(f"         → concept={cid} | class={cls} | canonical='{ctext}'")
    if is_suspicious:
        print(f"         ⚠️ Hint từ keyword: nên là {hint}, nhưng Minh gán {cls}")
        issues.append(item)
    else:
        ok.append(item)
    print()

print(f"{'='*80}")
print(f"\nKết quả sample 30:")
print(f"  ✅ Looks OK : {len(ok)}")
print(f"  ⚠️  Suspicious: {len(issues)}")
print()
if issues:
    print("Alias suspicious cần review thủ công:")
    for item in issues:
        print(f"  '{item['alias']}' → {item['concept_id']} ({item['ontology_class']})")

print(f"\n{'='*80}")
ratio = len(issues) / len(sample)
if ratio < 0.1:
    print(f"VERDICT: ✅ {len(issues)}/{len(sample)} suspicious — merge 304 alias được, cần review {len(issues)} case")
elif ratio < 0.17:
    print(f"VERDICT: ⚠️  {len(issues)}/{len(sample)} suspicious — review kỹ hơn trước khi merge")
else:
    print(f"VERDICT: 🔴 {len(issues)}/{len(sample)} suspicious — không merge tự động")
