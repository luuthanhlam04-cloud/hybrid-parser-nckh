import json
from typing import List
from .boundary_detector import BoundaryDetector
from .hierarchy_builder import HierarchyBuilder
from .node_generator import LegalNode

class RegexParser:
    def __init__(self):
        self.boundary_detector = BoundaryDetector()
        self.hierarchy_builder = HierarchyBuilder()

    def parse(self, text: str) -> List[LegalNode]:
        chunks = self.boundary_detector.detect_boundaries(text)
        nodes = self.hierarchy_builder.build_hierarchy(chunks)
        return nodes

    def parse_to_json(self, text: str) -> str:
        nodes = self.parse(text)
        return json.dumps([node.model_dump() for node in nodes], ensure_ascii=False, indent=2)

def parse_document(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    parser = RegexParser()
    nodes = parser.parse(text)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([node.model_dump() for node in nodes], f, ensure_ascii=False, indent=2)
