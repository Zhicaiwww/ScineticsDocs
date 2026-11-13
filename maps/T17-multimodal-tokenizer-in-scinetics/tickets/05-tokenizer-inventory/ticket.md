---
id: T17-05
title: 当前最新、完备的 tokenizer 信息是什么：有哪些版本的词表、哪个是现行、各自的 SHA、边界标记、保留 token 与词表行数？
type: research
status: resolved (t17-codex-driver, 2026-11-13T07:58:00Z)
blocked_by: []
updated: 2026-11-13T07:48:32Z
---

## Question
用户（2026-11-13）：tokenizer 的信息要最新且完备。盘点所有在用和历史的 tokenizer 产物：Qwen3.5 原生（248,320 行）、v0 的 264,465 行科学词表、v1 初始化、`reserved-vocab-v7`、`20261017T_node16-qwen35-2b-v2/init-from-base`、yjx 目录下的 `sft-gue-beacon-continuation-v2` 等。每个给出路径、SHA-256、基础 BPE 条目数、added_tokens 数、总 id 范围、与 embedding 行数的关系、边界标记与 id、保留 token、对齐回执；标出哪个是现行并给证据；各版本之间 id 是否兼容（追加关系或不兼容）。

## Acceptance
- 一张版本表加兼容关系图（文字即可），数字来自读取实际 `tokenizer.json`（脚本放票内目录，重跑得到同样数字），不是转述文档。
- 校正 `models/v0/architecture.md` §4 的 `pretokenize_regex` 与 `tokenizer.json` 正则是否一致（v0 文档说未核验）：实例化 tokenizer，对固定样本编码比较。
- 写成 `reference/tokenizer-inventory.md`（本 map 下）；与 `models/init/README.md`、`models/v1/` 页面不一致处列出，由 desk 去改页面。
- 不修改任何 tokenizer 文件。

## Log
- 2026-11-13T07:48:32Z (desk) 开票。

## Answer

脚本化盘点已完成，脚本、路径清单和原始 JSON 数字均在本票目录；汇总见 `reference/tokenizer-inventory.md`。当前 scinetics smoke 现行产物为 SHA `06b950...e523`、248044 base + 33 added、ID capacity 248077。科学 264k、v0、v1、Qwen base 与 yjx 历史族均列出 SHA、added ID 范围及兼容边界；未修改任何 tokenizer 文件。v0 `pretokenize_regex` 实例化对照因参考 tokenizer 文件不在当前可读路径，保留为待补证，不以文档转述代替。
