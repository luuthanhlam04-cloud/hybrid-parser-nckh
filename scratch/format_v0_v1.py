import pathlib

content = pathlib.Path('docs/researchnote_m7_v0_v1.md').read_text(encoding='utf-8')

parts = content.split('# Research Note: Module 7 — Ontology / Semantic Canonicalization')
part0 = parts[1] if len(parts) > 1 else ''
part1 = parts[2] if len(parts) > 2 else ''

final_content = f"""# TỔNG HỢP LỊCH SỬ M7 (V0.9 & V1.1)

---

# PHẦN 1: BẢN V0.9 (ARCHIVED)
# Research Note: Module 7 — Ontology / Semantic Canonicalization
{part0.strip()}

---
---

# PHẦN 2: BẢN V1.1
# Research Note: Module 7 — Ontology / Semantic Canonicalization
{part1.strip()}
"""

pathlib.Path('docs/researchnote_m7_v0_v1.md').write_text(final_content, encoding='utf-8')
