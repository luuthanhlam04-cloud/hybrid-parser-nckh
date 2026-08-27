import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(__file__))

from src.semantic_router.semantic_router import SemanticRouter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_semantic_router")

if __name__ == "__main__":
    print("=== CHẠY MODULE 5 (SEMANTIC ROUTER) ===")
    
    input_file = "outputs/physical_graphs/physical_graph.json"
    output_file = "outputs/candidate_nodes/routing_candidates.json"
    
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy {input_file}. Hãy chạy python run_physical_graph.py trước.")
        sys.exit(1)
        
    logger.info("Loading graph từ %s", input_file)
    with open(input_file, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    config = {
        "ablation_mode": "EXP-A", # Baseline 1: Regex-only
        "threshold_mode": "fixed",
        "threshold": 0.75
    }
    
    logger.info("Khởi tạo SemanticRouter mode: %s", config["ablation_mode"])
    router = SemanticRouter(graph=graph, config=config)
    
    logger.info("Đang chạy Routing...")
    results = router.run()
    
    logger.info("Xuất file kết quả: %s", output_file)
    router.export(results, output_file)
    
    # In báo cáo nhanh
    total_evaluated = len(results)
    total_candidates = sum(1 for r in results if r.route == "LLM_CANDIDATE")
    total_rules = sum(1 for r in results if r.route == "RULE_ONLY")
    total_rejects = sum(1 for r in results if r.route == "REJECT")
    
    print("\n--- BÁO CÁO NHANH (M5 - EXP-A) ---")
    print(f"Total Evaluated: {total_evaluated}")
    print(f"RULE_ONLY      : {total_rules}")
    print(f"LLM_CANDIDATE  : {total_candidates}")
    print(f"REJECT         : {total_rejects}")
    
