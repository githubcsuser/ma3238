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
| Body / symbol definitions / Meaning / Use / Check | 5.8 pt (column 8 is 5.6 pt) |
| Symbol definitions | one per line, only the symbol bold |

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

**Page 1** — 1 Probability tools · 2 Build and verify a chain · 3 Finite-time
probabilities · 4 Models and random walks · 5 First-step analysis

**Page 2** — 6 Verify and build martingales · 7 Stopping and optional stopping ·
8 Generating functions and sums · 9 Branching: growth and extinction ·
10 Branching variants

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
