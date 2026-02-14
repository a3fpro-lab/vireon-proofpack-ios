# Security Model

This repo demonstrates the **Proofpack** idea: cryptographic verification of **result claims** under deterministic **PASS/FAIL** verification.

## Threats covered
- **Artifact tampering** (post-run edits, swapped traces, changed configs/metrics)
- **Claim swapping** (attestation no longer binds the artifact digest)
- **Single-witness compromise** (k-of-n requires multiple distinct witnesses)
- **Log rewriting** (append-only hash-chain breaks if history is edited)
- **Replay fraud** (deterministic re-check fails when replay artifacts exist)

## Residual assumptions
- **SHA-256 collision resistance**
- **Signature scheme security**
  - Demo: local **HMAC-SHA256** witness bundles (portable)
  - Production: **Ed25519/Sigstore** (planned upgrade path)
- **≥k witnesses do not collude**
- **Verifier spec is honest and publicly inspectable**

## Trust Debt (definition)
**Trust debt** is the unverifiable assumption burden shifted to readers/reviewers (“trust me”).

Proofpacks collapse trust debt to the smallest remaining assumptions:
- **k witnesses didn’t collude**
- **verifier spec matches the claimed policy**

Everything else becomes mechanical **PASS/FAIL**:
- any post-publication change to artifacts → `integrity:SHA_MISMATCH:<path>`
- any claim/manifest mismatch → `binding:ATTESTATION_DIGEST_MISMATCH`
- insufficient valid witness bundles → `provenance:ONLY_<n>_VALID`

---

# Security Policy

## Reporting a vulnerability
If you believe you found a security issue in VPS / proofpack verification:
- Open a **GitHub Security Advisory** (preferred), or
- Open an issue labeled **security**.

Please include:
- affected file(s)
- steps to reproduce (exact commands)
- expected vs actual verifier output
- a minimal proofpack sample (or diffs) that triggers the issue
- repo commit hash / release tag (e.g., `v1.0.0`)

## Scope
This repo is a reference implementation and spec. Security issues include:
- verifier accepting a **forged/tampered** proofpack as PASS
- bypassing **hash / log / signature** validation
- bypassing schema/policy checks in a way that changes verification meaning
- causing nondeterministic verifier behavior (PASS/FAIL depends on machine state)

Non-security issues include:
- performance tuning requests
- missing features (tracked as enhancements)
- threats explicitly listed as residual assumptions (e.g., ≥k witness collusion)
