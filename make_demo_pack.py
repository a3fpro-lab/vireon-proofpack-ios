# make_demo_pack.py
# Generates demo_pack/ with:
#  - PROOFPACK/ARTIFACTS (toy replay)
#  - PROOFPACK/MANIFEST.json (integrity)
#  - PROOFPACK/ATTESTATION.json (binding)
#  - WITNESS_BUNDLES/*.json (k witnesses)
#  - PROOFPACK/PROVENANCE_CERT.json (k-of-n)

from pathlib import Path
import os
import time

import vproofpack as vp


def _safe_rmtree(root: Path) -> None:
    """Delete only inside demo_pack/ without shutil (portable)."""
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


def main(out_dir: str = "demo_pack", k: int = 2, steps: int = 50, eta: float = 0.1):
    root = Path(out_dir)
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"
    bundles_dir = root / "WITNESS_BUNDLES"

    # Fresh start (safe delete only inside demo_pack)
    _safe_rmtree(root)

    art.mkdir(parents=True, exist_ok=True)
    bundles_dir.mkdir(parents=True, exist_ok=True)

    # 1) Replay artifacts (deterministic toy)
    vp.toy_generate_artifacts(art_dir=art, steps=steps, eta=eta)

    # 2) MANIFEST over artifacts
    manifest = vp.make_manifest(pp_dir=pp, include_dirs=("ARTIFACTS",))
    vp.write_json(pp / "MANIFEST.json", manifest)

    # 3) ATTESTATION binds to MANIFEST digest
    requirements = [
        "MANIFEST integrity check passes",
        "ATTESTATION binds to MANIFEST digest",
        "k-of-n witness provenance validates statement",
        "Replay verifier passes on included artifacts",
    ]
    nonce = vp.sha256_bytes(os.urandom(16) + str(time.time()).encode("utf-8"))
    att = vp.make_attestation(
        pp_dir=pp,
        subject_name=root.name,
        policy_id="vireon.proofpack.policy.v1",
        requirements=requirements,
        nonce=nonce,
    )
    vp.write_json(pp / "ATTESTATION.json", att)

    # 4) Create witness bundles (demo local HMAC witnesses)
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
    prov = vp.make_provenance_cert(pp_dir=pp, k=int(k), bundle_refs=bundle_refs)
    vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    print(f"WROTE {root.as_posix()}/ (k={k})")
    print("Try: python verify_demo_pack.py")


if __name__ == "__main__":
    main()
