# -*- coding: utf-8 -*-
import sys
import logging
import json
import argparse

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from run_semantic_router import ensure_routing_candidates
from src.llm_extraction.structured_extractor import StructuredExtractor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Chạy Module 6: LLM Structured Extraction")
    parser.add_argument("--limit", type=int, default=0, help="Số lượng candidate node cần bóc tách (0 = tất cả)")
    parser.add_argument("--output", type=str, default="outputs/semantic_graphs/semantic_extraction.json", help="Đường dẫn file output JSON")
    args = parser.parse_args()

    print(f"=== CHAY MODULE 6 (LLM STRUCTURED EXTRACTION V7) - LIMIT: {args.limit} ===")
    
    # Đảm bảo M5 đã chạy (hiệu ứng domino)
    ensure_routing_candidates()
    
    candidates_path = "outputs/candidate_nodes/routing_candidates.json"
    physical_graph_path = "outputs/physical_graphs/physical_graph.json"
    output_path = args.output
    
    try:
        extractor = StructuredExtractor(candidates_path, physical_graph_path)
    except ValueError as e:
        print(f"Lỗi khởi tạo: {e}")
        print("Hãy chắc chắn bạn đã tạo file .env và điền OPENROUTER_API_KEY.")
        return
        
    print("Khởi tạo Extractor thành công. Đang tiến hành bóc tách các nodes.")
    output_data = extractor.run_extraction(limit=args.limit)
    
    print(f"\n=== HOÀN TẤT BÓC TÁCH {len(output_data.get('extracted_nodes', []))} NODES ===")
    extractor.export(output_data, output_path)

if __name__ == "__main__":
    main()