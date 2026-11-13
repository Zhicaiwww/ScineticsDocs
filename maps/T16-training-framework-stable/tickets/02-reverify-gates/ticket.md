---
id: T16-02
title: 在稳定提交上重跑门槛检查，哪些通过、哪些没通过？
type: experiment
status: open
blocked_by: [T16-01]
cost_cap: 5 GPU 小时
jobs: []
updated: 2026-11-13T07:00:13Z
---

## Question
在 T16-01 确定的提交（独立 worktree）上：(1) CPU 测试；(2) 221 文件身份检查；(3) 0.8B 四卡 BF16 与 FP8 各 10 步，FP8 覆盖 66 区域；(4) step2→10 恢复；(5) 原生导出 473 张量并严格读回；(6) PR #4 新增的续训、ZeRO-1 重分片、稳定性评测各跑一次最小用例；(7) 2B 单节点 BF16/FP8 各一个短测。结果如何？

## Acceptance
- 通过标准在跑之前固定：全部 loss 与 grad_norm 有限；FP8 对 BF16 的 NLL 相对差 ≤0.5%；恢复后 loss 与不中断对照一致；导出读回无差异。
- 每项给 run-id@node、日志路径和数字；失败项写明原因，不重试到通过为止。
- 短测不作为长期质量或速度结论。

## Log
- 2026-11-13T07:00:13Z (desk) 开票，等 T16-01。
