import os
import shutil
import tempfile
import unittest
from pathlib import Path

import vproofpack as vp


class TestVerifierContract(unittest.TestCase):
    def setUp(self):
        # Keep CI stable: never leave the process in a temp directory after cleanup.
        self._orig_cwd = Path.cwd()

        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

        # Work inside tmp, but remember to restore cwd in tearDown.
        os.chdir(self.tmp_path)

        self.root = self.tmp_path / "demo_pack"
        pp = self.root / "PROOFPACK"
        art = pp / "ARTIFACTS"
        bundles = self.root / "WITNESS_BUNDLES"

        art.mkdir(parents=True, exist_ok=True)
        bundles.mkdir(parents=True, exist_ok=True)

        # 1) deterministic artifacts
        vp.toy_generate_artifacts(art_dir=art, steps=10, eta=0.1)

        # 2) manifest
        manifest = vp.make_manifest(pp_dir=pp, include_dirs=("ARTIFACTS",))
        vp.write_json(pp / "MANIFEST.json", manifest)

        # 3) attestation binds to manifest digest
        att = vp.make_attestation(
            pp_dir=pp,
            subject_name="demo_pack",
            policy_id="vireon.proofpack.policy.v1",
            requirements=["demo"],
            nonce=vp.sha256_bytes(b"demo"),
        )
        vp.write_json(pp / "ATTESTATION.json", att)

        # 4) witness bundles + provenance cert
        witness_ids = ["witness_alpha", "witness_beta", "witness_gamma"]
        refs = []
        for wid in witness_ids:
            b = vp.make_witness_bundle(
                root_dir=self.root,
                witness_id=wid,
                issuer="vireon_local",
                subject=wid,
                validity_seconds=3600,
            )
            out = bundles / f"{wid}.json"
            vp.write_json(out, b)
            refs.append({"witness_id": wid, "path": out.relative_to(self.root).as_posix()})

        prov = vp.make_provenance_cert(pp_dir=pp, k=2, bundle_refs=refs)
        vp.write_json(pp / "PROVENANCE_CERT.json", prov)

    def tearDown(self):
        # Critical: restore cwd BEFORE deleting tempdir.
        try:
            os.chdir(self._orig_cwd)
        finally:
            self.tmp.cleanup()

    def test_pass_happy_path(self):
        ok, msg = vp.verify_all(self.root, k=2)
        self.assertTrue(ok, msg)

    def test_integrity_bitflip_fails(self):
        trace = self.root / "PROOFPACK" / "ARTIFACTS" / "trace.json"
        b = trace.read_bytes()
        b2 = bytearray(b)
        b2[0] = (b2[0] + 1) % 256
        trace.write_bytes(bytes(b2))

        ok, msg = vp.verify_all(self.root, k=2)
        self.assertFalse(ok)
        self.assertTrue(msg.startswith("integrity:"), msg)

    def test_binding_swap_fails(self):
        pp = self.root / "PROOFPACK"
        att = vp.read_json(pp / "ATTESTATION.json")
        att["subject"]["digest"]["sha256"] = "0" * 64
        vp.write_json(pp / "ATTESTATION.json", att)

        ok, msg = vp.verify_all(self.root, k=2)
        self.assertFalse(ok)
        self.assertTrue(msg.startswith("binding:"), msg)

    def test_provenance_k_fails_if_keys_missing(self):
        keys = self.root / ".witness_keys"
        shutil.rmtree(keys, ignore_errors=True)

        ok, msg = vp.verify_all(self.root, k=2)
        self.assertFalse(ok)
        self.assertTrue(msg.startswith("provenance:"), msg)


if __name__ == "__main__":
    unittest.main()
