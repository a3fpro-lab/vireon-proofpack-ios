# Security Model

This repo demonstrates the **Proofpack** idea: cryptographic verification of result claims.

## Threats covered
- Artifact tampering (post-run edits, swapped traces, changed configs)
- Claim swapping (attestation not matching artifacts)
- Single-witness compromise (k-of-n requires multiple)
- Log rewriting (hash-chain breaks if history edited)
- Replay fraud (deterministic re-check fails)

## Residual assumptions
- SHA-256 collision resistance
- Signature scheme security (demo uses local HMAC; production uses Ed25519/Sigstore)
- ≥k witnesses are not colluding
- Verifier spec is honest and publicly inspectable

## Trust Debt (definition)
Trust debt is the unverifiable assumption burden shifted to readers/reviewers.

Proofpacks collapse trust debt to the smallest remaining assumptions:
- k witnesses didn’t collude
- verifier spec matches the claimed policy
Everything else becomes PASS/FAIL.
