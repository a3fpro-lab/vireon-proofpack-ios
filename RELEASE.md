# Release: VPS v1.0.0

## What this is
A deployable standard + reference implementation for **verifiable result claims**.

## What’s included
- Proofpack objects: MANIFEST, ATTESTATION, WITNESS_BUNDLES, PROVENANCE_CERT
- k-of-n provenance policy
- offline transparency-style hash-chain log
- deterministic replay certificate (toy) + verifier rule
- CI that generates + verifies a pack on every push/PR
- Schemas + verifier spec + security model + test vectors
- Attack suite demonstrating FAIL modes for distinct tamper classes

## What’s novel
This is not just model signing.
It binds **results** to **artifacts**, **provenance**, and **replay** under PASS/FAIL verification.

## Next (v2)
- Sigstore/Rekor keyless bundles
- in-toto attestations (pipeline DAG)
- Multi-log redundancy
- Distributed RL shard packs merged by Merkle roots
