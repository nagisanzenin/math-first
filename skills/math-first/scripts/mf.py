#!/usr/bin/env python3
"""mf.py: Math First's calculator for R0 questions about rates, samples and thresholds.

Stdlib only, no network. Exact rational arithmetic where it is cheap (binomial tails, `needed`, Fisher's exact
power, Bonferroni and Holm); floating point elsewhere, and every answer says which. Every command prints its
assumptions and its source.

  python3 mf.py binom -k 6 -n 30 --conf 0.95            Clopper–Pearson bounds on a rate
  python3 mf.py needed --below 0.10 --conf 0.95 -k 1    trials needed to certify a rate is at most X
  python3 mf.py samplesize props --p1 0.10 --p2 0.20    n per group, two proportions
  python3 mf.py samplesize means --delta 0.5 --sd 1     n per group, two means
  python3 mf.py multi --alpha 0.05 -p 0.01 0.02 0.04    Bonferroni and Holm thresholds
  python3 mf.py cs-bernoulli -k 3 -n 200 --alpha 0.05   anytime-valid confidence sequence for a rate
  python3 mf.py spend --alpha 0.025 --looks 1 2 3       alpha spending per planned look
  python3 mf.py seq-binary --before 20 --looks 10 20 --alpha 0.05 --p0 0.1 --p1 0.3
                                                        exact early-look test for a rate, with detection by look

Add --json before the command for a machine-readable answer (for receipts).
Numbers accept decimals or fractions: 0.95, 19/20, 1e-3.
"""
import argparse
import json
import math
import sys
from fractions import Fraction
from math import comb
from statistics import NormalDist

BISECT_STEPS = 40          # bounds are found to within 2^-40 (about 1e-12) and rounded outward
EXACT_MAX_N = 5000         # above this, binomial tails use log-space floating point
FISHER_EXACT_MAX_N = 1000  # exact power check of Fisher's test is O(n^2); skipped above this


# ---------------------------------------------------------------------------------------------- binomial tails

def _cdf_num_den(k, n, p):
    """P(Bin(n, p) <= k) as an unreduced integer fraction (num, den), exact for rational p."""
    a, b = p.numerator, p.denominator
    q = b - a
    h, c, apow = 0, 1, 1
    for i in range(k + 1):          # Horner: h = sum_i C(n,i) a^i q^(k-i)
        h = h * q + c * apow
        c = c * (n - i) // (i + 1)
        apow *= a
    return h * q ** (n - k), b ** n


def _cdf_float(k, n, p):
    lp, lq, lg = math.log(p), math.log1p(-p), math.lgamma(n + 1)
    terms = [lg - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq for i in range(k + 1)]
    m = max(terms)
    return min(1.0, math.exp(m) * math.fsum(math.exp(t - m) for t in terms))


def cdf_cmp(k, n, p, alpha):
    """Sign of P(Bin(n, p) <= k) - alpha: -1, 0 or 1. Exact when n <= EXACT_MAX_N."""
    p, alpha = Fraction(p), Fraction(alpha)
    if k < 0:
        v = Fraction(0)
    elif k >= n or p == 0:
        v = Fraction(1)
    elif p == 1:
        v = Fraction(0)
    elif n > EXACT_MAX_N:
        f = _cdf_float(k, n, float(p))
        return (f > alpha) - (f < alpha)
    else:
        num, den = _cdf_num_den(k, n, p)
        lhs, rhs = num * alpha.denominator, alpha.numerator * den
        return (lhs > rhs) - (lhs < rhs)
    return (v > alpha) - (v < alpha)


def binom_cdf(k, n, p):
    """P(Bin(n, p) <= k) as a float (computed exactly first when n <= EXACT_MAX_N)."""
    p = Fraction(p)
    if k < 0:
        return 0.0
    if k >= n or p == 0:
        return 1.0
    if p == 1:
        return 0.0
    if n > EXACT_MAX_N:
        return _cdf_float(k, n, float(p))
    num, den = _cdf_num_den(k, n, p)
    return num / den


def cp_upper(k, n, alpha):
    """One-sided Clopper–Pearson upper bound: the p with P(X <= k | p) = alpha. Rounded up."""
    if k >= n:
        return Fraction(1)
    lo, hi = Fraction(0), Fraction(1)
    for _ in range(BISECT_STEPS):
        mid = (lo + hi) / 2
        if cdf_cmp(k, n, mid, alpha) > 0:
            lo = mid
        else:
            hi = mid
    return hi


