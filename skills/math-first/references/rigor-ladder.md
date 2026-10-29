# Rigor ladder: R0 to R3

Rigor costs time. Being wrong costs more, but only sometimes. The ladder makes the trade explicit: pick a rung from
the stakes, produce what that rung requires, and say which rung you used. A claim never outranks the rung that
produced it.

## Choose the rung

Score two things, each low, medium or high:

- **Stakes:** what a wrong answer costs. Low: a slower page for a minute. Medium: a user-visible bug, a day of rework,
  a default other people will copy. High: money, data loss, security, safety, a public number, a consensus or
  ordering guarantee.
- **Irreversibility:** how hard the mistake is to undo. Low: revert a commit. Medium: a migration, a published
  number, a shipped default. High: deleted data, money sent, a protocol other systems now depend on.

| | Irreversibility low | medium | high |
|---|---|---|---|
| **Stakes low** | R0 | R0 | R1 |
| **Stakes medium** | R0 | R1 | R2 |
| **Stakes high** | R1 | R2 | R3 for the core, R2 around it |

Then adjust:

- **Climb one rung** when the lower rung found a surprise (the estimate and the measurement disagree by more than
  their uncertainty, the null fires more than planned, a test you expected to pass fails).
- **Climb one rung** when the number will be reused: a default, a threshold in a library, a figure in a README.
- **Stay** when the next rung costs more than the worst case it protects against. Say so in the brief.
- **Never** describe R0 work as measured, or R2 work as proved.

## R0 Napkin (minutes)

Use it for most auto-activations. The output is the math note from SKILL.md §8.

Produce:
1. The object, named in one line ("this is a G/G/1 queue", "this is set cover", "this is a one-sided bound on a
   Bernoulli rate").
2. A Fermi estimate with its inputs: each input is a citation, a measurement or a labeled guess.
3. A dimension check: the units on both sides of every formula agree.
4. One formula or known result that bounds the answer, with its source.
5. The test that would show the estimate wrong.

Tools: `mf.py` for rates and sample sizes; arithmetic you show.

Example. "Will a 1 % error budget let us tell whether a deploy raised errors from 0.5 % to 1 %?" Object: two
proportions. `mf.py samplesize props --p1 0.005 --p2 0.01 --sides 1 --power 0.8` gives the requests needed per arm.
If that n is bigger than one day's traffic, the answer is no, and no dashboard will change it. That took one command.

Stop at R0 when the estimate is far from any decision boundary (a factor of ten or more), when the change is cheap to
undo, or when the next rung would cost more than the error it could catch.

## R1 Model (about an hour)

Use it for explicit invocations, for designs that touch money, data or concurrency, and when R0 lands near a decision
boundary.

Produce a Math Brief (`templates/math-brief.md`):
1. Frame: the quantity, unit, direction, the decision it feeds, the cost of each kind of error.
2. Definitions: every term the code will compute, defined so two people would compute the same number.
3. Assumptions A1, A2, …, each with what breaks if it is false and how it could be checked.
4. Known results and bounds, cited, with their hypotheses checked against the assumptions.
5. The current state, or a plan to measure it, including the null.
6. Candidate designs, each with the bound it meets and its cost.
7. The test plan: which properties, which null simulations, which mutations.
8. A claims ledger and the non-claims.

Exact small computations belong here too: an enumeration over all outcomes of a 15-trial experiment is minutes of
work and turns an assumed number into a proved one under the model. Label it "exact under the model", not "measured".

Stop at R1 when the brief shows one design meets the bound with margin under every assumption you named, and the
assumptions are standard for the field.

## R2 Evidence (about a day)

Use it when a number will be acted on by other people, when it becomes a default, or when R1 rests on an assumption
you cannot argue for.

Produce:
1. A simulation that calls the real code, not a copy of it. A re-implementation tests your understanding, not the
   system (`anti-patterns.md`, "a model of a copy").
2. The null run: the decision rule on data where the true effect is zero, with enough runs that the Monte Carlo
   error is small next to the margin you care about (`statistics.md`, null simulation).
3. Power runs at the effects that matter.
4. Property tests for each invariant, a differential test against an exact or slow reference, and mutation checks:
   break each guard, see a test fail, record the count (`verification.md`).
5. Receipts for every number: commit, machine, seed, command, n, date (`templates/receipt.json`).
6. The assumptions stress-tested: rerun the null with the assumption broken (correlated units, drift, heavy tails)
   and report how far the rate moves.

Stop at R2 when the measured rates hold their bounds within Monte Carlo error, the mutation checks all fail as
expected, and the stress runs show which assumption the guarantee depends on.

## R3 Proof (when being wrong is catastrophic)

Use it for the core of consensus, ordering, replication, money movement, access control, crash recovery, or any
invariant whose violation is silent and permanent. Keep the formal part small: the trusted core, not the system.

Produce:
1. A formal model of the core state machine: TLA+ or Quint with a model checker (TLC, Apalache), or a proof
   assistant (Lean, Coq, Isabelle) for a mathematical core such as an algorithm's correctness or a bound.
2. The safety invariants and, if they matter, the liveness properties, stated in the model.
3. The model checked to a stated bound (number of nodes, messages, steps), and the bound written down: a model
   checked with 3 nodes proved nothing about 4.
4. A link from model to code: conformance tests or trace checking that replays real executions against the model.
   A spec that drifted from the code is worse than none (`anti-patterns.md`, cargo-cult formal methods).
5. Everything R2 asks for, around the core.

R3 does not replace R2. The proof covers the model; the evidence covers the gap between the model and the code.

## What each rung can claim

| Rung | proved | measured | assumed | not claimed |
|---|---|---|---|---|
| R0 | only textbook results whose hypotheses are obvious | nothing new | most inputs | everything not estimated |
| R1 | results whose hypotheses you checked; exact computations under the model | existing receipts only | the model's assumptions | anything that needs the real code |
| R2 | as R1 | rates, timings and power with receipts and intervals | what the stress runs did not break | behavior outside the simulated regime |
| R3 | the core's invariants, within the checked bound | as R2 | the model-to-code link, if not trace-checked | the rest of the system |

## Common mistakes

- **Rung inflation.** Calling a Fermi estimate "measured", or a passing simulation "proved". The status table above
  is the check.
- **All rungs at once.** Writing a TLA+ spec for a feature whose risk is a slow page. Match the stakes.
- **Stopping at the bottom when the boundary is close.** An R0 estimate within a factor of two of the decision line
  does not decide anything. Climb.
- **Proof without evidence.** R3 on a model whose assumptions nobody tested against the running system.
