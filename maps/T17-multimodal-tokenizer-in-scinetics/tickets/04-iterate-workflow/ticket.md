---
id: T17-04
title: 迭代 tokenizer 时，改什么会使已有预计算数据失效，一次迭代的流程与验收是什么？
type: research
status: open
blocked_by: [T17-01]
updated: 2026-11-13T07:46:00Z
---

## Question
基于 01 的契约，写出迭代流程：追加保留 token 与新增模态与改 BPE 合并规则分别的影响；哪些改动要求重新预计算、哪些不用（给判据与例子）；每次迭代的验收清单（参考样本 token id 比对、对齐回执、边界标记表、模型词表行数）；与 `tokenizer_compatibility.py` 的关系。验收：一页流程加一个演练（追加 1 个假保留 token，走完验收，不落盘到正式目录）。

## Log
- 2026-11-13T07:46:00Z (desk) 开票。
