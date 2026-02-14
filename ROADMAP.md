# Roadmap (VPS v1 → v2)

## v1 (this repo)
- Integrity: MANIFEST over artifacts
- Binding: ATTESTATION binds MANIFEST digest
- Provenance: k-of-n witness bundles
- Log: offline hash-chain (toy transparency log)
- Replay: deterministic toy replay certificate

## v1.1
- JSON Schemas enforced in CI
- Replay engine interface for RL environments (CartPole spec)

## v2.0 (production)
- Sigstore keyless signing bundles (Fulcio + Rekor inclusion proof)
- in-toto attestations for pipeline materials/products DAG
- Multi-log redundancy (Rekor + additional logs)
- Distributed RL: node shard packs merged by Merkle roots
- Witness diversity policy (anti-sybil + rotation)
