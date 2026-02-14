# tools/verify_pack.py
# Verify an arbitrary proofpack directory with the full pipeline.
# Usage:
#   python tools/verify_pack.py demo_pack --k 2

from pathlib import Path
import argparse
import vproofpack as vp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir", help="Path to pack root (contains PROOFPACK/ and WITNESS_BUNDLES/)")
    ap.add_argument("--k", type=int, default=2, help="k-of-n requirement")
    args = ap.parse_args()

    root = Path(args.pack_dir)
    ok, msg = vp.verify_all(root_dir=root, k=args.k)
    if ok:
        print("PASS")
        return 0
    print("FAIL:", msg)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
