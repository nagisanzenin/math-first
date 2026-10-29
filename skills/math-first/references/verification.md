# Verification: tests that encode the math

Question 6 of the loop (Prove) turns the brief into checks a machine runs. A test earns a claim its status. This file
says which test earns which status, how to write each kind, and what to record so someone else can rerun it.

## What each kind of test can and cannot show

| Test | Can show | Cannot show |
|---|---|---|
| Example (unit) test | the code is right on these inputs | anything about other inputs |
| Property-based test | no counterexample in many generated inputs; a shrunk counterexample if one is found | that none exists (it is a search, not a proof) |
| Differential test | two implementations agree on the inputs tried | that either is right, if they share a mistake |
| Metamorphic test | a relation between outputs holds when you have no oracle for one output | the output itself is right |
| Mutation check | the tests can fail: a broken guard is noticed | that the tests are complete |
| Null simulation | the false alarm rate of the whole procedure, with an interval | the rate under assumptions you did not simulate |
| Model checking | the property holds in every state of a finite model | anything about the code, unless code and model are linked |
| Proof assistant | the property holds for all inputs of the formal definition | that the definition matches the code or the world |

Testing finds bugs; it does not show their absence (Dijkstra made this point in 1970). A passing test earns
**measured**, never **proved**. Proved comes from an argument or a checked proof, for the hypotheses it states.

## 1 · From an invariant to a property

An invariant in the brief (I1, I2, …) is a statement "for all inputs x, P(x)". A property-based test generates many x
and checks P on the real code. QuickCheck introduced the idea (Claessen & Hughes 2000, ICFP); Hypothesis is the
standard Python library (MacIver, Hatfield-Dodds et al. 2019, *Journal of Open Source Software*). Both shrink a
failure to a small counterexample.

Recipe:
1. Copy the invariant from the brief, with its quantifier. "For every arrival sequence, in every window [s, e], the
   limiter admits at most B + r(e − s) requests." That is the (σ, ρ) bound of a token bucket (Cruz 1991, *IEEE
   Transactions on Information Theory*).
2. Write a generator for the quantified variable. Include the edges: empty input, ties, zero gaps, huge values, the
   boundary of every guard.
3. Call the real code. Check P exactly, or with a tolerance you derived (float error), not one you picked.
4. Name the test after the invariant, so a failure says which math broke.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=0, max_value=10), min_size=1, max_size=200))
def test_I1_admits_at_most_B_plus_r_times_window(gaps):
    bucket = TokenBucket(capacity=5, rate=2.0)        # the real class, not a copy
    t, admitted = 0.0, []
    for g in gaps:
        t += g
        if bucket.allow(now=t):
            admitted.append(t)
    for i, s in enumerate(admitted):                  # every window [s, e]
        for j in range(i, len(admitted)):
            assert j - i + 1 <= 5 + 2.0 * (admitted[j] - s) + 1e-9   # float slack
