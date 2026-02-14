#!/usr/bin/env python3
# vireon-verify.py
# One-file VPS verifier (stdlib only). Drop-in, run anywhere.
#
# Usage:
#   python vireon-verify.py demo_pack --k 2
#   python vireon-verify.py demo_rl_pack --k 2
#
# Notes:
# - This repo’s v1 demo uses HMAC "local witnesses" for portability.
#   That means a demo pack MUST include .witness_keys/ to verify signatures.
# - Production witnesses swap HMAC -> Ed25519/Sigstore without changing the
#   integrity/binding/k-of-n/log structure.

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
from pathlib import Path


SCHEMA_VERSION = "1.0.0"


# -------------------------
# Canonicalization + Hashes
# -------------------------

def canon(obj) -> bytes:
    # Deterministic JSON bytes (sorted keys, no whitespace)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# -------------------------
# Integrity Engine (Manifest)
# -------------------------

def verify_manifest(pp_dir: Path) -> tuple[bool, str]:
    mpath = pp_dir / "MANIFEST.json"
    if not mpath.exists():
        return False, "MISSING_MANIFEST"

    m = read_json(mpath)
    files = m.get("files", [])
    if not isinstance(files, list):
        return False, "BAD_MANIFEST_FORMAT"

    for e in files:
        rel = e.get("path")
        expect = e.get("sha256")
        if not rel or not expect:
            return False, "BAD_MANIFEST_ENTRY"

        f = pp_dir / rel
        if not f.exists():
            return False, f"MISSING:{rel}"

        got = sha256_file(f)
        if got != expect:
            return False, f"SHA_MISMATCH:{rel}"

    return True, "OK"


def manifest_digest(pp_dir: Path) -> tuple[bool, str]:
    mpath = pp_dir / "MANIFEST.json"
    if not mpath.exists():
        return False, "MISSING_MANIFEST"
    return True, sha256_bytes(mpath.read_bytes())


# -------------------------
# Binding Engine (Attestation)
# -------------------------

def verify_attestation_binds_manifest(pp_dir: Path) -> tuple[bool, str]:
    apath = pp_dir / "ATTESTATION.json"
    if not apath.exists():
        return False, "MISSING_ATTESTATION"

    ok, d = manifest_digest(pp_dir)
    if not ok:
        return False, d

    att = read_json(apath)
    try:
        if att["subject"]["digest"]["sha256"] != d:
            return False, "ATTESTATION_DIGEST_MISMATCH"
    except Exception:
        return False, "BAD_ATTESTATION_FORMAT"

    return True, "OK"


def statement_sha256(pp_dir: Path) -> tuple[bool, str]:
    apath = pp_dir / "ATTESTATION.json"
    if not apath.exists():
        return False, "MISSING_ATTESTATION"
    att = read_json(apath)
    return True, sha256_bytes(canon(att))


# --------------------------------
# Local append-only log (hash-chain)
# --------------------------------

def log_check_membership(log_dir: Path, log: dict) -> tuple[bool, str]:
    try:
        log_id = log["log_id"]
        target = log["entry_hash_sha256"]
    except Exception:
        return False, "BAD_LOG_FORMAT"

    chain = log_dir / f"{log_id}.chain.jsonl"
    if not chain.exists():
        return False, "MISSING_LOG"

    for line in chain.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("hash") == target:
            return True, "OK"

    return False, "LOG_ENTRY_NOT_FOUND"


# -------------------------
# Witness Engine (local HMAC)
# -------------------------

def verify_witness_bundle(root_dir: Path, bundle: dict) -> tuple[bool, str]:
    pp_dir = root_dir / "PROOFPACK"
    keys_dir = root_dir / ".witness_keys"
    log_dir = root_dir / ".local_log"

    ok, stmt_sha = statement_sha256(pp_dir)
    if not ok:
        return False, stmt_sha

    if bundle.get("statement_sha256") != stmt_sha:
        return False, "STATEMENT_HASH_MISMATCH"

    try:
        wid = bundle["witness"]["witness_id"]
    except Exception:
        return False, "BAD_WITNESS_FORMAT"

    key_path = keys_dir / f"{wid}.hmac.key"
    if not key_path.exists():
        return False, "MISSING_WITNESS_KEY"

    key = key_path.read_bytes()
    key_id = sha256_bytes(key)

    try:
        if key_id != bundle["certificate"]["key_id"]:
            return False, "KEY_ID_MISMATCH"
    except Exception:
        return False, "BAD_CERT_FORMAT"

    # signature check
    att = read_json(pp_dir / "ATTESTATION.json")
    stmt_bytes = canon(att)

    expected = hmac.new(key, stmt_bytes, hashlib.sha256).digest()
    try:
        got = b64d(bundle["signature"]["value_b64"])
    except Exception:
        return False, "BAD_SIGNATURE_FORMAT"

    if not hmac.compare_digest(expected, got):
        return False, "BAD_SIGNATURE"

    # cert window check
    try:
        tau = int(bundle["log"]["integrated_time"])
        nb = int(bundle["certificate"]["not_before"])
        na = int(bundle["certificate"]["not_after"])
        if not (nb <= tau <= na):
            return False, "CERT_WINDOW_FAIL"
    except Exception:
        return False, "BAD_CERT_FORMAT"

    # log membership
    ok, msg = log_check_membership(log_dir, bundle.get("log", {}))
    if not ok:
        return False, msg

    return True, "OK"


