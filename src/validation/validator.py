"""
Validator - Main Orchestrator điều phối toàn bộ pipeline validation.
Luồng: raw_nodes.json -> Schema -> Integrity -> Sequence -> Filter -> Output
Nguyên tắc: Chỉ phát hiện, lọc và báo cáo lỗi, TUYỆT ĐỐI KHÔNG TỰ SỬA DỮ LIỆU.
"""
import json
import logging
from typing import List, Dict, Any

from src.regex_parser.node_generator import LegalNode
from .schema_validator import validate_schema
from .integrity_checker import check_integrity
from .sequence_checker import check_sequences
from .report_generator import generate_report

logger = logging.getLogger(__name__)


class ValidationEngine:
    """
    Orchestrator chính cho Module 3 - Validation Engine (Quality Gate).
    """

    def __init__(
        self,
        input_path: str = "outputs/physical_graphs/raw_nodes.json",
        validated_output_path: str = "outputs/physical_graphs/validated_nodes.json",
        report_output_path: str = "outputs/physical_graphs/validation_report.json",
    ):
        self.input_path = input_path
        self.validated_output_path = validated_output_path
        self.report_output_path = report_output_path

    def run(self) -> Dict[str, Any]:
        """
        Chạy toàn bộ pipeline validation.

        Returns:
            Report dict hoàn chỉnh.
        """
        logger.info("=== VALIDATION ENGINE START ===")

        # Phase 1: Load raw nodes
        raw_nodes = self._load_raw_nodes()
        total_nodes_received = len(raw_nodes)
        logger.info("Loaded %d raw nodes from '%s'", total_nodes_received, self.input_path)

        # Phase 2: Schema validation
        valid_nodes, schema_issues = validate_schema(raw_nodes)
        logger.info(
            "Schema validation: %d passed, %d failed",
            len(valid_nodes), len(schema_issues),
        )

        # Phase 3: Integrity check
        integrity_issues = check_integrity(valid_nodes)
        logger.info("Integrity check: %d issues found", len(integrity_issues))

        # Phase 4: Sequence check
        sequence_issues = check_sequences(valid_nodes)
        logger.info("Sequence check: %d issues found", len(sequence_issues))

        # Aggregate all issues
        all_issues = schema_issues + integrity_issues + sequence_issues

        # Phase 5: Filter out ERROR nodes -> validated_nodes
        validated_nodes = self._filter_error_nodes(valid_nodes, all_issues)
        logger.info(
            "Filtering: %d nodes passed -> validated_nodes.json",
            len(validated_nodes),
        )

        # Phase 6: Write validated_nodes.json
        self._write_validated_nodes(validated_nodes)

        # Phase 7: Generate report
        report = generate_report(
            total_nodes_received=total_nodes_received,
            all_issues=all_issues,
            output_path=self.report_output_path,
        )

        logger.info("=== VALIDATION ENGINE COMPLETE ===")
        return report

    def validate_nodes(self, nodes: List[LegalNode]) -> tuple[List[LegalNode], Dict[str, Any]]:
        """
        API dùng cho unit test: Nhận trực tiếp danh sách LegalNode,
        chạy integrity + sequence check, trả về validated nodes và report.
        """
        total_received = len(nodes)

        integrity_issues = check_integrity(nodes)
        sequence_issues = check_sequences(nodes)
        all_issues = integrity_issues + sequence_issues

        validated_nodes = self._filter_error_nodes(nodes, all_issues)

        fatal_count = sum(1 for i in all_issues if i["severity"] == "ERROR")
        warning_count = sum(1 for i in all_issues if i["severity"] == "WARNING")
        validated_count = len(validated_nodes)
        score = round((1 - (fatal_count / total_received)) * 100, 2) if total_received > 0 else 100.0

        report = {
            "summary": {
                "total_nodes_received": total_received,
                "total_nodes_validated": validated_count,
                "fatal_errors_count": fatal_count,
                "warnings_count": warning_count,
                "structural_integrity_score": score,
            },
            "issues": all_issues,
        }

        return validated_nodes, report

    def _load_raw_nodes(self) -> List[Dict[str, Any]]:
        """Đọc file raw_nodes.json."""
        with open(self.input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _filter_error_nodes(
        self,
        nodes: List[LegalNode],
        all_issues: List[Dict[str, Any]],
    ) -> List[LegalNode]:
        """
        Lọc bỏ các node bị đánh dấu ERROR (quarantine) VÀ tất cả các
        node con cháu của chúng (Cascading Quarantine) để tránh BrokenParent
        dây chuyền trong file output.
        """
        # Bước 1: Thu thập tập hợp node ID bị ERROR trực tiếp
        quarantined_ids = {
            issue["node_id"]
            for issue in all_issues
            if issue["severity"] == "ERROR"
        }

        # Bước 2: Xây dựng map parent -> children để duyệt nhanh
        children_map: Dict[str, List[LegalNode]] = {}
        for node in nodes:
            if node.parent_id is not None:
                children_map.setdefault(node.parent_id, []).append(node)

        # Bước 3: Cascading — BFS/đệ quy xóa tất cả con cháu của node bị quarantine
        cascade_queue = list(quarantined_ids)
        while cascade_queue:
            parent_id = cascade_queue.pop(0)
            for child in children_map.get(parent_id, []):
                if child.id not in quarantined_ids:
                    quarantined_ids.add(child.id)
                    cascade_queue.append(child.id)
                    # Ghi nhận issue cho node con bị cascade
                    all_issues.append({
                        "rule_id": "VAL-003",
                        "node_id": child.id,
                        "severity": "ERROR",
                        "issue_type": "BrokenParent",
                        "message": (
                            f"Node '{child.id}' cascading quarantine: "
                            f"parent '{child.parent_id}' was removed due to ERROR."
                        ),
                        "position": {
                            "start": child.position.start,
                            "end": child.position.end,
                        },
                    })

        return [node for node in nodes if node.id not in quarantined_ids]

    def _write_validated_nodes(self, nodes: List[LegalNode]) -> None:
        """Ghi file validated_nodes.json."""
        with open(self.validated_output_path, "w", encoding="utf-8") as f:
            json.dump(
                [node.model_dump() for node in nodes],
                f, ensure_ascii=False, indent=2,
            )
        logger.info("Written %d nodes to '%s'", len(nodes), self.validated_output_path)
