# -*- coding: utf-8 -*-
"""
run_judge_c1_bm25.py — Thẩm định Citation, Context Precision và Faithfulness
của Cấu hình C1 (Naive BM25 - Điều thô) bằng LLM-as-a-Judge (gpt-4o-mini qua OpenRouter).
Đồng bộ 100% với phương pháp luận và cấu trúc của C4 (Parser BM25), C5 (Parser Dense) và C6 (Parser Hybrid).
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import time
import requests
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BENCHMARK_ROOT = r"c:\Users\luuth\NCKH\Benchmark"
CORPUS_PATH = os.path.join(BENCHMARK_ROOT, "corpus_final.json")
QUERIES_PATH = os.path.join(BENCHMARK_ROOT, "benchmark_rewritten.json")
RESULTS_C1_PATH = os.path.join(BENCHMARK_ROOT, "02_baselines", "baseline_bm25_rewritten_results.csv")
OUTPUT_DIR = os.path.join(BENCHMARK_ROOT, "08_empirical_results")

def call_llm_judge(question: str, gt_articles: list, retrieved_chunks_text: str, api_key: str, max_retries: int = 3) -> Tuple[dict, dict, str]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    gt_str = ", ".join(gt_articles) if gt_articles else "Không có điều luật quy định"
    prompt = f"""Bạn là chuyên gia thẩm định RAG pháp lý.
Câu hỏi: {question}
Danh sách các điều luật đúng (Ground Truth): {gt_str}
Các đoạn trích do hệ thống truy xuất (văn bản cấp Điều thô):
{retrieved_chunks_text}

Hãy đánh giá xem:
1. context_precision (0.0 đến 1.0): Các đoạn trích có chứa điều luật giải quyết câu hỏi không?
2. citation_accuracy (0.0 đến 1.0): Tiền tố phân cấp hoặc nội dung trích dẫn có định vị chính xác số điều/khoản/điểm của căn cứ pháp lý không? (Nếu văn bản chỉ là điều luật thô không chỉ rõ khoản/điểm cụ thể cho câu hỏi, điểm tối đa là 0.5; nếu trúng chính xác điều khoản điểm đạt 1.0, không liên quan đạt 0.0).
3. faithfulness (0.0 đến 1.0): Thông tin trong đoạn trích có trung thực với nội dung câu hỏi và luật không?

