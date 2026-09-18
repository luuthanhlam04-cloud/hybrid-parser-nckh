import json
import logging
import time
from typing import Dict, Any, Generator
from collections import Counter
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
        self.canonical_entities: Dict[str, Dict[str, Any]] = {}
        self.quarantine_entities: list = []
        
        # Output Relations
        self.canonical_relations: list = []
        self.seen_canonical_edges: Dict[tuple, Dict[str, Any]] = {}
        
        # Validation Metrics
        self.rejection_breakdown = Counter()
        self.input_entities_count = 0
        self.input_relations_count = 0

    def _stream_nodes(self, input_path: str) -> Generator[Dict[str, Any], None, None]:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            extracted_nodes = data.get("extracted_nodes", [])
            for node_item in extracted_nodes:
                yield node_item

    def build_canonical_graph(self, input_path: str, output_path: str):
        start_time = time.time()
        logger.info(f"Bắt đầu xây dựng Ontology từ {input_path}")
        
        for node_item in self._stream_nodes(input_path):
            source_node_id = node_item.get("node_id")
            extraction = node_item.get("extraction", {})
            raw_entities = extraction.get("entities", [])
            raw_relations = extraction.get("relations", [])
            
            if not raw_entities and not raw_relations:
                continue
                
            self.input_entities_count += len(raw_entities)
            self.input_relations_count += len(raw_relations)
            
            local_to_canonical = {}
            
            # 1. Normalize Entities
            for raw_ent in raw_entities:
                local_id = raw_ent.get("id")
                raw_text = raw_ent.get("text")
                fallback_type = raw_ent.get("entity_type")
                
                norm_result = self.entity_normalizer.normalize(
                    raw_text=raw_text, 
                    fallback_type=fallback_type, 
                    source_node_id=source_node_id, 
                    local_id=local_id
                )
                canonical_id = norm_result["canonical_id"]
                
                local_to_canonical[local_id] = canonical_id
                
                if canonical_id.startswith("UNRESOLVED:"):
                    self.quarantine_entities.append(norm_result)
                else:
                    if canonical_id not in self.canonical_entities:
                        self.canonical_entities[canonical_id] = norm_result
                        
            # 2. Normalize and Validate Relations
            for raw_rel in raw_relations:
                canonical_rel = self.relation_normalizer.normalize(
                    raw_relation=raw_rel,
                    local_to_canonical=local_to_canonical,
                    source_node_id=source_node_id
                )
                
                if not canonical_rel:
                    continue
                    
                source_canonical = canonical_rel.get("source")
                target_canonical = canonical_rel.get("target")
                
                if source_canonical.startswith("UNRESOLVED:") or target_canonical.startswith("UNRESOLVED:"):
                    self.rejection_breakdown["SOURCE_OR_TARGET_UNRESOLVED"] += 1
                    continue
                    
                # 3. Validate against Schema Domain-Range constraints
                is_valid, reason = self.validator.validate_relation(
                    canonical_rel=canonical_rel,
                    canonical_entities=self.canonical_entities
                )
                
                if is_valid:
                    # 4. Relation Deduplication
                    dedup_key = (
                        source_canonical,
                        canonical_rel.get("relation_type"),
                        target_canonical,
                        source_node_id,
                        canonical_rel.get("logic_group", ""),
                        canonical_rel.get("operator", "")
                    )
                    
                    if dedup_key in self.seen_canonical_edges:
                        self.rejection_breakdown["DUPLICATE_RELATION"] += 1
                        existing_edge = self.seen_canonical_edges[dedup_key]
                        new_evidence = canonical_rel.get("evidence", "")
                        if new_evidence and new_evidence not in existing_edge["evidence"]:
                            existing_edge["evidence"] += f" | {new_evidence}"
                    else:
                        self.seen_canonical_edges[dedup_key] = canonical_rel
                        self.canonical_relations.append(canonical_rel)
                else:
                    self.rejection_breakdown[reason] += 1
                    
        # Xuất kết quả
        output_data = {
            "metadata": {
                "ontology_version": "1.3",
                "domain": "Luật Đất đai 2024",
                "generated_by": "M7_Builder",
                "execution_time_seconds": round(time.time() - start_time, 2)
            },
            "canonical_entities": list(self.canonical_entities.values()),
            "canonical_relations": self.canonical_relations,
            "quarantine_entities": self.quarantine_entities,
            "validation_report": {
                "input_entities": self.input_entities_count,
                "input_relations": self.input_relations_count,
                "canonical_entities": len(self.canonical_entities),
                "canonical_relations": len(self.canonical_relations),
                "quarantined_entities": len(self.quarantine_entities),
                "rejected_relations": sum(self.rejection_breakdown.values()),
                "rejection_breakdown": dict(self.rejection_breakdown)
            }
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Hoàn tất. Đã lưu đồ thị Ontology vào {output_path}")
        logger.info(f"Canonical Entities: {len(self.canonical_entities)} | Canonical Relations: {len(self.canonical_relations)}")
        logger.info(f"Quarantined Entities: {len(self.quarantine_entities)}")
        logger.info(f"Rejected Edges Breakdown: {dict(self.rejection_breakdown)}")