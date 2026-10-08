from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time

# Import Pydantic Schema từ thư mục core
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse

class BaseRAGSystem(ABC):
    """
    Interface bắt buộc (Adapter Pattern) cho mọi hệ thống RAG tham gia vào Benchmark Harness.
    Mục đích: Đảm bảo dù bên trong hệ thống dùng công nghệ gì (BM25, Qdrant, NanoGraphRAG),
    đầu vào và đầu ra khi giao tiếp với Harness vẫn luôn tuân thủ chuẩn Pydantic.
    """
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any] = None):
        """
        Khởi tạo hệ thống (Load Embedding Model, Load Reranker, Kết nối DB...)
        """
        pass
        
    @abstractmethod
    def index_corpus(self, corpus_path: str, index_dir: str):
        """
        Hàm thực hiện Indexing toàn bộ corpus_final.json.
        """
        pass
        
    @abstractmethod
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        """
        Hàm truy xuất dữ liệu. 
        BẮT BUỘC trả về object SystemResponse chứa danh sách retrieved_docs chuẩn.
        """
        pass
