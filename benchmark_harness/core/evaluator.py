import json
import requests
import time
from typing import List, Dict, Optional, Any
import os
from .pydantic_schemas import EvaluationScore, BenchmarkQuestion, SystemResponse

# Điền API Key của OpenRouter vào đây, hoặc đặt biến môi trường OPENROUTER_API_KEY
API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")

class LLMJudge:
    def __init__(self, model_name="openai/gpt-4o-mini"):
        self.model_name = model_name
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def evaluate(self, question: BenchmarkQuestion, response: SystemResponse, retrieved_texts: List[str], system_name: str, recall: Optional[float], mrr: Optional[float], strict_match: bool = None) -> EvaluationScore:
        base_prompt = f"""Bạn là giám khảo đánh giá hệ thống RAG pháp lý.
Câu hỏi: {question.question}
Danh sách các điều luật đúng (Ground Truth): {', '.join(question.relevant_articles)}
Câu trả lời của hệ thống: {response.generation}

Tài liệu hệ thống đã tìm được:
{chr(10).join(retrieved_texts)}

Hãy đánh giá hệ thống. BẮT BUỘC phải đưa ra lý luận (reasoning) trước khi chốt điểm để đảm bảo tính khách quan.
"""
        
        if question.category == "negative":
            base_prompt += """
ĐÂY LÀ CÂU HỎI NEGATIVE (Luật không quy định hoặc cấm).
Bạn cần đánh giá:
1. refusal_correct: Hệ thống có từ chối trả lời không? (true/false)
2. refusal_appropriate: Sự từ chối đó có chính xác vì lý do "luật không quy định/không có thông tin" không? (true/false). KHÔNG cho điểm tự động nếu hệ thống cố tình trả lời bừa.
3. context_precision: Tài liệu tìm được có bối cảnh liên quan không? (0.0 đến 1.0)
4. faithfulness: 1.0 nếu trả lời đúng bản chất từ chối dựa vào tài liệu, 0.0 nếu ảo giác/bịa đặt.
5. citation_accuracy: 1.0 nếu không bịa ra trích dẫn sai.

Chỉ trả về JSON object:
{
    "reasoning_refusal": "lý do...",
    "refusal_correct": bool,
    "refusal_appropriate": bool,
    "reasoning_context": "lý do...",
    "context_precision": float,
    "reasoning_faithfulness": "lý do...",
    "faithfulness": float,
    "reasoning_citation": "lý do...",
    "citation_accuracy": float
}
"""
        else:
            base_prompt += """
Hãy đánh giá 3 tiêu chí:
1. context_precision: Các tài liệu tìm được có chứa điều luật giải quyết câu hỏi không? (0.0 đến 1.0)
2. faithfulness: Câu trả lời có dựa hoàn toàn vào tài liệu tìm được không, hay bị ảo giác? (0.0 đến 1.0)
3. citation_accuracy: Hệ thống có trích dẫn đúng số điều/khoản không? (0.0 đến 1.0)

Chỉ trả về JSON object:
{
    "reasoning_context": "lý do...",
    "context_precision": float,
    "reasoning_faithfulness": "lý do...",
    "faithfulness": float,
    "reasoning_citation": "lý do...",
    "citation_accuracy": float
}
"""
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": base_prompt}],
            "temperature": 0.0,
            "max_tokens": 1000,
            "response_format": { "type": "json_object" }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        start_time = time.time()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        text = data['choices'][0]['message']['content'].strip()
                        res_dict = json.loads(text)
                        
                        usage = data.get("usage", {})
                        p_tokens = usage.get("prompt_tokens", 0)
                        c_tokens = usage.get("completion_tokens", 0)
                        t_tokens = usage.get("total_tokens", 0)
                        # Giá gpt-4o-mini openrouter: $0.15/1M input, $0.60/1M output
                        est_cost = (p_tokens / 1000000 * 0.150) + (c_tokens / 1000000 * 0.600)
                        
                        latency = (time.time() - start_time) * 1000
                        return EvaluationScore(
                            question_id=question.question_id,
                            system_name=system_name,
                            recall_at_5=recall,
                            mrr_at_5=mrr,
                            strict_match=strict_match,
                            refusal_correct=res_dict.get("refusal_correct"),
                            refusal_appropriate=res_dict.get("refusal_appropriate"),
                            context_precision=float(res_dict.get("context_precision", 0.0)),
                            faithfulness=float(res_dict.get("faithfulness", 0.0)),
                            citation_accuracy=float(res_dict.get("citation_accuracy", 0.0)),
                            evaluator_model=self.model_name,
                            eval_latency_ms=latency,
                            prompt_tokens=p_tokens,
                            completion_tokens=c_tokens,
                            total_tokens=t_tokens,
                            estimated_cost=est_cost
                        )
                elif resp.status_code == 429:
                    wait_time = 2 ** attempt * 5 # 5s, 10s, 20s
                    print(f"[LLMJudge] Rate limit, đợi {wait_time}s (Lần {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    wait_time = 2 ** attempt * 2
                    print(f"[LLMJudge] Lỗi API: {resp.status_code}. Đợi {wait_time}s...")
                    time.sleep(wait_time)
            except Exception as e:
                wait_time = 2 ** attempt * 2
                print(f"[LLMJudge] Lỗi kết nối: {e}. Đợi {wait_time}s...")
                time.sleep(wait_time)
                
        # Nếu fail hết 3 lần
        print(f"[LLMJudge] FAILED hoàn toàn cho câu {question.question_id}.")
        latency = (time.time() - start_time) * 1000
        return EvaluationScore(
            question_id=question.question_id,
            system_name=system_name,
            recall_at_5=recall,
            mrr_at_5=mrr,
            strict_match=strict_match,
            evaluator_model=self.model_name + "_FAILED",
            eval_latency_ms=latency
        )
