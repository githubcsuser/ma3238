"""Minimal zero-dependency PDF writer + column layout engine.

Coordinate system: PDF points, origin bottom-left. We work top-down internally
by tracking a 'cursor y' from the top of the column.

Fonts: base-14 (Helvetica, Helvetica-Bold, Helvetica-Oblique, Times-Roman,
Times-Bold, Times-Italic, Symbol). Symbol used for Greek/math glyphs.

Rich text: a "run list" is a list of tokens:
    ("t", text, font, size)                 normal text in a font
    ("sym", text, size)                      text rendered in Symbol font
    ("sup", text, font, size)                superscript (drawn smaller, raised)
    ("sub", text, font, size)                subscript (drawn smaller, lowered)
We measure and wrap runs to a max width, then draw them.
"""
import metrics

# ---- font registry: map logical name -> (pdf base font, width map, spacewidth)
_TEXT_FONTS = {}
for _fn in ["Helvetica", "Helvetica-Bold", "Helvetica-Oblique",
            "Times-Roman", "Times-Bold", "Times-Italic"]:
    _m, _sp = metrics.build_unicode_width_map(_fn)
    _TEXT_FONTS[_fn] = (_m, _sp)
_SYM_MAP = metrics.build_symbol_width_map()

# PDF font resource names
FONT_RES = {
    "Helvetica": "F1", "Helvetica-Bold": "F2", "Helvetica-Oblique": "F3",
    "Times-Roman": "F4", "Times-Bold": "F5", "Times-Italic": "F6",
    "Symbol": "FS",
}
FONT_PSNAME = {
    "Helvetica": "Helvetica", "Helvetica-Bold": "Helvetica-Bold",
    "Helvetica-Oblique": "Helvetica-Oblique", "Times-Roman": "Times-Roman",
    "Times-Bold": "Times-Bold", "Times-Italic": "Times-Italic",
    "Symbol": "Symbol",
}

# Symbol font uses StandardEncoding-ish; but for drawing we must output the
# byte code that Symbol maps to the glyph. Build unicode->symbol-bytecode.
_SYM_UNI_TO_CODE = {}
_symw = metrics.font_widths("Symbol")
# groff S file gives psname->width but not code; we need the Adobe Symbol
# encoding code points. Provide the essential mapping (Adobe Symbol encoding).
SYMBOL_ENCODING = {
    "\u03b1": 0x61, "\u03b2": 0x62, "\u03b3": 0x67, "\u03b4": 0x64,
    "\u03b5": 0x65, "\u03b6": 0x7a, "\u03b7": 0x68, "\u03b8": 0x71,
    "\u03b9": 0x69, "\u03ba": 0x6b, "\u03bb": 0x6c, "\u03bc": 0x6d,
    "\u03bd": 0x6e, "\u03be": 0x78, "\u03bf": 0x6f, "\u03c0": 0x70,
    "\u03c1": 0x72, "\u03c3": 0x73, "\u03c4": 0x74, "\u03c5": 0x75,
    "\u03c6": 0x66, "\u03d5": 0x6a, "\u03c7": 0x63, "\u03c8": 0x79,
    "\u03c9": 0x77,
    "\u0393": 0x47, "\u0394": 0x44, "\u0398": 0x51, "\u039b": 0x4c,
    "\u039e": 0x58, "\u03a0": 0x50, "\u03a3": 0x53, "\u03a6": 0x46,
    "\u03a8": 0x59, "\u03a9": 0x57,
    "\u2264": 0xa3, "\u2265": 0xb3, "\u2260": 0xb9, "\u2248": 0xbb,
    "\u2208": 0xce, "\u2209": 0xcf, "\u2211": 0xe5, "\u220f": 0xd5,
    "\u221a": 0xd6, "\u221e": 0xa5, "\u2202": 0xb6, "\u222b": 0xf2,
    "\u2192": 0xae, "\u2190": 0xac, "\u2194": 0xab, "\u21d2": 0xde,
    "\u00d7": 0xb4, "\u2212": 0x2d, "\u22c5": 0xd7, "\u2219": 0xd7,
    "\u222a": 0xc8, "\u2229": 0xc7, "\u2227": 0xd9, "\u2228": 0xda,
    "\u2282": 0xcc, "\u2286": 0xcd, "\u2205": 0xc6, "\u2203": 0x24,
    "\u2200": 0x22, "\u2220": 0xd0, "\u2245": 0x40, "\u221d": 0xb5,
    "\u2191": 0xad, "\u2193": 0xaf, "\u00b1": 0xb1, "\u0192": 0xa6,
    "\u00b7": 0xd7,
}
# Symbol widths keyed by unicode:
SYM_W = metrics.build_symbol_width_map()

