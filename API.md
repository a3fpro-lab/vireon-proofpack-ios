# API (Reference Implementation)

This repo exposes a minimal, stable interface for Proofpacks.

## Core module
`vproofpack.py`

### Canon + Hash
- `canon(obj) -> bytes`  
  Deterministic JSON encoding (sorted keys, no whitespace).
- `sha256_bytes(b: bytes) -> str`
- `sha256_file(path: Path) -> str`

### Integrity Engine
- `make_manifest(pp_dir: Path, include_dirs=("ARTIFACTS",)) -> dict`
- `verify_manifest(pp_dir: Path) -> (bool, str)`
- `manifest_digest(pp_dir: Path) -> str`  
  SHA256 over `MANIFEST.json` bytes.

### Binding Engine
- `make_attestation(pp_dir: Path, subject_name: str, policy_id: str, requirements: list, nonce: str) -> dict`
- `verify_attestation_binds_manifest(pp_dir: Path) -> (bool, str)`

### Log Engine (toy transparency log)
- `log_append(log_dir: Path, statement_sha256: str, log_id="local_log_v1") -> dict`
- `log_check_membership(log_dir: Path, log: dict, statement_sha256: str) -> (bool, str)`

### Witness Engine (demo: local HMAC)
- `make_witness_bundle(root_dir: Path, witness_id: str, issuer: str, subject: str, validity_seconds=3600) -> dict`
- `verify_witness_bundle(root_dir: Path, bundle: dict) -> (bool, str)`

### Provenance Engine (k-of-n)
- `make_provenance_cert(pp_dir: Path, k: int, bundle_refs: list) -> dict`
- `verify_kofn(root_dir: Path, k: int) -> (bool, str)`

### Replay Engine (toy deterministic)
- `toy_generate_artifacts(art_dir: Path, steps=50, eta=0.1) -> None`
- `toy_verify_artifacts(art_dir: Path) -> (bool, str)`

### Full verifier
- `verify_all(root_dir: Path, k: int = 2) -> (bool, str)`
Pipeline order:
1) integrity
2) binding
3) provenance
4) replay (if RUN.json exists)

Returns `(True, "PASS")` on success, else `(False, "<stage>:<reason>")`.

## Scripts
- `make_demo_pack.py` → writes `demo_pack/`
- `verify_demo_pack.py` → prints PASS/FAIL
- `tools/verify_pack.py <pack> --k K` → verify any pack
- `tools/attack_suite.py` → demonstrates three tamper attacks
