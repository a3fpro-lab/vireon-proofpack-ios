# vproofpack.py
# Proofpacks (iPhone-safe build): integrity + binding + k-of-n provenance + append-only log + replay.
# Stdlib only. Uses HMAC-SHA256 "local witnesses" so it runs anywhere.
# Swap HMAC -> Ed25519/Sigstore later using the same interfaces.

import os
import json
import time
import base64
import hashlib
import hmac
from pathlib import Path

SCHEMA_VERSION = "1.0.0"


# -------------------------
# Canonicalization + Hashes
# -------------------------

def canon(obj) -> bytes:
    """Deterministic JSON bytes (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# -------------------------
# Integrity Engine (Manifest)
# -------------------------

def make_manifest(pp_dir: Path, include_dirs=("ARTIFACTS",)) -> dict:
    files = []
    for d in include_dirs:
        base = pp_dir / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file():
                rel = p.relative_to(pp_dir).as_posix()
                files.append({"path": rel, "sha256": sha256_file(p)})
    # You can also include ATTESTATION/PROVENANCE_CERT if you want a tighter closure.
    return {"schema_version": SCHEMA_VERSION, "files": files}


def verify_manifest(pp_dir: Path) -> (bool, str):
    mpath = pp_dir / "MANIFEST.json"
    if not mpath.exists():
        return False, "MISSING_MANIFEST"
    m = read_json(mpath)
    for e in m["files"]:
        f = pp_dir / e["path"]
        if not f.exists():
            return False, f"MISSING:{e['path']}"
        got = sha256_file(f)
        if got != e["sha256"]:
            return False, f"SHA_MISMATCH:{e['path']}"
    return True, "OK"


def manifest_digest(pp_dir: Path) -> str:
    """Digest over MANIFEST.json bytes (binding target)."""
    return sha256_bytes((pp_dir / "MANIFEST.json").read_bytes())


# -------------------------
# Binding Engine (Attestation)
# -------------------------

def make_attestation(pp_dir: Path, subject_name: str, policy_id: str, requirements: list, nonce: str) -> dict:
    d = manifest_digest(pp_dir)
    return {
        "schema_version": SCHEMA_VERSION,
        "statement_type": "vireon.proofpack.attestation.v1",
        "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "subject": {"name": subject_name, "digest": {"sha256": d}},
        "policy": {"policy_id": policy_id, "requirements": requirements},
        "nonce": nonce,
    }


def attestation_hash(att: dict) -> str:
    return sha256_bytes(canon(att))


def verify_attestation_binds_manifest(pp_dir: Path) -> (bool, str):
    apath = pp_dir / "ATTESTATION.json"
    if not apath.exists():
        return False, "MISSING_ATTESTATION"
    att = read_json(apath)
    d = manifest_digest(pp_dir)
    if att["subject"]["digest"]["sha256"] != d:
        return False, "ATTESTATION_DIGEST_MISMATCH"
    return True, "OK"


# --------------------------------
# Local append-only log (hash-chain)
# --------------------------------

def log_append(log_dir: Path, statement_sha256: str, log_id="local_log_v1") -> dict:
    log_dir.mkdir(parents=True, exist_ok=True)
    chain = log_dir / f"{log_id}.chain.jsonl"
    head = log_dir / f"{log_id}.head"

    prev = "0" * 64
    if head.exists():
        prev = head.read_text(encoding="utf-8").strip()

    tau = int(time.time())
    entry = {"prev": prev, "integrated_time": tau, "statement_sha256": statement_sha256}
    entry_hash = sha256_bytes(canon(entry))

    chain.open("a", encoding="utf-8").write(json.dumps({"entry": entry, "hash": entry_hash}) + "\n")
    head.write_text(entry_hash, encoding="utf-8")

    return {
        "log_id": log_id,
        "integrated_time": tau,
        "entry_hash_sha256": entry_hash,
        "prev_entry_hash_sha256": prev,
    }


def log_check_membership(log_dir: Path, log: dict, statement_sha256: str) -> (bool, str):
    log_id = log["log_id"]
    chain = log_dir / f"{log_id}.chain.jsonl"
    if not chain.exists():
        return False, "MISSING_LOG"

    tau = int(log["integrated_time"])
    prev = log["prev_entry_hash_sha256"]
    expected_entry = {"prev": prev, "integrated_time": tau, "statement_sha256": statement_sha256}
    expected_hash = sha256_bytes(canon(expected_entry))

    if expected_hash != log["entry_hash_sha256"]:
        return False, "LOG_HASH_MISMATCH"

    target = log["entry_hash_sha256"]
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

def ensure_witness_key(keys_dir: Path, witness_id: str) -> bytes:
    keys_dir.mkdir(parents=True, exist_ok=True)
    kpath = keys_dir / f"{witness_id}.hmac.key"
    if kpath.exists():
        return kpath.read_bytes()
    key = os.urandom(32)
    kpath.write_bytes(key)
    return key


def make_witness_bundle(root_dir: Path, witness_id: str, issuer: str, subject: str, validity_seconds=3600) -> dict:
    pp_dir = root_dir / "PROOFPACK"
    keys_dir = root_dir / ".witness_keys"
    log_dir = root_dir / ".local_log"

    att = read_json(pp_dir / "ATTESTATION.json")
    stmt_bytes = canon(att)
    stmt_sha = sha256_bytes(stmt_bytes)

    key = ensure_witness_key(keys_dir, witness_id)
    sig = hmac.new(key, stmt_bytes, hashlib.sha256).digest()

    now = int(time.time())
    cert = {"not_before": now - 5, "not_after": now + int(validity_seconds), "key_id": sha256_bytes(key)}

    log = log_append(log_dir, stmt_sha)

    return {
        "schema_version": SCHEMA_VERSION,
        "witness": {"witness_id": witness_id, "issuer": issuer, "subject": subject},
        "statement_sha256": stmt_sha,
        "signature": {"alg": "hmac-sha256", "value_b64": b64(sig)},
        "certificate": cert,
        "log": log,
    }


def verify_witness_bundle(root_dir: Path, bundle: dict) -> (bool, str):
    pp_dir = root_dir / "PROOFPACK"
    keys_dir = root_dir / ".witness_keys"
    log_dir = root_dir / ".local_log"

    att = read_json(pp_dir / "ATTESTATION.json")
    stmt_bytes = canon(att)
    stmt_sha = sha256_bytes(stmt_bytes)

    if bundle["statement_sha256"] != stmt_sha:
        return False, "STATEMENT_HASH_MISMATCH"

    wid = bundle["witness"]["witness_id"]
    key_path = keys_dir / f"{wid}.hmac.key"
    if not key_path.exists():
        return False, "MISSING_WITNESS_KEY"
    key = key_path.read_bytes()

    if sha256_bytes(key) != bundle["certificate"]["key_id"]:
        return False, "KEY_ID_MISMATCH"

    expected = hmac.new(key, stmt_bytes, hashlib.sha256).digest()
    got = b64d(bundle["signature"]["value_b64"])
    if not hmac.compare_digest(expected, got):
        return False, "BAD_SIGNATURE"

    tau = int(bundle["log"]["integrated_time"])
    nb = int(bundle["certificate"]["not_before"])
    na = int(bundle["certificate"]["not_after"])
    if not (nb <= tau <= na):
        return False, "CERT_WINDOW_FAIL"

    ok, msg = log_check_membership(log_dir, bundle["log"], stmt_sha)
    if not ok:
        return False, msg

    return True, "OK"


# -------------------------
# Provenance Engine (k-of-n)
# -------------------------

def make_provenance_cert(pp_dir: Path, k: int, bundle_refs: list) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "k": int(k),
        "subject_digest_sha256": manifest_digest(pp_dir),
        "bundles": bundle_refs,
    }


def verify_kofn(root_dir: Path, k: int) -> (bool, str):
    pp_dir = root_dir / "PROOFPACK"
    pc_path = pp_dir / "PROVENANCE_CERT.json"
    if not pc_path.exists():
        return False, "MISSING_PROVENANCE_CERT"

    pc = read_json(pc_path)
    if int(pc["k"]) != int(k):
        return False, "K_MISMATCH_CERT"

    if pc["subject_digest_sha256"] != manifest_digest(pp_dir):
        return False, "PROVENANCE_DIGEST_MISMATCH"

    seen = set()
    valid = 0
    for ref in pc["bundles"]:
        bpath = root_dir / ref["path"]
        if not bpath.exists():
            continue
        bundle = read_json(bpath)
        ok, _ = verify_witness_bundle(root_dir, bundle)
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
# Replay Engine (deterministic toy)
# -------------------------

def toy_generate_artifacts(art_dir: Path, steps=50, eta=0.1) -> None:
    """
    Writes:
      RUN.json (params)
      trace.json (step-by-step)
      CLAIM.json (human-readable claim)
    """
    art_dir.mkdir(parents=True, exist_ok=True)

    alpha = 4 * eta - 4 * (eta ** 2)  # tight constant for the toy inequality
    x = 1.23456789

    trace = []
    for t in range(int(steps)):
        x_next = (1 - 2 * eta) * x
        trace.append({"t": t, "x": x, "x_next": x_next})
        x = x_next

    write_json(art_dir / "RUN.json", {"toy": "quadratic_descent_v1", "eta": eta, "alpha": alpha, "steps": int(steps)})
    write_json(art_dir / "trace.json", trace)
    write_json(
        art_dir / "CLAIM.json",
        {
            "claim_type": "toy_descent_certificate",
            "statement": "For every step in trace.json, x_next = (1-2*eta)*x and x_next^2 <= x^2 - alpha*x^2.",
            "accept": "PASS if verifier recomputes and inequality holds for all rows",
        },
    )


def toy_verify_artifacts(art_dir: Path) -> (bool, str):
    run_path = art_dir / "RUN.json"
    trace_path = art_dir / "trace.json"
    if not run_path.exists() or not trace_path.exists():
        return False, "MISSING_TOY_ARTIFACTS"

    run = read_json(run_path)
    eta = float(run["eta"])
    alpha = float(run["alpha"])

    trace = read_json(trace_path)
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
# Full Verify Pipeline
# -------------------------

def verify_all(root_dir: Path, k: int = 2) -> (bool, str):
    """
    Full verifier: integrity -> binding -> provenance -> replay (if toy artifacts exist).
    """
    pp_dir = root_dir / "PROOFPACK"

    ok, msg = verify_manifest(pp_dir)
    if not ok:
        return False, f"integrity:{msg}"

    ok, msg = verify_attestation_binds_manifest(pp_dir)
    if not ok:
        return False, f"binding:{msg}"

    ok, msg = verify_kofn(root_dir, k)
    if not ok:
        return False, f"provenance:{msg}"

    art_dir = pp_dir / "ARTIFACTS"
    if (art_dir / "RUN.json").exists():
        ok, msg = toy_verify_artifacts(art_dir)
        if not ok:
            return False, f"replay:{msg}"

    return True, "PASS"
