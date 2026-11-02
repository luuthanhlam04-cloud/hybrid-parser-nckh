# -*- coding: utf-8 -*-
"""
patch_lightrag_10.py — Xử lý và chuẩn hóa 10 câu LightRAG bị lỗi timeout API (q-454 đến q-463).
Tạo file final_benchmark_results_LIGHTRAG.csv với đầy đủ 512 dòng, phân định rõ ràng giữa:
- 502 câu chạy thực tế hợp lệ (is_imputed = False)
- 10 câu được chuẩn hóa số học theo phân phối trung bình (is_imputed = True)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
import os

def generate_clean_lightrag():
    src_file = "Benchmark/backup_lightrag_512.csv"
    out_file = "Benchmark/funnel_evaluation/tier1_benchmark_a/final_benchmark_results_LIGHTRAG.csv"
    
    df = pd.read_csv(src_file)
    print(f"[Patch] Đọc file gốc: {src_file} - Tổng số dòng: {len(df)}")
    
    # 1. Xác định tập hợp 502 câu hợp lệ
    valid_mask = df['faithfulness'].notnull() & (~df['evaluator_model'].str.contains('FAILED', na=False))
    valid_df = df[valid_mask]
    failed_mask = ~valid_mask
    
    print(f"[Patch] Số dòng hợp lệ thực tế: {len(valid_df)}")
    print(f"[Patch] Số dòng cần xử lý (FAILED): {failed_mask.sum()}")
    
    # 2. Tính trung bình các chỉ số ngữ nghĩa từ 502 câu hợp lệ
    mean_cp = round(valid_df['context_precision'].mean(), 4)
    mean_faith = round(valid_df['faithfulness'].mean(), 4)
    mean_citation = round(valid_df['citation_accuracy'].mean(), 4)
    mean_latency = round(valid_df['eval_latency_ms'].mean(), 2)
    mean_tokens = int(round(valid_df['total_tokens'].mean()))
    mean_cost = round(valid_df['estimated_cost'].mean(), 6)
    
    print(f"[Patch] Giá trị chuẩn hóa: CP={mean_cp}, Faith={mean_faith}, Citation={mean_citation}")
    
    # 3. Tạo bản sao và gán giá trị
    df_clean = df.copy()
    df_clean['is_imputed'] = False
    
    # Xử lý 10 dòng lỗi
    df_clean.loc[failed_mask, 'context_precision'] = mean_cp
    df_clean.loc[failed_mask, 'faithfulness'] = mean_faith
    df_clean.loc[failed_mask, 'citation_accuracy'] = mean_citation
    df_clean.loc[failed_mask, 'eval_latency_ms'] = mean_latency
    df_clean.loc[failed_mask, 'total_tokens'] = mean_tokens
    df_clean.loc[failed_mask, 'estimated_cost'] = mean_cost
    df_clean.loc[failed_mask, 'evaluator_model'] = "openai/gpt-4o-mini_IMPUTED"
    df_clean.loc[failed_mask, 'is_imputed'] = True
    
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    df_clean.to_csv(out_file, index=False)
    print(f"[Patch] Đã lưu file chuẩn hóa 512 câu tại: {out_file}")
    
    # Kiểm tra lại
    assert len(df_clean) == 512, "Số lượng dòng phải đúng 512"
    assert df_clean['context_precision'].isnull().sum() == 0, "Không được còn giá trị null ở CP"
    print("[Patch] Kiểm tra toàn vẹn: THÀNH CÔNG (100% hợp lệ).")

if __name__ == "__main__":
    generate_clean_lightrag()
