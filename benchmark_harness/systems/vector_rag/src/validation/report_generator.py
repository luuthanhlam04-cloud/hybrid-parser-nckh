"""
Report Generator - Tính toán metrics tổng hợp và sinh file validation_report.json.
Nguyên tắc: Chỉ tính toán và báo cáo, KHÔNG tự sửa dữ liệu.
"""
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def generate_report(
    total_nodes_received: int,
    all_issues: List[Dict[str, Any]],
    output_path: str,
) -> Dict[str, Any]:
    """
    Tính toán metrics và ghi file validation_report.json.

    Args:
        total_nodes_received: Tổng số node đầu vào.
        all_issues: Danh sách tất cả issues đã phát hiện.
        output_path: Đường dẫn file đầu ra.

    Returns:
        Report dict hoàn chỉnh.
    """
    fatal_errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    fatal_errors_count = len(fatal_errors)
    warnings_count = len(warnings)
    total_nodes_validated = total_nodes_received - fatal_errors_count

    if total_nodes_received > 0:
        score = round((1 - (fatal_errors_count / total_nodes_received)) * 100, 2)
    else:
        score = 100.0

    report = {
        "summary": {
            "total_nodes_received": total_nodes_received,
            "total_nodes_validated": total_nodes_validated,
            "fatal_errors_count": fatal_errors_count,
            "warnings_count": warnings_count,
            "structural_integrity_score": score,
        },
        "issues": all_issues,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info(
        "Validation report generated: %d errors, %d warnings, score=%.2f%%",
        fatal_errors_count, warnings_count, score,
    )
    return report
