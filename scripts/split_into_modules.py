#!/usr/bin/env python3
"""Split backtest_raw.pine into modular files based on section headers.
Rules:
- A header is a line matching '^// =+' (a long comment of '='), the next non-empty comment line will be used as title.
- Each section file will be named with a numeric prefix by order and a slug of the title.
"""
from pathlib import Path
import re

SRC = Path('pine/src/backtest_raw.pine')
OUT_DIR = Path('pine/src/parts')

if not SRC.exists():
    print('Source not found:', SRC)
    raise SystemExit(2)

text = SRC.read_text(encoding='utf-8')
lines = text.splitlines()

sections = []
cur = []
cur_title = 'preamble'
state = 0
for i, line in enumerate(lines):
    if re.match(r'^//\s*=+', line):
        # start of a new header block; commit previous
        if cur:
            sections.append((cur_title, cur))
            cur = []
        # peek ahead for next non-empty comment line to use as title
        title = None
        for j in range(i+1, min(i+6, len(lines))):
            ln = lines[j].strip()
            if ln.startswith('//'):
                # clean title
                title = ln.lstrip('/').strip()
                break
            elif ln:
                break
        cur_title = title or f'section_{len(sections)+1}'
        cur.append(line)
    else:
        cur.append(line)

# append final
if cur:
    sections.append((cur_title, cur))

OUT_DIR.mkdir(parents=True, exist_ok=True)
for idx, (title, content) in enumerate(sections, start=1):
    # make filename safe
    slug = re.sub(r"[^0-9a-zA-Zа-яА-Я_ -]", '', title)[:60].strip().replace(' ', '_')
    if not slug:
        slug = f'section_{idx}'
    fname = OUT_DIR / f"{idx:02d}_{slug}.pine"
    fname.write_text('\n'.join(content) + '\n', encoding='utf-8')
    print('Wrote', fname)

print('Split into', len(sections), 'parts in', OUT_DIR)