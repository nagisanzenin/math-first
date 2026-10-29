# Anti-patterns: symptom → the math → the fix

Read this when reviewing a claim, and before you report one of your own. Each entry is a way that math-shaped work
goes wrong while looking rigorous. New traps go at the bottom, in the same format, with the date.

| # | Anti-pattern | Symptom | Fix, in one line |
|---|---|---|---|
| 1 | Math theater | equations that no decision depends on | ask what changes if the number doubles; cut what changes nothing |
| 2 | False precision | "17.5 %" from a handful of trials | report the interval and n; round to what the interval supports |
| 3 | Magic constants | `timeout = 30`, `threshold = 3`, no source | derive it, cite it, or measure it with a receipt |
| 4 | Peeking | stop when p < 0.05 | fix the looks and split α, or use an anytime-valid method |
| 5 | Silent independence | n counts requests; users are the unit | name the assumption; analyse at the randomization unit |
| 6 | Averaging away tails | mean improved, p99 got worse | report quantiles with intervals |
| 7 | Optimizing the unmeasured | a faster step that was not the bottleneck | profile first; Amdahl's bound before the work |
| 8 | Cargo-cult formal methods | a spec of the wrong thing, or out of date | model the property that hurts; link model and code |
| 9 | Claims beyond evidence | "measured" reported as "proved" | one status per claim, no rounding up |
| 10 | The null never run | a rule whose false alarm rate is a guess | simulate the null through the real code |
| 11 | A model of a copy | the simulation re-implements the code | call the production function |
| 12 | Survivorship in benchmarks | failures and timeouts dropped | count every attempt; censor, don't delete |
| 13 | The denominator that moved | a rate fell because the base grew | fix the denominator; report numerator and denominator |
| 14 | Noise taken as a win | one run each, a 2 % "speedup" | measure the noise floor; repeat; interval on the difference |
| 15 | Goodhart on a proxy | the metric improved, the user did not | guardrails and a holdout the optimizer cannot see |
| 16 | "It's O(n log n), so it's fast" | asymptotics quoted at small n | find the crossover; measure the constant there |
| 17 | Approximation outside its regime | normal at n = 5; Little's law in a ramp | check the approximation's conditions, or go exact |
| 18 | The optimizer picks the start | the measured party chooses when a trial begins | fix, randomize or audit the start time |
| 19 | α spent where the test cannot use it | an early look whose budget is below every attainable p | check attainable p per look; recycle unused α |

## 1 · Math theater

**Symptom.** Pages of notation; the decision was made before and would be the same without them.
**The math.** A model earns its place by changing a decision or bounding a risk. Sensitivity is the test: if the
output can move by 2× and the decision stays, the model was decoration.
**Fix.** For each formula, write the decision it informs. Keep the ones where a plausible change of input flips the
decision; cut the rest. R0 with one formula that decides beats R1 with ten that don't.

## 2 · False precision

**Symptom.** "Failure rate 20.0 %" from 4 failures in 20 runs.
**The math.** The exact 95 % interval for 4 of 20 is [5.7 %, 43.7 %] (Clopper–Pearson, computed with `mf.py binom`).
The first digit is uncertain; the third is noise.
**Fix.** Always give n and the interval. Round the point estimate to the precision the interval supports.

## 3 · Magic constants

**Symptom.** A timeout, retry count, threshold, window or batch size with no stated origin.
**The math.** A constant is a claim about a distribution or a trade-off: "30 s" claims something about the latency
tail and the cost of waiting. Without a source it cannot be checked or updated when the world changes.
**Fix.** Every constant gets one of: a derivation (from a bound or an optimization), a citation, or a receipt (a
measured quantile with n, templates/receipt.json). Put the source in a comment next to the constant.

## 4 · Peeking

**Symptom.** The dashboard is checked daily; the test stops when it "turns green".
**The math.** Five looks at a nominal 5 % give a false positive rate of about 14 % (Armitage, McPherson & Rowe 1969;
statistics.md §3).
**Fix.** Fixed looks with a group-sequential boundary or a split α; or an e-value or confidence sequence if you must
look at will (statistics.md §5).

## 5 · Silent independence

**Symptom.** "Three replicas at 0.1 % failure each: 10⁻⁹ chance of losing all three." Or a test that treats every
request as independent when they come from a few users.
**The math.** P(all three fail) = p³ only under independence. A common cause (shared power, one bad deploy, the same
bug) that takes all three with probability q makes the joint failure at least q, whatever p³ is. For clustered data,
variance grows by Kish's design effect 1 + (m − 1)ρ (statistics.md §8).
**Fix.** Name independence as an assumption (A-number). Ask what common cause would break it. Analyse at the unit
that was randomized. Simulate with correlation present.

