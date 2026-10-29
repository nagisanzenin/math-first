# Statistics: the traps and the right tools

Questions 3, 4 and 6 of the loop (Bound, Measure, Prove) run on statistics whenever the data are noisy. Each entry
below is **trap → why (the math) → the right tool → what to run**. Numbers marked "computed here" were checked with
`python3` against the formula next to them; the rest cite their source.

| § | Trap |
|---|---|
| 1 | Normal approximations at small n and on discrete data |
| 2 | "0 of n" read as "never" |
| 3 | Looking at a growing sample more than once |
| 4 | Testing many things and reporting the winner |
| 5 | Monitoring continuously with a fixed-n test |
| 6 | No power: "we found nothing" |
| 7 | A decision rule never run on the null |
| 8 | Silent independence: clusters, sessions, time |
| 9 | Means that hide tails |
| 10 | Four classic illusions |
| 11 | Forecasts scored by feel |
| 12 | The pre-registration card |

## 1 · Small n and discrete data

**Trap.** A z-score or Welch's t on 5 or 10 observations, or on 0/1 data, and a threshold like "z ≥ 2".

**Why.** The normal approximation needs enough data in both tails. At small n the sample variance is itself noisy, and
on discrete data it can be exactly 0. A baseline with zero variance makes the standard error come from one group only,
and the statistic blows up. Example, computed here: a baseline of 5 runs with 0 errors, a candidate with 3 errors in
5 runs. z = 2.45, normal one-sided p = 0.7 %. Welch's t at its 4 degrees of freedom gives p = 3.5 %. The exact answer
(Fisher's test, below) is p = 10/120 = 8.3 %. Two of three methods call it significant at 5 %; it is not.

**Tools.**
- **Binomial rate:** the Clopper–Pearson interval (Clopper & Pearson 1934, *Biometrika*), which inverts the exact
  binomial tail. It is conservative: coverage is at least the nominal level at every n and p. For 6 events in 30, the
  Wald interval is [5.7 %, 34.3 %]; the exact two-sided 95 % interval is [7.7 %, 38.6 %], and the one-sided 95 % upper
  bound is 35.7 % (computed here). `mf.py binom -k 6 -n 30 --conf 0.95`.
- **Two rates:** Fisher's exact test (Fisher 1935, *The Design of Experiments*): conditional on the total number of
  events, the count in one group is hypergeometric under the null.
- **Two samples of anything:** the permutation test. If, under the null, the pooled observations are exchangeable
  (their joint distribution does not change when you shuffle the labels), then the observed labelling is one uniform
  draw from all labellings, and P(p ≤ α) ≤ α. That holds at every n, for every distribution, for any statistic you
  choose. The statistic only sets the power. Fisher's exact test is the permutation test on 0/1 data. A studentized
  statistic (Welch's t as the permutation statistic) stays exact under exchangeability and is also asymptotically
  valid when only the means are equal (Chung & Romano 2013, *Annals of Statistics*).
- **Too many labellings to enumerate:** draw B random relabellings and use p = (1 + #{T* ≥ T}) / (1 + B). The +1 keeps
  the test valid; a Monte Carlo p of exactly 0 is a bug (Phipson & Smyth 2010, *Statistical Applications in Genetics
  and Molecular Biology*). Near an attainable exact p just above α, a Monte Carlo p falls below α part of the time,
  so the test becomes a randomized one. It is still valid, but its size and power differ from the exact test's. Model
  that before you compare an exact computation with a system that uses Monte Carlo p-values. Example, computed here:
  an exact p of 5.02 % against α = 5 % rejects 46 % of the time with B = 9,999.

**Unknown nuisance parameters: condition on what the null fixes.** "No effect" rarely pins down the distribution: the
base rate, the scale or the shape is still free. A test is exact for every value of that nuisance parameter when you
condition on a statistic whose conditional distribution under the null does not depend on it. For two rates that is
the pooled event count (Fisher's test); for two samples of anything it is the pooled multiset (the permutation test).
For one-parameter exponential families the conditional test is the uniformly most powerful unbiased one, in its
randomized form (Lehmann & Romano, *Testing Statistical Hypotheses*, 3rd ed., Springer, 2005, ch. 4). This is also
the tool for sequential designs on discrete data (§3).

**Discreteness sets a floor.** An exact test on small discrete data has a finite set of attainable p-values. With 5
against 5, the smallest one-sided permutation p is 1/C(10,5) = 1/252 ≈ 0.40 %. A correction that asks for a smaller
level can never fire. Check the smallest attainable p before you split α (§3, §4); if it is above your threshold, the
design is blind and needs more data, not a cleverer test.

## 2 · "0 of n" is a bound, not a zero

**Trap.** "We ran it 30 times and it never failed", read as a failure rate of 0.

**Why.** With 0 events in n trials, every rate p with (1 − p)^n > α is still consistent with the data. The one-sided
upper bound is 1 − α^(1/n). For n = 30 at 95 %: 9.5 % (computed here). The **rule of three** approximates it as 3/n,
because −ln 0.05 = 3.0 (Hanley & Lippman-Hand 1983, *JAMA*).

**Tools.** `mf.py binom -k 0 -n 30` for the bound. To plan the run, ask the other way round: how many trials certify a
rate below X? `mf.py needed --below 0.10 --conf 0.95 -k 0` gives 29; with 1 event allowed, 46; with 2, 61 (computed
here). Decide k before you run, or the plan is a peek (§3).

## 3 · Multiple looks: peeking

**Trap.** Check the p-value after every batch; stop when it crosses 5 %.

**Why.** Each look is another chance for noise to cross the line. Armitage, McPherson & Rowe (1969, *JRSS A*) showed
the false positive rate of a nominal 5 % two-sided test grows with the number of equally spaced looks. Simulated here
(normal increments, 100,000 runs per row, Monte Carlo standard error at most 0.14 points), matching their table:

| Looks | 1 | 2 | 3 | 5 | 10 | 20 |
|---|---|---|---|---|---|---|
| False positive rate | 5.0 % | 8.3 % | 10.7 % | 14.3 % | 19.3 % | 24.9 % |

The rate keeps growing without bound as looks are added (the law of the iterated logarithm), so "stop when
significant" eventually rejects every true null.

**Tools, cheapest first.**
- **Union bound (always valid).** Give look k its own level α_k with Σ α_k ≤ α. Valid under any dependence between
  looks (Boole's inequality). Conservative, because successive looks at a growing sample are positively correlated
  (for a cumulative sum, the correlation between looks at n_j < n_k is √(n_j/n_k)).
- **Group-sequential boundaries.** Fixed look times, boundaries computed from the joint distribution of the looks.
  Pocock (1977, *Biometrika*): the same nominal level at every look; for 5 looks at 5 % two-sided, |z| ≥ 2.413, a
  nominal 1.6 % each. O'Brien & Fleming (1979, *Biometrics*): strict early, nearly α at the end; for 5 looks,
  |z| ≥ 2.040·√(5/k): 4.56, 3.23, 2.63, 2.28, 2.04. Both simulated here at 5.05 % and 5.07 % overall. Reference:
  Jennison & Turnbull, *Group Sequential Methods with Applications to Clinical Trials* (Chapman & Hall/CRC, 2000).
- **Alpha spending.** Lan & DeMets (1983, *Biometrika*): choose a spending function α(t) of the information fraction t
  and spend α(t_k) − α(t_{k−1}) at each look, so look times need not be fixed in advance.
- **Exact group-sequential tests at small n.** The boundaries above use a normal approximation. On small discrete
  samples, compute them from the exact (permutation) joint distribution, or simulate them through the real statistic.
  Mehta, Patel, Senchaudhuri & Tsiatis (1994, *Biometrics*) give exact permutational group-sequential tests.

**Discrete looks: two checks and one fix.**
1. *Check each early budget against the smallest p that look can attain.* An early look whose budget is below every
   attainable p never fires. O'Brien–Fleming-type spending puts very little at the first look: one-sided α = 2.5 %
   over three equal looks gives 0.0104 % at look 1 (`mf.py spend --alpha 0.025 --looks 1 2 3`). With 5 binary
   observations against 20, the smallest attainable p is 0.0019 % with no baseline events, 0.011 % with one and
   0.040 % with two. So that look fires only when all 5 are events and the baseline had none.
2. *Check what the union bound wastes.* Each look's exact test on discrete data has a size below its budget, so
   Σα_k overstates the risk. The last look pays for unused early budget.
3. *Fix: recycle the unused α by conditioning.* Under exchangeability, condition on the pooled data at the last look
   (the multiset of all observations, or the total count for 0/1 data). Each early look's conditional rejection
   probability is at most its budget, because its own sub-sample is a uniform draw from the pool. At the last look,
   compute the early looks' exact conditional mass and give the last look whatever is left of α. The level holds
   exactly for every value of the nuisance parameter. This is the conditional error idea (Proschan & Hunsberger 1995,
   *Biometrics*; Müller & Schäfer 2004, *Statistics in Medicine*) applied to a permutation null. For 0/1 data,
   `mf.py seq-binary` computes it exactly. It reports the level, the detection by look, and whether the design
   rolls back every outcome the single last-look test would. Example, computed here with `mf.py seq-binary --before
   30 --looks 10 20 30 --alpha 0.025 --p0 0.05 --p1 0.25`: one-sided α = 2.5 %, α/3 per early look, base rate 5 %,
   harm 25 %. Recycling catches 44.9 % by the last look, against 33.4 % for the plain union bound and 43.6 % for the
   single 30-observation test. It also catches 9.8 % at look 1 and 24.8 % by look 2. It rolls back all but 50 of the
   10,288 outcomes the single test rolls back, so it does not dominate here; check, don't assume.

**Monitors and guardrails: report the delay too.** For a rule that watches a live change, the user feels how long a
harm stays live. Report the detection probability by each look and the expected exposure,
Σ_k n_k·P(first caught at look k) + n_K·P(not caught). Report the null's exposure too: early looks should not shorten
a change that does nothing. Size the looks for the harms that matter. Use `mf.py samplesize` to see which harms any
rule at this n can detect at all.

**You pay only for the looks you take.** Planned looks at fixed times cost little: O'Brien–Fleming keeps the last
look near α. Anytime-valid methods (§5) pay for the right to look after every observation. If the looks are fixed,
use a group-sequential design; if they are not, use §5.

## 4 · Multiple comparisons

**Trap.** Twenty metrics, one at p < 0.05, reported as the finding.

**Why.** For m independent true nulls each tested at α, P(at least one false positive) = 1 − (1 − α)^m: 64 % at
m = 20, α = 5 % (computed here).

**Tools.**
- **Bonferroni:** test each at α/m. Controls the family-wise error rate (FWER) under any dependence.
- **Holm** (1979, *Scandinavian Journal of Statistics*): sort the p-values; compare the i-th smallest with
  α/(m − i + 1); stop at the first failure. Same FWER guarantee, never less powerful than Bonferroni.
- **Benjamini–Hochberg** (1995, *JRSS B*): reject the k smallest, k the largest i with p_(i) ≤ iα/m. Controls the
  false discovery rate (FDR) under independence or positive dependence; Benjamini & Yekutieli (2001, *Annals of
  Statistics*) give a version for any dependence at a log(m) cost.
- **Which.** FWER when any single false positive costs something real: a rollback, a release gate, a published claim.
  FDR when you screen many candidates and a second stage will check the winners.

Example, `mf.py multi --alpha 0.05 -p 0.01 0.02 0.04`: Bonferroni's threshold 1.67 % rejects one; Holm's thresholds
1.67 %, 2.5 %, 5 % reject all three. The comparisons you did not report still count in m.

## 5 · Anytime-valid inference: e-values and confidence sequences

**Trap.** A fixed-n test or interval, recomputed after every new observation, with the option to stop at any time.

**Why.** §3: a fixed-n guarantee holds at one n, chosen in advance. **Ville's inequality** (Ville 1939, *Étude
critique de la notion de collectif*): for a nonnegative supermartingale M with M_0 = 1, P(sup_t M_t ≥ 1/α) ≤ α. A test
built on such a process stays valid whenever you stop, for any stopping rule.

**Tools.**
- **E-values** (Vovk & Wang 2021, *Annals of Statistics*): a nonnegative E with E[E] ≤ 1 under the null. Reject when
  E ≥ 1/α (Markov's inequality). A likelihood ratio against a fixed alternative is one. Sequential e-values multiply;
  e-values from arbitrary dependent sources can be averaged. Background: Ramdas, Grünwald, Vovk & Shafer (2023,
  *Statistical Science*) and Grünwald, de Heide & Koolen, "Safe testing" (*JRSS B*, 2024).
- **Confidence sequences:** intervals that cover the true value at every n simultaneously. Robbins (1970, *Annals of
  Mathematical Statistics*) built them from mixture martingales; Howard, Ramdas, McAuliffe & Sekhon (2021, *Annals of
  Statistics*) give time-uniform, nonasymptotic bounds; Waudby-Smith & Ramdas (2024, *JRSS B*) bound means of bounded
  variables by betting. In A/B testing practice: Johari, Koomen, Pekelis & Walsh (2017, KDD), "Peeking at A/B tests".
- `mf.py cs-bernoulli -k 3 -n 200 --alpha 0.05`: a beta-binomial mixture confidence sequence for a rate.

**The cost.** At any fixed n they are wider than the fixed-n answer. Computed here: H0 p = 0.10 against H1 p = 0.30,
n = 20, α = 5 %. The fixed-n likelihood-ratio test rejects at 5 or more events (size 4.3 %, power 76 %). The same
likelihood ratio used as an e-value needs E ≥ 20, so 6 or more events (power 58 %). For 50 events in 1,000, a
uniform-mixture confidence sequence is [2.8 %, 8.0 %], against the exact fixed-n 95 % interval [3.7 %, 6.5 %]: 1.85×
as wide. Pay this when you must monitor continuously or cannot fix the stopping rule. Otherwise use §1 or §3.

## 6 · Power and sample size

**Trap.** A test with 20 % power finds nothing, and the report says "no effect".

**Why.** Power is P(reject | the effect you care about is real). Two means, effect d = 0.5 standard deviations, 10 per
group, 5 % two-sided: power 20 % (normal approximation, computed here). Four times in five such a study misses a real
effect. "Not significant" from it says almost nothing about the effect. Report the interval: it shows what the data
rule out.

**Tools** (`mf.py samplesize`). Both formulas are normal approximations; check them against an exact or simulated
power before you rely on them at small n.
- **Two proportions**, n per group: [z_{1−α/2}·√(2p̄(1 − p̄)) + z_{1−β}·√(p₁(1 − p₁) + p₂(1 − p₂))]² / (p₁ − p₂)², with
  p̄ the mean of p₁ and p₂. For 10 % against 20 %, 5 % two-sided, 80 % power: 199 per group; 219 with the continuity
  correction of Fleiss, Tytun & Ury (1980, *Biometrics*). Checked here against Fisher's exact test (one-sided 2.5 %):
  power 76.6 % at 199 and 81.2 % at 219. The approximation without correction falls short.
- **Two means**, n per group: 2(z_{1−α/2} + z_{1−β})²σ²/δ². For δ/σ = 0.5: 63. Guenther's correction for using t
  instead of z adds z²_{1−α/2}/4 (Guenther 1981, *The American Statistician*): 64.
- **No effect** is its own claim. Showing that a change is within a margin needs an equivalence or non-inferiority
  test, such as two one-sided tests (Schuirmann 1987, *Journal of Pharmacokinetics and Biopharmaceutics*), sized for
  that margin. Absence of a significant difference is not that test.

General reference: Cohen, *Statistical Power Analysis for the Behavioral Sciences* (2nd ed., 1988).

## 7 · Null simulation

**Trap.** A decision rule whose false alarm rate was derived on paper, or assumed, and never run.

**Why.** The proof covers the statistic under its assumptions. The code adds rounding, thresholds, edge cases (zero
variance, empty groups, ties), several looks and several metrics. Only a run shows the rate of the whole procedure.

**Procedure.**
1. Generate data where the effect is zero by construction: the same generator for both arms, or real data with
   shuffled labels.
2. Call the **real** decision code: the production function, not a re-implementation (anti-patterns.md, "a model of
   a copy").
3. Run the whole procedure: every look, every metric, every guard.
4. Count how often it fires. Report the rate, its Monte Carlo standard error √(r(1 − r)/N), N, the seed and the
   commit (templates/receipt.json).
5. Repeat under the assumption you trust least: clustering, heavy tails, drift. That shows how the level degrades.
6. Plant effects of the sizes you care about and measure power the same way.

**How many runs.** At r = 5 %, N = 1,000 gives a standard error of 0.69 points; N = 10,000 gives 0.22 (computed here).
Size N for the precision the decision needs.

**What a simulation can and cannot claim.** It can find a bug: a rate well above α. It cannot certify a level equal
to the true size. If the true size is exactly 5 %, 10,000 runs give about 500 rejections, and the one-sided 95 % upper
bound is 5.37 % (computed here): above 5 %, however long you run. The level is a proof obligation (status
**proved**, under named assumptions); the simulation is a bug check (status **measured**). If the true size is 4 %,
1,260 runs with 50 rejections are enough to show it is below 5 % (`mf.py needed --below 0.05 --conf 0.95 -k 50`).

## 8 · Clustering and dependence

**Trap.** n counts requests, but users, sessions or machines are the real independent units.

**Why.** Observations inside a cluster are correlated. Kish's design effect (Kish 1965, *Survey Sampling*): for
clusters of size m with intraclass correlation ρ, variance grows by 1 + (m − 1)ρ. For m = 20, ρ = 0.05 that is 1.95:
the effective sample is about half of n. In a time series with lag-1 autocorrelation ρ (AR(1)), the effective n for a
mean is about n(1 − ρ)/(1 + ρ): a third of n at ρ = 0.5. Tests that assume independence then reject far too often.
Exchangeability, which the permutation test needs, breaks too: two turns of one session are not interchangeable with
two turns of different sessions.

**Tools.**
- Randomize and analyse at the same unit. If you assign by user, analyse per user, or use a method that accounts for
  the clustering (Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments*, Cambridge, 2020, cover this for A/B
  tests).
- Permute whole clusters, not observations (a block permutation). Bootstrap whole clusters, or use a block bootstrap
  for time series (Künsch 1989, *Annals of Statistics*).
- Cluster-robust or autocorrelation-consistent standard errors (Newey & West 1987, *Econometrica*) at large n.
- Name the independence assumption (A-number) and simulate the null with clusters present (§7, step 5).

## 9 · Tails

**Trap.** "Mean latency fell 10 %" while p99 doubled.

**Why.** The mean is one number about a whole distribution. For a lognormal, mean / median = exp(σ²/2): 1.65 at σ = 1,
7.4 at σ = 2 (exact). With heavy tails the mean is dominated by rare values: a Pareto tail with shape ≤ 2 has infinite
variance, so the sample mean converges slower than 1/√n; with shape ≤ 1 there is no mean at all.

**Tools.**
- Report p50, p95 and p99 with n, or the whole empirical CDF.
- **Distribution-free intervals for a percentile** come from order statistics: [X_(r), X_(s)] covers the p-quantile
  with probability P(r ≤ Bin(n, p) ≤ s − 1) (David & Nagaraja, *Order Statistics*, 3rd ed., Wiley, 2003). Computed
  here: for the median of 100 samples, [X_(40), X_(61)] covers with 96.5 %; for p99 of 1,000 samples,
  [X_(983), X_(997)] covers with 97.6 %.
- **n limits which tails you can talk about.** The maximum of n samples exceeds the p99 with probability
  1 − 0.99^n; that reaches 95 % only at n ≥ 299 (computed here). Below that, you have no 95 % upper bound on p99.
- Compare tails quantile by quantile, each with its interval, not by the mean.

## 10 · Four classic illusions

- **Regression to the mean** (Galton 1886). Select the worst week, apply a fix, measure again: it improves even if the
  fix does nothing. Select on one measurement, judge on fresh data, and keep a control.
- **Simpson's paradox** (Simpson 1951, *JRSS B*). An effect in every subgroup reverses in the aggregate when group
  sizes differ between arms. Randomize, or stratify on the variable that sets the group sizes.
- **Survivorship.** The data are what survived a filter: runs that finished, users who stayed, services that were not
  turned off. Count the denominator before the filter.
- **Goodhart's law** (Goodhart 1975). A proxy that is optimized hard stops tracking the goal. Keep guardrail metrics
  and a holdout the optimizer cannot see. The best of many noisy candidates is biased upward (the winner's curse);
  confirm it on fresh data.

## 11 · Forecasts: calibration and proper scores

**Trap.** "The model is 90 % confident and usually right", judged by feel.

**Why and tools.** Score forecasts with a **proper** scoring rule, one whose expected score is best when you report
your true belief (Gneiting & Raftery 2007, *JASA*).
- **Brier score** (Brier 1950, *Monthly Weather Review*): the mean of (q − o)² over forecasts q and outcomes o ∈ {0, 1}.
  Murphy's decomposition (Murphy 1973, *Journal of Applied Meteorology*): BS = reliability − resolution + uncertainty,
  with uncertainty ō(1 − ō) for base rate ō. Always forecasting the base rate scores ō(1 − ō) in expectation, so a
  forecaster has skill only if BS < ō(1 − ō). Report the skill score 1 − BS/BS_ref against that reference, not the raw
  score.
- **Log score:** −log q of the outcome that happened. It punishes a confident miss without bound, which suits rare,
  costly events.
- A reliability plot needs enough forecasts per bin; with a few dozen forecasts, report the score with an interval
  (bootstrap the forecasts), not a plot.

## 12 · The pre-registration card

Write this before the data. Put it in the Math Brief (templates/math-brief.md, question 4) or in the experiment's
config. A rule written after the data is a peek.

```
Null:            <what "no effect" means, as a statement about a distribution>
Unit:            <the independent unit; what is randomized; what is analysed>
Statistic:       <the exact quantity computed>
Test:            <exact / permutation / approximate; why valid here; assumptions A1, A2 …>
Alpha:           <total level, one- or two-sided, and how it is split over looks and comparisons>
Looks:           <when, how many, the boundary at each; or the anytime-valid method>
Comparisons:     <every metric and arm that will be tested; FWER or FDR>
n and power:     <n per arm, the effect size it is powered for, the power; how computed>
Smallest p:      <the smallest attainable p at this n, checked against the split alpha>
Stopping rule:   <what ends the experiment, including "budget spent">
Null simulation: <command, N, seed; the false alarm rate of the whole procedure>
Report:          <estimate, interval, n, null rate, the receipt, the non-claims>
```

See also: verification.md (how to run null and power simulations as tests), anti-patterns.md (peeking, silent
independence, averaging away tails), structures.md (A/B and sequential testing as math objects), rigor-ladder.md
(how much of this a decision needs).
