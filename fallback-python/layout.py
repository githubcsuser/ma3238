"""Column-flow layout on top of pdfdoc.

Markup mini-language for inline runs (compact authoring):
  Plain text -> Helvetica body.
  Segments wrapped in markers:
    *bold*         -> Helvetica-Bold (used for formulas / bold symbols)
    /italic/       -> Times-Italic (rarely)
  Greek & math via backslash tokens that map to Symbol font:
    \pi \lambda \mu \sigma \phi \theta \alpha \beta \gamma \delta \rho \tau
    \Sigma \Pi \Phi \Omega \Delta
    \sum \prod \sqrt \in \notin \le \ge \ne \approx \to \Rightarrow \times
    \cdot \infty \partial \int \pm \cup \cap \emptyset \subset \subseteq
    \forall \exists \propto
  Super/subscripts:
    ^{...}  -> superscript ; _{...} -> subscript  (single char: ^x _i also ok)
  Font of the current segment (bold vs normal) carries into sup/sub and stays
  for sym tokens' size.
"""
import pdfdoc

TOKENS = {
    "pi": "\u03c0", "lambda": "\u03bb", "mu": "\u03bc", "sigma": "\u03c3",
    "phi": "\u03c6", "varphi": "\u03d5", "theta": "\u03b8", "alpha": "\u03b1",
    "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4", "rho": "\u03c1",
    "tau": "\u03c4", "eta": "\u03b7", "nu": "\u03bd", "xi": "\u03be",
    "kappa": "\u03ba", "zeta": "\u03b6", "psi": "\u03c8", "omega": "\u03c9",
    "epsilon": "\u03b5", "chi": "\u03c7",
    "Sigma": "\u03a3", "Pi": "\u03a0", "Phi": "\u03a6", "Omega": "\u03a9",
    "Delta": "\u0394", "Gamma": "\u0393", "Theta": "\u0398", "Lambda": "\u039b",
    "sum": "\u2211", "prod": "\u220f", "sqrt": "\u221a", "in": "\u2208",
    "notin": "\u2209", "le": "\u2264", "ge": "\u2265", "ne": "\u2260",
    "approx": "\u2248", "to": "\u2192", "gets": "\u2190", "Rightarrow": "\u21d2",
    "times": "\u00d7", "cdot": "\u22c5", "infty": "\u221e", "partial": "\u2202",
    "int": "\u222b", "pm": "\u00b1", "cup": "\u222a", "cap": "\u2229",
    "emptyset": "\u2205", "subset": "\u2282", "subseteq": "\u2286",
    "forall": "\u2200", "exists": "\u2203", "propto": "\u221d",
    "leftrightarrow": "\u2194", "uparrow": "\u2191", "downarrow": "\u2193",
    "cong": "\u2245",
}


def parse(markup, base_font="Helvetica", size=6.0):
    """Return a run list. base_font toggled by * markers to its bold variant."""
    bold_font = "Helvetica-Bold"
    norm_font = base_font
    runs = []
    i = 0
    n = len(markup)
    cur_font = norm_font
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            runs.append(("t", buf, cur_font, size))
            buf = ""

    while i < n:
        c = markup[i]
        if c == "*":
            flush()
            cur_font = bold_font if cur_font == norm_font else norm_font
            i += 1
            continue
        if c == "\\":
            # read token name
            j = i + 1
            name = ""
            while j < n and (markup[j].isalpha()):
                name += markup[j]; j += 1
            if name in TOKENS:
                flush()
                runs.append(("sym", TOKENS[name], size))
                i = j
                continue
            else:
                buf += "\\"
                i += 1
                continue
        if c == "^" or c == "_":
            flush()
            kind = "sup" if c == "^" else "sub"
            i += 1
            if i < n and markup[i] == "{":
                j = markup.index("}", i)
                content = markup[i+1:j]
                i = j + 1
            else:
                content = markup[i] if i < n else ""
                i += 1
            # superscript/subscript may itself contain a sym token (single)
            if content.startswith("\\"):
                nm = content[1:]
                if nm in TOKENS:
                    # approximate: draw as small sym via a sym token at reduced size
                    runs.append(("sym", TOKENS[nm], size * 0.72))
                    continue
            runs.append((kind, content, cur_font, size))
            continue
        buf += c
        i += 1
    flush()
    return runs


class Column:
    def __init__(self, pdf, x, top, width, bottom):
        self.pdf = pdf
        self.x = x
        self.top = top
        self.width = width
        self.bottom = bottom
        self.y = top
        self.overflow = False

    def space(self, dy):
        self.y -= dy

    def _fits(self, dy):
        return (self.y - dy) >= self.bottom

    def section(self, title, size=6.8):
        # shaded bar with bold title
        h = size + 2.2
        if not self._fits(h + 1):
            self.overflow = True
        self.pdf.rect_fill(self.x, self.y - h + 1.5, self.width, h, gray=0.82)
        self.pdf.text(self.x + 1.5, self.y - size + 1.2, title, "Helvetica-Bold", size)
        self.y -= (h + 1.0)

    def subhead(self, markup, size=5.8):
        runs = parse(markup, "Helvetica-Bold", size)
        self._emit_lines(runs, size, lead=size + 1.2, indent=0, color=None)

    def formula(self, markup, size=7.5, lead=None):
        """Formulas: rendered bold at 7.5pt by default."""
        runs = parse(markup, "Helvetica-Bold", size)
        if lead is None:
            lead = size + 1.6
        self._emit_lines(runs, size, lead=lead, indent=0)

    def body(self, markup, size=5.6, indent=0, lead=None):
        runs = parse(markup, "Helvetica", size)
        if lead is None:
            lead = size + 1.3
        self._emit_lines(runs, size, lead=lead, indent=indent)

    def symdef(self, sym_markup, definition, size=5.6):
        """Bold-symbol-only line: '<bold sym>: definition' one per line."""
        runs = parse("*" + sym_markup + "*", "Helvetica", size)
        runs += [("t", ": ", "Helvetica", size)]
        runs += parse(definition, "Helvetica", size)
        self._emit_lines(runs, size, lead=size + 1.2, indent=0, hang=True)

    def bullet(self, markup, size=5.6):
        runs = [("t", "\u2022 ", "Helvetica", size)] + parse(markup, "Helvetica", size)
        self._emit_lines(runs, size, lead=size + 1.2, indent=0, hang=True)

    def _emit_lines(self, runs, size, lead, indent=0, hang=False, color=None):
        maxw = self.width - indent
        lines = pdfdoc.wrap_runs(runs, maxw)
        for k, ln in enumerate(lines):
            if not self._fits(lead):
                self.overflow = True
            xoff = indent
            if hang and k > 0:
                xoff = indent + 7.0
            self.pdf.draw_runs(self.x + xoff, self.y - size, ln)
            self.y -= lead

    def fill_ratio(self):
        return (self.top - self.y) / (self.top - self.bottom)
