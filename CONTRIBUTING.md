# Contributing

This repo exists to make **result claims mechanically verifiable**. Contributions are welcome if they preserve the core property:

> Any meaningful tamper must deterministically FAIL with a precise **stage + reason code**.

---

## What to contribute
- Additional replay engines (e.g., CartPole evaluator rule)
- Sigstore/Rekor verifier integration (v2 roadmap)
- in-toto attestations for pipeline provenance
- JSON-schema full validation (optional dependency)
- Distributed RL shard-pack + merge demo (Merkle-root aggregation)

---

## Style rules
- Prefer **stdlib-only** for the core verifier path where possible (mobile-safe)
- Keep PASS/FAIL semantics **deterministic** and **explicit**
- Keep reason codes stable whenever possible (changing them is a breaking change)
- Add/update docs in `SPEC.md`, `VERIFIER.md`, and `docs/`

---

## Pull request checklist
- CI passes (must be green)
- Demo pack still verifies PASS:
  - `python make_demo_pack.py`
  - `python verify_demo_pack.py`
- Strict policy still passes:
  - `python tools/verify_pack_strict.py demo_pack --k 2 --min-issuers 1 --max-window 86400`
- Any new object has:
  - a schema (`schemas/`)
  - a verifier rule (`VERIFIER.md`)
  - spec entry (`SPEC.md`)

---

## Hard rules (no exceptions)
- **No placeholder text.**
- Any new verifier rule **MUST** be specified in `VERIFIER.md`.
- Any new object **MUST** be added to `SPEC.md` and its schema to `schemas/`.
- Any security-relevant change **MUST** include:
  - a **test vector** (positive + negative), and
  - an **attack case** (what it prevents), and
  - a short proof note in `FORMAL_PROOFS.md` or `docs/THEOREMS.md`.

---

## Dev workflow
Run locally:

```bash
python -m compileall -q .
python make_demo_pack.py
python verify_demo_pack.py
python tools/verify_pack_strict.py demo_pack --k 2 --min-issuers 1 --max-window 86400
python tools/attack_suite.py

CI must be green for merge.

---

## FILE — `CODE_OF_CONDUCT.md` (create this too)

Safari → GitHub → **Add file → Create new file**  
Name: `CODE_OF_CONDUCT.md`  
Paste:

```md
# Code of Conduct

Be professional. No harassment, threats, or discrimination.
Focus criticism on code and ideas, not people.

Maintain the repo standard: no placeholders, no unverifiable claims.
