"""ST3236 / MA3238 Stochastic Processes I - Midterm cheatsheet.
2-page A4 landscape, 5 columns/page. Exam-applied formulas & procedures only
(Lectures 1-5 + Tutorials 1-5 + Branching Processes deck).

Formulas: bold 7.5pt (layout.Column.formula). Body: 5.6pt (>=5.5). Symbol-defs
one per line with bold symbol only.
"""
import pdfdoc, layout

W, H = 842.0, 595.0
MARGIN = 13
GAP = 5
NCOL = 5

FS_FORM = 8.0     # formula size (bold)
FS_BODY = 5.8     # body size (>=5.5)
FS_SEC = 7.4      # section header
FS_SUB = 6.4      # subhead


def make_page(pdf):
    pdf.new_page()
    usable = W - 2 * MARGIN - (NCOL - 1) * GAP
    colw = usable / NCOL
    top = H - MARGIN
    bottom = MARGIN
    cols = []
    for i in range(NCOL):
        x = MARGIN + i * (colw + GAP)
        cols.append(layout.Column(pdf, x, top, colw, bottom))
    return cols


def build():
    pdf = pdfdoc.PDF(W, H)
    all_cols = []

    # ============================ PAGE 1 ============================
    cols = make_page(pdf)
    all_cols.append(cols)

    # ---------------- Column 1: Probability review ----------------
    c = cols[0]
    c.section("1. PROBABILITY TOOLKIT", FS_SEC)
    c.subhead("Conditioning & Bayes", FS_SUB)
    c.formula("P(A|B)=P(A\\cap B)/P(B)", FS_FORM)
    c.formula("P(A\\cap B)=P(A|B)P(B)", FS_FORM)
    c.body("Total probability, partition {B_i}:", FS_BODY)
    c.formula("P(A)=\\sum_i P(A|B_i)P(B_i)", FS_FORM)
    c.body("Bayes (invert the conditioning):", FS_BODY)
    c.formula("P(B_k|A)=P(A|B_k)P(B_k)/\\sum_i P(A|B_i)P(B_i)", FS_FORM)
    c.body("Independence: P(A\\cap B)=P(A)P(B).", FS_BODY)

    c.subhead("Expectation & variance", FS_SUB)
    c.formula("E[aX+bY]=aE[X]+bE[Y]", FS_FORM)
    c.formula("Var(X)=E[X^2]-(E[X])^2", FS_FORM)
    c.formula("Var(aX+b)=a^2 Var(X)", FS_FORM)
    c.body("Independent X,Y: E[XY]=E[X]E[Y] and Var(X+Y)=Var(X)+Var(Y).", FS_BODY)
    c.formula("Cov(X,Y)=E[XY]-E[X]E[Y]", FS_FORM)
    c.formula("E[1_A]=P(A)", FS_FORM)
    c.body("Linearity needs no independence. Independent variables have Cov=0 and E[XY]=E[X]E[Y]; zero covariance alone does not imply independence.", FS_BODY)
    c.subhead("Indicators", FS_SUB)
    c.formula("1_{A^c}=1-1_A,  1_{A\\cap B}=1_A1_B", FS_FORM)
    c.body("Use indicators to count visits, successes, or event occurrences; sum them and take expectations.", FS_BODY)

    c.subhead("Common distributions", FS_SUB)
    c.symdef("Bernoulli(p)", "mean p, var p(1-p)", FS_BODY)
    c.symdef("Binomial(n,p)", "mean np, var np(1-p)", FS_BODY)
    c.symdef("Geometric(p)", "P(X=k)=(1-p)^{k-1}p, k\\ge1; mean 1/p, var (1-p)/p^2", FS_BODY)
    c.symdef("Poisson(\\lambda)", "P=e^{-\\lambda}\\lambda^k/k!; mean=var=\\lambda", FS_BODY)

    # ---------------- Column 2: Conditional expectation + gen fns ----
    c = cols[1]
    c.section("2. COND. EXPECTATION", FS_SEC)
    c.body("E[X|Y]=g(Y) is a random variable (function of Y).", FS_BODY)
    c.subhead("Tower / total expectation", FS_SUB)
    c.formula("E[X]=E[ E[X|Y] ]", FS_FORM)
    c.formula("E[X]=\\sum_y E[X|Y=y]P(Y=y)", FS_FORM)
    c.subhead("Law of total variance", FS_SUB)
    c.formula("Var(X)=E[Var(X|Y)]+Var(E[X|Y])", FS_FORM)
    c.subhead("Useful identities", FS_SUB)
    c.formula("E[Xg(Y)|Y]=g(Y)E[X|Y]", FS_FORM)
    c.body("Take known functions of Y outside the conditional.", FS_BODY)

    c.section("3. RANDOM SUMS", FS_SEC)
    c.body("N random count, X_i iid, independent of N. S_N=X_1+...+X_N.", FS_BODY)
    c.formula("E[S_N]=E[N]E[X]", FS_FORM)
    c.formula("Var(S_N)=E[N]Var(X)+Var(N)(E[X])^2", FS_FORM)
    c.body("Derive by conditioning on N (tower + total variance).", FS_BODY)

    c.section("4. GEN. FUNCTIONS (PGF)", FS_SEC)
    c.body("For N-valued X:", FS_BODY)
    c.formula("\\phi(s)=E[s^X]=\\sum_k P(X=k)s^k", FS_FORM)
    c.body("Recover moments at s=1:", FS_BODY)
    c.formula("E[X]=\\phi'(1)", FS_FORM)
    c.formula("Var(X)=\\phi''(1)+\\phi'(1)-(\\phi'(1))^2", FS_FORM)
    c.body("Sum of iid: PGF is the product; used in branching.", FS_BODY)
    c.subhead("MGF and random sums", FS_SUB)
    c.formula("M_X(t)=E[e^{tX}],  E[X^k]=M_X^{(k)}(0)", FS_FORM)
    c.formula("M_{aX+b}(t)=e^{bt}M_X(at)", FS_FORM)
    c.body("For independent X,Y, M_{X+Y}=M_XM_Y. For W=sum_{r=1}^N X_r, M_W(t)=M_N(log M_X(t)).", FS_BODY)
    c.formula("E[W]=E[N]E[X],  Var(W)=E[N]Var(X)+Var(N)(E[X])^2", FS_FORM)
    c.body("N is independent of iid summands X_r; W=0 when N=0. PGF moments are at s=1; MGF moments are at t=0.", FS_BODY)

    # ---------------- Column 3: Markov chain definition ----------------
    c = cols[2]
    c.section("5. MARKOV CHAINS: SETUP", FS_SEC)
    c.body("Markov property (memoryless): future depends only on present state.", FS_BODY)
    c.formula("P(X_{n+1}=j | X_n=i, past)=P(X_{n+1}=j|X_n=i)", FS_FORM)
    c.subhead("Show a process is Markov", FS_SUB)
    c.formula("P(X_{n+1}=j|F_n)=P(X_{n+1}=j|X_n)", FS_FORM)
    c.bullet("Specify the state and possible values; condition on a history ending at the same current state i.", FS_BODY)
    c.bullet("Derive the full next-state law and show it depends only on i (and possibly n). Fresh randomness must be independent of the history.", FS_BODY)
    c.body("To disprove Markov, find two positive-probability histories with the same present value but different next-event probabilities. A function of a Markov chain need not be Markov; augment the state with the needed memory.", FS_BODY)
    c.subhead("State, filtration, specification", FS_SUB)
    c.symdef("S", "state space (list of possible states)", FS_BODY)
    c.symdef("\\pi_0", "initial distribution, row vector, entries sum to 1", FS_BODY)
    c.symdef("P", "one-step transition matrix, P_{ij}=P(X_{n+1}=j|X_n=i)", FS_BODY)
    c.body("Each row of P is a distribution: P_{ij}\\ge0, rows sum to 1 (stochastic).", FS_BODY)
    c.symdef("F_n", "information/history available through time n", FS_BODY)
    c.formula("X_{n+1}=g(X_n,\\zeta_{n+1})", FS_FORM)
    c.body("If \\zeta is fresh and independent of the history, then p_{ij}=sum over z with g(i,z)=j of P(\\zeta=z). Enumerate inputs, merge equal destinations, and check boundary rows.", FS_BODY)
    c.subhead("n-step transitions", FS_SUB)
    c.formula("P^{(n)}_{ij}=P(X_n=j|X_0=i)=(P^n)_{ij}", FS_FORM)
    c.subhead("Chapman-Kolmogorov", FS_SUB)
    c.formula("P^{(m+n)}_{ij}=\\sum_k P^{(m)}_{ik}P^{(n)}_{kj}", FS_FORM)
    c.formula("P^{(m+n)}=P^{(m)}P^{(n)}", FS_FORM)
    c.subhead("Distribution at time n", FS_SUB)
    c.formula("\\pi_n=\\pi_0 P^n", FS_FORM)
    c.formula("P(X_n=j)=\\sum_i \\pi_0(i)(P^n)_{ij}", FS_FORM)
    c.formula("\\pi_b=\\pi_a P^{a,b},  P^{a,b}=P^{a,a+1}...P^{b-1,b}", FS_FORM)
    c.body("For time-dependent rules multiply matrices chronologically; do not replace them by one fixed power.", FS_BODY)

    # ---------------- Column 4: Path prob + past inference ----------------
    c = cols[3]
    c.section("6. PATHS & INFERENCE", FS_SEC)
    c.subhead("Joint path probability", FS_SUB)
    c.body("Multiply start prob by successive one-step probs:", FS_BODY)
    c.formula("P(X_0=i_0,...,X_n=i_n)=\\pi_0(i_0) P_{i_0 i_1} ... P_{i_{n-1} i_n}", FS_FORM)
    c.formula("P(X_{t_0}=i_0,...,X_{t_r}=i_r)=\\pi_{t_0}(i_0)\\prod_l p_{i_{l-1}i_l}^{(t_l-t_{l-1})}", FS_FORM)
    c.body("Use one-step factors for consecutive times and matrix powers for gaps; sum over unspecified states.", FS_BODY)
    c.subhead("Bridge / intermediate state", FS_SUB)
    c.formula("P(X_t=k|X_a=i,X_b=j)=p_{ik}^{(t-a)}p_{kj}^{(b-t)}/p_{ij}^{(b-a)}", FS_FORM)
    c.body("For a<t<b and positive denominator, weight the possible middle state by evidence from both endpoints; the answers must sum to 1.", FS_BODY)
    c.subhead("Inferring the past (Bayes)", FS_SUB)
    c.body("To find P(X_0=i | X_n=j) use Bayes with forward probs:", FS_BODY)
    c.formula("P(X_0=i|X_n=j)=\\pi_0(i)(P^n)_{ij} / \\sum_k \\pi_0(k)(P^n)_{kj}", FS_FORM)
    c.body("Numerator: prob of that start AND the observation. Denominator: total prob of the observation.", FS_BODY)

    c.subhead("Time to hit / general recipe", FS_SUB)
    c.bullet("Condition on the first step (see first-step analysis).", FS_BODY)
    c.bullet("For 'ever reach' or 'reach before': set up linear equations in the unknown probabilities.", FS_BODY)
    c.bullet("Absorbing states give boundary conditions.", FS_BODY)

    # ---------------- Column 5: HMM filtering ----------------
    c = cols[4]
    c.section("7. HIDDEN MARKOV (FILTER)", FS_SEC)
    c.body("Hidden chain X_n (matrix P), observations Y_n with emission P(Y|X)=e_{x}(y). Track belief \\pi_n(i)=P(X_n=i | Y_{1..n}).", FS_BODY)
    c.subhead("Predict (time update)", FS_SUB)
    c.formula("pred(j)=\\sum_i \\pi_{n-1}(i)P_{ij}", FS_FORM)
    c.subhead("Update (observation Y_n=y)", FS_SUB)
    c.formula("\\pi_n(j)\\propto pred(j) e_j(y)", FS_FORM)
    c.formula("\\pi_n(j)=pred(j)e_j(y)/\\sum_k pred(k)e_k(y)", FS_FORM)
    c.body("Then normalize so \\pi_n sums to 1. Repeat predict-update per observation.", FS_BODY)
    c.subhead("Prediction of next / obs", FS_SUB)
    c.formula("P(X_{n+1}=j|Y_{1..n})=\\sum_i \\pi_n(i)P_{ij}", FS_FORM)
    c.formula("P(Y_{n+1}=y|Y_{1..n})=\\sum_j pred_{n+1}(j)e_j(y)", FS_FORM)
    c.subhead("HMM path probability", FS_SUB)
    c.formula("w(x_{0:m})=\\pi_0(x_0)b_{x_0}(y_0)\\prod_{r=1}^m p_{x_{r-1}x_r}b_{x_r}(y_r)", FS_FORM)
    c.body("To smooth a hidden past, sum w over paths with the requested hidden state and divide by the sum over all paths. This is a posterior, not an unnormalised joint probability.", FS_BODY)

    c.section("7b. STATIONARY DIST.", FS_SEC)
    c.body("A distribution \\pi (row vector) is stationary if it is unchanged by one step:", FS_BODY)
    c.formula("\\pi P=\\pi ,   \\sum_i \\pi_i=1", FS_FORM)
    c.body("Solve the linear system (drop one balance equation, use normalization). For irreducible aperiodic chains \\pi_n\\to\\pi as n\\to\\infty regardless of \\pi_0.", FS_BODY)
    c.body("2-state chain P=[[1-a,a],[b,1-b]]:", FS_BODY)
    c.formula("\\pi=(b/(a+b), a/(a+b))", FS_FORM)
    c.subhead("Worked filter step", FS_SUB)
    c.body("P=[[.7,.3],[.4,.6]], emit e_0=(.9,.1) e_1=(.2,.8), \\pi_0=(.5,.5). Obs y=0 \\to \\pi=(.846,.154).", FS_BODY)

    # ============================ PAGE 2 ============================
    cols = make_page(pdf)
    all_cols.append(cols)

    # ---------------- Column 1: Standard models ----------------
    c = cols[0]
    c.section("8. STANDARD MODELS", FS_SEC)
    c.subhead("Random walk", FS_SUB)
    c.body("Steps Z_i=+1 w.p. p, -1 w.p. q=1-p. S_n=S_0+Z_1+...+Z_n.", FS_BODY)
    c.formula("E[S_n]=S_0+n(p-q)", FS_FORM)
    c.formula("Var(S_n)=n(1-(p-q)^2)=4npq", FS_FORM)
    c.body("Position after n steps with R rights: S_n=S_0+2R-n, R~Bin(n,p).", FS_BODY)
    c.formula("P(S_n=S_0+2r-n)=C(n,r)p^r q^{n-r}", FS_FORM)

    c.subhead("Inventory (s,S) model", FS_SUB)
    c.body("Restock to S when stock \\le s; demand D_n iid.", FS_BODY)
    c.formula("X_{n+1}=max(X_n-D_{n+1},0) then reorder rule", FS_FORM)
    c.body("Build P from demand distribution; state = stock level.", FS_BODY)

    c.subhead("Queue model", FS_SUB)
    c.body("X_n = customers in system. Arrivals A_n iid, one served per step:", FS_BODY)
    c.formula("X_{n+1}=max(X_n-1,0)+A_{n+1}", FS_FORM)
    c.body("For capacity N with independent arrival probability \\lambda and service probability \\mu: interior p_{i,i+1}=\\lambda(1-\\mu), p_{i,i-1}=(1-\\lambda)\\mu, p_{ii}=\\lambda\\mu+(1-\\lambda)(1-\\mu); boundaries p_{01}=\\lambda and p_{N,N-1}=\\mu.", FS_BODY)
    c.subhead("Colour-flipping urn", FS_SUB)
    c.formula("p_{i,i-1}=i/N,  p_{i,i+1}=(N-i)/N", FS_FORM)
    c.body("i is the current red-ball count in a fixed population N; boundaries force p_{01}=p_{N,N-1}=1.", FS_BODY)
    c.subhead("General / multidimensional walk", FS_SUB)
    c.formula("E[S_n]=S_0+n\\mu_\\xi,  Var(S_n)=n\\sigma_\\xi^2", FS_FORM)
    c.body("For a simple symmetric walk in d dimensions, each coordinate moves by +/-1 with probability 1/(2d), stays put with probability 1-1/d; E[x_n]=0 and Var(x_n)=n/d.", FS_BODY)

    c.section("8b. STATE CLASSIFICATION", FS_SEC)
    c.symdef("accessible", "j reachable from i: (P^n)_{ij}>0 some n", FS_BODY)
    c.symdef("communicate", "i,j reach each other; classes partition S", FS_BODY)
    c.symdef("irreducible", "one class (all states communicate)", FS_BODY)
    c.symdef("recurrent", "return w.p. 1; else transient", FS_BODY)
    c.symdef("period d", "gcd of return times; d=1 aperiodic", FS_BODY)
    c.symdef("absorbing", "P_{ii}=1 (never leaves state i)", FS_BODY)

    # ---------------- Column 2: First-step analysis ----------------
    c = cols[1]
    c.section("9. FIRST-STEP ANALYSIS", FS_SEC)
    c.body("Absorbing states a (target) and set. Condition on the first move, then solve linear equations.", FS_BODY)
    c.subhead("Hitting probability u_i", FS_SUB)
    c.body("u_i=P(hit target A before B | start i). Boundary: u=1 on A, u=0 on B.", FS_BODY)
    c.formula("u_i=\\sum_j P_{ij} u_j  (i transient)", FS_FORM)
    c.subhead("Expected hitting time v_i", FS_SUB)
    c.body("v_i=E[steps to absorption | start i]. Boundary: v=0 on absorbing states.", FS_BODY)
    c.formula("v_i=1+\\sum_j P_{ij} v_j  (i transient)", FS_FORM)
    c.body("The +1 counts the current step. Solve the linear system for all transient i.", FS_BODY)
    c.subhead("Expected absorption reward", FS_SUB)
    c.formula("w_i=r_i+\\sum_j P_{ij} w_j", FS_FORM)

    # ---------------- Column 3: Gambler's ruin ----------------
    c = cols[2]
    c.section("10. GAMBLER'S RUIN", FS_SEC)
    c.body("On 0..N, absorbing at 0 and N. Up w.p. p, down w.p. q=1-p. u_i=P(reach N before 0 | start i).", FS_BODY)
    c.subhead("Case p \\ne q  (let r=q/p)", FS_SUB)
    c.formula("u_i=(1-r^i)/(1-r^N)", FS_FORM)
    c.subhead("Case p=q=1/2 (fair)", FS_SUB)
    c.formula("u_i=i/N", FS_FORM)
    c.subhead("Prob of ruin (hit 0 first)", FS_SUB)
    c.formula("=1-u_i", FS_FORM)
    c.subhead("Expected duration v_i", FS_SUB)
    c.body("Fair game p=q=1/2:", FS_BODY)
    c.formula("v_i=i(N-i)", FS_FORM)
    c.body("Biased p\\ne q:", FS_BODY)
    c.formula("v_i=i/(q-p) - (N/(q-p))(1-r^i)/(1-r^N)", FS_FORM)
    c.subhead("Worked: p=.4, N=5", FS_SUB)
    c.body("r=q/p=1.5. Reach N before 0: u_1\\approx.076, u_3\\approx.360. Ruin=1-u_i.", FS_BODY)

    # ---------------- Column 4: Stopping times & martingales ----------------
    c = cols[3]
    c.section("11. MARTINGALES", FS_SEC)
    c.body("{M_n} is a martingale if E|M_n|<\\infty and:", FS_BODY)
    c.formula("E[M_{n+1}|M_0..M_n]=M_n", FS_FORM)
    c.body("Then E[M_n]=E[M_0] for all n.", FS_BODY)
    c.subhead("Common constructions", FS_SUB)
    c.body("RW with p=1/2: M_n=S_n is a martingale.", FS_BODY)
    c.formula("M_n=S_n^2-n  (fair RW) is a martingale", FS_FORM)
    c.body("Biased RW: (q/p)^{S_n} is a martingale.", FS_BODY)

    c.section("12. STOPPING TIMES / OST", FS_SEC)
    c.body("T is a stopping time if {T=n} depends only on X_0..X_n (no peeking ahead).", FS_BODY)
    c.subhead("Optional Stopping Theorem", FS_SUB)
    c.formula("E[M_T]=E[M_0]", FS_FORM)
    c.body("Holds if ANY one condition holds:", FS_BODY)
    c.bullet("T is bounded (T\\le c), or", FS_BODY)
    c.bullet("M is bounded and T<\\infty a.s., or", FS_BODY)
    c.bullet("E[T]<\\infty and increments bounded.", FS_BODY)
    c.body("Use: apply E[M_T]=E[M_0] to solve exit probs / expected times.", FS_BODY)

    # ---------------- Column 5: Branching processes ----------------
    c = cols[4]
    c.section("13. BRANCHING (GALTON-WATSON)", FS_SEC)
    c.body("Z_n = size of generation n, Z_0=1. Each individual has iid offspring, PGF \\phi.", FS_BODY)
    c.symdef("X", "offspring count per individual", FS_BODY)
    c.symdef("m", "mean offspring E[X]=\\phi'(1)", FS_BODY)
    c.symdef("\\sigma^2", "offspring variance Var(X)", FS_BODY)
    c.subhead("Generation PGF (compose)", FS_SUB)
    c.formula("\\phi_{n+1}(s)=\\phi_n(\\phi(s))=\\phi(\\phi_n(s))", FS_FORM)
    c.subhead("Moments", FS_SUB)
    c.formula("E[Z_n]=m^n", FS_FORM)
    c.body("Variance (m\\ne1):", FS_BODY)
    c.formula("Var(Z_n)=\\sigma^2 m^{n-1}(m^n-1)/(m-1)", FS_FORM)
    c.body("If m=1: Var(Z_n)=n\\sigma^2.", FS_BODY)
    c.subhead("Extinction prob q", FS_SUB)
    c.body("q = smallest root in [0,1] of:", FS_BODY)
    c.formula("q=\\phi(q)", FS_FORM)
    c.bullet("m\\le1 \\Rightarrow q=1 (certain extinction).", FS_BODY)
    c.bullet("m>1 \\Rightarrow q<1 (survival possible).", FS_BODY)
    c.subhead("Vaccination / thinning", FS_SUB)
    c.body("Vaccinate fraction v: effective mean m'=m(1-v). Outbreak dies if m'\\le1.", FS_BODY)
    c.formula("v^* = 1 - 1/m  (herd-immunity threshold)", FS_FORM)
    c.subhead("Worked: Poisson(m) offspring", FS_SUB)
    c.body("\\phi(s)=e^{m(s-1)}. m=1.5 gives extinction q\\approx0.417, herd v^*=1/3.", FS_BODY)

    n = pdf.save("/projects/sandbox/work/out/cheatsheet.pdf")
    return pdf, all_cols


if __name__ == "__main__":
    pdf, all_cols = build()
    print("built cheatsheet.pdf, pages=", len(pdf.pages))
    for pi, page_cols in enumerate(all_cols):
        for ci, c in enumerate(page_cols):
            flag = "  <<< OVERFLOW" if c.overflow else ""
            print("  page %d col %d: fill=%.2f%s" % (pi + 1, ci + 1, c.fill_ratio(), flag))
