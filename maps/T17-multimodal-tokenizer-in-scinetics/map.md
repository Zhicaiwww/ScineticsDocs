---
id: T17
title: 把 v0 BioMatrix 的科学模态 tokenizer 处理并入 scinetics 架构，并让 tokenizer 能持续迭代
status: claimed (t17-codex-driver, 2026-11-13T07:32:00Z)
outcome:
updated: 2026-11-13T07:46:00Z
---

## Destination

训练仓库 `scinetics` 内有一层“模态编码 + 统一 tokenizer”的正式模块：(1) 每个模态（文本、DNA/RNA、蛋白 1D、分子 1D SMILES/SELFIES、分子 3D、蛋白 3D）有一个编码器插件，输入原始记录、输出带边界标记的符号序列，接口统一；(2) 统一 tokenizer 是带版本和 SHA 的产物，词表变化走声明的兼容契约（追加保留 token 或新版本）；(3) 在固定样本上，CPU 编码器的输出与 v0 参考实现逐样本 token id 一致（0 不一致）；(4) 有一条文档化的“迭代 tokenizer”流程：改什么、怎样验证、哪些改动会使已有预计算数据失效。

## Notes

- 用户（2026-11-13）：“这些 tokenizer 的处理，都需要加入到当前的 scinetics 的架构中，我们也要不断的迭代我的 tokenizer。”
- 事实起点（读自 `models/v0/architecture.md` §4、§4A，未重跑）：统一 tokenizer.json 264,465 行（基础 BPE 248,044，added_tokens 16,421）；模态先转符号序列再编码。DNA/RNA、蛋白 1D、SMILES/SELFIES 为 CPU；分子 3D 继续用 MolStructTok VQ-VAE（512 码本）；蛋白 3D 按用户 2026-11-13 决定改为 AtlasLM 连续 per-position 特征 + backbone z pair bias，不再把 GCP-VQVAE 作为新路径。
- 现状：`scinetics` 里只有 `data/tokenizer_compatibility.py`（追加保留 token 的校验），编码器在 `/nas/nas8/users/wzc/code/BioMatrix/`（`molstructok/`、`gcp_vqvae/`）。v0 文档自己写明：历史训练分片是否都用现有码本文件未逐一证明。
- 与任务书 B-20261113-03 相关：其预处理面板要按“编码器 + 统一 tokenizer”两层覆盖，本 map 的接口定下来后它按此测。

## Contract

- **Benchmark**: 固定样本集（01 票预先登记，覆盖每个模态）上，新模块对 v0 参考实现的 token id 逐样本比较，不一致数为 0。
- **Without asking**: 只读盘点、在 worktree 里写代码与 CPU 测试、经执行器跑编码器（单票 ≤5 GPU 小时）。改动 v0 权重、tokenizer.json、BioMatrix 目录；推送、合并、打 tag；改变既有词表或 token id 均先问用户。

## Decisions so far

- 2026-11-13 T17-01 claimed. Initial architecture uses encoder plugins emitting boundary-delimited symbols plus provenance, and a versioned tokenizer artifact with append-only reserved-token compatibility. New worktree is based on pinned `35f9646`; default text/BF16/FP8 path remains untouched.
- 2026-11-13 T17-05 resolved：tokenizer 版本盘点脚本与实际 JSON 数字已落票目录；现行 scinetics smoke 为 248044 base + 33 added，科学/v0/v1/历史族的 SHA 与兼容关系已列出。
- 2026-11-13 user decision：蛋白3D新路径采用 AtlasLM 连续特征；`<S n>` 及 IDs 260322–264417、已有 L3 shards、v0 GCP baseline 全部保留，词表变更先报用户。

## Not yet specified

- 新模块放 `scinetics` 的哪个包；分子 3D 和蛋白 3D 编码器的权重是否随仓库管理；tokenizer 版本号规则。

## Out of scope

- 重新训练模型；改变既有 token id；已有预计算数据的重新生成（先由 04 票判定哪些改动需要）。
