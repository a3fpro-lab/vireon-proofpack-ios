# Changelog

## v1.0.0 — 2026-02-13
- Ratified VPS v1.0.0 (`STANDARD.md`)
- Full verifier pipeline: integrity → binding → k-of-n provenance → replay (`VERIFIER.md`)
- Reference implementation (stdlib-only): `vproofpack.py`
- Demo pack generator + verifier (`make_demo_pack.py`, `verify_demo_pack.py`)
- Strict policy verifier (`tools/verify_pack_strict.py`)
- Attack suite demonstrating distinct FAIL modes (`tools/attack_suite.py`)
- Formal docs: formulas + theorems + expanded proofs (`docs/FORMULAS.md`, `docs/THEOREMS.md`, `FORMAL_PROOFS.md`)
- CI enforces pack generation + verification + strict policy + attack suite
