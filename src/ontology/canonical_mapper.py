import yaml
import os
from typing import Dict, Any, Tuple

class CanonicalMapper:
    """
    Chịu trách nhiệm load và parse 2 file YAML cấu hình của Ontology.
    Cung cấp giao diện truy xuất constraints và taxonomy.
    """
    def __init__(self, schema_path: str = None, taxonomy_path: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if schema_path is None:
            schema_path = os.path.join(base_dir, "configs", "ontology_schema.yaml")
        if taxonomy_path is None:
            taxonomy_path = os.path.join(base_dir, "configs", "taxonomy_aliases.yaml")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = yaml.safe_load(f)
            
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = yaml.safe_load(f)
            
    def get_relation_constraints(self, relation_type: str) -> Dict[str, Any]:
        """
        Trả về dictionary chứa domain, range, self_loop, max_depth của một relation type.
        """
        relations = self.schema.get("relations", {})
        if relation_type not in relations:
            return None
        return relations[relation_type]
    
    def get_allowed_classes(self) -> list:
        return self.schema.get("classes", [])

    def get_taxonomy(self) -> Dict[str, Any]:
        """
        Trả về dictionary taxonomy {canonical_id: {ontology_class, canonical_text, aliases}}
        """
        return self.taxonomy
