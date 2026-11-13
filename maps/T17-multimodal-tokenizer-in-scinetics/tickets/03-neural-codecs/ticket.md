---
id: T17-03
title: 分子 3D（MolStructTok）与蛋白 3D（AtlasLM 连续特征）怎样作为插件接入，身份与迁移边界怎样固定？
type: prototype
status: open
blocked_by: [T17-01]
updated: 2026-11-13T07:46:00Z
---

## Question
按 01 的接口规划两个神经通道：分子 3D 继续使用 MolStructTok VQ-VAE；蛋白 3D 不再迁移 GCP-VQVAE `<S 0>...<S 4095>` 离散 token，而改用 AtlasLM 连续特征。AtlasLM 的逐位置特征进入输入 rows；backbone `z` pair 特征投影为 bias，只加到 full-attention 层 logits，linear-attention 层不加。只出方案与影响清单，不改 tokenizer、不删 GCP 资产或已有 shards。

## Design / impact plan (2026-11-13 user decision)

### Unchanged channels

- 分子 3D：MolStructTok VQ-VAE（512 codebook）保持原方案；继续记录代码/权重 SHA、原子顺序与有效原子映射。
- DNA、RNA、蛋白 1D、SMILES/SELFIES：CPU 符号编码与统一 tokenizer 路径不变。

### Replacement channel

- 蛋白 3D 输入不序列化为 `<S n>` 离散 token。AtlasLM 逐链运行，输出连续 per-position features；经过冻结/可审计的 feature projector 后注入 scinetics input rows。
- 复合物/链间 3D 信息使用 backbone `z` pair features，经 pair projector 生成 attention-logit bias；只在底座 full-attention layers 生效，linear-attention layers 不接 bias。该路径服务科学模态理解，不是结构预测输出头。
- 编码记录必须携带 AtlasLM 代码版本、权重 SHA、配置、链/残基映射、特征维度、dtype、归一化与 projector 版本；GCP 权重不再是新路径的运行依赖。

### Replacement impact checklist (no mutation performed)

1. **Tokenizer rows `<S n>` / IDs 260322–264417 (4096 rows):** mark as deprecated for the new protein-3D route, but do not delete, renumber, or rewrite them. Any future tokenizer release must choose explicitly between (a) retaining them for legacy compatibility, or (b) a new major tokenizer version with an alignment/migration receipt. User decision required before any vocabulary edit.
2. **Existing L3 shards containing `<S n>`:** remain readable legacy artifacts and must not be rewritten or deleted. Add a manifest distinction (`protein_3d_codec=gcp_vqvae_discrete` vs `atlaslm_continuous`) when new preprocessing is designed; do not silently reinterpret old IDs as AtlasLM features.
3. **v0 comparison baseline:** preserve the GCP-VQVAE tokenized baseline as a historical/reference line. It is no longer the target implementation for new protein-3D understanding, and its parity numbers must not be used to claim AtlasLM parity. A future comparison should be an explicitly named dual-path study (legacy GCP tokens vs AtlasLM continuous features).
4. **Model/training interface:** use the existing default-off encoder feature seam from T16-04; zero-init projectors preserve the base path. Pair bias is restricted to full-attention layers and cannot be routed through linear-attention kernels.
5. **Precomputed data and contracts:** old tokenizer SHA, vocabulary size, and `<S n>` IDs remain pinned for old shards. New AtlasLM-feature datasets require a new feature-manifest version and cannot reuse old token-ID parity receipts.

No GCP files, checkpoints, tokenizer rows, or shards were removed or modified in this ticket.

## Log
- 2026-11-13T07:46:00Z (desk) 开票。
- 2026-11-13 user decision：蛋白3D由 GCP-VQVAE 离散 token 改为 AtlasLM 连续特征（含 backbone z pair bias）；本票只记录方案与影响清单。
