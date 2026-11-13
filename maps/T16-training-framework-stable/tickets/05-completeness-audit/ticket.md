---
id: T16-05
title: scinetics 的稳定提交是否已包含全部最新架构与优化？哪些优化只存在于未合并的分支或 worktree，各自是否应并入？
type: research
status: resolved (t16-codex-driver, 2026-11-13T07:55:00Z)
blocked_by: []
updated: 2026-11-13T07:48:32Z
---

## Question
用户（2026-11-13）：要保证 scinetics 代码完备、带有所有最新架构和优化。逐个盘点 origin/main `35f9646`（含 PR #3、#4）与 PR #5 之外仍有未合并提交的分支和 worktree（盘点时 origin/main 之上领先：`codex/fp8-perf-node16-20261025` 43、`codex/fp8-merge-gates-20261024` 42、`codex/v22-successor-node3` 41、`codex/cpt-2b-tps-20261017` 8、`codex/pt-stability-20261019` 5、`codex/v23-resume-24gpu-20261025` 3、`feat/tool-sft-runtime-20261028` 2、`codex/spike-diagnosis-v20` 2、`codex/token-loss-safety` 1、`codex/packmix-v22` 1，另有 worktree `scinetics-node7-v16`）。对每个分支回答：领先提交里的内容是否已被 PR #3/#4 以合并或重写方式包含（对比文件内容，不只看提交号）；没有包含的功能或优化是什么；有无验收记录；是否冲突于稳定提交。

## Acceptance
- 一张表：分支、领先提交数、已包含的内容、未包含的功能/优化、证据（文件与提交）、建议（并入 / 不并入 / 需验证）及理由。
- 对比用文件内容与 diff，不是提交信息；列出所用命令与分母（比较的文件数）。
- 把“架构与优化清单”写成 `reference/feature-inventory.md`：每项对应的代码位置、配置开关、有无验证记录；稳定介绍页（T16-03）据此补全。
- 不合并、不推送；建议并入的项由用户决定。

## Log
- 2026-11-13T07:48:32Z (desk) 开票。

## Answer

脚本 `audit.sh` 与原始输出 `audit-output.txt` 已落票目录；比较分母是每个 ref 相对 pinned base 的全部 git 文件 diff（8–65 changed files）。结果表与架构/优化清单见 `reference/feature-inventory.md`。35f9646 已包含 PR #3/#4 的稳定 CPT、续训、ZeRO-1 重分片与 stability hook；其余分支仍有未证明纳入的实验/优化，未自动合并，建议按表逐项评审。
