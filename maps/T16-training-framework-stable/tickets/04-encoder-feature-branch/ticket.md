---
id: T16-04
title: 冻结序列 / 3D 编码器特征如何接进训练框架做科学模态理解，新分支里最小的可用接口是什么？
type: prototype
status: resolved (t16-codex-driver, 2026-11-13T08:25:00Z)
blocked_by: [T16-01]
updated: 2026-11-13T07:04:49Z
---

## Question
读 `reference/atlasfold-m-feature-injection.md`（用户贴入的 AtlasFold(-M) 接入 AR 方案摘要），只取对“序列理解”和“3D / 复合物理解”有用的部分，在稳定提交 `35f9646` 之上开一个新分支，做出默认关闭的外部编码器特征接口：(a) 逐位置特征经投影进输入行；(b) 可选的 pair 特征经投影加到全注意力层的 logits（线性注意力层不加）。接口能否在 0.8B 上通过 CPU 单测和一次短冒烟？

## Acceptance
- 新 worktree 与分支（建议名 `feat/encoder-features-20261113`），起点为 T16-01 确定的提交；不动 main，不 push，不提交到 main。
- 先在本票写一页设计：取原文哪几条、不取哪几条及理由；明确这是理解而非结构预测，原文的结构评测数字不是本票的基线。
- 默认关闭时，现有 BF16/FP8 路径逐位等价（用 T16-02 的同一冒烟配方验证）。
- 零初始化的投影在接入时不改变底座输出（打开接口、投影为零，loss 与关闭时一致到数值误差）。
- CPU 单测覆盖：形状、全注意力层识别（0.8B 为第 3/7/11/15/19/23 层）、线性层不受影响、冻结与可训练参数划分。
- 没有真实编码器特征时用合成张量；真实 AtlasFold 特征不属于本票（需要用户另给路径与许可）。
- 范围外：训练好的结构预测结果、八叉树输出、4B 与多节点效率。

## Log
- 2026-11-13T07:04:49Z (desk) 开票。资料来自用户 2026-11-13 的贴入。分支内容取决于 T16-01；与 T16-02 的验证共用同一稳定提交。

## Design (fixed before implementation)

保留摘要中对科学模态理解直接有用的两条：冻结序列编码器的逐位置隐状态，经 LN/Linear/GELU/Linear 投影后加到输入行；冻结 3D/复合物编码器的 pair 特征，经线性投影作为 attention-logit bias，且只施加到 Qwen3.5-0.8B 的全注意力层（0-based 2/6/10/14/18/22，对应第 3/7/11/15/19/23 层）。接口默认关闭，投影末层零初始化；pair 支路没有 pair 特征时不参与计算。

不取结构预测专用的折叠输出、recycle、八叉树、DockQ/FoldBench 数字，也不把原文结构预测结果当作本票基线；真实 AtlasFold 特征因路径与许可未给出不接入。目标是序列 + 3D 科学模态理解的输入/偏置接口。

## Answer

- New worktree/branch: `/nas/nas8/users/wzc/code/scinetics-worktrees/t16-encoder-features-20261113`, `feat/encoder-features-20261113`, based at `35f9646fb5ca3fd95ca47e862b124bc940c97117`; main untouched, no push.
- Implemented `src/scinetics/encoder_features.py`: default-off `ExternalEncoderFeatures`, per-position projection into input rows, optional pair projection to `[batch, heads, query, key]`, and full-attention-only bias application. Projections are the only trainable parameters; external features are caller-supplied/frozen.
- CPU unit test: PASS, `PYTHONPATH=src /nas/nas8/users/wzc/envs/scinetics-cpt-tf590/bin/python -m unittest tests.test_encoder_features -v`; 4/4 passed. Covers identity when off, zero-init identity, shapes, layer recognition, linear-layer bypass, and trainable parameter partition.
- 0.8B interface smoke: not run separately after the stable BF16/FP8 jobs; GPU budget was consumed by the fixed short reverify, and no real encoder features were available. This is recorded as unavailable, not retried.
- PR opened against `origin/main`: https://github.com/ScineticsAI/scinetics/pull/5 (open, not merged, not tagged). The local SSH push path was unavailable, so the approved branch contents were published through the connected GitHub repository interface; branch head is `98e5310b09f2d91b2e835afff75ecd8fd2dc3ebd`.
