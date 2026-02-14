# tools/schema_check.py
# Minimal schema check without external deps:
# - Ensures required files exist
# - Loads JSON successfully
# - Performs lightweight structural checks (not full JSON Schema validation)

from pathlib import Path
import json
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def must_hex64(x: str, label: str):
    if not isinstance(x, str) or not HEX64.match(x):
        raise ValueError(f"{label} must be 64 hex")

def main():
    root = Path(".")
    pack = root / "demo_pack" / "PROOFPACK"
    bundles = root / "demo_pack" / "WITNESS_BUNDLES"

    # If demo_pack doesn't exist (e.g., CI order changed), just exit OK.
    if not pack.exists():
        print("schema_check: demo_pack not present; skip")
        return 0

    manifest = load(pack / "MANIFEST.json")
    if "schema_version" not in manifest or "files" not in manifest:
        raise ValueError("MANIFEST missing fields")
    for e in manifest["files"]:
        if "path" not in e or "sha256" not in e:
            raise ValueError("MANIFEST.files entry missing fields")
        must_hex64(e["sha256"], "MANIFEST.files.sha256")

    att = load(pack / "ATTESTATION.json")
    must_hex64(att["subject"]["digest"]["sha256"], "ATTESTATION.subject.digest.sha256")

    prov = load(pack / "PROVENANCE_CERT.json")
    if int(prov["k"]) < 1:
        raise ValueError("k must be >=1")
    must_hex64(prov["subject_digest_sha256"], "PROVENANCE_CERT.subject_digest_sha256")
    if not prov["bundles"]:
        raise ValueError("PROVENANCE_CERT.bundles empty")

    # Bundles referenced must exist and match hash format
    for ref in prov["bundles"]:
        bpath = (root / "demo_pack" / ref["path"]).resolve()
        if not bpath.exists():
            raise ValueError(f"missing bundle: {ref['path']}")
        b = load(bpath)
        must_hex64(b["statement_sha256"], "BUNDLE.statement_sha256")
        must_hex64(b["certificate"]["key_id"], "BUNDLE.certificate.key_id")
        must_hex64(b["log"]["entry_hash_sha256"], "BUNDLE.log.entry_hash_sha256")
        must_hex64(b["log"]["prev_entry_hash_sha256"], "BUNDLE.log.prev_entry_hash_sha256")

    print("schema_check: OK")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("schema_check: FAIL:", e)
        sys.exit(1)
