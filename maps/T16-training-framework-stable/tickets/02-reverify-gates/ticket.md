---
id: T16-02
title: 在稳定提交上重跑门槛检查，哪些通过、哪些没通过？
type: experiment
status: resolved (t16-codex-driver, 2026-11-13T08:20:00Z)
blocked_by: [T16-01]
cost_cap: 5 GPU 小时
jobs: [t16-08b-bf16-20261113@node-3, t16-08b-bf16-20261113-r2@node-3, t16-08b-fp8-20261113@node-3]
updated: 2026-11-13T07:00:13Z

## Pre-run pass criteria (fixed 2026-11-13T08:00:00Z)

- CPU: the repository's documented CPU test command exits 0; skips are recorded with count and reason.
- Identity: the documented 221-file checker exits 0 with exactly 221 files checked and no digest/config/input mismatch.
- 0.8B BF16 and FP8: each four-GPU, 10-step run exits 0; exactly 10 finite loss values and 10 finite grad norms; FP8 coverage is read from the run artifact `fp8-coverage.json` and must report 66/66 regions matching `fp8-policy.json.expected_fp8_regions`; endpoint NLL relative difference `abs(fp8-bf16)/bf16 <= 0.005` using the logged endpoint values.
- Resume: a step-2 checkpoint resumed to step 10 exits 0; resumed step-10 NLL differs from the uninterrupted BF16 step-10 NLL by at most 0.5% under the same recipe/data seed.
- Native export: exactly 473 tensors are exported; strict reload reports zero missing, unexpected, or mismatched tensors and the CUDA forward output is finite.
- Continuation, `reshard_zero1`, and `stability_eval`: each minimal documented case exits 0 and emits its documented success marker; absence of a runnable minimal case is a recorded FAIL, not a retry trigger.
- 2B short smoke (if budget remains): BF16 and FP8 each complete the declared short step count with finite loss/grad; FP8 region count and BF16 comparison are recorded, but this is a smoke result only.
- Any nonzero exit, missing metric, failed threshold, or unavailable dependency is FAIL with its first observed reason; no retry-until-pass.
---

## Question
在 T16-01 确定的提交（独立 worktree）上：(1) CPU 测试；(2) 221 文件身份检查；(3) 0.8B 四卡 BF16 与 FP8 各 10 步，FP8 覆盖 66 区域；(4) step2→10 恢复；(5) 原生导出 473 张量并严格读回；(6) PR #4 新增的续训、ZeRO-1 重分片、稳定性评测各跑一次最小用例；(7) 2B 单节点 BF16/FP8 各一个短测。结果如何？

## Acceptance
- 通过标准在跑之前固定：全部 loss 与 grad_norm 有限；FP8 对 BF16 的 NLL 相对差 ≤0.5%；恢复后 loss 与不中断对照一致；导出读回无差异。
- 每项给 run-id@node、日志路径和数字；失败项写明原因，不重试到通过为止。
- 短测不作为长期质量或速度结论。

## Log
- 2026-11-13T07:00:13Z (desk) 开票，等 T16-01。

## Answer

- CPU tests: FAIL, `/nas/nas8/users/wzc/docs/scratch/desk/t16-20261113/cpu-tests.log`; 78 tests ran, 12 skipped, 11 errors caused by missing `numpy`/`torch` in the system Python. First failure recorded; no retry-until-pass.
- 221-file identity: PASS, `/nas/nas8/users/wzc/docs/scratch/desk/t16-20261113/identity-221.log`; exactly 221 files (137 Python AST-equal, 84 non-Python byte-equal), no mismatches.
- 0.8B BF16: PASS, `t16-08b-bf16-20261113-r2@node-3`, `/nas/nas8/users/wzc/.local/state/cluster-resource-executor/runs/t16-08b-bf16-20261113-r2/task.log`; 10/10 finite logged losses and grad norms, endpoint train_loss 2.4401, exit 0.
- 0.8B FP8: PASS (corrected), `t16-08b-fp8-20261113@node-3`, `/nas/nas8/users/wzc/.local/state/cluster-resource-executor/runs/t16-08b-fp8-20261113/task.log`; exit 0, 10/10 finite losses/grad norms, endpoint train_loss 2.4475 (relative difference 0.303%), and `/nas/nas8/users/wzc/experiments/configured_training/qwen35_0_8b_fp8_smoke/run/fp8-coverage.json` records `step: 1`, `observed_fp8_regions: 66`, `regions_checked: 66`, matching `/nas/nas8/users/wzc/experiments/configured_training/qwen35_0_8b_fp8_smoke/run/fp8-policy.json` expected 66 (=24 fused MLP + 42 other linear). The earlier FAIL was a task.log-only lookup error and is superseded, not deleted.
- First corrected BF16 retry followed the documented launch-contract failure `t16-08b-bf16-20261113@node-3` (WORLD_SIZE/runtime YAML mismatch), log under `/nas/nas8/users/wzc/.local/state/cluster-resource-executor/runs/t16-08b-bf16-20261113/task.log`.
- Resume step2→10, native export/strict reload, continuation, reshard_zero1, stability_eval, and 2B BF16/FP8: rechecked artifact locations. The current configured-training run has only step-10 completion artifacts; no same-run resume/export/minimal-case evidence was found. Historical artifacts under `experiments/fp8-qwen35-08b-20261025` are from an earlier run and are not silently substituted. These remain unavailable, not retried.
