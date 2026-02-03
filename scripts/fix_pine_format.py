#!/usr/bin/env python3
import sys
from pathlib import Path


def paren_balance(s):
    return s.count("(") - s.count(")")

def quotes_balanced(s):
    # simple check: counts of double quotes even
    return s.count('"') % 2 == 0 and s.count("'") % 2 == 0


def fix_file(src, dst):
    src_p = Path(src)
    dst_p = Path(dst)
    if not src_p.exists():
        print(f"Source not found: {src}")
        return 2
    buf = ""
    out_lines = []
    import re
    stmt_split_re = re.compile(r"\)\s+(?=[a-zA-Z_][a-zA-Z0-9_]*\s*=)")
    with src_p.open('r', encoding='utf-8') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if not buf:
                buf = line
            else:
                buf += ' ' + line
            # If parentheses and quotes are balanced we flush
            if paren_balance(buf) == 0 and quotes_balanced(buf):
                # collapse multiple spaces
                cleaned = ' '.join(buf.split())
                # split into multiple statements if something like ')  identifier = ' was merged
                # replace pattern with ')\n' to ensure each statement is on its own line
                cleaned = stmt_split_re.sub(')\n', cleaned)
                for stmt in cleaned.split('\n'):
                    out_lines.append(stmt)
                buf = ""
            else:
                # continue accumulating
                continue
    # Flush remaining
    if buf:
        cleaned = ' '.join(buf.split())
        cleaned = stmt_split_re.sub(')\n', cleaned)
        for stmt in cleaned.split('\n'):
            out_lines.append(stmt)

    # Write output
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    with dst_p.open('w', encoding='utf-8') as f:
        for l in out_lines:
            f.write(l + '\n')
    print(f"Wrote cleaned file to: {dst}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: fix_pine_format.py <input> <output>')
        sys.exit(2)
    sys.exit(fix_file(sys.argv[1], sys.argv[2]))
