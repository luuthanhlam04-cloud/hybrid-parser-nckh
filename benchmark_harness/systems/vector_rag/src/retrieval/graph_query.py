"""Parameterized Neo4j traversal queries for M10 retrieval modes."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class GraphQuery:
	"""Retrieve norm-aware records or a bounded generic subgraph from UKG."""

	MODE_A_QUERY = """
		UNWIND $anchor_ids AS anchor_id
		MATCH (anchor:UKG_NODE:LegalNode {id: anchor_id})-[:MENTIONS]->
			  (norm:UKG_NODE:GLOBAL_NORM)
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_SUBJECT]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS subjects
		}
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_ACTION]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS actions
		}
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_OBJECT]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS objects
		}
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_CONDITION]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS conditions
		}
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_EXCEPTION]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS exceptions
		}
		CALL {
			WITH norm
			OPTIONAL MATCH (norm)-[:HAS_CONSEQUENCE]->(entity:UKG_NODE)
			RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {
				id: entity.id,
				text: coalesce(entity.canonical_text, entity.preferred_name, entity.id)
			} END) AS consequences
		}
			 OPTIONAL MATCH (anchor)-[:BELONG_TO*0..3]->(article:UKG_NODE:ARTICLE)
		RETURN anchor.id AS anchor_id,
			   anchor.text AS anchor_text,
			   anchor.number AS anchor_number,
				 labels(anchor) AS anchor_labels,
			   anchor.title AS anchor_title,
			   anchor.law_code AS law_code,
				 article.number AS article_number,
			   norm.id AS norm_id,
			   norm.modality AS modality,
			   norm.status AS status,
			   norm.evidence AS evidence,
			   subjects, actions, objects, conditions, exceptions, consequences
		ORDER BY anchor_id, norm_id
		LIMIT $limit
	"""

	MODE_B_QUERY_TEMPLATE = """
		UNWIND $anchor_ids AS anchor_id
		MATCH (anchor:UKG_NODE:LegalNode {id: anchor_id})
		MATCH path=(anchor)-[*1..{max_hops}]-(neighbor:UKG_NODE)
		WHERE neighbor <> anchor
		RETURN DISTINCT anchor.id AS anchor_id,
			   [node IN nodes(path) | {
				   id: node.id,
				   node_kind: node.node_kind,
				   labels: labels(node),
				   properties: properties(node)
			   }] AS nodes,
			   [rel IN relationships(path) | {
				   type: type(rel),
				   properties: properties(rel)
			   }] AS relationships
		LIMIT $max_paths
	"""

	def __init__(self, driver: Any, database: str | None = None) -> None:
		self.driver = driver
		self.database = database

	@staticmethod
	def _validate_anchor_ids(anchor_ids: Sequence[str]) -> list[str]:
		if isinstance(anchor_ids, (str, bytes)):
			raise ValueError("anchor_ids must be a sequence of node IDs, not a string.")
		normalized: list[str] = []
		for anchor_id in anchor_ids:
			if not isinstance(anchor_id, str) or not anchor_id.strip():
				raise ValueError("Every anchor ID must be a non-empty string.")
			if anchor_id not in normalized:
				normalized.append(anchor_id)
		return normalized

	@staticmethod
	def _positive_int(value: int, name: str) -> None:
		if isinstance(value, bool) or not isinstance(value, int) or value < 1:
			raise ValueError(f"{name} must be a positive integer.")

	def retrieve_mode_a(
		self, anchor_ids: Sequence[str], *, limit: int = 20
	) -> list[dict[str, Any]]:
		"""Return complete GLOBAL_NORM records connected to the physical anchors."""
		anchors = self._validate_anchor_ids(anchor_ids)
		self._positive_int(limit, "limit")
		if not anchors:
			return []

		with self.driver.session(database=self.database) as session:
			result = session.run(self.MODE_A_QUERY, anchor_ids=anchors, limit=limit)
			return [dict(record) for record in result]

	def retrieve_mode_b(
		self,
		anchor_ids: Sequence[str],
		*,
		max_hops: int = 2,
		max_paths: int = 100,
	) -> list[dict[str, Any]]:
		"""Return bounded generic paths without interpreting normative structure."""
		anchors = self._validate_anchor_ids(anchor_ids)
		self._positive_int(max_hops, "max_hops")
		self._positive_int(max_paths, "max_paths")
		if max_hops > 3:
			raise ValueError("max_hops cannot exceed 3.")
		if not anchors:
			return []

		query = self.MODE_B_QUERY_TEMPLATE.replace("{max_hops}", str(max_hops))
		with self.driver.session(database=self.database) as session:
			result = session.run(
				query,
				anchor_ids=anchors,
				max_paths=max_paths,
			)
			return [dict(record) for record in result]
