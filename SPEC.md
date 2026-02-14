# Vireon Proofpack Standard (VPS) v1.0

A **proofpack** is a cryptographic, replay-verifiable receipt for a result claim.  
Goal: turn “trust me” into **PASS/FAIL** verification with minimal assumptions.

## Core problem it solves (Trust Debt)
Modern AI/RL results create **trust debt**: unverifiable dependence on hidden code, hidden settings, hidden compute, and unverifiable provenance.

**VPS reduces trust debt** by binding:
1) artifacts (what was run),
2) attestation (what is being claimed),
3) provenance (who witnessed it),
4) replay (can an independent verifier recompute the claim).

## Objects

### 1) PROOFPACK/MANIFEST.json (Integrity)
Lists SHA-256 digests of artifacts.

**Rule**: verification MUST recompute and match all listed digests.

### 2) PROOFPACK/ATTESTATION.json (Binding)
A canonical statement that binds to the manifest digest:

`ATTESTATION.subject.digest.sha256 = SHA256(bytes(MANIFEST.json))`

**Rule**: verification MUST recompute this digest and require equality.

### 3) WITNESS_BUNDLES/*.json (k-of-n provenance)
Independent witness bundles sign the canonical attestation statement and anchor it to a log entry.

**Rule**: verification MUST accept only if ≥k distinct witness IDs validate the same attestation.

### 4) PROOFPACK/PROVENANCE_CERT.json (Policy)
Declares the required k and which bundles are eligible.

**Rule**: verification MUST ensure the cert binds to the same manifest digest.

### 5) Replay artifacts (Replay)
A pack MAY include deterministic replay artifacts and a verifier rule that must pass.

**Rule**: if replay artifacts are present, verification MUST run replay and fail on any mismatch.

## Formal security claims (informal but rigorous)

### Theorem A (Manifest integrity ⇒ tamper detection)
If MANIFEST passes and SHA-256 is collision resistant, then artifacts were not modified since manifest creation.

### Theorem B (Attestation binding)
If ATTESTATION binds to MANIFEST digest, then the attestation is cryptographically bound to the exact artifact set.

### Theorem C (k-of-n provenance soundness)
If ≥k distinct witness bundles verify the same statement, then faking provenance requires either:
- forging signatures, OR
- breaking log append-only/chain membership, OR
- colluding/compromising ≥k witnesses.

### Corollary (Trust-Debt Law)
A VPS-verified claim collapses trust debt to:
- “k witnesses didn’t collude”
- “verifier spec is honest”

Everything else reduces to breaking cryptographic primitives or failing deterministic replay.

## Extension hooks (future)
VPS intentionally supports upgrades without breaking the core:
- Sigstore/Rekor keyless signing bundles
- in-toto attestations (materials/products DAG)
- SLSA provenance mapping
- Multi-log redundancy
- Distributed RL: node shard packs merged by Merkle roots
