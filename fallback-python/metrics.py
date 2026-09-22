"""Parse groff devps metric files into {psglyphname: width_per_1000em} maps
for the base-14 fonts we use. Also build char->width maps keyed by unicode.

groff metric line format (after the 'charset' line):
    <groffname>\t<width[,h,d,...]>\t<type>\t<code>\t<psname>
or continuation lines like:  dq\t"   (alias of previous)
We only need width (first comma field of field 2) and the psname (last field).
"""
import os

GROFF = "/usr/share/groff/1.22.4/font/devps"

FONT_FILES = {
    "Helvetica": "HR",
    "Helvetica-Bold": "HB",
    "Helvetica-Oblique": "HI",
    "Times-Roman": "TR",
    "Times-Bold": "TB",
    "Times-Italic": "TI",
    "Symbol": "S",
}

# PostScript standard glyph name -> unicode char, for the glyphs we care about.
# (subset; extended as needed)
PS_TO_UNICODE = {
    "space": " ", "exclam": "!", "quotedbl": '"', "numbersign": "#",
    "dollar": "$", "percent": "%", "ampersand": "&", "quotesingle": "'",
    "parenleft": "(", "parenright": ")", "asterisk": "*", "plus": "+",
    "comma": ",", "hyphen": "-", "period": ".", "slash": "/",
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "colon": ":", "semicolon": ";", "less": "<", "equal": "=", "greater": ">",
    "question": "?", "at": "@",
    "bracketleft": "[", "backslash": "\\", "bracketright": "]",
    "asciicircum": "^", "underscore": "_", "grave": "`",
    "braceleft": "{", "bar": "|", "braceright": "}", "asciitilde": "~",
    "quoteleft": "\u2018", "quoteright": "\u2019",
    "quotedblleft": "\u201c", "quotedblright": "\u201d",
    "endash": "\u2013", "emdash": "\u2014", "bullet": "\u2022",
    "periodcentered": "\u00b7", "multiply": "\u00d7", "divide": "\u00f7",
    "minus": "\u2212", "degree": "\u00b0",
}
for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
    PS_TO_UNICODE[c] = c

# Symbol font glyph name -> unicode we intend to render via the Symbol font
SYMBOL_TO_UNICODE = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "epsilon": "\u03b5", "zeta": "\u03b6", "eta": "\u03b7", "theta": "\u03b8",
    "iota": "\u03b9", "kappa": "\u03ba", "lambda": "\u03bb", "mu": "\u03bc",
    "nu": "\u03bd", "xi": "\u03be", "omicron": "\u03bf", "pi": "\u03c0",
    "rho": "\u03c1", "sigma": "\u03c3", "tau": "\u03c4", "upsilon": "\u03c5",
    "phi": "\u03c6", "phi1": "\u03d5", "chi": "\u03c7", "psi": "\u03c8", "omega": "\u03c9",
    "Gamma": "\u0393", "Delta": "\u0394", "Theta": "\u0398", "Lambda": "\u039b",
    "Xi": "\u039e", "Pi": "\u03a0", "Sigma": "\u03a3", "Phi": "\u03a6",
    "Psi": "\u03a8", "Omega": "\u03a9",
    "lessequal": "\u2264", "greaterequal": "\u2265", "notequal": "\u2260",
    "approxequal": "\u2248", "element": "\u2208", "notelement": "\u2209",
    "summation": "\u2211", "product": "\u220f", "radical": "\u221a",
    "infinity": "\u221e", "partialdiff": "\u2202", "integral": "\u222b",
    "arrowright": "\u2192", "arrowleft": "\u2190", "arrowboth": "\u2194",
    "arrowdblright": "\u21d2", "multiply": "\u00d7", "minus": "\u2212",
    "periodcentered": "\u22c5", "bullet": "\u2219", "dotmath": "\u22c5",
    "union": "\u222a", "intersection": "\u2229", "logicaland": "\u2227",
    "logicalor": "\u2228", "propersubset": "\u2282", "reflexsubset": "\u2286",
    "emptyset": "\u2205", "existential": "\u2203", "universal": "\u2200",
    "angle": "\u2220", "congruent": "\u2245", "proportional": "\u221d",
    "arrowup": "\u2191", "arrowdown": "\u2193", "plusminus": "\u00b1",
    "florin": "\u0192",
}


def _parse(path):
    widths = {}
    started = False
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            if not started:
                if line.strip() == "charset":
                    started = True
                continue
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                # alias/continuation line like: dq\t"
                continue
            metric = parts[1]
            psname = parts[-1].strip()
            w = metric.split(",")[0]
            try:
                widths[psname] = int(w)
            except ValueError:
                continue
    return widths


_CACHE = {}


def font_widths(fontname):
    if fontname in _CACHE:
        return _CACHE[fontname]
    path = os.path.join(GROFF, FONT_FILES[fontname])
    _CACHE[fontname] = _parse(path)
    return _CACHE[fontname]


def build_unicode_width_map(fontname):
    """char -> width(1000em) for text fonts."""
    w = font_widths(fontname)
    m = {}
    for ps, ch in PS_TO_UNICODE.items():
        if ps in w:
            m[ch] = w[ps]
    return m, w.get("space", 278)


def build_symbol_width_map():
    w = font_widths("Symbol")
    m = {}
    for ps, ch in SYMBOL_TO_UNICODE.items():
        if ps in w:
            m[ch] = w[ps]
    return m


if __name__ == "__main__":
    for fn in ["Helvetica", "Helvetica-Bold", "Times-Roman", "Times-Bold"]:
        m, sp = build_unicode_width_map(fn)
        print(fn, "glyphs=", len(m), "space=", sp,
              "W(A)=", m.get("A"), "W(i)=", m.get("i"))
    sym = build_symbol_width_map()
    print("Symbol glyphs=", len(sym), "pi=", sym.get("\u03c0"),
          "sum=", sym.get("\u2211"), "<=", sym.get("\u2264"))
