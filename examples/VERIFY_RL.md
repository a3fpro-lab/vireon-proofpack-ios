# RL proofpack demo (stdlib-only)

This demo produces RL-style artifacts (env params, seed, returns, rollout trace) and seals them into a VPS proofpack.

## Run
```bash
python examples/rl_minicartpole.py
python examples/make_rl_proofpack.py
python tools/verify_pack_strict.py demo_rl_pack --k 2 --min-issuers 1 --max-window 86400
