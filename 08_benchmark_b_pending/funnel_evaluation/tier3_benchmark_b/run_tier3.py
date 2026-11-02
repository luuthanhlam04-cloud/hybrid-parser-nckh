# -*- coding: utf-8 -*-
"""
run_tier3.py — Tầng 3: Đáy phễu (Tối ưu hóa Kiến trúc Tri thức Chuyên sâu).
So sánh đối đầu trực tiếp trên Benchmark B (50 câu chuyên sâu Chương III Luật Đất đai 2024):
1. Generic GraphRAG (LightRAG đại trà)
2. Domain-specific Legal UKG (Hybrid Parser / UKG - M10 AUTO_FUSION + Jev Router)

Trích xuất toàn bộ dữ liệu kiểm chứng độc lập từ báo cáo thực nghiệm Benchmark B,
xuất ra bảng đối đầu toàn diện và phân tích chi tiết theo 8 Category pháp lý.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import pandas as pd

def run_tier3_analysis():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== [TẦNG 3] BẮT ĐẦU ĐỐI SÁNH CHUYÊN SÂU BENCHMARK B (CHƯƠNG III LĐĐ 2024) ===")
    
    # 1. BẢNG SO SÁNH ĐỐI ĐẦU TOÀN DIỆN (COMPREHENSIVE HEAD-TO-HEAD)
    comparison_data = [
        # Nhóm 1: Retrieval & Evidence
        {"Metric_Category": "Retrieval & Evidence", "Metric_Name": "Retrieval Recall@5", "LightRAG (Generic)": "0.7358", "Hybrid Parser/UKG (Ours)": "0.9184", "Delta_Improvement": "+18.26%", "Assessment": "UKG áp đảo độ phủ căn cứ Top-5"},
        {"Metric_Category": "Retrieval & Evidence", "Metric_Name": "Retrieval MRR@5", "LightRAG (Generic)": "0.5539", "Hybrid Parser/UKG (Ours)": "0.8848", "Delta_Improvement": "+33.09%", "Assessment": "Căn cứ đúng được đẩy lên vị trí Top-1"},
        {"Metric_Category": "Retrieval & Evidence", "Metric_Name": "Expanded Evidence Recall", "LightRAG (Generic)": "N/A", "Hybrid Parser/UKG (Ours)": "0.9770", "Delta_Improvement": "N/A", "Assessment": "97.7% căn cứ liên quan được đưa vào context"},
        {"Metric_Category": "Retrieval & Evidence", "Metric_Name": "Context Evidence Items / câu", "LightRAG (Generic)": "N/A", "Hybrid Parser/UKG (Ours)": "7.64", "Delta_Improvement": "N/A", "Assessment": "Mật độ căn cứ pháp lý tập trung cao"},

        # Nhóm 2: Định vị & Trích dẫn cấu trúc (Citation Granularity)
        {"Metric_Category": "Citation Granularity", "Metric_Name": "Citation Điều (Precision)", "LightRAG (Generic)": "0.3333", "Hybrid Parser/UKG (Ours)": "0.8369", "Delta_Improvement": "+50.36%", "Assessment": "Định vị cấp Điều chính xác vượt trội"},
        {"Metric_Category": "Citation Granularity", "Metric_Name": "Citation Điều (Recall)", "LightRAG (Generic)": "0.2961", "Hybrid Parser/UKG (Ours)": "0.9078", "Delta_Improvement": "+61.17%", "Assessment": "Bắt trọn vẹn 90.78% Điều luật liên quan"},
        {"Metric_Category": "Citation Granularity", "Metric_Name": "Citation Khoản (Precision / Recall)", "LightRAG (Generic)": "0.0435 / 0.0435", "Hybrid Parser/UKG (Ours)": "0.7757 / 0.8170", "Delta_Improvement": "+77.35%", "Assessment": "LightRAG sụp đổ ở cấp Khoản; UKG giữ vững >81%"},
        {"Metric_Category": "Citation Granularity", "Metric_Name": "Citation Điểm (Precision / Recall)", "LightRAG (Generic)": "0.0270 / 0.0270", "Hybrid Parser/UKG (Ours)": "0.6797 / 0.6374", "Delta_Improvement": "+61.04%", "Assessment": "Khả năng truy vết tới tiểu tiết Điểm quy phạm"},

        # Nhóm 3: Chất lượng trả lời (LLM Judge)
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Legal Correctness", "LightRAG (Generic)": "0.8210", "Hybrid Parser/UKG (Ours)": "0.8777", "Delta_Improvement": "+5.67%", "Assessment": "Độ chính xác pháp lý cao hơn"},
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Atomic Fact Coverage", "LightRAG (Generic)": "0.8551", "Hybrid Parser/UKG (Ours)": "0.8686", "Delta_Improvement": "+1.35%", "Assessment": "Bao quát đầy đủ các sự kiện nguyên tử"},
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Exception Coverage (14 câu)", "LightRAG (Generic)": "0.3929", "Hybrid Parser/UKG (Ours)": "0.6786", "Delta_Improvement": "+28.57%", "Assessment": "UKG bắt ngoại lệ tốt hơn rõ rệt"},
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Subject-Scope Accuracy (18 câu)", "LightRAG (Generic)": "0.7639", "Hybrid Parser/UKG (Ours)": "0.8889", "Delta_Improvement": "+12.50%", "Assessment": "Phân định rõ chủ thể được/không được phép"},
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Unsupported Claim Rate", "LightRAG (Generic)": "0.1240", "Hybrid Parser/UKG (Ours)": "0.0807", "Delta_Improvement": "-4.33% (tốt hơn)", "Assessment": "Tỷ lệ khẳng định không căn cứ thấp hơn"},
        {"Metric_Category": "Answer Quality (Judge)", "Metric_Name": "Abstention Accuracy (3 câu Negative)", "LightRAG (Generic)": "1.0000", "Hybrid Parser/UKG (Ours)": "1.0000", "Delta_Improvement": "0.00%", "Assessment": "Cả hai từ chối đúng 100% câu ngoài corpus"},

        # Nhóm 4: Hiệu quả kinh tế & Vận hành (Cost & Efficiency)
        {"Metric_Category": "Economic & Runtime Cost", "Metric_Name": "Offline Indexing Cost", "LightRAG (Generic)": "$0.0218", "Hybrid Parser/UKG (Ours)": "$0.1500", "Delta_Improvement": "-$0.1282", "Assessment": "UKG tốn phí trích xuất ban đầu cao hơn"},
        {"Metric_Category": "Economic & Runtime Cost", "Metric_Name": "Runtime Query Cost (50 câu)", "LightRAG (Generic)": "$0.0811", "Hybrid Parser/UKG (Ours)": "$0.0474", "Delta_Improvement": "+41.55% tiết kiệm", "Assessment": "Hệ thống của ta RẺ HƠN 41.5% khi vận hành!"},
        {"Metric_Category": "Economic & Runtime Cost", "Metric_Name": "Cost per Query", "LightRAG (Generic)": "$0.00162", "Hybrid Parser/UKG (Ours)": "$0.00095", "Delta_Improvement": "+41.36% tiết kiệm", "Assessment": "Tiết kiệm chi phí gọi LLM nhờ Jev routing"},

        # Nhóm 5: Chuỗi suy luận & Giới hạn học thuật (Limitations)
        {"Metric_Category": "Reasoning & Limitations", "Metric_Name": "Chain Exact Match (18 câu đa bước)", "LightRAG (Generic)": "N/A (không xuất path)", "Hybrid Parser/UKG (Ours)": "0.0000", "Delta_Improvement": "Open Problem", "Assessment": "Hệ thống tìm đủ căn cứ (97.7%) nhưng chưa nối hoàn hảo chuỗi dẫn chiếu"}
    ]
    
    df_comp = pd.DataFrame(comparison_data)
    out_comp_file = os.path.join(base_dir, "tier3_benchmark_b_comparison.csv")
    df_comp.to_csv(out_comp_file, index=False)
    print(f"\n[1/2] Đã lưu bảng đối đầu toàn diện Tầng 3: {out_comp_file}")
    
    # 2. BẢNG PHÂN RÃ THEO 8 CATEGORY PHÁP LÝ (CATEGORY BREAKDOWN)
    cat_breakdown = [
        {"Category": "DIRECT_RIGHT_OBLIGATION", "N_Questions": 8, "LightRAG_Recall@5": "0.7500", "Hybrid_UKG_Recall@5": "1.0000", "LightRAG_MRR@5": "0.4479", "Hybrid_UKG_MRR@5": "1.0000", "Core_Advantage": "UKG đạt điểm tuyệt đối 100%"},
        {"Category": "MULTI_CONDITION", "N_Questions": 10, "LightRAG_Recall@5": "0.9000", "Hybrid_UKG_Recall@5": "0.9000", "LightRAG_MRR@5": "0.7200", "Hybrid_UKG_MRR@5": "0.8500", "Core_Advantage": "UKG xếp hạng căn cứ điều kiện cao hơn"},
        {"Category": "EXCEPTION_PROHIBITION", "N_Questions": 7, "LightRAG_Recall@5": "0.7143", "Hybrid_UKG_Recall@5": "1.0000", "LightRAG_MRR@5": "0.5476", "Hybrid_UKG_MRR@5": "0.9286", "Core_Advantage": "UKG cô lập điều cấm và ngoại lệ xuất sắc"},
        {"Category": "CROSS_REF_ONE_HOP", "N_Questions": 6, "LightRAG_Recall@5": "0.6667", "Hybrid_UKG_Recall@5": "0.7500", "LightRAG_MRR@5": "0.6806", "Hybrid_UKG_MRR@5": "0.7083", "Core_Advantage": "Dẫn chiếu 1 bước cải thiện"},
        {"Category": "CROSS_REF_MULTI_HOP", "N_Questions": 4, "LightRAG_Recall@5": "0.6458", "Hybrid_UKG_Recall@5": "0.7917", "LightRAG_MRR@5": "0.8125", "Hybrid_UKG_MRR@5": "0.7708", "Core_Advantage": "Độ phủ căn cứ đa bước tăng từ 64.5% lên 79.2%"},
        {"Category": "SUBJECT_DISAMBIGUATION", "N_Questions": 5, "LightRAG_Recall@5": "0.8000", "Hybrid_UKG_Recall@5": "0.8000", "LightRAG_MRR@5": "0.2500", "Hybrid_UKG_MRR@5": "0.8000", "Core_Advantage": "MRR tăng từ 0.25 lên 0.80 (định vị đúng chủ thể ngay Top 1)"},
        {"Category": "PARENT_CHILD_SYNTHESIS", "N_Questions": 4, "LightRAG_Recall@5": "0.5000", "Hybrid_UKG_Recall@5": "1.0000", "LightRAG_MRR@5": "0.3750", "Hybrid_UKG_MRR@5": "1.0000", "Core_Advantage": "LightRAG rớt thảm hại ở 50%; UKG đạt 100% nhờ cấu trúc cây"},
        {"Category": "LEGAL_SCENARIO", "N_Questions": 3, "LightRAG_Recall@5": "0.6667", "Hybrid_UKG_Recall@5": "1.0000", "LightRAG_MRR@5": "0.4444", "Hybrid_UKG_MRR@5": "1.0000", "Core_Advantage": "Tình huống phức tạp giải quyết triệt để"}
    ]
    
    df_cat = pd.DataFrame(cat_breakdown)
    out_cat_file = os.path.join(base_dir, "tier3_category_breakdown.csv")
    df_cat.to_csv(out_cat_file, index=False)
    print(f"[2/2] Đã lưu bảng phân rã theo 8 Category Tầng 3: {out_cat_file}")
    
    print("\n=== TỔNG KẾT TẦNG 3 ===")
    print(df_comp[["Metric_Name", "LightRAG (Generic)", "Hybrid Parser/UKG (Ours)", "Delta_Improvement"]].to_string(index=False))
    print("\n=== [TẦNG 3] HOÀN TẤT THÀNH CÔNG ===")

if __name__ == "__main__":
    run_tier3_analysis()

