# Lenses: borrow a proven structure from another field

A lens is a question from a field that has already solved a problem shaped like yours. Most useful novelty in
engineering is a transplant: a structure with a known theorem, moved to a place where nobody had looked for it.

How to use one:

1. **Ask the lens's question about your system, in its terms.** "What is conserved here?" "What is the
   rate-limiting step?"
2. **Keep the lens only if it gives a model you can test**: a formula, an invariant, a predicted curve, an
   impossibility. "It is like an ecosystem" is not a model. Drop it and move on.
3. **Write the mapping.** Which of your quantities plays which role, with units. If the units do not line up, the
   mapping is wrong.
4. **Name what transfers and what may not.** The theorem transfers only with its hypotheses. Write each hypothesis
   as an assumption (A1, A2, …) and mark the ones you checked.
5. **Run the cheapest test that could break the mapping** before building on it.

A transplanted result is **assumed** until its hypotheses are checked in your system. After that it is **proved**
for those hypotheses, or **measured** if you checked its prediction directly. The checklist at the end of this file
is the short form.

## Physics

**Ask:** What is conserved? What is minimized? Do the dimensions agree? Is there a phase transition?

**Structures and results**
- **Conservation and flow balance.** In steady state, what flows in flows out (Kirchhoff's current law). For
  queues this is Little's law, `L = λW` (Little 1961, Operations Research). Any capacity claim must balance: work
  arriving per second equals work done per second, or something is piling up.
- **Conserved budgets.** An error budget behaves like a conserved quantity: α spent at one look or one metric is
  not available to another. Ask where the budget is spent and where it is wasted. A discrete test that cannot use its
  share wastes it, unless the design returns the unused part (`statistics.md` §3, recycling).
- **Dimensional analysis.** A meaningful equation can be written in dimensionless groups (Buckingham 1914, Physical
  Review). In software: requests/s × s/request is a utilization (no unit); bytes ÷ (bytes/s) is seconds. A formula
  whose units do not cancel is wrong before you run it.
- **Energy minimization.** Physical equilibria minimize a potential. Many placement, assignment and allocation
  problems are convex optimization problems: one minimum, and a certificate of optimality from duality (Boyd and
  Vandenberghe, *Convex Optimization*, Cambridge University Press, 2004). For non-convex ones, simulated annealing
  borrows the Metropolis rule from statistical physics (Kirkpatrick, Gelatt and Vecchi 1983, Science).
- **Phase transitions.** Behavior that changes sharply at a threshold. A random graph grows a giant connected
  component when the average degree crosses 1 (Erdős and Rényi 1960). Random 3-SAT instances are hardest near about
  4.3 clauses per variable (Mitchell, Selman and Levesque 1992, AAAI). Queue delay blows up as utilization nears 1
  (`structures.md`, queues). If your system has a threshold, find it before your users do.

**Worked example: a capacity claim.** "One 8-core box serves 50,000 requests/s at 2 ms of CPU each."
Balance the work: 50,000 req/s × 0.002 CPU-s/req = 100 CPU-s per second, that is, 100 cores fully busy. The box has
8. The claim is off by 12.5×. Either the 2 ms is wall time that includes waiting on I/O, or the rate is wrong.
Frame: the quantity is CPU-s per request. Measure it with a profiler under load before anything else. One line of
arithmetic saved a load test.

## Chemistry

**Ask:** What is the rate-limiting step? Where is the equilibrium? What would act as a catalyst?

**Structures and results**
- **Rate-limiting step.** The slowest step in a sequence sets the overall rate. In software this is Amdahl's law
  (Amdahl 1967, AFIPS Spring Joint Computer Conference): speeding up a fraction `f` of the work by `s` gives a total
  speedup of `1 / ((1 − f) + f/s)`, never more than `1 / (1 − f)`. In a pipeline, throughput is the minimum over the
  stages' throughputs.
- **Equilibrium and Le Chatelier.** A system at equilibrium shifts to counter a disturbance. The software analog is
  backpressure: when the consumer slows, the producer must slow too. Without a counteracting mechanism there is no
  equilibrium; a queue with arrival rate above service rate grows without bound.
- **Catalyst.** A catalyst lowers the activation barrier without being consumed. Reaction rate depends
  exponentially on the barrier: `k = A·e^(−Ea/RT)` (Arrhenius 1889). Software catalysts are indexes, caches and
  precomputed tables: they change the cost of each operation, not its result. Stale data is catalyst poisoning; it
  changes the result, so it needs its own invariant (invalidation).
- **Saturation kinetics.** Michaelis–Menten (Michaelis and Menten 1913, Biochemische Zeitschrift):
  `v = Vmax·S / (Km + S)`. Rate rises linearly at low load, then saturates; `Km` is the load at half the maximum. A
  few load-test points fit both parameters and give you the ceiling before you hit it.

**Worked example: which step to speed up.** A request takes 200 ms: parse 40, validate 5, database 155. The
proposal is a parser 10× faster. Amdahl with `f = 40/200 = 0.2`, `s = 10`: speedup `1 / (0.8 + 0.02) = 1.22`
(200 → 164 ms). Even an infinitely fast parser caps at `1/0.8 = 1.25`. Halving the database step instead gives
200 → 122.5 ms, a 1.63× speedup. Measure the per-step breakdown first (a trace over n requests, p50 and p99 per
step). The rate-limiting step at p99 is often not the one at p50.

## Biology

**Ask:** What is the selection pressure? What keeps it in homeostasis? What is the carrying capacity?

**Structures and results**
- **Selection.** Whatever is rewarded becomes more frequent, wanted or not. Goodhart's law (Goodhart 1975), in
  Strathern's phrasing: a measure that becomes a target stops being a good measure (Strathern 1997, European
  Review). A metric under optimization pressure (pass rate, coverage, a benchmark score) drifts from the quality it
  stood for. Defenses: a held-out measurement the optimizer cannot see, more than one proxy, and an occasional
  direct measurement of the real target.
