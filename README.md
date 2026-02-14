# vireon-proofpack-ios

A **proofpack** is a tamper-evident, replay-verifiable container for *result claims*.

This repo is **iPhone-safe** (stdlib-only Python). It implements:

- **Integrity**: `MANIFEST.json` (SHA-256 over artifacts)
- **Binding**: `ATTESTATION.json` binds to manifest digest
- **k-of-n provenance**: witness bundles + a provenance cert
- **Transparency log**: append-only hash-chain (toy log, offline)
- **Replay**: deterministic toy trace check

## Repo layout

- `vproofpack.py` — core proofpack library (stdlib only)
- `make_demo_pack.py` — generates `demo_pack/` with k witnesses
- `verify_demo_pack.py` — verifies the pack (PASS/FAIL)
- `docs/FORMULAS.md` — all formulas used by the verifier
- `docs/THEOREMS.md` — formal theorems (soundness claims)

## What “PASS” means

PASS implies:
1) No artifact tampering (manifest matches files)
2) Attestation binds exactly that manifest
3) At least k distinct witness bundles validate the same statement
4) The log hash-chain membership checks out
5) The deterministic replay inequality holds for every step

This reduces “trust me” to “k witnesses didn’t collude + verifier spec is honest.”

## Run (later, on any computer with Python 3.10+)

```bash
python make_demo_pack.py
python verify_demo_pack.py
