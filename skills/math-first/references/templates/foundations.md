# Foundations: <project>

The project's mathematical spec: what it promises, in terms a test can check. Code is an attempt to meet this file.
Change this file first, then the code. Every entry has an id that tests, briefs and commit messages can cite.

Last reviewed: <YYYY-MM-DD> · Owner: <name>

## 1 · Goals

What the project is for, as quantities with units and directions. A goal with no unit is a wish.

| Id | Goal | Quantity (unit, direction) | Target or bound | Who feels it |
|---|---|---|---|---|
| G1 | | | | |

## 2 · Definitions

Every term the code computes and the docs repeat, defined once.

- **D1 <term>** := <definition>. Unit: <...>. Computed by: <module or function>.

## 3 · Invariants

What must hold in every reachable state. Each one is a property test or a model-checked property.

| Id | Invariant | Kind (safety, monotonicity, conservation, bound) | Checked by |
|---|---|---|---|
| I1 | | | <test name, or "owed"> |

## 4 · Assumptions

What the guarantees rest on. Each one is either checked, monitored, or listed as a risk.

| Id | Assumption | Guarantees that depend on it | If it fails | Status (checked, monitored, assumed) |
|---|---|---|---|---|
| A1 | | | | |

## 5 · Known results used

| Result | Source | Used for | Hypotheses and where they are checked |
|---|---|---|---|
| | <author, year, venue> | | |

## 6 · Non-claims

What the project does not promise, so nobody reads it into the docs.

- N1 <...>

## 7 · Trusted core

The smallest set of code whose correctness the invariants depend on. Keep it small; review it hardest; climb the rigor
ladder here first (`rigor-ladder.md`).

| Component | Invariants it carries | Size | Rung | Evidence |
|---|---|---|---|---|
| | | <lines> | <R0–R3> | <tests, model, receipts> |

## 8 · Claims ledger

Public numbers and promises, each with a status.

| Claim | Where it appears | Status (proved, measured, assumed, not claimed) | Evidence |
|---|---|---|---|
| | <README, docs, release notes> | | <receipt or argument> |
