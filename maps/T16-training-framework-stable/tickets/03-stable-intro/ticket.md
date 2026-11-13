---
id: T16-03
title: 稳定版本的介绍页写什么，范围与缺口是否如实？
type: task
status: resolved (t16-codex-driver, 2026-11-13T07:30:00Z)
blocked_by: [T16-02]
updated: 2026-11-13T07:00:13Z
---

## Question
写 `intro.md`：稳定提交哈希、能力（模型、FP8、packing、续训、导出）、配置入口、已验证范围（引用 T16-02 的数字）、未覆盖范围。

## Acceptance
- 每个数字带运行或文件出处；未重跑的项标明“沿用旧记录”。
- 没有 4B 与多节点的结论性语句。

## Log
- 2026-11-13T07:00:13Z (desk) 开票；初稿见 intro.md（基于旧记录，T16-02 之前不算稳定）。

## Answer

`intro.md` 已更新，区分本次 T16-02 短测与沿用旧记录，并明确 4B、多节点和未重跑门槛不作结论；FP8 覆盖证据引用 `run/fp8-coverage.json`。
