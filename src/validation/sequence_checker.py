"""
Sequence Checker - Kiểm tra tính liên tục (GapIndex) của các chuỗi đánh số:
  - Số La Mã (Chương): I, II, III, IV...
  - Số Tự Nhiên (Mục, Điều, Khoản): 1, 2, 3...
  - Bảng chữ cái tiếng Việt (Điểm): a, b, c, d, đ, e, g, h, i, k, l, m, n, o, p, q, r, s, t, u, v, x, y
Nguyên tắc: Chỉ phát hiện (WARNING), KHÔNG tự sửa dữ liệu.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.validation.schema_validator import LegalNode

logger = logging.getLogger(__name__)

# Bảng chữ cái tiếng Việt chuẩn pháp luật (bỏ f, j, w, z)
VN_ALPHABET = [
    "a", "b", "c", "d", "đ", "e", "g", "h", "i", "k",
    "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
    "v", "x", "y",
]

# Bảng số La Mã (hỗ trợ tới 50, đủ cho số chương của bất kỳ bộ luật nào)
ROMAN_NUMERALS = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII",
    "XXIX", "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV",
    "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL", "XLI", "XLII",
    "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L",
]


def _extract_marker(node: LegalNode) -> Optional[str]:
    """
    Trích xuất giá trị marker (số hoặc chữ) từ metadata của node.
    Sử dụng Single Source of Truth (node.number / node.marker) từ M1.
    Fallback về Regex nếu metadata bị mất (TXT mode).
    """
    if node.type == "POINT" and node.marker is not None:
        return str(node.marker).lower()
    if node.type in ("CHAPTER", "SECTION", "ARTICLE", "CLAUSE") and node.number is not None:
        return str(node.number)

    # Legacy regex fallback (cho TXT)
    if not node.title:
        return None

    title = node.title.strip()
    node_type = node.type

    if node_type == "CHAPTER":
        # Tìm số La Mã: "Chương III" hoặc "Chương III\n..."
        match = re.search(r'Chương\s+([IVXLCDM]+)', title)
        if match:
            return match.group(1)

    elif node_type == "SECTION":
        # Tìm số tự nhiên: "Mục 1" hoặc "Mục 1\n..."
        match = re.search(r'Mục\s+(\d+)', title)
        if match:
            return match.group(1)

    elif node_type == "ARTICLE":
        # Tìm số tự nhiên: "Điều 26." hoặc "Điều 26. Tiêu đề"
        match = re.search(r'Điều\s+(\d+)', title)
        if match:
            return match.group(1)

    elif node_type == "CLAUSE":
        # "1." hoặc "2."
        match = re.match(r'(\d+)\.', title)
        if match:
            return match.group(1)

    elif node_type == "POINT":
        # "a)" hoặc "đ)"
        match = re.match(r'([a-zđ])\)', title, re.IGNORECASE)
        if match:
            return match.group(1).lower()

    return None


def check_sequences(nodes: List[LegalNode]) -> List[Dict[str, Any]]:
    """
    Kiểm tra tính liên tục của chuỗi đánh số cho mỗi nhóm node cùng cha.

    Returns:
        Danh sách issue dicts (severity=WARNING).
    """
    issues: List[Dict[str, Any]] = []

    # Nhóm node theo (parent_id, type)
    groups: Dict[tuple, List[LegalNode]] = defaultdict(list)
    for node in nodes:
        if node.type in ("CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT"):
            key = (node.parent_id, node.type)
            groups[key].append(node)

    for (parent_id, node_type), group_nodes in groups.items():
        markers = []
        for n in group_nodes:
            marker = _extract_marker(n)
            if marker is not None:
                markers.append((marker, n))

        if len(markers) < 2:
            continue

        if node_type == "CHAPTER":
            _check_roman_sequence(markers, parent_id, issues)
        elif node_type in ("SECTION", "ARTICLE", "CLAUSE"):
            _check_numeric_sequence(markers, parent_id, node_type, issues)
        elif node_type == "POINT":
            _check_alpha_sequence(markers, parent_id, issues)

    return issues


def _check_roman_sequence(
    markers: List[tuple],
    parent_id: Optional[str],
    issues: List[Dict[str, Any]],
) -> None:
    """Kiểm tra chuỗi số La Mã (Chương)."""
    actual_values = [m[0] for m in markers]

    try:
        start_idx = ROMAN_NUMERALS.index(actual_values[0])
        end_idx = ROMAN_NUMERALS.index(actual_values[-1])
    except ValueError:
        return

    expected = ROMAN_NUMERALS[start_idx:end_idx + 1]
    expected_set = set(expected)
    actual_set = set(actual_values)
    missing = expected_set - actual_set

    for m in sorted(missing, key=lambda x: ROMAN_NUMERALS.index(x)):
        # Tìm vị trí trước và sau phần tử bị thiếu
        m_idx = ROMAN_NUMERALS.index(m)
        before = ROMAN_NUMERALS[m_idx - 1] if m_idx > 0 else None
        after = ROMAN_NUMERALS[m_idx + 1] if m_idx + 1 < len(ROMAN_NUMERALS) else None

        issues.append({
            "rule_id": "VAL-006",
            "node_id": f"chapter_{m}",
            "severity": "WARNING",
            "issue_type": "GapIndex",
            "message": (
                f"Missing sequence element 'chapter_{m}' detected "
                f"between 'chapter_{before}' and 'chapter_{after}' "
                f"under parent '{parent_id or 'root'}'."
            ),
            "position": {"start": -1, "end": -1},
        })
        logger.info("GapIndex: Missing chapter_%s under '%s'", m, parent_id)


def _check_numeric_sequence(
    markers: List[tuple],
    parent_id: Optional[str],
    node_type: str,
    issues: List[Dict[str, Any]],
) -> None:
    """Kiểm tra chuỗi số tự nhiên (Mục, Điều, Khoản)."""
    type_label = node_type.lower()

    actual_numbers = []
    for marker_val, _ in markers:
        try:
            actual_numbers.append(int(marker_val))
        except ValueError:
            continue

    if len(actual_numbers) < 2:
        return

    start_num = actual_numbers[0]
    end_num = actual_numbers[-1]
    expected = set(range(start_num, end_num + 1))
    actual = set(actual_numbers)
    missing = expected - actual

    for m in sorted(missing):
        # Tìm phần tử liền trước và liền sau
        before_num = m - 1
        after_num = m + 1

        issues.append({
            "rule_id": "VAL-006",
            "node_id": f"{type_label}_{m}",
            "severity": "WARNING",
            "issue_type": "GapIndex",
            "message": (
                f"Missing sequence element '{type_label}_{m}' detected "
                f"between '{type_label}_{before_num}' and '{type_label}_{after_num}' "
                f"under parent '{parent_id or 'root'}'."
            ),
            "position": {"start": -1, "end": -1},
        })
        logger.info("GapIndex: Missing %s_%d under '%s'", type_label, m, parent_id)


def _check_alpha_sequence(
    markers: List[tuple],
    parent_id: Optional[str],
    issues: List[Dict[str, Any]],
) -> None:
    """Kiểm tra chuỗi bảng chữ cái tiếng Việt (Điểm)."""
    actual_letters = [m[0] for m in markers]

    try:
        start_idx = VN_ALPHABET.index(actual_letters[0])
        end_idx = VN_ALPHABET.index(actual_letters[-1])
    except ValueError:
        return

    expected = VN_ALPHABET[start_idx:end_idx + 1]
    expected_set = set(expected)
    actual_set = set(actual_letters)
    missing = expected_set - actual_set

    for m in sorted(missing, key=lambda x: VN_ALPHABET.index(x)):
        m_idx = VN_ALPHABET.index(m)
        before = VN_ALPHABET[m_idx - 1] if m_idx > 0 else None
        after = VN_ALPHABET[m_idx + 1] if m_idx + 1 < len(VN_ALPHABET) else None

        issues.append({
            "rule_id": "VAL-006",
            "node_id": f"point_{m}",
            "severity": "WARNING",
            "issue_type": "GapIndex",
            "message": (
                f"Missing sequence element 'point_{m}' detected "
                f"between 'point_{before}' and 'point_{after}' "
                f"under parent '{parent_id or 'root'}'."
            ),
            "position": {"start": -1, "end": -1},
        })
        logger.info("GapIndex: Missing point_%s under '%s'", m, parent_id)
