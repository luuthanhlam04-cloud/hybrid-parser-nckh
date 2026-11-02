# -*- coding: utf-8 -*-
"""
structure_aware_parser.py — Module M1-M3 Structure-Aware Regex Parser (Phiên bản v2 Tối ưu hóa Tiền tố Ngữ cảnh).
Tự động khôi phục tiêu đề thực tế từ dòng 1 của văn bản nếu trường title bị generic ('Điều X').
Kế thừa đầy đủ cấu trúc phân cấp: [Luật: {law_id} | Điều {num}: {actual_title}] vào TẤT CẢ các Khoản và Điểm.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import os
from typing import List, Dict, Any

RE_ARTICLE = re.compile(r"^\s*(?:Đ|Ð)i[eề]u\s+(?P<number>\d+)\.?\s*(?P<title>.*)$", re.IGNORECASE | re.MULTILINE)
RE_CLAUSE = re.compile(r"^\s*(?P<number>\d+)\.\s+(?P<text>.+)$")
RE_POINT = re.compile(r"^\s*(?P<marker>[a-zđ])\)\s+(?P<text>.+)$")
RE_GENERIC_TITLE = re.compile(r"^(?:Điều|Ðiều)\s+\d+\.?$", re.IGNORECASE)


class StructureAwareParser:
    def __init__(self):
        pass

    def extract_article_title(self, raw_title: str, text: str, article_number: int) -> tuple:
        """
        Khôi phục tiêu đề thực tế của điều luật nếu trường title bị generic ('Điều X').
        Trả về: (actual_title, body_lines)
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            actual_t = raw_title.strip() if raw_title and raw_title.strip() else f"Điều {article_number}"
            return actual_t, []

        # Kiểm tra xem raw_title có phải generic ("Điều 1", "Điều 357" hoặc rỗng) không
        is_generic = not raw_title or bool(RE_GENERIC_TITLE.match(raw_title.strip()))
        
        if is_generic and lines:
            first_line = lines[0]
            # Nếu dòng đầu tiên không phải Khoản ("1. ") hay Điểm ("a) ")
            if not RE_CLAUSE.match(first_line) and not RE_POINT.match(first_line):
                art_match = RE_ARTICLE.match(first_line)
                if art_match and art_match.group("title").strip():
                    actual_title = art_match.group("title").strip()
                else:
                    actual_title = first_line
                return actual_title, lines[1:]  # Loại bỏ dòng tiêu đề khỏi body_lines
        
        # Nếu raw_title đã có tên cụ thể
        art_match = RE_ARTICLE.match(raw_title)
        if art_match and art_match.group("title").strip():
            actual_title = art_match.group("title").strip()
        else:
            actual_title = raw_title.strip() if raw_title.strip() else f"Điều {article_number}"

        # Kiểm tra nếu dòng đầu tiên của body lặp lại y hệt tiêu đề thì loại bỏ
        if lines and (lines[0].lower() == actual_title.lower() or RE_GENERIC_TITLE.match(lines[0])):
            return actual_title, lines[1:]

        return actual_title, lines

    def parse_article_text(self, text: str, article_id: str, law_id: str, article_number: int, raw_title: str) -> List[Dict[str, Any]]:
        """
        Bóc tách 1 điều luật thành danh sách các cấu trúc vi mô (Hierarchical Chunks).
        Kế thừa đầy đủ tiêu đề thực tế vào TẤT CẢ các Khoản và Điểm.
        """
        actual_title, body_lines = self.extract_article_title(raw_title, text, article_number)
        base_prefix = f"[Luật: {law_id} | Điều {article_number}: {actual_title}]"

        if not body_lines:
            return [{
                "chunk_id": f"{article_id}_p0",
                "article_id": article_id,
                "law_id": law_id,
                "article_number": article_number,
                "article_title": actual_title,
                "hierarchical_path": base_prefix,
                "text": f"{base_prefix} {actual_title}",
                "has_explicit_locator": True
            }]

        chunks = []
        current_clause_num = None
        current_point_marker = None

        for line in body_lines:
            # 1. Kiểm tra Khoản (ví dụ: "1. Người nào...")
            clause_match = RE_CLAUSE.match(line)
            if clause_match:
                current_clause_num = clause_match.group("number")
                current_point_marker = None
                clause_text = clause_match.group("text")
                hierarchical_path = f"{base_prefix} > [Khoản {current_clause_num}]"
                chunks.append({
                    "chunk_id": f"{article_id}_k{current_clause_num}",
                    "article_id": article_id,
                    "law_id": law_id,
                    "article_number": article_number,
                    "article_title": actual_title,
                    "clause": current_clause_num,
                    "point": None,
                    "hierarchical_path": hierarchical_path,
                    "text": f"{hierarchical_path} {clause_text}",
                    "has_explicit_locator": True
                })
                continue

            # 2. Kiểm tra Điểm (ví dụ: "a) Tổ chức trong nước...")
            point_match = RE_POINT.match(line)
            if point_match:
                current_point_marker = point_match.group("marker")
                point_text = point_match.group("text")
                clause_str = f" > [Khoản {current_clause_num}]" if current_clause_num else ""
                hierarchical_path = f"{base_prefix}{clause_str} > [Điểm {current_point_marker}]"
                chunks.append({
                    "chunk_id": f"{article_id}_k{current_clause_num or 0}_d{current_point_marker}",
                    "article_id": article_id,
                    "law_id": law_id,
                    "article_number": article_number,
                    "article_title": actual_title,
                    "clause": current_clause_num,
                    "point": current_point_marker,
                    "hierarchical_path": hierarchical_path,
                    "text": f"{hierarchical_path} {point_text}",
                    "has_explicit_locator": True
                })
                continue

            # 3. Đoạn văn dẫn hoặc đoạn không có đánh số
            if not chunks:
                hierarchical_path = base_prefix
                chunks.append({
                    "chunk_id": f"{article_id}_p0",
                    "article_id": article_id,
                    "law_id": law_id,
                    "article_number": article_number,
                    "article_title": actual_title,
                    "clause": None,
                    "point": None,
                    "hierarchical_path": hierarchical_path,
                    "text": f"{hierarchical_path} {line}",
                    "has_explicit_locator": True
                })
            else:
                chunks[-1]["text"] += f" {line}"

        return chunks

    def parse_corpus(self, corpus_path: str) -> List[Dict[str, Any]]:
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
            
        all_structured_chunks = []
        for doc in corpus:
            aid = doc.get("article_id")
            law_id = doc.get("law_id", "")
            art_num = doc.get("article_number", 0)
            raw_title = doc.get("title", "")
            text = doc.get("text", "")
            
            parsed_chunks = self.parse_article_text(text, aid, law_id, art_num, raw_title)
            all_structured_chunks.extend(parsed_chunks)
            
        return all_structured_chunks
