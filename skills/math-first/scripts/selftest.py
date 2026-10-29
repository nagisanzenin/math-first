"""Selftest for mf.py: known values, exact properties, a differential check and a null simulation.

  python3 selftest.py            # prints "ok"; doubles as the install check on every platform

Stdlib only, no network, about a second.
"""
import json
import math
import random
import subprocess
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mf  # noqa: E402

A05 = Fraction(1, 20)


def close(x, y, tol):
    return abs(float(x) - float(y)) <= tol


def test_binom_known_values():
    # one-sided 95 % Clopper–Pearson upper bounds
    assert round(float(mf.cp_upper(6, 30, A05)), 3) == 0.357
    assert round(float(mf.cp_upper(0, 30, A05)), 3) == 0.095
    # closed forms at the edges: k = 0 gives 1 - alpha^(1/n); k = n gives alpha^(1/n) as the lower bound
    assert close(mf.cp_upper(0, 30, A05), 1 - 0.05 ** (1 / 30), 1e-9)
    assert close(mf.cp_lower(30, 30, A05), 0.05 ** (1 / 30), 1e-9)
    # two-sided 95 % interval for 6 of 30 (standard tables: 0.0771 to 0.3857)
    lo, hi = mf.cp_lower(6, 30, A05 / 2), mf.cp_upper(6, 30, A05 / 2)
    assert round(float(lo), 4) == 0.0771 and round(float(hi), 4) == 0.3857
    # bounds are rounded outward: the exact tail at the reported bound is on the safe side
    assert mf.cdf_cmp(6, 30, mf.cp_upper(6, 30, A05), A05) <= 0
    assert mf.cdf_cmp(5, 30, mf.cp_lower(6, 30, A05), 1 - A05) >= 0


def test_binom_coverage_is_exact():
    # property: for every p, P(U(X) >= p) >= 95 %, computed exactly (no simulation)
    n = 20
    ups = [mf.cp_upper(k, n, A05) for k in range(n + 1)]
    grid = [Fraction(i, 200) for i in range(1, 200)] + [u for u in ups if u < 1]
    for p in grid:
        cover = sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1) if ups[k] >= p)
        assert cover >= Fraction(19, 20), (p, float(cover))


def test_needed():
    assert mf.needed_n(Fraction(1, 10), A05, 0) == 29
    assert mf.needed_n(Fraction(1, 10), A05, 1) == 46
    assert mf.needed_n(Fraction(1, 10), A05, 2) == 61
    # the boundary convention is "bound <= X": (1/2)^3 = 1/8 exactly, so n = 3 (not 4) certifies at alpha 1/8
    assert mf.needed_n(Fraction(1, 2), Fraction(1, 8), 0) == 3
    # consistent with binom: the bound is at most X at n and above X at n - 1
    for k in (0, 1, 2, 7):
        n = mf.needed_n(Fraction(1, 10), A05, k)
        assert mf.cp_upper(k, n, A05) <= Fraction(1, 10) + Fraction(1, 2 ** 39)
        assert mf.cp_upper(k, n - 1, A05) > Fraction(1, 10)


def test_float_path_matches_exact():
    # differential: the log-space float tail (used above EXACT_MAX_N) against the exact one
    for k, n, p in ((3, 200, Fraction(1, 50)), (40, 300, Fraction(3, 20)), (0, 1000, Fraction(1, 1000))):
        num, den = mf._cdf_num_den(k, n, p)
        assert abs(mf._cdf_float(k, n, float(p)) - num / den) <= 1e-10 * max(1e-300, num / den) + 1e-15


def test_samplesize():
    n, ncc = mf.n_two_props(0.10, 0.20, 0.05, 0.8, 2)
    assert math.ceil(n) == 199 and math.ceil(ncc) == 219
    nz, ng = mf.n_two_means(0.5, 1.0, 0.05, 0.8, 2)
    assert math.ceil(nz) == 63 and math.ceil(ng) == 64
    # the corrected n reaches 80 % exact power; the uncorrected one does not
    assert mf.fisher_power(199, 0.10, 0.20, A05 / 2) < 0.8 <= mf.fisher_power(219, 0.10, 0.20, A05 / 2)


def test_fisher_power_differential():
    # against a slow reference: Fisher's one-sided p-value computed from scratch for every table
    n, p1, p2, a = 12, 0.2, 0.6, Fraction(1, 20)
    ref = 0.0
    for x1 in range(n + 1):
        for x2 in range(n + 1):
            K = x1 + x2
            pval = Fraction(sum(comb(n, j) * comb(n, K - j) for j in range(x2, min(n, K) + 1)), comb(2 * n, K))
            if pval <= a:
                ref += comb(n, x1) * p1 ** x1 * (1 - p1) ** (n - x1) * comb(n, x2) * p2 ** x2 * (1 - p2) ** (n - x2)
    assert abs(mf.fisher_power(n, p1, p2, a) - ref) < 1e-12
    # the boundary convention is "p <= alpha": with n = 2 the table (0, 2) has p = 1/6 exactly
    assert abs(mf.fisher_power(2, 0.5, 0.5, Fraction(1, 6)) - 0.5 ** 4) < 1e-15


