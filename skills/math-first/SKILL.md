---
name: math-first
description: Math-first design discipline. Before writing code, name the mathematical object the problem really is, make the math the spec, borrow models from the sciences, measure where you are (and the null case), build the smallest thing that meets the bound, and prove it holds. Use when a task involves designing a system, feature or data model; choosing an algorithm or data structure; optimizing, scaling or capacity planning; setting a threshold, limit, timeout or other constant; measuring performance; statistics, A/B tests, experiments, guardrails, alerts or monitoring rules; estimating a rate or risk; or checking whether a claim (a speedup, a benchmark, an accuracy, "no regression") is true. Explicit invocation (/math-first) runs a full Math Brief. Do not use for trivial edits such as renames, formatting, typo or copy fixes, or dependency bumps.
---

# Math First

*Name the math. Then write the code.*

**Before writing code, find the mathematical object the problem really is. Make the math the spec. Borrow models
from the sciences. Measure where you are. Build the smallest thing that meets the bound. Prove it holds.**

Code is an attempt to meet a spec. When the spec is a sentence, nobody can tell whether the code meets it. When the
spec is a definition, an invariant and a bound, a test can.

## 0 · Resolve the skill directory

Everything this skill references sits next to this file: `references/*.md`, `references/templates/`, `scripts/`
(`mf.py`, `selftest.py`). If you need an absolute path:

```bash
MF="${ZCODE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-${MATH_FIRST_ROOT:-}}}}"
[ -n "$MF" ] && MF="$MF/skills/math-first"   # else: the directory containing this SKILL.md
```

Install check (stdlib only, no network, about 2 s): `python3 "$MF/scripts/selftest.py"` prints `ok`.

## 1 · When it fires, and how hard

- **Auto (the description matched):** answer the six questions at the rung the stakes call for (§5). For most
  tasks that is R0: a short math note in your reply, then the code. Do not turn a small task into a report.
- **Explicit (`/math-first`, or the user asks for a Math Brief):** write a full Math Brief from
  `references/templates/math-brief.md`, at R1 or higher.
- **Not at all:** renames, formatting, copy changes, version bumps, edits whose correctness a reader can see at a
  glance. If you are unsure, spend one line: name the object and the invariant. If that line is trivial, stop.

Always say which rung you used and why.

## 2 · Four layers, math at the core

| Layer | Holds | Example question |
|---|---|---|
| **Math** (truth) | definitions, invariants, bounds, probability | what must always hold? what is the best possible? |
| **Science** (models of the world) | physics, chemistry, biology, economics, information theory, control | what does the world do to this system? |
| **Engineering** (mechanisms under constraints) | CS, systems, cost, scale | what is the smallest mechanism that meets the bound? |
| **Product** (value for users) | the quantity a user feels | why does any of this matter? |

Every outer-layer decision traces back to the math (the spec) and forward to user value (the why). A mechanism with
no line to a definition is a guess. A theorem with no line to a user is a hobby.

## 3 · The loop: six questions

Answer them in order. Write the answers down; an answer that lives only in your head cannot be checked.

1. **Frame.** What quantity or decision actually matters to the user? Give it a name, a unit and a direction
   ("p99 latency in ms, lower is better"; "false rollbacks per change, at most 2 %"). Say what being wrong costs and
   whether it can be undone.
2. **Model.** Which mathematical object is this? An optimization problem, a probability model, a graph, a queue, a
   state machine, an invariant over a lattice, a game. Name each assumption: A1, A2, … An assumption you did not name
   is one you cannot test. `references/structures.md` maps common problems to their objects.
3. **Bound.** What does the math say is possible? A known result, a complexity class, an optimum, a lower or upper
   bound, an impossibility. Cite it, and check its hypotheses against your A1, A2, … A bound tells you when to stop.
4. **Measure.** Where are we now, with what noise? Measure the null case too: run the statistic where the true effect
   is zero and see how often it fires. A statistic never run on the null is a guess. If you predict a system with a
   model of your own, first reproduce numbers the system already measured (`references/verification.md` §2); a model
   that cannot reproduce today's numbers cannot predict tomorrow's.
