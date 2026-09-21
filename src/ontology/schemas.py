# -*- coding: utf-8 -*-
"""
schemas.py — Data Contracts cho Module 7 (Ontology / Semantic Canonicalization)

Kiến trúc 6 lớp:
  Layer 1: Core Semantic Types (LegalSubject, LegalAction, ...)
  Layer 2: Controlled Taxonomy (subtype, qua taxonomy_registry.yaml)
  Layer 3: Local Semantic Mention (mỗi lần xuất hiện của entity trong corpus)
  Layer 4: Canonical Concept Hub (khái niệm dùng chung, không chứa normative edges)
  Layer 5: Norm / Assertion (giữ đúng normative context)
  Layer 6: Neo4j Projection (output labels cho downstream)

QUY TẮC BẤT BIẾN:
  1. Normative edges (ALLOW/REQUIRE/...) KHÔNG bao giờ đặt trên CanonicalConcept.
  2. Condition/Exception/Consequence thuộc NormAssertion, không thuộc LegalAction.
  3. Mọi LocalMention phải có provenance_node_id ≠ None.
  4. DENOTES: LocalMention → CanonicalConcept (không phải INSTANCE_OF).

ID Formula:
  LocalMention  : <physical_node_id>#<MENTION_TYPE>#<local_index>
  NormAssertion : <physical_node_id>#NORM#<local_index>
  CanonicalConcept: CONCEPT_<NAME> (từ concept_registry.yaml)

Ví dụ:
  doc_chuong-iii_muc-1_dieu-48_khoan-2_p520#SUBJECT#1
  doc_chuong-iii_muc-1_dieu-48_khoan-2_p520#NORM#1
  CONCEPT_ETHNIC_MINORITY_INDIVIDUAL
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, model_validator


# =============================================================================
# ENUMS
# =============================================================================

class MentionType(str, Enum):
    """Loại entity mention — map 1-1 với M6 entity_type."""
    SUBJECT   = "SUBJECT"
    ACTION    = "ACTION"
    OBJECT    = "OBJECT"
    CONDITION = "CONDITION"
    EXCEPTION = "EXCEPTION"
    REFERENCE = "REFERENCE"
    PENALTY   = "PENALTY"


class SemanticType(str, Enum):
    """Core Semantic Type sau khi canonical hóa."""
    LEGAL_SUBJECT     = "LegalSubject"
    LEGAL_ACTION      = "LegalAction"
    LEGAL_OBJECT      = "LegalObject"
    LEGAL_CONSEQUENCE = "LegalConsequence"
    CONDITION         = "Condition"
    EXCEPTION         = "Exception"
    REFERENCE         = "Reference"    # Tạm thời trong pipeline; resolve thành REFERENCES edge


class NormativeModality(str, Enum):
    """Normative modality — dùng trong NormAssertion, không phải entity class."""
    ALLOW    = "ALLOW"
    REQUIRE  = "REQUIRE"
    PROHIBIT = "PROHIBIT"


class RelationType(str, Enum):
    """Loại cạnh trong Canonical Semantic Graph."""
    # Normative (simple norm)
    ALLOW    = "ALLOW"
    REQUIRE  = "REQUIRE"
    PROHIBIT = "PROHIBIT"
    # Structural
    HAS_OBJECT      = "HAS_OBJECT"
    HAS_CONDITION   = "HAS_CONDITION"
    HAS_EXCEPTION   = "HAS_EXCEPTION"
    HAS_CONSEQUENCE = "HAS_CONSEQUENCE"
    # Reference
    REFERENCES = "REFERENCES"
    # Canonicalization
    DENOTES = "DENOTES"
    # NormAssertion relations
    HAS_SUBJECT = "HAS_SUBJECT"
    HAS_ACTION  = "HAS_ACTION"


class MentionStatus(str, Enum):
    """Trạng thái sau Semantic Role Audit."""
    VALID      = "VALID"       # Role hợp lệ
    CORRECTED  = "CORRECTED"   # Đã sửa tự động bằng rule-based (pattern đủ chắc)
    UNRESOLVED = "UNRESOLVED"  # Uncertain → giữ nguyên + cắm cờ để review


class NormStatus(str, Enum):
    VALID   = "VALID"
    FLAGGED = "FLAGGED"


class LogicOperator(str, Enum):
    AND = "AND"
    OR  = "OR"


# =============================================================================
# LAYER 3: LOCAL SEMANTIC MENTION
# =============================================================================

class LocalMention(BaseModel):
    """
    Một lần xuất hiện cụ thể của một semantic entity trong corpus.

    ID formula: <physical_node_id>#<MENTION_TYPE>#<local_index>
    Ví dụ: doc_chuong-iii_dieu-48_khoan-2_p520#SUBJECT#1

    QUAN TRỌNG:
      - Mọi normative relation (ALLOW/REQUIRE/...) nối GIỮA các LocalMention,
        KHÔNG nối từ CanonicalConcept.
      - provenance_node_id KHÔNG ĐƯỢC là None.
    """
    id: str = Field(description="<physical_node_id>#<MENTION_TYPE>#<index>")

    # Thông tin từ M6
    mention_type: MentionType = Field(description="Loại entity theo M6 schema")
    raw_text: str = Field(description="Chuỗi nguyên văn từ M6 extraction")
    m6_local_id: str = Field(description="ID cục bộ trong M6 (e1, e2, ...) để map relations")

    # Thông tin sau M7 canonicalization
    semantic_type: SemanticType = Field(description="Core Semantic Type sau canonicalize")
    subtype: Optional[str] = Field(
        default=None,
        description="Controlled subtype từ taxonomy_registry.yaml (VD: EthnicMinorityIndividual)"
    )
    canonical_concept_id: Optional[str] = Field(
        default=None,
        description="ID của CanonicalConcept mà Mention này DENOTES tới"
    )

    # Provenance — BẮT BUỘC
    provenance_node_id: str = Field(
        description="Physical Graph node ID mà entity này được trích xuất từ đó. KHÔNG ĐƯỢC None."
    )
    evidence: str = Field(
        description="Trích nguyên văn từ Physical Node. KHÔNG được để trống."
    )

    # Status từ Semantic Role Audit
    status: MentionStatus = Field(default=MentionStatus.VALID)
    audit_note: Optional[str] = Field(
        default=None,
        description="Ghi chú từ semantic role audit (rule_id, lý do CORRECTED/UNRESOLVED)"
    )

    # Neo4j labels (Layer 6 projection)
    neo4j_labels: List[str] = Field(
        default_factory=list,
        description="Labels sẽ gán khi nạp Neo4j. VD: [LegalSubject, DomesticEntity, EthnicMinority]"
    )

    @model_validator(mode='after')
    def validate_provenance(self) -> 'LocalMention':
        if not self.provenance_node_id or not self.provenance_node_id.strip():
            raise ValueError(f"LocalMention {self.id}: provenance_node_id không được rỗng!")
        if not self.evidence or not self.evidence.strip():
            raise ValueError(f"LocalMention {self.id}: evidence không được rỗng!")
        return self


# =============================================================================
# LAYER 4: CANONICAL CONCEPT HUB
# =============================================================================

class CanonicalConcept(BaseModel):
    """
    Một khái niệm pháp lý dùng chung — tồn tại DUY NHẤT trong toàn bộ graph.

    QUAN TRỌNG BẤT BIẾN:
      - Normative edges (ALLOW/REQUIRE/PROHIBIT/HAS_CONDITION...) KHÔNG BAO GIỜ
        được đặt trên CanonicalConcept.
      - source_mentions chỉ là aggregation field để thống kê; không dùng để
        merge normative context.
    """
    id: str = Field(description="CONCEPT_<NAME> — global unique ID")
    concept_type: SemanticType = Field(description="Core Semantic Type")
    preferred_name: str = Field(description="Tên chuẩn của khái niệm")
    alt_labels: List[str] = Field(
        default_factory=list,
        description="Các biến thể ngôn ngữ khác nhau trong corpus"
    )
    taxonomy_path: Optional[str] = Field(
        default=None,
        description="Đường dẫn trong Controlled Taxonomy. VD: LegalSubject.DomesticEntity.EthnicMinorityIndividual"
    )

    # Aggregation — CHỈ ĐỂ THỐNG KÊ
    source_mention_count: int = Field(
        default=0,
        description="Số lần concept này được DENOTES tới (aggregation only)"
    )


# =============================================================================
# LAYER 5: NORM / ASSERTION
# =============================================================================

class ConditionGroup(BaseModel):
    """
    Nhóm điều kiện với logic AND/OR (flat, v1).
    Nested Boolean phức tạp → mark COMPLEX_LOGIC, không flatten sai.
    """
    group_id: str
    operator: LogicOperator = LogicOperator.AND
    condition_ids: List[str] = Field(description="LocalMention IDs của Condition type")
    is_complex: bool = Field(
        default=False,
        description="True nếu cấu trúc lồng nhau phức tạp → UNRESOLVED/COMPLEX_LOGIC"
    )


class NormAssertion(BaseModel):
    """
    Một quy phạm pháp lý đầy đủ — giữ toàn bộ normative context trong cùng một frame.

    Tại sao cần NormAssertion (không chỉ dùng ALLOW/REQUIRE edge):
      Cùng action "chuyển nhượng" có thể xuất hiện trong 3 quy tắc với
      3 bộ điều kiện hoàn toàn khác nhau. Nếu gắn condition vào Action thì
      bộ điều kiện của quy tắc này bị trộn sang quy tắc kia → SAI ngữ nghĩa.

    Sơ đồ:
      NormAssertion
        ├── HAS_SUBJECT  → LocalMention (LegalSubject)
        ├── HAS_ACTION   → LocalMention (LegalAction)
        ├── HAS_OBJECT   → LocalMention (LegalObject)
        ├── HAS_CONDITION → LocalMention (Condition)
        ├── HAS_EXCEPTION → LocalMention (Exception)
        └── HAS_CONSEQUENCE → LocalMention (LegalConsequence)
    """
    id: str = Field(description="<physical_node_id>#NORM#<index>")
    modality: NormativeModality = Field(description="ALLOW / REQUIRE / PROHIBIT")

    # LocalMention ID lists (references, không embed trực tiếp để tránh cycle)
    subject_ids: List[str] = Field(default_factory=list)
    action_ids: List[str] = Field(default_factory=list)
    object_ids: List[str] = Field(default_factory=list)
    condition_ids: List[str] = Field(default_factory=list)
    condition_groups: List[ConditionGroup] = Field(
        default_factory=list,
        description="Nhóm điều kiện với AND/OR logic (flat). Nested → is_complex=True"
    )
    exception_ids: List[str] = Field(default_factory=list)
    consequence_ids: List[str] = Field(default_factory=list)

    # Provenance & Evidence
    provenance_node_id: str = Field(description="Physical Graph node ID")
    evidence: str = Field(description="Trích nguyên văn")
    rule_id: str = Field(description="Mã quy tắc. VD: RULE_M7_01 — phục vụ audit")

    # Status
    status: NormStatus = Field(default=NormStatus.VALID)
    notes: Optional[str] = Field(default=None)


# =============================================================================
# SEMANTIC EDGES
# =============================================================================

class SemanticEdge(BaseModel):
    """
    Một cạnh trong Canonical Semantic Graph.

    Loại cạnh:
      - Simple norm: ALLOW/REQUIRE/PROHIBIT (source=LocalMention → target=LocalMention)
      - Structural:  HAS_OBJECT/HAS_CONDITION/HAS_EXCEPTION/HAS_CONSEQUENCE
      - Canonicalization: DENOTES (LocalMention → CanonicalConcept)
      - Reference: REFERENCES (LocalMention → Physical Node ID)
      - NormAssertion: HAS_SUBJECT/HAS_ACTION/... (NormAssertion → LocalMention)
    """
    source_id: str
    target_id: str
    relation_type: RelationType
    evidence: Optional[str] = Field(default=None)
    rule_id: Optional[str] = Field(default=None)
    logic_group: Optional[str] = Field(
        default=None,
        description="Nhóm logic AND/OR cho Condition edges (VD: G1, G2)"
    )
    operator: Optional[LogicOperator] = Field(
        default=None,
        description="AND hoặc OR cho nhóm logic_group"
    )


# =============================================================================
# VALIDATION REPORT
# =============================================================================

class ValidationReport(BaseModel):
    """Báo cáo kết quả validation của toàn bộ pipeline M7."""
    total_mentions: int = 0
    valid_mentions: int = 0
    corrected_mentions: int = 0
    unresolved_mentions: int = 0

    total_norms: int = 0
    valid_norms: int = 0
    flagged_norms: int = 0

    total_edges: int = 0
    rejected_edges: int = 0

    total_references: int = 0
    resolved_references: int = 0
    unresolved_references: int = 0

    total_concepts: int = 0
    rejected_reasons: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# CANONICAL SEMANTIC GRAPH (OUTPUT)
# =============================================================================

class CanonicalSemanticGraph(BaseModel):
    """
    Output chính của Module 7 — đầu vào của Module 8 (Fusion Engine).

    Cấu trúc:
      - nodes:      List[LocalMention]   — mọi semantic entity
      - norms:      List[NormAssertion]  — mọi normative assertion
      - concepts:   List[CanonicalConcept] — Concept Hub nodes
      - edges:      List[SemanticEdge]   — tất cả cạnh
      - validation_report: ValidationReport
    """
    metadata: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[LocalMention] = Field(default_factory=list)
    norms: List[NormAssertion] = Field(default_factory=list)
    concepts: List[CanonicalConcept] = Field(default_factory=list)
    edges: List[SemanticEdge] = Field(default_factory=list)
    validation_report: ValidationReport = Field(default_factory=ValidationReport)

    def get_mention_by_id(self, mention_id: str) -> Optional[LocalMention]:
        for node in self.nodes:
            if node.id == mention_id:
                return node
        return None

    def get_concept_by_id(self, concept_id: str) -> Optional[CanonicalConcept]:
        for concept in self.concepts:
            if concept.id == concept_id:
                return concept
        return None

    def summary(self) -> str:
        r = self.validation_report
        return (
            f"M7 Output: {r.total_mentions} mentions "
            f"(valid={r.valid_mentions}, corrected={r.corrected_mentions}, "
            f"unresolved={r.unresolved_mentions}) | "
            f"{r.total_norms} norms | "
            f"{r.total_concepts} concepts | "
            f"{r.total_edges} edges "
            f"(rejected={r.rejected_edges}) | "
            f"refs {r.resolved_references}/{r.total_references} resolved"
        )
