# math-first: maintainer notes

This repo ships one Agent Skill, `skills/math-first/`, with thin per-platform manifests (`.claude-plugin/`,
`.codex-plugin/`, `.agents/plugins/`, root `plugin.json`), following https://github.com/nagisanzenin/omniplugin.

- The skill folder is the portable core and must stay self-contained: `SKILL.md`, `references/`, `scripts/`. Never make
  it depend on files outside `skills/math-first/`.
- `SKILL.md` stays a summary under about 250 lines; detail goes to `references/`. Keep its router table in sync with
  the file tree.
- Scripts stay stdlib-only. Run `python3 skills/math-first/scripts/selftest.py` before every commit. A new `mf.py`
  command needs a known-value test, a property or differential test against a slow reference, and a hand-written
  mutation seen to fail (record the count in README "Honest status").
- Every number in the docs needs a derivation, a citation or a receipt. Compute examples with `mf.py` and keep the
  text equal to its output. Cite author, year and venue; if a detail is uncertain, leave it out or check it.
- Examples stay generic. Material from private projects goes in only after it is public, as a case study.
- A new trap goes into `references/anti-patterns.md` (symptom → the math → the fix); a borrowed structure that worked
  goes into `references/structures.md` with its citation and its check in code.
- Release: bump `version` in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` together, rerun
  `claude plugin validate .` and `claude plugin validate skills`, update README honest status with the date and
  versions, tag `vX.Y.Z`.
- Before adding a root-level file or directory, check which platforms scan that name (omniplugin rule R9).
