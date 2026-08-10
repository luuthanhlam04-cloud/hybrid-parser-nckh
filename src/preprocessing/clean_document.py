"""
clean_document.py
=================
Pipeline điều phối chính của Module 1: Document Preprocessing.

Luồng xử lý:
    .docx  →  [DocxLoader]  →  [TextCleaner]  →  [UnicodeNormalizer]
           →  [Formatter]   →  clean_law_document.txt

Sử dụng:
    # Chạy trực tiếp
    python src/preprocessing/clean_document.py

    # Import trong code khác
    from src.preprocessing.clean_document import run_pipeline
    result = run_pipeline("datasets/raw_laws/Luat_dat_dai_chuong_3.docx")
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Đường dẫn gốc của project (2 cấp trên thư mục src/preprocessing/)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Thêm project root vào sys.path để import tuyệt đối hoạt động
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.preprocessing.document_loader import get_loader
from src.preprocessing.formatter import Formatter
from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.unicode_normalizer import UnicodeNormalizer

# ---------------------------------------------------------------------------
# Cấu hình logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataclass kết quả pipeline
# ---------------------------------------------------------------------------
@dataclass
class PipelineResult:
    """Kết quả trả về sau khi chạy pipeline."""

    input_path: Path
    output_path: Path
    success: bool
    elapsed_seconds: float
    input_lines: int = 0
    output_chars: int = 0
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "✅ THÀNH CÔNG" if self.success else "❌ THẤT BẠI"
        lines = [
            "=" * 60,
            f"  KẾT QUẢ PIPELINE — {status}",
            "=" * 60,
            f"  File đầu vào : {self.input_path}",
            f"  File đầu ra  : {self.output_path}",
            f"  Dòng đầu vào : {self.input_lines:,}",
            f"  Ký tự đầu ra : {self.output_chars:,}",
            f"  Thời gian    : {self.elapsed_seconds:.3f}s",
        ]
        if self.error:
            lines.append(f"  Lỗi          : {self.error}")
        if self.warnings:
            lines.append(f"  Cảnh báo     : {len(self.warnings)} mục")
            for w in self.warnings[:5]:  # Hiển thị tối đa 5 cảnh báo
                lines.append(f"    • {w}")
            if len(self.warnings) > 5:
                lines.append(f"    ... và {len(self.warnings) - 5} cảnh báo khác.")
        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pipeline chính
# ---------------------------------------------------------------------------
def run_pipeline(
    input_path: str | Path,
    output_path: str | Path | None = None,
    log_file: str | Path | None = None,
) -> PipelineResult:
    """
    Chạy toàn bộ pipeline tiền xử lý cho một file văn bản pháp luật.

    Args:
        input_path:  Đường dẫn tới file đầu vào (.docx hoặc .txt).
        output_path: Đường dẫn file đầu ra. Nếu None, tự động tạo tên
                     dựa trên tên file đầu vào trong thư mục outputs/clean_texts/.
        log_file:    Đường dẫn file log. Nếu None, không ghi log ra file.

    Returns:
        PipelineResult chứa thông tin chi tiết về quá trình xử lý.
    """
    input_path = Path(input_path)
    start_time = time.perf_counter()
    warnings: list[str] = []

    # --- Xác định đường dẫn đầu ra ---
    if output_path is None:
        output_dir = _PROJECT_ROOT / "outputs" / "clean_texts"
        stem = input_path.stem
        output_path = output_dir / f"clean_{stem}.txt"
    output_path = Path(output_path)

    logger.info("=" * 60)
    logger.info("BẮT ĐẦU PIPELINE TIỀN XỬ LÝ")
    logger.info("  Đầu vào : %s", input_path)
    logger.info("  Đầu ra  : %s", output_path)
    logger.info("=" * 60)

    # Đảm bảo thư mục đầu ra tồn tại
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # ----------------------------------------------------------------
        # Bước 1: Tải văn bản & phục hồi đánh số tự động
        # ----------------------------------------------------------------
        logger.info("[Bước 1/4] Tải văn bản từ '%s'...", input_path.name)
        loader = get_loader(input_path)
        raw_lines = loader.load(input_path)
        logger.info("  → Đã tải %d dòng.", len(raw_lines))

        if not raw_lines:
            warnings.append("File đầu vào trống hoặc không đọc được nội dung.")

        # ----------------------------------------------------------------
        # Bước 2: Làm sạch nhiễu
        # ----------------------------------------------------------------
        logger.info("[Bước 2/4] Làm sạch văn bản...")
        cleaner = TextCleaner()
        clean_lines = cleaner.clean(raw_lines)
        removed = len(raw_lines) - len(clean_lines)
        logger.info("  → Đã xóa %d dòng nhiễu, còn %d dòng.", removed, len(clean_lines))

        # ----------------------------------------------------------------
        # Bước 3: Chuẩn hóa Unicode NFC
        # ----------------------------------------------------------------
        logger.info("[Bước 3/4] Chuẩn hóa Unicode NFC...")
        normalizer = UnicodeNormalizer()
        normalized_lines = normalizer.normalize(clean_lines)

        if normalizer.stats["lines_changed"] > 0:
            warnings.append(
                f"Phát hiện {normalizer.stats['lines_changed']} dòng có ký tự NFD — "
                f"đã chuẩn hóa sang NFC."
            )

        # ----------------------------------------------------------------
        # Bước 4: Định dạng cấu trúc
        # ----------------------------------------------------------------
        logger.info("[Bước 4/4] Định dạng cấu trúc văn bản...")
        formatter = Formatter()
        final_text = formatter.format(normalized_lines)

        # ----------------------------------------------------------------
        # Ghi file đầu ra (UTF-8, kết thúc bằng \n)
        # ----------------------------------------------------------------
        output_path.write_text(final_text, encoding="utf-8")
        logger.info("  → Đã ghi %d ký tự vào '%s'.", len(final_text), output_path)

        elapsed = time.perf_counter() - start_time
        result = PipelineResult(
            input_path=input_path,
            output_path=output_path,
            success=True,
            elapsed_seconds=elapsed,
            input_lines=len(raw_lines),
            output_chars=len(final_text),
            warnings=warnings,
        )

    except FileNotFoundError as exc:
        elapsed = time.perf_counter() - start_time
        logger.error("[Pipeline] File không tìm thấy: %s", exc)
        result = PipelineResult(
            input_path=input_path,
            output_path=output_path,
            success=False,
            elapsed_seconds=elapsed,
            error=str(exc),
            warnings=warnings,
        )

    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        logger.exception("[Pipeline] Lỗi không xác định khi xử lý '%s': %s", input_path.name, exc)
        result = PipelineResult(
            input_path=input_path,
            output_path=output_path,
            success=False,
            elapsed_seconds=elapsed,
            error=f"{type(exc).__name__}: {exc}",
            warnings=warnings,
        )

    # --- Ghi log ra file nếu được yêu cầu ---
    if log_file is not None:
        _write_log_file(Path(log_file), result)

    print(result)
    return result


def run_batch(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
    pattern: str = "*.docx",
) -> list[PipelineResult]:
    """
    Xử lý hàng loạt tất cả file trong một thư mục.

    Args:
        input_dir:  Thư mục chứa các file đầu vào.
        output_dir: Thư mục đầu ra (mặc định: outputs/clean_texts/).
        pattern:    Glob pattern để lọc file (mặc định: "*.docx").

    Returns:
        Danh sách PipelineResult cho từng file.
    """
    input_dir = Path(input_dir)
    if output_dir is None:
        output_dir = _PROJECT_ROOT / "outputs" / "clean_texts"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(input_dir.glob(pattern))
    if not files:
        logger.warning("[Batch] Không tìm thấy file nào khớp với '%s' trong '%s'.", pattern, input_dir)
        return []

    logger.info("[Batch] Tìm thấy %d file — bắt đầu xử lý...", len(files))
    results: list[PipelineResult] = []

    for file in files:
        out_path = output_dir / f"clean_{file.stem}.txt"
        log_path = output_dir / f"log_{file.stem}.txt"
        result = run_pipeline(file, out_path, log_path)
        results.append(result)

    # --- Tổng kết batch ---
    success_count = sum(1 for r in results if r.success)
    logger.info(
        "[Batch] Hoàn tất: %d/%d file thành công.",
        success_count, len(results),
    )
    return results


# ---------------------------------------------------------------------------
# Ghi log ra file
# ---------------------------------------------------------------------------
def _write_log_file(log_path: Path, result: PipelineResult) -> None:
    """Ghi kết quả pipeline ra file log văn bản."""
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(str(result))
            f.write("\n")
        logger.info("[Pipeline] Log đã ghi vào '%s'.", log_path)
    except OSError as exc:
        logger.warning("[Pipeline] Không thể ghi log: %s", exc)


# ---------------------------------------------------------------------------
# Entrypoint: chạy trực tiếp
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Module 1: Tiền xử lý văn bản pháp luật Việt Nam (.docx → .txt sạch)"
    )
    parser.add_argument(
        "--input",
        default=str(_PROJECT_ROOT / "datasets" / "raw_laws"),
        help="Đường dẫn file hoặc thư mục đầu vào (mặc định: datasets/raw_laws/)",
    )
    parser.add_argument(
        "--output",
        default=str(_PROJECT_ROOT / "outputs" / "clean_texts"),
        help="Đường dẫn file hoặc thư mục đầu ra (mặc định: outputs/clean_texts/)",
    )
    parser.add_argument(
        "--log",
        default=str(_PROJECT_ROOT / "outputs" / "clean_texts" / "processing.log"),
        help="Đường dẫn file log (mặc định: outputs/clean_texts/processing.log)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Ép buộc xử lý hàng loạt tất cả .docx trong thư mục --input",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.batch or input_path.is_dir():
        # Nếu là thư mục, tự động chạy chế độ batch
        out_dir = output_path.parent if output_path.suffix else output_path
        run_batch(
            input_dir=input_path,
            output_dir=out_dir,
        )
    else:
        # Nếu là file, chạy chế độ xử lý 1 file
        # Nếu output truyền vào là một thư mục, tự động sinh tên file
        if not output_path.suffix:
            output_path = output_path / f"clean_{input_path.stem}.txt"
            
        result = run_pipeline(
            input_path=input_path,
            output_path=output_path,
            log_file=args.log,
        )
        sys.exit(0 if result.success else 1)