## 6 · Averaging away tails

**Symptom.** "Mean latency down 10 %" in a change that doubled p99.
**The math.** The mean is one functional of a distribution. Users who wait feel the tail; for a lognormal with σ = 2
the mean is 7.4× the median (statistics.md §9).
**Fix.** Report p50, p95, p99 with n and intervals. Check that n is large enough for the tail you name: the max of n
samples bounds p99 at 95 % only from n = 299.

## 7 · Optimizing the unmeasured

**Symptom.** A week spent making a step 2× faster; the end-to-end time barely moves.
**The math.** Amdahl's law (Amdahl 1967, AFIPS Spring Joint Computer Conference): if a step takes a fraction f of the
time and you speed it up by s, the total speedup is 1 / ((1 − f) + f/s). With f = 10 %, an infinite speedup gives
1.11×; a 2× speedup gives 1.05×.
**Fix.** Profile first. Find the rate-limiting step (lenses.md, chemistry). Compute the Amdahl bound before starting.

## 8 · Cargo-cult formal methods

**Symptom.** A TLA+ or Lean artifact exists, but it models an idealized system (atomic steps the code does not have,
no crashes, no message loss), or it has not been updated since the code changed.
**The math.** A model checker proves the model. The claim about the code holds only through the link between them
(verification.md §6).
**Fix.** Model the property whose failure hurts (safety of money, data, consensus), at the granularity where the code
can actually interleave or fail. Link it with conformance tests. Update it in the same change as the code. If the
link is missing, list it in the non-claims.

## 9 · Claims beyond evidence

**Symptom.** "This holds" after a simulation; "faster" after one machine; "safe" after a passing test.
**The math.** Each status has its own evidence (SKILL.md §3; verification.md §8). A simulation under a model is
**measured**, under that model. A theorem is **proved** only for its hypotheses.
**Fix.** One status per claim, with its evidence and scope ("measured on M2, debug build, synthetic model X"). Never
round a status up. Write the non-claims.

## 10 · The null never run

**Symptom.** A detector, alert or gate whose false alarm rate was argued on paper and never observed.
**The math.** The code adds thresholds, edge cases, multiple looks and multiple metrics that the paper argument did
not see. The rate of the whole procedure is an empirical question (statistics.md §7).
**Fix.** Simulate the null through the real code; report the rate with n and an interval; keep a small version as a
test.

## 11 · A model of a copy

**Symptom.** The simulation imports a re-implementation of the decision logic, written for the simulation.
**The math.** The measured rate belongs to the copy. Any drift between copy and code is invisible.
**Fix.** The simulation calls the production function. If it cannot (the logic is buried), refactor so the decision
is a pure function both can call.

## 12 · Survivorship in benchmarks

**Symptom.** "Median time 1.2 s over the runs that finished"; timeouts and crashes are not in the table.
**The math.** Conditioning on success biases every statistic toward the fast cases. The dropped runs are the tail.
**Fix.** Report attempts, successes, failures and timeouts. Treat timeouts as censored at the limit, not as missing.
Compare success rates as their own metric.

## 13 · The denominator that moved

