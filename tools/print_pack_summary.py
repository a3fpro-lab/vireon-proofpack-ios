# tools/print_pack_summary.py
# Prints key digests + provenance status for a pack (for public screenshots/posts).

from pathlib import Path
import argparse
import json

import vproofpack as vp


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir", nargs="?", default="demo_pack", help="Pack directory (default: demo_pack)")
    ap.add_argument("--k", type=int, default=2, help="k-of-n threshold (default: 2)")
    args = ap.parse_args()

    root = Path(args.pack_dir)
    pp = root / "PROOFPACK"

    if not pp.exists():
        print("FAIL: missing PROOFPACK at", pp.as_posix())
        return 2

    d = vp.manifest_digest(pp)

    att_path = pp / "ATTESTATION.json"
    prov_path = pp / "PROVENANCE_CERT.json"

    att = load_json(att_path) if att_path.exists() else {}
    prov = load_json(prov_path) if prov_path.exists() else {}

    ok, msg = vp.verify_all(root_dir=root, k=args.k)

    print("PACK:", root.as_posix())
    print("MANIFEST_DIGEST_SHA256:", d)
    print("ATTESTATION_BINDS:", bool(att) and att.get("subject", {}).get("digest", {}).get("sha256") == d)
    print("K_REQUIRED:", prov.get("k", "MISSING"))
    print("SUBJECT_DIGEST_MATCH:", bool(prov) and prov.get("subject_digest_sha256") == d)
    print("VERIFY:", "PASS" if ok else f"FAIL:{msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
