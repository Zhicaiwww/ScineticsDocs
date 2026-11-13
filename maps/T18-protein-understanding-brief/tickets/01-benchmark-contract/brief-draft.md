---
id: null
title: 蛋白序列与结构输入的功能理解条目小样
assignee: null
reviewer: null
requester: wzc
status: draft
source: T18-01
created: 2026-11-13
due: null
access: ticket-only; source-read-only
---

## 目标
**场景**：独立研究目录，复用T9真实来源；蛋白序列/结构两轨，构造可回源条目，不训练。
**指标**：当前2条输入冒烟/1实体、功能监督0条；验收以来源字段一致率100%、重建字节一致率100%、测试答案读取0为准，无模型效果基线或提升承诺。
**完成标志**：EC/GO或定位官方train标签与至少一条真实序列配对，结构轨缺失明确；版本/scorer/局部隔离字段齐且重放通过。
原因：先证明数据能支撑功能能力，而非积累“蛋白”主题文本。

## 背景与依据
### 已知结论
|结论|数字与适用范围|出处|
|当前只验证输入格式|序列1、结构1，均target=null；不是功能监督|verification.json / examples.jsonl|
|数据协议不能混排|EC 13089/1465/1604；GO 26224/2904/3350，为SaProt过滤子集，不是原DeepFRI全量|T14-08 03-protein.csv|
|Fmax实现需重新钉扎|官方issue在2024-04-18记录flatten形状修正；本票未执行scorer|官方SaProt issue23搜索返回|
|结构输入不是结构预测目标|当前仅2个CA点，不能当完整结构或3Di|examples.jsonl|
### 代码版本
仓库：/nas/nas8/users/wzc/docs；本轮未commit。复现脚本：相邻T19票的build_examples.py；实际Python/脚本hash见task.json与verification.json。SaProt scorer commit未核实。

## 输入
本票report.md、benchmark-contract.csv、examples.jsonl；T9已保存结构样例；T14原始文献抽取。后续取数只用官方train或已核非测试来源，不开放test答案。

## 交付物
benchmark-contract.csv（能力、输入、输出、metric/split/scorer/version/evidence）；examples.jsonl（输入、目标、来源、字段定位、hash、split、配方）；verification.json；report.md；task.json。

## 验收标准
- 通过：真实train序列与同版EC标签按明确身份连接；input不含答案；实际运行重建hash一致。
- 反例：把PDB标题中的EC抄作序列分类答案；把缺坐标标完整结构；把未知split写train。
- 任一未核项保留null或UNVERIFIED。输入冒烟和功能监督分别计数，不能以当前2条报“功能数据完成”。

## 不做与约束
不训练、不全量下载/扫描、不改map.md、L1/L2或冻结发布，不关闭ticket。研究小样不等待全库L2；实际跨源结构-序列连接才补局部桥。生产准入单列。

## 资源与权限
人类负责人待指定，账户路径null；reviewer待指定。仅允许本ticket写入，来源只读；现有Python做小型读取。超出小型读取才走executor并登记真实run-id。

## 汇报
报告路径、真实实体/序列/结构/监督条数、未核项与实际运行证据；禁止以agent完成自述替代验证。

## 时间点
草案2026-11-13；分配和deadline均待requester指定，不伪造assigned。

## 问题与决定记录
- 2026-11-13：原文网络获取部分阻塞；保留当前可复现输入小样，功能监督未完成。
- 本草案位于ticket，不写assignment/tasks或REGISTER；未运行会改注册表的--register。正式分配后按task-brief checker检查。
