# -*- coding: utf-8 -*-
"""
c2_ablation.py — Prototype C2: Ablation Study (TXT Information Loss)

Mục tiêu:
  Đo lường (1) mức suy giảm cấu trúc khi mất metadata DOCX → TXT,
  và (2) khả năng phục hồi bằng context heuristics (H1, H2, H3).

Evaluation Protocol:
  - Sử dụng Reference Annotation (output_module2_merged.json) là output đã
    cross-check đại diện, KHÔNG phải Gold Standard đầy đủ (chưa manual-annotate toàn corpus).
  - FP/FN được tính bằng text-based matching (vì DOCX index ≠ TXT index):
      Match = candidate.text ≈ ref_clause.text (substring hoặc normalized exact)
  - Cả isolated (H1, H2, H3 riêng) VÀ cumulative (H1+H2+H3) đều được chạy.

Chạy từ thư mục gốc:
  python scripts/experiments_module2/c2_ablation.py
"""

import sys, io, json, re
from pathlib import Path
from collections import Counter
from typing import Optional
from unicodedata import normalize

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "src"
DOCX_FILE     = ROOT.parent / "Luat_dat_dai_chuong_3 (1).docx"
CLEAN_TXT     = ROOT.parent / "luat_ch3_clean.txt"
REF_ANNOTATON = ROOT / "output_module2_merged.json"   # Reference Annotation (≠ Gold Standard)
TXT_OUT       = ROOT / "output_c2_txt_baseline.json"

sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / "preprocessing"))
sys.path.insert(0, str(SRC / "regex_parser"))

from document_loader import DocxLoader, TxtLoader
from parser import LegalParser
from txt_recovery import H1Detector, H2Detector, H3Detector


# ===========================================================================
# BƯỚC 1: Tạo Clean TXT từ DOCX (dùng M1, không serialize metadata)
# ===========================================================================
def generate_clean_txt() -> Path:
    print("[C2] Bước 1: Tạo Clean TXT từ DOCX (không serialize metadata)...")
    loader = DocxLoader()
    paragraphs = loader.load_structured(DOCX_FILE)
    lines = [p.text for p in paragraphs if p.text.strip()]
    with open(CLEAN_TXT, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"       => {len(lines)} dòng → {CLEAN_TXT.name}")
    return CLEAN_TXT


# ===========================================================================
# BƯỚC 2: Parse TXT Baseline
# ===========================================================================
def run_txt_baseline(txt_path: Path) -> tuple[list[dict], list]:
    print("[C2] Bước 2: Parse TXT Baseline...")
    loader  = TxtLoader()
    paras   = loader.load_structured(txt_path)
    parser  = LegalParser(law_prefix="ldd-2024", law_code="59/2024/QH15")
    result  = parser.parse_structured(paras, source_doc=txt_path.name)
    with open(TXT_OUT, "w", encoding="utf-8") as f:
        json.dump(result.nodes, f, ensure_ascii=False, indent=2)
    c = Counter(n["type"] for n in result.nodes)
    print(f"       => {len(result.nodes)} nodes | CLAUSE={c.get('CLAUSE',0)} | POINT={c.get('POINT',0)}")
    return result.nodes, paras


