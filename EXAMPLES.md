# Examples (what Proofpacks catch)

This file shows how Proofpacks scale beyond the toy replay demo.

---

## Example 1 — CartPole RL (single node)

### Claim
> “Policy achieves avg reward ≥ 475 over 100 eval episodes on CartPole-v1.”

### Proofpack contents
- `ARTIFACTS/`
  - `code/` (exact training script snapshot or commit id)
  - `config.json` (env params, seeds, hyperparams)
  - `rollouts/` or `eval.json` (episode returns)
  - `MODEL.bin` (policy weights)
- `MANIFEST.json` hashes everything above
- `ATTESTATION.json` binds the manifest digest and states the claim
- `WITNESS_BUNDLES/*.json` provide k-of-n provenance

### Verification
PASS requires:
- all hashes match (no post-run edits),
- attestation digest binds the exact artifacts,
- ≥k witnesses signed the same statement,
- evaluation replay rule checks:
  - env id matches,
  - seeds/config match,
  - reward average computed from included eval logs meets threshold.

### Non-determinism handling
You *don’t* claim “exact weights match” across hardware.
You claim “included evaluation logs + deterministic evaluator rules produce the score.”
If training is nondeterministic, **the proofpack still works** because it pins *the produced artifacts* and proves the claimed score from them.

---

## Example 2 — Distributed RL (multi-GPU, many nodes)

### Problem
Distributed training creates “trust debt” via:
- per-node drift (different code, different data),
- hidden gradient tampering (one node injects poison),
- silent checkpoint swaps.

### Solution: shard packs + global merge
Each node produces a **Shard Proofpack**:

`node_i_pack/`
- `ARTIFACTS/`
  - `node_config.json` (rank, seed, device, commit)
  - `grad_chunk.bin` (or gradient stats)
  - `step_metrics.jsonl` (loss, norm, updates)
- `MANIFEST.json` hashes shard artifacts
- `ATTESTATION.json` binds shard manifest and states:
  - “At step t, my gradient summary == G_i and norm <= N”
- witness bundles (local or cross-node)

A coordinator (or peer quorum) produces a **Global Proofpack** that includes:
- list of shard manifest digests
- Merkle root over all shard digests
- global attestation:
  - “Global update U_t equals aggregation(A(shard_i))”
- k-of-n witness provenance over the global statement

### How “tampered gradient” is caught
If one node swaps `grad_chunk.bin` after the run:
- shard MANIFEST fails (hash mismatch) → FAIL.

If one node lies about its gradient stats:
- shard replay rule recomputes stats from artifact → FAIL.

If a coordinator omits or replaces shard digests:
- global Merkle root mismatch → FAIL.

If a malicious node submits a shard with inconsistent statement:
- its shard attestation hash differs → it can’t be included in the global statement without breaking signatures.

Result: “trust me, the cluster did the right thing” becomes **PASS/FAIL**.

---

## Example 3 — Preventing “trust debt” in robotics multi-agent training

### Scenario
Multi-agent policies trained with:
- multiple simulators,
- stochastic perturbations,
- distributed rollouts.

### Proofpack approach
- Each rollout generator publishes a shard proofpack:
  - simulator version, scene hash, perturbation seed stream hash
- A global pack binds the ensemble:
  - set of rollouts used
  - aggregated metrics computed from those rollouts
- Witness policy requires independent verification nodes to sign:
  - “rollouts + metric rule reproduce reported score”

This flags:
- missing rollouts,
- swapped scenes,
- selective reporting,
- post-hoc “metric edits.”

---

## Bottom line
Proofpacks don’t require training to be deterministic.
They require **published claims** to be cryptographically bound to **the actual artifacts** and (when possible) to a deterministic evaluation/replay rule.
