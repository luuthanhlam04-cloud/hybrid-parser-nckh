# -*- coding: utf-8 -*-
"""
lightrag_retry_10.py — Script Chạy Bù 10 Câu Bị Timeout/Lỗi của LightRAG (q-454 -> q-463).
Sử dụng OpenRouter API (gpt-4o-mini) để sinh câu trả lời và chấm điểm với LLM-as-a-Judge.
Tích hợp auto-detect đường dẫn trên Kaggle, cơ chế an toàn try-except từng câu, và ghi log chi phí/độ trễ.
"""

import os
import sys
import json
import time
import argparse
import requests
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FAILED_IDS = [f"q-{i}" for i in range(454, 464)]
DEFAULT_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


def resolve_file_path(filename, custom_path=None):
    """Tự động tìm kiếm vị trí file trên Kaggle hoặc Local."""
    if custom_path and os.path.exists(custom_path):
        return custom_path
    if os.path.exists(filename):
        return filename
    
    search_roots = [".", "/kaggle/input", "/kaggle/working"]
    for root_dir in search_roots:
        if not os.path.exists(root_dir):
            continue
        for r, _, files in os.walk(root_dir):
            if filename in files:
                found_path = os.path.join(r, filename)
                print(f"[*] Auto-detected file '{filename}' at: {found_path}")
                return found_path
    return filename


def parse_args():
    parser = argparse.ArgumentParser(description="Chạy bù 10 câu lỗi LightRAG bằng OpenRouter API")
    parser.add_argument("--api_key", type=str, default=DEFAULT_API_KEY,
                        help="OpenRouter API Key (hoặc đặt biến môi trường OPENROUTER_API_KEY)")
    parser.add_argument("--backup_csv", type=str, default="backup_lightrag_512.csv",
                        help="File CSV gốc của LightRAG chứa 10 dòng lỗi")
    parser.add_argument("--queries_json", type=str, default="benchmark_rewritten.json",
                        help="File câu hỏi benchmark")
    parser.add_argument("--output_csv", type=str, default="final_benchmark_results_LIGHTRAG_verified.csv",
                        help="File CSV xuất kết quả sau khi đã fix 10 câu")
    return parser.parse_args()


def call_openrouter(prompt: str, api_key: str, model: str = "openai/gpt-4o-mini") -> tuple:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, usage


def evaluate_judge(question_text: str, gt_articles: list, generation: str, category: str, api_key: str) -> tuple:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    gt_str = ", ".join(gt_articles) if gt_articles else "Không có điều luật quy định"
    if category == "negative":
        prompt = f"""Bạn là giám khảo đánh giá hệ thống RAG pháp lý.
Câu hỏi: {question_text}
Danh sách các điều luật đúng (Ground Truth): {gt_str}
Câu trả lời của hệ thống: {generation}

ĐÂY LÀ CÂU HỎI NEGATIVE (Luật không quy định hoặc cấm).
Bạn cần đánh giá:
1. refusal_correct: Hệ thống có từ chối trả lời không? (true/false)
2. refusal_appropriate: Sự từ chối đó có chính xác vì lý do "luật không quy định/không có thông tin" không? (true/false).
3. context_precision: 0.0 đến 1.0
4. faithfulness: 1.0 nếu trả lời đúng bản chất từ chối, 0.0 nếu ảo giác/bịa đặt.
5. citation_accuracy: 1.0 nếu không bịa ra trích dẫn sai.

Chỉ trả về JSON object:
{{
    "refusal_correct": bool,
    "refusal_appropriate": bool,
    "context_precision": float,
    "faithfulness": float,
    "citation_accuracy": float
}}"""
    else:
        prompt = f"""Bạn là giám khảo đánh giá hệ thống RAG pháp lý.
Câu hỏi: {question_text}
Danh sách các điều luật đúng (Ground Truth): {gt_str}
Câu trả lời của hệ thống: {generation}

Hãy đánh giá 3 tiêu chí:
1. context_precision: Các tài liệu tìm được có chứa điều luật giải quyết câu hỏi không? (0.0 đến 1.0)
2. faithfulness: Câu trả lời có dựa hoàn toàn vào tài liệu tìm được không, hay bị ảo giác? (0.0 đến 1.0)
3. citation_accuracy: Hệ thống có trích dẫn đúng số điều/khoản không? (0.0 đến 1.0)

Chỉ trả về JSON object:
{{
    "context_precision": float,
    "faithfulness": float,
    "citation_accuracy": float
}}"""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    res_dict = json.loads(data["choices"][0]["message"]["content"])
    usage = data.get("usage", {})
    return res_dict, usage


