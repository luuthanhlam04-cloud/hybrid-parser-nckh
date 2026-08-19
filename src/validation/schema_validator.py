"""
Schema Validator - Kiểm tra tính hợp lệ của Pydantic schema cho từng node.
Nguyên tắc: Chỉ phát hiện, KHÔNG tự sửa dữ liệu.
"""
import logging
from typing import List, Dict, Any

from pydantic import ValidationError
from src.regex_parser.node_generator import LegalNode

logger = logging.getLogger(__name__)


def validate_schema(raw_nodes: List[Dict[str, Any]]) -> tuple[List[LegalNode], List[Dict[str, Any]]]:
    """
    Kiểm tra từng raw dict có khớp Pydantic LegalNode schema hay không.

    Returns:
        tuple: (valid_nodes, issues)
            - valid_nodes: Danh sách LegalNode đã parse thành công.
            - issues: Danh sách các issue dict cho các node lỗi schema.
    """
    valid_nodes: List[LegalNode] = []
    issues: List[Dict[str, Any]] = []

    for idx, raw in enumerate(raw_nodes):
        try:
            node = LegalNode.model_validate(raw)
            valid_nodes.append(node)
        except ValidationError as e:
            node_id = raw.get("id", f"unknown_index_{idx}")
            position = raw.get("position", {"start": -1, "end": -1})
            issues.append({
                "rule_id": "VAL-000",
                "node_id": node_id,
                "severity": "ERROR",
                "issue_type": "SchemaViolation",
                "message": f"Pydantic schema validation failed: {str(e)}",
                "position": position,
            })
            logger.warning("SchemaViolation for node '%s': %s", node_id, e)

    return valid_nodes, issues
