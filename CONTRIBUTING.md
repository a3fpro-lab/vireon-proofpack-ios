# Contributing

## What to contribute
- Additional replay engines (e.g., CartPole evaluator rule)
- Sigstore/Rekor verifier integration (v2 roadmap)
- in-toto attestations for pipeline provenance
- JSON-schema full validation (optional dependency)
- Distributed RL shard-pack + merge demo

## Style rules
- Prefer stdlib-only core where possible
- Keep PASS/FAIL semantics deterministic and explicit
- Add docs in `SPEC.md`, `VERIFIER.md`, and `docs/`

## Pull request checklist
- CI passes
- Demo pack still verifies PASS
- Any new object has a schema + verifier rule

# Contributing

## Hard rules (no exceptions)
- No placeholder text.
- Any new verifier rule MUST be specified in `VERIFIER.md`.
- Any new object MUST be added to `SPEC.md` and its schema to `schemas/`.
- Any security-relevant change MUST include:
  - a test vector (positive + negative)
  - an attack case (what it prevents)
  - a short proof note in `FORMAL_PROOFS.md` or `docs/THEOREMS.md`

## Dev workflow
Run locally:
```bash
python -m compileall -q .
python make_demo_pack.py
python verify_demo_pack.py
python tools/verify_pack_strict.py demo_pack --k 2 --min-issuers 1 --max-window 86400
python tools/attack_suite.py

CI must be green for merge.

Commit.

---

## FILE 51 — `CODE_OF_CONDUCT.md`
Create: `CODE_OF_CONDUCT.md`  
Paste:

```md
# Code of Conduct

Be professional. No harassment, threats, or discrimination.
Focus criticism on code and ideas, not people.

Maintain the repo standard: no placeholders, no unverifiable claims.
