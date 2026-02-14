# tools/forge_attack.py
# Demonstrates tamper detection:
# 1) generates a fresh demo_pack
# 2) edits one artifact AFTER manifest/attestation/provenance
# 3) verifier must FAIL at integrity stage

from pathlib import Path
import json

import vproofpack as vp


def tamper_trace(art_dir: Path) -> None:
    trace_path = art_dir / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    # Flip a single value slightly
    trace[0]["x_next"] = float(trace[0]["x_next"]) + 0.12345
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True), encoding="utf-8")


def main():
    # 1) Build pack
    import make_demo_pack  # ensures file exists / module importable

    make_demo_pack.main()

    root = Path("demo_pack")
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"

    # 2) Verify it passes before tamper
    ok, msg = vp.verify_all(root_dir=root, k=2)
    print("BEFORE tamper:", "PASS" if ok else f"FAIL:{msg}")

    # 3) Tamper with one artifact after it was sealed
    tamper_trace(art)

    # 4) Verify it fails
    ok2, msg2 = vp.verify_all(root_dir=root, k=2)
    print("AFTER tamper:", "PASS" if ok2 else f"FAIL:{msg2}")


if __name__ == "__main__":
    main()
