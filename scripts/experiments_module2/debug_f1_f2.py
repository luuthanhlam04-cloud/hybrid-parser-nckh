# -*- coding: utf-8 -*-
"""Debug script cho failure F1 (CLAUSE) và F2 (POINT)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/regex_parser')))

from regex_engine import RegexEngine, load_docx_paragraphs

engine = RegexEngine()
docx_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Luat_dat_dai_chuong_3 (1).docx')
paragraphs = load_docx_paragraphs(docx_path)

with open('debug_f1_f2.txt', 'w', encoding='utf-8') as out:
    def w(s=''):
        out.write(s + '\n')

    # F1: List Paragraph
    lp = [p for p in paragraphs if p.get('style') == 'List Paragraph']
    w(f'=== F1 DEBUG: List Paragraph (total={len(lp)}) ===')
    for p in lp[:12]:
        r = engine.match_text(p['text'], word_style=p['style'])
        matched = r.node_type.value if r else 'NO_MATCH'
        w(f'  [{matched}] repr={repr(p["text"][:80])}')

    w()
    # F2: Body Text
    bt = [p for p in paragraphs if p.get('style') == 'Body Text']
    w(f'=== F2 DEBUG: Body Text (total={len(bt)}) ===')
    for p in bt:
        r = engine.match_text(p['text'], word_style=p['style'])
        matched = r.node_type.value if r else 'NO_MATCH'
        w(f'  [{matched}] repr={repr(p["text"][:80])}')

    # Test POINT pattern trực tiếp
    w()
    w('=== DIRECT PATTERN TEST ===')
    import re
    point_pattern = re.compile(r'^\s*(?P<marker>[a-z\u0111])\)\s+(?P<text>.+)$', re.UNICODE)
    for p in bt:
        m = point_pattern.match(p['text'].strip())
        w(f'  pattern_match={bool(m)} | repr={repr(p["text"][:50])}')

print('Done -> debug_f1_f2.txt')
