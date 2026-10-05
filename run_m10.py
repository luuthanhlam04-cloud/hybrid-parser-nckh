import argparse
import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

from src.retrieval.anchor_search import AnchorSearch
from src.retrieval.graph_query import GraphQuery
from src.retrieval.answer_generator import AnswerGenerator
from src.retrieval.context_assembler import ContextAssembler
from src.retrieval.m10_pipeline import M10Pipeline

def main():
    parser = argparse.ArgumentParser(description="Test M10 Graph Retrieval Pipeline")
    parser.add_argument("question", type=str, help="Câu hỏi pháp lý bằng tiếng Việt")
    parser.add_argument("--mode", choices=["A", "B"], default="A", help="Mode A (Norm) hoặc Mode B (k-hop)")
    parser.add_argument("--top-k", type=int, default=5, help="Số lượng mỏ neo (Anchor nodes) cần tìm")
    args = parser.parse_args()

    load_dotenv()
    
    # Hỗ trợ lấy từ LLM_API_KEY nếu OPENROUTER_API_KEY không có
    if not os.getenv("OPENROUTER_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = os.getenv("LLM_API_KEY", "")
        
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Lỗi: Không tìm thấy OPENROUTER_API_KEY hoặc LLM_API_KEY trong file .env!")
        print("Vui lòng mở file .env và điền key vào trước khi chạy M10.")
        sys.exit(1)

    uri = os.getenv("NEO4J_URI", "neo4j+s://59bbc655.databases.neo4j.io")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    
    print("[*] Đang kết nối Neo4j...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    print(f"[*] Khởi tạo M10 Pipeline (Đang load model nhúng sentence-transformers, có thể hơi lâu chút)...")
    try:
        pipeline = M10Pipeline(
            anchor_search=AnchorSearch(driver=driver),
            graph_query=GraphQuery(driver=driver),
            answer_generator=AnswerGenerator.from_environment(),
            context_assembler=ContextAssembler()
        )
        
        print(f"\n[*] Đang truy vấn câu hỏi (Mode {args.mode}): '{args.question}'")
        result = pipeline.answer(
            question=args.question,
            mode=args.mode,
            top_k=args.top_k
        )
        
        print("\n" + "="*70)
        print("💡 CÂU TRẢ LỜI TỪ LLM:")
        print("="*70)
        print(result["answer"])
        print("\n" + "="*70)
        print(f"🔍 NGỮ CẢNH (CONTEXT) TRÍCH XUẤT TỪ NEO4J ({result['retrieved_count']} nodes):")
        print("="*70)
        print(result["context"])
        
    except Exception as e:
        print(f"\n[!] Đã xảy ra lỗi khi chạy pipeline: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