# Unicode -> WinAnsiEncoding byte code, for the non-ASCII glyphs we emit in
# text (Helvetica/Times) fonts.
_WINANSI = {
    "\u2018": 0x91, "\u2019": 0x92, "\u201c": 0x93, "\u201d": 0x94,
    "\u2022": 0x95, "\u2013": 0x96, "\u2014": 0x97, "\u2212": 0x2d,
    "\u00b7": 0xb7, "\u00d7": 0xd7, "\u00f7": 0xf7, "\u00b0": 0xb0,
    "\u00b1": 0xb1, "\u00b2": 0xb2, "\u00b3": 0xb3, "\u00bd": 0xbd,
    "\u00bc": 0xbc, "\u00be": 0xbe, "\u00a0": 0x20,
}


def sym_width(ch):
    return SYM_W.get(ch, 549)


def char_width(ch, font, size):
    m, sp = _TEXT_FONTS[font]
    if ch == " ":
        w = sp
    else:
        w = m.get(ch)
        if w is None:
            # fallback: treat unknown as average
            w = m.get("n", 500)
    return w * size / 1000.0


def sym_char_width(ch, size):
    return sym_width(ch) * size / 1000.0


# ---------- Run measurement ----------
def measure_run_token(tok):
    kind = tok[0]
    if kind == "t":
        _, text, font, size = tok
        return sum(char_width(c, font, size) for c in text)
    if kind == "sym":
        _, text, size = tok
        return sum(sym_char_width(c, size) for c in text)
    if kind in ("sup", "sub"):
        _, text, font, size = tok
        ssize = size * 0.72
        return sum(char_width(c, font, ssize) for c in text)
    return 0.0


def measure_runs(runs):
    return sum(measure_run_token(t) for t in runs)


def _split_token_words(tok):
    """Split a text/sym token into word-level sub-tokens for wrapping,
    keeping trailing spaces attached (space becomes its own breakable gap)."""
    kind = tok[0]
    if kind == "t":
        _, text, font, size = tok
        out = []
        cur = ""
        for c in text:
            if c == " ":
                if cur:
                    out.append(("t", cur, font, size)); cur = ""
                out.append(("sp", " ", font, size))
            else:
                cur += c
        if cur:
            out.append(("t", cur, font, size))
        return out
    return [tok]


def wrap_runs(runs, maxwidth):
    """Greedy word-wrap a run list into lines (each a run list).
    Break only at spaces (sp tokens); sym/sup/sub stay glued to neighbors."""
    # Flatten into atoms; group non-space atoms between spaces into words.
    atoms = []
    for tok in runs:
        atoms.extend(_split_token_words(tok))
    lines = []
    cur = []
    curw = 0.0
    i = 0
    # Build words: a word is a maximal run of atoms with no 'sp'
    words = []
    word = []
    for a in atoms:
        if a[0] == "sp":
            if word:
                words.append(word); word = []
            words.append([a])  # space as its own unit
        else:
            word.append(a)
    if word:
        words.append(word)

    def wwidth(w):
        s = 0.0
        for a in w:
            if a[0] == "sp":
                s += char_width(" ", a[2], a[3])
            else:
                s += measure_run_token(a)
        return s

    for w in words:
        ww = wwidth(w)
        is_space = (len(w) == 1 and w[0][0] == "sp")
        if cur and curw + ww > maxwidth and not is_space:
            lines.append(cur)
            cur = []
            curw = 0.0
        if is_space and not cur:
            continue  # skip leading space
        cur.extend(a if a[0] != "sp" else ("t", " ", a[2], a[3]) for a in w)
        curw += ww
    if cur:
        lines.append(cur)
    return lines


