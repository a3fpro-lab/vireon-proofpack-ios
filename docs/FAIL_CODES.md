# VPS FAIL Codes (stable contract)

VPS verifiers MUST report failures as:

`<stage>:<reason_code>`

Stages:
- `integrity`
- `binding`
- `provenance`
- `log`
- `replay`
- `schema` (strict mode)

This file is a stability contract: adding new codes is OK; renaming/removing existing codes is a breaking change.

---

## integrity

- `integrity:MISSING_MANIFEST`
- `integrity:MISSING:<path>`
- `integrity:SHA_MISMATCH:<path>`

Meaning: artifact bytes differ from what the pack claims.

---

## binding

- `binding:MISSING_ATTESTATION`
- `binding:ATTESTATION_DIGEST_MISMATCH`

Meaning: the claim does not bind to the exact manifest/root.

---

## provenance

- `provenance:MISSING_PROVENANCE_CERT`
- `provenance:K_MISMATCH_CERT`
- `provenance:PROVENANCE_DIGEST_MISMATCH`
- `provenance:ONLY_<n>_VALID`

Meaning: fewer than k distinct valid witness bundles attest the same canonical statement.

---

## log

- `log:MISSING_LOG`
- `log:LOG_HASH_MISMATCH`
- `log:LOG_ENTRY_NOT_FOUND`

Meaning: the anchoring evidence is missing or inconsistent.

---

## replay

- `replay:MISSING_TOY_ARTIFACTS`
- `replay:REPLAY_XNEXT_MISMATCH`
- `replay:INEQUALITY_FAIL`

Meaning: deterministic replay checks fail (only applied if replay artifacts exist).

---

## schema (strict mode)

Strict mode MAY add schema violations as FAIL codes. Examples:
- `schema:BAD_JSON`
- `schema:MISSING_FIELD:<field>`
- `schema:TYPE_MISMATCH:<field>`
- `schema:UNKNOWN_FIELD:<field>` (optional rule)

Meaning: pack object structure violates strict policy.
