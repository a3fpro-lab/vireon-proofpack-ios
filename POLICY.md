# Witness Policy (VPS v1.0.0)

This file defines policy rules that a verifier MAY enforce in addition to `VERIFIER.md`.
In VPS v1, the only mandatory policy field is `k` from `PROVENANCE_CERT.json`.
This document specifies stricter policies for high-stakes claims.

---

## 1) Threshold (k-of-n) — REQUIRED BY VPS v1
Let:
- \(k\) be `PROVENANCE_CERT.k`
- bundles list witnesses and bundle paths

A verifier MUST require ≥k distinct witness IDs with valid bundles for the same canonical attestation.

---

## 2) Issuer diversity (recommended)
To reduce collusion risk, require witnesses to span multiple issuers.

### Rule
Let `issuer(w)` be the witness bundle issuer string.

Policy:
- require at least `min_distinct_issuers ≥ 2` among the accepted k bundles.

Fail provenance if k signatures are all from one issuer.

---

## 3) Time-window policy (recommended)
Witness bundle cert windows bound the signing validity.

### Rule
For each accepted witness bundle:
- `integrated_time` MUST satisfy:
\[
nb \le \tau \le na
\]
where \(nb=\texttt{not\_before}\), \(na=\texttt{not\_after}\), \(\tau=\texttt{integrated\_time}\).

For high stakes, require:
- `max_window_seconds ≤ 86400` (24 hours)
so signatures must be anchored promptly.

---

## 4) Multi-log redundancy (v2-ready recommendation)
VPS v1 demo uses a toy offline log.
In production, policy SHOULD require anchoring to multiple transparency logs.

### Rule (conceptual)
For each accepted bundle:
- provide inclusion proofs for ≥L logs (e.g., Rekor + secondary log)
- if logs disagree, flag the claim as disputed.

Suggested:
- `L ≥ 2`

---

## 5) Rotation / replay-resistance (recommended)
To prevent static witness capture:
- rotate witness identities on a schedule (e.g., weekly/monthly)
- require that at least 1 witness in the k-set is “fresh” (new key within window)

This reduces long-term key compromise risk.

---

## 6) Practical mapping
A realistic deployment can set:
- k = 2 for normal claims
- k = 3+ for leaderboards / regulated domains
- min_distinct_issuers = 2
- max_window_seconds = 86400
- multi-log = 2 (production)

These policies don’t change the core VPS objects; they tighten verifier acceptance rules.
