# -*- coding: utf-8 -*-
"""
master_funnel_runner.py — Điều phối toàn bộ luồng thực nghiệm Cái Phễu 3 Tầng:
- Tầng 1: Đánh giá diện rộng (Benchmark A - 512 câu / 2.088 điều)
- Tầng 2: Tối ưu hóa tầng dữ liệu (Ablation 2x2 - M1-M3 Parser)
- Tầng 3: Tối ưu hóa kiến trúc tri thức chuyên sâu (Benchmark B - 50 câu Chương III)

Chạy 1 lệnh duy nhất ra toàn bộ dữ liệu, biểu đồ và bảng đối soát hoàn chỉnh.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time

def run_master_funnel():
    print("=" * 70)
    print("   HỆ THỐNG ĐIỀU PHỐI ĐÁNH GIÁ CÁI PHỄU 3 TẦNG (THE 3-TIER FUNNEL)")
    print("   Đề tài: Đánh giá và Tối ưu hóa các kiến trúc RAG trên nền tảng")
    print("           dữ liệu cấu trúc đặc thù (Luật Việt Nam)")
    print("=" * 70)
    
    t_start = time.time()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tier1_script = os.path.join(base_dir, "tier1_benchmark_a", "run_tier1.py")
    tier1_patch = os.path.join(base_dir, "tier1_benchmark_a", "patch_lightrag_10.py")
    tier2_script = os.path.join(base_dir, "tier2_ablation_2x2", "run_tier2_ablation.py")
    tier3_script = os.path.join(base_dir, "tier3_benchmark_b", "run_tier3.py")
    
    # 1. Chạy vá & chuẩn hóa LightRAG 10 câu
    print("\n>>> BƯỚC 1: CHUẨN HÓA DỮ LIỆU LIGHTRAG (512 CÂU)...")
    os.system(f"python \"{tier1_patch}\"")
    
    # 2. Chạy Tầng 1
    print("\n>>> BƯỚC 2: THỰC THI TẦNG 1 (BENCHMARK A - 3 KIẾN TRÚC CƠ SỞ)...")
    os.system(f"python \"{tier1_script}\"")
    
    # 3. Chạy Tầng 2
    print("\n>>> BƯỚC 3: THỰC THI TẦNG 2 (ABLATION STUDY 2x2 - M1-M3 PARSER)...")
    os.system(f"python \"{tier2_script}\"")
    
    # 4. Chạy Tầng 3
    print("\n>>> BƯỚC 4: THỰC THI TẦNG 3 (BENCHMARK B - ĐỒ THỊ CHUYÊN SÂU)...")
    os.system(f"python \"{tier3_script}\"")
    
    elapsed = time.time() - t_start
    print("\n" + "=" * 70)
    print(f"   TOÀN BỘ TIẾN TRÌNH CÁI PHỄU 3 TẦNG ĐÃ HOÀN TẤT TRONG {elapsed:.2f} GIÂY!")
    print("   Toàn bộ kết quả CSV/JSON đã được lưu tại thư mục: Benchmark/funnel_evaluation/")
    print("=" * 70)

if __name__ == "__main__":
    run_master_funnel()

