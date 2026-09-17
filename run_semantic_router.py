import os
import sys
import json
import logging
import hashlib
from typing import Dict, Any

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from src.semantic_router.semantic_router import SemanticRouter
from scripts.generate_offline_embeddings import ensure_embeddings, get_input_hash

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_semantic_router")

def get_config_hash(config: Dict[str, Any]) -> str:
    """Tạo mã băm cho cấu hình M5."""
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode('utf-8')).hexdigest()

def ensure_routing_candidates(
    input_file: str = "outputs/physical_graphs/physical_graph.json",
    output_file: str = "outputs/candidate_nodes/routing_candidates.json",
    config: Dict[str, Any] = None
) -> bool:
    """
    Chạy M5 Semantic Router an toàn với Level 1 Cache.
    Return True nếu dùng cache, False nếu vừa sinh mới.
    """
    if config is None:
        config = {
            "ablation_mode": "EXP-C", # Max-Fusion
            "threshold_mode": "fixed",
            "threshold": 0.85
        }
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Lỗi: Không tìm thấy {input_file}. Hãy chạy M4 trước.")
        
    logger.info("Đọc Graph từ %s", input_file)
    with open(input_file, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    # Tính input hash
    nodes = graph.get("nodes", [])
    texts = [n.get("properties", {}).get("text", "") for n in nodes]
    current_input_hash = get_input_hash(texts)
    
    # Tính config hash
    current_config_hash = get_config_hash(config)
    
    # LEVEL 1 CACHE CHECK
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                
            meta = cached_data.get("metadata", {})
            cached_input_hash = meta.get("input_hash")
            cached_config_hash = meta.get("config_hash")
            
            if cached_input_hash == current_input_hash and cached_config_hash == current_config_hash:
                logger.info("Cache Hit! Input Graph và Config không đổi. Bỏ qua chạy thuật toán M5.")
                return True
            else:
                logger.info("Cache Miss! Phát hiện thay đổi trong dữ liệu hoặc cấu hình.")
        except json.JSONDecodeError:
            logger.warning("File cache bị lỗi JSON. Sẽ sinh lại.")
    else:
        logger.info("Không tìm thấy file candidate cache. Cần sinh mới.")
        
    # Chuẩn bị Embeddings
    ensure_embeddings(graph_path=input_file)
    
    # Chạy thuật toán
    logger.info("Khởi tạo SemanticRouter mode: %s", config["ablation_mode"])
    router = SemanticRouter(graph=graph, config=config)
    
    logger.info("Đang chạy Routing...")
    results = router.run()
    
    # Lưu file
    logger.info("Xuất file kết quả: %s", output_file)
    metadata = {
        "schema_version": "m5.v2",
        "config": config,
        "config_hash": current_config_hash,
        "input_hash": current_input_hash,
    }
    router.export(results, output_file, metadata=metadata)
    
    # Báo cáo nhanh
    total_evaluated = len(results)
    total_candidates = sum(1 for r in results if r.route == "LLM_CANDIDATE")
    total_rules = sum(1 for r in results if r.route == "RULE_ONLY")
    total_rejects = sum(1 for r in results if r.route == "REJECT")
    
    print("\n--- BÁO CÁO NHANH (M5 - E2E) ---")
    print(f"Total Evaluated: {total_evaluated}")
    print(f"RULE_ONLY      : {total_rules}")
    print(f"LLM_CANDIDATE  : {total_candidates}")
    print(f"REJECT         : {total_rejects}")
    print("--------------------------------\n")
    
    return False

if __name__ == "__main__":
    print("=== CHẠY MODULE 5 (SEMANTIC ROUTER) ===")
    ensure_routing_candidates()
