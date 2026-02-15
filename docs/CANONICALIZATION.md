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
