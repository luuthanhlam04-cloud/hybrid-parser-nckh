# -*- coding: utf-8 -*-
from update_final_locked_script import slides

total = 0
for s in slides:
    w = len(s['spoken'].split())
    total += w
    print(f"Slide {s['slide']:02d}: {w:3d} words")
print(f"Total: {total} words")
