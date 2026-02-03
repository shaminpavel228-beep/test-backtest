#!/usr/bin/env python3
"""Simple static checks for Pine scripts.
Checks for:
- balanced parentheses/brackets
- even number of double quotes
- no extremely long single-line statements (as a heuristic)
"""
import sys
from pathlib import Path

def check(path: Path):
    s = path.read_text(encoding='utf-8')
    # brackets
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for i, ch in enumerate(s, 1):
        if ch in '([{':
            stack.append((ch, i))
        elif ch in ')]}':
            if not stack or stack[-1][0] != pairs[ch]:
                print(f"Unbalanced bracket {ch} at pos {i}")
                return 1
            stack.pop()
    if stack:
        print('Unmatched opening brackets at positions:', [pos for _, pos in stack])
        return 1

    # quotes
    if s.count('"') % 2 != 0:
        print('Odd number of double quotes')
        return 1

    # long lines heuristic
    bad = [ (i+1,len(l)) for i,l in enumerate(s.splitlines()) if len(l) > 400 ]
    if bad:
        print('Warning: extremely long lines (line,length):')
        for b in bad[:10]:
            print(b)

    print('Checks passed for', path)
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: check_pine.py <file>')
        raise SystemExit(2)
    raise SystemExit(check(Path(sys.argv[1])))
