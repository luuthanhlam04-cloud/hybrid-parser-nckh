"""Strictly grounded answer generation for M10."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv


SYSTEM_PROMPT = """Bạn là trợ lý hỏi đáp pháp luật Việt Nam.
Chỉ trả lời dựa trên NGỮ CẢNH được cung cấp; không suy đoán hoặc bổ sung kiến thức ngoài ngữ cảnh.

Yêu cầu bắt buộc:
1. Trả lời trực tiếp câu hỏi và xác định đúng chủ thể, phạm vi áp dụng.
2. Nếu câu hỏi yêu cầu danh sách, phải liệt kê riêng từng điều kiện, quyền, nghĩa vụ hoặc ngoại lệ; không trả lời chung chung kiểu “theo Điều ...”.
3. Phân biệt rõ được phép, bắt buộc, bị cấm, điều kiện và ngoại lệ.
4. Mỗi kết luận phải kèm căn cứ Điều–Khoản–Điểm chính xác khi locator có trong ngữ cảnh.
5. Nếu có dẫn chiếu, nêu cả quy định nguồn và quy định đích.
6. Không dùng node ID, tên file hoặc locator UNRESOLVED làm căn cứ pháp lý.
7. Nếu ngữ cảnh thiếu, nói rõ phần nào chưa đủ; không tự điền phần thiếu.
8. Nếu nội dung cụ thể nằm ngoài Chương III, nói rõ giới hạn corpus và chỉ nêu phần Chương III thực sự cung cấp."""


class AnswerGenerator:
    def __init__(self, client: Any, model_name: str = "openai/gpt-4o-mini") -> None:
        if not model_name.strip():
            raise ValueError("model_name must not be empty.")
        self.client = client
        self.model_name = model_name

    @classmethod
    def from_environment(cls) -> "AnswerGenerator":
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required for M10 answer generation.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("M10 answer generation requires the openai package.") from exc
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return cls(client, os.getenv("M10_LLM_MODEL", "openai/gpt-4o-mini"))

    def generate(self, question: str, context: str) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"CÂU HỎI:\n{question}\n\nNGỮ CẢNH:\n{context}",
                },
            ],
            temperature=0.0,
        )
        answer = response.choices[0].message.content
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The answer model returned an empty response.")
        usage = getattr(response, "usage", None)
        if usage is not None and hasattr(usage, "model_dump"):
            usage = usage.model_dump()
        return {
            "answer": answer.strip(),
            "model": getattr(response, "model", self.model_name),
            "usage": usage,
        }