def test_multi():
    pv = [Fraction(1, 100), Fraction(2, 100), Fraction(4, 100)]
    rej, adj = mf.holm(pv, A05)
    assert sum(rej) == 3 and sum(p <= A05 / 3 for p in pv) == 1
    assert [float(x) for x in adj] == [0.03, 0.04, 0.04]
    # adjusted p-values are monotone in the sorted order: 3(0.01), 2(0.04) = 0.08, then max(0.08, 0.045)
    _, adj = mf.holm([Fraction(1, 100), Fraction(4, 100), Fraction(45, 1000)], A05)
    assert [float(x) for x in adj] == [0.03, 0.08, 0.08]
    # Holm never rejects less than Bonferroni
    rnd = random.Random(7)
    for _ in range(200):
        ps = [Fraction(rnd.randint(1, 2000), 20000) for _ in range(rnd.randint(1, 8))]
        r, _ = mf.holm(ps, A05)
        assert sum(r) >= sum(p <= A05 / len(ps) for p in ps)


def test_cs_bernoulli():
    # M_0 = 1 for every prior and every p (the martingale starts at 1; Ville needs it)
    for a, b in ((1.0, 1.0), (0.5, 0.5), (2.0, 5.0)):
        assert abs(mf.log_mixture_ratio(0, 0, 0.3, a, b)) < 1e-12
    lo, hi = mf.cs_bernoulli(50, 1000, 0.05)
    assert round(lo, 3) == 0.028 and round(hi, 3) == 0.080
    clo, chi = float(mf.cp_lower(50, 1000, A05 / 2)), float(mf.cp_upper(50, 1000, A05 / 2))
    assert lo < clo and hi > chi                      # anytime validity costs width
    # null simulation through the same function: the true p is ever excluded at most alpha of the time
    rnd, p, alpha, runs, steps = random.Random(2026), 0.3, 0.05, 1000, 300
    cut, missed = math.log(1 / alpha), 0
    for _ in range(runs):
        s = 0
        for t in range(1, steps + 1):
            s += rnd.random() < p
            if mf.log_mixture_ratio(s, t, p) >= cut:
                missed += 1
                break
    assert missed / runs <= alpha + 3 * math.sqrt(alpha * (1 - alpha) / runs), missed


def test_spend():
    # one-sided alpha 0.025: both shapes spend exactly alpha at t = 1
    for fam in ('obf', 'pocock'):
        assert abs(mf.spending(0.025, [1.0], fam)[0] - 0.025) < 1e-12
    # at t = 1/2: OBF-type 2 - 2 Phi(z_0.9875 / sqrt(1/2)) = 0.001525; Pocock-type 0.025 ln(1 + (e - 1)/2) = 0.015503
    obf, poc = mf.spending(0.025, [0.5], 'obf')[0], mf.spending(0.025, [0.5], 'pocock')[0]
    assert abs(obf - 0.001525) < 2e-6 and abs(poc - 0.015503) < 2e-6
    # spending is increasing in t
    c = mf.spending(0.05, [0.2, 0.4, 0.6, 0.8, 1.0], 'obf')
    assert all(x < y for x, y in zip(c, c[1:]))


def _brute_seq(before, looks, alpha, spend, p0, p1, mode='recycle'):
    """Slow reference for seq_binary: enumerate every 0/1 sequence of before + after turns.

    Returns (level, P(caught by the last look | p0, p1), expected turns live, sequences the fixed test rejects but
    the design does not)."""
    from itertools import product
    N, n = before + looks[-1], looks[-1]

    def tail(prefix_len, ones, n_after, s_obs):          # exact p by listing every arrangement of the prefix
        cnt = tot = 0
        for seq in product((0, 1), repeat=prefix_len):
            if sum(seq) == ones:
                tot += 1
                cnt += sum(seq[prefix_len - n_after:]) >= s_obs
        return Fraction(cnt, tot)
    seqs = list(product((0, 1), repeat=N))
    early = {}
    for seq in seqs:
        fired = 0
        for j, a in enumerate(spend):
            m = before + looks[j]
            if tail(m, sum(seq[:m]), looks[j], sum(seq[before:m])) <= a:
                fired = j + 1
                break
        early[seq] = fired
    reject, level, fixed = {}, Fraction(0), {}
    for K in range(N + 1):
        group = [q for q in seqs if sum(q) == K]
        for q in group:
            fixed[q] = tail(N, K, n, sum(q[before:])) <= alpha
        if mode == 'union':
            for q in group:
                reject[q] = bool(early[q]) or tail(N, K, n, sum(q[before:])) <= alpha - sum(spend)
        else:
            budget = alpha * len(group) - sum(bool(early[q]) for q in group)
            by_s = {}
            for q in group:
                if not early[q]:
                    by_s[sum(q[before:])] = by_s.get(sum(q[before:]), 0) + 1
            t = n + 1
            for sv in sorted(by_s, reverse=True):
                if by_s[sv] <= budget:
                    budget -= by_s[sv]
                    t = sv
                else:
                    break
            for q in group:
                reject[q] = bool(early[q]) or sum(q[before:]) >= t
        level = max(level, Fraction(sum(reject[q] for q in group), len(group)))

    def pr(q):
        sb, sa = sum(q[:before]), sum(q[before:])
        return p0 ** sb * (1 - p0) ** (before - sb) * p1 ** sa * (1 - p1) ** (n - sa)
    power = sum(pr(q) for q in seqs if reject[q])
    live = sum(pr(q) * (looks[early[q] - 1] if early[q] else n) for q in seqs)
    missed = sum(1 for q in seqs if fixed[q] and not reject[q])
    return level, power, live, missed