- **Homeostasis.** A setpoint, a sensor, an effector and negative feedback (Cannon 1932, *The Wisdom of the Body*).
  This is control theory (below); biology adds that robust systems run several loops, each with a limited range.
- **Carrying capacity.** Logistic growth (Verhulst 1838): `dN/dt = rN(1 − N/K)`. Early data fit an exponential and
  a logistic curve equally well; they part after the inflection at `N = K/2`. With `K = 100,000` users,
  `N0 = 1,000` and `r = 0.1`/day, the exponential predicts 403,429 users on day 60, four times the whole market; the
  logistic predicts 80,296. Capacity plans built on the exponential overbuy.

**Worked example: selection on a noisy benchmark.** You try 100 configurations that are truly identical. The
benchmark has noise with sd σ. You keep the best. The winner's expected lead is the expected maximum of 100
standard normals, 2.51σ (numerical integration; the asymptotic `√(2 ln n)` = 3.03 overstates it at this n). With
σ = 1 %, the "best" configuration looks 2.5 % better and is not. Frame: the quantity is the true effect, not the
observed maximum. Prove: re-measure the winner on fresh runs (a held-out confirmation) and compare against the
null distribution of the maximum, which you can simulate. `statistics.md` has the multiple-comparison tools.

## Economics

**Ask:** Who has which incentive? Can a party game it? Which mechanism makes honesty the best strategy?

**Structures and results**
- **Incentive compatibility.** Design the rules so that each party's best strategy is the one you want. In a
  second-price sealed-bid auction, bidding your true value is a dominant strategy (Vickrey 1961, Journal of Finance).
  VCG mechanisms generalize this (Vickrey 1961; Clarke 1971, Public Choice; Groves 1973, Econometrica).
- **Impossibility.** Every non-dictatorial voting rule over three or more options can be manipulated (Gibbard 1973,
  Econometrica; Satterthwaite 1975, Journal of Economic Theory). Do not try to build a strategy-proof ranked vote;
  choose which manipulation you can live with.
- **Proper scoring rules.** A strictly proper rule is optimized in expectation only by reporting your true belief:
  the Brier score (Brier 1950, Monthly Weather Review) and the log score (Good 1952, Journal of the Royal Statistical
  Society B). Survey: Gneiting and Raftery 2007, Journal of the American Statistical Association.
- **Commons.** A shared resource with private benefit gets overused (Hardin 1968, Science). Shared CI runners and
  API quotas are commons; rate limits and prices are the fixes.
