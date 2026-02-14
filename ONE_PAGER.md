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
