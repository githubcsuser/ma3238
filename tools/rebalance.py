#!/usr/bin/env python3
"""Read cheatsheet.tex, measure every block, and repartition the blocks into 10
contiguous columns balanced under the page height.

  python3 rebalance.py            -> report the proposed partition only
  python3 rebalance.py --write    -> rewrite cheatsheet.tex with that partition

Block order is preserved (it is the teaching order); only the column boundaries
move. Column titles come from TITLES below and are applied in order.
"""
import re
import sys

import estimate_fill as E

SRC = 'cheatsheet.tex'
NCOL = 10

TITLES = [
    r'1\quad Probability tools',
    r'2\quad Conditioning and process setup',
    r'3\quad Markov property and transitions',
    r'4\quad Inference, hidden Markov, models',
    r'5\quad Walks and first-step analysis',
    r'6\quad Martingales',
    r'7\quad Stopping times and OST',
    r'8\quad Generating functions and sums',
    r'9\quad Branching: growth and extinction',
    r'10\quad Branching variants',
]


def split_blocks(src):
    """Ordered [(name, text, height)] across every column, plus the shared head."""
    cols = E.split_columns(src)
    fs, lead = E.env_default(src)
    out = []
    for _title, body, cfs, clead in cols:
        for part in re.split(r'(?=\\bx\{)', body):
            if not part.strip():
                continue
            h, _ = E.measure(part, cfs, clead)
            m = re.match(r'\\bx\{(.*?)\}', part)
            name = m.group(1) if m else '(intro text)'
            out.append((name, part.rstrip() + '\n', h))
    return out


def partition(blocks, ncol, cap):
    """Optimal contiguous split minimising the tallest column (DP).

    dp[j][i] = smallest achievable tallest column when the first i blocks are
    cut into j contiguous columns. Greedy first-fit is not optimal here, which
    is why an exact DP is used.
    """
    sizes = [h for _, _, h in blocks]
    n = len(sizes)
    pre = [0.0] * (n + 1)
    for i, s in enumerate(sizes):
        pre[i + 1] = pre[i] + s

    INF = float('inf')
    dp = [[INF] * (n + 1) for _ in range(ncol + 1)]
    cut = [[0] * (n + 1) for _ in range(ncol + 1)]
    for i in range(n + 1):
        dp[1][i] = pre[i]
    for j in range(2, ncol + 1):
        for i in range(1, n + 1):
            best, bt = INF, 0
            for t in range(j - 1, i):
                val = max(dp[j - 1][t], pre[i] - pre[t])
                if val < best:
                    best, bt = val, t
            dp[j][i], cut[j][i] = best, bt

    bounds, i = [], n
    for j in range(ncol, 0, -1):
        t = cut[j][i] if j > 1 else 0
        bounds.append((t, i))
        i = t
    bounds.reverse()
    groups = []
    for a, b in bounds:
        items = blocks[a:b]
        groups.append((items, sum(x[2] for x in items)))
    return dp[ncol][n], groups


def main():
    src = open(SRC).read()
    E.load_metrics(src)
    blocks = split_blocks(src)
    cap = E.CAPACITY
    total = sum(h for _, _, h in blocks)
    print('blocks %d   total %.0fpt   capacity %.0fpt   overall %.1f%%'
          % (len(blocks), total, NCOL * cap, total / (NCOL * cap) * 100))
    limit, groups = partition(blocks, NCOL, cap)
    print('balanced limit %.0fpt (%.1f%% of the %.0fpt column)\n'
          % (limit, limit / cap * 100, cap))
    ok = True
    for i, (items, h) in enumerate(groups, 1):
        flag = ''
        if h > cap:
            flag = '  *** OVER'
            ok = False
        print('col %2d  %5.0fpt  %5.1f%%  %d blocks%s'
              % (i, h, h / cap * 100, len(items), flag))
        for name, _, s in items:
            print('        %4.0fpt  %s' % (s, name))
    print('\n' + ('FITS: every column within the page height'
                  if ok else 'STILL OVER - shed more content'))

    if '--write' in sys.argv and ok:
        head = src[:src.index(r'\begin{col}{')]
        tail = '\\end{document}\n'
        page2_head = re.search(r'(\\head\{Stopping[^\n]*\n\\noindent\n)', src)
        parts = [head]
        for i, (items, _h) in enumerate(groups):
            if i == 5:  # page break before column 6
                parts.append('\\end{col}\n\\newpage\n')
                parts.append(page2_head.group(1) if page2_head else '')
            elif i:
                parts.append('\\end{col}\\gap%\n')
            parts.append('\\begin{col}{%s}\n' % TITLES[i])
            for _n, text, _s in items:
                parts.append(text)
        parts.append('\\end{col}\n' + tail)
        open(SRC, 'w').write(''.join(parts))
        print('\nrewrote %s' % SRC)


if __name__ == '__main__':
    main()