5. **Build.** The smallest implementation that meets the bound. Every constant gets a derivation, a citation or a
   receipt. Prefer exact computation when it is cheap.
6. **Prove.** Tests that encode the math: properties for invariants, differential tests against a reference, mutation
   checks that the tests can fail, null simulations for statistics. Re-measure. Give every claim a status.

**Claim status, one of four:**

| Status | Means | Needs |
|---|---|---|
| **proved** | follows from definitions and named assumptions | the argument, or a citation whose hypotheses you checked |
| **measured** | observed, with uncertainty | a receipt: commit, machine, seed, command, n, and an interval |
| **assumed** | taken as true, not checked | its A-number, and what breaks if it is false |
| **not claimed** | explicitly out of scope | a line in the non-claims list |

A cited theorem is proved only for the hypotheses it states; each hypothesis you have not checked is an assumption.
An exact computation or enumeration under a model is proved for that model: write "proved under A3", never
"measured".
A measured rate of 0 events in n trials is not "never"; it is an upper bound (`mf.py binom`).

## 4 · Ten principles

1. **Math is the spec; code is an attempt to meet it; tests check it.**
2. **Name the object before writing code.** The object brings its known results with it.
3. **Every assumption has a name; every claim has a status.**
4. **Know the bound and the current state before optimizing.** The gap between them is the only room you have.
5. **Measure the null too.** False alarms are a rate. Measure it.
6. **No magic numbers.** Every constant has a derivation, a citation or a receipt.
7. **Exact when cheap, bounded when not.** Report distributions and tails, not just averages.
8. **Borrow before you invent.** Someone has usually proved the structure you need, in another field.
9. **Scale is asymptotics plus constants.** Find where the curve bends, then measure the constant there.
10. **Rigor matches stakes.** Spend proof where being wrong is expensive and hard to undo.

## 5 · Rigor ladder (detail: `references/rigor-ladder.md`)

| Rung | Cost | Produce |
|---|---|---|
| **R0 Napkin** | minutes | the object, a Fermi estimate, a dimension check, one formula, the bound |
| **R1 Model** | about an hour | a Math Brief: definitions, assumptions, known results, bounds, the measure and test plan |
| **R2 Evidence** | about a day | simulation that calls the real code, property and mutation tests, null runs, receipts |
| **R3 Proof** | when being wrong is catastrophic | a formal model (TLA+/Quint, Lean, a model checker) of the core, kept in sync with the code |

Pick the rung from **stakes × irreversibility**. Cheap and undoable: R0. Costly or user-visible: R1. A number other
people will act on, or a default many users get: R2. Safety, money, data loss, security, consensus: R3 for the core,
R2 for the rest. Climb a rung when the lower one finds a surprise. Never claim a higher rung than the evidence.

## 6 · Lenses (detail and worked examples: `references/lenses.md`)

Novelty usually comes from moving a proven structure across fields, not from inventing one. Ask each lens its
question; keep the ones that give a model you can test.

| Lens | Question |
|---|---|
| Physics | What is conserved? What is minimized? Do the dimensions agree? Is there a phase transition? |
| Chemistry | What is the rate-limiting step? Where is the equilibrium? What would act as a catalyst? |
| Biology | What is the selection pressure? What keeps it in homeostasis? What is the carrying capacity? |
| Economics | Who has which incentive? Can a party game it? Which mechanism makes honesty the best strategy? |
| Information theory | How many bits does this really carry? What do entropy and coding bounds allow? |
| Control | Where is the feedback loop? What is the delay? Is it stable, and with what margin? |

## 7 · Route by task

