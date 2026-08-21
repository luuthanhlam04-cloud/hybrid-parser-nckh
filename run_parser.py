import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from regex_parser.parser import parse_document

if __name__ == "__main__":
    input_file = "outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt"
    output_file = "outputs/physical_graphs/raw_nodes.json"
    
    print(f"Parsing {input_file}...")
    try:
        parse_document(input_file, output_file)
        print(f"Success! Output written to {output_file}")
    except Exception as e:
        print(f"Error parsing document: {e}")