# -------------------------
# Provenance Engine (k-of-n)
# -------------------------

def verify_kofn(root_dir: Path, k: int) -> tuple[bool, str]:
    pp_dir = root_dir / "PROOFPACK"
    pc_path = pp_dir / "PROVENANCE_CERT.json"
    if not pc_path.exists():
        return False, "MISSING_PROVENANCE_CERT"

    pc = read_json(pc_path)

    try:
        if int(pc["k"]) != int(k):
            return False, "K_MISMATCH_CERT"
    except Exception:
        return False, "BAD_PROVENANCE_CERT_FORMAT"

    ok, d = manifest_digest(pp_dir)
    if not ok:
        return False, d

    if pc.get("subject_digest_sha256") != d:
        return False, "PROVENANCE_DIGEST_MISMATCH"

    valid = 0
    seen = set()

    for ref in pc.get("bundles", []):
        bpath = root_dir / ref.get("path", "")
        if not bpath.exists():
            continue

        bundle = read_json(bpath)
        ok, _msg = verify_witness_bundle(root_dir, bundle)
        if not ok:
            continue

        wid = bundle["witness"]["witness_id"]
        if wid in seen:
            continue
        seen.add(wid)
        valid += 1
        if valid >= k:
            return True, "OK"

    return False, f"ONLY_{valid}_VALID"


# -------------------------
# Replay Engine (toy only)
# -------------------------

def toy_verify_artifacts(art_dir: Path) -> tuple[bool, str]:
    run_path = art_dir / "RUN.json"
    trace_path = art_dir / "trace.json"
    if not run_path.exists() or not trace_path.exists():
        return False, "MISSING_TOY_ARTIFACTS"

    run = read_json(run_path)
    trace = read_json(trace_path)

    eta = float(run["eta"])
    alpha = float(run["alpha"])

    for row in trace:
        x = float(row["x"])
        x_next = float(row["x_next"])

        expected_next = (1 - 2 * eta) * x
        if abs(expected_next - x_next) > 1e-12:
            return False, "REPLAY_XNEXT_MISMATCH"

        E = x * x
        E_next = x_next * x_next
        P = x * x

        if not (E_next <= E - alpha * P + 1e-12):
            return False, "INEQUALITY_FAIL"

    return True, "OK"


# -------------------------
# Full Verify Pipeline + Summary
# -------------------------

def verify_pack(root_dir: Path, k: int) -> tuple[dict, str]:
    pp_dir = root_dir / "PROOFPACK"
    if not pp_dir.exists():
        return {"pack": str(root_dir), "status": "FAIL"}, "MISSING_PROOFPACK_DIR"

    summary = {
        "pack": root_dir.name,
        "k_required": k,
        "manifest_digest_sha256": None,
        "integrity": False,
        "binding": False,
        "provenance": False,
        "replay": None,
        "status": "FAIL",
    }

    ok, d = manifest_digest(pp_dir)
    if ok:
        summary["manifest_digest_sha256"] = d

    ok, msg = verify_manifest(pp_dir)
    summary["integrity"] = ok
    if not ok:
        return summary, f"integrity:{msg}"

    ok, msg = verify_attestation_binds_manifest(pp_dir)
    summary["binding"] = ok
    if not ok:
        return summary, f"binding:{msg}"

    ok, msg = verify_kofn(root_dir, k)
    summary["provenance"] = ok
    if not ok:
        return summary, f"provenance:{msg}"

    # replay is optional; only enforced if toy artifacts are present
    art_dir = pp_dir / "ARTIFACTS"
    if (art_dir / "RUN.json").exists() and (art_dir / "trace.json").exists():
        ok, msg = toy_verify_artifacts(art_dir)
        summary["replay"] = ok
        if not ok:
            return summary, f"replay:{msg}"
    else:
        summary["replay"] = None

    summary["status"] = "PASS"
    return summary, "PASS"


def print_summary(s: dict, reason: str) -> None:
    print("\n" + "=" * 62)
    print("VIREON PROOFPACK STANDARD (VPS) v1.0.0 — one-file verifier")
    print("=" * 62)
    print(f"PACK: {s.get('pack')}")
    md = s.get("manifest_digest_sha256")
    if md:
        print(f"MANIFEST_DIGEST_SHA256: {md}")
    print(f"K_REQUIRED: {s.get('k_required')}")
    print(f"INTEGRITY: {s.get('integrity')}")
    print(f"BINDING: {s.get('binding')}")
    print(f"PROVENANCE(k-of-n): {s.get('provenance')}")
    print(f"REPLAY(toy if present): {s.get('replay')}")
    print("-" * 62)
    print(f"VERIFY: {s.get('status')}   ({reason})")
    print("=" * 62 + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="One-file VPS verifier (stdlib only)")
    ap.add_argument("pack", help="Path to pack directory (must contain PROOFPACK/)")
    ap.add_argument("--k", type=int, default=2, help="k-of-n threshold (default: 2)")
    args = ap.parse_args()

    root = Path(args.pack)
    summary, reason = verify_pack(root, args.k)
    print_summary(summary, reason)
    return 0 if summary.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
