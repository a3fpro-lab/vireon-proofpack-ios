# vireon-proofpack-ios

A **proofpack** is a tamper-evident, replay-verifiable container for *result claims*.

This repo is **iPhone-safe** (stdlib-only Python). It implements:

- **Integrity**: `MANIFEST.json` (SHA-256 over artifacts)
- **Binding**: `ATTESTATION.json` binds to manifest digest
- **k-of-n provenance**: witness bundles + a provenance cert
- **Transparency log**: append-only hash-chain (toy log, offline)
- **Replay**: deterministic toy trace check

## Repo layout

- `vproofpack.py` — core proofpack library (stdlib only)
- `make_demo_pack.py` — generates `demo_pack/` with k witnesses
- `verify_demo_pack.py` — verifies the pack (PASS/FAIL)
- `docs/FORMULAS.md` — all formulas used by the verifier
- `docs/THEOREMS.md` — formal theorems (soundness claims)

## What “PASS” means

PASS implies:
1) No artifact tampering (manifest matches files)
2) Attestation binds exactly that manifest
3) At least k distinct witness bundles validate the same statement
4) The log hash-chain membership checks out
5) The deterministic replay inequality holds for every step

This reduces “trust me” to “k witnesses didn’t collude + verifier spec is honest.”

## Run (later, on any computer with Python 3.10+)

```bash
python make_demo_pack.py
python verify_demo_pack.py

Commit.

---

# FILE 3 — `docs/FORMULAS.md`
Create new file: `docs/FORMULAS.md`  
Paste:

```md
# Proofpack formulas (v1, iPhone-safe build)

Let \(H\) be SHA-256.

## Hashes
- File hash: \(h(f) = H(\text{bytes}(f))\)
- Manifest digest: \(d = H(\text{bytes}(\texttt{MANIFEST.json}))\)

## Canonical statement encoding
Let `canon(s)` be deterministic JSON canonicalization:
sorted keys, no whitespace, UTF-8.

Statement hash:
\[
\mathrm{stmt\_hash}(s) = H(\mathrm{canon}(s))
\]

## Attestation binding
ATTESTATION contains `subject.digest.sha256 = d`.

Binding condition:
\[
\text{binds} \iff \texttt{ATTESTATION.subject.digest.sha256} = H(\texttt{MANIFEST bytes})
\]

## Local transparency log (offline hash-chain)
Each log entry commits to:
\[
e_i = (\text{prev}_i, \tau_i, \mathrm{stmt\_hash})
\]
\[
\mathrm{entry\_hash}_i = H(\mathrm{canon}(e_i))
\]
and sets:
\[
\text{prev}_{i+1} = \mathrm{entry\_hash}_i
\]
Changing any past entry breaks the chain.

## k-of-n provenance
A witness bundle is valid iff:
1) statement hash matches attestation
2) signature verifies over canonical statement bytes
3) integrated time \(\tau\) is inside cert window \([nb, na]\)
4) log membership verifies

k-of-n passes iff there exist ≥k distinct witness IDs with valid bundles.

## Replay check (toy)
Energy \(E(x)=x^2\), progress \(P(x)=x^2\), map \(T(x)=(1-2\eta)x\).

For each step:
\[
x_{t+1} = T(x_t)
\]
\[
E(x_{t+1}) \le E(x_t) - \alpha P(x_t)
\]
where the demo uses:
\[
\alpha = 4\eta - 4\eta^2
\]
