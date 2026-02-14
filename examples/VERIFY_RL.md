# RL proofpack demo (stdlib-only)

This demo produces RL-style artifacts (env params, seed, returns, rollout trace) and seals them into a VPS proofpack.

## Run
```bash
python examples/rl_minicartpole.py
python examples/make_rl_proofpack.py
python tools/verify_pack_strict.py demo_rl_pack --k 2 --min-issuers 1 --max-window 86400

If PASS, the published “avg_return” and rollout trace are cryptographically bound to the claim statement and k-of-n provenance.

---

## CI UPDATE (make it official)
Add these steps near the end of `.github/workflows/ci.yml` (before pinned vectors is fine):

```yaml
      - name: RL artifacts (stdlib demo)
        run: python examples/rl_minicartpole.py

      - name: RL proofpack seal
        run: python examples/make_rl_proofpack.py

      - name: RL proofpack verify (strict)
        run: python tools/verify_pack_strict.py demo_rl_pack --k 2 --min-issuers 1 --max-window 86400


