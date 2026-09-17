import os
import sys
import json
import subprocess

def run_tests():
    print("="*60)
    print("1. RUNNING ALL UNIT TESTS (M4 & M5)")
    print("="*60)
    
    # Chạy pytest chỉ cho M4 và M5
    result = subprocess.run(
        [sys.executable, "-m", "pytest", 
         "tests/unit/test_physical_graph.py", 
         "tests/unit/test_embedding_engine.py"], 
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("PHÁT HIỆN LỖI TRONG UNIT TEST!")
        print(result.stderr)
        return False
    return True

def verify_m4_output():
    print("\n" + "="*60)
    print("2. KIỂM TRA ĐẦU VÀO TỪ M4 (physical_graph.json)")
    print("="*60)
    
    graph_path = "outputs/physical_graphs/physical_graph.json"
    if not os.path.exists(graph_path):
        print(f"LỖI: Không tìm thấy {graph_path}")
        return False
        
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    
    print(f"Đã nạp {len(nodes)} nodes và {len(edges)} edges từ M4.")
    
    # Kiểm tra tính toàn vẹn (schema_version)
    graph_metadata = graph.get("graph_metadata", {})
    if "schema_version" not in graph_metadata:
        print("CẢNH BÁO: M4 Graph thiếu schema_version trong graph_metadata")
    else:
        print(f"Graph Schema Version: {graph_metadata['schema_version']}")
        
    return True

def show_m5_output():
    print("\n" + "="*60)
    print("3. HIỂN THỊ KẾT QUẢ M5 (EXP-C: Max-Fusion)")
    print("="*60)
    
    candidates_path = "outputs/candidate_nodes/routing_candidates_expC.json"
    if not os.path.exists(candidates_path):
        print(f"LỖI: Không tìm thấy {candidates_path}")
        return
        
    with open(candidates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    candidates = data.get("candidates", [])
    
    llm_cands = [c for c in candidates if c.get("route") == "LLM_CANDIDATE"]
    rule_only = [c for c in candidates if c.get("route") == "RULE_ONLY"]
    rejects = [c for c in candidates if c.get("route") == "REJECT"]
    
    print(f"Tổng số nodes đã định tuyến: {len(candidates)}")
    print(f"- Đẩy vào LLM (M6): {len(llm_cands)} nodes")
    print(f"- Giải quyết bằng Rule (Không gọi LLM): {len(rule_only)} nodes")
    print(f"- Từ chối (Không chứa ngữ nghĩa chéo): {len(rejects)} nodes")
    
    print("\n--- DANH SÁCH LLM CANDIDATES ---")
    for i, c in enumerate(llm_cands[:20]): # Chỉ hiển thị 20 cái đầu để tránh trôi màn hình
        print(f"\n[{i+1}/{len(llm_cands)}] Node ID: {c['node_id']}")
        print(f"   Reason: {c.get('reason')}")
        print(f"   Score : {c.get('routing_score', 0):.3f}")
        # Lấy text
        text = str(c.get("text", ""))[:150]
        text = text.replace('\n', ' ')
        print(f"   Text  : {text}...")
        
    if len(llm_cands) > 20:
        print(f"\n... (Và {len(llm_cands) - 20} candidates khác đang bị ẩn để dễ nhìn).")

def main():
    print("BẮT ĐẦU TEST E2E M4-M5...\n")
    if not run_tests():
        sys.exit(1)
        
    if not verify_m4_output():
        sys.exit(1)
        
    show_m5_output()
    print("\nHOÀN TẤT E2E TEST!")

if __name__ == "__main__":
    main()
