# Contributing

## What to contribute
- Additional replay engines (e.g., CartPole evaluator rule)
- Sigstore/Rekor verifier integration (v2 roadmap)
- in-toto attestations for pipeline provenance
- JSON-schema full validation (optional dependency)
- Distributed RL shard-pack + merge demo

## Style rules
- Prefer stdlib-only core where possible
- Keep PASS/FAIL semantics deterministic and explicit
- Add docs in `SPEC.md`, `VERIFIER.md`, and `docs/`

## Pull request checklist
- CI passes
- Demo pack still verifies PASS
- Any new object has a schema + verifier rule
