"""
Integrity Checker - Rà soát các lỗi toàn vẹn cấu trúc đồ thị:
  - DuplicateNodeID (ERROR)
  - OrphanNode (ERROR)
  - BrokenParent (ERROR)
  - CyclicDependency (ERROR)
  - EmptyNode (WARNING)
Nguyên tắc: Chỉ phát hiện, KHÔNG tự sửa dữ liệu.
"""
import logging
from typing import List, Dict, Any, Set

from src.regex_parser.node_generator import LegalNode

logger = logging.getLogger(__name__)


def check_integrity(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """
    Kiểm tra toàn vẹn cấu trúc đồ thị (DAG) cho danh sách LegalNode.

    Returns:
        Danh sách issue dicts.
    """
    issues: List[Dict[str, Any]] = []

    issues.extend(_check_duplicate_ids(nodes))
    issues.extend(_check_orphan_nodes(nodes))
    issues.extend(_check_broken_parents(nodes))
    issues.extend(_check_cyclic_dependencies(nodes))
    issues.extend(_check_empty_nodes(nodes))

    return issues


def _check_duplicate_ids(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """Phát hiện các node có ID trùng lặp."""
    issues: List[Dict[str, Any]] = []
    seen: Dict[str, int] = {}

    for idx, node in enumerate(nodes):
        if node.id in seen:
            issues.append({
                "rule_id": "VAL-001",
                "node_id": node.id,
                "severity": "ERROR",
                "issue_type": "DuplicateNodeID",
                "message": f"Duplicate node ID '{node.id}' found at index {idx}, "
                           f"first seen at index {seen[node.id]}.",
                "position": {"start": node.position.start, "end": node.position.end},
            })
            logger.warning("DuplicateNodeID: '%s' at index %d", node.id, idx)
        else:
            seen[node.id] = idx

    return issues


def _check_orphan_nodes(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """
    Phát hiện node con có parent_id = None.
    Các node top-level (PART, CHAPTER, TEXT ở đầu file) hợp lệ khi parent_id = None.
    """
    issues: List[Dict[str, Any]] = []
    # Top-level types cho phép parent_id = None
    top_level_types = {"PART", "CHAPTER", "TEXT"}

    for node in nodes:
        if node.parent_id is None and node.type.value not in top_level_types:
            issues.append({
                "rule_id": "VAL-002",
                "node_id": node.id,
                "severity": "ERROR",
                "issue_type": "OrphanNode",
                "message": f"Node '{node.id}' (type={node.type.value}) has no parent "
                           f"(parent_id is None).",
                "position": {"start": node.position.start, "end": node.position.end},
            })
            logger.warning("OrphanNode: '%s' (type=%s)", node.id, node.type.value)

    return issues


def _check_broken_parents(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """Phát hiện node con trỏ tới parent_id không tồn tại."""
    issues: List[Dict[str, Any]] = []
    all_ids: Set[str] = {node.id for node in nodes}

    for node in nodes:
        if node.parent_id is not None and node.parent_id not in all_ids:
            issues.append({
                "rule_id": "VAL-003",
                "node_id": node.id,
                "severity": "ERROR",
                "issue_type": "BrokenParent",
                "message": f"Node '{node.id}' has parent_id '{node.parent_id}' "
                           f"which does not exist in the dataset.",
                "position": {"start": node.position.start, "end": node.position.end},
            })
            logger.warning("BrokenParent: '%s' -> '%s'", node.id, node.parent_id)

    return issues


def _check_cyclic_dependencies(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """
    Phát hiện vòng lặp quan hệ cha con bằng thuật toán DFS cycle detection.
    Duyệt từ mỗi node, đi ngược lên theo chuỗi parent_id.
    Nếu gặp lại chính nó thì có chu trình.
    """
    issues: List[Dict[str, Any]] = []
    parent_map: Dict[str, str] = {}
    node_map: Dict[str, LegalNode] = {}

    for node in nodes:
        node_map[node.id] = node
        if node.parent_id is not None:
            parent_map[node.id] = node.parent_id

    reported_cycles: Set[str] = set()

    for node in nodes:
        visited: Set[str] = set()
        current = node.id

        while current in parent_map:
            if current in visited:
                # Tìm thấy cycle
                if current not in reported_cycles:
                    reported_cycles.add(current)
                    target_node = node_map.get(current, node)
                    issues.append({
                        "rule_id": "VAL-004",
                        "node_id": current,
                        "severity": "ERROR",
                        "issue_type": "CyclicDependency",
                        "message": f"Cyclic dependency detected: node '{current}' "
                                   f"is part of a parent-child loop.",
                        "position": {
                            "start": target_node.position.start,
                            "end": target_node.position.end,
                        },
                    })
                    logger.warning("CyclicDependency: '%s'", current)
                break
            visited.add(current)
            current = parent_map[current]

    return issues


def _check_empty_nodes(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """
    Phát hiện node không có nội dung text (WARNING).
    Chỉ kiểm tra CLAUSE, POINT, TEXT — bỏ qua PART, CHAPTER, SECTION, ARTICLE
    vì chúng là container cấu trúc và không bao giờ có body text theo thiết kế.
    """
    issues: List[Dict[str, Any]] = []
    check_types = {"CLAUSE", "POINT", "TEXT"}

    for node in nodes:
        if node.type.value not in check_types:
            continue
        if not node.text or not node.text.strip():
            issues.append({
                "rule_id": "VAL-005",
                "node_id": node.id,
                "severity": "WARNING",
                "issue_type": "EmptyNode",
                "message": f"Node '{node.id}' (type={node.type.value}) has empty text content.",
                "position": {"start": node.position.start, "end": node.position.end},
            })

    return issues
