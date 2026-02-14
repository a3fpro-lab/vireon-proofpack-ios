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


def main():
    root = Path("demo_pack")
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"
    bundles_dir = root / "WITNESS_BUNDLES"

    # Fresh start (safe delete only inside demo_pack)
    if root.exists():
        # Minimal delete without shutil to keep it simple/portable
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

    # 1) Replay artifacts (deterministic toy)
    vp.toy_generate_artifacts(art_dir=art, steps=50, eta=0.1)

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
        subject_name="demo_pack",
        policy_id="vireon.proofpack.policy.v1",
        requirements=requirements,
        nonce=nonce,
    )
    vp.write_json(pp / "ATTESTATION.json", att)

    # 4) Create witness bundles
    # On iPhone build these are HMAC-based local witnesses (demo).
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

    # 5) Provenance cert (k-of-n). Default k=2.
    k = 2
    prov = vp.make_provenance_cert(pp_dir=pp, k=k, bundle_refs=bundle_refs)
    vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    print("WROTE demo_pack/")
    print("Try: python verify_demo_pack.py")


if __name__ == "__main__":
    main()
