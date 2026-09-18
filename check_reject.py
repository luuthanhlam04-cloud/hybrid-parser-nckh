import os
import json
import logging
from collections import Counter
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Thư mục log
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "src", "ontology", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_dir, "rejected_edges.log")
    summary_file_path = os.path.join(log_dir, "rejection_summary.json")

    # Xóa log cũ nếu có
    if os.path.exists(log_file_path):
        os.remove(log_file_path)

    # Cấu hình logging để ghi vào file
    logger = logging.getLogger("src.ontology.ontology_validator")
    logger.setLevel(logging.WARNING)
    
    # File handler
    fh = logging.FileHandler(log_file_path, encoding="utf-8")
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Tạm thời tắt in ra console cho logger này để tránh rác terminal
    logger.propagate = False

    print("Đang chạy lại Module 7 để phân tích lỗi...")
    from src.ontology.ontology_builder import OntologyBuilder
    
    input_path = os.path.join(base_dir, "outputs", "semantic_graphs", "semantic_extraction.json")
    output_path = os.path.join(base_dir, "outputs", "semantic_graphs", "canonical_semantic_graph.json")
    
    if not os.path.exists(input_path):
        print(f"Error: Không tìm thấy {input_path}")
        sys.exit(1)
        
    builder = OntologyBuilder()
    
    # Ghi đè log info của builder để không in ra màn hình quá nhiều
    builder_logger = logging.getLogger("src.ontology.ontology_builder")
    builder_logger.setLevel(logging.ERROR)
    
    builder.build_canonical_graph(input_path, output_path)
    
    # Đóng handler
    fh.close()
    
    print("Hoàn tất chạy Module 7. Đang tổng hợp lỗi...")

    # Phân tích file log
    rejection_counts = Counter()
    
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("REJECT:"):
                    # Chỉ lấy phần thông báo chính, loại bỏ phần text cụ thể (nếu có dấu ngoặc)
                    # VD: REJECT: Range violation for ALLOW. Target class LEGAL_SUBJECT not in ['LEGAL_ACTION']
                    reason = line
                    rejection_counts[reason] += 1
                    
    # Sắp xếp theo số lượng giảm dần
    sorted_reasons = dict(sorted(rejection_counts.items(), key=lambda item: item[1], reverse=True))
    
    # Lưu báo cáo
    report = {
        "total_rejected_edges": sum(sorted_reasons.values()),
        "breakdown": sorted_reasons
    }
    
    with open(summary_file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
        
    print(f"\n=== BÁO CÁO TỪ CHỐI (REJECTION SUMMARY) ===")
    print(f"Tổng số cạnh bị loại: {report['total_rejected_edges']}")
    print("-" * 50)
    for reason, count in sorted_reasons.items():
        print(f"[{count} lần] {reason}")
    print("-" * 50)
    print(f"Đã lưu chi tiết tại: {summary_file_path}")
    print(f"Log gốc tại       : {log_file_path}")

if __name__ == "__main__":
    main()
