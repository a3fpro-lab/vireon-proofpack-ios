# Theorems (VPS v1)

Let \(H\) be SHA-256. Let `canon(·)` be deterministic JSON canonicalization.

---

## Theorem 1 — Integrity soundness
If `MANIFEST.json` lists \(h_i = H(\text{bytes}(f_i))\) for each artifact file \(f_i\), then any post-sealing change to any \(f_i\) is detected unless SHA-256 collision resistance fails.

---

## Theorem 2 — Binding soundness
Let \(d = H(\text{bytes}(\texttt{MANIFEST.json}))\).  
If verifier requires `ATTESTATION.subject.digest.sha256 = d`, then swapping the manifest without detection implies a SHA-256 collision.

---

## Theorem 3 — k-of-n provenance boundary
Let \(s = H(\text{canon}(\texttt{ATTESTATION}))\).  
If verifier accepts only when ≥k distinct witnesses provide valid bundles for the same \(s\), then forging provenance without ≥k colluding/compromised witnesses implies breaking signature security, SHA-256, or log membership soundness.

---

## Corollary — Trust-Debt Law
If integrity + binding + k-of-n provenance + replay (when present) all PASS, residual trust debt collapses to:
**“k witnesses didn’t collude + verifier spec is honest.”**
