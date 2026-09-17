import json
import logging
import time
from typing import Dict, Any, Generator
from .canonical_mapper import CanonicalMapper
from .entity_normalizer import EntityNormalizer
from .relation_normalizer import RelationNormalizer
from .ontology_validator import OntologyValidator

logger = logging.getLogger(__name__)

class OntologyBuilder:
    """
    Main orchestrator for Module 7.
    """
    def __init__(self):
        self.mapper = CanonicalMapper()
        self.entity_normalizer = EntityNormalizer(taxonomy=self.mapper.get_taxonomy())
        self.relation_normalizer = RelationNormalizer()
        self.validator = OntologyValidator(canonical_mapper=self.mapper)
        
        # Global Registry for Entities (Duplication free)
        self.global_entities: Dict[str, Dict[str, Any]] = {}
        
        # Output Relations
        self.canonical_relations = []
        
        # Validation Metrics
        self.rejected_edges_count = 0
        self.quarantined_entities_count = 0

    def _stream_nodes(self, input_path: str) -> Generator[Dict[str, Any], None, None]:
        """
        Đọc file JSON đầu vào theo luồng (Generator) để tối ưu bộ nhớ.
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # In a true huge-file scenario, ijson could be used here. 
            # For this context, yielding from the loaded list is acceptable as approved.
            extracted_nodes = data.get("extracted_nodes", [])
            for node_item in extracted_nodes:
                yield node_item

    def build_canonical_graph(self, input_path: str, output_path: str):
        """
        Thực thi toàn bộ quy trình của M7.
        """
        start_time = time.time()
        logger.info(f"Bắt đầu xây dựng Ontology từ {input_path}")
        
        for node_item in self._stream_nodes(input_path):
            source_node_id = node_item.get("node_id")
            extraction = node_item.get("extraction", {})
            raw_entities = extraction.get("entities", [])
            raw_relations = extraction.get("relations", [])
            
            if not raw_entities and not raw_relations:
                continue
                
            # Ràng buộc 1: Local ID Mapping Scope (chỉ có giá trị cục bộ trong 1 node)
            local_to_canonical = {}
            
            # 1. Normalize Entities
            for raw_ent in raw_entities:
                local_id = raw_ent.get("id")
                raw_text = raw_ent.get("text")
                fallback_type = raw_ent.get("entity_type")
                raw_evidence = raw_ent.get("evidence", "")
                
                norm_result = self.entity_normalizer.normalize(raw_text, fallback_type)
                canonical_id = norm_result["canonical_id"]
                
                # Lưu ánh xạ cục bộ
                local_to_canonical[local_id] = canonical_id
                
                if canonical_id.startswith("unassigned."):
                    self.quarantined_entities_count += 1
                
                # Ràng buộc 2: Entity Array Aggregation (Chỉ lấy thông tin cơ bản)
                if canonical_id not in self.global_entities:
                    self.global_entities[canonical_id] = norm_result
                        
            # 2. Normalize and Validate Relations
            for raw_rel in raw_relations:
                canonical_rel = self.relation_normalizer.normalize(
                    raw_relation=raw_rel,
                    local_to_canonical=local_to_canonical,
                    source_node_id=source_node_id
                )
                
                if not canonical_rel:
                    self.rejected_edges_count += 1
                    continue
                    
                # 3. Validate against Schema Domain-Range constraints
                is_valid = self.validator.validate_relation(
                    canonical_rel=canonical_rel,
                    canonical_entities=self.global_entities
                )
                
                if is_valid:
                    self.canonical_relations.append(canonical_rel)
                else:
                    self.rejected_edges_count += 1
                    
        # Xuất kết quả
        output_data = {
            "metadata": {
                "ontology_version": "1.3",
                "domain": "Luật Đất đai 2024",
                "generated_by": "M7_Builder",
                "execution_time_seconds": round(time.time() - start_time, 2)
            },
            "entities": list(self.global_entities.values()),
            "relations": self.canonical_relations,
            "validation_report": {
                "rejected_edges_count": self.rejected_edges_count,
                "quarantined_entities_count": self.quarantined_entities_count
            }
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Hoàn tất. Đã lưu đồ thị Ontology vào {output_path}")
        logger.info(f"Entities: {len(self.global_entities)} | Relations: {len(self.canonical_relations)}")
        logger.info(f"Rejected Edges: {self.rejected_edges_count} | Quarantined Entities: {self.quarantined_entities_count}")
