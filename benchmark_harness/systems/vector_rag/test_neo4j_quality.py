import os
import time
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def run_test(driver, test_name, cypher, expected_count=0, expect_operator="=="):
    print(f"\n{'-'*60}")
    print(f"🚀 {test_name}")
    print(f"{'-'*60}")
    
    start_time = time.time()
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(cypher)
        records = list(result)
        
    execution_time = (time.time() - start_time) * 1000
    actual_count = len(records)
    
    # Evaluate expectation
    passed = False
    if expect_operator == "==":
        passed = actual_count == expected_count
    elif expect_operator == ">=":
        passed = actual_count >= expected_count
    elif expect_operator == "<=":
        passed = actual_count <= expected_count
        
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"Status: {status}")
    print(f"Records returned: {actual_count}")
    print(f"Execution time: {execution_time:.2f} ms")
    
    if not passed and actual_count > 0:
        print("\n⚠️ Sample failing records:")
        for idx, rec in enumerate(records[:3]):
            print(f"  {idx+1}. {rec.data()}")
            
    return passed

def run_performance_test(driver, test_name, cypher):
    print(f"\n{'-'*60}")
    print(f"⚡ {test_name}")
    print(f"{'-'*60}")
    
    start_time = time.time()
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(cypher)
        records = list(result)
        
    execution_time = (time.time() - start_time) * 1000
    passed = execution_time < 50
    status = "✅ PASS" if passed else "⚠️ WARNING"
    
    print(f"Status: {status} (Target: < 50ms)")
    print(f"Records returned: {len(records)}")
    print(f"Execution time: {execution_time:.2f} ms")
    
    if records:
        print("\n📄 Sample extracted data:")
        print(f"  {records[0].data()}")

def main():
    print(f"🔗 Connecting to Neo4j at {NEO4J_URI} (Database: {NEO4J_DATABASE})...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        # TEST 1.1: No Broken Physical Branches
        run_test(driver, "Test 1.1: Không có Nhánh vật lý gãy (No Broken Physical Branches)", """
            MATCH (n:LegalNode) WHERE n:CLAUSE OR n:POINT
            OPTIONAL MATCH path = (n)-[:BELONG_TO*]->(c:CHAPTER)
            WITH n, path
            WHERE path IS NULL
            RETURN n.id, labels(n)
        """)
        
        # TEST 1.2: RAG Grounding Readiness
        run_test(driver, "Test 1.2: RAG Grounding Readiness (Sẵn sàng Text & Vector)", """
            MATCH (n:LegalNode)
            WHERE (n.text IS NULL OR trim(n.text) = "") 
               OR n.embedding IS NULL 
               OR size(n.embedding) <> 768
            RETURN n.id, labels(n)
        """)
        
        # TEST 2.1: No Ghost Pointers
        run_test(driver, "Test 2.1: Không có Con trỏ Ma (No Ghost Pointers)", """
            MATCH (norm:GLOBAL_NORM)
            UNWIND norm.source_node_ids AS phys_id
            OPTIONAL MATCH (p:LegalNode {id: phys_id})
            WITH norm, phys_id, p
            WHERE p IS NULL
            RETURN norm.id, phys_id AS dead_pointer
        """)
        
        # TEST 2.2: Inverted Index hợp lệ (Mentions Coverage)
        # Using <= to not fail if there are some orphaned concepts, just as a warning.
        print(f"\n{'-'*60}")
        print(f"🚀 Test 2.2: Inverted Index hợp lệ (Mentions Coverage)")
        print(f"{'-'*60}")
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (c:SemanticEntity) WHERE NOT c:GLOBAL_NORM
                OPTIONAL MATCH (:LegalNode)-[:MENTIONS]->(c)
                WITH c, count(*) AS refs
                WHERE refs = 0
                RETURN c.id, c.canonical_text
            """)
            records = list(result)
            if len(records) == 0:
                print("Status: ✅ PASS")
            else:
                print(f"Status: ⚠️ WARNING (Found {len(records)} unmentioned concepts)")
            
            if records:
                print("Sample unmentioned concepts (Imaginary / Hallucinated?):")
                for rec in records[:3]:
                    print(f"  - {rec['c.id']}: {rec['c.canonical_text']}")
        
        # TEST 3.1: Mệnh đề hoàn chỉnh (Action-bound Norms)
        run_test(driver, "Test 3.1: Mệnh đề hoàn chỉnh (Action-bound Norms)", """
            MATCH (norm:GLOBAL_NORM)
            OPTIONAL MATCH (norm)-[:HAS_ACTION]->(a:LEGAL_ACTION)
            WITH norm, a
            WHERE a IS NULL
            RETURN norm.id, norm.modality
        """)
        
        # TEST 3.2: Bắt Xung đột Quy phạm trực diện (Direct Deontic Collision)
        run_test(driver, "Test 3.2: Bắt Xung đột Quy phạm trực diện (Direct Deontic Collision)", """
            MATCH (s:LEGAL_SUBJECT)<-[:HAS_SUBJECT]-(n1:GLOBAL_NORM)-[:HAS_ACTION]->(a:LEGAL_ACTION)
            MATCH (s)<-[:HAS_SUBJECT]-(n2:GLOBAL_NORM)-[:HAS_ACTION]->(a)
            WHERE n1.id < n2.id 
              AND n1.modality <> n2.modality
              AND NOT (n1)-[:HAS_CONDITION]->() 
              AND NOT (n2)-[:HAS_CONDITION]->()
            RETURN s.canonical_text, a.canonical_text, n1.modality, n2.modality
        """)
        
        # TEST 4.1: Subgraph Extraction (Bài test truy vấn lõi)
        run_performance_test(driver, "Test 4.1: Subgraph Extraction (Bài test truy vấn lõi)", """
            MATCH (subj:LEGAL_SUBJECT)<-[:HAS_SUBJECT]-(norm:GLOBAL_NORM)-[:HAS_ACTION]->(act:LEGAL_ACTION)
            WHERE subj.canonical_text CONTAINS "Người sử dụng đất" 
              AND act.canonical_text CONTAINS "chuyển nhượng"
            UNWIND norm.source_node_ids AS phys_id
            MATCH (p:LegalNode {id: phys_id})-[:BELONG_TO*]->(art:ARTICLE)
            RETURN norm.modality, art.number, p.text
        """)
        
    finally:
        driver.close()
        print(f"\n{'-'*60}")
        print("🎯 TẤT CẢ BÀI KIỂM ĐỊNH HOÀN TẤT!")
        print(f"{'-'*60}")

if __name__ == "__main__":
    main()
