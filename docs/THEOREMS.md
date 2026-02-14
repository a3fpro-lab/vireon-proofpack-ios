# Proofpack theorems (formal core)

## Theorem 1 (Manifest Integrity ⇒ Tamper Detection)
Let \(H\) be collision resistant. Let MANIFEST list hashes \(H(f_p)\) for files \(f_p\).
If an adversary changes any file \(f_p \to f'_p \ne f_p\) but still passes verification, then \(H(f_p)=H(f'_p)\),
a collision. ∎

## Theorem 2 (Attestation Binding)
Let \(d=H(\texttt{MANIFEST bytes})\). If verification accepts an attestation with subject digest \(d\),
it is bound to that exact manifest. Any different manifest requires a collision. ∎

## Theorem 3 (k-of-n provenance soundness)
Assume:
1) \(H\) collision resistant
2) the signature scheme is unforgeable (EUF-CMA)
3) the log is append-only (or hash-chain is intact)

If verification accepts k distinct witness bundles on the same attestation statement,
then faking provenance requires either:
- forging a witness signature, OR
- breaking log append-only / hash-chain membership, OR
- colluding/compromising ≥k witnesses. ∎

## Corollary (Trust-Debt Law)
Define trust debt as unverifiable assumption a third party must accept.
A proofpack with integrity + binding + k-of-n provenance + deterministic replay collapses trust debt to:
“k witnesses didn’t collude and the verifier spec is honest.”
All other tampering reduces to breaking crypto or replay failing. ∎
