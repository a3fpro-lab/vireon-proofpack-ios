# Interop (Independent Verifier Implementation)

This document explains how to implement a VPS v1 verifier in any language and match the pinned test vectors.

---

## 1) The only “gotchas” that break interop

### A) Canonical JSON must match exactly
Canonicalization MUST be:
- UTF-8
- keys sorted recursively
- separators exactly `(",", ":")`
- no whitespace
- no escaping changes beyond standard JSON

If your language’s JSON library can’t do this reliably, write a tiny canonicalizer.

### B) Hash the raw bytes of MANIFEST.json
Binding digest is:
\[
d = \text{SHA256}(\text{raw bytes of MANIFEST.json})
\]
Do NOT re-serialize the manifest and hash that; hash the file bytes as stored.

### C) File hashing is SHA256 over raw bytes
For each manifest entry:
- compute SHA256(file bytes)
- compare to manifest value

### D) Log membership
For this repo’s vectors, the log is a local hash-chain:
- each entry commits to `prev`, `integrated_time`, `statement_sha256`
- membership means the claimed entry hash exists in the `.chain.jsonl` file

---

## 2) Minimal verifier algorithm (portable)

Inputs:
- `root_dir`
- `k`

Output:
- PASS or FAIL with a reason code

### Step 1 — Integrity
- load `PROOFPACK/MANIFEST.json`
- for each `{path, sha256}`:
  - compute `SHA256(bytes(PROOFPACK/path))`
  - if missing → FAIL `MISSING:<path>`
  - if mismatch → FAIL `SHA_MISMATCH:<path>`

### Step 2 — Binding
- read raw bytes of `PROOFPACK/MANIFEST.json`
- compute `d = SHA256(manifest_bytes)`
- load `PROOFPACK/ATTESTATION.json`
- require `ATTESTATION.subject.digest.sha256 == d`
- else FAIL `ATTESTATION_DIGEST_MISMATCH`

### Step 3 — k-of-n Provenance
- load `PROOFPACK/PROVENANCE_CERT.json`
- require `PROVENANCE_CERT.subject_digest_sha256 == d`
- require `PROVENANCE_CERT.k == k` (for the run’s k)
- compute `s = SHA256(canon(ATTESTATION))`
- for each bundle ref:
  - load bundle JSON
  - require `bundle.statement_sha256 == s`
  - verify signature over `canon(ATTESTATION)` bytes
  - require `not_before <= integrated_time <= not_after`
  - verify log membership
- accept only if ≥k distinct witness IDs are valid
- else FAIL `ONLY_<n>_VALID`

### Step 4 — Replay (if present)
If `PROOFPACK/ARTIFACTS/RUN.json` exists:
- load `RUN.json` and `trace.json`
- recompute deterministic next-step and inequality per spec
- else FAIL with replay reason

---

## 3) Matching this repo’s pinned test vectors

This repo pins:
- `test_vectors/v1_pack`

To check you match:
1) Your verifier must return PASS for `test_vectors/v1_pack` with k=2
2) Compute the vector root digest:
   - For every file under `test_vectors/v1_pack`, compute `SHA256(file bytes)`
   - Make lines: `relpath sha256`
   - Join with `\n`
   - Hash the joined bytes with SHA256
3) Your computed root must match the repo’s expected value (see `tools/verify_test_vectors.py`).

If you match, your implementation is interop-correct for VPS v1 behavior.

---

## 4) Cryptography notes
This repo uses **HMAC-SHA256 local witnesses** for portability and demo vectors. Production deployments should replace this with:
- Ed25519 signatures OR Sigstore keyless signing + Rekor inclusion proofs
without changing the verification pipeline structure.
