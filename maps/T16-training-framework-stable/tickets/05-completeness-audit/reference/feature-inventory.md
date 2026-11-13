# Stable-commit feature inventory

Source command and denominator are recorded in `../audit.sh` and `../audit-output.txt`. The audit compares each named ref to pinned `35f9646` by file content (`git diff --stat BASE...REF`), not commit messages. The ten requested branches have 8–65 changed files beyond the base.

| Branch | Ahead | Content not demonstrated in 35f9646 | Evidence / recommendation |
|---|---:|---|---|
| `codex/fp8-perf-node16-20261025` | 43 | FP8 performance candidates and node16 runs | 65 files/5884 insertions; recommend separate review, not auto-merge |
| `codex/fp8-merge-gates-20261024` | 42 | FP8 merge-gate experiments and export checks | 65 files/5861 insertions; historical evidence exists, needs cherry-pick review |
| `codex/v22-successor-node3` | 41 | v22 successor training/diagnostics | 61 files/5510 insertions; not proven compatible with stable CPT |
| `codex/cpt-2b-tps-20261017` | 8 | 2B throughput instrumentation | 10 files/599 insertions; benchmark-only, no stability evidence |
| `codex/pt-stability-20261019` | 5 | stability tooling | 15 files/993 insertions; PR #4 has a different stability hook, compare before merge |
| `codex/v23-resume-24gpu-20261025` | 3 | 24-GPU resume workflow | 10 files/808 insertions; historical run, not 0.8B stable contract |
| `feat/tool-sft-runtime-20261028` | 2 | tool-call SFT runtime | 16 files/1036 insertions; explicitly outside T16 stable scope |
| `codex/spike-diagnosis-v20` | 2 | diagnosis spike | 5 files/117 insertions; exploratory, do not merge |
| `codex/token-loss-safety` | 1 | token-loss safety guard | 14 files/447 insertions; needs targeted regression review |
| `codex/packmix-v22` | 1 | packmix v22 | 8 files/242 insertions; changes data ordering contract, do not merge without new identity evidence |

The audit also records the `scinetics-node7-v16` worktree on `codex/node7-full-speed-v16`; its branch is not in the named list and must be audited separately before claiming completeness. No branch is merged or pushed by this ticket.
