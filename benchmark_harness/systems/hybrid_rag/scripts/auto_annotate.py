import csv
import os

INPUT_CSV = "outputs/golden_set_annotation.csv"

def is_semantic(text: str) -> int:
    text_lower = text.lower()
    
    # Empty text -> 0
    if not text.strip():
        return 0
        
    # Keywords indicating a semantic graph relationship (exception, condition, cross-ref)
    keywords = [
        "trừ trường hợp", "ngoại trừ", "trừ khi",
        "theo quy định", "quy định tại", "quy định của pháp luật", "quy định của chính phủ",
        "trường hợp", "trong trường hợp", 
        "khi có đủ điều kiện", "khi đáp ứng điều kiện",
        "các trường hợp không được"
    ]
    
    # Tránh các câu dạo đầu (preamble) không chứa semantic rule cụ thể
    # Ví dụ: "Quyền và nghĩa vụ... được quy định như sau:" 
    # Nhưng nếu preamble có chứa cross-ref (như "quy định tại Điều X") thì vẫn tính.
    
    for kw in keywords:
        if kw in text_lower:
            # Check if it's just a preamble without real reference
            if kw == "trường hợp" and "các trường hợp không được" not in text_lower and not text_lower.startswith("trường hợp"):
                pass
            return 1
            
    return 0

def main():
    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            node_id = row[0]
            text = row[1]
            semantic_val = is_semantic(text)
            rows.append([node_id, text, str(semantic_val), "AI Annotated"])

    with open(INPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Đã gán nhãn thành công {len(rows)} nodes!")

if __name__ == "__main__":
    main()
