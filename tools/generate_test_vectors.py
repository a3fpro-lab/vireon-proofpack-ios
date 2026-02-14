# tools/generate_test_vectors.py
# Deterministic, pinned test vectors for VPS v1.0.0.
# Generates: test_vectors/v1_pack/...
#
# Goal: CI can regenerate vectors and verify they match the expected root digest.

from __future__ import annotations

import json
import hashlib
import hmac
import base64
from pathlib import Path

import vproofpack as vp


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


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
    # -------------------------
    # Pinned constants (do not change without bumping vector version)
    # -------------------------
    issued_at = "2026-02-13T00:00:00Z"
    integrated_time = 1760000000
    validity_seconds = 3600
    issuer = "vireon_vector_issuer"

    seed = b"VPS_TEST_VECTOR_SEED_v1"
    witness_ids = ["witness_alpha", "witness_beta", "witness_gamma"]

    steps = 50
    eta = 0.1
    k_required = 2

    requirements = [
        "MANIFEST integrity check passes",
        "ATTESTATION binds to MANIFEST digest",
        "k-of-n witness provenance validates statement",
        "Replay verifier passes on included artifacts",
    ]
    nonce = vp.sha256_bytes(b"test_vector_nonce_v1")

    # -------------------------
    # Layout
    # -------------------------
    root = Path("test_vectors") / "v1_pack"
    pp = root / "PROOFPACK"
    art = pp / "ARTIFACTS"
    bundles_dir = root / "WITNESS_BUNDLES"
    keys_dir = root / ".witness_keys"
    log_dir = root / ".local_log"

    # clean + mkdir
    safe_rmtree(root)
    art.mkdir(parents=True, exist_ok=True)
    bundles_dir.mkdir(parents=True, exist_ok=True)
    keys_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Deterministic witness keys (stored locally for vector verification)
    # key = SHA256(seed ":" witness_id)
    # -------------------------
    for wid in witness_ids:
        key = hashlib.sha256(seed + b":" + wid.encode("utf-8")).digest()
        (keys_dir / f"{wid}.hmac.key").write_bytes(key)

    # -------------------------
    # Artifacts (deterministic toy)
    # -------------------------
    vp.toy_generate_artifacts(art_dir=art, steps=steps, eta=eta)

    # -------------------------
    # MANIFEST
    # -------------------------
    manifest = vp.make_manifest(pp_dir=pp, include_dirs=("ARTIFACTS",))
    vp.write_json(pp / "MANIFEST.json", manifest)
    man_digest = vp.sha256_bytes((pp / "MANIFEST.json").read_bytes())

    # -------------------------
    # ATTESTATION (manual to pin time)
    # -------------------------
    att = {
        "schema_version": vp.SCHEMA_VERSION,
        "statement_type": "vireon.proofpack.attestation.v1",
        "issued_at": issued_at,
        "subject": {"name": "v1_pack", "digest": {"sha256": man_digest}},
        "policy": {"policy_id": "vireon.proofpack.policy.v1", "requirements": requirements},
        "nonce": nonce,
    }
    vp.write_json(pp / "ATTESTATION.json", att)

    stmt_bytes = vp.canon(att)
    stmt_sha = vp.sha256_bytes(stmt_bytes)

    # -------------------------
    # Local log chain (append-only hash chain, deterministic)
    # We write the chain directly so times + prev links are pinned.
    # -------------------------
    chain_path = log_dir / "local_log_v1.chain.jsonl"
    head_path = log_dir / "local_log_v1.head"

    prev = "0" * 64
    lines = []
    bundle_refs = []

    nb = integrated_time - 5
    na = integrated_time + validity_seconds

    for wid in witness_ids:
        entry = {"prev": prev, "integrated_time": integrated_time, "statement_sha256": stmt_sha}
        entry_hash = vp.sha256_bytes(vp.canon(entry))
        lines.append(json.dumps({"entry": entry, "hash": entry_hash}))

        log = {
            "log_id": "local_log_v1",
            "integrated_time": integrated_time,
            "entry_hash_sha256": entry_hash,
            "prev_entry_hash_sha256": prev,
        }
        prev = entry_hash

        key = (keys_dir / f"{wid}.hmac.key").read_bytes()
        sig = hmac.new(key, stmt_bytes, hashlib.sha256).digest()
        cert = {"not_before": nb, "not_after": na, "key_id": vp.sha256_bytes(key)}

        bundle = {
            "schema_version": vp.SCHEMA_VERSION,
            "witness": {"witness_id": wid, "issuer": issuer, "subject": wid},
            "statement_sha256": stmt_sha,
            "signature": {"alg": "hmac-sha256", "value_b64": b64(sig)},
            "certificate": cert,
            "log": log,
        }

        out = bundles_dir / f"{wid}.json"
        vp.write_json(out, bundle)
        bundle_refs.append({"witness_id": wid, "path": out.relative_to(root).as_posix()})

    chain_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    head_path.write_text(prev, encoding="utf-8")

    # -------------------------
    # PROVENANCE_CERT (k-of-n)
    # -------------------------
    prov = {
        "schema_version": vp.SCHEMA_VERSION,
        "k": int(k_required),
        "subject_digest_sha256": man_digest,
        "bundles": bundle_refs,
    }
    vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    print("WROTE test_vectors/v1_pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
