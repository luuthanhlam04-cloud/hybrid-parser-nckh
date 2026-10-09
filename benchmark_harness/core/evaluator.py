import json
import requests
import time
from typing import List
import os
from .pydantic_schemas import EvaluationScore, BenchmarkQuestion, SystemResponse

# Điền API Key của OpenRouter vào đây, hoặc đặt biến môi trường OPENROUTER_API_KEY
API_KEY = os.environ.get("OPENROUTER_API_KEY", "ĐIỀN_API_KEY_OPENROUTER_CỦA_BẠN_VÀO_ĐÂY")

class LLMJudge:
    def __init__(self, model_name="openai/gpt-4o-mini"):
        self.model_name = model_name
        self.url = "https://openrouter.ai/api/v1/chat/completions"

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

Chỉ trả về định dạng JSON object, không kèm văn bản nào khác: {{"context_precision": float, "faithfulness": float, "citation_accuracy": float}}
"""
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 512,
            "response_format": { "type": "json_object" }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        start_time = time.time()
        for attempt in range(3):
            try:
                resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        text = data['choices'][0]['message']['content'].strip()
                        res_dict = json.loads(text)
                        
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
                    print("[LLMJudge] Bị rate limit, đang đợi 10s...")
                    time.sleep(10)
                    continue
                else:
                    print(f"[LLMJudge] Lỗi API: {resp.status_code} - {resp.text}")
                    time.sleep(5)
            except Exception as e:
                print(f"[LLMJudge] Lỗi kết nối: {e}")
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
