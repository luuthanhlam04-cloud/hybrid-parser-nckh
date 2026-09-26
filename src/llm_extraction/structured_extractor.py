# -*- coding: utf-8 -*-
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import openai
import instructor

from src.llm_extraction.schema_manager import SemanticExtraction
from src.llm_extraction.prompt_builder import PromptBuilder, SYSTEM_PROMPT
from src.llm_extraction.retry_controller import safe_retry_extractor

logger = logging.getLogger(__name__)

class StructuredExtractor:
    def __init__(self, candidates_path: str, physical_graph_path: str):
        self.candidates_path = Path(candidates_path)
        self.physical_graph_path = Path(physical_graph_path)
        
        # Nạp biến môi trường từ .env
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY không được tìm thấy trong file .env")
            
        # Khởi tạo client OpenAI và trỏ Base URL tới OpenRouter
        # Dùng instructor để bọc client
        self.client = instructor.from_openai(
            openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=60.0,
            ),
            mode=instructor.Mode.JSON
        )
        self.model_name = "openai/gpt-4o-mini"
        
        self.candidates = self._load_json(self.candidates_path)
        self.physical_graph = self._load_json(self.physical_graph_path)
        
        self.prompt_builder = PromptBuilder(self.physical_graph)

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @safe_retry_extractor(max_attempts=3)
    def extract_node(self, node_id: str) -> SemanticExtraction:
        """
        Gọi LLM để trích xuất thông tin từ node.
        Tự động retry 3 lần và fail-safe fallback về SemanticExtraction rỗng nếu lỗi.
        """
        prompt = self.prompt_builder.build_prompt(node_id)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            response_model=SemanticExtraction,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        return response

    def run_extraction(
        self, limit: int = 0, node_ids: list[str] | None = None
    ) -> Dict[str, Any]:
        """
        Chạy trích xuất cho các LLM_CANDIDATE.
        limit: Số lượng node tối đa cần trích xuất (để debug). 0 = tất cả.
        """
        candidate_nodes = self.candidates.get("candidates", [])
        llm_candidates = [c for c in candidate_nodes if c.get("route") == "LLM_CANDIDATE"]
        if node_ids:
            candidates_by_id = {
                str(candidate.get("node_id")): candidate
                for candidate in llm_candidates
            }
            missing = [node_id for node_id in node_ids if node_id not in candidates_by_id]
            if missing:
                raise ValueError(
                    "Requested node IDs are not LLM_CANDIDATE entries: "
                    + ", ".join(missing)
                )
            llm_candidates = [candidates_by_id[node_id] for node_id in node_ids]

        if limit > 0:
            llm_candidates = llm_candidates[:limit]
            
        logger.info(f"Bắt đầu bóc tách cho {len(llm_candidates)} LLM_CANDIDATE(s)...")
        
        extracted_data = []
        for i, candidate in enumerate(llm_candidates):
            node_id = candidate.get("node_id")
            logger.info(f"Đang bóc tách [{i+1}/{len(llm_candidates)}]: {node_id}")
            
            try:
                result: SemanticExtraction = self.extract_node(node_id)
                
                # Chuyển Pydantic model thành dict để lưu
                result_dict = result.model_dump()
                extracted_data.append({
                    "node_id": node_id,
                    "extraction": result_dict
                })
            except Exception as e:
                logger.error(f"Lỗi không thể bóc tách node {node_id}: {e}")
                extracted_data.append({
                    "node_id": node_id,
                    "extraction": {"entities": [], "relations": []}
                })
                
            # Rate limiting sleep để tránh lỗi 429 Too Many Requests
            time.sleep(0.5)
                
        output = {
            "metadata": {
                "model": self.model_name,
                "total_candidates_processed": len(llm_candidates)
            },
            "extracted_nodes": extracted_data
        }
        
        return output

    def export(self, data: Dict[str, Any], output_path: str):
        """
        Lưu kết quả trích xuất ra file JSON.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Đã lưu kết quả trích xuất tại: {path}")
