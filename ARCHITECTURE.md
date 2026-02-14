# Architecture

This document explains Proofpacks as a system: objects, flows, threat model, and the production upgrade path.

---

## 1) Components (VPS v1)

### Producer (Runner)
Generates artifacts and seals them into a Proofpack:

1. Writes `PROOFPACK/ARTIFACTS/*`
2. Computes `PROOFPACK/MANIFEST.json`
3. Writes `PROOFPACK/ATTESTATION.json` binding the manifest digest
4. Collects witness bundles `WITNESS_BUNDLES/*.json`
5. Writes `PROOFPACK/PROVENANCE_CERT.json` declaring k and bundle refs

### Witnesses (Quorum)
Each witness signs the canonical attestation statement and anchors it in a log:
- signature over `canon(ATTESTATION)`
- timestamp window (validity)
- log inclusion / membership proof (toy in v1)

### Verifier (Public)
Runs a deterministic PASS/FAIL pipeline defined in `VERIFIER.md`.

---

## 2) Data model (what binds to what)

Artifacts -> MANIFEST
- MANIFEST lists SHA256 of artifact files

MANIFEST -> ATTESTATION
- ATTESTATION.subject.digest.sha256 = SHA256(bytes(MANIFEST.json))

ATTESTATION -> WITNESS_BUNDLES
- each bundle commits statement_sha256 = SHA256(canon(ATTESTATION))
- each bundle signs the canonical attestation statement bytes

ATTESTATION + bundles -> PROVENANCE_CERT
- provenance cert binds the same manifest digest and requires k valid distinct witnesses

Optional: Replay
- artifacts include deterministic replay data and verifier checks replay rule

This is the “chain of custody” for result claims.

---

## 3) Why k-of-n is the killer feature
Single provenance is fragile:
- one key compromise
- one insider
- one flawed verifier

k-of-n forces the attack surface into an explicit, measurable boundary:
- to fake provenance, adversary must collude/compromise ≥k witnesses
- otherwise they must break crypto or log append-only guarantees

This turns reputation-based trust into a cryptographic threshold.

---

## 4) What VPS v1 proves (by construction)
- Integrity catches post-run edits
- Binding catches claim swapping
- Provenance catches forged/unauthorized attribution
- Replay catches fake evaluation results (when deterministically checkable)

The attack suite (`tools/attack_suite.py`) demonstrates this with three distinct FAIL modes.

---

## 5) Production upgrade path (VPS v2)

### Replace demo HMAC with Sigstore keyless signing
In v1:
- witness bundle uses local HMAC keys (portable, iPhone-safe demo)

In v2:
- witness bundle includes Sigstore materials:
  - Fulcio ephemeral cert chain
  - Rekor log index + inclusion proof
  - statement signature (Ed25519/ECDSA as per Sigstore)
Verifier checks:
- signature verifies under cert key
- cert is valid at Rekor integrated time
- Rekor inclusion proof validates

### Add in-toto attestations (pipeline DAG)
Attach in-toto metadata:
- materials (input datasets, code commits)
- products (models, logs, eval outputs)
- steps (train, eval, export)
Bind in-toto root digest into ATTESTATION to ensure:
- the claim is tied to a specific pipeline graph, not just a folder of files

### Multi-log redundancy
For high-stakes claims:
- publish witness bundles to ≥2 transparency logs
- verifier requires agreement or flags divergence

### Distributed RL / multi-node training
Use shard packs:
- each node emits a shard proofpack with its own artifacts and attestation
Global pack:
- Merkle root over shard digests
- global attestation commits to aggregation rule
k-of-n witnesses sign the global attestation

This prevents hidden “trust debt” in the cluster.

---

## 6) Operational model (who are witnesses?)
Witnesses can be:
- benchmark operators
- conference artifact-evaluation committees
- independent auditors
- multiple organizations in a “repro quorum”

Policy expresses diversity requirements (future):
- min number of independent issuers
- anti-sybil constraints
- rotation windows

---

## 7) Bottom line
Proofpacks are not “model signing.”
They are **result signing** with:
- artifact integrity
- claim binding
- k-of-n provenance
- deterministic replay (when possible)

That is the enforcement layer missing from AI progress reporting.
