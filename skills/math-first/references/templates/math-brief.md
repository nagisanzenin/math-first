# Math Brief: <title>

Rung: <R1 | R2 | R3>, because <stakes × irreversibility, one line>.
Date: <YYYY-MM-DD> · Author: <agent or person> · Status: <draft | reviewed | decided>

## 0 · Decision in five lines

<What is recommended, the bound it meets, the main risk, the rung, what is still open. Write this last.>

## 1 · Frame

- **Quantity:** <name>, in <unit>, <higher | lower> is better.
- **Decision it feeds:** <what someone will do differently depending on the answer>.
- **User value:** <why a user cares; the outermost layer>.
- **Errors and their costs:** false alarm costs <...>; a miss costs <...>. Which is worse, and can each be undone?
- **Constraints already decided:** <levels, budgets, latency, things the owner fixed; quote them>.

## 2 · Model

- **Object:** <the mathematical object: optimization, probability model, graph, queue, state machine, lattice, game>.
- **Definitions:**
  - D1 <term> := <definition precise enough that two people compute the same number>
- **Assumptions:**

| Id | Assumption | Why it is plausible | What breaks if false | How to check |
|---|---|---|---|---|
| A1 | | | | |

- **Invariants** (must hold in every state): I1 <...>
- **Lenses tried** (`lenses.md`): <lens → what it suggested → kept or dropped, and why>

## 3 · Bound

What the math says is possible, before any design:

| Result | Source | Hypotheses | Hold here? | What it implies |
|---|---|---|---|---|
| | <author, year, venue> | | <yes / under A2 / no> | |

- **Best possible:** <the optimum, or the lower bound no design can beat>
- **Impossible:** <what no design can do under these assumptions, and why>

## 4 · Measure

- **Current state:** <value ± uncertainty, n, receipt; or "not measured" and the plan>
- **Null case:** <the rule's false-alarm rate when the true effect is zero: measured, computed, or owed>
- **Noise floor:** <the smallest change the instrument can see>
- **Gap to the bound:** <current vs best possible; this is the room for improvement>

## 5 · Build

Candidate designs, each against the bound:

| Design | Meets the bound? | Cost | Constants and their sources | Main risk |
|---|---|---|---|---|
| | | | | |

- **Recommended:** <the smallest design that meets the bound, and why the others lose>
- **Constants:** every number in the design with its derivation, citation or receipt. No magic numbers.

## 6 · Prove

- **Properties** (each invariant and bound as a test): <...>
- **Differential tests:** <against an exact computation, a slow reference, the old version>
- **Null simulation:** <runs, through the real code, expected Monte Carlo error>
- **Mutation checks:** <the guards to break and the test that must fail for each>
- **Re-measure:** <what to measure after the build, and the receipt fields>

## 7 · Claims ledger

| Claim | Status | Evidence |
|---|---|---|
| | proved / measured / assumed / not claimed | <argument, citation, receipt, or A-number> |

## 8 · Non-claims and open questions

- **Not claimed:** <what this brief does not show>
- **Weakest assumption:** <the one whose failure hurts most, and what would detect it>
- **Open:** <questions for the owner, each with a recommended answer>
