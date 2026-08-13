import re
from dataclasses import dataclass
from typing import Optional, List, Tuple
from .node_generator import NodeType, Position
from .regex_engine import (
    PART_PATTERN, CHAPTER_PATTERN, SECTION_PATTERN,
    ARTICLE_PATTERN, CLAUSE_PATTERN, POINT_PATTERN
)

@dataclass
class RawChunk:
    type: NodeType
    marker: Optional[str]
    title: Optional[str]
    text: str
    position: Position

class BoundaryDetector:
    def __init__(self):
        pass

    def detect_boundaries(self, text: str) -> List[RawChunk]:
        chunks: List[RawChunk] = []
        lines = text.splitlines(keepends=True)
        current_char_index = 0

        pending_chunk: Optional[dict] = None

        def flush_pending(end_index: int):
            nonlocal pending_chunk
            if pending_chunk:
                combined_text = "".join(pending_chunk["text_lines"]).strip()
                chunks.append(
                    RawChunk(
                        type=pending_chunk["type"],
                        marker=pending_chunk["marker"],
                        title=pending_chunk["title"],
                        text=combined_text,
                        position=Position(start=pending_chunk["start"], end=end_index)
                    )
                )
                pending_chunk = None

        i = 0
        while i < len(lines):
            line = lines[i]
            line_start_idx = current_char_index
            line_len = len(line)
            current_char_index += line_len
            
            stripped = line.strip()
            
            if not stripped:
                if pending_chunk:
                    pending_chunk["text_lines"].append(line)
                i += 1
                continue

            point_matches = list(POINT_PATTERN.finditer(line))
            if point_matches:
                flush_pending(line_start_idx)
                
                for match_idx, match in enumerate(point_matches):
                    point_marker = match.group(1) 
                    point_title = f"{point_marker})"
                    start_pos = line_start_idx + match.start()
                    
                    next_start = point_matches[match_idx + 1].start() if match_idx + 1 < len(point_matches) else line_len
                    
                    marker_full_str = match.group(0)
                    text_part = line[match.start() + len(marker_full_str):next_start]
                    
                    if match_idx == len(point_matches) - 1:
                        pending_chunk = {
                            "type": NodeType.POINT,
                            "marker": point_marker,
                            "title": point_title,
                            "text_lines": [text_part],
                            "start": start_pos
                        }
                    else:
                        end_pos = line_start_idx + next_start
                        chunks.append(
                            RawChunk(
                                type=NodeType.POINT,
                                marker=point_marker,
                                title=point_title,
                                text=text_part.strip(),
                                position=Position(start=start_pos, end=end_pos)
                            )
                        )
                i += 1
                continue

            match_part = PART_PATTERN.search(line)
            match_chapter = CHAPTER_PATTERN.search(line)
            match_section = SECTION_PATTERN.search(line)
            match_article = ARTICLE_PATTERN.search(line)
            match_clause = CLAUSE_PATTERN.search(line)

            matched_type = None
            marker_val = None
            title_val = None
            text_val = ""

            if match_part:
                matched_type = NodeType.PART
                marker_str = match_part.group(0)
                marker_val = marker_str.strip()
                title_val = marker_str.strip()
                text_val = line[match_part.end():]
            elif match_chapter:
                matched_type = NodeType.CHAPTER
                marker_str = match_chapter.group(0)
                marker_val = marker_str.strip()
                title_val = marker_str.strip()
                text_val = line[match_chapter.end():]
            elif match_section:
                matched_type = NodeType.SECTION
                marker_str = match_section.group(0)
                marker_val = marker_str.strip()
                title_val = marker_str.strip()
                text_val = line[match_section.end():]
            elif match_article:
                matched_type = NodeType.ARTICLE
                marker_str = match_article.group(0) 
                marker_val = re.search(r'\d+', marker_str).group(0) if re.search(r'\d+', marker_str) else marker_str
                rest_line = line[match_article.end():].strip()
                if rest_line:
                    title_val = marker_str.strip() + " " + rest_line
                    text_val = "" 
                else:
                    title_val = marker_str.strip()
                    text_val = ""
            elif match_clause:
                matched_type = NodeType.CLAUSE
                marker_str = match_clause.group(0)
                marker_val = re.search(r'\d+', marker_str).group(0) if re.search(r'\d+', marker_str) else marker_str
                title_val = marker_str.strip()
                text_val = line[match_clause.end():]

            if matched_type:
                flush_pending(line_start_idx)
                
                if matched_type in (NodeType.PART, NodeType.CHAPTER, NodeType.SECTION):
                    title_val = line.strip()
                    if i + 1 < len(lines):
                        next_line = lines[i+1]
                        next_stripped = next_line.strip()
                        if next_stripped and not any(p.search(next_line) for p in [PART_PATTERN, CHAPTER_PATTERN, SECTION_PATTERN, ARTICLE_PATTERN, CLAUSE_PATTERN, POINT_PATTERN]):
                            title_val += "\n" + next_stripped
                            pending_chunk = {
                                "type": matched_type,
                                "marker": marker_val,
                                "title": title_val,
                                "text_lines": [], 
                                "start": line_start_idx
                            }
                            current_char_index += len(next_line)
                            i += 2
                            continue
                
                pending_chunk = {
                    "type": matched_type,
                    "marker": marker_val,
                    "title": title_val,
                    "text_lines": [text_val] if text_val else [],
                    "start": line_start_idx
                }
            else:
                if pending_chunk:
                    pending_chunk["text_lines"].append(line)
                else:
                    pending_chunk = {
                        "type": NodeType.TEXT,
                        "marker": None,
                        "title": None,
                        "text_lines": [line],
                        "start": line_start_idx
                    }
            i += 1

        flush_pending(current_char_index)
        return chunks
