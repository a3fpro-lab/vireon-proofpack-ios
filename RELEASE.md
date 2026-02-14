# Release: VPS v1.0.0

**Trust-Debt Law:** a verified proofpack collapses “trust me” to **“k witnesses didn’t collude + verifier spec is honest.”**

## What this is
A deployable **standard + reference implementation** for publishing **verifiable result claims** with deterministic **PASS/FAIL** verification.

## What’s included
- Proofpack objects: `MANIFEST.json`, `ATTESTATION.json`, `WITNESS_BUNDLES/`, `PROVENANCE_CERT.json`
- **k-of-n provenance** (threshold witnesses)
- **Offline transparency-style log** (append-only hash-chain, demo-safe)
- **Deterministic replay** certificate (toy) + verifier rule
- **Pinned test vectors** (locked root digest) + CI regen/verify
- **Strict policy verifier** (issuer/min-window enforcement)
- **Attack suite** demonstrating expected FAIL modes (tamper classes)
- **Stdlib RL-shaped demo** (MiniCartPole artifacts) + **1-bit tamper ⇒ FAIL**

## 10-second demo
```bash
pip install .
vps make-demo --out demo_pack_cli
vps verify demo_pack_cli --k 2
