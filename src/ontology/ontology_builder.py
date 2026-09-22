# -*- coding: utf-8 -*-
"""
ontology_builder.py — Phase 7, Module 7

Pipeline Orchestrator: chain toàn bộ M7 components.

Input:
  - M6 semantic_extraction.json (từ outputs/semantic_graphs/)
  - M4 physical_graph.json (từ outputs/physical_graphs/ hoặc tương đương)

Output:
  - canonical_semantic_graph.json (M8-ready)

Pipeline:
  1. Load M6 + M4
  2. Với mỗi extraction node:
     a. entity_normalizer: semantic-role audit + type mapping
     b. relation_normalizer: modality normalization
     c. canonical_mapper: DENOTES → CanonicalConcept
     d. norm_builder: simple edge hoặc NormAssertion
     e. reference_resolver: REFERENCES → Physical Node
  3. Gom toàn bộ vào CanonicalSemanticGraph
  4. ontology_validator: validate + reject violations
  5. Export canonical_semantic_graph.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.ontology.canonical_mapper import CanonicalMapper
from src.ontology.entity_normalizer import EntityNormalizer
from src.ontology.norm_builder import NormBuilder
from src.ontology.ontology_validator import OntologyValidator
from src.ontology.reference_classifier import ReferenceClassifier
from src.ontology.relation_normalizer import RelationNormalizer
from src.ontology.semantic_quality_gate import SemanticQualityGate
from src.ontology.schemas import (
    CanonicalSemanticGraph,
    LocalMention,
    MentionType,
    NormAssertion,
    SemanticEdge,
)

logger = logging.getLogger(__name__)


class OntologyBuilder:
    """
    Pipeline chính của Module 7.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)

        # Khởi tạo các components
        self.entity_normalizer    = EntityNormalizer(config_dir)
        self.relation_normalizer  = RelationNormalizer(config_dir)
        self.quality_gate         = SemanticQualityGate()
        self.canonical_mapper     = CanonicalMapper(config_dir)
        self.norm_builder         = NormBuilder(config_dir)
        self.reference_classifier = ReferenceClassifier(config_dir)
        self.validator            = OntologyValidator()

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def build(
        self,
        m6_path: Path,
        physical_graph_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> CanonicalSemanticGraph:
        """
        Chạy toàn bộ M7 pipeline.

        Args:
            m6_path:             Path tới semantic_extraction.json
            physical_graph_path: Path tới physical_graph.json (cho reference resolver)
            output_path:         Path để export canonical_semantic_graph.json

        Returns:
            CanonicalSemanticGraph đã validated
        """
        logger.info("=" * 60)
        logger.info("MODULE 7 — Ontology Builder START")
        logger.info("=" * 60)

        # Step 1: Load M6
        logger.info(f"Loading M6 from: {m6_path}")
        m6_data = self._load_json(m6_path)
        extracted_nodes = m6_data.get("extracted_nodes", [])
        logger.info(f"Số extraction nodes: {len(extracted_nodes)}")

        # Step 2: Load Physical Graph (M4)
        physical_graph: Dict[str, Any] = {"nodes": [], "edges": []}
        if physical_graph_path and physical_graph_path.exists():
            logger.info(f"Loading Physical Graph from: {physical_graph_path}")
            physical_graph = self._load_json(physical_graph_path)
        else:
            logger.warning(
                "Physical Graph không được cung cấp hoặc không tồn tại. "
                "Reference resolver sẽ không thể resolve references."
            )

        # Accumulators
        all_mentions:  List[LocalMention]  = []
        all_references: List[Any]          = []
        all_norms:     List[NormAssertion] = []
        all_edges:     List[SemanticEdge]  = []
        norm_index_counter: Dict[str, int] = {}

        # Step 3: Xử lý từng extraction node
        for item in extracted_nodes:
            node_id = item.get("node_id", "")
            extraction = item.get("extraction", {})
            m6_entities_raw = extraction.get("entities", [])
            m6_relations_raw = extraction.get("relations", [])

            if not m6_entities_raw and not m6_relations_raw:
                logger.debug(f"Skip empty node: {node_id}")
                continue

            logger.debug(f"Processing: {node_id} ({len(m6_entities_raw)} entities, {len(m6_relations_raw)} relations)")

            # 3a. Entity Normalizer: semantic-role audit + type mapping
            mentions = self.entity_normalizer.normalize_all(
                m6_entities=m6_entities_raw,
                provenance_node_id=node_id,
            )

            # Build mention_map: m6_local_id → LocalMention (cho relation_normalizer)
            # Map từ m6_local_id gốc (e1, e2, ...) sang LocalMention object
            m6_id_to_local_id: Dict[str, str] = {}
            for raw_ent in m6_entities_raw:
                m6_id = raw_ent.get("id", "")
                m6_type = raw_ent.get("entity_type", "").upper()
                if m6_type in ("PERMISSION", "OBLIGATION"):
                    continue
                # Tìm mention tương ứng theo m6_local_id
                for m in mentions:
                    if m.m6_local_id == m6_id:
                        m6_id_to_local_id[m6_id] = m.id
                        break

            mention_map = {
                m.m6_local_id: m for m in mentions
            }

            # 3b. Relation Normalizer
            normalized_relations, modality_ctx = self.relation_normalizer.normalize_all(
                m6_relations=m6_relations_raw,
                m6_entities_raw=m6_entities_raw,
                mention_map=mention_map,
            )

            # 3b-2. Semantic Quality Gate (Gate 1)
            mentions, normalized_relations = self.quality_gate.evaluate(
                mentions=mentions,
                normalized_relations=normalized_relations,
            )

            # 3c. Canonical Mapper: DENOTES → CanonicalConcept
            denotes_edges = self.canonical_mapper.map_mentions(mentions)
            all_edges.extend(denotes_edges)

            # 3d. Norm Builder: NormAssertion hoặc simple edges
            norms, norm_edges = self.norm_builder.build(
                mentions=mentions,
                normalized_relations=normalized_relations,
                modality_ctx=modality_ctx,
                provenance_node_id=node_id,
                norm_index_counter=norm_index_counter,
            )
            all_norms.extend(norms)
            all_edges.extend(norm_edges)

            # 3e. Reference Classifier
            kept_mentions, ref_mentions = self.reference_classifier.classify_all(
                mentions=mentions,
                m6_relations_raw=m6_relations_raw,
                mention_map=mention_map,
                norms=norms,
                current_provenance_node_id=node_id,
            )
            all_mentions.extend(kept_mentions)
            all_references.extend(ref_mentions)

        # Step 4: Thu thập Canonical Concepts
        concepts = self.canonical_mapper.get_all_concepts()
        logger.info(
            f"Tổng: {len(all_mentions)} mentions, {len(all_norms)} norms, "
            f"{len(concepts)} concepts, {len(all_edges)} edges"
        )

        # Step 5: Assemble graph
        graph = CanonicalSemanticGraph(
            metadata={
                "m6_source": str(m6_path),
                "physical_graph_source": str(physical_graph_path) if physical_graph_path else None,
                "m7_version": "1.0.0",
                "pipeline": [
                    "entity_normalizer",
                    "relation_normalizer",
                    "canonical_mapper",
                    "norm_builder",
                    "reference_classifier",
                    "ontology_validator",
                ],
            },
            active_nodes=all_mentions,
            references=all_references,
            norms=all_norms,
            concepts=concepts,
            active_edges=all_edges,
        )

        # Step 6: Validate
        logger.info("Running ontology validation...")
        graph = self.validator.validate(graph)

        # Step 7: Export
        if output_path:
            self._export(graph, output_path)

        logger.info("=" * 60)
        logger.info(f"MODULE 7 DONE: {graph.summary()}")
        logger.info("=" * 60)

        return graph

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _export(self, graph: CanonicalSemanticGraph, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = graph.model_dump()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported canonical_semantic_graph to: {output_path}")
