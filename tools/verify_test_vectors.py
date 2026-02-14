# tools/verify_test_vectors.py
# Verifies pinned VPS test vectors and enforces a stable root digest.

from __future__ import annotations

import hashlib
from pathlib import Path

import vproofpack as vp


EXPECTED_V1_ROOT_SHA256 = "2599c7cb71c9b7af5ecc55374033b607e19173aceb387ffa1204d1644830929b"


def vector_root_digest(root_dir: Path) -> str:
    # sha256 over lines: "relpath sha256(file)"
    lines = []
    for p in sorted(root_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root_dir).as_posix()
            h = vp.sha256_file(p)
            lines.append(f"{rel} {h}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> int:
    root = Path("test_vectors") / "v1_pack"
    if not root.exists():
        print("FAIL: missing test_vectors/v1_pack (run generate_test_vectors.py first)")
        return 2

    ok, msg = vp.verify_all(root_dir=root, k=2)
    if not ok:
        print("FAIL: verify_all:", msg)
        return 1

    got = vector_root_digest(root)
    if got != EXPECTED_V1_ROOT_SHA256:
        print("FAIL: vector_root_digest mismatch")
        print(" expected:", EXPECTED_V1_ROOT_SHA256)
        print(" got     :", got)
        return 1

    print("PASS: test vectors pinned + verified")
    print("VECTOR_ROOT_SHA256:", got)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
