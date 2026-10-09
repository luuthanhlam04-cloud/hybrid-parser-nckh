import json
import time
import os
import pandas as pd
from typing import List, Dict

from core.pydantic_schemas import BenchmarkQuestion
from core.evaluator import LLMJudge

import argparse

# Kế hoạch là dev team sẽ import wrapper thật ở đây
from systems.hybrid_rag.wrapper import HybridRAGWrapper
from systems.vector_rag.wrapper import VectorRAGWrapper
from systems.light_rag.wrapper import LightRAGWrapper

def load_data():
    with open("data/benchmark_rewritten.json", "r", encoding="utf-8") as f:
        questions = [BenchmarkQuestion(**q) for q in json.load(f)]
        
    with open("data/corpus_final.json", "r", encoding="utf-8") as f:
        corpus = json.load(f)
    corpus_dict = {item['article_id']: item['text'] for item in corpus}
    return questions, corpus_dict

def calculate_recall_mrr(retrieved_ids: List[str], ground_truth: List[str]):
    if not ground_truth:
        return 0.0, 0.0 # Bỏ qua hoặc tính riêng cho negative
    
    hits = [1 if aid in ground_truth else 0 for aid in retrieved_ids]
    recall = sum(hits) / len(ground_truth) if ground_truth else 0.0
    
    mrr = 0.0
    for i, aid in enumerate(retrieved_ids):
        if aid in ground_truth:
            mrr = 1.0 / (i + 1)
            break
            
    return recall, mrr

