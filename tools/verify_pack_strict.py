# tools/verify_pack_strict.py
# Strict verifier wrapper:
# - runs core VPS verification
# - enforces issuer diversity + max cert window policy on accepted k bundles
#
# Usage:
#   python tools/verify_pack_strict.py demo_pack --k 2 --min-issuers 2 --max-window 86400

from pathlib import Path
import argparse
import json
import sys

# Ensure repo root is importable when running from tools/
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import vproofpack as vp  # noqa: E402


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir", nargs="?", default="demo_pack")
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--min-issuers", type=int, default=2)
    ap.add_argument("--max-window", type=int, default=86400)  # seconds
    args = ap.parse_args()

    root = Path(args.pack_dir)

    ok, msg = vp.verify_all(root_dir=root, k=args.k)
    if not ok:
        print("FAIL:", msg)
        return 1

    prov = load(root / "PROOFPACK" / "PROVENANCE_CERT.json")
    bundle_refs = prov["bundles"]

    issuers = set()
    acceptable = 0

    for ref in bundle_refs:
        bpath = root / ref["path"]
        b = load(bpath)

        nb = int(b["certificate"]["not_before"])
        na = int(b["certificate"]["not_after"])
        window = na - nb
        if window > args.max_window:
            continue

        issuers.add(b["witness"]["issuer"])
        acceptable += 1

    if acceptable < args.k:
        print("FAIL: policy:k_accept (not enough bundles within max-window)")
        return 1

    if len(issuers) < args.min_issuers:
        print("FAIL: policy:issuer_diversity")
        return 1

    print("PASS_STRICT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
