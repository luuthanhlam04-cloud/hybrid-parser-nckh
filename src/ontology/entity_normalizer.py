import os
import re
from typing import Dict, Any, Tuple
from thefuzz import fuzz
import unicodedata

class EntityNormalizer:
    """
    Thực thi quy tắc 2-Tier Matching (Exact Match và Fuzzy Match).
    """
    def __init__(self, taxonomy: Dict[str, Any]):
        self.taxonomy = taxonomy
        
        # Prepare exact match dictionary mapping alias -> canonical_id
        self.exact_match_dict = {}
        for canonical_id, data in self.taxonomy.items():
            aliases = data.get("aliases", [])
            for alias in aliases:
                norm_alias = self._normalize_text(alias)
                self.exact_match_dict[norm_alias] = canonical_id
                
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

    def _quarantine(self, raw_text: str, norm_text: str) -> str:
        """
        Ghi log và cấp ID quarantine.
        """
        canonical_id = f"unassigned.{norm_text.replace(' ', '_')}"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{raw_text}\n")
        return canonical_id

    def normalize(self, raw_text: str, fallback_type: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Thực hiện 2-Tier Matching. Trả về thông tin entity theo chuẩn.
        """
        norm_text = self._normalize_text(raw_text)
        
        # Tier 1: Exact Match
        if norm_text in self.exact_match_dict:
            canonical_id = self.exact_match_dict[norm_text]
            tax_data = self.taxonomy[canonical_id]
            return {
                "canonical_id": canonical_id,
                "ontology_class": tax_data["ontology_class"],
                "canonical_text": tax_data["canonical_text"],
                "aliases": tax_data.get("aliases", [])
            }
            
        # Tier 2: Fuzzy Match
        best_match_id = None
        best_score = 0
        for alias, canonical_id in self.exact_match_dict.items():
            score = fuzz.ratio(norm_text, alias)
            if score > best_score:
                best_score = score
                best_match_id = canonical_id
                
        if best_score >= 85 and best_match_id:
            tax_data = self.taxonomy[best_match_id]
            return {
                "canonical_id": best_match_id,
                "ontology_class": tax_data["ontology_class"],
                "canonical_text": tax_data["canonical_text"],
                "aliases": tax_data.get("aliases", [])
            }
            
        # Fallback: Quarantine
        quarantine_id = self._quarantine(raw_text, norm_text)
        
        m6_to_m7_map = {
            "SUBJECT": "LEGAL_SUBJECT",
            "ACTION": "LEGAL_ACTION",
            "PERMISSION": "LEGAL_ACTION",
            "OBLIGATION": "LEGAL_ACTION",
            "CONDITION": "CONDITION",
            "EXCEPTION": "EXCEPTION",
            "REFERENCE": "LEGAL_DOCUMENT_REF",
            "PENALTY": "PENALTY"
        }
        mapped_class = m6_to_m7_map.get(fallback_type, fallback_type)
        
        return {
            "canonical_id": quarantine_id,
            "ontology_class": mapped_class,
            "canonical_text": raw_text,
            "aliases": []
        }
