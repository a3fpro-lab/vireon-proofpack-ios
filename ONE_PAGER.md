# VPS v1 in one page

## Problem: Trust debt
Modern ML/RL results ship as “trust me” bundles: code + weights + charts.  
Even honest teams accumulate **trust debt** because replay is hard, environments drift, and provenance is unclear.

## Solution: Proofpacks
A **proofpack** is a tamper-evident, replay-verifiable container for a *result claim*.

VPS binds:
1) **Integrity**: `MANIFEST.json` (SHA-256 over artifact bytes)  
2) **Binding**: `ATTESTATION.json` binds to manifest digest  
3) **Provenance**: ≥k witness bundles sign the same canonical claim  
4) **Transparency**: log anchoring (offline toy in ref build; Rekor in production)  
5) **Replay (optional)**: deterministic verification when artifacts permit

## Trust-Debt Law (boundary)
If a proofpack verifies PASS, then forging the claim without detection requires:
- breaking SHA-256/signatures/log membership, OR
- colluding/compromising ≥k witnesses.

Residual trust debt collapses to:
**“k witnesses didn’t collude + verifier spec is honest.”**

## Why this matters
- Conferences/leaderboards can require VPS for SOTA claims.
- Labs can publish results with a cryptographic audit trail.
- Reviewers get PASS/FAIL instead of vibes.

## 10-second demo
```bash
pip install .
vps make-demo --out demo_pack_cli
vps verify demo_pack_cli --k 2

Standard docs
	•	RFC.md (IETF-style spec)
	•	STANDARD.md (normative rules + compliance matrix)
	•	THREAT_MODEL.md (attack → detector → FAIL code)
	•	INTEROP.md (implement verifier anywhere + match vectors)

---

## FILE 62 — `examples/PUBLISH_WALKTHROUGH.md`
Create: `examples/PUBLISH_WALKTHROUGH.md`  
Paste → Commit:

```md
# Publish a result claim with VPS (walkthrough)

This is the minimal publisher flow.

## 1) Produce artifacts
Put your artifacts under:
`<pack>/PROOFPACK/ARTIFACTS/`

Artifacts can be:
- run traces
- metrics
- model checkpoints (optional)
- environment params
- any file you want to bind to the claim

## 2) Seal integrity (MANIFEST)
Compute SHA-256 for each artifact and write:
`PROOFPACK/MANIFEST.json`

## 3) Bind the claim (ATTESTATION)
Write `PROOFPACK/ATTESTATION.json` such that:
- `subject.digest.sha256 = SHA256(raw bytes of MANIFEST.json)`
- the claim requirements are explicit

## 4) Collect witness bundles (k-of-n)
Each witness signs the canonical attestation bytes and produces a bundle:
`WITNESS_BUNDLES/<witness_id>.json`

## 5) Issue provenance cert
Write `PROOFPACK/PROVENANCE_CERT.json`:
- `k`
- `subject_digest_sha256` = manifest digest
- references to witness bundle paths

## 6) Publish
Publish the whole pack directory in the repo or as a release asset.

## 7) Verification
Anyone runs:
```bash
vps verify <pack_dir> --k <k>

For strict policy:
vps verify-strict <pack_dir> --k <k> --min-issuers 2 --max-window 86400
---

## FILE 63 — `examples/VERIFY_IN_ONE_COMMAND.md`
Create: `examples/VERIFY_IN_ONE_COMMAND.md`  
Paste → Commit:

```md
# Verify in one command

Install + verify the reference vectors:

```bash
pip install .
python tools/generate_test_vectors.py
python tools/verify_test_vectors.py
Expected output includes:
	•	PASS for test_vectors/v1_pack
	•	locked VECTOR_ROOT_SHA256 match
---

## README upgrade (make it hit fast)
Edit `README.md` and put this at the very top (above everything else). Replace your opening section with this:

```md
**Trust-Debt Law:** a verified proofpack collapses “trust me” to **“k witnesses didn’t collude + verifier spec is honest.”**  
![proofpack-ci](../../actions/workflows/ci.yml/badge.svg) ![license](https://img.shields.io/badge/license-MIT-green) ![release](https://img.shields.io/badge/release-v1.0.0-blue)

# vireon-proofpack-ios (VPS v1.0.0)

VPS is a **deployable standard** for publishing *result claims* with deterministic **PASS/FAIL** verification.

## 10-second demo
```bash
pip install .
vps make-demo --out demo_pack_cli
vps verify demo_pack_cli --k 2
What PASS means

PASS implies:
	1.	artifacts match MANIFEST.json (integrity)
	2.	ATTESTATION.json binds manifest digest (binding)
	3.	≥k witness bundles validate the same canonical claim (k-of-n provenance)
	4.	transparency log membership checks out (toy offline log here)
	5.	replay checks pass when artifacts permit (toy demo included)

Standard docs
	•	RFC.md
	•	STANDARD.md
	•	THREAT_MODEL.md
	•	INTEROP.md
	•	VERIFIER_PSEUDOCODE.md
	•	ONE_PAGER.md
