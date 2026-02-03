#!/usr/bin/env python3
"""Build script for Pine sources.
If `pine/src/parts` exists, concatenate all files in sorted order into `pine/backtest.pine`.
Otherwise fall back to copying `pine/src/backtest_raw.pine`.
"""
from pathlib import Path
import shutil

SRC = Path('pine/src/backtest_raw.pine')
PARTS_DIR = Path('pine/src/parts')
DST = Path('pine/backtest.pine')

DST.parent.mkdir(parents=True, exist_ok=True)

if PARTS_DIR.exists() and PARTS_DIR.is_dir():
    parts = sorted(PARTS_DIR.glob('*.pine'))
    if not parts:
        print('No parts found in', PARTS_DIR)
    else:
        with DST.open('w', encoding='utf-8') as out:
            out.write('// Built from parts in {}\n\n'.format(PARTS_DIR))
            for p in parts:
                out.write(f'// --- {p.name} ---\n')
                out.write(p.read_text(encoding='utf-8'))
                out.write('\n\n')
        print('Built', DST, 'from', len(parts), 'parts')
elif SRC.exists():
    shutil.copy2(SRC, DST)
    print('Built', DST, 'from raw source')
else:
    print('No source found:', SRC, 'or parts in', PARTS_DIR)
    raise SystemExit(2)
