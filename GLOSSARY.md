# Glossary

## Proofpack
A tamper-evident, replay-verifiable container for a **result claim**. It binds artifacts, claim, provenance, and (optionally) replay checks into a deterministic PASS/FAIL verification pipeline.

## Trust debt
The unverifiable assumption burden placed on readers/reviewers when results are published without enforceable provenance, binding, and replay.

## Artifact
A file produced or used by a run: configs, logs, rollouts, checkpoints, metrics, code snapshot pointers, dataset identifiers, etc.

## Manifest
`MANIFEST.json`: a list of `(path, sha256)` entries. Passing manifest verification means artifacts match their recorded hashes.

## Manifest digest
`d = SHA256(bytes(MANIFEST.json))`. Important: the digest is over the raw file bytes, not a parsed JSON object.

## Attestation
`ATTESTATION.json`: the canonical statement of “what is claimed,” which binds to `d` via:
`ATTESTATION.subject.digest.sha256 = d`.

## Canonicalization (canon)
A deterministic JSON encoding:
- sorted keys
- no whitespace
- UTF-8
Used so all witnesses sign identical bytes.

## Statement hash
`stmt_hash = SHA256(canon(ATTESTATION))`

## Witness
An independent signer who attests to the same canonical statement. In production this is Sigstore keyless signing or an org key. In this demo it is HMAC-SHA256 for portability.

## Witness bundle
A signed record containing:
- witness identity
- statement hash
- signature over canonical attestation bytes
- certificate validity window
- log anchoring (toy hash-chain in v1)

## k-of-n provenance
A proofpack passes provenance only if ≥k distinct witness bundles validate the same statement. This turns provenance into a measurable threshold.

## Transparency log
A public append-only log used to prevent “sign then deny.” In v1 this repo includes a toy hash-chain; in v2 it maps to Rekor (and optionally other logs).

## Replay
A deterministic verification rule that recomputes the claim outcome from published artifacts. Replay is optional in the standard, but mandatory to run when present.

## Shard pack
A proofpack emitted by one node in distributed training (e.g., per-GPU/per-rank). Global packs can Merkle-commit to shard digests.

## Global pack
A proofpack that commits to a Merkle root over shard pack digests and attests to an aggregation rule across shards.
