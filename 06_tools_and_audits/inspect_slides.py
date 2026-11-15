# -*- coding: utf-8 -*-
import os

with open('06_tools_and_audits/craft_master_1800_script.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect each slide's current word count
namespace = {}
exec(content, namespace)
slides = namespace['slides_data']

for s in slides:
    words = len(s['spoken'].split())
    print(f"Slide {s['slide']:02d}: {words:3d} words")
