import os
import sys

def main():
    from src.ontology.ontology_builder import OntologyBuilder
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "outputs", "semantic_graphs", "semantic_extraction.json")
    output_path = os.path.join(base_dir, "outputs", "semantic_graphs", "canonical_semantic_graph.json")
    
    if not os.path.exists(input_path):
        print(f"Error: Lỗi không tìm thấy file đầu vào tại {input_path}")
        sys.exit(1)
        
    builder = OntologyBuilder()
    builder.build_canonical_graph(input_path, output_path)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    main()
