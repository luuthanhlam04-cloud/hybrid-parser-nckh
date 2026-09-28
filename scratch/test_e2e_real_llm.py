import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import openai
import instructor

sys.path.append(r"c:\Users\luuth\NCKH\hybrid_parser_graphrag")
load_dotenv()

from src.llm_extraction.schema_manager import SemanticExtraction
from src.llm_extraction.prompt_builder import SYSTEM_PROMPT
from src.ontology.ontology_builder import OntologyBuilder

def test_real_llm_e2e():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Không tìm thấy OPENROUTER_API_KEY")
        return

    # Khởi tạo OpenAI Client qua OpenRouter
    client = instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON
    )

    text_to_extract = "Hợp đồng chuyển nhượng quyền sử dụng đất phải được công chứng."
    
    print(f"1. Gửi văn bản cho LLM (M6): '{text_to_extract}'")
    prompt = f"[BỐI CẢNH] Không có\n[NỘI DUNG CẦN TRÍCH XUẤT]\n{text_to_extract}"
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            response_model=SemanticExtraction,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
    except Exception as e:
        print(f"Lỗi gọi LLM: {e}")
        return

    m6_output = response.model_dump()
    print("\n2. Kết quả M6 (Raw JSON từ LLM):")
    print(json.dumps(m6_output, ensure_ascii=False, indent=2))
    
    print("\n3. Đưa qua M7 Ontology Builder...")
    # Giả lập dữ liệu đồ thị vật lý cho builder
    m6_extracted_data = [{
        "node_id": "test_node_01",
        "extraction": m6_output
    }]
    
    m6_path = Path("scratch/temp_m6_test.json")
    with open(m6_path, "w", encoding="utf-8") as f:
        json.dump(m6_extracted_data, f, ensure_ascii=False, indent=2)
        
    builder = OntologyBuilder()
    
    final_graph = builder.build(m6_path=m6_path)
    
    print("\n4. Kết quả M7 (Final Graph):")
    print(f"- Số lượng Mentions: {len(final_graph.active_nodes)}")
    print(f"- Số lượng Edges: {len(final_graph.active_edges)}")
    print(f"- Số lượng Norms: {len(final_graph.norms)}")
    
    if final_graph.norms:
        norm = final_graph.norms[0]
        print("\n--- Chi tiết NormAssertion ---")
        print(f"Modality: {norm.modality}")
        print(f"Subject IDs: {norm.subject_ids}")
        print(f"Subject Status: {getattr(norm, 'subject_status', 'RESOLVED')}")
        print(f"Action IDs: {norm.action_ids}")
        print(f"Object IDs: {norm.object_ids}")
        print(f"Status: {norm.status.value}")
        
    print("\n--- Chi tiết Edges ---")
    for edge in final_graph.active_edges:
        print(f"{edge.source_id} --[{edge.relation_type}]--> {edge.target_id}")

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    test_real_llm_e2e()
