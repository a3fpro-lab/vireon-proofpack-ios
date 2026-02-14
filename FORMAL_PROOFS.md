# Formal Proofs (expanded)

This file gives explicit proofs underlying VPS v1.

Notation:
- \(H\) = SHA-256.
- `canon(s)` = canonical JSON bytes (sorted keys, no whitespace).
- All hashes are hex strings of 64 lowercase hex chars.

---

## Theorem 1 (Manifest Integrity ⇒ Tamper Detection)

**Statement.**  
Let \(M\) be a manifest listing pairs \((p_i, h_i)\) where \(h_i = H(f_i)\) and \(f_i\) is the byte-string content of file path \(p_i\).  
If verification recomputes \(H(f'_i)\) from the on-disk file at \(p_i\) and accepts only when \(H(f'_i)=h_i\) for every entry, then any post-sealing modification to any file is detected unless SHA-256 collisions exist.

**Proof.**  
Assume an adversary modifies at least one file: \(f'_j \neq f_j\) but verification still accepts.  
Acceptance implies \(H(f'_j) = h_j = H(f_j)\).  
Thus the adversary has found a collision \(f'_j \neq f_j\) with equal SHA-256 hash.  
Therefore, if SHA-256 is collision resistant, modifications are detected. ∎

---

## Theorem 2 (Attestation Binding)

**Statement.**  
Let \(d = H(\text{bytes}(\texttt{MANIFEST.json}))\).  
Verifier accepts binding only if:
\[
\texttt{ATTESTATION.subject.digest.sha256} = d.
\]
Then any accepted attestation is bound to the exact manifest file bytes.

**Proof.**  
If a different manifest \(\tilde{M}\) is substituted, then its bytes differ: \(\text{bytes}(\tilde{M}) \ne \text{bytes}(M)\).  
For the same attestation to validate binding under both, we would require:
\[
H(\text{bytes}(\tilde{M})) = H(\text{bytes}(M)).
\]
That is a collision on SHA-256 over distinct inputs.  
Hence, under collision resistance, the attestation binds uniquely to the original manifest bytes. ∎

---

## Theorem 3 (k-of-n provenance soundness)

**Statement.**  
Assume:
1) SHA-256 collision resistance,
2) the witness signature scheme is EUF-CMA secure,
3) the transparency log membership check is sound (append-only or hash-chain integrity).

If the verifier accepts ≥k **distinct** witnesses over the same canonical statement, then any successful provenance forgery implies at least one of:
- signature forgery for some witness,
- log/chain membership break,
- compromise/collusion of ≥k witnesses.

**Proof (reduction sketch).**  
Let the statement be \(S = \texttt{ATTESTATION}\) with bytes \(b=\text{canon}(S)\) and statement hash \(s=H(b)\).

A witness bundle is accepted only if:
- it asserts statement hash \(s\),
- its signature verifies on bytes \(b\),
- its log membership check validates for \(s\),
- its log timestamp is within the cert window.

Suppose an adversary produces ≥k distinct accepted bundles without colluding with ≥k witnesses.

Consider any accepted bundle for an uncompromised witness.  
Because the witness is uncompromised, the adversary does not know the signing key.  
To produce a verifying signature on \(b\) they must forge a signature (EUF-CMA break), unless they can alter \(b\) while keeping \(s\) fixed.

But altering \(b\) while keeping \(H(b)=s\) is a SHA-256 collision/preimage-style break.  
If neither signature forgery nor hash collision is feasible, the only remaining path is to fake the log membership/time constraints, contradicting log membership soundness.  
Therefore, absent breaking primitives, the adversary must compromise/collude with ≥k witnesses to reach ≥k accepted distinct witness IDs. ∎

---

## Corollary (Trust-Debt Law)

**Statement.**  
If verification accepts:
- manifest integrity,
- attestation binding,
- k-of-n provenance,
- deterministic replay (when present),

then the residual trust debt is exactly:
- ≥k witnesses did not collude/compromise, and
- the verifier spec is honest/public.

**Proof.**  
From Theorems 1–3, tampering, swapping, or provenance forgery reduces to breaking crypto/log assumptions or collusion.  
Replay (when present) removes “metric fabrication” by re-deriving the claim directly from artifacts.  
No other hidden assumption remains. ∎

---

# Proof of the Toy Replay Inequality (as implemented)

The demo uses:
\[
x_{t+1} = (1 - 2\eta)x_t,\quad E(x)=x^2,\quad P(x)=x^2,\quad \alpha = 4\eta - 4\eta^2.
\]

We must show for every step:
\[
E(x_{t+1}) \le E(x_t) - \alpha P(x_t).
\]

Compute:
\[
E(x_{t+1}) = x_{t+1}^2 = (1-2\eta)^2 x_t^2.
\]
So the inequality becomes:
\[
(1-2\eta)^2 x_t^2 \le x_t^2 - \alpha x_t^2
\]
Divide by \(x_t^2 \ge 0\) (if \(x_t=0\) it is equality):
\[
(1-2\eta)^2 \le 1 - \alpha.
\]
Expand LHS:
\[
(1-2\eta)^2 = 1 - 4\eta + 4\eta^2.
\]
So we need:
\[
1 - 4\eta + 4\eta^2 \le 1 - \alpha
\]
Cancel 1:
\[
-4\eta + 4\eta^2 \le -\alpha
\]
Multiply by \(-1\) reversing inequality:
\[
4\eta - 4\eta^2 \ge \alpha.
\]
Choosing \(\alpha = 4\eta - 4\eta^2\) makes it tight with equality for all \(x_t\). ∎
