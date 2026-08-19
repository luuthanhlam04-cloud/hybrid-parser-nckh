import logging
import re
from typing import List, Dict, Optional
from .node_generator import NodeType, LegalNode, Position, generate_hybrid_id
from .boundary_detector import RawChunk

logger = logging.getLogger(__name__)

class HierarchyBuilder:
    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.active_nodes: Dict[NodeType, Optional[LegalNode]] = {
            NodeType.PART: None,
            NodeType.CHAPTER: None,
            NodeType.SECTION: None,
            NodeType.ARTICLE: None,
            NodeType.CLAUSE: None,
            NodeType.POINT: None,
        }

    def _generate_prefix(self, chunk_type: NodeType, marker: Optional[str]) -> str:
        def strip_p(node_id: str) -> str:
            return re.sub(r'_p\d+$', '', node_id)

        clean_marker = str(marker).split()[-1] if marker else "unknown"
        if chunk_type == NodeType.ARTICLE:
            return f"article_{clean_marker}"
        elif chunk_type == NodeType.CLAUSE:
            base = "orphan"
            if self.active_nodes[NodeType.ARTICLE]:
                base = strip_p(self.active_nodes[NodeType.ARTICLE].id)
            return f"{base}_clause_{clean_marker}"
        elif chunk_type == NodeType.POINT:
            base = "orphan"
            if self.active_nodes[NodeType.CLAUSE]:
                base = strip_p(self.active_nodes[NodeType.CLAUSE].id)
            elif self.active_nodes[NodeType.ARTICLE]:
                base = strip_p(self.active_nodes[NodeType.ARTICLE].id)
            return f"{base}_point_{clean_marker}"
        elif chunk_type == NodeType.PART:
            return f"part_{clean_marker}"
        elif chunk_type == NodeType.CHAPTER:
            return f"chapter_{clean_marker}"
        elif chunk_type == NodeType.SECTION:
            return f"section_{clean_marker}"
        return "unknown"

    def build_hierarchy(self, chunks: List[RawChunk]) -> List[LegalNode]:
        nodes: List[LegalNode] = []
        self.reset_state()

        def get_parent_id(target_type: NodeType) -> Optional[str]:
            if target_type == NodeType.CHAPTER:
                return self.active_nodes[NodeType.PART].id if self.active_nodes[NodeType.PART] else None
            elif target_type == NodeType.SECTION:
                if self.active_nodes[NodeType.CHAPTER]: return self.active_nodes[NodeType.CHAPTER].id
                if self.active_nodes[NodeType.PART]: return self.active_nodes[NodeType.PART].id
                return None
            elif target_type == NodeType.ARTICLE:
                if self.active_nodes[NodeType.SECTION]: return self.active_nodes[NodeType.SECTION].id
                if self.active_nodes[NodeType.CHAPTER]: return self.active_nodes[NodeType.CHAPTER].id
                if self.active_nodes[NodeType.PART]: return self.active_nodes[NodeType.PART].id
                return None
            elif target_type == NodeType.CLAUSE:
                return self.active_nodes[NodeType.ARTICLE].id if self.active_nodes[NodeType.ARTICLE] else None
            elif target_type == NodeType.POINT:
                if self.active_nodes[NodeType.CLAUSE]: return self.active_nodes[NodeType.CLAUSE].id
                if self.active_nodes[NodeType.ARTICLE]: return self.active_nodes[NodeType.ARTICLE].id
                return None
            elif target_type == NodeType.TEXT:
                for pt in [NodeType.POINT, NodeType.CLAUSE, NodeType.ARTICLE, NodeType.SECTION, NodeType.CHAPTER, NodeType.PART]:
                    if self.active_nodes.get(pt):
                        return self.active_nodes[pt].id
                return None
            return None

        def update_active_state(node: LegalNode):
            if node.type == NodeType.PART:
                self.active_nodes[NodeType.PART] = node
                self.active_nodes[NodeType.CHAPTER] = None
                self.active_nodes[NodeType.SECTION] = None
                self.active_nodes[NodeType.ARTICLE] = None
                self.active_nodes[NodeType.CLAUSE] = None
                self.active_nodes[NodeType.POINT] = None
            elif node.type == NodeType.CHAPTER:
                self.active_nodes[NodeType.CHAPTER] = node
                self.active_nodes[NodeType.SECTION] = None
                self.active_nodes[NodeType.ARTICLE] = None
                self.active_nodes[NodeType.CLAUSE] = None
                self.active_nodes[NodeType.POINT] = None
            elif node.type == NodeType.SECTION:
                self.active_nodes[NodeType.SECTION] = node
                self.active_nodes[NodeType.ARTICLE] = None
                self.active_nodes[NodeType.CLAUSE] = None
                self.active_nodes[NodeType.POINT] = None
            elif node.type == NodeType.ARTICLE:
                self.active_nodes[NodeType.ARTICLE] = node
                self.active_nodes[NodeType.CLAUSE] = None
                self.active_nodes[NodeType.POINT] = None
            elif node.type == NodeType.CLAUSE:
                self.active_nodes[NodeType.CLAUSE] = node
                self.active_nodes[NodeType.POINT] = None
            elif node.type == NodeType.POINT:
                self.active_nodes[NodeType.POINT] = node

        for chunk in chunks:
            # Bug 3 fix: Bỏ qua các node TEXT rỗng
            if chunk.type == NodeType.TEXT and not chunk.text.strip():
                continue

            parent_id = get_parent_id(chunk.type)
            
            if parent_id is None and chunk.type not in (NodeType.PART, NodeType.CHAPTER):
                logger.warning(f"Orphan node detected: {chunk.type} - {chunk.text.strip()[:30]}")

            if chunk.type == NodeType.TEXT:
                base_id = parent_id if parent_id else "orphan"
                base_prefix = re.sub(r'_p\d+$', '', base_id)
                prefix = f"{base_prefix}_text"
                node_id = generate_hybrid_id(prefix, chunk.position.start)
                title = None
            else:
                prefix = self._generate_prefix(chunk.type, chunk.marker)
                node_id = generate_hybrid_id(prefix, chunk.position.start)
                title = chunk.title
                
            node = LegalNode(
                id=node_id,
                type=chunk.type,
                title=title,
                text=chunk.text,
                parent_id=parent_id,
                position=chunk.position
            )
            
            nodes.append(node)
            update_active_state(node)
            
        return nodes
