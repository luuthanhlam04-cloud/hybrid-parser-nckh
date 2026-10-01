# LEGAL ONTOLOGY SPECIFICATION V1.3 (AGENT-READABLE BLUEPRINT)
**Project:** Hybrid Parser for Vietnamese Legal GraphRAG
**Module:** M7 - Legal Ontology Builder
**Architecture:** Rule-Based, Deterministic, Property Graph

---

## 1. CORE ARCHITECTURAL PRINCIPLES (MUST FOLLOW)
1. **No LLM in M7:** Module 7 operates strictly on predefined rules, regex, dictionary mapping, and string similarity. Do NOT use any LLM generation calls.
2. **Action Neutrality (Hohfeldian Model):** Legal rights and duties are NOT node classes. They are represented by edges (`ALLOW`, `REQUIRE`, `PROHIBIT`) pointing to a neutral `LEGAL_ACTION` node.
3. **Edge-Level Provenance:** Nodes are global, lightweight concepts. ALL local context (where the rule came from, verbatim text) MUST be pushed to Edge properties.
4. **Zero Data Loss:** Unresolved entities from M6 are NEVER deleted. They are placed in "Quarantine Mode" with a temporary ID.

---

## 2. NODE SCHEMA (CANONICAL ENTITIES)
Nodes act as "Identity Hubs" to resolve duplicates. They DO NOT store source documentation or evidences.

### 2.1 Allowed Node Classes (Strict Enum)
1. `LEGAL_SUBJECT` (E.g., Citizen, State, Enterprise)
2. `LEGAL_ACTION` (E.g., Transfer, Notarize, Revoke)
3. `CONDITION` (E.g., Has certificate, No dispute)
4. `EXCEPTION` (E.g., Except for inheritance cases)
5. `PENALTY` (E.g., Administrative fine)
6. `LEGAL_DOCUMENT_REF` (E.g., Clause 1 Article 45)

### 2.2 Node Properties
| Property | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `canonical_id` | String | REQUIRED | Primary Key. Uses dot notation (e.g., `subject.land_user.individual`). |
| `ontology_class` | String | REQUIRED | Must be one of the 6 Allowed Node Classes. |
| `canonical_text` | String | REQUIRED | Normalized Vietnamese display name. |
| `aliases` | List[Str] | OPTIONAL | Synonyms used for matching (e.g., `["cá nhân", "người sử dụng đất"]`). |

---

## 3. EDGE SCHEMA (CANONICAL RELATIONS)
Edges hold the legal logic, boolean operators, and exact source provenance.

### 3.1 Allowed Relation Types (Strict Enum)
`ALLOW`, `REQUIRE`, `PROHIBIT`, `HAS_CONDITION`, `HAS_EXCEPTION`, `REFERENCE_TO`, `HAS_PENALTY`.

### 3.2 Edge Properties
| Property | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `relation_id` | String | REQUIRED | Unique ID for the edge (e.g., `REL_001`). |
| `relation_type` | String | REQUIRED | Must be one of the 7 Allowed Relation Types. |
| `source_node_id`| String | REQUIRED | Physical Node ID from M4 (e.g., `doc_dieu-45_khoan-1`). **CRITICAL PROVENANCE**. |
| `evidence` | String | REQUIRED | Verbatim text justifying this edge. |
| `rule_id` | String | REQUIRED | M7 normalization rule applied (e.g., `RULE_M7_01`). For auditability. |
| `assertion_status`| String | REQUIRED | Always `"ASSERTED"`. |
| `logic_group` | String | OPTIONAL | Boolean logic grouping (e.g., `G1`, `G2`). |
| `operator` | String | OPTIONAL | Boolean operator (`AND`, `OR`). |

---

## 4. DOMAIN-RANGE CONSTRAINTS MATRIX
The Validator MUST enforce this matrix. Any relation violating these rules must be `REJECTED`.

| Relation | Source Domain | Target Range | Self-Loop Allowed? |
| :--- | :--- | :--- | :--- |
| `ALLOW` | `LEGAL_SUBJECT` | `LEGAL_ACTION` | FALSE |
| `REQUIRE` | `LEGAL_SUBJECT`, `LEGAL_ACTION` | `LEGAL_ACTION` | FALSE |
| `PROHIBIT` | `LEGAL_SUBJECT` | `LEGAL_ACTION` | FALSE |
| `HAS_CONDITION` | `LEGAL_SUBJECT`, `LEGAL_ACTION` | `CONDITION` | **TRUE** (Max Depth: 2) |
| `HAS_EXCEPTION` | `LEGAL_ACTION`, `CONDITION` | `EXCEPTION` | **TRUE** (Max Depth: 2) |
| `REFERENCE_TO` | *All Classes* | `LEGAL_DOCUMENT_REF` | FALSE |
| `HAS_PENALTY` | `LEGAL_ACTION` | `PENALTY` | FALSE |

---

## 5. M7 PROCESSING PIPELINE RULES

### Rule 1: Entity Normalization (2-Tier Matching)
When mapping raw text (e.g., "người sử dụng đất") to a Canonical ID:
- **Tier 1:** Exact match against `taxonomy_aliases.yaml` keys and aliases (after lowercasing and stripping whitespace).
- **Tier 2:** Fuzzy match (Levenshtein/thefuzz). If similarity >= 0.85, assign ID.
- **Fallback (Quarantine):** If both fail, assign `canonical_id = "unassigned.[normalized_text]"`, log to `unresolved_entities.log`.

### Rule 2: Edge Provenance Preservation
When converting local relations (e.g., `e1 -> ALLOW -> e2`) to canonical relations, the normalizer MUST copy `source_node_id`, `evidence`, `logic_group`, and `operator` from the raw M6 input into the new Canonical Relation properties.

### Rule 3: Output Format
The final `canonical_semantic_graph.json` must have the following structure:
```json
{
  "metadata": {
    "ontology_version": "1.3",
    "domain": "Luật Đất đai 2024",
    "generated_by": "M7_Builder"
  },
  "entities": [
    // Unique list of Canonical Entities (No duplicates)
  ],
  "relations": [
    // List of Canonical Relations
  ],
  "validation_report": {
    "rejected_edges_count": 0,
    "quarantined_entities_count": 0
  }
}