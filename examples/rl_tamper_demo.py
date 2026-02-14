# examples/rl_tamper_demo.py
# Demonstrates trust-debt collapse:
# 1) Build RL artifacts + seal proofpack
# 2) Verify PASS
# 3) Flip one byte in rollout.jsonl
# 4) Verify FAIL with precise code

from __future__ import annotations

from pathlib import Path

import vproofpack as vp


def flip_one_byte(path: Path) -> None:
    b = bytearray(path.read_bytes())
    if not b:
        raise RuntimeError("empty file")
    # flip a single bit in the middle
    i = len(b) // 2
    b[i] ^= 0x01
    path.write_bytes(bytes(b))


def main() -> int:
    # Ensure packs exist
    # Run the same flow as docs:
    #   python examples/rl_minicartpole.py
    #   python examples/make_rl_proofpack.py
    # But we won't import those scripts; we assume user ran them or CI runs them.
    root = Path("demo_rl_pack")

    if not root.exists():
        print("Missing demo_rl_pack. Run:")
        print("  python examples/rl_minicartpole.py")
        print("  python examples/make_rl_proofpack.py")
        return 2

    ok, msg = vp.verify_all(root_dir=root, k=2)
    if not ok:
        print("Expected PASS before tamper, got FAIL:", msg)
        return 1

    print("PASS (pre-tamper)")

    target = root / "PROOFPACK" / "ARTIFACTS" / "rollout.jsonl"
    if not target.exists():
        print("Missing rollout.jsonl in pack artifacts")
        return 2

    flip_one_byte(target)
    print("TAMPERED: flipped 1 bit in rollout.jsonl")

    ok2, msg2 = vp.verify_all(root_dir=root, k=2)
    if ok2:
        print("ERROR: expected FAIL after tamper, but got PASS")
        return 1

    print("FAIL (post-tamper):", msg2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
