# Vireon Proofpack Standard (VPS) v1.0.0 — Ratified

## Scope
VPS defines the minimal, enforceable objects and verification rules required to publish a **result claim** with deterministic **PASS/FAIL** verification.

A VPS proofpack is valid only if an independent verifier can re-run the verification rules and obtain PASS.

---

## Normative objects (MUST)

A conforming proofpack MUST include:

1) `PROOFPACK/MANIFEST.json`  
   Lists SHA-256 digests for required artifacts.

2) `PROOFPACK/ATTESTATION.json`  
   A claim statement that MUST bind to the manifest digest.

3) `WITNESS_BUNDLES/*.json`  
   Witness bundles that commit to the same canonical statement and include a verifiable signature and log anchor.

4) `PROOFPACK/PROVENANCE_CERT.json`  
   Declares threshold `k` and the witness bundle references; MUST bind to the same manifest digest.

If replay artifacts exist, the proofpack MUST specify replay acceptance conditions in artifacts and the verifier MUST enforce them.

---

## Canonicalization (MUST)

Witness signatures MUST be computed over canonical JSON bytes:

- UTF-8
- keys sorted
- separators `(",", ":")` (no whitespace)

This ensures all witnesses sign identical bytes.

Let `canon(x)` be this canonicalization.

---

## Verification order (MUST)

A verifier MUST apply rules in this order and FAIL immediately on the first failure:

1) **Integrity**: manifest file hashes match artifact bytes  
2) **Binding**: attestation digest matches manifest digest  
3) **Provenance**: ≥k distinct valid witness bundles for the same statement  
4) **Replay**: if replay artifacts exist, replay verification passes

This order is normative to prevent “partial PASS” ambiguity.

---

## Binding formulas (normative)

Let \(H\) be SHA-256 and \(M\) be the raw bytes of `MANIFEST.json`.

Manifest digest:
\[
d = H(M)
\]

Binding requirement:
\[
\texttt{ATTESTATION.subject.digest.sha256} = d
\]

Provenance cert binding requirement:
\[
\texttt{PROVENANCE\_CERT.subject\_digest\_sha256} = d
\]

Statement hash:
\[
s = H(\text{canon}(\texttt{ATTESTATION}))
\]

k-of-n requirement:
Verifier MUST accept provenance only if ≥k distinct witness IDs provide valid bundles for the same statement hash \(s\).

---

## Security boundary (normative claim)

If a proofpack verifies PASS, then forging the claim without detection requires:
- breaking SHA-256 collision resistance, OR
- forging witness signatures, OR
- breaking log membership / append-only guarantees, OR
- colluding/compromising ≥k witnesses.

This is the enforced **Trust-Debt Law** boundary for published results.

---

## Reference implementation
This repository provides:
- a stdlib-only verifier (`vproofpack.py`)
- an installable CLI (`vps`)
- an attack suite demonstrating expected FAIL modes
- pinned test vectors with a locked root digest

---

## Compliance matrix (VPS v1.0.0)

A proofpack/verifier pair is VPS-compliant if all applicable checks PASS.

### Proofpack requirements
- [ ] MANIFEST exists and hashes all required artifacts
- [ ] ATTESTATION exists and binds to MANIFEST digest
- [ ] PROVENANCE_CERT exists, binds to MANIFEST digest, declares k and bundle refs
- [ ] Witness bundles exist, sign canonical attestation, include log anchor
- [ ] Replay artifacts (if present) are sufficient for deterministic verification

### Verifier requirements
- [ ] Deterministic canonicalization (`canon`)
- [ ] Integrity check over MANIFEST entries
- [ ] Binding check (ATTESTATION → MANIFEST digest)
- [ ] k-of-n provenance check (distinct witness IDs, valid bundles)
- [ ] Log membership verification
- [ ] Replay verification when artifacts exist
- [ ] Ordered FAIL-fast semantics

### Policy extensions (optional)
Additional policies MAY be enforced (issuer diversity, max window, multi-log). These are defined in `POLICY.md` and MUST NOT weaken baseline VPS acceptance criteria.

---

## Test vectors (normative for this repo)
This repo includes pinned test vectors:
- `test_vectors/v1_pack`

CI regenerates them and verifies the locked root digest. If the digest changes, VPS v1 behavior has changed and MUST require a version bump (v1.0.1 or v1.1.0).
