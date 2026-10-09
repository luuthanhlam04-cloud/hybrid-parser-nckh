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

def run_benchmark(system_name="hybrid", n_test=None):
    print(f"=== STARTING BENCHMARK HARNESS FOR {system_name.upper()} ===")
    questions, corpus_dict = load_data()
    print(f"Loaded {len(questions)} questions.")
    
    # Khởi tạo hệ thống (Trên Kaggle sẽ tốn VRAM GPU ở đây)
    if system_name == "vector":
        system = VectorRAGWrapper()
    elif system_name == "hybrid":
        system = HybridRAGWrapper()
    elif system_name == "light":
        system = LightRAGWrapper()
    else:
        raise ValueError(f"System {system_name} is not supported.")
        
    # Thực hiện Indexing dữ liệu corpus trước khi benchmark
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
    
    test_size = n_test if n_test else len(questions)
    
    start_time = time.time()
    for i, q in enumerate(questions[:test_size]):
        print(f"\n[{i+1}/{test_size}] Đang xử lý câu hỏi: {q.question_id}")
        
        if str(q.question_id) in completed_ids:
            print("   -> Đã xử lý trong checkpoint (Skip).")
            continue
        
        # 1. RAG chạy (Retrieval + Generation)
        response = system.retrieve_and_answer(q, top_k=5)
        
        # 2. Tính Recall/MRR cơ sở
        retrieved_ids = [doc.article_id for doc in response.retrieved_docs]
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
    
    avg_recall = df['recall_at_5'].mean()
    avg_mrr = df['mrr_at_5'].mean()
    
    print("\n" + "="*40)
    print("BÁO CÁO NHANH (QUICK REPORT)")
    print(f"- Hệ thống: {system_name.upper()}")
    print(f"- Tổng số câu đã chạy: {len(df)}")
    print(f"- Recall@5 trung bình: {avg_recall:.4f}")
    print(f"- MRR@5 trung bình: {avg_mrr:.4f}")
    print(f"- File kết quả: {out_file}")
    print(f"- Thời gian chạy thực tế: {total_time:.2f} giây")
    print("- Trạng thái: PASS (Sẵn sàng up lên Kaggle)")
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG Benchmark Harness")
    parser.add_argument("--system", type=str, default="hybrid", choices=["vector", "hybrid", "light"], 
                        help="Hệ thống RAG cần chạy (vector, hybrid, light)")
    parser.add_argument("--n_test", type=int, default=None, 
                        help="Số lượng câu để test. Bỏ trống để chạy full tập data.")
    args = parser.parse_args()
    
    run_benchmark(system_name=args.system, n_test=args.n_test)
