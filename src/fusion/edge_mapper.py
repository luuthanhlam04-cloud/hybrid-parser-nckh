"""Edge conversion and confidence calibration for Module 8."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def calibrated_confidence(edge: Dict[str, Any], source_node: Dict[str, Any]) -> float:
    properties = edge.get("properties", {})
    signals = []
    for key in ("confidence_m6", "similarity", "sim_vector"):
        value = properties.get(key)
        if value is not None:
            signals.append(_clamp(float(value)))
    evidence_confidence = (
        1 - _product(1 - signal for signal in signals)
        if signals
        else 0.5
    )
    source_weight = properties.get(
        "source_confidence", source_node.get("source_confidence", 1.0)
    )
    return round(_clamp(evidence_confidence * _clamp(float(source_weight))), 4)


def _product(values: Any) -> float:
    result = 1.0
    for value in values:
        result *= value
    return result


@dataclass
class EdgeMapper:
    calibrator: Any | None = None

    def _confidence(self, properties: Dict[str, Any], source_node: Dict[str, Any]) -> float:
        raw_confidence = calibrated_confidence({"properties": properties}, source_node)
        properties["confidence_raw"] = raw_confidence
        if self.calibrator is None:
            properties["confidence_status"] = "heuristic_uncalibrated"
            return raw_confidence
        properties["confidence_status"] = "calibrated"
        return round(_clamp(float(self.calibrator.predict(raw_confidence))), 4)

    def physical(self, edge: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source": edge["source"], "target": edge["target"], "type": edge["type"],
            "properties": dict(edge.get("properties", {})), "provenance": ["M4"],
        }

    def semantic(
        self, relation: Dict[str, Any], source_node: Dict[str, Any],
        resolved_context_node_id: str | None = None,
        resolved_reference_node_ids: list[str] | None = None,
    ) -> Dict[str, Any]:
        properties = {
            key: value for key, value in relation.items()
            if key not in {"source", "target", "relation_type"}
        }
        properties["provenance"] = "M7"
        properties["confidence"] = self._confidence(properties, source_node)
        if resolved_context_node_id:
            properties["resolved_context_node_id"] = resolved_context_node_id
        if resolved_reference_node_ids:
            properties["resolved_reference_node_ids"] = resolved_reference_node_ids
        return {
            "source": relation["source"], "target": relation["target"],
            "type": relation["relation_type"], "properties": properties,
            "provenance": ["M7"],
        }

    def mentions(self, source_node_id: str, entity_id: str, evidence: str = "") -> Dict[str, Any]:
        return {
            "source": source_node_id, "target": entity_id, "type": "MENTIONS",
            "properties": {"evidence": evidence, "provenance": "M7", "confidence": 1.0},
            "provenance": ["M7"],
        }

    def resolves_to(
        self, reference_entity_id: str, physical_node_id: str, relation_id: str | None
    ) -> Dict[str, Any]:
        return {
            "source": reference_entity_id,
            "target": physical_node_id,
            "type": "RESOLVES_TO",
            "properties": {
                "relation_id": relation_id,
                "provenance": "M8",
                "confidence": 1.0,
            },
            "provenance": ["M8"],
        }