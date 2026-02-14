**Trust-Debt Law:** a verified proofpack collapses “trust me” to **“k witnesses didn’t collude + verifier spec is honest.”**

![proofpack-ci](../../actions/workflows/ci.yml/badge.svg)

# vireon-proofpack-ios

A **proofpack** is a tamper-evident, replay-verifiable container for **result claims**. It binds artifacts, the claim, provenance, and (when present) replay checks into a deterministic **PASS/FAIL** verifier pipeline.

This repo is **iPhone-safe** (stdlib-only Python). It implements:

- **Integrity**: `MANIFEST.json` (SHA-256 over artifacts)
- **Binding**: `ATTESTATION.json` binds to manifest digest
- **k-of-n provenance**: witness bundles + `PROVENANCE_CERT.json`
- **Transparency log**: append-only hash-chain (toy offline log)
- **Replay**: deterministic toy trace + inequality check

---

## Repo layout

- `vproofpack.py` — core proofpack library (stdlib only)
- `make_demo_pack.py` — generates `demo_pack/` with k witnesses
- `verify_demo_pack.py` — verifies the pack (PASS/FAIL)
- `tools/verify_pack.py` — verifies any pack path
- `tools/attack_suite.py` — demonstrates tamper → FAIL at the correct stage
- `docs/FORMULAS.md` — definitions and formulas used by the verifier
- `docs/THEOREMS.md` — core soundness theorems
- `FORMAL_PROOFS.md` — expanded proofs + toy replay inequality proof
- `SPEC.md` / `VERIFIER.md` — standard + exact verification rules
- `ARCHITECTURE.md` — production upgrade path (Sigstore/in-toto/shards)

---

## What “PASS” means

PASS implies:

1) **No artifact tampering** (manifest hashes match files)  
2) **Claim binding holds** (attestation binds exactly that manifest digest)  
3) **k-of-n provenance holds** (≥k distinct witness bundles validate the same canonical statement)  
4) **Log membership holds** (hash-chain anchoring verifies)  
5) **Replay holds** (if replay artifacts exist, the deterministic replay rule passes for every step)

So published results stop being social trust and become **mechanically verifiable**.

---

## Run (on any computer with Python 3.10+)

```bash
python make_demo_pack.py
python verify_demo_pack.py

Expected output:

PASS

Tamper demo (shows FAIL modes):

python tools/attack_suite.py


⸻

The replay certificate (math, fully checked)

The demo includes a deterministic replay inequality.

Step map:
[
x_{t+1} = (1-2\eta)x_t
]

Energy and progress:
[
E(x)=x^2,\quad P(x)=x^2
]

Choose:
[
\alpha = 4\eta - 4\eta^2
]

Verifier checks for every step in trace.json:
[
E(x_{t+1}) \le E(x_t) - \alpha P(x_t)
]

Full derivation is in FORMAL_PROOFS.md, and the verifier recomputes it from artifacts.

⸻

Production direction

This demo uses local HMAC witness bundles for portability. The architecture is designed to upgrade to:
	•	Sigstore keyless signing + Rekor inclusion proofs
	•	in-toto attestations (pipeline DAG)
	•	multi-log redundancy
	•	distributed RL shard packs merged via Merkle roots

See ARCHITECTURE.md and ROADMAP.md.

