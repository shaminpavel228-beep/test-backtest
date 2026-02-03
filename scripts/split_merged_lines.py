#!/usr/bin/env python3
import re
from pathlib import Path

def split_merged_lines(src, dst):
    p = Path(src)
    text = p.read_text(encoding='utf-8')
    out_lines = []
    for line in text.splitlines():
        # if line contains a ')' followed by spaces and then an identifier + ' ='
        m = re.search(r"\)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
        if m:
            # split at the ')' that precedes the identifier
            idx = line.find(')')
            before = line[:idx+1].rstrip()
            after = line[idx+1:].lstrip()
            # append both parts as separate lines
            out_lines.append(before)
            out_lines.append(after)
        else:
            out_lines.append(line)
    Path(dst).write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    print(f"Wrote {dst}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('usage: split_merged_lines.py <src> <dst>')
        raise SystemExit(2)
    split_merged_lines(sys.argv[1], sys.argv[2])
