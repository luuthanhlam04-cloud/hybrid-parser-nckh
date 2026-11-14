# -*- coding: utf-8 -*-
with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'r', encoding='utf-8') as f:
    text = f.read()

part2 = text.split('# PHẦN 2:')[1].split('# PHẦN 3:')[0]
lines = [l.strip() for l in part2.splitlines() if l.strip().startswith('>')]
spoken_text = ' '.join(lines).replace('>', '').replace('*', '').replace('"', '')
words = spoken_text.split()
print('Total exact spoken words in Part 2:', len(words))

# By slide
import re
slides = re.split(r'\*\*\[Slide ', part2)[1:]
for i, s in enumerate(slides, 1):
    s_lines = [l.strip() for l in s.splitlines() if l.strip().startswith('>')]
    s_spoken = ' '.join(s_lines).replace('>', '').replace('*', '').replace('"', '')
    s_words = s_spoken.split()
    print(f'Slide {i:2d}: {len(s_words):3d} words  |  Est. time: {len(s_words)/2.1:.1f}s')
