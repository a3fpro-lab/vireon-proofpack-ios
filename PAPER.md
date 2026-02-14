# Proofpacks and the Trust-Debt Law (Vireon)

## Abstract
AI/RL results are often published as *claims without cryptographic enforcement*: code changes, hidden settings, unlogged data, and unverifiable training runs create **trust debt**. A **proofpack** is a tamper-evident, replay-verifiable container for result claims that collapses trust debt into a small, explicit residual: *witness collusion* and *verifier honesty*.

This repo provides a minimal, deployable proofpack spec and reference implementation.

---

## 1. Problem: Trust Debt in AI Results
A typical claim:

> “Model/policy achieves X on benchmark Y.”

is hard to verify because:
- artifacts can change after the run,
- the claim can drift from the artifacts,
- provenance is social (“trust me”) not cryptographic,
- replay is missing or non-deterministic.

**Trust debt** is the burden shifted to the reader/reviewer to accept unverifiable assumptions.

---

## 2. Design Goal
Turn “trust me” into a mechanical outcome:

> **PASS** (cryptographically consistent, replay-valid)  
> **FAIL** (tampered, inconsistent, or unverifiable)

---

## 3. Proofpack Objects (VPS v1)
A proofpack binds four things:

### (A) Integrity — `MANIFEST.json`
A list of SHA-256 digests for artifacts.
Verification recomputes all digests.

### (B) Binding — `ATTESTATION.json`
A canonical statement that binds to the manifest digest:
`ATTESTATION.subject.digest.sha256 = SHA256(bytes(MANIFEST.json))`.

### (C) Provenance — `WITNESS_BUNDLES/*.json`
Independent witnesses sign the same canonical attestation and anchor it to a log entry.

### (D) Replay — `ARTIFACTS/*` (+ replay rule)
If deterministic replay artifacts exist, a verifier recomputes the step relation and inequality (or score) and fails on mismatch.

---

## 4. Formal Security Reductions (core theorems)

### Theorem 1 (Integrity)
If verification passes MANIFEST and SHA-256 is collision resistant, artifacts were not modified after the manifest was created.

*Reason:* modifying a file while preserving its hash implies a SHA-256 collision.

### Theorem 2 (Binding)
If verification passes ATTESTATION binding, the attestation is cryptographically bound to exactly that manifest.

*Reason:* any mismatch implies a collision on the manifest digest.

### Theorem 3 (k-of-n provenance soundness)
If verification accepts ≥k distinct witness bundles over the same attestation statement, then faking that provenance requires:
- forging ≥1 witness signature, OR
- breaking log append-only/chain membership, OR
- colluding/compromising ≥k witnesses.

---

## 5. The Trust-Debt Law (Corollary)
Let trust debt be unverifiable assumption burden.

A proofpack that passes:
- integrity,
- binding,
- k-of-n provenance,
- deterministic replay (when present),

collapses trust debt to:
1) **“≥k witnesses did not collude”**
2) **“verifier spec is honest and publicly inspectable.”**

Everything else reduces to breaking crypto primitives or failing replay.

---

## 6. Why this is “groundbreaking” (practically)
Existing practice signs *artifacts* or *models*.
Proofpacks sign **results** and enforce:
- what was run (integrity),
- what is claimed (binding),
- who witnessed it (k-of-n provenance),
- whether it replays (verification).

This is a supply-chain/security standard for **published claims**.

---

## 7. Demo in this repo
This repository includes:
- a deterministic toy “replay certificate”
- a k-of-n witness policy
- a transparency-style hash-chain log
- CI that generates + verifies the pack

Run:
```bash
python make_demo_pack.py
python verify_demo_pack.py

8. Production upgrades (v2 direction)

The same interfaces extend to:
	•	Sigstore keyless signing (Fulcio + Rekor inclusion proof)
	•	in-toto attestations (materials/products DAG)
	•	multi-log redundancy
	•	distributed RL shard packs merged by Merkle roots
	•	witness diversity policy and rotation

See ROADMAP.md.