- **Who controls the start of the measurement?** If the party being measured chooses when a trial starts (a deploy,
  an experiment, a benchmark run), it can start right after a bad stretch. Then regression to the mean scores the
  change as an improvement for free, and a harm hides behind a high baseline. Fix the start by rule, randomize it, or
  record it and test whether baselines before chosen starts are worse than average (`anti-patterns.md` #18).

**Worked example: scoring forecasts so nobody can game them.** A forecaster believes a change passes with
probability `p = 0.7` and reports `q`. Under absolute error `|o − q|`, the expected loss is `p(1 − q) + (1 − p)q`:
0.42 at the honest `q = 0.7`, 0.30 at `q = 1`. The rule pays for exaggeration. Under Brier `(o − q)²`: 0.21 at
`q = 0.7`, 0.25 at `q = 0.9`, 0.30 at `q = 1`. Under log loss: 0.611 at 0.7, 0.765 at 0.9, infinite at 1. Proof for
Brier: the derivative of `p(1 − q)² + (1 − p)q²` is zero only at `q = p`. Check in code: a property test that, for
a grid of `p`, the `q` minimizing the expected score is `p`.

## Information theory

**Ask:** How many bits does this really carry? What do entropy and coding bounds allow?

**Structures and results**
- **Source coding.** No lossless code averages fewer bits per symbol than the source entropy `H` (Shannon 1948,
  Bell System Technical Journal). Textbook: Cover and Thomas, *Elements of Information Theory*, 2nd ed., Wiley, 2006.
- **Counting.** Telling `N` outcomes apart needs `log2 N` bits, or `log2 N` yes/no questions. Sorting by comparisons
  needs at least `log2(n!)` of them (`structures.md`, ranking).
- **Approximate membership.** Any structure that answers "is x in S?" for n elements with false-positive rate ε
  needs at least `n·log2(1/ε)` bits (Carter, Floyd, Gill, Markowsky and Wegman 1978, STOC). A Bloom filter uses
  `n·log2(1/ε)/ln 2 ≈ 1.44·n·log2(1/ε)` (Bloom 1970, Communications of the ACM; survey: Broder and Mitzenmacher 2004,
  Internet Mathematics).
- **Collisions.** Random IDs collide by the birthday bound (`structures.md`, hashing).

**Worked example: two claims.**
(a) "We store a million random UUIDs losslessly in 8 bytes each." A version-4 UUID carries 122 random bits
(RFC 9562): 15.25 bytes of entropy. 2^64 codes cannot name 2^122 values, so the claim is false for random IDs. It
can only hold if the IDs are not random (a sequence, a known subset), and then that is the assumption to name.
(b) A membership filter at ε = 1 %: the floor is `log2(100)` = 6.64 bits per element. A Bloom filter needs 9.59, with
the optimal 6.64 hashes; using 7 gives a false-positive rate of 1.004 %. For 10 million elements that is 12.0 MB.
Measure: query a million keys known to be absent and count the hits; `mf.py binom` gives the interval on the rate.

## Control

**Ask:** Where is the feedback loop? What is the delay? Is it stable, and with what margin?

**Structures and results**
- **Feedback with delay.** Delay eats stability margin. Nyquist's criterion decides stability from the loop's
  frequency response (Nyquist 1932, Bell System Technical Journal). Textbook: Åström and Murray, *Feedback Systems*,
  Princeton University Press, 2008.
- **PID control.** Proportional, integral and derivative terms; Ziegler and Nichols 1942 (Transactions of the ASME)
  gave the classic tuning rules. **Integral windup:** while the actuator is saturated (an autoscaler at its replica
  cap), the integral keeps growing and the loop overshoots when the cap lifts. Clamp the integral.
- **Hysteresis.** Two thresholds (scale up at 70 %, down at 40 %) stop a loop from chattering around one threshold.
- **AIMD.** Additive increase, multiplicative decrease converges to a fair and efficient share (Chiu and Jain 1989,
  Computer Networks and ISDN Systems). It is the core of TCP congestion control (Jacobson 1988, SIGCOMM).

**Worked example: an autoscaler that acts on a stale metric.** Load `L`, capacity `c` per replica, error
`e_t = L − c·r_t`. The controller sets `r_{t+1} = r_t + g·e_{t−d}/c`, acting on a reading `d` periods old. Then
`e_{t+1} = e_t − g·e_{t−d}`.
- With no delay (`d = 0`), it is stable for `0 < g < 2` and settles in one step at `g = 1`.
- With one period of delay, the characteristic equation is `z² − z + g = 0`; it is stable only for `0 < g < 1`.
  The obvious policy, "set replicas to what the last reading needs" (`g = 1`), sits on the boundary: the error goes
  1, 1, 0, −1, −1, 0, 1, … forever. At `g = 0.5` the roots have `|z| = √0.5 ≈ 0.71`, so the error shrinks by about
  29 % per period.
- The largest stable gain for `d` = 0, 1, 2, 3 is 2, 1, 0.618, 0.445 (computed from `z^(d+1) − z^d + g = 0`; these
  match `2·sin(π / (2(2d + 1)))`).

Build: a gain well inside the bound, a deadband, a cooldown at least as long as the metric delay. Prove: drive the
real controller code with a load step and a delayed metric in a simulation, and assert the error decays.

## Transplant checklist

| Step | Write down |
|---|---|
| 1 · Source | the structure and its theorem, with a citation |
| 2 · Mapping | each source quantity → your quantity, with units that cancel the same way |
| 3 · Hypotheses | each hypothesis of the theorem as an assumption A-n in your system; mark the ones you checked |
| 4 · Prediction | what the transplant predicts that you could not have guessed without it: a number, a curve, an impossibility |
| 5 · Cheapest test | the smallest measurement or simulation that could falsify the prediction |
| 6 · Status | assumed until step 5 runs; then measured (with a receipt) or proved (for the checked hypotheses) |

Hypotheses that most often fail in software: independence (failures correlate), stationarity (load has daily and
weekly cycles), continuity (counts are discrete and small), unbounded resources (queues have caps, retries add load),
and rational agents (the other party may be a script or an adversary). `anti-patterns.md` lists what happens when
you skip step 3.
