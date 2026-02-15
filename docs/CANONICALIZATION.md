# Canonicalization (VPS v1)

All signed/hashed statements use deterministic JSON canonicalization:

- UTF-8 encoding
- object keys sorted lexicographically
- separators: `,` and `:`
- no whitespace
- `ensure_ascii=False`
- arrays preserved in order

Reference function:

```py
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

What is canonicalized?
	•	The full ATTESTATION.json object (as a JSON value), canon-encoded.
	•	Any statement object that a witness signs MUST be canon-encoded the same way.

Why this matters

If canonicalization differs across verifiers, signatures stop being portable and “provenance” becomes ambiguous. Canonicalization is therefore part of the verifier meaning.


