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
logger = logging.getLogger("run_experiments")

def run_experiment(graph, ablation_mode: str, output_file: str):
    logger.info("=========================================")
    logger.info("Chạy %s", ablation_mode)
    
    config = {
        "ablation_mode": ablation_mode,
        "threshold_mode": "fixed",
        "threshold": 0.75
    }
    
    router = SemanticRouter(graph=graph, config=config)
    results = router.run()
    router.export(results, output_file)
    
    total_evaluated = len(results)
    total_candidates = sum(1 for r in results if r.route == "LLM_CANDIDATE")
    total_rules = sum(1 for r in results if r.route == "RULE_ONLY")
    total_rejects = sum(1 for r in results if r.route == "REJECT")
    
    print(f"\n--- BÁO CÁO NHANH (M5 - {ablation_mode}) ---")
    print(f"Total Evaluated: {total_evaluated}")
    print(f"RULE_ONLY      : {total_rules}")
    print(f"LLM_CANDIDATE  : {total_candidates}")
    print(f"REJECT         : {total_rejects}\n")

if __name__ == "__main__":
    input_file = "outputs/physical_graphs/physical_graph.json"
    
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy {input_file}.")
        sys.exit(1)
        
    logger.info("Loading graph từ %s", input_file)
    with open(input_file, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    # Tạo thư mục output
    os.makedirs("outputs/candidate_nodes", exist_ok=True)
    
    # Chạy 3 chế độ Ablation
    run_experiment(graph, "EXP-A", "outputs/candidate_nodes/routing_candidates_expA.json")
    run_experiment(graph, "EXP-B", "outputs/candidate_nodes/routing_candidates_expB.json")
    run_experiment(graph, "EXP-C", "outputs/candidate_nodes/routing_candidates_expC.json")
    