def cp_lower(k, n, alpha):
    """One-sided Clopper–Pearson lower bound: the p with P(X >= k | p) = alpha. Rounded down."""
    if k <= 0:
        return Fraction(0)
    lo, hi = Fraction(0), Fraction(1)
    one_minus = 1 - Fraction(alpha)          # P(X >= k) < alpha  <=>  P(X <= k-1) > 1 - alpha
    for _ in range(BISECT_STEPS):
        mid = (lo + hi) / 2
        if cdf_cmp(k - 1, n, mid, one_minus) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def needed_n(below, alpha, k, max_n=10 ** 9):
    """Smallest n such that k events in n trials give a one-sided upper bound <= below at level alpha.

    That is the smallest n with P(Bin(n, below) <= k) <= alpha; the tail falls as n grows, so search is exact."""
    def ok(n):
        return cdf_cmp(k, n, below, alpha) <= 0
    hi = k + 1
    while not ok(hi):
        hi *= 2
        if hi > max_n:
            raise ValueError(f'no n <= {max_n}')
    lo = max(k, hi // 2)                       # ok(lo) is false (or lo == k, where the bound is 1)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


# ---------------------------------------------------------------------------------------------- sample size

def _z(prob):
    return NormalDist().inv_cdf(prob)


def n_two_props(p1, p2, alpha, power, sides):
    za, zb = _z(1 - alpha / sides), _z(power)
    pbar = (p1 + p2) / 2
    d = abs(p1 - p2)
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / d ** 2
    ncc = n / 4 * (1 + math.sqrt(1 + 4 / (n * d))) ** 2
    return n, ncc


def fisher_power(n, p1, p2, alpha_one):
    """Exact power of the one-sided Fisher (conditional) test with n per group, at level alpha_one.

    The critical values are found in exact integer arithmetic; the power sum is floating point."""
    if p2 < p1:
        p1, p2 = p2, p1
    a = Fraction(alpha_one)
    c_n = [comb(n, j) for j in range(n + 1)]
    crit = []
    for K in range(2 * n + 1):
        lo, hi = max(0, K - n), min(n, K)
        total = comb(2 * n, K) * a.numerator
        tail, c = 0, hi + 1
        for x2 in range(hi, lo - 1, -1):
            tail += c_n[x2] * c_n[K - x2]
            if tail * a.denominator <= total:
                c = x2
            else:
                break
        crit.append(c)

    def pmf(p):
        if p in (0.0, 1.0):
            return [1.0 if (j == 0) == (p == 0.0) else 0.0 for j in range(n + 1)]
        lg, lp, lq = math.lgamma(n + 1), math.log(p), math.log1p(-p)
        return [math.exp(lg - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq)
                for j in range(n + 1)]
    b1, b2 = pmf(p1), pmf(p2)
    return math.fsum(b1[x1] * b2[x2] for x1 in range(n + 1) for x2 in range(n + 1) if x2 >= crit[x1 + x2])


def n_two_means(delta, sd, alpha, power, sides):
    za, zb = _z(1 - alpha / sides), _z(power)
    nz = 2 * (za + zb) ** 2 * (sd / delta) ** 2
    return nz, nz + za ** 2 / 4


# ---------------------------------------------------------------------------------------------- multiplicity

def holm(pvals, alpha):
    """Holm step-down: returns (order, thresholds, rejected flags, adjusted p) in the input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    rejected, adj = [False] * m, [0.0] * m
    still, running = True, Fraction(0)
    for rank, i in enumerate(order):
        thr = alpha / (m - rank)
        if still and pvals[i] <= thr:
            rejected[i] = True
        else:
            still = False
        running = max(running, min(Fraction(1), (m - rank) * pvals[i]))
        adj[i] = running
    return rejected, adj


# ---------------------------------------------------------------------------------------------- confidence sequence

def _lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def log_mixture_ratio(s, n, p, a=1.0, b=1.0):
    """log M_n(p): the Beta(a, b) mixture likelihood over the Bernoulli likelihood at p.

    Under the true p, M_n(p) is a nonnegative martingale with M_0 = 1, so Ville's inequality gives
    P(exists n: M_n(p) >= 1/alpha) <= alpha."""
    mix = _lbeta(a + s, b + n - s) - _lbeta(a, b)
    if p <= 0.0:
        return math.inf if s > 0 else mix
    if p >= 1.0:
        return math.inf if s < n else mix
    return mix - s * math.log(p) - (n - s) * math.log1p(-p)


def cs_bernoulli(s, n, alpha, a=1.0, b=1.0):
    """The confidence sequence {p : M_n(p) < 1/alpha} at time n, an interval; ends rounded outward."""
    cut = math.log(1 / alpha)
    phat = s / n if n else 0.5

    def inside(p):
        return log_mixture_ratio(s, n, p, a, b) < cut

    if inside(0.0):
        lower = 0.0
    else:
        lo, hi = 0.0, phat
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if inside(mid) else (mid, hi)
        lower = lo
    if inside(1.0):
        upper = 1.0
    else:
        lo, hi = phat, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid) else (lo, mid)
        upper = hi
    return lower, upper


# ---------------------------------------------------------------------------------------------- sequential looks

def spending(alpha, fracs, family):
    """Lan–DeMets cumulative alpha spent at information fractions fracs (one-sided)."""
    nd = NormalDist()
    if family == 'obf':
        z = nd.inv_cdf(1 - alpha / 2)
        return [2 - 2 * nd.cdf(z / math.sqrt(t)) for t in fracs]
    return [alpha * math.log(1 + (math.e - 1) * t) for t in fracs]


def _hyp_tail_count(N, K, n, s):
    """Number of ways (out of C(N, n)) to draw n of N with at least s of the K events: the exact one-sided count."""
    lo, hi = max(0, K - (N - n)), min(n, K)
    return sum(comb(K, j) * comb(N - K, n - j) for j in range(max(s, lo), hi + 1))


def seq_binary(before, looks, alpha, spend, mode):
    """Exact group-sequential one-sided test of a binary rate: after-turns against a fixed baseline.

    Look j (cumulative n_j after-turns) rolls back when the exact (hypergeometric) p-value of the after-sum among the
    before + n_j turns is <= spend[j]. The last look: 'union' uses alpha - sum(spend); 'recycle' rolls back the largest
    after-sums such that, given the pooled event count K, the total rollback mass is <= alpha. Returns a dict with the
    outcome table and per-K thresholds; everything in exact integer arithmetic."""
    alpha = Fraction(alpha)
    spend = [Fraction(a) for a in spend]
    J = len(looks)
    blocks = [looks[0]] + [looks[j] - looks[j - 1] for j in range(1, J)]
    N = before + looks[-1]
    tail = {}

    def p_le(nn, K, n, s, a):                       # exact: count / C(nn, n) <= a
        key = (nn, K, n, s)
        if key not in tail:
            tail[key] = _hyp_tail_count(nn, K, n, s)
        return tail[key] * a.denominator <= a.numerator * comb(nn, n)

    outcomes = []                                    # (b, xs, K, first early look that fires or 0, s_final, weight)
    def rec(j, xs):
        if j == J:
            yield tuple(xs)
            return
        for x in range(blocks[j] + 1):
            xs.append(x)
            yield from rec(j + 1, xs)
            xs.pop()
    for xs in rec(0, []):
        for b in range(before + 1):
            s_cum, fired = 0, 0
            for j in range(J - 1):
                s_cum += xs[j]
                if p_le(before + looks[j], b + s_cum, looks[j], s_cum, spend[j]):
                    fired = j + 1
                    break
            s = sum(xs)
            w = comb(before, b)
            for j, x in enumerate(xs):
                w *= comb(blocks[j], x)
            outcomes.append((b, xs, b + s, fired, s, w))
    final_alpha = alpha - sum(spend)
    by_k = {}
    for o in outcomes:
        by_k.setdefault(o[2], []).append(o)
    thr = {}
    level = Fraction(0)
    spent_max = Fraction(0)
    for K in range(N + 1):
        tot = comb(N, K)
        spent, by_s = 0, {}
        for (b, xs, k, fired, s, w) in by_k.get(K, []):
            if fired:
                spent += w
            else:
                by_s[s] = by_s.get(s, 0) + w
        spent_max = max(spent_max, Fraction(spent, tot))
        if mode == 'recycle':
            budget, t = alpha * tot - spent, looks[-1] + 1
            for s in sorted(by_s, reverse=True):
                if by_s[s] <= budget:
                    budget -= by_s[s]
                    t = s
                else:
                    break
        else:
            t = next((s for s in range(looks[-1] + 1)
                      if p_le(N, K, looks[-1], s, final_alpha) and final_alpha > 0), looks[-1] + 1)
        thr[K] = t
        rej = spent + sum(m for s, m in by_s.items() if s >= t)
        level = max(level, Fraction(rej, tot))
    fixed_thr = {K: next((s for s in range(looks[-1] + 1) if p_le(N, K, looks[-1], s, alpha)), looks[-1] + 1)
                 for K in range(N + 1)}
    fixed_level = max(Fraction(sum(w for (b, xs, k, f, s, w) in by_k.get(K, []) if s >= fixed_thr[K]), comb(N, K))
                      for K in range(N + 1))
    missed = sum(1 for (b, xs, k, fired, s, w) in outcomes if s >= fixed_thr[k] and not fired and s < thr[k])
    fixed_rejects = sum(1 for (b, xs, k, fired, s, w) in outcomes if s >= fixed_thr[k])
    return {'outcomes': outcomes, 'thr': thr, 'fixed_thr': fixed_thr, 'level': level, 'fixed_level': fixed_level,
            'early_spent_max': spent_max, 'missed': missed, 'fixed_rejects': fixed_rejects, 'blocks': blocks}


def seq_binary_power(res, before, looks, p0, p1):
    """P(caught by look j) for j = 1..J, and the same for the fixed final-look test, under iid Bernoulli rates."""
    J = len(looks)

    def pmf(n, p):
        return [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    pb = pmf(before, p0)
    pbl = [pmf(d, p1) for d in res['blocks']]
    by = [0.0] * J
    fixed = 0.0
    for (b, xs, k, fired, s, w) in res['outcomes']:
        pr = pb[b]
        for j, x in enumerate(xs):
            pr *= pbl[j][x]
        if fired:
            by[fired - 1] += pr
        elif s >= res['thr'][k]:
            by[J - 1] += pr
        if s >= res['fixed_thr'][k]:
            fixed += pr
    cum, acc = [], 0.0
    for v in by:
        acc += v
        cum.append(acc)
    exposure = sum(looks[j] * by[j] for j in range(J)) + looks[-1] * (1 - acc)
    return cum, fixed, exposure


# ---------------------------------------------------------------------------------------------- CLI

def pct(x, digits=2):
    return f'{float(x) * 100:.{digits}f} %'


def cmd_binom(a):
    k, n, conf = a.k, a.n, Fraction(a.conf)
    if not 0 <= k <= n or n < 1:
        raise SystemExit('need 0 <= k <= n and n >= 1')
    alpha = 1 - conf
    up1, lo1 = cp_upper(k, n, alpha), cp_lower(k, n, alpha)
    lo2, up2 = cp_lower(k, n, alpha / 2), cp_upper(k, n, alpha / 2)
    exact = n <= EXACT_MAX_N
    lines = [
        f'{k} of {n} = {pct(Fraction(k, n))} observed',
        f'one-sided {pct(conf, 0)} upper bound: {pct(up1)}   (the rate is at most this)',
        f'one-sided {pct(conf, 0)} lower bound: {pct(lo1)}   (the rate is at least this)',
        f'two-sided {pct(conf, 0)} interval:    [{pct(lo2)}, {pct(up2)}]',
    ]
    if k == 0:
        lines.append(f'rule of three check: 3/n = {pct(Fraction(3, n))} (approximation of the one-sided 95 % bound)')
    return {
        'command': 'binom', 'inputs': {'k': k, 'n': n, 'conf': str(conf)},
        'result': {'upper_one_sided': float(up1), 'lower_one_sided': float(lo1),
                   'two_sided': [float(lo2), float(up2)]},
        'assumptions': ['A1: the n trials are independent', 'A2: every trial has the same event rate p',
                        'A3: n was fixed before looking (for repeated looks use cs-bernoulli)'],
        'method': (f'Clopper–Pearson: invert the exact binomial tail; tails computed in '
                   f'{"exact rational" if exact else "log-space floating point"} arithmetic, bounds to 2^-40, '
                   f'rounded outward. Coverage is at least the stated level for every p.'),
        'source': 'Clopper & Pearson (1934), Biometrika 26(4):404–413.',
        'lines': lines}


def cmd_needed(a):
    below, conf, k = Fraction(a.below), Fraction(a.conf), a.k
    if not 0 < below < 1 or k < 0:
        raise SystemExit('need 0 < below < 1 and k >= 0')
    alpha = 1 - conf
    n = needed_n(below, alpha, k)
    lines = [f'to certify the rate is at most {pct(below)} at {pct(conf, 0)} confidence with {k} event(s):',
             f'n >= {n} trials (at n = {n - 1} the one-sided upper bound is still above {pct(below)})']
    if k == 0:
        lines.append(f'closed form: n >= ln(1 - c) / ln(1 - X) = {math.log(float(alpha)) / math.log1p(-float(below)):.2f}')
    return {
        'command': 'needed', 'inputs': {'below': str(below), 'conf': str(conf), 'k': k},
        'result': {'n': n},
        'assumptions': ['A1: trials (or groups) are independent; if events cluster inside a group, count groups',
                        'A2: every trial has the same event rate', 'A3: the plan fixes n before the data',
                        f'A4: at most {k} event(s) will be observed; each extra event raises n'],
        'method': f'smallest n with P(Bin(n, {below}) <= {k}) <= {alpha} (exact rational arithmetic '
                  f'up to n = {EXACT_MAX_N}); equivalent to the one-sided Clopper–Pearson bound <= {below}.',
        'source': 'Clopper & Pearson (1934), Biometrika 26(4):404–413.',
        'lines': lines}


def cmd_samplesize(a):
    alpha, power, sides = float(Fraction(a.alpha)), float(Fraction(a.power)), a.sides
    if a.kind == 'props':
        p1, p2 = float(Fraction(a.p1)), float(Fraction(a.p2))
        if not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
            raise SystemExit('need 0 < p1, p2 < 1 and p1 != p2')
        n, ncc = n_two_props(p1, p2, alpha, power, sides)
        res = {'n_per_group': math.ceil(n), 'n_per_group_cc': math.ceil(ncc)}
        lines = [f'{p1} vs {p2}, alpha {alpha} ({sides}-sided), power {power}:',
                 f'normal approximation: n = {math.ceil(n)} per group ({n:.2f})',
                 f'with continuity correction: n = {math.ceil(ncc)} per group ({ncc:.2f})']
        if a.exact and math.ceil(ncc) <= FISHER_EXACT_MAX_N:
            for label, m in (('normal', math.ceil(n)), ('corrected', math.ceil(ncc))):
                pw = fisher_power(m, p1, p2, Fraction(a.alpha) / sides)
                res[f'fisher_power_at_{label}'] = pw
                lines.append(f'exact power of Fisher\'s one-sided test at {alpha / sides:g} with n = {m}: {pct(pw, 1)}')
        elif a.exact:
            lines.append(f'exact check skipped: n > {FISHER_EXACT_MAX_N} (it is O(n^2)); simulate instead')
        assumptions = ['A1: independent units, randomized to two groups of equal size',
                       'A2: one rate per group (no clustering; if units cluster, multiply n by the design effect)',
                       'A3: one look at the end (several looks need a group-sequential plan)']
        method = ('Fleiss normal approximation; continuity correction of Fleiss, Tytun & Ury; '
                  'then the exact power of Fisher\'s conditional test at that n (critical values in exact '
                  'integer arithmetic). Trust the exact line when they disagree.')
        source = ('Fleiss, Tytun & Ury (1980), Biometrics 36(2):343–346; Fisher (1935), J. R. Stat. Soc. 98(1). '
                  'Fleiss, Levin & Paik, Statistical Methods for Rates and Proportions (3rd ed., 2003).')
        inputs = {'p1': p1, 'p2': p2}
    else:
        delta, sd = float(Fraction(a.delta)), float(Fraction(a.sd))
        if delta == 0 or sd <= 0:
            raise SystemExit('need delta != 0 and sd > 0')
        nz, ng = n_two_means(delta, sd, alpha, power, sides)
        res = {'n_per_group_z': math.ceil(nz), 'n_per_group': math.ceil(ng)}
        lines = [f'difference {delta} with sd {sd} (d = {delta / sd:.3g}), alpha {alpha} ({sides}-sided), '
                 f'power {power}:',
                 f'z formula: n = {math.ceil(nz)} per group ({nz:.2f})',
                 f'with Guenther\'s t correction: n = {math.ceil(ng)} per group ({ng:.2f})  <- use this']
        assumptions = ['A1: independent units, two groups of equal size',
                       'A2: roughly normal outcome (or n large enough for the mean to be), same sd in both groups',
                       'A3: sd is known from a pilot or a log, not guessed; a wrong sd scales n by (sd_true/sd)^2',
                       'A4: one look at the end; heavy tails need a transformed or rank-based test']
        method = 'n = 2 (z_a + z_b)^2 (sd/delta)^2, plus z_a^2/4 to approximate the t test (Guenther).'
        source = 'Guenther (1981), The American Statistician 35.'
        inputs = {'delta': delta, 'sd': sd}
    inputs.update({'alpha': alpha, 'power': power, 'sides': sides})
    return {'command': f'samplesize {a.kind}', 'inputs': inputs, 'result': res,
            'assumptions': assumptions, 'method': method, 'source': source, 'lines': lines}


def cmd_multi(a):
    alpha = Fraction(a.alpha)
    pv = [Fraction(p) for p in (a.p or [])]
    m = len(pv) if pv else a.m
    if not m or m < 1:
        raise SystemExit('give -m M or -p p1 p2 ...')
    bonf = alpha / m
    lines = [f'm = {m} tests, family-wise alpha {float(alpha):g}',
             f'Bonferroni: every test at alpha/m = {bonf} = {float(bonf):.6g}',
             'Holm thresholds for the sorted p-values: ' +
             ', '.join(f'{alpha / (m - i)}' for i in range(m))]
    res = {'bonferroni': float(bonf), 'holm_thresholds': [float(alpha / (m - i)) for i in range(m)]}
    if pv:
        rej_h, adj = holm(pv, alpha)
        rej_b = [p <= bonf for p in pv]
        for i, p in enumerate(pv):
            lines.append(f'p = {float(p):g}: Bonferroni {"reject" if rej_b[i] else "keep"}, '
                         f'Holm {"reject" if rej_h[i] else "keep"} (Holm-adjusted p = {float(adj[i]):.6g})')
        lines.append(f'rejected: Bonferroni {sum(rej_b)}, Holm {sum(rej_h)} of {m}')
        res.update({'rejected_bonferroni': sum(rej_b), 'rejected_holm': sum(rej_h),
                    'holm_adjusted': [float(x) for x in adj]})
    return {'command': 'multi', 'inputs': {'alpha': str(alpha), 'm': m, 'p': [str(p) for p in pv]},
            'result': res,
            'assumptions': ['A1: each p-value is valid on its own (P(p <= t) <= t under its null)',
                            'A2: nothing about dependence: Bonferroni and Holm hold under any dependence between the tests',
                            'A3: m counts every test you ran or could have reported, not only the ones shown'],
            'method': ('union bound (Bonferroni); Holm step-down, which is uniformly more powerful and controls '
                       'the same family-wise error. Exact rational thresholds. For planned looks at one growing '
                       'sample, a group-sequential plan spends less (statistics.md).'),
            'source': 'Holm (1979), Scandinavian Journal of Statistics 6(2):65–70.',
            'lines': lines}


def cmd_cs(a):
    k, n, alpha = a.k, a.n, float(Fraction(a.alpha))
    if not 0 <= k <= n or n < 1:
        raise SystemExit('need 0 <= k <= n and n >= 1')
    lo, hi = cs_bernoulli(k, n, alpha, a.a, a.b)
    fa = Fraction(a.alpha)
    flo, fhi = float(cp_lower(k, n, fa / 2)), float(cp_upper(k, n, fa / 2))
    lines = [f'{k} of {n}, alpha {alpha:g}, Beta({a.a:g}, {a.b:g}) mixture:',
             f'anytime-valid interval: [{pct(lo)}, {pct(hi)}]  (valid at every n at once: look as often as you like)',
             f'fixed-n Clopper–Pearson, same alpha: [{pct(flo)}, {pct(fhi)}]  (valid only if n was fixed in advance)',
             f'price of peeking freedom: width x{(hi - lo) / max(fhi - flo, 1e-300):.2f}',
             'keep the running intersection of the intervals you have seen; it is still valid']
    return {'command': 'cs-bernoulli', 'inputs': {'k': k, 'n': n, 'alpha': alpha, 'a': a.a, 'b': a.b},
            'result': {'cs': [lo, hi], 'clopper_pearson_fixed_n': [flo, fhi]},
            'assumptions': ['A1: the trials are independent with one constant rate p (no drift)',
                            'A2: the mixing prior Beta(a, b) was fixed before the data; it tunes where the '
                            'interval is tight, not whether it is valid'],
            'method': ('{p : M_n(p) < 1/alpha}, where M_n(p) is the Beta(a, b) mixture of Bernoulli likelihoods '
                       'divided by the likelihood at p: a nonnegative martingale under p, so by Ville\'s inequality '
                       'the true p is excluded at some n with probability at most alpha. Floating point (lgamma), '
                       'ends found by bisection and rounded outward.'),
            'source': ('Ville (1939), Étude critique de la notion de collectif; Robbins (1970), Ann. Math. Statist. '
                       '41(5):1397–1409; Lai (1976), Ann. Statist. 4(2):265–280; Howard, Ramdas, McAuliffe & '
                       'Sekhon (2021), Ann. Statist. 49(2):1055–1080.'),
            'lines': lines}


def _fracs(looks):
    vals = [Fraction(x) for x in looks]
    if any(v <= 0 for v in vals) or vals != sorted(vals) or len(set(vals)) != len(vals):
        raise SystemExit('looks must be positive and increasing')
    return [v / vals[-1] for v in vals]


def cmd_spend(a):
    alpha = float(Fraction(a.alpha))
    fr = _fracs(a.looks)
    ft = [float(t) for t in fr]
    m = len(fr)
    lines = [f'one-sided alpha {alpha:g}, {m} looks at information fractions ' + ', '.join(f'{t:.3g}' for t in ft)]
    res = {}
    for fam, name in (('obf', "O'Brien–Fleming-type"), ('pocock', 'Pocock-type')):
        cum = spending(alpha, ft, fam)
        inc = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, m)]
        res[fam] = {'cumulative': cum, 'increments': inc}
        lines.append(f'{name:<21} spend per look: ' + ', '.join(f'{x * 100:.4g} %' for x in inc) +
                     '   (cumulative ' + ', '.join(f'{x * 100:.4g} %' for x in cum) + ')')
    lines.append(f'{"Bonferroni, equal":<21} spend per look: ' + ', '.join(f'{alpha / m * 100:.4g} %' for _ in range(m)))
    lines.append('check each early budget against the smallest p-value that look can attain; below it, the look never fires')
    return {'command': 'spend', 'inputs': {'alpha': alpha, 'looks': [str(x) for x in a.looks]}, 'result': res,
            'assumptions': ['A1: look times are fixed before the data (or follow the planned information fractions)',
                            'A2: the shapes come from normal theory; on small or discrete samples use them only as '
                            'per-look budgets for exact tests (valid by the union bound, or recycled: seq-binary)',
                            'A3: one-sided'],
            'method': ("O'Brien–Fleming-type: alpha(t) = 2 - 2 Phi(z_{1-alpha/2} / sqrt t); Pocock-type: "
                       'alpha(t) = alpha ln(1 + (e - 1) t). Floating point.'),
            'source': ('Lan & DeMets (1983), Biometrika 70(3):659–663; Jennison & Turnbull, Group Sequential Methods '
                       'with Applications to Clinical Trials (2000).'),
            'lines': lines}


def cmd_seq(a):
    looks = [int(x) for x in a.looks]
    if any(x <= 0 for x in looks) or looks != sorted(looks) or len(set(looks)) != len(looks):
        raise SystemExit('looks must be positive, increasing turn counts')
    alpha = Fraction(a.alpha)
    if a.spend:
        spend = [Fraction(x) for x in a.spend]
        if len(spend) != len(looks) - 1:
            raise SystemExit('give one --spend value per early look (all looks but the last)')
    else:
        fr = [float(t) for t in _fracs(looks)]
        if a.spend_fn == 'equal':
            spend = [alpha / len(looks)] * (len(looks) - 1)
        else:
            cum = spending(float(alpha), fr, a.spend_fn)
            inc = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, len(cum))]
            spend = [Fraction(x).limit_denominator(10 ** 9) for x in inc[:-1]]
    if sum(spend) > alpha:
        raise SystemExit('early spend exceeds alpha')
    size = (a.before + 1)
    for d in [looks[0]] + [looks[j] - looks[j - 1] for j in range(1, len(looks))]:
        size *= d + 1
    if size > 300_000:
        raise SystemExit(f'{size} outcomes to enumerate; keep (before + 1) x prod(block + 1) <= 300,000')
    res = seq_binary(a.before, looks, alpha, spend, a.mode)
    p0 = float(Fraction(a.p0))
    lines = [f'{a.before} turns before; looks at {", ".join(map(str, looks))} after; one-sided alpha {float(alpha):g}; '
             f'early spend ' + ', '.join(f'{float(x) * 100:.4g} %' for x in spend) + f'; last look: {a.mode}',
             f'exact level, sup over the pooled event count: {float(res["level"]) * 100:.4f} %   '
             f'(fixed test at look {looks[-1]} alone: {float(res["fixed_level"]) * 100:.4f} %)',
             f'rollbacks of the fixed look-{looks[-1]} test that this design misses: {res["missed"]} of '
             f'{res["fixed_rejects"]} outcomes' + ('  (pathwise dominance: proved by enumeration)' if res['missed'] == 0 else '')]
    out = {'level': float(res['level']), 'fixed_level': float(res['fixed_level']), 'missed': res['missed'],
           'fixed_rejects': res['fixed_rejects'], 'rates': {}}
    for p1 in [p0] + [float(Fraction(x)) for x in (a.p1 or [])]:
        cum, fixed, expo = seq_binary_power(res, a.before, looks, p0, p1)
        tag = 'null' if p1 == p0 else f'p1 = {p1:g}'
        lines.append(f'{tag:<10} caught by look ' + ' / '.join(f'{c * 100:.1f}' for c in cum) +
                     f' %;  fixed look-{looks[-1]} test {fixed * 100:.1f} %;  expected turns live {expo:.2f}')
        out['rates'][str(p1)] = {'caught_by_look': cum, 'fixed': fixed, 'turns_live': expo}
    return {'command': 'seq-binary', 'inputs': {'before': a.before, 'looks': looks, 'alpha': str(alpha),
                                                'spend': [str(x) for x in spend], 'mode': a.mode, 'p0': p0,
                                                'p1': a.p1 or []},
            'result': out,
            'assumptions': ['A1: under the null the before and after turns are exchangeable (any base rate); the level '
                            'needs only this',
                            'A2: look times and the spend are fixed before the data; the baseline is fixed at the start',
                            'A3: for detection rates only: turns iid Bernoulli(p0) before and Bernoulli(p1) after'],
            'method': ('exact hypergeometric (Fisher) test at each look; union: last look at alpha - sum(spend); '
                       'recycle: given the pooled count K, the last look gets alpha minus the early looks\' exact '
                       'conditional mass, so alpha the discrete early looks could not use returns to the end. '
                       'Levels in exact integer arithmetic over every outcome; detection in floating point.'),
            'source': ('Fisher (1935); Mehta, Patel, Senchaudhuri & Tsiatis (1994), Biometrics (exact permutational '
                       'group-sequential tests); Proschan & Hunsberger (1995), Biometrics 51:1315–1324 (conditional '
                       'error); statistics.md §3.'),
            'lines': lines}


def main(argv=None):
    ap = argparse.ArgumentParser(prog='mf.py', description=__doc__.split('\n\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    sub = ap.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('binom', help='Clopper–Pearson bounds for k events in n trials')
    b.add_argument('-k', type=int, required=True)
    b.add_argument('-n', type=int, required=True)
    b.add_argument('--conf', default='0.95')
    b.set_defaults(fn=cmd_binom)

    nd = sub.add_parser('needed', help='trials (or groups) needed to certify a rate is at most X')
    nd.add_argument('--below', required=True, help='the rate X to certify, e.g. 0.10')
    nd.add_argument('--conf', default='0.95')
    nd.add_argument('-k', type=int, default=0, help='events you expect to see (default 0)')
    nd.set_defaults(fn=cmd_needed)

    ss = sub.add_parser('samplesize', help='n per group for two proportions or two means')
    ss.add_argument('kind', choices=['props', 'means'])
    ss.add_argument('--p1')
    ss.add_argument('--p2')
    ss.add_argument('--delta')
    ss.add_argument('--sd')
    ss.add_argument('--alpha', default='0.05')
    ss.add_argument('--power', default='0.8')
    ss.add_argument('--sides', type=int, choices=[1, 2], default=2)
    ss.add_argument('--no-exact', dest='exact', action='store_false', help='skip the exact Fisher power check')
    ss.set_defaults(fn=cmd_samplesize)

    mu = sub.add_parser('multi', help='Bonferroni and Holm thresholds')
    mu.add_argument('--alpha', default='0.05')
    mu.add_argument('-m', type=int)
    mu.add_argument('-p', nargs='+')
    mu.set_defaults(fn=cmd_multi)

    cs = sub.add_parser('cs-bernoulli', help='anytime-valid confidence sequence for a Bernoulli rate')
    cs.add_argument('-k', type=int, required=True)
    cs.add_argument('-n', type=int, required=True)
    cs.add_argument('--alpha', default='0.05')
    cs.add_argument('--a', type=float, default=1.0, help='Beta prior a (default 1)')
    cs.add_argument('--b', type=float, default=1.0, help='Beta prior b (default 1)')
    cs.set_defaults(fn=cmd_cs)

    sp = sub.add_parser('spend', help='Lan–DeMets alpha spending per look (and the Bonferroni split)')
    sp.add_argument('--alpha', default='0.025', help='one-sided level (default 0.025)')
    sp.add_argument('--looks', nargs='+', required=True, help='look sizes or information fractions, increasing')
    sp.set_defaults(fn=cmd_spend)

    sq = sub.add_parser('seq-binary', help='exact group-sequential test of a binary rate against a fixed baseline')
    sq.add_argument('--before', type=int, required=True, help='baseline turns')
    sq.add_argument('--looks', nargs='+', required=True, help='cumulative after-turns at each look, e.g. 5 10 15')
    sq.add_argument('--alpha', default='0.025', help='one-sided level over all looks')
    sq.add_argument('--spend', nargs='+', help='level of each early look (all looks but the last)')
    sq.add_argument('--spend-fn', dest='spend_fn', choices=['equal', 'obf', 'pocock'], default='equal',
                    help='derive --spend: alpha/looks each (default), or a Lan–DeMets shape')
    sq.add_argument('--mode', choices=['recycle', 'union'], default='recycle')
    sq.add_argument('--p0', required=True, help='base rate, for the null and detection rows')
    sq.add_argument('--p1', nargs='+', help='harmful rates to report detection for')
    sq.set_defaults(fn=cmd_seq)

    a = ap.parse_args(argv)
    if a.cmd == 'samplesize':
        need = ('p1', 'p2') if a.kind == 'props' else ('delta', 'sd')
        if any(getattr(a, x) is None for x in need):
            ap.error(f'samplesize {a.kind} needs ' + ' and '.join('--' + x for x in need))
    out = a.fn(a)
    if a.json:
        out = {k: v for k, v in out.items() if k != 'lines'}
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return out
    print('\n'.join(out['lines']))
    print('assumes: ' + '\n         '.join(out['assumptions']))
    print('method:  ' + out['method'])
    print('source:  ' + out['source'])
    return out


if __name__ == '__main__':
    main()