def run_benchmark(system_name="hybrid", n_test=None, n_docs=None):
    print(f"=== STARTING BENCHMARK HARNESS FOR {system_name.upper()} ===")
    questions, corpus_dict = load_data()
    print(f"Loaded {len(questions)} questions.")
    
    # Khởi tạo hệ thống (Trên Kaggle sẽ tốn VRAM GPU ở đây)
    if system_name == "vector":
        system = VectorRAGWrapper()
    elif system_name == "hybrid":
        system = HybridRAGWrapper()
    elif system_name in ["light", "lightrag"]:
        system = LightRAGWrapper()
    else:
        raise ValueError(f"System {system_name} is not supported.")
        
    # Thực hiện Indexing dữ liệu corpus trước khi benchmark
    if system_name == "lightrag":
        n_docs_for_lightrag = n_docs if n_docs is not None else 50
        system.index_corpus("data/corpus_final.json", "data/index", n_docs=n_docs_for_lightrag, resume=True)
    else:
        system.index_corpus("data/corpus_final.json", "data/index")
    
    judge = LLMJudge(model_name="openai/gpt-4o-mini")
    
    checkpoint_file = f"checkpoint_results_{system_name.upper()}.csv"
    results = []
    completed_ids = set()
    if os.path.exists(checkpoint_file):
        try:
            df_ckpt = pd.read_csv(checkpoint_file)
            results = df_ckpt.to_dict('records')
            completed_ids = set(df_ckpt['question_id'].astype(str).tolist())
            print(f"[Resume] Đã load {len(completed_ids)} câu từ Checkpoint cũ.")
        except Exception as e:
            print(f"[Lỗi] Không thể load checkpoint: {e}")
    if system_name in ["light", "lightrag"]:
        if n_docs is not None and n_docs < 500 and n_test is None:
            n_test = 5
            print("[Thông báo] Vì n_docs < 500, tự động giới hạn n_test = 5 để test. (Bạn có thể ép chạy bằng --n_test)")
            
    test_size = n_test if n_test else len(questions)
    
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0
    
    start_time = time.time()
    for i, q in enumerate(questions[:test_size]):
        print(f"\n[{i+1}/{test_size}] Đang xử lý câu hỏi: {q.question_id}")
        
        if str(q.question_id) in completed_ids:
            print("   -> Đã xử lý trong checkpoint (Skip).")
            continue
        
        # 1. RAG chạy (Retrieval + Generation)
        try:
            response = system.retrieve_and_answer(q, top_k=5)
            if not response.generation or "error" in str(response.generation).lower():
                response.generation = "ERROR: LLM Crash"
        except Exception as e:
            print(f"   [Lỗi nghiêm trọng] RAG_CRASHED tại câu {q.question_id}: {e}")
            from core.pydantic_schemas import SystemResponse
            response = SystemResponse(
                question_id=q.question_id,
                retrieved_docs=[],
                generation="ERROR: RAG_CRASHED",
                metadata={"error": str(e)}
            )
        
        # 2. Tính Recall/MRR cơ sở
        retrieved_ids = [doc.article_id for doc in response.retrieved_docs]
        if system_name in ["light", "lightrag"]:
            recall, mrr, strict_match = None, None, None
            print("   -> Recall@5: N/A | MRR@5: N/A (GraphRAG không hỗ trợ chunk ID)")
        else:
            recall, mrr = calculate_recall_mrr(retrieved_ids, q.relevant_articles)
            print(f"   -> Recall@5: {recall:.2f} | MRR@5: {mrr:.2f}")
            strict_match = None
            if q.category == "multi_hop" and q.relevant_articles:
                strict_match = all(aid in retrieved_ids for aid in q.relevant_articles)
            
        # 3. Lấy full text của các bài viết đã retrieve để gửi cho Giám khảo
        retrieved_texts = [corpus_dict.get(aid, "Nội dung không tồn tại.") for aid in retrieved_ids]
        
        # 4. LLM Judge chấm điểm Semantic
        score = judge.evaluate(
            question=q, 
            response=response, 
            retrieved_texts=retrieved_texts, 
            system_name=system_name.upper(),
            recall=recall,
            mrr=mrr,
            strict_match=strict_match
        )
        
        results.append(score.model_dump())
        
        # Cập nhật chi phí
        total_prompt_tokens += score.prompt_tokens or 0
        total_completion_tokens += score.completion_tokens or 0
        total_cost += score.estimated_cost or 0.0
        
        if total_cost > 5.0:
            print(f"\n[BÁO ĐỘNG] Chi phí API đã vượt ngưỡng an toàn ($5.0). Chi phí hiện tại: ${total_cost:.2f}. DỪNG KHẨN CẤP!")
            break
        
        # Tự động lưu Checkpoint sau mỗi 10 câu
        if (i + 1) % 10 == 0 or (i + 1) == test_size:
            df = pd.DataFrame(results)
            df.to_csv(checkpoint_file, index=False)
            print("   [Checkpoint] Đã lưu tiến trình.")
            
    total_time = time.time() - start_time
    
    # 5. Tổng hợp và xuất báo cáo
    df = pd.DataFrame(results)
    out_file = f"final_benchmark_results_{system_name.upper()}.csv"
    df.to_csv(out_file, index=False)
    
    print(f"- Tổng số câu đã chạy: {len(df)}")
    if system_name in ["light", "lightrag"]:
        print("- Recall@5 trung bình: N/A")
        print("- MRR@5 trung bình: N/A")
    else:
        avg_recall = df['recall_at_5'].mean()
        avg_mrr = df['mrr_at_5'].mean()
        print(f"- Recall@5 trung bình: {avg_recall:.4f}")
        print(f"- MRR@5 trung bình: {avg_mrr:.4f}")
    print(f"- Tổng Prompt Tokens: {total_prompt_tokens}")
    print(f"- Tổng Completion Tokens: {total_completion_tokens}")
    print(f"- Ước tính chi phí API: ${total_cost:.4f}")
    print(f"- File kết quả: {out_file}")
    print(f"- Thời gian chạy thực tế: {total_time:.2f} giây")
    
    if len(df) == test_size:
        print("- Trạng thái: PASS (Sẵn sàng up lên Kaggle)")
    else:
        print("- Trạng thái: FAIL (Dừng giữa chừng do lỗi hoặc giới hạn)")
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG Benchmark Harness")
    parser.add_argument("--system", type=str, default="hybrid", choices=["vector", "hybrid", "lightrag"], 
                        help="Hệ thống RAG cần chạy (vector, hybrid, lightrag)")
    parser.add_argument("--n_test", type=int, default=None, 
                        help="Số lượng câu để test. Bỏ trống để chạy full tập data.")
    parser.add_argument("--n_docs", type=int, default=None, 
                        help="Số lượng văn bản cần index (chỉ dùng cho LightRAG). Mặc định 50.")
    args = parser.parse_args()
    
    run_benchmark(system_name=args.system, n_test=args.n_test, n_docs=args.n_docs)
