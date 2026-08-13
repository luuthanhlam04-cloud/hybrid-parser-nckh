import re

# PART: "Phần"
PART_PATTERN = re.compile(r"^\s*Phần\s+(?:[IVXLCDM]+|thứ\s+[a-zA-ZáàãảạăắằẵẳặâấầẫẩậéèẽẻẹêếềễểệíìĩỉịóòõỏọôốồỗổộơớờỡởợúùũủụưứừữửựýỳỹỷỵđĐ]+)", re.IGNORECASE)

# CHAPTER: "Chương"
CHAPTER_PATTERN = re.compile(r"^\s*Chương\s+[IVXLCDM]+")

# SECTION: "Mục"
SECTION_PATTERN = re.compile(r"^\s*Mục\s+\d+")

# ARTICLE: "Điều"
ARTICLE_PATTERN = re.compile(r"^\s*Điều\s+\d+\.")

# CLAUSE: "Khoản"
CLAUSE_PATTERN = re.compile(r"^\s*\d+\.")

# POINT: "Điểm"
POINT_PATTERN = re.compile(r"(?:^\s*|\s+)([a-zđĐ])\)\s")
