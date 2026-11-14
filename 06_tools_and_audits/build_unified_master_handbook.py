# -*- coding: utf-8 -*-
"""
build_unified_master_handbook.py
Xây dựng Bộ Cẩm nang Phản biện NCKH Thống nhất (Unified Master Edition)
kết hợp 5 Tầng kiến thức nền tảng, 64 câu hỏi thực chiến chuẩn format 6 thành phần,
và Cheat sheet số liệu đối soát 100% bancuoi.docx.
"""

import os
import re

md_path = r"c:\Users\luuth\NCKH\Benchmark\docs\cam_nang_chuyen_sau_chuan_bi_phan_bien.md"
docx_path = r"c:\Users\luuth\NCKH\Benchmark\cam_nang_chuyen_sau_chuan_bi_phan_bien.docx"

print("[*] Generating master markdown content...")

