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

Canonical bytes MUST equal:
{"a":1,"b":2}
Vector 2 — Statement hash

Given the canonical bytes above, statement hash is:
SHA256(UTF8(canon(obj)))

Implementations must match Python:
hashlib.sha256(canon_bytes).hexdigest().

Vector 3 — Manifest digest

Manifest digest is:
SHA256(bytes(MANIFEST.json))
NOT SHA of parsed JSON.

Vector 4 — Attestation binding

PASS iff:
ATTESTATION.subject.digest.sha256 == SHA256(bytes(MANIFEST.json))

Vector 5 — k-of-n provenance

PASS iff:
	•	provenance cert binds same manifest digest
	•	≥k distinct witness_ids validate the same statement hash + signature

Vector 6 — Replay (toy)

Toy step:
x_next = (1-2*eta)*x
Inequality:
x_next^2 <= x^2 - alpha*x^2
with alpha = 4*eta - 4*eta^2.

Any mismatch FAILs replay stage.
Commit.

---

# FILE 31 — `BADGES.md` (optional marketing/positioning)
Create: `BADGES.md`  
Paste:

```md
# Badges / Positioning