```

Common invariant shapes and their properties:

| Shape | Property |
|---|---|
| conservation | sum in = sum out + held (money, tokens, messages) |
| order | output is sorted and is a permutation of the input |
| monotonicity | a pointer, version or epoch never goes back |
| idempotence, commutativity, associativity | merge(a, a) = a; merge(a, b) = merge(b, a); grouping does not matter (a semilattice join, structures.md) |
| round trip | decode(encode(x)) = x |
| bound | a cost, latency or count stays within the bound in the brief |
| refinement | every step of the implementation is a step the spec allows |

## 2 · Differential tests

Run two implementations on the same inputs and compare (McKeeman 1998, "Differential testing for software", *Digital
Technical Journal*). Good references to compare against:
- a slow, obviously correct version (brute force, enumeration);
- an exact computation (rational arithmetic, full enumeration of a permutation distribution) for a fast approximate
  one;
- the previous release, for a refactor that must not change outputs;
- an independent library, for a numerical routine.

Derive the tolerance. If the fast version is approximate, its error bound is part of the spec: a sketch with
guarantee ε is checked at ε, not at "close enough". Two implementations that share a formula share its bugs; at least
one reference should be different in kind.

**Calibrate a model against the system before you use it.** When a brief predicts a system's behavior with a model
(an exact computation, a queue formula, a simulation of your own), first reproduce numbers the system already
measured. Score each cell as z = (measured − model) / SE, with the measurement's own Monte Carlo or sampling error.
Expect about 95 % of cells within 2 and Σz²/cells near 1. A cluster of large z in one regime is a finding: the model
or the system does something the other does not. Model the system's known approximations first, such as a Monte
Carlo p-value or a timeout. Only then call a model's numbers a stand-in for the system's.

## 3 · Metamorphic tests

When there is no oracle for one output, test a relation between outputs (Chen, Cheung & Yiu 1998, HKUST technical
report HKUST-CS98-01; survey: Chen et al. 2018, *ACM Computing Surveys*). Relations that come from the math:
- **invariance:** shuffling the input order, adding a constant to both groups of a two-sample test, relabelling
  nodes of a graph: the answer must not change;
- **units:** rescaling every input by c scales the output by c^k, with k from dimensional analysis (lenses.md,
  physics);
- **monotonicity:** more evidence of harm never lowers a harm score; a larger budget never yields a worse optimum;
- **symmetry:** swapping the arms negates the effect and swaps the one-sided p-values.

## 4 · Mutation checks

A test that cannot fail proves nothing. Mutation testing (DeMillo, Lipton & Sayward 1978, *IEEE Computer*; survey: Jia
& Harman 2011, *IEEE Transactions on Software Engineering*) changes the code on purpose and asks whether a test fails.

For every guard the brief relies on:
1. Break it: flip a comparison, drop the correction, use the wrong α, move a window by one, remove a cap, skip a
   look.
2. Run the tests. One must fail. If none does, write the missing test, or explain why the mutant is equivalent (it
   cannot change behaviour).
3. Restore the code and record the result: "k of k mutations caught", with the list.

Tools exist per language (mutmut for Python, cargo-mutants for Rust, Stryker for JavaScript, PIT for Java). For the
guards that matter, hand-written mutations aimed at the math are worth more than a tool's random ones. Check that a
mutation really changed the code; a mutation that is a no-op catches nothing.

## 4b · Dominance by enumeration

"Better in one way, worse in none" can sometimes be proved, not sampled. When two decision rules act on a finite
outcome space (counts of events, small discrete samples, bounded state), enumerate every outcome and check that rule A
fires wherever rule B fires. Then A's detection is at least B's under every alternative at once, including the ones
nobody modelled (ramps, drifts, odd mixtures). Pair it with an exact level for A, and A is no worse than B on both
errors that matter. `mf.py seq-binary` reports this count for an early-look design against the single last-look
test. When the check fails, the count of missed outcomes and their probability under plausible alternatives show
what the trade costs.

## 5 · Null and power simulations, through the real code

statistics.md §7 gives the procedure. As tests:
- **Call the production function.** A simulation of a re-implementation measures the re-implementation
  (anti-patterns.md, "a model of a copy").
- **Seed everything** and record the seed. Derive per-worker seeds from one master seed, so a parallel run is
  reproducible.
- **Assert with intervals,** not points: fail when the Clopper–Pearson lower bound of the false alarm rate is above
  the stated level (`mf.py binom`). A test that fails when the point estimate crosses the level fails by chance about
  half the time when the size equals the level.
- **Keep a small version in the normal suite** (fast, fewer runs) and the full version behind a flag. Record the full
  run's receipt.
- **Mutate the simulation too.** Plant a known bug (double the effective α) and check the simulation sees it. A
  simulation that cannot see a planted bug cannot see a real one.

## 6 · Model-based testing and R3

Climb to R3 (rigor-ladder.md) when being wrong is catastrophic or hard to undo: concurrency, distributed protocols,
consensus, money ledgers, access control, irreversible data operations. Model the core, not the system.

- **TLA+** (Lamport, *Specifying Systems*, Addison-Wesley, 2002): state machines and temporal properties. TLC checks a
  finite instance by enumerating states; Apalache checks symbolically with an SMT solver (Konnov, Kukovec & Tran 2019,
  OOPSLA). **Quint** is a specification language with a typed, programmer-friendly syntax on the same logic, with a
  simulator and Apalache as a backend. Industrial experience: Newcombe et al. 2015, "How Amazon Web Services uses
  formal methods", *Communications of the ACM*.
- **Alloy** (Jackson, *Software Abstractions*, MIT Press, 2006): relational models, small-scope search.
- **Lean 4** (de Moura & Ullrich 2021, CADE): machine-checked proofs, best for pure functions and mathematical claims
  (a bound, an invariant of a data structure).
- **Fault injection against the real system** (Jepsen, jepsen.io): partitions, clock skew, crashes, with a checker
  for the consistency model claimed.
- **Model-based testing** (Utting & Legeard, *Practical Model-Based Testing*, Morgan Kaufmann, 2007): generate test
  sequences from the model and run them against the code.

**The link is the weak point.** A model checker proves the model. The claim about the code is **proved (model)** plus
**measured (conformance)**: traces from the model run against the code, or code traces replayed in the model. Without
that link, say so in the non-claims. Keep the model in the repo, run its check in CI, and update it in the same
change as the code it models.

## 7 · Receipts and reproducibility

A **measured** claim needs a receipt that lets someone else rerun it. Use templates/receipt.json. The fields that
matter:

| Field | Why |
|---|---|
| claim, value, interval, n | what was measured, and how sure |
| command | the exact command, copy-pasteable |
| commit (and whether the tree was dirty) | which code |
| machine, OS, toolchain, build mode | which environment; timings depend on all four |
| seed, RNG | so the run is bit-identical on rerun |
| date | facts about tools and data drift |
| data source | real trace (and its hash) or a named synthetic model; never unlabelled |
| null rate | for any decision rule: how often it fires when nothing changed |

Reproducibility rules:
- Deterministic code with the same seed and commit gives bit-identical output. If it does not, find out why before
  trusting any number from it.
- Floating-point reductions in parallel can change the last bits between runs. Either make the reduction order fixed
  or state the tolerance and why it is enough.
- Timing is never bit-identical. Report the distribution over repeated runs, the machine, and the noise floor (the
  spread of the baseline against itself).
- A receipt with no command is an anecdote.

## 8 · Which test earns which status

| Claim | Earns **proved** | Earns **measured** |
|---|---|---|
| an invariant of a pure function | a proof (paper or Lean), with its hypotheses checked | property tests + mutation checks |
| a protocol or concurrency property | model checking of the core + conformance tests | fault injection (Jepsen-style), long randomized runs |
| a statistical level (false alarm rate) | the test's validity theorem, with its assumptions named | a null simulation of the whole procedure, through the real code |
| power or detection rate | an exact power computation under a named model | a power simulation with planted effects |
| a speedup or cost change | a complexity argument (asymptotics only) | repeated runs on both versions, interval on the difference, noise floor |
| a numerical routine's accuracy | an error bound | differential test against an exact or higher-precision reference |
| "no regression" | rarely provable | an equivalence or non-inferiority test with a stated margin (statistics.md §6) |

A claim with none of these is **assumed**. A claim nobody checked and nobody needs goes in **not claimed**.

## Checklist for question 6

- Every invariant in the brief has a property test named after it.
- Every guard has a mutation that was seen to fail its test.
- Every statistical rule has a null simulation of the whole procedure, and a power run at the effect sizes in the
  frame.
- Every approximate routine has a differential test against an exact one, at a derived tolerance.
- Every measured number has a receipt.
- The claims ledger lists each claim with its status, and the non-claims are written down.
