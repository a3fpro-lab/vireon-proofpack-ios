# Threat Model & Detection Map (VPS v1)

This maps concrete attacker actions to the VPS engine that detects them and the verifier FAIL code.

Legend:
- **Engine** = Integrity / Binding / Provenance / Log / Replay / Policy
- **FAIL code** = the string returned by the reference verifier path

---

## A. Artifact tampering

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Modify any artifact bytes after sealing | `PROOFPACK/ARTIFACTS/*` | Integrity (manifest) | `integrity:SHA_MISMATCH:<path>` |
| Delete required artifact | missing file | Integrity (manifest) | `integrity:MISSING:<path>` |
| Swap artifact with different file | wrong bytes | Integrity (manifest) | `integrity:SHA_MISMATCH:<path>` |

---

## B. Manifest attacks

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Delete `MANIFEST.json` | missing manifest | Integrity | `integrity:MISSING_MANIFEST` |
| Modify manifest to “match” tampered artifacts | MANIFEST bytes change | Binding (attestation digest mismatch) | `binding:ATTESTATION_DIGEST_MISMATCH` |
| Keep manifest but attempt to swap attestation | ATTESTATION changes | Provenance (statement hash mismatch) or signature fail | `provenance:STATEMENT_HASH_MISMATCH` / `provenance:BAD_SIGNATURE` |

---

## C. Attestation attacks

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Delete `ATTESTATION.json` | missing attestation | Binding | `binding:MISSING_ATTESTATION` |
| Change `subject.digest.sha256` | wrong binding digest | Binding | `binding:ATTESTATION_DIGEST_MISMATCH` |
| Change requirements/policy text | ATTESTATION bytes change | Provenance (signature no longer matches) | `provenance:BAD_SIGNATURE` |
| Change nonce / issued_at | ATTESTATION bytes change | Provenance (signature mismatch) | `provenance:BAD_SIGNATURE` |

---

## D. Provenance cert attacks

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Delete `PROVENANCE_CERT.json` | missing provenance cert | Provenance | `provenance:MISSING_PROVENANCE_CERT` |
| Change k in cert | k mismatch | Provenance | `provenance:K_MISMATCH_CERT` |
| Change subject digest | digest mismatch | Provenance | `provenance:PROVENANCE_DIGEST_MISMATCH` |
| Point bundles to missing files | missing bundle path | Provenance (insufficient valid) | `provenance:ONLY_<n>_VALID` |

---

## E. Witness bundle attacks

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Change bundle’s statement hash | bundle mismatch | Provenance | `provenance:STATEMENT_HASH_MISMATCH` |
| Forge signature bytes | invalid sig | Provenance | `provenance:BAD_SIGNATURE` |
| Remove witness key (demo build) | missing key file | Provenance | `provenance:MISSING_WITNESS_KEY` |
| Swap witness key (demo build) | key id mismatch | Provenance | `provenance:KEY_ID_MISMATCH` |
| Duplicate same witness ID to fake quorum | duplicate IDs | Provenance (distinct check) | `provenance:ONLY_<n>_VALID` |

---

## F. Transparency log attacks (toy offline log)

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Delete log chain file | missing chain | Provenance (log membership) | `provenance:MISSING_LOG` |
| Change log entry hash | mismatch | Provenance (log membership) | `provenance:LOG_HASH_MISMATCH` |
| Claim membership for non-existent entry | not found | Provenance (log membership) | `provenance:LOG_ENTRY_NOT_FOUND` |
| Rewrite past log entry | breaks chain (entry hash differs) | Provenance | `provenance:LOG_HASH_MISMATCH` / `LOG_ENTRY_NOT_FOUND` |

---

## G. Replay attacks (toy deterministic trace)

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Modify `trace.json` values | wrong next-step | Replay | `replay:REPLAY_XNEXT_MISMATCH` |
| Modify `RUN.json` eta/alpha | inequality mismatch | Replay | `replay:INEQUALITY_FAIL` |
| Remove replay artifacts | missing run/trace | Replay | `replay:MISSING_TOY_ARTIFACTS` |

---

## H. Policy-only attacks (strict verifier)

Policy checks are enforced by `tools/verify_pack_strict.py` / `vps verify-strict`.

| Attack | What changes | Detected by | FAIL code |
|---|---|---|---|
| Overlong cert windows | `not_after - not_before` too large | Policy | `policy:k_accept` |
| Single-issuer quorum (if min-issuers>1) | all same issuer | Policy | `policy:issuer_diversity` |

Note: the baseline VPS verifier does NOT require issuer diversity; that is a policy extension.

---

## Summary
VPS v1 defends against post-publication tampering and provenance forgery by:
- hashing every artifact (integrity),
- binding claim → manifest digest (binding),
- requiring ≥k independent witness bundles for the same canonical statement (provenance),
- and optionally verifying deterministic replay artifacts (replay).

Residual risk after PASS is limited to cryptographic breaks or ≥k witness collusion.
