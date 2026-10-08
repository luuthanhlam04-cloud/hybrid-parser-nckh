import json
import csv
from collections import defaultdict
from rank_bm25 import BM25Okapi
from pyvi import ViTokenizer

def run_baseline():
    print("Loading corpus...")
    with open('corpus_final.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    print("Tokenizing corpus...")
    corpus_ids = [a['article_id'] for a in corpus]
    tokenized_corpus = []
    for a in corpus:
        text = a.get('text', '')
        # Simple tokenization
        tokens = ViTokenizer.tokenize(text).lower().split()
        tokenized_corpus.append(tokens)
        
    bm25 = BM25Okapi(tokenized_corpus)
    
    with open('benchmark_rewritten.json', 'r', encoding='utf-8') as f:
        bench = json.load(f)
        
    results = []
    total_recall = 0
    total_mrr = 0
    cat_metrics = defaultdict(lambda: {'recall': 0, 'mrr': 0, 'count': 0})
    
    print(f"Running BM25 for {len(bench)} queries...")
    for q in bench:
        q_id = q.get('question_id')
        question = q.get('question', '')
        category = q.get('category', 'unknown')
        ground_truth = q.get('relevant_articles', [])
        
        tokenized_query = ViTokenizer.tokenize(question).lower().split()
        # Get scores
        doc_scores = bm25.get_scores(tokenized_query)
        
        # Get top 5
        top_5_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:5]
        top_5_ids = [corpus_ids[i] for i in top_5_indices]
        
        # Calculate Recall@5
        intersection = set(ground_truth).intersection(set(top_5_ids))
        recall = len(intersection) / len(ground_truth) if len(ground_truth) > 0 else 0
        
        # Calculate MRR@5
        mrr = 0
        for i, doc_id in enumerate(top_5_ids):
            if doc_id in ground_truth:
                mrr = 1.0 / (i + 1)
                break
                
        results.append({
            'question_id': q_id,
            'question': question,
            'retrieved_articles': "|".join(top_5_ids),
            'ground_truth': "|".join(ground_truth),
            'recall@5': recall,
            'mrr@5': mrr,
            'category': category
        })
        
        total_recall += recall
        total_mrr += mrr
        cat_metrics[category]['recall'] += recall
        cat_metrics[category]['mrr'] += mrr
        cat_metrics[category]['count'] += 1
        
    # Output to CSV
    with open('baseline_bm25_rewritten_results.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['question_id', 'question', 'retrieved_articles', 'ground_truth', 'recall@5', 'mrr@5', 'category'])
        writer.writeheader()
        writer.writerows(results)
        
    # Output report
    avg_recall = total_recall / len(bench)
    avg_mrr = total_mrr / len(bench)
    
    cat_str = ", ".join([f"{k}: R={v['recall']/v['count']:.3f}/M={v['mrr']/v['count']:.3f}" for k, v in cat_metrics.items()])
    
    print(f"- Tổng số câu đã chạy: {len(bench)}")
    print(f"- Recall@5 trung bình: {avg_recall:.4f}")
    print(f"- MRR@5 trung bình: {avg_mrr:.4f}")
    print(f"- Phân bố category: {cat_str}")
    print("- Trạng thái: PASS")

if __name__ == "__main__":
    run_baseline()