**Symptom.** "Errors per request fell 20 %" in a week when bots doubled traffic with cheap, error-free requests.
**The math.** A ratio moves when either part moves. A changed mix changes the rate with no change to any unit (a
cousin of Simpson's paradox, statistics.md §10).
**Fix.** Report numerator and denominator. Fix the population, or stratify. Pick the denominator the user feels.

## 14 · Noise taken as a win

**Symptom.** One run before, one run after, "2 % faster".
**The math.** If one run has a standard deviation of 3 %, seeing a true 1 % change at 5 % two-sided with 80 % power
needs about 2(1.96 + 0.84)² × 3² ≈ 142 runs per arm (the two-means formula, statistics.md §6). Benchmark setups add
bias that repeats do not remove: environment size and link order can shift results (Mytkowicz, Diwan, Hauswirth &
Sweeney 2009, ASPLOS).
**Fix.** Measure the noise floor (baseline against itself). Repeat, interleave the arms, randomize the order, report
the interval on the difference (Georges, Buytaert & Eeckhout 2007, OOPSLA; Kalibera & Jones 2013, ISMM). For an
optimization campaign, hand the measure-and-keep loop to strictlybetter (SKILL.md §10).

## 15 · Goodhart on a proxy

**Symptom.** The optimized metric improves steadily; complaints do not fall.
**The math.** A proxy tracks the goal only over the region where it was validated. Hard optimization moves the system
out of that region (Goodhart 1975; statistics.md §10).
**Fix.** Frame (question 1) names the user quantity, not only the proxy. Keep guardrail metrics. Hold out an
evaluation the optimizer never sees. Re-check proxy against goal after big moves.

## 16 · "It's O(n log n), so it's fast"

**Symptom.** An algorithm chosen on its complexity class alone, for a problem where n is small or memory-bound.
**The math.** Asymptotics hide constants. log₂(10⁶) ≈ 20, so a constant factor of 20 cancels the whole log term at a
million items. Memory access patterns often set constants of that size (SKILL.md principle 9).
**Fix.** Find where the curves cross. Measure both at the n you actually have and at 10× it. State the crossover as a
measured claim with a receipt.

## 17 · Approximation outside its regime

**Symptom.** A z-test on 5 observations; Little's law applied during a traffic ramp; M/M/1 formulas for a server with
deterministic service.
**The math.** Every approximation has conditions. The normal approximation needs data in the tails: at 3 of 5 against
0 of 5 it gives p = 0.7 % where the exact p is 8.3 % (statistics.md §1). Little's law L = λW holds for long-run
averages of a system with a steady state (Little 1961, *Operations Research*); during a ramp, or with arrivals faster
than service, there is none. M/M/1's mean number in the system, ρ/(1 − ρ), is 9 at ρ = 0.9 and 99 at ρ = 0.99 (Kleinrock 1975,
*Queueing Systems*, vol. 1): averaging the load over a day hides that bend.
**Fix.** Write the approximation's conditions next to its use. Check them. Below the regime, compute exactly
(`mf.py`), or simulate.

## 18 · The optimizer picks the start

**Symptom.** An agent, a team or a script decides when a change goes live or when a benchmark starts, and the
before-and-after comparison uses the turns just before that moment.
**The math.** A start chosen after seeing the baseline is a selection on the baseline. If starts follow bad
stretches, regression to the mean (statistics.md §10) makes "after" look better with no effect at all. A harm can
also hide behind a high baseline. The exchangeability a permutation test needs is gone, because the before-turns were
picked by their values.
**Fix.** Start by rule (a fixed schedule), randomize the start, or hide the measured values from whoever picks it.
Otherwise record every start time and test whether baselines before chosen starts differ from baselines before
random times. Name the assumption (lenses.md, economics).

## 19 · α spent where the test cannot use it

**Symptom.** A sequential design splits α over looks, but on small discrete data the early looks almost never fire
and the last look is weaker than a single test would be.
**The math.** An exact test on discrete data attains only some p-values. If a look's budget is below the smallest
attainable p, that look is blind and its share is wasted. Even above it, each look's true size is below its budget,
and the union bound charges the full budget anyway. Computed here: with 30 baseline observations, looks at 10, 20 and
30, one-sided α = 2.5 % and α/3 per early look, the union design catches 33.4 % of a fivefold rise of a 5 % rate by
the last look. Recycling the unused α catches 44.9 % (statistics.md §3).
**Fix.** Check the smallest attainable p at each look (`mf.py spend` shows the budget). Recycle by conditioning on
the pooled data (`mf.py seq-binary`), or move the early looks later.

## Smells in a review

Phrases that should trigger a question, and the question:

| Phrase | Ask |
|---|---|
| "no significant difference" | What was the power? What does the interval rule out? |
| "statistically significant" | What n, what α, how many looks, how many comparisons? |
| "on average" | What about p99? What is the spread? |
| "up to 40 % faster" | What is the median and the interval? On which inputs? |
| "it never failed in testing" | In how many trials? The upper bound is about 3/n. |
| "we ran it a few times" | How many, and what was the noise floor? |
| "best of 5 runs" | Why the best and not the distribution? |
| "after removing outliers" | By which rule, decided when? What were they? |
| "basically independent" | Which common cause would correlate them? |
| "should be fine at scale" | Where does the curve bend? Measured at which n? |
| "the threshold is 3" | Derived from what? What is its false alarm rate? |
| "the model proves it" | Which model, which property, and what links it to the code? |
| "verified" | By whom, how, on what commit, when? Where is the receipt? |
| "we tuned it until it worked" | On which data, and was it confirmed on fresh data? |
| "p = 0.049" | Was the analysis fixed before the data? How many other analyses were run? |

See also: statistics.md (the tools behind entries 2, 4, 5, 6, 10, 14, 17), verification.md (entries 8, 9, 10, 11),
lenses.md and structures.md (the models that replace guesses), rigor-ladder.md (how much evidence a claim needs).
