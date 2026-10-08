import os
import sys
import io
import logging

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from src.physical_graph.graph_builder import PhysicalGraphBuilder

if __name__ == "__main__":
    print("=== CHẠY MODULE 4 (PHYSICAL GRAPH BUILDER) ===")
    
    input_file = "outputs/physical_graphs/validated_nodes.json"
    output_file = "outputs/physical_graphs/physical_graph.json"
    
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy {input_file}. Hãy chạy Module 3 trước.")
        sys.exit(1)
        
    builder = PhysicalGraphBuilder(input_path=input_file, output_path=output_file)
    builder.run()
