---
id: T17-01
title: 模态编码器插件接口、统一 tokenizer 产物与版本/兼容契约应当怎样设计，才能放进 scinetics 且不破坏现有预计算和 FP8/BF16 路径？
type: prototype
status: resolved (t17-codex-driver, 2026-11-13T08:00:00Z)
blocked_by: []
updated: 2026-11-13T07:46:00Z
---

## Question
先读 `models/v0/architecture.md` §4–4A、`scinetics/src/scinetics/data/tokenizer_compatibility.py`、`/nas/nas8/users/wzc/code/BioMatrix/`。在稳定提交 `35f9646` 之上开新 worktree，设计并落最小骨架：(a) 编码器插件接口（输入记录、输出带边界符号序列、声明 CPU/GPU 需求、记录自身代码与权重 SHA）；(b) tokenizer 产物（`tokenizer.json` SHA、词表大小、边界与保留 token 表）及兼容模式（追加保留 token / 新版本）；(c) 固定样本集清单（每模态至少 N 条，写明来源与 N）。验收：一页设计；接口骨架有 CPU 单测；默认路径不变。

## Log
- 2026-11-13T07:46:00Z (desk) 开票。

## Design / Answer (first pass)

新 worktree：`/nas/nas8/users/wzc/code/scinetics-worktrees/t17-multimodal-tokenizer-20261113`，起点 `35f9646fb5ca3fd95ca47e862b124bc940c97117`。骨架位于 `src/scinetics/data/multimodal_tokenizer.py`：`ModalityEncoder.encode(record) -> EncodedModality`，结果包含 modality、带边界的 symbols、CPU/GPU device、encoder version、代码 SHA 与可选权重 SHA；`EncoderRegistry` 负责按模态注册与调用，默认文本路径不变。

`tokenizer_artifact()` 生成 schema/version、`tokenizer.json` SHA-256、词表大小、边界 token ID、reserved token ID 和 compatibility mode。兼容模式沿用 `append_only_reserved_tokens`：只允许追加连续 special IDs；任何旧 token ID、旧 tokenizer pipeline 或模型维度变化都必须新版本。版本建议 `vMAJOR.MINOR.PATCH`：MAJOR 改语义/旧 ID 或码本；MINOR 只追加保留 token；PATCH 只修文档/manifest。

DNA/RNA、蛋白1D、SMILES/SELFIES 为 CPU 符号编码；MolStructTok 分子3D 为 512 码本；GCP-VQVAE 蛋白3D 为 4096 码本。3D 插件必须记录对应代码与权重 SHA，真实权重不随本骨架复制。

固定样本清单初版为每模态 8 条：text、dna、rna、protein_1d、smiles、selfies、mol_3d、protein_3d，共 64 条。每条保存 source URI/row ID、原始输入 SHA、规范化规则版本和参考 token IDs；CPU 模态先逐样本比对 v0，3D 模态待权重与许可确认后执行。

CPU 骨架单测 `tests/test_multimodal_tokenizer.py`：3/3 通过，覆盖注册、重复/未知模态拒绝、边界 metadata 与 append-only artifact identity；尚不宣称真实 v0 样本 parity。
