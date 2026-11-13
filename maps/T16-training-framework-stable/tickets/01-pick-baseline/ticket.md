---
id: T16-01
title: 稳定对象是哪个提交，本地 main、origin/main 与各分支的差别是什么？
type: research
status: open
blocked_by: []
updated: 2026-11-13T07:00:13Z
---

## Question
列出 origin/main `35f9646` 与本地 main、`feat/tool-sft-runtime-20261028`、`codex/cpt-stable-08b-2b-20261027` 的提交与文件差异，确认 `35f9646` 含 PR #3 与 #4 的全部内容，写明每个分支为什么纳入或不纳入。

## Acceptance
- 一张表：分支 | 相对 origin/main 的提交数 | 内容一句话 | 纳入/不纳入与理由。
- 稳定提交的哈希由 `git rev-parse` 给出，不凭记忆。

## Log
- 2026-11-13T07:00:13Z (desk) 开票。
