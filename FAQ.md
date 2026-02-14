# FAQ (Proofpacks / VPS v1)

## What’s the one core problem this solves?
**Trust debt**: readers must “trust” that artifacts, configs, runs, and reported metrics weren’t altered, swapped, cherry-picked, or misattributed. Proofpacks make result claims **verifiable** with a deterministic PASS/FAIL verifier.

## What exactly is verified?
VPS v1 verifies four layers (see `VERIFIER.md`):
1) **Integrity**: `MANIFEST.json` matches artifact hashes (SHA-256).
2) **Binding**: `ATTESTATION.json` binds to the exact manifest digest.
3) **Provenance**: ≥k distinct witness bundles validate the same attestation.
4) **Replay** (if present): verifier recomputes a deterministic rule from artifacts.

## Does this require training determinism?
No. Proofpacks do not require deterministic training. They require **deterministic verification** of the published claim from the published artifacts (e.g., eval logs, metric rule, seeds for evaluation, etc.). If training is nondeterministic, the pack still pins the produced artifacts and proves the claim from them.

## What’s the minimal cryptography here?
- Hash: SHA-256.
- Demo witness signatures: HMAC-SHA256 (portable, stdlib-only).
Production (v2): swap witness signature block to Sigstore keyless signing + Rekor inclusion proof (see `ARCHITECTURE.md`).

## What does k-of-n actually buy you?
It replaces “one key / one org says it’s fine” with a **threshold**:
Verification passes only if ≥k *distinct* witnesses signed the same attestation statement. Fraud then requires:
- colluding/compromising ≥k witnesses, OR
- breaking crypto, OR
- breaking the transparency log assumptions.

## What is a “witness” in real life?
A witness can be:
- an artifact-evaluation committee,
- benchmark operator,
- independent auditor,
- multiple orgs in a “repro quorum.”

## How is the attestation bound to artifacts?
Let:
- `M = bytes(MANIFEST.json)`
- `d = SHA256(M)`

Then the attestation must satisfy:
`ATTESTATION.subject.digest.sha256 == d`

Any mismatch is a FAIL at binding.

## What is the “toy replay” in this repo?
A deterministic certificate with a provable inequality:

Define:
- step map: `x_{t+1} = (1 - 2η) x_t`
- energy: `E(x) = x^2`
- progress: `P(x) = x^2`
- choose `α = 4η - 4η^2`

Then for every step:
`E(x_{t+1}) ≤ E(x_t) - α P(x_t)`

The verifier recomputes this from artifacts and FAILs on any mismatch.

## How do you handle hardware variance?
You don’t claim “same weights from scratch everywhere.” You claim:
- “these artifacts exist”
- “their hashes match”
- “this metric computed from these artifacts meets the threshold”
- “≥k witnesses attest to the same claim”
That is robust under hardware variance.

## What’s the overhead?
In v1, overhead is:
- hashing artifacts (linear in artifact size),
- verifying k witness bundles (cheap),
- replay rule (linear in trace length).
In production, signature verification and log inclusion proofs are also cheap compared to training.

## Where are the formal theorems?
- `docs/THEOREMS.md` (core theorems)
- `docs/FORMULAS.md` (definitions)
- `FORMAL_PROOFS.md` (expanded proofs and the toy inequality proof)

## How do I show this “catches tampering”?
Run:
- `python tools/attack_suite.py`

You will see:
- artifact edit → integrity FAIL
- attestation swap → binding FAIL
- bundle swap → provenance FAIL
