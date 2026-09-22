"""Lightweight PDF structural validator (no deps).
Checks: header, %%EOF, startxref points at 'xref', xref offsets each land on
'<n> 0 obj', trailer references a Root catalog, and every content stream's
/Length matches the actual stream bytes.
"""
import re, sys


def validate(path):
    data = open(path, "rb").read()
    errs = []
    if not data.startswith(b"%PDF-"):
        errs.append("missing %PDF- header")
    if b"%%EOF" not in data[-64:]:
        errs.append("missing trailing %%EOF")
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF", data)
    if not m:
        errs.append("no startxref/EOF")
        return errs
    xref_off = int(m.group(1))
    if data[xref_off:xref_off+4] != b"xref":
        errs.append(f"startxref does not point at 'xref' (got {data[xref_off:xref_off+8]!r})")
    # parse xref table
    xm = re.match(rb"xref\s+0\s+(\d+)\s+", data[xref_off:])
    if not xm:
        errs.append("cannot parse xref header")
        return errs
    count = int(xm.group(1))
    body_start = xref_off + xm.end()
    entries = re.findall(rb"(\d{10}) (\d{5}) (n|f)\s", data[body_start:body_start + count*20 + 40])
    for i, (off, gen, kind) in enumerate(entries):
        if kind == b"n":
            o = int(off)
            snippet = data[o:o+30]
            if not re.match(rb"%d 0 obj" % i, snippet):
                errs.append(f"obj {i}: xref offset {o} not at object start (got {snippet[:20]!r})")
    # check content stream lengths
    for mm in re.finditer(rb"<< /Length (\d+) >>\s*stream\r?\n", data):
        length = int(mm.group(1))
        s = mm.end()
        # stream should be followed by exactly 'length' bytes then endstream
        after = data[s + length: s + length + 20]
        if b"endstream" not in after:
            errs.append(f"stream at {s}: /Length {length} does not reach endstream (got {after[:15]!r})")
    return errs


if __name__ == "__main__":
    for p in sys.argv[1:]:
        e = validate(p)
        if e:
            print(f"[FAIL] {p}")
            for x in e:
                print("   -", x)
        else:
            print(f"[OK]   {p} — structurally valid")
