#!/usr/bin/env bash
set -euo pipefail
FILE=${1:-${FILE:-pine/backtest.pine}}
export FILE="$FILE"
python3 - <<'PY'
import os, sys, re
p = os.environ.get('FILE')
if not p:
    print('FILE env var not set')
    sys.exit(2)
s = open(p, encoding='utf-8').read()
parens = s.count('(') - s.count(')')
quotes = s.count('"') % 2
squotes = s.count("'") % 2
print(f"Parens balance: {parens}")
print(f'Double quotes balanced: {quotes==0}')
print(f"Single quotes balanced: {squotes==0}")
if parens != 0 or quotes != 0 or squotes != 0:
    print('ERROR: Unbalanced syntax detected')
    sys.exit(1)
# check for multiple statements on a single line (simple heuristic)
bad = []
for i,l in enumerate(open(p, encoding='utf-8')):
    if re.search(r"\)\s+\w+\s*=", l):
        bad.append((i+1,l.strip()))
if bad:
    print('WARNING: potential multiple statements on one line found:')
    for ln, txt in bad[:10]:
        print(ln, txt)
    # don't exit non-zero, just warn
print('Basic validation OK')
PY

echo "Done"
