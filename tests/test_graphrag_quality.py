import os
import pytest
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def neo4j_session():
    """Fixture to provide a Neo4j session for all tests."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    session = driver.session(database=database)
    yield session
    session.close()
    driver.close()

# ---------------------------------------------------------
# GROUP 1: Basic Retrieval & Modality Check
# ---------------------------------------------------------

def test_q1_quyen_chung_nguoi_sdd(neo4j_session):
    """Rights of Land Users - Article 26: Expected >= 8 ALLOW actions."""
    cypher = """
        MATCH (subj:LEGAL_SUBJECT)<-[:HAS_SUBJECT]-(norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
        WHERE subj.canonical_text CONTAINS "Người sử dụng đất" AND norm.modality = 'ALLOW'
        RETURN act.canonical_text AS action
    """
    result = neo4j_session.run(cypher)
    actions = {record["action"] for record in result}
    
    assert len(actions) >= 8, f"Expected at least 8 distinct actions for rights, got {len(actions)}"
    # Verify we didn't accidentally mix PROHIBIT actions (the cypher guarantees ALLOW, but checking structural integrity)
    assert all(actions), "Actions should not be empty strings"

def test_q2_nghia_vu_chung(neo4j_session):
    """Obligations of Land Users - Article 31: Expected >= 7 REQUIRE actions."""
    cypher = """
        MATCH (subj:LEGAL_SUBJECT)<-[:HAS_SUBJECT]-(norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
        WHERE subj.canonical_text CONTAINS "Người sử dụng đất" AND norm.modality = 'REQUIRE'
        RETURN act.canonical_text AS action
    """
    result = neo4j_session.run(cypher)
    actions = {record["action"] for record in result}
    
    assert len(actions) >= 7, f"Expected at least 7 distinct actions for obligations, got {len(actions)}"


# ---------------------------------------------------------
# GROUP 2: Conditions & Exceptions (Context Collapse Prevention)
# ---------------------------------------------------------

def test_q5_dieu_kien_chuyen_nhuong(neo4j_session):
    """Transfer Conditions - Article 45, Clause 1: Expected exactly 5 conditions (a, b, c, d, đ)."""
    cypher = """
        MATCH (norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
        WHERE act.canonical_text CONTAINS "Chuyển nhượng"
        UNWIND norm.source_node_ids AS phys_id
        MATCH (p:LegalNode {id: phys_id})
        WHERE p.id CONTAINS "dieu-45_khoan-1"
        MATCH (norm)-[:HAS_CONDITION]->(cond:CONDITION)
        RETURN collect(DISTINCT cond.canonical_text) AS conditions
    """
    result = neo4j_session.run(cypher)
    record = result.single()
    conditions = record["conditions"] if record else []
    
    assert len(conditions) == 5, f"Expected exactly 5 conditions (a, b, c, d, đ) for Article 45 Clause 1 transfer, got {len(conditions)}. Context Collapse occurred during extraction!"

def test_q6_ngoai_le_chuyen_nhuong(neo4j_session):
    """Transfer Exceptions - Article 45, Clause 1, Point a: Expected > 0 exceptions."""
    cypher = """
        MATCH (norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
        WHERE act.canonical_text CONTAINS "Chuyển nhượng"
        UNWIND norm.source_node_ids AS phys_id
        MATCH (p:LegalNode {id: phys_id})
        WHERE p.id CONTAINS "dieu-45_khoan-1"
        MATCH (norm)-[:HAS_EXCEPTION]->(exc:EXCEPTION)
        RETURN collect(DISTINCT exc.canonical_text) AS exceptions
    """
    result = neo4j_session.run(cypher)
    record = result.single()
    exceptions = record["exceptions"] if record else []
    
    assert len(exceptions) > 0, f"Expected > 0 exceptions for Article 45 Clause 1 (e.g. 'thừa kế', 'dồn điền đổi thửa'), got {len(exceptions)}"
    # Verify semantic context
    has_target = any("thừa kế" in exc.lower() or "đổi" in exc.lower() for exc in exceptions)
    assert has_target, f"Expected exceptions to mention specific legal exclusions (thừa kế, đổi thửa), got {exceptions}"


# ---------------------------------------------------------
# GROUP 3: Cross-Reference Resolution
# ---------------------------------------------------------

def test_q9_dan_chieu_dieu_32(neo4j_session):
    """Cross-reference Article 32 -> 26, 31"""
    cypher = """
        MATCH (p:LegalNode {id: "doc_chuong-iii_muc-2_dieu-32_khoan-1"})-[:MENTIONS]->(norm:GLOBAL_NORM)-[:REFERENCE_TO]->(target:LegalNode)
        RETURN collect(target.id) AS targets
    """
    result = neo4j_session.run(cypher)
    record = result.single()
    targets = record["targets"] if record else []
    
    assert len(targets) > 0, "No cross-references found for Article 32, Clause 1. The REFERENCE_TO edges were not built."
    
    has_d26 = any("dieu-26" in t for t in targets)
    has_d31 = any("dieu-31" in t for t in targets)
    
    assert has_d26, f"Expected cross-reference to dieu-26, but targets were {targets}"
    assert has_d31, f"Expected cross-reference to dieu-31, but targets were {targets}"


# ---------------------------------------------------------
# GROUP 4 & 5: Logical Reasoning & Comparison
# ---------------------------------------------------------

def test_q17_so_sanh_quyen(neo4j_session):
    """Compare Rights: Individual vs Economic Org on 'thuê đất trả tiền hằng năm'."""
    def get_rights(subject):
        cypher = """
            MATCH (subj:LEGAL_SUBJECT)<-[:HAS_SUBJECT]-(norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
            WHERE subj.canonical_text CONTAINS $subject AND norm.modality = 'ALLOW'
            MATCH (norm)-[:HAS_CONDITION]->(cond:CONDITION)
            WHERE cond.canonical_text CONTAINS "thuê đất trả tiền hằng năm"
            RETURN collect(DISTINCT act.canonical_text) AS actions
        """
        result = neo4j_session.run(cypher, subject=subject)
        record = result.single()
        return record["actions"] if record else []
        
    ca_nhan_rights = get_rights("Cá nhân")
    to_chuc_rights = get_rights("Tổ chức kinh tế")
    
    # Check graph separation - Cá nhân MUST have "thừa kế"
    ca_nhan_has_thua_ke = any("thừa kế" in act.lower() for act in ca_nhan_rights)
    assert ca_nhan_has_thua_ke, f"Expected 'Cá nhân' to have 'thừa kế' right under annual lease, got: {ca_nhan_rights}"
    
    # Check graph separation - Tổ chức kinh tế MUST NOT have "thừa kế"
    to_chuc_has_thua_ke = any("thừa kế" in act.lower() for act in to_chuc_rights)
    assert not to_chuc_has_thua_ke, f"Expected 'Tổ chức kinh tế' to NOT have 'thừa kế' right. Over-merging detected! Got: {to_chuc_rights}"
