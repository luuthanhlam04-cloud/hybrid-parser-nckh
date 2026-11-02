import json
from collections import Counter

def run_strict_audit():
    print("=== BẮT ĐẦU KIỂM TOÁN KHẮT KHE (STRICT AUDIT) ===")
    
    # 1. Load data
    try:
        with open("benchmark_harness/data/corpus_final.json", "r", encoding="utf-8") as f:
            corpus = json.load(f)
        with open("benchmark_harness/data/benchmark_rewritten.json", "r", encoding="utf-8") as f:
            benchmark = json.load(f)
    except Exception as e:
        print(f"Lỗi load data: {e}")
        return

    # 2. Check Corpus
    corpus_ids = [item.get("article_id") for item in corpus]
    
    # Check null/empty IDs
    missing_ids = [i for i, aid in enumerate(corpus_ids) if not aid]
    if missing_ids:
        print(f"[CẢNH BÁO] Có {len(missing_ids)} điều luật bị thiếu article_id tại index: {missing_ids[:5]}")
        
    # Check duplicates
    id_counts = Counter(corpus_ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1 and k}
    if duplicates:
        print(f"[CẢNH BÁO] Cực kỳ nghiêm trọng: Phát hiện {len(duplicates)} article_id BỊ TRÙNG LẶP trong Corpus!")
        for k, v in list(duplicates.items())[:5]:
            print(f"  - {k} xuất hiện {v} lần")
    else:
        print("[OK] Không có article_id trùng lặp trong Corpus.")

    # Check malformed IDs (dấu phẩy)
    malformed = [aid for aid in corpus_ids if aid and ("," in aid or " " in aid)]
    if malformed:
        print(f"[CẢNH BÁO] Phát hiện {len(malformed)} article_id chứa dấu phẩy hoặc khoảng trắng (có thể gây lỗi string matching):")
        for m in malformed[:5]:
            print(f"  - {m}")
    else:
        print("[OK] Định dạng article_id chuẩn (không chứa dấu phẩy/khoảng trắng).")

    # 3. Check Benchmark mapping
    corpus_id_set = set(corpus_ids)
    missing_in_corpus = set()
    total_relevant = 0
    
    for q in benchmark:
        for aid in q.get("relevant_articles", []):
            total_relevant += 1
            if aid not in corpus_id_set:
                missing_in_corpus.add(aid)
                
    if missing_in_corpus:
        print(f"[CẢNH BÁO] TRẦM TRỌNG: Phát hiện {len(missing_in_corpus)} article_id nằm trong Benchmark (Ground Truth) nhưng KHÔNG TỒN TẠI trong Corpus!")
        for m in list(missing_in_corpus)[:10]:
            print(f"  - Thiếu: {m}")
        print("=> Hậu quả: Recall sẽ không bao giờ đạt 100% vì hệ thống RAG không thể tìm ra bài viết không tồn tại.")
    else:
        print(f"[OK] Toàn bộ {total_relevant} ground truth id trong Benchmark đều tồn tại hợp lệ trong Corpus. Mapping hoàn hảo.")
        
    print("\n=== KẾT THÚC KIỂM TOÁN ===")

if __name__ == "__main__":
    run_strict_audit()
