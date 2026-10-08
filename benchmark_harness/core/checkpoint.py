import json
import os
import tempfile
from typing import Dict, Any

class CheckpointManager:
    """
    Quản lý lưu trạng thái theo kiến trúc Per-Question Atomic Write (Option B).
    Mỗi câu hỏi được lưu thành một file .json riêng biệt.
    Không bao giờ xảy ra tình trạng Half-written corrupt.
    """
    def __init__(self, system_dir: str):
        self.system_dir = system_dir
        os.makedirs(self.system_dir, exist_ok=True)

    def get_filepath(self, question_id: str) -> str:
        return os.path.join(self.system_dir, f"{question_id}.json")

    def is_completed(self, question_id: str) -> bool:
        return os.path.exists(self.get_filepath(question_id))

    def save(self, question_id: str, data: Dict[str, Any]):
        filepath = self.get_filepath(question_id)
        
        # Atomic Write
        fd, temp_path = tempfile.mkstemp(dir=self.system_dir, text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        os.replace(temp_path, filepath)
