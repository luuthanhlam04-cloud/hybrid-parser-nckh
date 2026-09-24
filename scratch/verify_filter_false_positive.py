import sys, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

_PLACEHOLDERS = {'', 'n/a', 'na', 'none', 'null', 'unknown', 'test', '...', 'khong co', 'không có'}

def is_placeholder(text):
    normalized = re.sub(r'\s+', ' ', text).strip().casefold()
    normalized = unicodedata.normalize('NFC', normalized)
    return normalized in _PLACEHOLDERS

# Test: valid legal texts that CONTAIN placeholder substrings
# Nếu check là exact match → những case này phải PASS (không bị block nhầm)
test_cases = [
    # Texts chứa substring "không có" nhưng là câu hợp lệ
    ("Đất không có tranh chấp", "valid — có 'không có' nhưng là cụm từ pháp lý"),
    ("Trường hợp không có giấy chứng nhận", "valid — câu điều kiện"),
    ("Không có giấy tờ", "valid — điều kiện"),
    # Texts chứa "null" theo nghĩa tiếng Anh
    ("null and void", "valid — cụm pháp lý tiếng Anh"),
    ("Null hypothesis", "valid — thuật ngữ"),
    # Texts chứa "unknown"
    ("Unknown person", "edge case"),
    # Texts chứa "test"
    ("test case pháp lý", "edge case"),
    # Texts rõ ràng là placeholder (phải bị BLOCK)
    ("không có", "garbage — placeholder chính xác"),
    ("...", "garbage — placeholder"),
    ("n/a", "garbage — placeholder"),
    ("", "garbage — rỗng"),
    ("null", "garbage — placeholder"),
    ("unknown", "garbage — placeholder"),
    ("   ", "garbage — chỉ có space"),
    # Valid texts bình thường
    ("Nhà nước", "valid entity"),
    ("Chuyển nhượng quyền sử dụng đất", "valid action"),
    ("Ủy ban nhân dân cấp tỉnh", "valid subject"),
    ("Quyền sử dụng đất", "valid object"),
]

print("=" * 70)
print("NodeQualityFilter False Positive Verify")
print("Kiểm tra: exact match hay substring match?")
print("=" * 70)

false_positives = []
false_negatives = []

for text, label in test_cases:
    result = is_placeholder(text)
    is_garbage = "garbage" in label
    is_valid = "valid" in label

    if result and is_valid:
        flag = "🔴 FALSE POSITIVE"
        false_positives.append(text)
    elif not result and is_garbage:
        flag = "🔴 FALSE NEGATIVE"
        false_negatives.append(text)
    elif result and is_garbage:
        flag = "✅ Correct BLOCK"
    else:
        flag = "✅ Correct PASS"

    print(f"  {flag}")
    print(f"    text   : '{text}'")
    print(f"    context: {label}")
    print()

print("=" * 70)
print(f"False Positives (bị block nhầm): {len(false_positives)}")
for fp in false_positives:
    print(f"  '{fp}'")
print(f"False Negatives (không block garbage): {len(false_negatives)}")
for fn in false_negatives:
    print(f"  '{fn}'")

if not false_positives and not false_negatives:
    print("\nVERDICT: ✅ Exact match — NodeQualityFilter AN TOÀN, không false positive")
elif false_positives:
    print("\nVERDICT: ⚠️  Có false positive — cần kiểm tra lại logic match")
