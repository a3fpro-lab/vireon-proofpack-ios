```python
# tools/print_pack_summary.py
# Prints the key digests and provenance status for a pack (for public posts).

from pathlib import Path
import argparse
import json
import vproofpack as vp


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir", nargs="?", default="demo_pack")
    ap.add_argument("--k", type=int, default=2)
    args = ap.parse_args()

    root = Path(args.pack_dir)
    pp = root / "PROOFPACK"

    ok, d = vp.manifest_digest(pp)
    if not ok:
        raise SystemExit(f"FAIL: {d}")

    att = load(pp / "ATTESTATION.json")
    prov = load(pp / "PROVENANCE_CERT.json")

    ok2, msg = vp.verify_all(root_dir=root, k=args.k)

    print("PACK:", root.as_posix())
    print("MANIFEST_DIGEST_SHA256:", d)
    print("ATTESTATION_BINDS:", att["subject"]["digest"]["sha256"] == d)
    print("K_REQUIRED:", prov["k"])
    print("SUBJECT_DIGEST_MATCH:", prov["subject_digest_sha256"] == d)
    print("VERIFY:", "PASS" if ok2 else f"FAIL:{msg}")


if __name__ == "__main__":
    raise SystemExit(main())


