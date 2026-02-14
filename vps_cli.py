# vps_cli.py
# CLI for VPS proofpacks (stdlib-only).
#
# Commands:
#   vps make-demo [--out demo_pack] [--steps 50] [--eta 0.1] [--k 2]
#   vps verify <pack_dir> [--k 2]
#   vps verify-strict <pack_dir> [--k 2] [--min-issuers 1] [--max-window 86400]
#   vps summary <pack_dir> [--k 2]
#
# Note: strict verify mirrors tools/verify_pack_strict.py policy logic.

from __future__ import annotations

import argparse
import json
from pathlib import Path

import vproofpack as vp


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_make_demo(args: argparse.Namespace) -> int:
    root = Path(args.out)
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"
    bundles_dir = root / "WITNESS_BUNDLES"

    # Safe delete inside target dir
    if root.exists():
        for p in sorted(root.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                try:
                    p.rmdir()
                except Exception:
                    pass

    art.mkdir(parents=True, exist_ok=True)
    bundles_dir.mkdir(parents=True, exist_ok=True)

    # 1) deterministic toy artifacts
    vp.toy_generate_artifacts(art_dir=art, steps=int(args.steps), eta=float(args.eta))

    # 2) MANIFEST over artifacts
    manifest = vp.make_manifest(pp_dir=pp, include_dirs=("ARTIFACTS",))
    vp.write_json(pp / "MANIFEST.json", manifest)

    # 3) ATTESTATION binds manifest digest
    requirements = [
        "MANIFEST integrity check passes",
        "ATTESTATION binds to MANIFEST digest",
        "k-of-n witness provenance validates statement",
        "Replay verifier passes on included artifacts",
    ]
    nonce = vp.sha256_bytes((str(root).encode("utf-8") + b":" + str(args.steps).encode("utf-8")))
    att = vp.make_attestation(
        pp_dir=pp,
        subject_name=root.name,
        policy_id="vireon.proofpack.policy.v1",
        requirements=requirements,
        nonce=nonce,
    )
    vp.write_json(pp / "ATTESTATION.json", att)

    # 4) Witness bundles (local HMAC demo)
    witness_ids = ["witness_alpha", "witness_beta", "witness_gamma"]
    bundle_refs = []
    for wid in witness_ids:
        bundle = vp.make_witness_bundle(
            root_dir=root,
            witness_id=wid,
            issuer="vireon_local",
            subject=wid,
            validity_seconds=3600,
        )
        out_path = bundles_dir / f"{wid}.json"
        vp.write_json(out_path, bundle)
        bundle_refs.append({"witness_id": wid, "path": out_path.relative_to(root).as_posix()})

    # 5) Provenance cert (k-of-n)
    prov = vp.make_provenance_cert(pp_dir=pp, k=int(args.k), bundle_refs=bundle_refs)
    vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    print("WROTE:", root.as_posix())
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    ok, msg = vp.verify_all(root_dir=Path(args.pack_dir), k=int(args.k))
    if ok:
        print("PASS")
        return 0
    print("FAIL:", msg)
    return 1


def cmd_verify_strict(args: argparse.Namespace) -> int:
    root = Path(args.pack_dir)

    ok, msg = vp.verify_all(root_dir=root, k=int(args.k))
    if not ok:
        print("FAIL:", msg)
        return 1

    prov = _load(root / "PROOFPACK" / "PROVENANCE_CERT.json")
    bundle_refs = prov["bundles"]

    issuers = set()
    acceptable = 0

    for ref in bundle_refs:
        b = _load(root / ref["path"])
        nb = int(b["certificate"]["not_before"])
        na = int(b["certificate"]["not_after"])
        if (na - nb) > int(args.max_window):
            continue
        issuers.add(b["witness"]["issuer"])
        acceptable += 1

    if acceptable < int(args.k):
        print("FAIL: policy:k_accept (not enough bundles within max-window)")
        return 1
    if len(issuers) < int(args.min_issuers):
        print("FAIL: policy:issuer_diversity")
        return 1

    print("PASS_STRICT")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    root = Path(args.pack_dir)
    pp = root / "PROOFPACK"

    d = vp.manifest_digest(pp)
    att = _load(pp / "ATTESTATION.json")
    prov = _load(pp / "PROVENANCE_CERT.json")

    ok, msg = vp.verify_all(root_dir=root, k=int(args.k))

    print("PACK:", root.as_posix())
    print("MANIFEST_DIGEST_SHA256:", d)
    print("ATTESTATION_BINDS:", att["subject"]["digest"]["sha256"] == d)
    print("K_REQUIRED:", prov["k"])
    print("SUBJECT_DIGEST_MATCH:", prov["subject_digest_sha256"] == d)
    print("VERIFY:", "PASS" if ok else f"FAIL:{msg}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="vps")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("make-demo")
    p.add_argument("--out", default="demo_pack")
    p.add_argument("--steps", type=int, default=50)
    p.add_argument("--eta", type=float, default=0.1)
    p.add_argument("--k", type=int, default=2)
    p.set_defaults(fn=cmd_make_demo)

    p = sub.add_parser("verify")
    p.add_argument("pack_dir")
    p.add_argument("--k", type=int, default=2)
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("verify-strict")
    p.add_argument("pack_dir")
    p.add_argument("--k", type=int, default=2)
    p.add_argument("--min-issuers", type=int, default=1)
    p.add_argument("--max-window", type=int, default=86400)
    p.set_defaults(fn=cmd_verify_strict)

    p = sub.add_parser("summary")
    p.add_argument("pack_dir")
    p.add_argument("--k", type=int, default=2)
    p.set_defaults(fn=cmd_summary)

    args = ap.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
