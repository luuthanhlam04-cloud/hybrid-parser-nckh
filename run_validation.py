import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Thêm root dir và src/regex_parser vào sys.path để tránh lỗi import
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "regex_parser"))

import logging
logging.basicConfig(level=logging.INFO)

from src.validation import ValidationEngine

if __name__ == "__main__":
    print("=== CHẠY MODULE 3 (VALIDATION ENGINE) ===")
    input_file = "outputs/physical_graphs/raw_nodes_clean_Luat_dat_dai_chuong_3.json"
    
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy {input_file}. Hãy chạy python run_parser.py trước.")
        sys.exit(1)
        
    engine = ValidationEngine(input_path=input_file)
    report = engine.run()

    s = report["summary"]
    print("\n--- BÁO CÁO NHANH ---")
    print(f"Score:     {s['structural_integrity_score']}%")
    print(f"Errors:    {s['fatal_errors_count']}")
    print(f"Warnings:  {s['warnings_count']}")
    print(f"Validated: {s['total_nodes_validated']}/{s['total_nodes_received']}")
