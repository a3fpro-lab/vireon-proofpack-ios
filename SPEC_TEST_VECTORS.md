# Spec Test Vectors (VPS v1)

Purpose: enable independent implementations to match exact expected behavior.

## Vector 1 — Canonicalization
Canonical JSON uses:
- UTF-8
- sorted keys
- separators: `,` and `:`
- no whitespace

Example object:
```json
{"b":2,"a":1}
