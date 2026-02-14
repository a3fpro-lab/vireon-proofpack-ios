# examples/make_rl_proofpack.py
# Creates a VPS proofpack from stdlib-only RL artifacts:
# - copies examples/rl_artifacts into demo_rl_pack/PROOFPACK/ARTIFACTS
# - seals MANIFEST + ATTESTATION
# - generates k witness bundles + provenance cert

from __future__ import annotations

from pathlib import Path
import os
import time
import shutil

import vproofpack as vp


def safe_rmtree(root: Path) -> None:
    if not root.exists():
        return
    for p in sorted(root.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()
        else:
            try:
                p.rmdir()
            except Exception:
                pass


def main() -> int:
    src = Path("examples") / "rl_artifacts"
    if not src.exists():
        print("Missing examples/rl_artifacts. Run: python examples/rl_minicartpole.py")
        return 2

    root = Path("demo_rl_pack")
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"
    bundles_dir = root / "WITNESS_BUNDLES"

    safe_rmtree(root)
    art.mkdir(parents=True, exist_ok=True)
    bundles_dir.mkdir(parents=True, exist_ok=True)

    # Copy artifacts
    for p in sorted(src.iterdir()):
        if p.is_file():
            shutil.copy2(p, art / p.name)

    # Manifest (integrity)
    manifest = vp.make_manifest(pp_dir=pp, include_dirs=("ARTIFACTS",))
    vp.write_json(pp / "MANIFEST.json", manifest)

    # Attestation (binding)
    requirements = [
        "MANIFEST integrity check passes",
        "ATTESTATION binds to MANIFEST digest",
        "k-of-n witness provenance validates statement",
        "RL artifacts include env params + seed + returns + rollout trace",
    ]
    nonce = vp.sha256_bytes(os.urandom(16) + str(time.time()).encode("utf-8"))
    att = vp.make_attestation(
        pp_dir=pp,
        subject_name="demo_rl_pack",
        policy_id="vireon.proofpack.policy.v1",
        requirements=requirements,
        nonce=nonce,
    )
    vp.write_json(pp / "ATTESTATION.json", att)

    # Witness bundles (k-of-n)
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

    # Provenance cert
    k = 2
    prov = vp.make_provenance_cert(pp_dir=pp, k=k, bundle_refs=bundle_refs)
    vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    print("WROTE demo_rl_pack/")
    print("Verify: python tools/verify_pack_strict.py demo_rl_pack --k 2 --min-issuers 1 --max-window 86400")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
