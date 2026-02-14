# RFC: Vireon Proofpack Standard (VPS) v1.0.0
Status: Proposed Standard (Reference Implementation Included)  
Date: 2026-02-13

## Abstract
VPS defines a tamper-evident container and verification procedure for publishing **result claims** with deterministic PASS/FAIL verification. VPS binds artifact integrity, claim binding, k-of-n provenance, transparency log anchoring, and optional replay verification into a single enforceable envelope.

## 1. Terminology
- **Proofpack**: directory containing VPS objects and artifacts.
- **Verifier**: program that evaluates a proofpack and outputs PASS/FAIL.
- **Witness**: entity that signs the canonical claim statement.
- **k-of-n**: threshold provenance policy requiring ≥k distinct witnesses.
- **Trust debt**: unverified reliance on “trust me” claims.

Normative terms **MUST**, **SHOULD**, **MAY** are as in RFC 2119.

## 2. Goals
- Make published result claims mechanically verifiable.
- Reduce trust debt to a clear cryptographic boundary.
- Enable independent verifier implementations (interop).
- Support offline/airgapped verification (toy log in reference build).

## 3. Non-Goals
- VPS does not require deterministic training for all domains.
- VPS does not mandate a specific signature scheme (HMAC/Ed25519/Sigstore acceptable).
- VPS does not define a global PKI; it defines verification semantics.

## 4. Data Model (Required Objects)

### 4.1 MANIFEST.json (Integrity)
Contains `{path, sha256}` entries for required artifacts.
Verifier MUST recompute SHA256 over raw file bytes.

### 4.2 ATTESTATION.json (Binding)
Contains:
- `subject.digest.sha256` = digest of raw MANIFEST bytes
- `policy.requirements` (human-readable requirements list)
- `nonce` (freshness discriminator)

### 4.3 WITNESS_BUNDLES (Provenance)
Each bundle MUST contain:
- `statement_sha256` = SHA256(canon(ATTESTATION))
- `signature` over `canon(ATTESTATION)` bytes
- `certificate.not_before/not_after` validity bounds
- `log` anchor for transparency membership verification

### 4.4 PROVENANCE_CERT.json (Threshold)
Contains:
- `k` threshold
- `subject_digest_sha256` binding to MANIFEST digest
- list of bundle references

## 5. Canonicalization
`canon(x)` MUST be deterministic JSON serialization:
- UTF-8
- sorted keys
- no whitespace (separators `(",", ":")`)

Witness signatures MUST be computed over `canon(ATTESTATION)` bytes.

## 6. Verification Procedure (Normative)
Verifier MUST apply checks in order:

1) Integrity:
- load MANIFEST
- verify each file exists and SHA256(file bytes) matches

2) Binding:
- compute `d = SHA256(bytes(MANIFEST.json))`
- require `ATTESTATION.subject.digest.sha256 == d`

3) Provenance:
- load PROVENANCE_CERT
- require `PROVENANCE_CERT.subject_digest_sha256 == d`
- require `PROVENANCE_CERT.k == k` for the run
- compute `s = SHA256(canon(ATTESTATION))`
- validate witness bundles; accept only if ≥k distinct witness IDs are valid for the same `s`

4) Replay (optional):
- if replay artifacts exist, verifier MUST execute replay checks and FAIL on violation

Verifier MUST be FAIL-fast and MUST produce an unambiguous reason code.

## 7. Security Considerations

### 7.1 Threat model
Adversary may:
- tamper with artifacts after publication
- swap manifests/attestations
- inject counterfeit witness bundles
- attempt log equivocation or membership forgery
- attempt replay spoofing via inconsistent artifacts

### 7.2 Integrity
Tampering detection reduces to SHA-256 preimage/collision resistance.

### 7.3 Binding
Manifest substitution without detection requires breaking SHA-256 binding (collision or second-preimage).

### 7.4 Provenance (k-of-n)
Forging provenance without detection requires one of:
- signature forgery, or
- breaking canonicalization equivalence, or
- log membership forgery / append-only failure, or
- colluding/compromising ≥k witnesses.

### 7.5 Replay
Replay checks provide domain-specific integrity of execution traces when artifacts permit deterministic verification. Replay is OPTIONAL but, if present, MUST be enforced.

### 7.6 Residual trust boundary (Trust-Debt Law)
After PASS, residual trust debt collapses to:
**“k witnesses didn’t collude + verifier spec is honest.”**

## 8. Interoperability
Independent verifier implementations MUST match:
- canonicalization
- raw-byte hashing semantics
- verification order
- witness bundle signature inputs

Interop guidance and pinned vectors are provided in `INTEROP.md` and `test_vectors/`.

## 9. Versioning
Any change that alters:
- canonicalization,
- hashing inputs,
- verification semantics,
- required object fields,
MUST bump the VPS version and regenerate pinned vectors.

## 10. Reference Implementation
This repository includes:
- stdlib-only reference verifier (`vproofpack.py`)
- CLI (`vps`) for generation and verification
- attack suite demonstrating expected FAIL modes
- pinned test vectors verified in CI