# ===========================================================================
# BƯỚC 3: Load Reference Annotation
# ===========================================================================
def load_reference() -> list[dict]:
    with open(REF_ANNOTATON, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    print(f"[C2] Reference Annotation: {len(nodes)} nodes từ {REF_ANNOTATON.name}")
    print(f"     (Cross-checked đại diện — không phải full manual Ground Truth)")
    return nodes


# ===========================================================================
# Evaluation: Text-Based Alignment
# ===========================================================================
def _normalize(text: str) -> str:
    """Chuẩn hóa text để matching: NFC, lower, collapse whitespace."""
    t = normalize("NFC", text or "").lower()
    return re.sub(r"\s+", " ", t).strip()

def _build_ref_clause_set(ref_nodes: list[dict]) -> list[dict]:
    """Lấy danh sách CLAUSE từ Reference Annotation, chuẩn hóa text."""
    return [
        {
            "id":         n["id"],
            "text_norm":  _normalize(n.get("text", "")),
            "parent_id":  n.get("parent_id", ""),
            "start_idx":  n.get("start_idx"),
            "end_idx":    n.get("end_idx"),
        }
        for n in ref_nodes if n.get("type") == "CLAUSE"
    ]

def _match_candidate_to_ref(
    candidate_text: str,
    ref_clauses: list[dict],
    parent_article_id: str,
) -> Optional[dict]:
    """
    Tìm ref CLAUSE khớp với candidate dựa trên text similarity.

    Matching rule (theo thứ tự ưu tiên):
      1. Exact match sau normalize.
      2. Candidate text là substring của ref.text (phần đầu).
      3. Ref.text bắt đầu bằng candidate text (candidate bị cắt ngắn).

    Parent article được dùng để giới hạn không gian tìm kiếm.
    """
    c_norm = _normalize(candidate_text)
    if not c_norm:
        return None

    # Giới hạn theo article: ref clause phải thuộc cùng article
    # (parent_id của ref CLAUSE = article_id)
    # TXT article ID và ref article ID nên giống nhau vì cùng pipeline prefix
    art_candidates = [r for r in ref_clauses if parent_article_id in r["parent_id"]]
    if not art_candidates:
        art_candidates = ref_clauses  # fallback: tìm toàn bộ

    for ref in art_candidates:
        r_norm = ref["text_norm"]
        if not r_norm:
            continue
        # Exact match
        if c_norm == r_norm:
            return ref
        # Candidate text là phần đầu của ref text (ref trải nhiều paragraph)
        if r_norm.startswith(c_norm[:min(len(c_norm), 60)]) and len(c_norm) >= 20:
            return ref
        # Ref text là phần đầu của candidate text
        if c_norm.startswith(r_norm[:min(len(r_norm), 60)]) and len(r_norm) >= 20:
            return ref

    return None

from typing import Optional

def evaluate_candidates(
    candidates: list,
    ref_clauses: list[dict],
    hypothesis_name: str,
) -> dict:
    """
    Đánh giá FP/FN cho một tập candidates dựa trên text-based matching.

    TP: Candidate match được một ref CLAUSE.
    FP: Candidate không match được ref CLAUSE nào.
    FN: Ref CLAUSE không được bất kỳ candidate nào match.

    Note: Một ref CLAUSE chỉ được match tối đa một lần (greedy left-to-right).
    """
    matched_ref_ids: set[str] = set()
    tp = fp = 0

    for c in candidates:
        ref = _match_candidate_to_ref(c.text, ref_clauses, c.parent_article_id)
        if ref and ref["id"] not in matched_ref_ids:
            tp += 1
            matched_ref_ids.add(ref["id"])
        else:
            fp += 1

    fn = len(ref_clauses) - len(matched_ref_ids)
    total_ref = len(ref_clauses)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / total_ref  if total_ref > 0  else 0.0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "hypothesis":  hypothesis_name,
        "candidates":  len(candidates),
        "tp": tp, "fp": fp, "fn": fn,
        "precision":   round(precision, 3),
        "recall":      round(recall, 3),
        "f1":          round(f1, 3),
        "ref_clauses": total_ref,
    }


# ===========================================================================
# In bảng kết quả
# ===========================================================================
def print_degradation_table(ref_nodes: list[dict], txt_nodes: list[dict]):
    ref_c = Counter(n["type"] for n in ref_nodes)
    txt_c = Counter(n["type"] for n in txt_nodes)

    print("\n" + "=" * 82)
    print("C2 — DEGRADATION BASELINE (DOCX Reference vs TXT No-Metadata)")
    print("=" * 82)
    header = f"{'Stage':<28} {'CHAP':>5} {'SECT':>5} {'ART':>5} {'CLAUSE':>7} {'POINT':>7} {'Total':>7}"
    print(header)
    print("-" * 82)

    types = ["CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT"]
    def row(label, counts):
        vals = [counts.get(t, 0) for t in types]
        return f"{label:<28} " + " ".join(f"{v:>5}" if i < 3 else f"{v:>7}" for i, v in enumerate(vals)) + f" {sum(vals):>7}"

    print(row("DOCX Reference Annotation", ref_c))
    print(row("TXT Baseline (No Metadata)", txt_c))
    print()
    for t in types:
        rv, tv = ref_c.get(t, 0), txt_c.get(t, 0)
        pct = round((tv - rv) / rv * 100, 1) if rv > 0 else 0.0
        mark = "⚠" if pct < -50 else ("✓" if pct == 0 else "·")
        print(f"  {mark} {t:<10}: {rv:>3} → {tv:>3}  ({pct:+.1f}%)")


def _baseline_entry(ref_clauses: list[dict]) -> dict:
    """TXT Baseline entry: 0 candidates, 0 TP, 0 FP, all 84 ref CLAUSEs missed (FN)."""
    return {
        "hypothesis": "TXT Baseline",
        "candidates": 0,
        "tp": 0, "fp": 0, "fn": len(ref_clauses),
        "precision": 0.0, "recall": 0.0, "f1": 0.0,
        "ref_clauses": len(ref_clauses),
    }


