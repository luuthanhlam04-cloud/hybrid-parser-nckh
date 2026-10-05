import subprocess
import json
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("=" * 60)
    print("1. ĐANG CHẠY UNIT TESTS (pytest)")
    print("=" * 60)
    
    # Run pytest
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_ontology_m7.py", "-v"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("UNIT TESTS FAILED! Xin vui lòng kiểm tra lại code.")
        print(result.stderr)
        return

    print("=" * 60)
    print("2. ĐANG CHẠY TÍCH HỢP M7 (Integration với M6 Data)")
    print("=" * 60)
    
    # Run ontology builder
    from src.ontology.ontology_builder import OntologyBuilder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "outputs", "semantic_graphs", "semantic_extraction.json")
    output_path = os.path.join(base_dir, "outputs", "semantic_graphs", "canonical_semantic_graph.json")
    
    if not os.path.exists(input_path):
        print(f"Error: Không tìm thấy file {input_path}")
        return
        
    builder = OntologyBuilder()
    builder.build_canonical_graph(input_path, output_path)
    
    # Read output validation report
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    report = data.get("validation_report", {})
    
    print("\n" + "=" * 60)
    print("3. BẢNG BEFORE/AFTER METRICS (DỰA TRÊN P0 FIX)")
    print("=" * 60)
    print(f"Input Entities từ M6: {report.get('input_entities')}")
    print(f"Input Relations từ M6: {report.get('input_relations')}")
    print("-" * 60)
    print(f"Canonical Entities  : {report.get('canonical_entities')}")
    print(f"Quarantined Entities: {report.get('quarantined_entities')} (Tăng vọt do Strict Class Constraint)")
    print("-" * 60)
    print(f"Canonical Relations : {report.get('canonical_relations')}")
    print(f"Rejected Relations  : {report.get('rejected_relations')}")
    print("\n[Chi tiết Rejection Breakdown]")
    for reason, count in report.get('rejection_breakdown', {}).items():
        print(f" - [{count:03d} lần] {reason}")
        
    print("\n" + "=" * 60)
    print("!!! CẢNH BÁO CHO HUMAN !!!")
    print("Tỷ lệ Quarantine TĂNG VỌT là ĐÚNG THIẾT KẾ do Class-Constraint.")
    print("M7 đã chặn mọi nỗ lực Fuzzy Match chéo class (VD: ép ACTION thành SUBJECT).")
    print("Do đó, dữ liệu rác từ M6 bị lộ diện. Đề nghị sửa Prompt M6 để LLM trích xuất đúng Class.")
    print("============================================================")

if __name__ == "__main__":
    main()
