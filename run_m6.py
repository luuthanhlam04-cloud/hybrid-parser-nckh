import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(__file__))

from run_semantic_router import ensure_routing_candidates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_m6")

def main():
    print("=== CHẠY MODULE 6 (GRAPH CONSTRUCTION) ===")
    
    # 1. Kích hoạt hiệu ứng Domino ngược để đảm bảo M5 (và M4) đã chạy
    logger.info("Kiểm tra và chuẩn bị dữ liệu đầu vào từ M5...")
    ensure_routing_candidates()
    
    # 2. Nạp dữ liệu
    candidates_path = "outputs/candidate_nodes/routing_candidates.json"
    if not os.path.exists(candidates_path):
        logger.error(f"Không tìm thấy {candidates_path}. Có lỗi xảy ra trong M5.")
        sys.exit(1)
        
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    candidates = data.get("candidates", [])
    llm_cands = [c for c in candidates if c.get("route") == "LLM_CANDIDATE"]
    
    logger.info(f"Đã nạp {len(llm_cands)} nodes để đưa vào LLM.")
    
    # TODO: Khởi tạo Prompt và gọi API LLM ở đây
    print("\n[M6] Đã sẵn sàng thiết kế Schema và gọi LLM API!")

if __name__ == "__main__":
    main()
