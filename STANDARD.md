# Vireon Proofpack Standard (VPS) v1.0.0 — Ratified

## Scope
VPS defines the minimal, enforceable objects and verification rules required to publish a **result claim** with deterministic PASS/FAIL verification.

## Normative objects (MUST)
A conforming proofpack MUST include:

1) `PROOFPACK/MANIFEST.json`  
   Contains SHA-256 digests for required artifacts.

2) `PROOFPACK/ATTESTATION.json`  
   Contains a claim statement and MUST bind to the manifest digest.

3) `WITNESS_BUNDLES/*.json`  
   Each bundle MUST commit to the same canonical attestation statement and include a verifiable signature and log anchor.

4) `PROOFPACK/PROVENANCE_CERT.json`  
   Declares threshold `k` and the witness bundle references; MUST bind to the same manifest digest.

## Canonicalization (MUST)
Witness signatures MUST be computed over the canonical JSON bytes:
- UTF-8
- keys sorted
- no whitespace
This ensures all witnesses sign identical bytes.

## Verification (MUST)
A verifier MUST implement the PASS/FAIL rules in `VERIFIER.md` in order:
1) integrity (manifest)
2) binding (attestation → manifest digest)
3) provenance (k-of-n witness bundles + log checks)
4) replay (if replay artifacts exist)

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

## Security boundary (normative claim)
If a proofpack verifies PASS, then forging the claim without detection requires:
- breaking SHA-256 collision resistance, OR
- forging witness signatures, OR
- breaking log membership/append-only guarantees, OR
- colluding/compromising ≥k witnesses.

This is the enforced **Trust-Debt Law** boundary for published results.

## Reference implementation
This repository provides a reference implementation and test vectors. The CI workflow constructs and verifies a conforming proofpack on every push/PR.
