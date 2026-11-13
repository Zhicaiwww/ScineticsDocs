---
id: T16-01
title: 稳定对象是哪个提交，本地 main、origin/main 与各分支的差别是什么？
type: research
status: resolved (t16-codex-driver, 2026-11-13T08:05:00Z)
blocked_by: []
updated: 2026-11-13T08:00:00Z
---

## Question
列出 origin/main `35f9646` 与本地 main、`feat/tool-sft-runtime-20261028`、`codex/cpt-stable-08b-2b-20261027` 的提交与文件差异，确认 `35f9646` 含 PR #3 与 #4 的全部内容，写明每个分支为什么纳入或不纳入。

## Acceptance
- 一张表：分支 | 相对 origin/main 的提交数 | 内容一句话 | 纳入/不纳入与理由。
- 稳定提交的哈希由 `git rev-parse` 给出，不凭记忆。

## Log
- 2026-11-13T07:00:13Z (desk) 开票。

## Answer

Stable commit is `35f9646fb5ca3fd95ca47e862b124bc940c97117`, verified with `git rev-parse origin/main`. The detached validation worktree is `/nas/nas8/users/wzc/code/scinetics-worktrees/t16-stable-35f9646` and is clean.

| branch | relative to origin/main | content | decision |
|---|---:|---|---|
| `main` | 4 commits behind | local branch stops before the current merged PR #4 state | exclude; stale |
| `feat/tool-sft-runtime-20261028` | 2 commits ahead | tool-call SFT and scientific-search runtime additions | exclude; outside the CPT stable target |
| `codex/cpt-stable-08b-2b-20261027` | 1 commit behind | PR #3 Qwen3.5 FP8 work plus PR #4 continuation/reshard/stability work | exclude as a branch; its merged contents are in `origin/main` |
| `origin/main` | baseline | merge commit for PR #4, with PR #3 in its history | include; pinned stable target |

`git show origin/main` identifies the PR #4 merge and the changed continuation, `reshard_zero1`, and `stability_eval` files. The validation worktree was created without changing local `main` or any existing worktree.
