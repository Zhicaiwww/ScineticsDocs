---
id: null
title: 六模态共享桥到条目的轻量小样契约
assignee: null
reviewer: null
requester: wzc
status: draft
source: T24-01
created: 2026-11-13
due: null
access: ticket-only-write; source-read-only
---

# 任务书草案（未分配、未登记，不占正式 B 编号）

## 目标
- **场景**：内部研究短迭代；蛋白、DNA、RNA、分子/反应、细胞、材料的小样构造；桥只处理该条目所依赖的跨来源身份。
- **指标**：对照直接来源字段，所抽条目的字段回放不一致数=0、被渲染的保护内容数=0、不确定 join 被当确定答案数=0；报告实际成功/跳过/未知条数，不设全库完成率。本轮仅复核已有回执，不报告新条目产量。
- **完成标志**：运行本目录 verify_receipts.py 通过，并能按 bridge-contract.csv 为三条真实回执路径选择 route、标出未知项；研究结果不升级为生产准入。
- 为什么做：无关条目先构造，缺桥局部试点，不让全库 L2 或全面审查成为起步依赖。

## 背景与依据
### 已知结论
| 结论 | 数字与适用范围 | 出处 |
|---|---|---|
| L1 原字段足够即可直建 | 六模态均支持此路由；不代表已有六模态新小样 | layers.md；training-item.md |
| GO→UniProt 存在真实桥核查回执 | 200000 抽查行；198867 same_anchor、1133 isoform HOLD；不是新实验验证 | T9-10/results/bridge_check.json |
| RNA→transcript 链可核查 | 400/400 序列相同；16 个 hit pairs 被保护排除；不证明同一基因 | T9-17/results/verify_links_f.json |
| BindingDB 测量 facet 有回放回执 | 400 items/3667 lines/0 mismatches；不是所有 join 分支正确的证明 | T9-19/results/replay_released_n400_zeroledger.json |

缺口：本轮未读 L1 正文，未重跑桥；不知六轨最终 benchmark/scorer/version；不据此报模型收益或训练准入。

### 代码版本
- 仓库 `/nas/nas8/users/wzc/docs`，基线 commit `daceecd758b30975cf50b8d37e0541b1dca6b93a`；工作树已有改动，实际文件版本以 verification.json 的 SHA-256 为准。
- 校验脚本只用 Python 标准库；不执行旧 T9 全量脚本，不依赖第三方 worker 输出。

## 输入
| 路径 | 内容 | 权限/版本 |
|---|---|---|
| 本目录 report.md、bridge-contract.csv | 字段/路由/单位条件/隔离契约 | 本 ticket 可写；研究侧车 v1 |
| 上表三个 T9 results 原文件 | 真实回执 | 只读；哈希在 verification.json |
| data/v1/02-scientific-evidence/l2.md、03-tasks-samples/training-item.md | 现行 L2/facets 设计 | 只读；不改正式 schema |

## 交付物
| 文件 | 格式与内容 |
|---|---|
| report.md | 路由、最少字段、六模态策略、三路径、双清单 |
| bridge-contract.csv | contract_id/modality/capability/route/source_to_item/join_keys/minimum_fields/units_conditions/uncertain_policy/test_protection/evidence_path/evidence_scope/research_check/production_check |
| verify_receipts.py、verification.json | 轻量检查入口、实测结果/回执哈希/限制 |
| task.json | T24-01 身份、执行者、状态、来源与产物；未知原生会话 ID 留 null |

## 验收标准
- 本目录脚本退出码 0；CSV 覆盖六模态和三条回执路径；不把空组当回放成功。
- 直建不强迫桥；缺桥可局部 join；保留原值、比较符、单位和条件；ambiguous 不取首个候选为唯一真值。
- 测试保护沿本条依赖传播；来源拒绝照旧；未知只限制相关条目。正式生产清单独立，不作本轮前置。
- 通过例：RNA 回执 400/400 只标“相同规范化序列的候选”，16 个 held 不纳入训练。
- 反例：把 held 改成 train，或以 CID 单独命中宣称完整立体结构一致，或把 BindingDB 的 IC50 当 Kd。

## 不做与约束
- 不训练、全量构造/下载、写 L1/L2/冻结 L3、发布、commit/push、改 map.md/STATUS/共享脚本；不关闭 ticket。
- 生产或全量需 wzc 另行授权；不复查无变化的全库许可/安全事项，不绕过已有权限拒绝。

## 资源与权限
- 人类负责人未指定；不猜账号、reviewer 或 assigned 状态。正式任务书由协调者分配后另登记。
- 当前只可写本 ticket；现有资料只读。轻量 JSON/CSV 检查在当前主机，无 GPU、无集群任务；实际大批处理须另授权走 executor。

## 汇报
- 在本 ticket 汇报核实内容与未知范围，给文件路径；不主动通知其他人，不修改共享登记。

## 时间点
| 时间 | 里程碑 |
|---|---|
| 2026-11-13 | 草案与回执核查；具体执行期限待指定，不编造 due |

## 问题与决定记录
- 2026-11-13：按用户最新要求输出共享轻量契约，研究验证与生产验收拆开；task-brief 正式分配/REGISTER 操作不适用于本次目录受限草案，未运行 --register。
