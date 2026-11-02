# -*- coding: utf-8 -*-
"""
test_funnel_pipeline.py — Bộ kiểm thử tự động toàn diện (Automated Test Suite)
cho Hệ thống Đánh giá Cái Phễu 3 Tầng.
Chạy bằng pytest hoặc python trực tiếp để xác thực tính toàn vẹn 100% của mọi tệp dữ liệu và chỉ số.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def test_tier1_outputs():
    """Kiểm thử tính toàn vẹn của Tầng 1 (Benchmark A)"""
    summary_path = os.path.join(BASE_DIR, "tier1_benchmark_a", "tier1_consolidated_metrics.csv")
    cat_path = os.path.join(BASE_DIR, "tier1_benchmark_a", "tier1_category_breakdown.csv")
    stat_path = os.path.join(BASE_DIR, "tier1_benchmark_a", "tier1_statistical_tests.json")
    clean_lrag_path = os.path.join(BASE_DIR, "tier1_benchmark_a", "final_benchmark_results_LIGHTRAG.csv")

    assert os.path.exists(summary_path), "Thiếu file tier1_consolidated_metrics.csv"
    assert os.path.exists(cat_path), "Thiếu file tier1_category_breakdown.csv"
    assert os.path.exists(stat_path), "Thiếu file tier1_statistical_tests.json"
    assert os.path.exists(clean_lrag_path), "Thiếu file final_benchmark_results_LIGHTRAG.csv"

    # Kiểm tra số lượng dòng
    df_clean = pd.read_csv(clean_lrag_path)
    assert len(df_clean) == 512, f"LightRAG clean phải có 512 dòng, thực tế: {len(df_clean)}"
    assert df_clean["is_imputed"].sum() == 10, "Phải có đúng 10 dòng được chuẩn hóa (imputed)"

    # Kiểm tra số liệu Tầng 1
    df_sum = pd.read_csv(summary_path)
    assert len(df_sum) == 4, "Bảng tổng hợp Tầng 1 phải có 4 cấu hình"
    
    vec_row = df_sum[df_sum["System"] == "Vector RAG"].iloc[0]
    hyb_row = df_sum[df_sum["System"] == "Hybrid RAG"].iloc[0]
    lrag_row = df_sum[df_sum["System"] == "LightRAG (N=512)"].iloc[0]

    # Hybrid phải thắng Vector ở MRR
    assert float(hyb_row["mrr_at_5"]) > float(vec_row["mrr_at_5"])
    # Cả hai phải dậm chân ở trần Citation ~40%
    assert 0.39 <= float(vec_row["citation_accuracy"]) <= 0.41
    assert 0.39 <= float(hyb_row["citation_accuracy"]) <= 0.41
    # LightRAG Context Precision phải sụp đổ (< 0.45)
    assert float(lrag_row["context_precision"]) < 0.45

    with open(stat_path, "r", encoding="utf-8") as f:
        stat_data = json.load(f)
    assert stat_data["mrr_at_5"]["statistically_significant"] is True
    assert stat_data["recall_at_5"]["statistically_significant"] is False
    print("[PASS] Test Tier 1: Toàn vẹn và chính xác 100%.")

def test_tier2_outputs():
    """Kiểm thử tính toàn vẹn của Tầng 2 (Ablation 2x2)"""
    matrix_path = os.path.join(BASE_DIR, "tier2_ablation_2x2", "tier2_ablation_matrix.csv")
    assert os.path.exists(matrix_path), "Thiếu file tier2_ablation_matrix.csv"

    df_mat = pd.read_csv(matrix_path)
    assert len(df_mat) == 4, "Ma trận 2x2 phải có đúng 4 cấu hình"

    # Lấy 4 hàng
    vec_naive = df_mat[(df_mat["Retrieval_Method"].str.contains("Vector")) & (df_mat["Chunking_Strategy"].str.contains("Naive"))].iloc[0]
    vec_parser = df_mat[(df_mat["Retrieval_Method"].str.contains("Vector")) & (df_mat["Chunking_Strategy"].str.contains("Parser"))].iloc[0]
    hyb_naive = df_mat[(df_mat["Retrieval_Method"].str.contains("Hybrid")) & (df_mat["Chunking_Strategy"].str.contains("Naive"))].iloc[0]
    hyb_parser = df_mat[(df_mat["Retrieval_Method"].str.contains("Hybrid")) & (df_mat["Chunking_Strategy"].str.contains("Parser"))].iloc[0]

    # Kiểm tra sự bứt phá của Citation Accuracy
    assert float(vec_parser["Citation_Accuracy"]) > float(vec_naive["Citation_Accuracy"]) + 0.30, "Parser Vector phải tăng tối thiểu +30% Citation"
    assert float(hyb_parser["Citation_Accuracy"]) > float(hyb_naive["Citation_Accuracy"]) + 0.35, "Parser Hybrid phải tăng tối thiểu +35% Citation"
    assert float(hyb_parser["Citation_Accuracy"]) >= 0.75, "Parser Hybrid phải đạt Citation >= 75%"
    print("[PASS] Test Tier 2: Ma trận 2x2 giải phóng trần Citation thành công.")

def test_tier3_outputs():
    """Kiểm thử tính toàn vẹn của Tầng 3 (Benchmark B)"""
    comp_path = os.path.join(BASE_DIR, "tier3_benchmark_b", "tier3_benchmark_b_comparison.csv")
    cat_path = os.path.join(BASE_DIR, "tier3_benchmark_b", "tier3_category_breakdown.csv")

    assert os.path.exists(comp_path), "Thiếu file tier3_benchmark_b_comparison.csv"
    assert os.path.exists(cat_path), "Thiếu file tier3_category_breakdown.csv"

    df_comp = pd.read_csv(comp_path)
    assert len(df_comp) >= 15, "Bảng so sánh Tầng 3 phải có tối thiểu 15 chỉ số"

    # Kiểm tra tiết kiệm Runtime Cost
    cost_row = df_comp[df_comp["Metric_Name"].str.contains("Runtime Query Cost")].iloc[0]
    assert "41.55%" in cost_row["Delta_Improvement"], "Phải xác nhận tiết kiệm 41.55% chi phí runtime"

    # Kiểm tra Citation Khoản/Điểm vượt trội
    khoan_row = df_comp[df_comp["Metric_Name"].str.contains("Citation Khoản")].iloc[0]
    diem_row = df_comp[df_comp["Metric_Name"].str.contains("Citation Điểm")].iloc[0]
    assert "0.8170" in khoan_row["Hybrid Parser/UKG (Ours)"]
    assert "0.6374" in diem_row["Hybrid Parser/UKG (Ours)"]

    # Kiểm tra Chain Exact Match được báo cáo trung thực
    chain_row = df_comp[df_comp["Metric_Name"].str.contains("Chain Exact Match")].iloc[0]
    assert "0.0000" in chain_row["Hybrid Parser/UKG (Ours)"]

    df_cat = pd.read_csv(cat_path)
    assert len(df_cat) == 8, "Benchmark B phải có đúng 8 Category pháp lý"
    print("[PASS] Test Tier 3: Đối đầu chuyên sâu và báo cáo giới hạn thành công.")

if __name__ == "__main__":
    print("=== BẮT ĐẦU CHẠY TOÀN BỘ BỘ TEST SUITE CHO CÁI PHỄU ===")
    test_tier1_outputs()
    test_tier2_outputs()
    test_tier3_outputs()
    print("=== TẤT CẢ TEST ĐÃ PASS 100%! HỆ THỐNG HOÀN TOÀN SẴN SÀNG ===")