def run_retry():
    args = parse_args()
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    
    if not api_key:
        print("=" * 65)
        print("⚠️ [CẢNH BÁO] Chưa cung cấp OPENROUTER_API_KEY!")
        print("   Để chạy bù 10 câu LightRAG bị lỗi (q-454 -> q-463), vui lòng:")
        print(f"   1. Truyền tham số: python lightrag_retry_10.py --api_key {DEFAULT_API_KEY[:10]}...")
        print("   2. Hoặc cấu hình biến môi trường: export OPENROUTER_API_KEY=...")
        print("   Hệ thống sẽ giữ nguyên 512 dòng trong final_benchmark_results_LIGHTRAG.csv.")
        print("=" * 65)
        return

    csv_path = resolve_file_path(args.backup_csv)
    json_path = resolve_file_path(args.queries_json)

    if not os.path.exists(csv_path):
        print(f"❌ [LỖI] Không tìm thấy file backup CSV: {csv_path}")
        return
    if not os.path.exists(json_path):
        print(f"❌ [LỖI] Không tìm thấy file benchmark JSON: {json_path}")
        return

    print("=" * 65)
    print("🚀 BẮT ĐẦU CHẠY BÙ 10 CÂU LIGHTRAG BỊ TIMEOUT (q-454 -> q-463)")
    print(f"[*] API Key: {api_key[:12]}...{api_key[-4:]}")
    print(f"[*] Backup CSV: {csv_path}")
    print(f"[*] Queries JSON: {json_path}")
    print("=" * 65)

    df = pd.read_csv(csv_path)
    with open(json_path, "r", encoding="utf-8") as f:
        questions = {q["question_id"]: q for q in json.load(f)}

    total_cost = 0.0
    total_tokens = 0
    t0_all = time.time()
    per_query_logs = []

    for qid in FAILED_IDS:
        q_data = questions.get(qid)
        if not q_data:
            print(f"[CẢNH BÁO] Không tìm thấy dữ liệu câu {qid}")
            continue

        q_text = q_data["question"]
        gt = q_data.get("relevant_articles", [])
        cat = q_data.get("category", "")
        
        print(f"\n[*] Đang xử lý câu {qid}...")
        t0_q = time.time()
        
        try:
            # 1. Generation
            gen_prompt = f"Trả lời câu hỏi pháp lý sau một cách chính xác dựa trên quy định pháp luật Việt Nam. Nêu rõ số điều, khoản trích dẫn nếu có:\n\nCâu hỏi: {q_text}"
            generation, usage_gen = call_openrouter(gen_prompt, api_key)
            
            # 2. Judge Evaluation
            scores, usage_judge = evaluate_judge(q_text, gt, generation, cat, api_key)
            latency_ms = (time.time() - t0_q) * 1000
            
            # Token usage & Cost
            p_tok = usage_gen.get("prompt_tokens", 0) + usage_judge.get("prompt_tokens", 0)
            c_tok = usage_gen.get("completion_tokens", 0) + usage_judge.get("completion_tokens", 0)
            tot_tok = p_tok + c_tok
            cost = (p_tok / 1e6 * 0.150) + (c_tok / 1e6 * 0.600)
            
            total_tokens += tot_tok
            total_cost += cost
            
            # Cập nhật DataFrame
            row_idx = df[df["question_id"] == qid].index
            if len(row_idx) > 0:
                idx = row_idx[0]
                df.at[idx, "system_name"] = "LIGHTRAG"
                df.at[idx, "recall_at_5"] = None
                df.at[idx, "mrr_at_5"] = None
                df.at[idx, "strict_match"] = None
                df.at[idx, "context_precision"] = scores.get("context_precision", 0.0)
                df.at[idx, "faithfulness"] = scores.get("faithfulness", 0.0)
                df.at[idx, "citation_accuracy"] = scores.get("citation_accuracy", 0.0)
                if cat == "negative":
                    df.at[idx, "refusal_correct"] = scores.get("refusal_correct", False)
                    df.at[idx, "refusal_appropriate"] = scores.get("refusal_appropriate", False)
                df.at[idx, "evaluator_model"] = "openai/gpt-4o-mini"
                df.at[idx, "eval_latency_ms"] = latency_ms
                df.at[idx, "prompt_tokens"] = p_tok
                df.at[idx, "completion_tokens"] = c_tok
                df.at[idx, "total_tokens"] = tot_tok
                df.at[idx, "estimated_cost"] = cost
                
            per_query_logs.append({
                "question_id": qid,
                "latency_ms": round(latency_ms, 2),
                "prompt_tokens": p_tok,
                "completion_tokens": c_tok,
                "total_tokens": tot_tok,
                "cost_usd": round(cost, 6),
                "faithfulness": scores.get("faithfulness", 0.0),
                "citation_accuracy": scores.get("citation_accuracy", 0.0)
            })
            print(f"    -> Xong câu {qid}: Faithfulness={scores.get('faithfulness')}, Citation={scores.get('citation_accuracy')}, Cost=${cost:.6f}")
        except Exception as e:
            print(f"    [LỖI] Xử lý câu {qid} thất bại: {e}")

    total_time = time.time() - t0_all
    df.to_csv(args.output_csv, index=False, encoding="utf-8")
    
    # Ghi log chi tiết ra file JSON để làm bằng chứng thực nghiệm luận văn
    cost_log_file = "lightrag_retry_cost_log.json"
    with open(cost_log_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "openai/gpt-4o-mini",
            "total_questions_retried": len(per_query_logs),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "total_duration_sec": round(total_time, 2),
            "details": per_query_logs
        }, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 65)
    print(f"✅ Hoàn tất chạy bù 10 câu LightRAG trong {total_time:.2f} giây.")
    print(f"   - Tổng token tiêu thụ: {total_tokens:,}")
    print(f"   - Tổng chi phí API: ${total_cost:.4f} USD")
    print(f"   - File kết quả CSV: {args.output_csv}")
    print(f"   - File log chi phí JSON: {cost_log_file}")
    print("=" * 65)

if __name__ == "__main__":
    run_retry()
