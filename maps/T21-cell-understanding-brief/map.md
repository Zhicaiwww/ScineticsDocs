---
id: T21
title: 细胞与组学：benchmark反推训练条目任务书
status: claimed (data desk docs-60, 2026-11-13T09:30:00Z)
outcome:
updated: 2026-11-13T08:32:25.116240+00:00
---

## Destination
从现有参考文献的可核验benchmark定义科学理解能力，反推多源训练条目、跨源桥依赖、泄漏边界与验收标准，交付独立任务书草案；不宣称已提升benchmark。

## Notes
- [benchmark与条目契约研究](tickets/01-benchmark-contract/ticket.md)。
- 复用T14文献、T9条目和L1库存；不修改其产物。
- 人类执行负责人未指定，不借用why/xux身份或伪造assigned状态。

## Contract
- 快速迭代：每轨先核2–3个benchmark，立即形成方案并从已有训练来源构造小样；不等待全面综述、全库L2或全库审查。
- 研究小样与生产准入分开；小样仅保留来源追溯、测试隔离和基本字段/连接正确性检查，未知项标注不阻塞其他条目。
- 顺序：benchmark原始协议 → 科学任务输入/输出 → 所需证据 → L1/L2整合 → L3条目 → 验收。
- 可做：论文与官方代码只读调研、元数据盘点、此map独立ticket内文档与小型校验。
- 不可做：训练、全量构造/下载、修改L1/L2/冻结L3、发布切换、commit/push。
- 基准必须记录版本、split、metric、scorer、输入模态、监督/零样本设置及未核项。
- 测试题/答案/rubric及其改写不得构造训练样本；跨源连接传播holdout隔离；训练来源须独立授权。

## Decisions so far
- 2026-11-13T08:52:54.526156+00:00 首轮[任务书草案](tickets/01-benchmark-contract/brief-draft.md)与[报告](tickets/01-benchmark-contract/report.md)已交付；实际JSONL 3行，非生产准入或benchmark提升，具体缺口见报告。
- 2026-11-13T08:32:25.116240+00:00 用户要求独立模态map，先benchmark与科学理解定义，再反推训练条目。

## Fog
- 目标benchmark协议与本地数据可用性待逐项核对。
- L2桥只对有实际跨源身份/关系依赖的条目要求，不强制所有L1先过L2。

## Out of scope
- 已有打标任务、L4配比、实际训练和发布。
