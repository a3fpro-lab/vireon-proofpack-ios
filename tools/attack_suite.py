# tools/attack_suite.py
# Runs three attacks and shows where the verifier fails:
#  A1: artifact edit -> integrity FAIL
#  A2: attestation swap -> binding FAIL
#  A3: witness bundle swap -> provenance FAIL

from pathlib import Path
import json
import copy

import vproofpack as vp
import make_demo_pack


def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _write(p: Path, obj):
    p.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def a1_artifact_edit(root: Path):
    # Edit ARTIFACTS/trace.json after sealing -> MANIFEST mismatch
    trace_path = root / "PROOFPACK" / "ARTIFACTS" / "trace.json"
    trace = _read(trace_path)
    trace[0]["x_next"] = float(trace[0]["x_next"]) + 0.333
    _write(trace_path, trace)


def a2_attestation_swap(root: Path):
    # Swap attestation digest so it no longer binds to MANIFEST
    apath = root / "PROOFPACK" / "ATTESTATION.json"
    att = _read(apath)
    # Flip one hex digit in the bound digest
    d = att["subject"]["digest"]["sha256"]
    att["subject"]["digest"]["sha256"] = ("0" if d[0] != "0" else "1") + d[1:]
    _write(apath, att)


def a3_bundle_swap(root: Path):
    # Replace witness_beta bundle statement hash so provenance fails
    bpath = root / "WITNESS_BUNDLES" / "witness_beta.json"
    bundle = _read(bpath)
    h = bundle["statement_sha256"]
    bundle["statement_sha256"] = ("f" if h[0] != "f" else "e") + h[1:]
    _write(bpath, bundle)


def run_case(label: str, mutator):
    make_demo_pack.main(out_dir="demo_pack", k=2)
    root = Path("demo_pack")

    ok0, msg0 = vp.verify_all(root_dir=root, k=2)
    print(label, "BASE:", "PASS" if ok0 else f"FAIL:{msg0}")

    mutator(root)

    ok, msg = vp.verify_all(root_dir=root, k=2)
    print(label, "AFTER:", "PASS" if ok else f"FAIL:{msg}")
    print("-" * 60)


def main():
    run_case("A1_ARTIFACT_EDIT", a1_artifact_edit)
    run_case("A2_ATTESTATION_SWAP", a2_attestation_swap)
    run_case("A3_BUNDLE_SWAP", a3_bundle_swap)


if __name__ == "__main__":
    main()