Chỉ trả về JSON object:
{{
    "context_precision": float,
    "citation_accuracy": float,
    "faithfulness": float,
    "reason": "Nhận xét ngắn gọn 1 câu"
}}"""
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=40)
            if resp.status_code == 429:
                time.sleep(2.0 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            gen_id = data.get("id", "")
            res_dict = json.loads(data["choices"][0]["message"]["content"])
            usage = data.get("usage", {})
            return res_dict, usage, gen_id
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
            
    raise last_err or RuntimeError("Failed after max retries")

def main():
    print("=" * 80)
    print("🚀 BẮT ĐẦU THẨM ĐỊNH LLM-AS-A-JUDGE CHO CẤU HÌNH C1 (NAIVE BM25)")
    print("=" * 80)

    # 1. Load corpus
    print(f"[*] Đang nạp corpus từ {CORPUS_PATH}...")
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    corpus_map = {item["article_id"]: item.get("text", "") for item in corpus}
    print(f"    -> Đã nạp {len(corpus_map):,} điều luật.")

    # 2. Load questions
    print(f"[*] Đang nạp danh sách câu hỏi từ {QUERIES_PATH}...")
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"    -> Đã nạp {len(questions)} câu hỏi benchmark.")

    # 3. Load C1 retrieval results
    print(f"[*] Đang nạp kết quả truy xuất C1 từ {RESULTS_C1_PATH}...")
    df_c1 = pd.read_csv(RESULTS_C1_PATH)
    print(f"    -> Đã nạp kết quả truy xuất cho {len(df_c1)} câu hỏi.")

    # 4. Multi-threaded Judge execution
    workers = 16
    total_q = len(questions)
    judge_logs = [None] * total_q
    lock = threading.Lock()
    completed_count = 0
    total_tokens = 0
    total_cost = 0.0
    nl = "\n"

    print(f"\n[*] Đang chạy LLM Judge trên {total_q} câu hỏi (Đa luồng: {workers} workers)...")
    t0 = time.perf_counter()

    def process_one(idx, q):
        qid = q["question_id"]
        gt = q.get("relevant_articles", [])
        row = df_c1[df_c1["question_id"] == qid]
        matched_texts = []
        if len(row) > 0:
            ret_arts_str = str(row.iloc[0].get("retrieved_articles", ""))
            if ret_arts_str and ret_arts_str != "nan":
                ret_arts = ret_arts_str.split("|")[:3]  # top 3 articles
                for aid in ret_arts:
                    if aid in corpus_map:
                        t = corpus_map[aid][:800] # truncate per article to avoid token overflow
                        matched_texts.append(f"[{aid}]: {t}")

        context_str = nl.join(matched_texts) if matched_texts else "Không truy xuất được văn bản nào."

        try:
            scores, usage, gen_id = call_llm_judge(q["question"], gt, context_str, API_KEY)
            p_tok = usage.get("prompt_tokens", 0)
            c_tok = usage.get("completion_tokens", 0)
            cost = usage.get("cost", 0.0) or (p_tok / 1e6 * 0.150) + (c_tok / 1e6 * 0.600)

            res_entry = {
                "question_id": qid,
                "generation_id": gen_id,
                "citation_accuracy": float(scores.get("citation_accuracy", 0.0)),
                "context_precision": float(scores.get("context_precision", 0.0)),
                "faithfulness": float(scores.get("faithfulness", 0.0)),
                "reason": scores.get("reason", ""),
                "prompt_tokens": p_tok,
                "completion_tokens": c_tok,
                "cost_usd": cost
            }
            return idx, res_entry
        except Exception as e:
            res_entry = {
                "question_id": qid,
                "generation_id": "",
                "citation_accuracy": 0.0,
                "context_precision": 0.0,
                "faithfulness": 0.0,
                "reason": f"Lỗi gọi API: {str(e)}",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost_usd": 0.0
            }
            return idx, res_entry

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_one, i, q): i for i, q in enumerate(questions)}
        for fut in as_completed(futures):
            idx, res = fut.result()
            judge_logs[idx] = res
            with lock:
                completed_count += 1
                total_tokens += (res["prompt_tokens"] + res["completion_tokens"])
                total_cost += res["cost_usd"]
                if completed_count % 50 == 0 or completed_count == total_q:
                    elapsed = time.perf_counter() - t0
                    print(f"    -> Đã hoàn thành {completed_count}/{total_q} câu ({completed_count/total_q*100:.1f}%) | "
                          f"Thời gian: {elapsed:.1f}s | Token: {total_tokens:,} | Chi phí: ${total_cost:.4f}")

    total_time = time.perf_counter() - t0

    # 5. Calculate metrics
    cites = [j["citation_accuracy"] for j in judge_logs if j]
    precs = [j["context_precision"] for j in judge_logs if j]
    faiths = [j["faithfulness"] for j in judge_logs if j]

    mean_cite = round(float(sum(cites) / len(cites)), 4)
    mean_prec = round(float(sum(precs) / len(precs)), 4)
    mean_faith = round(float(sum(faiths) / len(faiths)), 4)
    perfect_count = sum(1 for c in cites if c >= 0.99)
    perfect_pct = round(perfect_count / len(cites) * 100, 1)

    print("\n" + "=" * 80)
    print("🏆 KẾT QUẢ THẨM ĐỊNH CHÍNH THỨC CHO CẤU HÌNH C1 (NAIVE BM25):")
    print(f"   - Kích thước mẫu: {len(judge_logs)} câu hỏi")
    print(f"   - Mean Citation Accuracy:  {mean_cite * 100:.2f}% ({mean_cite})")
    print(f"   - Mean Context Precision:   {mean_prec * 100:.2f}% ({mean_prec})")
    print(f"   - Mean Faithfulness:        {mean_faith * 100:.2f}% ({mean_faith})")
    print(f"   - Tỷ lệ câu đạt 1.0 điểm:   {perfect_count}/{len(cites)} ({perfect_pct}%)")
    print(f"   - Tổng chi phí thực tế:     ${total_cost:.4f} USD")
    print(f"   - Tổng thời gian:           {total_time:.1f} giây")
    print("=" * 80)

    # 6. Save output files
    out_json = os.path.join(OUTPUT_DIR, "parser_citation_llm_judge_c1_naive_bm25_512.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "system_name": "C1_NAIVE_BM25",
            "sample_size": len(judge_logs),
            "mean_citation_accuracy": mean_cite,
            "mean_context_precision": mean_prec,
            "mean_faithfulness": mean_faith,
            "perfect_score_count": perfect_count,
            "perfect_score_percentage": perfect_pct,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "total_latency_seconds": round(total_time, 2),
            "details": judge_logs
        }, f, indent=2, ensure_ascii=False)
    print(f"[+] Đã lưu toàn bộ nhật ký chi tiết vào: {out_json}")

if __name__ == "__main__":
    main()

