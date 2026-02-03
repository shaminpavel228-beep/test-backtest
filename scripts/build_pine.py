#!/usr/bin/env python3
"""Simple build script for Pine sources.
Currently copies `pine/src/backtest_raw.pine` to `pine/backtest.pine`.
Future: concatenate modular files in a defined order.
"""
from pathlib import Path
import shutil

SRC = Path('pine/src/backtest_raw.pine')
DST = Path('pine/backtest.pine')

DST.parent.mkdir(parents=True, exist_ok=True)
if SRC.exists():
    shutil.copy2(SRC, DST)
    print('Built', DST)
else:
    print('Source not found:', SRC)
    raise SystemExit(2)
