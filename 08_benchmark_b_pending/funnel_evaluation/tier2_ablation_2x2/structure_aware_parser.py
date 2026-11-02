# -*- coding: utf-8 -*-
"""
structure_aware_parser.py — Module M1-M3 Structure-Aware Regex Parser.
Phân tích 2.088 điều luật trong corpus_final.json thành các đơn vị có cấu trúc:
- Điều (Article)
- Khoản (Clause)
- Điểm (Point)
Gắn tiền tố phân cấp: [Luật: {law_id} | Điều {num}: {title} | Khoản {c} | Điểm {p}]
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import os
from typing import List, Dict, Any

# Regex patterns chuẩn hóa cho văn bản quy phạm pháp luật Việt Nam
RE_ARTICLE = re.compile(r"^\s*(?:Đ|Ð)i[eề]u\s+(?P<number>\d+)\.?\s*(?P<title>.*)$", re.IGNORECASE | re.MULTILINE)
RE_CLAUSE = re.compile(r"^\s*(?P<number>\d+)\.\s+(?P<text>.+)$")
RE_POINT = re.compile(r"^\s*(?P<marker>[a-zđ])\)\s+(?P<text>.+)$")

class StructureAwareParser:
    def __init__(self):
        pass

    def parse_article_text(self, text: str, article_id: str, law_id: str, article_number: int, title: str) -> List[Dict[str, Any]]:
        """
        Bóc tách 1 điều luật thành danh sách các cấu trúc vi mô (Hierarchical Chunks).
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return [{
                "chunk_id": f"{article_id}_chunk_0",
                "article_id": article_id,
                "law_id": law_id,
                "article_number": article_number,
                "hierarchical_path": f"[Luật: {law_id} | Điều {article_number}: {title}]",
                "text": text,
                "has_explicit_locator": True
            }]

        chunks = []
        current_clause = None
        current_clause_num = None
        current_point_marker = None
        
        # Tiền tố Điều
        base_prefix = f"[Luật: {law_id} | Điều {article_number}: {title}]"

        for line in lines:
            # 1. Kiểm tra Khoản (ví dụ: "1. Người có đất...")
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
                    "clause": current_clause_num,
                    "point": current_point_marker,
                    "hierarchical_path": hierarchical_path,
                    "text": f"{hierarchical_path} {point_text}",
                    "has_explicit_locator": True
                })
                continue

            # 3. Dòng thông thường (tiêu đề hoặc đoạn dẫn)
            if not chunks:
                hierarchical_path = base_prefix
                chunks.append({
                    "chunk_id": f"{article_id}_p0",
                    "article_id": article_id,
                    "law_id": law_id,
                    "article_number": article_number,
                    "clause": None,
                    "point": None,
                    "hierarchical_path": hierarchical_path,
                    "text": f"{hierarchical_path} {line}",
                    "has_explicit_locator": True
                })
            else:
                # Nối tiếp vào chunk gần nhất
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
            title = doc.get("title", f"Điều {art_num}")
            text = doc.get("text", "")
            
            chunks = self.parse_article_text(text, aid, law_id, art_num, title)
            all_structured_chunks.extend(chunks)
            
        return all_structured_chunks

    def create_naive_chunks(self, corpus_path: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Tạo naive chunks theo phương pháp cắt vụn cố định truyền thống (không gắn tiền tố phân cấp).
        """
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
            
        naive_chunks = []
        for doc in corpus:
            aid = doc.get("article_id")
            law_id = doc.get("law_id", "")
            art_num = doc.get("article_number", 0)
            text = doc.get("text", "")
            
            # Cắt thành các đoạn văn bản phẳng
            words = text.split()
            if len(words) <= chunk_size:
                has_locator = bool(f"điều {art_num}" in text.lower() or f"điều {art_num}." in text.lower())
                naive_chunks.append({
                    "chunk_id": f"{aid}_naive_0",
                    "article_id": aid,
                    "law_id": law_id,
                    "article_number": art_num,
                    "text": text,
                    "has_explicit_locator": has_locator
                })
            else:
                step = chunk_size - overlap
                for c_idx, start in enumerate(range(0, len(words), step)):
                    chunk_words = words[start:start + chunk_size]
                    chunk_text = " ".join(chunk_words)
                    # Chỉ đoạn đầu tiên có tiêu đề Điều X, các đoạn sau bị mất dấu
                    has_locator = bool(c_idx == 0 and (f"điều {art_num}" in chunk_text.lower()))
                    naive_chunks.append({
                        "chunk_id": f"{aid}_naive_{c_idx}",
                        "article_id": aid,
                        "law_id": law_id,
                        "article_number": art_num,
                        "text": chunk_text,
                        "has_explicit_locator": has_locator
                    })
        return naive_chunks

if __name__ == "__main__":
    parser = StructureAwareParser()
    corpus_p = "Benchmark/corpus_final.json"
    s_chunks = parser.parse_corpus(corpus_p)
    n_chunks = parser.create_naive_chunks(corpus_p)
    print(f"Tổng số Điều ban đầu: 2.088")
    print(f"Tổng số Structured Chunks (M1-M3): {len(s_chunks)}")
    print(f"Tổng số Naive Chunks: {len(n_chunks)}")
    print("Mẫu Structured Chunk:", s_chunks[1]["text"][:150])

