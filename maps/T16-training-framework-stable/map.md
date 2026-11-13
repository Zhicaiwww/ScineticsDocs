---
id: T16
title: 稳定最新的训练框架并给出稳定版本介绍
status: open
outcome:
updated: 2026-11-13T07:00:13Z
---

## Destination

训练仓库（`/nas/nas8/users/wzc/code/scinetics`）有一个被钉住的稳定提交：在该提交上，门槛检查（CPU 测试、0.8B 与 2B 的 BF16/FP8 短测、恢复、原生导出）重新跑过并有记录；`tickets/03-stable-intro/intro.md` 介绍这个稳定版本的能力、配置入口、已验证范围和未覆盖范围。

## Notes

- 用户（2026-11-13）：“请你启动一个 map 来稳定我们目前最新的训练框架,并给出框架稳定版本的介绍,然后形成 commit。”
- 起点（已读 git）：本地 main `2942155` 落后 origin/main 4 个提交；origin/main 是 `35f9646`（PR #4 合入 `d377bdd`：Qwen3.5 CPT 续训、ZeRO-1 重分片、稳定性评测）。另有 `feat/tool-sft-runtime-20261028`（领先 origin/main 2 个提交，工具调用 SFT），以及 .worktrees 下几条旧分支。
- 已有记录里的验证（来自 CHANGELOG 与 experiments，未在本 map 内重跑）：0.8B 四卡 BF16/FP8 各 10 步、66 区域、step2→10 恢复、473 张量原生导出；96 项 CPU 测试（94 通过 2 跳过）。
- 已知缺口：没有 4B 实测；没有 H100 多节点实测（与任务书 B-20261113-03 相关）；PR #4 之后的门槛检查没有记录。

## Contract

- **Benchmark**: 门槛检查清单（ticket 02 预先登记），在固定提交上跑，BF16 对 FP8 沿用 NLL 相对差 ≤0.5%。
- **Without asking**: 只读盘点、在 worktree 里跑 CPU 测试、经执行器跑短测（单票 ≤5 GPU 小时）。推送、打 tag、合并分支、改训练仓库默认分支均先问用户。

## Decisions so far

- 2026-11-13 desk：稳定对象选 origin/main `35f9646`（含 PR #3、#4），不含工具调用 SFT 分支；理由：前者有验收记录，后者未验收。可由用户改。

## Not yet specified

- 稳定版本的命名与是否打 tag；是否把 `feat/tool-sft-runtime` 纳入；4B 和多节点是否算稳定范围（暂不算）。

## Out of scope

- 4B 与多节点效率优化（见任务书 B-20261113-03）；数据构造；科学评测。
