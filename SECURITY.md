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

# Security Policy

## Reporting a vulnerability
If you believe you found a security issue in VPS / proofpack verification:
- Open a GitHub Security Advisory (preferred), or
- Open an issue labeled **security**.

Please include:
- the affected file(s)
- steps to reproduce
- expected vs actual behavior
- any proofpack sample that triggers the issue

## Scope
This repo is a reference implementation and spec. Security issues include:
- verifier accepting a forged/tampered proofpack
- hash/log/signature validation bypass
- schema validation bypass that changes verification meaning
