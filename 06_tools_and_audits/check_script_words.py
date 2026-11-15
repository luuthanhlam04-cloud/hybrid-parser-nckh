# -*- coding: utf-8 -*-
import re

with open('docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

quotes = re.findall(r'> \*"([\s\S]*?)"\*', text)
print(f"Total slides matched: {len(quotes)}")
total = 0
for i, q in enumerate(quotes):
    clean_q = re.sub(r'>\s*', '', q)
    w = len(clean_q.split())
    total += w
    print(f"Slide {i+1:02d}: {w:3d} words")

print("-" * 30)
print(f"Total spoken words: {total}")
time_min = total / 130
print(f"Time @ 130 wpm: {time_min:.2f} mins ({total/(130/60):.0f}s)")
print(f"Buffer: {15*60 - total/(130/60):.0f}s")
