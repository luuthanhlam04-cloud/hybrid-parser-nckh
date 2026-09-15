import os
import sys
import json
import logging
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

sys.path.insert(0, os.path.dirname(__file__))

from run_semantic_router import ensure_routing_candidates
from src.llm_extraction.structured_extractor import StructuredExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_m6")

def main():
    parser = argparse.ArgumentParser(description="Chạy Module 6: LLM Structured Extraction (E2E Pipeline)")
    parser.add_argument("--limit", type=int, default=0, help="Số lượng candidate node cần bóc tách (0 = tất cả)")
    parser.add_argument("--output", type=str, default="outputs/semantic_graphs/semantic_extraction_v0.json", help="Đường dẫn file output JSON tạm thời của M6")
    args = parser.parse_args()

    print("=== CHẠY MODULE 6 (GRAPH CONSTRUCTION - PROTOTYPE V0) ===")
    
    # 1. Kích hoạt hiệu ứng Domino ngược để đảm bảo M5 (và M4) đã chạy
    logger.info("Kiểm tra và chuẩn bị dữ liệu đầu vào từ M5 (Contract)...")
    ensure_routing_candidates()
    
    # 2. Định nghĩa Contract Files
    candidates_path = "outputs/candidate_nodes/routing_candidates.json"
    physical_graph_path = "outputs/physical_graphs/physical_graph.json"
    output_path = args.output
    
    if not os.path.exists(candidates_path):
        logger.error(f"Không tìm thấy {candidates_path}. Có lỗi xảy ra trong M5.")
        sys.exit(1)
        
    # 3. Gọi Extractor của Minh
    try:
        extractor = StructuredExtractor(candidates_path, physical_graph_path)
    except ValueError as e:
        logger.error(f"Lỗi khởi tạo Extractor: {e}")
        logger.error("Hãy chắc chắn bạn đã tạo file .env và điền OPENROUTER_API_KEY.")
        sys.exit(1)
        
    logger.info(f"Khởi tạo Extractor thành công. Đang bóc tách (limit={args.limit})...")
    output_data = extractor.run_extraction(limit=args.limit)
    
    print(f"\n=== HOÀN TẤT BÓC TÁCH {len(output_data.get('extracted_nodes', []))} NODES ===")
    extractor.export(output_data, output_path)
    logger.info(f"File output tạm thời được ghi tại: {output_path}")

if __name__ == "__main__":
    main()