| Task | Do | Read |
|---|---|---|
| **New project** | Frame the product quantity; model the core objects; write a foundations file (goals, definitions, invariants, assumptions, non-claims, trusted core) before the first module. R1 for the core. | `templates/foundations.md`, `structures.md`, `rigor-ladder.md` |
| **Feature** | Name the invariants the feature must keep and the ones it adds; write them as property tests first. R0, R1 if it touches money, data or concurrency. | `structures.md`, `verification.md` |
| **Optimization** | Bound first: the floor (physics, a lower bound, the hardware). Measure the current state and its noise. Find the rate-limiting step. Then build. For the measure-and-keep loop, use strictlybetter (below). | `structures.md`, `lenses.md` (chemistry, physics), `statistics.md` |
| **Statistics and experiments** | Write the null and the decision rule before the data. Size the sample. Simulate the null through the real code. Exact tests at small n; correct for every look and every comparison. A guardrail, alert or monitor is a sequential test: count its looks and report its detection delay. | `statistics.md`, `verification.md`, `mf.py` |
| **Reviewing a claim** | Restate the claim as a quantity with a unit. Ask for n, the null rate, the receipt and the assumptions. Assign a status. Name what would falsify it. | `anti-patterns.md`, `statistics.md` |
| **Research and ideation** | Run every lens. For each candidate, name the source structure, what transfers, and which assumption might not. Rank by test cost. | `lenses.md`, `structures.md` |

Read the reference before acting on it. This file is a summary.

## 8 · Output contract

**At R0**, put a math note before the code, at most about ten lines:

```
Math note (R0: <why this rung>)
Object:  <the mathematical object>
Assume:  A1 <...>; A2 <...>
Bound:   <known result or estimate, with source>
Now:     <current measurement, or "not measured">
Plan:    <smallest build that meets the bound; constants and where they come from>
Check:   <the test that encodes the math>
Claims:  <claim> [proved|measured|assumed|not claimed]
```

**At R1 and above**, write a Math Brief (`references/templates/math-brief.md`) as a file the user can review, and
summarize it in your reply: the decision, the bound, the rung, the claims ledger, the open risks.

**Always:**
- state the rung and why;
- give every number a source: a derivation, a citation, or a receipt (`references/templates/receipt.json`);
- report uncertainty with every measurement: an interval and n, and the null rate for any decision rule;
- list non-claims: what you did not check, and the assumption whose failure would hurt most;
- if a claim cannot be checked at this rung, say so instead of rounding it up.

## 9 · Tools

`scripts/mf.py` is a stdlib-only calculator. It uses exact rational arithmetic where it can and prints its
assumptions with every answer.

```bash
python3 "$MF/scripts/mf.py" binom -k 6 -n 30 --conf 0.95            # Clopper–Pearson bounds on a rate
python3 "$MF/scripts/mf.py" needed --below 0.10 --conf 0.95 -k 1    # trials to certify a rate below 10 %
python3 "$MF/scripts/mf.py" samplesize props --p1 0.10 --p2 0.20    # n per group for two proportions
python3 "$MF/scripts/mf.py" samplesize means --delta 0.5 --sd 1     # n per group for two means
python3 "$MF/scripts/mf.py" multi --alpha 0.05 -p 0.01 0.02 0.04    # Bonferroni and Holm
python3 "$MF/scripts/mf.py" cs-bernoulli -k 3 -n 200 --alpha 0.05   # anytime-valid interval for a rate
python3 "$MF/scripts/mf.py" spend --alpha 0.025 --looks 1 2 3        # alpha spending per planned look
python3 "$MF/scripts/mf.py" seq-binary --before 30 --looks 10 20 30 --p0 0.05 --p1 0.25
                                       # exact early-look test for a rate: level, detection by look, dominance
```

Most commands answer one R0 question exactly; `seq-binary` is an R1 tool, an exact enumeration of a whole sequential
design on 0/1 data. For dependence, many-valued data under several looks, or a statistic you wrote yourself, simulate
the null through the real code (`references/verification.md`).

## 10 · Relation to strictlybetter

Math First is the design discipline upstream: the model, the bound, the spec, the null. For optimization work, the
measure-and-keep loop (noise floors, isolated trials, keep a change only when it is better in one way and worse in
none) is [strictlybetter](https://github.com/nagisanzenin/strictlybetter). Use this skill to decide what to measure
and what "better" means; hand the campaign to strictlybetter when it is installed. If it is not, follow
`references/statistics.md` and `references/verification.md` directly.

## 11 · When you learn something new

A trap this skill did not warn about goes into `references/anti-patterns.md` (symptom → the math → the fix). A
structure you borrowed that worked goes into `references/structures.md` with its citation. If you are in a
plugin-cache copy, tell the user what to upstream to github.com/nagisanzenin/math-first instead of editing the cache.
