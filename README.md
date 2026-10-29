# Math First

**A skill that makes your coding agent find the mathematical object a problem really is before it writes code, then
make the math the spec: named assumptions, a known bound, a measured baseline and null case, the smallest build that
meets the bound, and tests that prove it holds.**

One skill, native installs on Claude Code, OpenAI Codex, Antigravity, Pi, Hermes, ZCode, OpenClaw, and anything else
that reads the [Agent Skills](https://agentskills.io) `SKILL.md` standard. Built on the
[omniplugin](https://github.com/nagisanzenin/omniplugin) pattern: one portable core, thin per-platform glue.

## Why

Agents write code fast and argue about it in sentences. A sentence cannot be tested. "Retries make it more reliable",
"the cache should help", "the alert is not too noisy", "the new version is faster": each hides a quantity, a model, a
bound and a null case that nobody wrote down. So the agent tunes a constant by feel, ships a threshold whose false
alarm rate is a guess, or optimizes a step that was never the bottleneck.

Most of these problems were solved long ago, often in another field. Caching is online paging, with a proven
competitive ratio. A rate limiter is an arrival curve. A flaky-test budget is a binomial bound. A canary is a
sequential test. An autoscaler is a feedback loop with delay. Math First makes the agent name that object first.
The known result then comes with the name, and so do the tests that check it.

## The loop

Six questions, in order, written down:

1. **Frame:** what quantity or decision matters to the user? A unit and a direction.
2. **Model:** which mathematical object is this? Every assumption gets a name: A1, A2, …
3. **Bound:** what does the math say is possible? Cite the result, and check its hypotheses.
4. **Measure:** where are we now, including on the null case? A statistic never run on the null is a guess.
5. **Build:** the smallest implementation that meets the bound. No magic numbers.
6. **Prove:** tests that encode the math (property, differential, mutation, null simulation). Then re-measure.

Every claim gets one of four statuses: **proved**, **measured**, **assumed** or **not claimed**. The agent picks a
rigor rung from stakes × irreversibility, from R0 (a napkin) to R3 (a formal proof of the core), and says which one it
used.

## What your agent gets

| Piece | What it does |
|---|---|
| [`SKILL.md`](skills/math-first/SKILL.md) | the one line, four layers, six questions, ten principles, the rigor ladder, six lenses, a router by task type, the output contract |
| [`references/lenses.md`](skills/math-first/references/lenses.md) | physics, chemistry, biology, economics, information theory, control: the question each asks, known results, a worked example each, a transplant checklist |
| [`references/structures.md`](skills/math-first/references/structures.md) | 18 common engineering problems mapped to their math object, known result, citation and code check (matching, caching, queues, hashing, ranking, quorums, lattices, estimation, sequential tests, scale laws, retries, clocks) |
| [`references/statistics.md`](skills/math-first/references/statistics.md) | traps and tools: exact tests at small n, peeking and group-sequential designs, recycling α on discrete looks, multiple comparisons, e-values and confidence sequences, power, null simulation, clustering, tails, proper scores, a pre-registration card |
| [`references/verification.md`](skills/math-first/references/verification.md) | property, differential, metamorphic and mutation tests; calibrating a model against the system; dominance by enumeration; null simulations through the real code; R3 tools; receipts |
| [`references/rigor-ladder.md`](skills/math-first/references/rigor-ladder.md) | R0–R3: how to choose the rung, what each one produces, what each one can claim |
| [`references/anti-patterns.md`](skills/math-first/references/anti-patterns.md) | 19 ways math-shaped work goes wrong while looking rigorous, and review smells |
| [`references/templates/`](skills/math-first/references/templates/) | `math-brief.md` (the R1+ deliverable), `foundations.md` (a project's mathematical spec), `receipt.json` (what a measured claim records) |
| [`scripts/mf.py`](skills/math-first/scripts/mf.py) | stdlib-only calculator, exact rational arithmetic where it can be: `binom`, `needed`, `samplesize`, `multi`, `cs-bernoulli`, `spend`, `seq-binary`. Every answer prints its assumptions and its source |
| [`scripts/selftest.py`](skills/math-first/scripts/selftest.py) | known values, exact coverage, brute-force differential checks and a null simulation; no network |

## Install

| Platform | Install | Invoke |
|---|---|---|
| **Claude Code** | `claude plugin marketplace add nagisanzenin/math-first` then `claude plugin install math-first@math-first` | auto, or `/math-first:math-first` |
| **OpenAI Codex** | `codex plugin marketplace add nagisanzenin/math-first` then `codex plugin add math-first@math-first` | auto, or `$math-first` |
| **Antigravity** | `agy plugin install https://github.com/nagisanzenin/math-first` | auto, or `/math-first` |
| **Pi** | `pi install git:github.com/nagisanzenin/math-first` | auto, or `/skill:math-first` |
| **ZCode** | Settings → Plugin Management → Discover → `+` add `github.com/nagisanzenin/math-first` | auto |
| **Hermes Agent** | `git clone https://github.com/nagisanzenin/math-first ~/math-first`, then add `~/math-first/skills` to `skills.external_dirs` in `~/.hermes/config.yaml` | auto, or `/skill math-first` |
| **OpenClaw** | `openclaw plugins install math-first --marketplace nagisanzenin/math-first` | auto |
| **Anything that reads `SKILL.md`** | copy or symlink `skills/math-first/` into the platform's skills directory (e.g. `~/.agents/skills/math-first`) | auto |

The skill folder is self-contained (`SKILL.md` + `references/` + `scripts/`), so even installers that copy a single
skill directory get everything it needs.

Verify any install (stdlib Python 3, no network, about 2 s):

```bash
python3 <install-path>/skills/math-first/scripts/selftest.py     # prints: ok
```

### Honest status (per the omniplugin rule: verified-live or say so)

Checked on 2026-10-29, macOS (Apple M2), from a local clone. The GitHub routes cannot be checked until the repo is
public.

- **Claude Code 2.1.261: manifests verified, local install verified, live invoke not yet.**
  - `claude plugin validate` passes on the marketplace, the plugin manifest and `skills/`. With `--strict`, the
    marketplace and `skills/` pass. The plugin manifest gets one warning: the root `CLAUDE.md` is not loaded as
    plugin context. That is intended; it holds maintainer notes for people working in this repo, as in modal-skill.
  - A copy with broken frontmatter was seen to fail, so the check does read the skill.
  - In a throwaway `HOME`, `claude plugin marketplace add <local clone>` and `claude plugin install
    math-first@math-first` succeed.
  - `claude plugin details` lists one skill, about 218 tokens always on and about 3.2k per invocation.
  - Still owed: a session where the skill auto-activates on a design task and stays quiet on a rename.
- **Hermes Agent v0.18.2: discovery verified, live invoke not yet.** With `skills.external_dirs` pointing at a local
  clone, `hermes skills list` shows `math-first` as local and enabled.
- **Pi 0.85.0: install verified, discovery not yet.** `pi install <local clone>` registers the package; a session
  that lists the skill is still owed.
- **Selftest: verified** on macOS, Python 3.14.4. 21 hand-written mutations of `mf.py`, each seen to fail it.
- **Codex, Antigravity, ZCode, OpenClaw: not verified.**
  - Codex and Antigravity: no binary on the test machine.
  - ZCode: GUI only.
  - OpenClaw 2026.3.2: local-path installs want a `package.json`, and the marketplace route needs the public repo.
  - The manifests mirror [modal-skill](https://github.com/nagisanzenin/modal-skill)'s, which mirror omniplugin's.
    The skill is plain markdown plus two stdlib scripts, so the worst failure is a skill that does not register.
    The copy-the-folder route always works.
- **No hooks, no subagents, no background processes, no network.** Nothing runs unless your agent invokes it.

Tell me what you see on your platform and this section gets upgraded.

## Use it

It fires on its own when a task involves design, an algorithm choice, optimization or scale, a threshold or
constant, measurement, statistics or an experiment, a guardrail or alert, or checking a claim. It stays quiet on
renames, formatting and copy edits. For most tasks the agent writes a short math note before the code:

```
Math note (R0: an undoable config change)
Object:  token bucket = (σ, ρ) arrival curve
Assume:  A1 clients retry at most once; A2 next month's traffic looks like last week's
Bound:   admits at most b + r·t in any window of length t (Cruz 1991)
Now:     p99 sustained 100 req/s; p99 2-s burst 560 req (receipt: 7 days of logs, 302,400 windows)
Plan:    r = 120/s (20 % over sustained p99), b = 400: admits 640 per 2 s, 14 % over the burst
Check:   property test: no window of any generated arrival sequence exceeds b + r·t
Claims:  never admits more than b + r·t [proved for the algorithm, property-tested in code];
         the 14 % margin holds next month [assumed: A2]
```

Ask for `/math-first` (or "write a Math Brief") and it writes a full brief from the template: frame, definitions,
assumptions, known results with their hypotheses checked, current state and null, candidate designs against the
bound, the test plan, a claims ledger and the non-claims.

The calculator also works on its own:

```bash
python3 skills/math-first/scripts/mf.py needed --below 0.01 --conf 0.95 -k 0    # 299 clean runs to claim < 1 %
python3 skills/math-first/scripts/mf.py samplesize props --p1 0.10 --p2 0.12   # what an A/B test of 2 points costs
python3 skills/math-first/scripts/mf.py seq-binary --before 30 --looks 10 20 30 --alpha 0.025 --p0 0.05 --p1 0.25
```

## Relation to strictlybetter

Math First is the design discipline upstream: the model, the bound, the spec, the null.
[strictlybetter](https://github.com/nagisanzenin/strictlybetter) is the measure-and-keep loop downstream: noise
floors, isolated trials, keep a change only when it is better in one way and worse in none. For optimization work the
skill decides what to measure and what "better" means, then hands the campaign to strictlybetter when it is
installed.

## Scope

The skill was first used on a real design problem: early looks for a guardrail on rare binary events, at a fixed
false-alarm level. That run changed the skill. It added `seq-binary` and `spend`, the recycling and
attainable-p checks in `statistics.md`, model calibration and dominance by enumeration in `verification.md`, and two
anti-patterns. A public write-up of that case may follow.

The citations we were least sure of while writing were checked against Project Euclid, arXiv, DBLP and publisher
records on 2026-10-29; the rest are standard references, not re-checked one by one. Every number in the docs is
computed with `mf.py` or a shown formula, or cited. If you find one that is not, that is a bug: open an issue.

## More from the same workshop

[strictlybetter](https://github.com/nagisanzenin/strictlybetter) · [modal-skill](https://github.com/nagisanzenin/modal-skill) ·
[omniplugin](https://github.com/nagisanzenin/omniplugin) · [engram](https://github.com/nagisanzenin/engram) ·
[effortmining](https://github.com/nagisanzenin/effortmining) · [idiolect](https://github.com/nagisanzenin/idiolect) ·
[less](https://github.com/nagisanzenin/less)

---

<sub>MIT · Most engineering problems have been solved before, often in another field. This skill makes the agent look
there first.</sub>