# ---------- PDF document ----------
class PDF:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pages = []          # list of content byte strings
        self._buf = []           # current page ops

    def new_page(self):
        if self._buf is not None and self.pages is not None:
            pass
        self._buf = []
        self.pages.append(self._buf)

    def _esc(self, s):
        # Map unicode -> WinAnsi byte codes, escaping PDF string specials.
        out = []
        for ch in s:
            code = _WINANSI.get(ch)
            if code is None:
                o = ord(ch)
                code = o if o < 256 else ord("?")
            if code in (0x28, 0x29, 0x5c):  # ( ) \
                out.append("\\" + chr(code))
            elif 32 <= code < 127:
                out.append(chr(code))
            else:
                out.append("\\%03o" % code)
        return "".join(out)

    def text(self, x, y, s, font, size):
        """Draw a single-font ASCII/latin string at (x,y) baseline."""
        res = FONT_RES[font]
        self._buf.append(
            f"BT /{res} {size:.2f} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({self._esc(s)}) Tj ET"
        )

    def text_sym(self, x, y, s, size):
        res = FONT_RES["Symbol"]
        # encode chars to symbol byte codes
        out = []
        for c in s:
            code = SYMBOL_ENCODING.get(c)
            if code is None:
                out.append("?")
            else:
                out.append(f"\\{code:03o}")
        enc = "".join(out)
        self._buf.append(
            f"BT /{res} {size:.2f} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({enc}) Tj ET"
        )

    def draw_runs(self, x, y, runs):
        """Draw a run list on baseline y starting at x. Returns end x."""
        cx = x
        for tok in runs:
            kind = tok[0]
            if kind == "t":
                _, text, font, size = tok
                self.text(cx, y, text, font, size)
                cx += sum(char_width(c, font, size) for c in text)
            elif kind == "sym":
                _, text, size = tok
                self.text_sym(cx, y, text, size)
                cx += sum(sym_char_width(c, size) for c in text)
            elif kind == "sup":
                _, text, font, size = tok
                ss = size * 0.72
                self.text(cx, y + size * 0.34, text, font, ss)
                cx += sum(char_width(c, font, ss) for c in text)
            elif kind == "sub":
                _, text, font, size = tok
                ss = size * 0.72
                self.text(cx, y - size * 0.16, text, font, ss)
                cx += sum(char_width(c, font, ss) for c in text)
        return cx

    def line(self, x1, y1, x2, y2, w=0.4, gray=0.0):
        self._buf.append(f"{gray:.2f} G {w:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S 0 G")

    def rect_fill(self, x, y, w, h, gray=0.9):
        self._buf.append(f"{gray:.2f} g {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f 0 g")

    def save(self, path):
        out = bytearray()
        def w(b):
            out.extend(b.encode("latin-1") if isinstance(b, str) else b)
        w("%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}
        nobj = 0
        def start(n):
            offsets[n] = len(out)
        # Object numbering:
        # 1 catalog, 2 pages, then per page: page obj + content obj, then fonts.
        npages = len(self.pages)
        page_obj_ids = []
        content_obj_ids = []
        oid = 3
        for _ in range(npages):
            page_obj_ids.append(oid); oid += 1
            content_obj_ids.append(oid); oid += 1
        font_ids = {}
        for logical in FONT_RES:
            font_ids[logical] = oid; oid += 1
        total = oid - 1

        start(1); w(f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        kids = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
        start(2); w(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {npages} >>\nendobj\n")
        fontres = " ".join(f"/{FONT_RES[l]} {font_ids[l]} 0 R" for l in FONT_RES)
        for i in range(npages):
            pid = page_obj_ids[i]; cid = content_obj_ids[i]
            start(pid)
            w(f"{pid} 0 obj\n<< /Type /Page /Parent 2 0 R "
              f"/MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
              f"/Resources << /Font << {fontres} >> >> "
              f"/Contents {cid} 0 R >>\nendobj\n")
            content = "\n".join(self.pages[i]).encode("latin-1")
            start(cid)
            w(f"{cid} 0 obj\n<< /Length {len(content)} >>\nstream\n")
            out.extend(content)
            w("\nendstream\nendobj\n")
        for logical, fid in font_ids.items():
            ps = FONT_PSNAME[logical]
            start(fid)
            if logical == "Symbol":
                w(f"{fid} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Symbol >>\nendobj\n")
            else:
                w(f"{fid} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /{ps} "
                  f"/Encoding /WinAnsiEncoding >>\nendobj\n")
        xref = len(out)
        w(f"xref\n0 {total+1}\n0000000000 65535 f \n")
        for n in range(1, total + 1):
            w(f"{offsets[n]:010d} 00000 n \n")
        w(f"trailer\n<< /Size {total+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n")
        with open(path, "wb") as f:
            f.write(out)
        return total
