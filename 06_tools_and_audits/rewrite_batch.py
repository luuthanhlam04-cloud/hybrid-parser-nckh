import json
import requests
import time
from pyvi import ViTokenizer
import re

API_KEY = "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"

def compute_overlap(q_text, doc_texts):
    if not doc_texts: return 0.0
    q_tokens = set(ViTokenizer.tokenize(q_text).lower().split())
    if not q_tokens: return 0.0
    doc_tokens = set()
    for d in doc_texts:
        doc_tokens.update(ViTokenizer.tokenize(d).lower().split())
    return len(q_tokens.intersection(doc_tokens)) / len(q_tokens)

def rewrite_batch(batch):
    # batch is list of (idx, q, rel_docs)
    prompt = """Bạn là một chuyên gia pháp lý. Hãy viết lại các câu hỏi sau thành câu hỏi tự nhiên của người dùng phổ thông.
QUY TẮC BẮT BUỘC:
1. KHÔNG được dùng quá 3 từ liên tiếp giống với điều luật gốc. Phải diễn đạt lại (paraphrase).
2. Giữ nguyên ý nghĩa pháp lý và ground truth.
3. Chỉ trả về một JSON array duy nhất, không có markdown (ví dụ ```json), theo định dạng:
[{"id": "câu_hỏi_id", "new_question": "câu hỏi đã viết lại"}, ...]

Danh sách câu hỏi cần viết lại:
"""
    items_json = []
    for idx, q, rel_docs in batch:
        items_json.append({
            "id": q.get('question_id', str(idx)),
            "question": q['question'],
            "law": rel_docs[0] if rel_docs else ""
        })
    prompt += json.dumps(items_json, ensure_ascii=False, indent=2)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }
    
    for attempt in range(5):
        try:
            resp = requests.post(URL, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    # Clean markdown code block if present
                    if text.startswith('```json'): text = text[7:]
                    if text.startswith('```'): text = text[3:]
                    if text.endswith('```'): text = text[:-3]
                    text = text.strip()
                    try:
                        res_list = json.loads(text)
                        return res_list
                    except json.JSONDecodeError:
                        return None
            elif resp.status_code == 429:
                time.sleep(10)
                continue
            else:
                return None
        except Exception:
            time.sleep(5)
    return None

def run():
    print("Loading datasets...")
    with open('benchmark_final.json', 'r', encoding='utf-8') as f:
        bench = json.load(f)
        
    with open('corpus_final.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    corpus_dict = {a['article_id']: a.get('text', '') for a in corpus}
    
    to_rewrite = []
    for i, q in enumerate(bench):
        q_text = q.get('question', '')
        rel_docs = [corpus_dict.get(aid, '') for aid in q.get('relevant_articles', [])]
        overlap = compute_overlap(q_text, rel_docs)
        if overlap > 0.5:
            to_rewrite.append((i, q, rel_docs))
            
    print(f"Found {len(to_rewrite)} questions with overlap > 0.5. Batch rewriting...")
    
    batch_size = 20
    batches = [to_rewrite[i:i + batch_size] for i in range(0, len(to_rewrite), batch_size)]
    
    success_count = 0
    fail_count = 0
    
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)} (Size: {len(batch)})...")
        res_list = rewrite_batch(batch)
        if res_list:
            res_dict = {str(item['id']): item['new_question'] for item in res_list if 'id' in item and 'new_question' in item}
            for idx, q, _ in batch:
                qid = q.get('question_id', str(idx))
                if qid in res_dict:
                    bench[idx]['question'] = res_dict[qid]
                    success_count += 1
                else:
                    fail_count += 1
        else:
            fail_count += len(batch)
            print("Batch failed.")
        
        # Respect 15 RPM (1 request every 4 seconds)
        time.sleep(5)
                
    print(f"Rewrite completed. Success: {success_count}, Failed: {fail_count}")
    
    with open('benchmark_rewritten.json', 'w', encoding='utf-8') as f:
        json.dump(bench, f, ensure_ascii=False, indent=2)
        
    print("Saved to benchmark_rewritten.json")
    return True

if __name__ == "__main__":
    run()
