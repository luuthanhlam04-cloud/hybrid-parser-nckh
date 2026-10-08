"""
__init__.py — src/preprocessing
================================
Xuất public API của Module 1: Document Preprocessing.

Các thành phần có thể import trực tiếp từ package:

    from src.preprocessing import DocxLoader, TextCleaner
    from src.preprocessing import UnicodeNormalizer, Formatter
    from src.preprocessing import run_pipeline, run_batch
    from src.preprocessing import get_loader, normalize_nfc, is_nfc
"""

from src.preprocessing.clean_document import PipelineResult, run_batch, run_pipeline
from src.preprocessing.document_loader import (
    BaseLoader,
    DocxLoader,
    TxtLoader,
    get_loader,
)
from src.preprocessing.formatter import Formatter
from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.unicode_normalizer import UnicodeNormalizer, is_nfc, normalize_nfc

__all__ = [
    # Loaders
    "BaseLoader",
    "DocxLoader",
    "TxtLoader",
    "get_loader",
    # Cleaner
    "TextCleaner",
    # Unicode
    "UnicodeNormalizer",
    "normalize_nfc",
    "is_nfc",
    # Formatter
    "Formatter",
    # Pipeline
    "run_pipeline",
    "run_batch",
    "PipelineResult",
]