def test_seq_binary_differential():
    # case 1: the early look fires (2 of 2 with 2 events in 6 has p = 1/15); case 2: union misses fixed rollbacks
    for before, looks, alpha, spend in ((4, [2, 4], Fraction(1, 5), [Fraction(1, 15)]),
                                        (3, [2, 4], Fraction(3, 10), [Fraction(1, 15)])):
        for mode in ('recycle', 'union'):
            res = mf.seq_binary(before, looks, alpha, spend, mode)
            level, power, live, missed = _brute_seq(before, looks, alpha, spend, 0.2, 0.6, mode)
            assert res['level'] == level <= alpha, mode
            cum, _, expo = mf.seq_binary_power(res, before, looks, 0.2, 0.6)
            assert abs(cum[-1] - power) < 1e-12 and abs(expo - live) < 1e-12, mode
            assert (res['missed'] > 0) == (missed > 0), mode
    case1 = mf.seq_binary(4, [2, 4], Fraction(1, 5), [Fraction(1, 15)], 'recycle')
    assert mf.seq_binary_power(case1, 4, [2, 4], 0.2, 0.6)[2] < 4                     # early catches shorten exposure
    assert mf.seq_binary(3, [2, 4], Fraction(3, 10), [Fraction(1, 15)], 'union')['missed'] > 0


def test_seq_binary_properties():
    for before, looks, alpha in ((10, [5, 10], Fraction(1, 20)), (20, [4, 8, 12], Fraction(1, 40)),
                                 (6, [3, 6, 9], Fraction(1, 10))):
        third = alpha / len(looks)
        rec = mf.seq_binary(before, looks, alpha, [third] * (len(looks) - 1), 'recycle')
        uni = mf.seq_binary(before, looks, alpha, [third] * (len(looks) - 1), 'union')
        assert rec['level'] <= alpha and uni['level'] <= alpha
        assert rec['early_spent_max'] <= sum([third] * (len(looks) - 1))      # each early look valid given K
        for p1 in (0.3, 0.6):
            assert mf.seq_binary_power(rec, before, looks, 0.1, p1)[0][-1] >= \
                mf.seq_binary_power(uni, before, looks, 0.1, p1)[0][-1] - 1e-12  # recycling never loses
        # no early spend: the recycled design is exactly the fixed final-look test
        zero = mf.seq_binary(before, looks, alpha, [Fraction(0)] * (len(looks) - 1), 'recycle')
        assert all((sv >= zero['thr'][k]) == (sv >= zero['fixed_thr'][k]) for (_, _, k, _, sv, _) in zero['outcomes'])


def test_cli():
    for args in (['binom', '-k', '6', '-n', '30'], ['needed', '--below', '0.1', '-k', '1'],
                 ['samplesize', 'props', '--p1', '0.1', '--p2', '0.2'],
                 ['samplesize', 'means', '--delta', '0.5', '--sd', '1'],
                 ['multi', '-p', '0.01', '0.02', '0.04'], ['cs-bernoulli', '-k', '3', '-n', '200'],
                 ['spend', '--looks', '1', '2', '3'],
                 ['seq-binary', '--before', '10', '--looks', '5', '10', '--p0', '0.1', '--p1', '0.4']):
        r = subprocess.run([sys.executable, str(HERE / 'mf.py'), '--json', *args], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        assert out['assumptions'] and out['source'] and out['result'], args
    r = subprocess.run([sys.executable, str(HERE / 'mf.py'), 'needed', '--below', '0.1', '-k', '1'],
                       capture_output=True, text=True)
    assert 'n >= 46' in r.stdout and 'assumes:' in r.stdout


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
    print('ok')
