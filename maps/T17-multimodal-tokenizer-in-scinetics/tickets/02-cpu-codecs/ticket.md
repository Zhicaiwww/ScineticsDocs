---
id: T17-02
title: DNA/RNA、蛋白 1D、SMILES、SELFIES 的编码在新模块里实现后，对 v0 参考实现的 token id 不一致数是多少？
type: experiment
status: open
blocked_by: [T17-01]
updated: 2026-11-13T07:46:00Z
---

## Question
按 01 的接口实现四类 CPU 编码器，在固定样本集上与 v0 参考实现（BioMatrix 与当前统一 tokenizer.json）逐样本比较 token id。验收：每类的样本数、不一致数（目标 0）、吞吐（tokens/s/核，计时样本 n 与重复数）；不一致的逐条列出原因。

## Log
- 2026-11-13T07:46:00Z (desk) 开票。
