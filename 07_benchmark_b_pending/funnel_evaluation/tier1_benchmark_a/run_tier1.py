# -*- coding: utf-8 -*-
"""
run_tier1.py — Tầng 1: Đánh giá diện rộng (Benchmark A - 512 câu, 2.088 điều luật).
So sánh 3 kiến trúc RAG cơ sở:
1. Vector RAG (Naive Chunking 512 + BGE-M3 Dense + FAISS)
2. Hybrid RAG (Naive Chunking 512 + BM25 + BGE-M3 Dense + Reranker)
3. LightRAG (Generic GraphRAG - Community Summary & Dual-level retrieval)

Tính toán toàn bộ 18 chỉ số, phân loại theo 4 Category và chạy kiểm định thống kê.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import pandas as pd
import numpy as np
from scipy import stats

def run_tier1_analysis():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_bench = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    vec_path = os.path.join(root_bench, "final_benchmark_results_VECTOR.csv")
    hyb_path = os.path.join(root_bench, "final_benchmark_results_HYBRID.csv")
    lrag_path = os.path.join(base_dir, "final_benchmark_results_LIGHTRAG.csv")
    bench_data_path = os.path.join(root_bench, "benchmark_rewritten.json")
    
    print("=== [TẦNG 1] BẮT ĐẦU PHÂN TÍCH BENCHMARK A (512 CÂU) ===")
    
    df_vec = pd.read_csv(vec_path)
    df_hyb = pd.read_csv(hyb_path)
    df_lrag = pd.read_csv(lrag_path)
    
    with open(bench_data_path, "r", encoding="utf-8") as f:
        bench_questions = json.load(f)
    q_cat_map = {q["question_id"]: q.get("category", "unknown") for q in bench_questions}
    
    for df in [df_vec, df_hyb, df_lrag]:
        df["category"] = df["question_id"].map(q_cat_map)
        
    # 1. TỔNG HỢP CHỈ SỐ TOÀN CỤC (OVERALL METRICS)
    metrics_to_calc = [
        "recall_at_5", "mrr_at_5", "strict_match",
        "context_precision", "faithfulness", "citation_accuracy",
        "refusal_correct", "refusal_appropriate",
        "eval_latency_ms", "total_tokens", "estimated_cost"
    ]
    
    summary_rows = []
    systems = [
        ("Vector RAG", df_vec),
        ("Hybrid RAG", df_hyb),
        ("LightRAG (N=512)", df_lrag),
        ("LightRAG (N=502 valid)", df_lrag[~df_lrag["is_imputed"]])
    ]
    
    for name, df in systems:
        row = {"System": name, "N": len(df)}
        for m in metrics_to_calc:
            if m in df.columns:
                valid_vals = df[m].dropna()
                if len(valid_vals) > 0:
                    val = valid_vals.mean()
                    row[m] = round(float(val), 4)
                else:
                    row[m] = "N/A"
            else:
                row[m] = "N/A"
        summary_rows.append(row)
        
    df_summary = pd.DataFrame(summary_rows)
    out_summary_file = os.path.join(base_dir, "tier1_consolidated_metrics.csv")
    df_summary.to_csv(out_summary_file, index=False)
    print(f"\n[1/3] Đã lưu bảng tổng hợp chỉ số Tầng 1: {out_summary_file}")
    print(df_summary.to_string(index=False))
    
    # 2. PHÂN TÍCH THEO CATEGORY
    categories = ["clean_factoid", "conditional", "multi_hop", "negative"]
    cat_rows = []
    
    for cat in categories:
        for name, df in [("Vector RAG", df_vec), ("Hybrid RAG", df_hyb), ("LightRAG", df_lrag)]:
            sub = df[df["category"] == cat]
            row = {"Category": cat, "System": name, "N_Samples": len(sub)}
            for m in ["recall_at_5", "mrr_at_5", "strict_match", "context_precision", "faithfulness", "citation_accuracy", "refusal_correct"]:
                if m in sub.columns:
                    v = sub[m].dropna()
                    row[m] = round(float(v.mean()), 4) if len(v) > 0 else "N/A"
                else:
                    row[m] = "N/A"
            cat_rows.append(row)
            
    df_cat = pd.DataFrame(cat_rows)
    out_cat_file = os.path.join(base_dir, "tier1_category_breakdown.csv")
    df_cat.to_csv(out_cat_file, index=False)
    print(f"\n[2/3] Đã lưu bảng phân loại theo Category: {out_cat_file}")
    
    # 3. KIỂM ĐỊNH THỐNG KÊ (PAIRED T-TEST & WILCOXON SIGNED-RANK TEST)
    merged = pd.merge(df_vec, df_hyb, on="question_id", suffixes=("_vec", "_hyb"))
    test_metrics = ["mrr_at_5", "recall_at_5", "faithfulness", "context_precision", "citation_accuracy"]
    stat_results = {}
    
    print("\n[3/3] KẾT QUẢ KIỂM ĐỊNH Ý NGHĨA THỐNG KÊ (Vector vs Hybrid):")
    for m in test_metrics:
        col_v = f"{m}_vec"
        col_h = f"{m}_hyb"
        valid = merged.dropna(subset=[col_v, col_h])
        v_vals = valid[col_v].astype(float)
        h_vals = valid[col_h].astype(float)
        
        t_stat, p_val = stats.ttest_rel(v_vals, h_vals)
        w_stat, p_val_w = stats.wilcoxon(v_vals, h_vals, zero_method="zsplit")
        diff = float(h_vals.mean() - v_vals.mean())
        
        is_significant = bool(p_val < 0.05)
        stat_results[m] = {
            "mean_vector": round(float(v_vals.mean()), 4),
            "mean_hybrid": round(float(h_vals.mean()), 4),
            "diff_hybrid_minus_vector": round(diff, 4),
            "paired_t_stat": round(float(t_stat), 4),
            "paired_t_p_value": float(f"{p_val:.4e}"),
            "wilcoxon_w_stat": round(float(w_stat), 4),
            "wilcoxon_p_value": float(f"{p_val_w:.4e}"),
            "statistically_significant": is_significant
        }
        sig_str = "CÓ Ý NGHĨA THỐNG KÊ (p < 0.05)" if is_significant else "KHÔNG CÓ KHÁC BIỆT THỐNG KÊ (p >= 0.05)"
        print(f"  - {m.upper()}: Vector={v_vals.mean():.4f} | Hybrid={h_vals.mean():.4f} | Diff={diff:+.4f} | p={p_val:.4e} -> {sig_str}")
        
    out_stat_file = os.path.join(base_dir, "tier1_statistical_tests.json")
    with open(out_stat_file, "w", encoding="utf-8") as f:
        json.dump(stat_results, f, indent=2, ensure_ascii=False)
    print(f"Đã lưu kết quả kiểm định tại: {out_stat_file}")
    print("=== [TẦNG 1] HOÀN TẤT THÀNH CÔNG ===")

if __name__ == "__main__":
    run_tier1_analysis()

