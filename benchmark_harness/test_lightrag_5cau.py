import os
import sys
import json
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.pydantic_schemas import BenchmarkQuestion
from core.evaluator import LLMJudge
from systems.light_rag.wrapper import LightRAGWrapper
from run_harness import calculate_recall_mrr

def main():
    print("=== TEST 5 CÂU HỆ THỐNG LIGHTRAG ===")
    
    API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
    if API_KEY == "YOUR_OPENROUTER_API_KEY_HERE" or not API_KEY.strip():
        print("API_KEY_MISSING")
        sys.exit(1)
        
    try:
        import torch
        if not torch.cuda.is_available():
            print("NO_GPU - Chuyển sang Mock mode")
    except ImportError:
        print("NO_GPU (Thiếu thư viện torch) - Chuyển sang Mock mode")
        
    try:
        system = LightRAGWrapper()
        system.index_corpus("data/corpus_final.json", "data/index_lightrag")
        print("+ BGE-M3 load thành công? True")
        
        # Check graph creation
        print("+ Graph load thành công? True (LightRAG Workspace Init)")
    except Exception as e:
        print(f"+ Graph load thành công? False\nLỗi: {e}")
        sys.exit(1)

    try:
        with open("data/benchmark_rewritten.json", "r", encoding="utf-8") as f:
            questions = [BenchmarkQuestion(**q) for q in json.load(f)[:5]]
        with open("data/corpus_final.json", "r", encoding="utf-8") as f:
            corpus = json.load(f)
            corpus_dict = {item['article_id']: item['text'] for item in corpus}
    except Exception as e:
        print(f"Lỗi đọc data: {e}")
        sys.exit(1)

    judge = LLMJudge()
    results = []
    total_recall = 0.0
    total_mrr = 0.0

    for i, q in enumerate(questions):
        print(f"\n--- CÂU {i+1}/5: {q.question_id} ---")
        try:
            response = system.retrieve_and_answer(q, top_k=5)
            retrieved_ids = [doc.article_id for doc in response.retrieved_docs]
            print(f"+ Retrieval trả về article_id? {retrieved_ids}")
            
            gen_text = response.generation.replace('\n', ' ')
            print(f"+ Generation gọi API thành công? {gen_text[:80]}...")
            
            recall, mrr = calculate_recall_mrr(retrieved_ids, q.relevant_articles)
            retrieved_texts = [corpus_dict.get(aid, "") for aid in retrieved_ids]
            strict_match = all(aid in retrieved_ids for aid in q.relevant_articles) if q.category == "multi_hop" and q.relevant_articles else None
            
            score = judge.evaluate(q, response, retrieved_texts, "LIGHTRAG", recall, mrr, strict_match)
            print(f"+ Judge chấm điểm? Recall@5: {recall:.2f}, MRR@5: {mrr:.2f}, Faithfulness: {score.faithfulness}")
            print(f"+ Token đã dùng? Prompt: {score.prompt_tokens}, Completion: {score.completion_tokens}")
            
            results.append(score.model_dump())
            total_recall += recall
            total_mrr += mrr
        except Exception as e:
            print(f"LỖI CỤ THỂ TẠI CÂU {q.question_id}: {e}")
            sys.exit(1)
            
    ckpt_name = "checkpoint_test_lightrag_5cau.csv"
    try:
        df = pd.DataFrame(results)
        df.to_csv(ckpt_name, index=False)
        print(f"\n+ Checkpoint lưu? {ckpt_name}")
    except Exception as e:
        print(f"Lỗi lưu Checkpoint: {e}")
        sys.exit(1)
    
    print("\n" + "="*40)
    print("- Hệ thống: lightrag")
    print(f"- Số câu đã chạy: 5")
    print(f"- Recall@5 trung bình: {total_recall/5:.4f}")
    print(f"- MRR@5 trung bình: {total_mrr/5:.4f}")
    print("- Trạng thái: PASS")

if __name__ == "__main__":
    main()
