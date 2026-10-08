import json
from collections import Counter
import random

def verify_benchmark():
    print("Loading datasets...")
    with open('benchmark_rewritten.json', 'r', encoding='utf-8') as f:
        bench = json.load(f)
        
    with open('corpus_final.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    corpus_ids = set([a['article_id'] for a in corpus])
    
    report = ["# VERIFY BENCHMARK REPORT\n"]
    report.append(f"Tổng số câu trong benchmark_rewritten.json: {len(bench)}\n")
    
    cats = Counter(q.get('category', 'unknown') for q in bench)
    report.append(f"Phân bố category: {dict(cats)}\n")
    
    missing_ids = set()
    for q in bench:
        for article_id in q.get('relevant_articles', []):
            if article_id not in corpus_ids:
                missing_ids.add(article_id)
                
    if missing_ids:
        report.append(f"LỖI: Có {len(missing_ids)} article_id không tồn tại trong corpus_final.json!")
        report.append(f"Danh sách missing: {list(missing_ids)[:20]}")
        with open('verify_benchmark_report.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        print("LỖI: Có article_id không tồn tại. Dừng.")
        return False
        
    report.append("Toàn bộ relevant_articles đều tồn tại trong corpus.\n")
    
    report.append("--- 5 Câu Mẫu ---")
    sample = random.sample(bench, min(5, len(bench)))
    for q in sample:
        report.append(f"QID: {q.get('question_id')}")
        report.append(f"Q: {q.get('question')}")
        report.append(f"Articles: {q.get('relevant_articles')}")
        report.append(f"Category: {q.get('category')}")
        report.append("-")
        
    with open('verify_benchmark_report.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print("Verify Passed!")
    return True

if __name__ == "__main__":
    verify_benchmark()
