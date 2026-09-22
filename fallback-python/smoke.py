import pdfdoc, layout

# A4 landscape points: 842 x 595
W, H = 842.0, 595.0
pdf = pdfdoc.PDF(W, H)
pdf.new_page()
margin = 14
gap = 6
ncol = 5
usable = W - 2 * margin - (ncol - 1) * gap
colw = usable / ncol
top = H - margin
bottom = margin
cols = []
for i in range(ncol):
    x = margin + i * (colw + gap)
    cols.append(layout.Column(pdf, x, top, colw, bottom))

c = cols[0]
c.section("TEST: Probability")
c.formula("E[aX+bY]=aE[X]+bE[Y]")
c.formula("Var(X)=E[X^2]-(E[X])^2")
c.body("Law of total expectation for a partition of the sample space:")
c.formula("E[X]=\\sum_i E[X|A_i]P(A_i)")
c.symdef("\\pi_0", "initial distribution row vector over the state space, entries sum to one")
c.symdef("P", "one-step transition matrix, row-stochastic")
c.subhead("Gambler's ruin (p\\ne q):")
c.formula("u_i=(1-(q/p)^i)/(1-(q/p)^N)")
c.bullet("Wrapping check: this is a longer explanatory sentence meant to exceed the column width so we can confirm greedy word wrap and hanging indent both function correctly.")
c.body("Greek row: \\alpha \\beta \\gamma \\lambda \\mu \\sigma^2 \\phi \\theta with \\le \\ge \\ne \\to \\Rightarrow \\sum \\sqrt{n} \\infty")

print("col0 fill ratio = %.3f overflow=%s" % (c.fill_ratio(), c.overflow))
n = pdf.save("/projects/sandbox/work/out/smoke.pdf")
print("objects:", n)
