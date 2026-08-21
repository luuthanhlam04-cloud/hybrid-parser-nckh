import os
import sys
import json
from pathlib import Path

# Thêm root dir và src/regex_parser vào sys.path để tránh lỗi import
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "regex_parser"))

from src.preprocessing.document_loader import DocxLoader
from src.regex_parser.parser import LegalParser

if __name__ == "__main__":
    print("=== CHẠY M1 -> M2 (DOCX REGRESSION TEST) ===")
    docx_path = "datasets/raw_laws/Luat_dat_dai_chuong_3.docx"
    output_path = "outputs/physical_graphs/raw_nodes_clean_Luat_dat_dai_chuong_3.json"
    
    if not os.path.exists(docx_path):
        print(f"Lỗi: Không tìm thấy file {docx_path}")
        sys.exit(1)
        
    print(f"[M1] Đang nạp DOCX và trích xuất cấu trúc từ: {docx_path}...")
    loader = DocxLoader()
    paragraphs = loader.load_structured(docx_path)
    
    print("[M2] Đang parse văn bản (Sử dụng metadata M1 + Hybrid ID)...")
    parser = LegalParser(law_prefix="doc", law_code="59/2024/QH15", source_doc="Luat_dat_dai_chuong_3.docx")
    result = parser.parse_structured(paragraphs, source_doc="Luat_dat_dai_chuong_3.docx")
    
    # Fail-Fast: duplicate ID check
    seen_ids = set()
    for node in result.nodes:
        if node["id"] in seen_ids:
            print(f"CRITICAL ERROR: Phát hiện ID trùng lặp: {node['id']}")
            sys.exit(1)
        seen_ids.add(node["id"])
    
    parser.save_json(result, output_path)
    result.print_summary()
    print(f"Thành công! Output đã lưu tại {output_path}")
