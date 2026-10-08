import json
import requests
import time
from typing import List
from .pydantic_schemas import EvaluationScore, BenchmarkQuestion, SystemResponse

API_KEY = "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={API_KEY}"

class LLMJudge:
    def __init__(self, model_name="gemini-3.5-flash-lite"):
        self.model_name = model_name

    def evaluate(self, question: BenchmarkQuestion, response: SystemResponse, retrieved_texts: List[str], system_name: str, recall: float, mrr: float) -> EvaluationScore:
        prompt = f"""Bạn là giám khảo đánh giá hệ thống RAG pháp lý.
Câu hỏi: {question.question}
Danh sách các điều luật đúng (Ground Truth): {', '.join(question.relevant_articles)}
Câu trả lời của hệ thống: {response.generation}

Tài liệu hệ thống đã tìm được:
{chr(10).join(retrieved_texts)}

Hãy đánh giá 3 tiêu chí:
1. context_precision: Các tài liệu tìm được có chứa điều luật đúng không? (0.0 đến 1.0)
2. faithfulness: Câu trả lời có dựa hoàn toàn vào tài liệu tìm được không, hay bị ảo giác? (0.0 đến 1.0)
3. citation_accuracy: Hệ thống có trích dẫn đúng điều/khoản không? (0.0 đến 1.0)

Chỉ trả về JSON object: {{"context_precision": float, "faithfulness": float, "citation_accuracy": float}}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 512}
        }
        
        start_time = time.time()
        for attempt in range(3):
            try:
                resp = requests.post(URL, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                        if text.startswith('```json'): text = text[7:]
                        if text.startswith('```'): text = text[3:]
                        if text.endswith('```'): text = text[:-3]
                        res_dict = json.loads(text.strip())
                        
                        latency = (time.time() - start_time) * 1000
                        return EvaluationScore(
                            question_id=question.question_id,
                            system_name=system_name,
                            recall_at_5=recall,
                            mrr_at_5=mrr,
                            context_precision=float(res_dict.get("context_precision", 0.0)),
                            faithfulness=float(res_dict.get("faithfulness", 0.0)),
                            citation_accuracy=float(res_dict.get("citation_accuracy", 0.0)),
                            evaluator_model=self.model_name,
                            eval_latency_ms=latency
                        )
                elif resp.status_code == 429:
                    time.sleep(10)
                    continue
            except Exception as e:
                time.sleep(5)
                
        latency = (time.time() - start_time) * 1000
        return EvaluationScore(
            question_id=question.question_id,
            system_name=system_name,
            recall_at_5=recall,
            mrr_at_5=mrr,
            evaluator_model=self.model_name + "_FAILED",
            eval_latency_ms=latency
        )
