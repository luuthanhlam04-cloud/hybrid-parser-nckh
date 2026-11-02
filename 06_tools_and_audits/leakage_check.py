import json
from collections import Counter
from pyvi import ViTokenizer
import re

def compute_overlap(q_text, doc_texts):
    if not doc_texts:
        return 0.0
    
    # Clean and tokenize
    q_tokens = set(ViTokenizer.tokenize(q_text).lower().split())
    if not q_tokens:
        return 0.0
        
    doc_tokens = set()
    for d in doc_texts:
        doc_tokens.update(ViTokenizer.tokenize(d).lower().split())
        
    overlap = len(q_tokens.intersection(doc_tokens)) / len(q_tokens)
    return overlap

def run_leakage_check():
    with open('benchmark_rewritten.json', 'r', encoding='utf-8') as f:
        bench = json.load(f)
        
    with open('corpus_final.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    corpus_dict = {a['article_id']: a.get('text', '') for a in corpus}
    
    results = []
    total_overlap = 0.0
    
    print("Computing overlap...")
    for q in bench:
        q_text = q.get('question', '')
        rel_docs = [corpus_dict.get(aid, '') for aid in q.get('relevant_articles', [])]
        overlap = compute_overlap(q_text, rel_docs)
        total_overlap += overlap
        results.append({
            'question_id': q.get('question_id', ''),
            'question': q_text,
            'overlap': overlap,
            'article_text': " | ".join(d[:100] + '...' for d in rel_docs)
        })
        
    avg_overlap = total_overlap / len(bench) if bench else 0
    results.sort(key=lambda x: x['overlap'], reverse=True)
    
    report = ["# LEAKAGE CHECK REPORT\n"]
    
    # 2. Categories
    cats = Counter(q.get('category', 'unknown') for q in bench)
    report.append("## Phân bố Category")
    for k, v in cats.items():
        report.append(f"- {k}: {v}")
    report.append("")
        
    # 3. Sources
    # Assume source is 'source' field, or deduce from ID
    def get_source(q):
        src = q.get('source')
        if src: return src
        qid = q.get('question_id', '')
        if 'vilegal' in qid.lower(): return 'ViLegalExpert'
        return 'VMTEB'
        
    sources = Counter(get_source(q) for q in bench)
    report.append("## Phân bố Nguồn")
    for k, v in sources.items():
        report.append(f"- {k}: {v}")
    report.append("")
        
    # Top 10 overlap
    report.append(f"## Data Leakage Overlap (Trung bình: {avg_overlap:.4f})\n")
    if avg_overlap > 0.6:
        report.append("CẢNH BÁO LEAKAGE: Tỷ lệ trùng lặp trung bình > 0.6!\n")
    else:
        report.append("BÌNH THƯỜNG: Tỷ lệ trùng lặp ở mức an toàn.\n")
        
    report.append("--- Top 10 câu trùng lặp cao nhất ---")
    for i, r in enumerate(results[:10]):
        report.append(f"{i+1}. QID: {r['question_id']} (Overlap: {r['overlap']:.4f})")
        report.append(f"Q: {r['question']}")
        report.append(f"A: {r['article_text']}")
        report.append("-")
        
    report_text = "\n".join(report)
    with open('leakage_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
        
    print(report_text)

if __name__ == "__main__":
    run_leakage_check()
