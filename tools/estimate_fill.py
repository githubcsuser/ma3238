#!/usr/bin/env python3
"""Estimate per-column height of cheatsheet.tex without a TeX engine.

Models the layout the preamble actually sets up:
  page  A4 landscape 595.28pt tall, 5mm (14.23pt) margins
  header ~15pt, section rule block ~13pt
  body   5.8pt/6.55pt leading (5.6pt/6.3pt where a column overrides)
  column 55mm = 156.5pt wide -> ~60 chars per line at 5.8pt Times

Calibration: the known-good 2-page version must show every column under the
capacity figure. Run against a known-good file first to trust the numbers.
"""
import re
import sys

PAGE_H = 595.28
MARGIN = 14.23
HEADER = 15.0
SECTION = 13.0
GEOMETRIC = PAGE_H - 2 * MARGIN - HEADER - SECTION  # ~539pt, naive figure

# CALIBRATION. The naive geometric figure above is ~9% pessimistic: this model
# over-counts wrapped lines (control words are charged a full glyph, RaggedRight
# packs better than assumed). Reference point: the version committed as the
# known-good sheet compiled to exactly two A4 landscape pages, and its tallest
# column measures 589pt under this same model. So 589pt is an empirically
# demonstrated ceiling. A safety margin is kept below it.
REFERENCE_MAX = 589.0
CAPACITY = 570.0

COL_W_PT = 55.0 / 25.4 * 72.0  # 55mm in points

# filled in from the source by load_metrics()
EQ_LEAD = 9.0
EQ_PAD = 1.2
BX_PAD = 1.8


def load_metrics(src):
    """Read the actual \eq leading/padding and \bx spacing out of the preamble."""
    global EQ_LEAD, EQ_PAD, BX_PAD
    m = re.search(r'\\newcommand\{\\eq\}.*?\\fontsize\{[\d.]+\}\{([\d.]+)\}', src, re.S)
    if m:
        EQ_LEAD = float(m.group(1))
    m = re.search(r'\\newcommand\{\\eq\}.*?\\vspace\{([\d.]+)pt\}', src, re.S)
    if m:
        EQ_PAD = float(m.group(1))
    m = re.search(r'\\newcommand\{\\bx\}.*?\\vspace\{([\d.]+)pt\}', src, re.S)
    if m:
        BX_PAD = float(m.group(1))


def chars_per_line(fs):
    # average glyph advance for Times-like text ~0.45em
    return max(1, int(COL_W_PT / (0.45 * fs)))


def strip_math(s):
    """Rough visible-length of a snippet containing LaTeX markup."""
    s = re.sub(r'\\[a-zA-Z]+\s*', 'x', s)   # control words -> ~1 glyph
    s = re.sub(r'[{}$\\]', '', s)
    return s


def wrapped_lines(text, fs):
    n = len(strip_math(text))
    cpl = chars_per_line(fs)
    return max(1, -(-n // cpl))


def env_default(src):
    """Body font size/leading set by the col environment in the preamble."""
    m = re.search(r'\\begin\{minipage\}\[t\]\{55mm\}\\fontsize\{([\d.]+)\}\{([\d.]+)\}', src)
    return (float(m.group(1)), float(m.group(2))) if m else (5.8, 6.55)


def split_columns(src):
    """Return [(title, body, fontsize, leading)] for each col environment.

    A column may carry an inline \fontsize override right after its title,
    which wins over the environment default.
    """
    base_fs, base_lead = env_default(src)
    out = []
    for m in re.finditer(r'\\begin\{col\}\{(.*?)\}(.*?)\\end\{col\}', src, re.S):
        title, body = m.group(1), m.group(2)
        fs = base_fs
        fo = re.match(r'\s*\\fontsize\{([\d.]+)\}\{([\d.]+)\}\\selectfont', body)
        lead = None
        if fo:
            fs = float(fo.group(1))
            lead = float(fo.group(2))
            body = body[fo.end():]
        if lead is None:
            lead = base_lead if fs == base_fs else fs * 1.13
        out.append((title, body, fs, lead))
    return out


def brace_span(s, start):
    """Index just past the matching close brace for the '{' at s[start]."""
    depth = 0
    i = start
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(s)


def measure(body, fs, lead):
    """Walk the column body and accumulate estimated height in points."""
    h = 0.0
    i = 0
    detail = []
    while i < len(body):
        m = re.compile(r'\\(bx|eq|sy|mng|use|ck)\{').search(body, i)
        if not m:
            tail = body[i:].strip()
            if tail:
                lines = wrapped_lines(tail, fs)
                h += lines * lead
                detail.append(('text', lines * lead))
            break
        # plain text sitting between macros (e.g. the notation paragraph)
        gap = body[i:m.start()].strip()
        if gap:
            lines = wrapped_lines(gap, fs)
            h += lines * lead
            detail.append(('text', lines * lead))
        kind = m.group(1)
        open_brace = m.end() - 1
        end = brace_span(body, open_brace)
        arg = body[open_brace + 1:end - 1]
        if kind == 'bx':
            # block title line, plus the {ref} argument that follows
            end2 = brace_span(body, end) if end < len(body) and body[end] == '{' else end
            h += BX_PAD + lead
            detail.append(('bx', 2.2 + lead))
            end = end2
        elif kind == 'eq':
            rows = arg.count('\\\\') + 1
            # displayed math: leading and surrounding vspace read from \eq
            block = rows * EQ_LEAD + 2 * EQ_PAD
            h += block
            detail.append(('eq', block))
        else:
            lines = wrapped_lines(arg, fs)
            h += lines * lead
            detail.append((kind, lines * lead))
        i = end
    return h, detail


def main(path):
    src = open(path).read()
    load_metrics(src)
    cols = split_columns(src)
    print(f'file: {path}')
    print(f'capacity per column: {CAPACITY:.0f}pt '
          f'({CAPACITY/72*25.4:.0f}mm)\n')
    worst = 0.0
    over = []
    for n, (title, body, fs, lead) in enumerate(cols, 1):
        h, _ = measure(body, fs, lead)
        pct = h / CAPACITY * 100
        flag = ''
        if pct > 100:
            flag = '  *** OVER'
            over.append(n)
        elif pct > 92:
            flag = '  <-- tight'
        clean = re.sub(r'\\quad', ' ', title)
        print(f'col {n:2d}  {h:6.0f}pt  {pct:5.1f}%  {fs}pt  {clean}{flag}')
        worst = max(worst, pct)
    print(f'\nworst column: {worst:.1f}% of capacity')
    if over:
        print(f'columns over capacity: {over}  -> would spill past 2 pages')
    else:
        print('all columns within capacity -> 2 pages')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'cheatsheet.tex')
