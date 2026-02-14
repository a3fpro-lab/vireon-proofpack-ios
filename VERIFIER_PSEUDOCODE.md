# VPS v1 Verifier Pseudocode (Normative)

Given root_dir and threshold k:

1. pp := root_dir/PROOFPACK
2. m := read_json(pp/MANIFEST.json) else FAIL(MISSING_MANIFEST)
3. For each entry e in m.files:
4.   f := pp/e.path; if !exists(f) FAIL(MISSING:e.path)
5.   if SHA256(bytes(f)) != e.sha256 FAIL(SHA_MISMATCH:e.path)

6. d := SHA256(bytes(pp/MANIFEST.json))
7. a := read_json(pp/ATTESTATION.json) else FAIL(MISSING_ATTESTATION)
8. if a.subject.digest.sha256 != d FAIL(ATTESTATION_DIGEST_MISMATCH)

9. pc := read_json(pp/PROVENANCE_CERT.json) else FAIL(MISSING_PROVENANCE_CERT)
10. if pc.subject_digest_sha256 != d FAIL(PROVENANCE_DIGEST_MISMATCH)
11. if pc.k != k FAIL(K_MISMATCH_CERT)

12. s := SHA256(canon(a))
13. valid := set()
14. For each bundle ref r in pc.bundles:
15.   b := read_json(root_dir/r.path); if bundle_valid(b, a, s) valid.add(b.witness_id)
16. if |valid| < k FAIL(ONLY_|valid|_VALID)

17. If exists(pp/ARTIFACTS/RUN.json):
18.   if !replay_ok(pp/ARTIFACTS) FAIL(REPLAY_FAIL)

19. PASS
