# Verifier Rules (PASS/FAIL)

A verifier MUST execute the following pipeline in order.

## 1) Integrity (MANIFEST)
Input: `PROOFPACK/MANIFEST.json`

For each entry `{path, sha256}`:
- read bytes of `PROOFPACK/<path>`
- compute SHA-256
- FAIL if mismatch or missing file

PASS this stage iff all entries match.

## 2) Binding (ATTESTATION → MANIFEST)
Input: `PROOFPACK/ATTESTATION.json`

Compute:
`d = SHA256(bytes(PROOFPACK/MANIFEST.json))`

FAIL unless:
`ATTESTATION.subject.digest.sha256 == d`

## 3) Provenance (k-of-n witnesses)
Input: `PROOFPACK/PROVENANCE_CERT.json` + `WITNESS_BUNDLES/*.json`

Requirements:
- `PROVENANCE_CERT.subject_digest_sha256 == d`
- let `k = PROVENANCE_CERT.k`
- for each bundle referenced:
  - FAIL bundle if statement hash != SHA256(canon(ATTESTATION))
  - FAIL bundle if signature invalid on canon(ATTESTATION)
  - FAIL bundle if integrated_time outside cert window [not_before, not_after]
  - FAIL bundle if log membership cannot be proven (hash-chain membership)
- PASS this stage iff ≥k distinct witness_ids have valid bundles

## 4) Replay (optional but enforced if present)
If `PROOFPACK/ARTIFACTS/RUN.json` exists:
- verifier MUST recompute the step relation and inequality for every step record
- FAIL on any mismatch

## PASS criteria
Verifier returns PASS iff all applicable stages PASS.
