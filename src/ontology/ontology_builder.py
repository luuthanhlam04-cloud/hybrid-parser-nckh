import json
import logging
import time
from collections import Counter
from typing import Dict, Any, Generator
from .canonical_mapper import CanonicalMapper
from .entity_normalizer import EntityNormalizer
from .relation_normalizer import RelationNormalizer
from .ontology_validator import OntologyValidator
from .edge_quality_filter import EdgeQualityFilter
from .node_quality_filter import NodeQualityFilter

logger = logging.getLogger(__name__)

class OntologyBuilder:
    """
    Main orchestrator for Module 7.
    """
    def __init__(self):
        self.min_quarantine_occurrences = 2
        self.mapper = CanonicalMapper()
        self.entity_normalizer = EntityNormalizer(taxonomy=self.mapper.get_taxonomy())
        self.relation_normalizer = RelationNormalizer()
        self.validator = OntologyValidator(canonical_mapper=self.mapper)
        self.edge_quality_filter = EdgeQualityFilter(
            relation_types=set(self.mapper.schema.get("relations", {}))
        )
        self.node_quality_filter = NodeQualityFilter()
        
        # Global Registry for Entities (Duplication free)
        self.global_entities: Dict[str, Dict[str, Any]] = {}
        
        # Output Relations
        self.canonical_relations = []
        
        # Validation Metrics
        self.rejected_edges_count = 0
        self.quality_rejected_edges_count = 0
        self.quality_rejection_breakdown = self.edge_quality_filter.rejection_breakdown
        self.quarantined_entities_count = 0
        self.filtered_nodes_count = 0
        self.orphan_entities_count = 0
        self.low_frequency_quarantine_count = 0
        self.relations_removed_with_low_frequency_quarantine = 0
        self.ontology_rejection_breakdown: Counter[str] = Counter()
        self.entity_occurrences: Counter[str] = Counter()

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
            source_node_id, raw_entities, raw_relations = (
                self.node_quality_filter.filter_node(node_item)
            )
            if source_node_id is None:
                self.filtered_nodes_count += 1
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
                self.entity_occurrences[canonical_id] += 1
                
                # Lưu ánh xạ cục bộ
                local_to_canonical[local_id] = canonical_id
                
                if canonical_id.startswith("unassigned."):
                    self.quarantined_entities_count += 1
                
                # Keep entities temporarily; orphan entities are pruned after edge validation.
                if canonical_id not in self.global_entities:
                    self.global_entities[canonical_id] = norm_result

            # 2. Normalize and Validate Relations
            for raw_rel in raw_relations:
                accepted, _ = self.edge_quality_filter.check(raw_rel, source_node_id)
                if not accepted:
                    self.rejected_edges_count += 1
                    self.quality_rejected_edges_count += 1
                    continue

                canonical_rel = self.relation_normalizer.normalize(
                    raw_relation=raw_rel,
                    local_to_canonical=local_to_canonical,
                    source_node_id=source_node_id
                )
                
                if not canonical_rel:
                    self.rejected_edges_count += 1
                    continue
                    
                # 3. Validate against Schema Domain-Range constraints
                is_valid, rejection_reason = self.validator.validate_relation(
                    canonical_rel=canonical_rel,
                    canonical_entities=self.global_entities
                )
                
                if is_valid:
                    self.canonical_relations.append(canonical_rel)
                    self.validator.register_accepted_relation(canonical_rel)
                else:
                    self.rejected_edges_count += 1
                    reason_code = rejection_reason.split(":", 1)[0]
                    self.ontology_rejection_breakdown[reason_code] += 1
                    
        # Keep canonical entities and only recurring quarantine entities.
        quarantine_ids = {
            entity_id
            for entity_id, entity in self.global_entities.items()
            if entity_id.startswith("unassigned.")
            and self.entity_occurrences[entity_id]
            < self.min_quarantine_occurrences
        }
        self.low_frequency_quarantine_count = len(quarantine_ids)
        retained_relations = [
            relation
            for relation in self.canonical_relations
            if relation["source"] not in quarantine_ids
            and relation["target"] not in quarantine_ids
        ]
        self.relations_removed_with_low_frequency_quarantine = (
            len(self.canonical_relations) - len(retained_relations)
        )

        # Only entities participating in an accepted edge belong in the canonical graph.
        referenced_entity_ids = {
            entity_id
            for relation in retained_relations
            for entity_id in (relation["source"], relation["target"])
        }
        orphan_entity_ids = set(self.global_entities) - referenced_entity_ids
        self.orphan_entities_count = len(orphan_entity_ids)
        canonical_entities = [
            entity
            for entity_id, entity in self.global_entities.items()
            if entity_id in referenced_entity_ids
        ]

        # Xuất kết quả
        output_data = {
            "metadata": {
                "ontology_version": "1.3",
                "domain": "Luật Đất đai 2024",
                "generated_by": "M7_Builder",
                "execution_time_seconds": round(time.time() - start_time, 2)
            },
            "entities": canonical_entities,
            "relations": retained_relations,
            "validation_report": {
                "rejected_edges_count": self.rejected_edges_count,
                "quality_rejected_edges_count": self.quality_rejected_edges_count,
                "quality_rejection_breakdown": dict(self.quality_rejection_breakdown),
                "quarantined_entities_count": self.quarantined_entities_count,
                "filtered_nodes_count": self.filtered_nodes_count,
                "orphan_entities_count": self.orphan_entities_count,
                "min_quarantine_occurrences": self.min_quarantine_occurrences,
                "low_frequency_quarantine_count": self.low_frequency_quarantine_count,
                "relations_removed_with_low_frequency_quarantine": (
                    self.relations_removed_with_low_frequency_quarantine
                ),
                "ontology_rejection_breakdown": dict(
                    self.ontology_rejection_breakdown
                ),
                "node_quality_rejection_breakdown": dict(
                    self.node_quality_filter.rejection_breakdown
                ),
            }
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Hoàn tất. Đã lưu đồ thị Ontology vào {output_path}")
        logger.info(f"Entities: {len(canonical_entities)} | Relations: {len(retained_relations)}")
        logger.info(f"Rejected Edges: {self.rejected_edges_count} | Quarantined Entities: {self.quarantined_entities_count}")
