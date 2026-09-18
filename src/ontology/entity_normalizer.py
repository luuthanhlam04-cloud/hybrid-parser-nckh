import os
import re
import logging
from typing import Dict, Any, Tuple, List
from thefuzz import fuzz
import unicodedata

logger = logging.getLogger(__name__)

M6_TO_M7_MAP = {
    "SUBJECT": "LEGAL_SUBJECT",
    "ACTION": "LEGAL_ACTION",
    "PERMISSION": "LEGAL_ACTION",
    "OBLIGATION": "LEGAL_ACTION",
    "CONDITION": "CONDITION",
    "EXCEPTION": "EXCEPTION",
    "REFERENCE": "LEGAL_DOCUMENT_REF",
    "PENALTY": "PENALTY",
    "OBJECT": "LEGAL_OBJECT"  # Map OBJECT to LEGAL_OBJECT
}

FUZZY_THRESHOLD = 85
FUZZY_MIN_MARGIN = 5

class EntityNormalizer:
    """
    Thực thi quy tắc 2-Tier Matching (Exact Match và Fuzzy Match).
    """
    def __init__(self, taxonomy: Dict[str, Any]):
        self.taxonomy = taxonomy
        
        # Prepare exact match dictionary mapping alias -> List[canonical_id]
        self.exact_match_dict: Dict[str, List[str]] = {}
        for canonical_id, data in self.taxonomy.items():
            aliases = data.get("aliases", [])
            canonical_text = data.get("canonical_text", "")
            
            all_texts = aliases + ([canonical_text] if canonical_text else [])
            norm_texts = {self._normalize_text(t) for t in all_texts if t}
            
            for norm_alias in norm_texts:
                if not norm_alias:
                    continue
                if norm_alias not in self.exact_match_dict:
                    self.exact_match_dict[norm_alias] = []
                self.exact_match_dict[norm_alias].append(canonical_id)
                
        # Boot-time Validation: Phát hiện Alias trùng lặp (Collision)
        for alias, can_ids in self.exact_match_dict.items():
            if len(can_ids) > 1:
                logger.warning(f"WARNING: ALIAS COLLISION DETECTED for '{alias}'. Maps to: {can_ids}")
                
        # Khởi tạo log file cho Quarantine entities
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "unresolved_entities.log")
        
    def _normalize_text(self, text: str) -> str:
        """
        Dọn dẹp văn bản: chuyển chữ thường, xóa khoảng trắng thừa, chuẩn hóa Unicode.
        """
        if not text:
            return ""
        text = str(text).lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = unicodedata.normalize('NFC', text)
        return text

    def _quarantine(self, raw_text: str, source_node_id: str, local_id: str) -> str:
        """
        Ghi log và cấp ID quarantine mang tính scope.
        """
        canonical_id = f"UNRESOLVED:{source_node_id}:{local_id}"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{canonical_id} | {raw_text}\n")
        return canonical_id

    def normalize(self, raw_text: str, fallback_type: str, source_node_id: str, local_id: str) -> Dict[str, Any]:
        """
        Thực hiện 2-Tier Matching. Trả về thông tin entity theo chuẩn.
        """
        norm_text = self._normalize_text(raw_text)
        target_class = M6_TO_M7_MAP.get(fallback_type, fallback_type)
        
        # Tier 1: Exact Match
        if norm_text in self.exact_match_dict:
            can_ids = self.exact_match_dict[norm_text]
            if len(can_ids) > 1:
                # AMBIGUOUS_ALIAS -> QUARANTINE
                pass
            else:
                canonical_id = can_ids[0]
                tax_data = self.taxonomy[canonical_id]
                # Chấp nhận nếu class hợp lệ (trùng target_class)
                if tax_data["ontology_class"] == target_class:
                    return {
                        "canonical_id": canonical_id,
                        "ontology_class": tax_data["ontology_class"],
                        "canonical_text": tax_data["canonical_text"],
                        "aliases": tax_data.get("aliases", []),
                        "match_method": "EXACT"
                    }
            
        # Tier 2: Fuzzy Match (Class-Constrained)
        best_match_id = None
        best_score = 0
        second_best_score = 0
        
        for alias, can_ids in self.exact_match_dict.items():
            score = fuzz.ratio(norm_text, alias)
            if score > second_best_score:
                # Check class constraint for all matching candidates
                valid_can_ids = [cid for cid in can_ids if self.taxonomy[cid]["ontology_class"] == target_class]
                if valid_can_ids:
                    if score > best_score:
                        second_best_score = best_score
                        best_score = score
                        best_match_id = valid_can_ids[0]
                    else:
                        second_best_score = score
                        
        if best_score >= FUZZY_THRESHOLD and (best_score - second_best_score) >= FUZZY_MIN_MARGIN and best_match_id:
            tax_data = self.taxonomy[best_match_id]
            return {
                "canonical_id": best_match_id,
                "ontology_class": tax_data["ontology_class"],
                "canonical_text": tax_data["canonical_text"],
                "aliases": tax_data.get("aliases", []),
                "match_method": "FUZZY"
            }
            
        # Fallback: Quarantine
        quarantine_id = self._quarantine(raw_text, source_node_id, local_id)
        
        return {
            "canonical_id": quarantine_id,
            "ontology_class": None, # Unresolved không thuộc class nào
            "canonical_text": raw_text,
            "aliases": [],
            "m6_entity_type": fallback_type,
            "match_method": "QUARANTINED"
        }