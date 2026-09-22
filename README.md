# ST3236 / MA3238 Stochastic Processes I — midterm cheatsheet

Two-page A4 landscape reference sheet, 5 columns per page (10 columns total),
covering Lectures 1–5 and Tutorials 1–5.

## Build

```sh
pdflatex cheatsheet.tex
```

One pass is enough — no bibliography or index.

**Required packages:** `geometry`, `fontenc`, `amsmath`, `bm`, `xcolor`,
`microtype`, `ragged2e`, `newtxtext`, `newtxmath`.

If `newtx` is not installed, replace

```latex
\usepackage{newtxtext,newtxmath}
```

with

```latex
\usepackage{lmodern}
```

The layout still fits two pages.

## Layout spec

| Element | Setting |
|---|---|
| Paper | A4 landscape, 5 mm margins |
| Columns | 5 per page, 55 mm wide, 3 mm gaps |
| Formulas | bold, 7.5 pt (the only prominent line in each block) |
| Body / symbol definitions / Meaning / Use / Check | 5.5 pt |
| Symbol definitions | one per line, only the symbol bold |

All math script and scriptscript sizes are >= 5.5 pt, so nothing on the sheet
renders below 5.5 pt.

Each block follows: name → formula → one symbol definition per line →
`Meaning:` → `Use:` → `Check:` (verification blocks only).

## Build diagnostics

The preamble writes two diagnostics to the `.log`:

- `COLUMN-HEIGHT` — height of each of the 10 columns, to check for overflow.
- `WIDE-EQ <line number>` — any formula wider than the 55 mm column.

Grep for them after building:

```sh
grep -E 'COLUMN-HEIGHT|WIDE-EQ|Overfull|Output written' cheatsheet.log
```

If `WIDE-EQ` names the whole-parent vaccination formula (column 10), change the
`,\quad` in that line to `\\` to split it across two lines.

## Numerical verification

```sh
python3 verify_math.py
```

Checks the worked results against exact rational arithmetic:

- T2.4 queue construction, matrix power, bridge distribution
- T2.5 HMM filtering and next-observation probability
- L4 gambler's ruin probability and duration, biased case
- T4.1 non-unit jump overshoot, exit distribution, OST duration
- T4.3 compound PGF composition and coefficients
- T4.5 / T5.5 alternating composition order and moment recursions
- Branching variance: subcritical, critical, supercritical
- T5.3 independent-child vaccination mean and variance

All eight groups pass.

## Contents by column

**Page 1** — 1 Probability tools · 2 Conditioning and process setup ·
3 Markov property and transitions · 4 Inference, hidden Markov, models ·
5 Walks and first-step analysis

**Page 2** — 6 Martingales · 7 Stopping times and OST · 8 Generating functions
and sums · 9 Branching: growth and extinction · 10 Branching variants

58 blocks total: 57 formulas, 150 symbol definitions, 57 `Meaning`/`Use` pairs,
10 `Check` procedures.

## `tools/` — layout measurement

The sheet is packed close to the page limit, so two scripts measure and balance
it without needing a TeX engine.

```sh
python3 tools/estimate_fill.py cheatsheet.tex   # per-column height vs capacity
python3 tools/rebalance.py                      # propose a balanced partition
python3 tools/rebalance.py --write              # apply that partition
```

`estimate_fill.py` models wrapped-line heights and reports each column as a
percentage of the usable page height. Its capacity figure is **calibrated**: the
naive geometric value (539 pt) proved ~9% pessimistic, because the model charges
a full glyph per LaTeX control word and assumes worse line packing than
`RaggedRight` achieves. The reference point is a version that compiled to
exactly two pages while measuring 589 pt in its tallest column, so 589 pt is a
demonstrated ceiling; the scripts work to 570 pt for margin.

`rebalance.py` measures every block, then finds the **optimal** contiguous split
into 10 columns by dynamic programming (minimising the tallest column). Greedy
first-fit is not optimal here and leaves columns overfull, which is why the DP
is used. Current worst column: 546 pt, 96% of the 570 pt working capacity.

## `fallback-python/`

A dependency-free Python PDF generator (no TeX, no third-party packages) plus
its output, `cheatsheet-python-fallback.pdf`. This is an **earlier, less
complete** version of the sheet — useful only if you cannot run `pdflatex`.
`cheatsheet.tex` is the authoritative source.

```sh
cd fallback-python && python3 cheatsheet.py
```

## Note

`cheatsheet.tex` has not been compiled in this environment (no TeX engine
available). Its structure and all numerical results were verified; pagination
should be confirmed on first local build.
