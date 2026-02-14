# Trust-Debt Demo (one-bit tamper ⇒ deterministic FAIL)

This repo proves a simple law:

**Trust-Debt Law:** a verified proofpack collapses “trust me” to **“k witnesses didn’t collude + verifier spec is honest.”**

## What the demo does
1) Generates RL-shaped artifacts (stdlib MiniCartPole):
- env params (`env.json`)
- training params + seed (`train.json`)
- final policy (`policy.json`)
- returns (`returns.json`)
- full rollout trace (`rollout.jsonl`)

2) Seals them into a VPS proofpack:
- `MANIFEST.json` hashes every artifact byte
- `ATTESTATION.json` binds to the manifest digest
- ≥k witness bundles sign the canonical attestation
- `PROVENANCE_CERT.json` enforces k-of-n provenance

3) Verifies PASS

4) Flips **one bit** in `rollout.jsonl`

5) Verifies FAIL (with an exact reason code)

## Run it
```bash
python examples/rl_minicartpole.py
python examples/make_rl_proofpack.py
python examples/rl_tamper_demo.py
