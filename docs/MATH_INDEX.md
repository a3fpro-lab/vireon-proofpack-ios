# VPS Math Index (v1.0.0)

This repo is built on two pillars:

1) **Cryptographic integrity** (hashes, binding, provenance, logs)
2) **Mathematical replay certificates** (deterministic rules checked from artifacts)

Everything below is written so a verifier is a *mathematical predicate* returning PASS/FAIL.

---

## A. Cryptographic definitions

- Canonicalization: `docs/CANONICALIZATION.md`
- Hash functions and digests: `docs/FORMULAS.md`
- FAIL code contract: `docs/FAIL_CODES.md`

---

## B. Theorems (soundness)

- Core theorems: `docs/THEOREMS.md`
- Expanded formal proofs: `FORMAL_PROOFS.md`

Key claim:
> PASS collapses “trust me” to (i) ≥k witnesses didn’t collude, and (ii) verifier spec is honest.

---

## C. Replay mathematics (certificates)

The demo replay is a quadratic descent certificate:
- Update rule: \(x_{t+1}=(1-2\eta)x_t\)
- Energy: \(E(x)=x^2\)
- Progress: \(P(x)=x^2\)
- Certified decrease constant: \(\alpha=4\eta-4\eta^2\)

See:
- `docs/FORMULAS.md`
- `FORMAL_PROOFS.md` (derivation and proof)

---

## D. Scale extensions (optional, v1-compatible)

- Merkle roots: `MERKLE.md`
- Sharded packs: `SHARDING.md`

These allow:
- O(1) witness signing over roots
- inclusion proofs for subset verification
- streaming / huge runs

---

## E. Roadmap math (next certificates)

Replay engines to add (each with a proof section + verifier rule):

1) **General contraction certificate**
   - If \( \|x_{t+1}\|\le c\|x_t\| \) with \(c<1\), then energy decreases geometrically.

2) **Lyapunov-style certificate**
   - If \(V(s_{t+1}) \le V(s_t)-\alpha W(s_t)\), the verifier checks inequality from logs.

3) **Finite-state deterministic MDP certificate**
   - A seed-fixed evaluator with an auditable transition table.

Each engine must ship with:
- artifacts format
- verifier predicate
- theorem + proof note