def print_recovery_table(eval_results: list[dict], ref_clauses: list[dict]):
    baseline = _baseline_entry(ref_clauses)
    print("\n" + "=" * 92)
    print("C2 — RECOVERY EXPERIMENT (Isolated + Cumulative)")
    print("Note: Matching by text similarity — Reference Annotation (\u2260 full Ground Truth)")
    print("=" * 92)
    delta_col = "\u0394F1"
    header = (
        f"{'Config':<18} {'Cands':>6} {'TP':>5} {'FP':>5} {'FN':>5}"
        f" {'Prec.':>7} {'Rec.':>7} {'F1':>7} {delta_col:>7}"
    )
    print(header)
    print("-" * 92)

    isolated_keys   = ["H1", "H2", "H3"]
    cumulative_keys = ["H1+H2", "H1+H3", "H2+H3", "H1+H2+H3"]
    base_f1 = baseline["f1"]

    # Hàng TXT Baseline
    _print_row(baseline, base_f1)
    print("  [Isolated]")
    for r in eval_results:
        if r["hypothesis"] in isolated_keys:
            _print_row(r, base_f1)

    print("  [Cumulative]")
    for r in eval_results:
        if r["hypothesis"] in cumulative_keys:
            _print_row(r, base_f1)

    print("-" * 92)
    print(f"  Reference CLAUSE count: {baseline['ref_clauses']}")
    print(f"  \u0394F1 = F1 - F1(TXT Baseline). Gain > 0 = recovery so with no-metadata baseline.")
    print("=" * 92)


def _print_row(r: dict, base_f1: float = 0.0):
    delta = r["f1"] - base_f1
    delta_str = f"{delta:+.3f}" if r["hypothesis"] != "TXT Baseline" else "  —  "
    print(
        f"  {r['hypothesis']:<16} {r['candidates']:>6} {r['tp']:>5} {r['fp']:>5}"
        f" {r['fn']:>5} {r['precision']:>7.3f} {r['recall']:>7.3f} {r['f1']:>7.3f} {delta_str:>7}"
    )


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("\n" + "=" * 82)
    print("PROTOTYPE C2 — TXT Information Loss Ablation Study")
    print("Corpus: Chương III Luật Đất đai 2024 (Ch3-LDD)")
    print("=" * 82 + "\n")

    # Bước 1–3: Setup
    txt_path           = generate_clean_txt()
    txt_nodes, txt_paras = run_txt_baseline(txt_path)
    ref_nodes          = load_reference()
    ref_clauses        = _build_ref_clause_set(ref_nodes)

    # Bước 4: Chạy detectors (isolated)
    print("\n[C2] Bước 3: Chạy Hypothesis Detectors (isolated)...")
    h1_cands = H1Detector().detect(txt_nodes, txt_paras)
    h2_cands = H2Detector().detect(txt_nodes, txt_paras)
    h3_cands = H3Detector().detect(txt_nodes, txt_paras)
    print(f"       H1: {len(h1_cands)} ứng cử viên")
    print(f"       H2: {len(h2_cands)} ứng cử viên")
    print(f"       H3: {len(h3_cands)} ứng cử viên")

    # Bước 5: Evaluate — Isolated
    print("\n[C2] Bước 4: Evaluate (text-based matching)...")

    def dedup(cands: list) -> list:
        """Dedup bằng para_index — tránh match một paragraph nhiều lần."""
        seen = set()
        result = []
        for c in cands:
            if c.para_index not in seen:
                seen.add(c.para_index)
                result.append(c)
        return result

    eval_h1 = evaluate_candidates(dedup(h1_cands), ref_clauses, "H1")
    eval_h2 = evaluate_candidates(dedup(h2_cands), ref_clauses, "H2")
    eval_h3 = evaluate_candidates(dedup(h3_cands), ref_clauses, "H3")

    # Cumulative combinations
    h1h2_cands   = dedup(h1_cands + h2_cands)
    h1h3_cands   = dedup(h1_cands + h3_cands)
    h2h3_cands   = dedup(h2_cands + h3_cands)
    h1h2h3_cands = dedup(h1_cands + h2_cands + h3_cands)

    eval_h1h2   = evaluate_candidates(h1h2_cands,   ref_clauses, "H1+H2")
    eval_h1h3   = evaluate_candidates(h1h3_cands,   ref_clauses, "H1+H3")
    eval_h2h3   = evaluate_candidates(h2h3_cands,   ref_clauses, "H2+H3")
    eval_h1h2h3 = evaluate_candidates(h1h2h3_cands, ref_clauses, "H1+H2+H3")

    all_evals = [eval_h1, eval_h2, eval_h3, eval_h1h2, eval_h1h3, eval_h2h3, eval_h1h2h3]

    # Bước 6: In bảng
    print_degradation_table(ref_nodes, txt_nodes)
    print_recovery_table(all_evals, ref_clauses)

    # Lưu kết quả candidates JSON
    for name, cands in [("h1", h1_cands), ("h2", h2_cands), ("h3", h3_cands),
                         ("h1h2h3", h1h2h3_cands)]:
        out = ROOT / f"output_c2_{name}_candidates.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(
                [{"para_index": c.para_index, "text": c.text[:80],
                  "parent_article_id": c.parent_article_id,
                  "hypothesis": c.hypothesis, "confidence": c.confidence,
                  "reason": c.reason}
                 for c in cands],
                f, ensure_ascii=False, indent=2
            )
    print(f"\n[C2] Candidates đã lưu vào output_c2_*.json")
    print("[C2] Xong.\n")


if __name__ == "__main__":
    main()
