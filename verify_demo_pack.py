# verify_demo_pack.py
# Verifies demo_pack/ using the full engine pipeline.

from pathlib import Path
import vproofpack as vp


def main():
    root = Path("demo_pack")
    ok, msg = vp.verify_all(root_dir=root, k=2)
    if ok:
        print("PASS")
    else:
        print("FAIL:", msg)


if __name__ == "__main__":
    main()
