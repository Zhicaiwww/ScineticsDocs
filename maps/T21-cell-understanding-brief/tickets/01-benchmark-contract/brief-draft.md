---
id: T21-01-brief-draft
title: 将细胞表达谱和研究摘要分开，补一个合法训练研究的原生表达格式小样
assignee: null
reviewer: null
requester: wzc
status: draft
source: T21-01
created: 2026-11-13
due: null
access: 仅指定ticket写；既有数据只读；内部非商业研究
---

## 目标
**场景**：独立研究小样；不接生产L1/L2/L4、不训练、不等待全库整理。将细胞表达谱和研究摘要分开，补一个合法训练研究的原生表达格式小样。
**指标**：样本数逐类精确计数；来源、原split、hash和字段校验零失败；原benchmark指标单列，基线为未经融合的原生来源条目。本票不报告模型性能或容忍度。
**完成标志**：交付3–10个cell-profile-label样本；数据不可达则明确0条和来源阻塞，保留现有3个study_summary，不造表达值，并以可运行检查与明确阻塞记录证明结果。
原因：先验证科学对象和证据能否正确输入任务，再扩大构造，避免把覆盖量当能力。

## 背景与依据
### 已知结论
|结论|数字与适用范围|出处|
|---|---|---|
|当前证据|已核2个原始端点；3个真实研究摘要、0个表达谱；hPancreas/CINEMA精确候选目录无H5AD。摘要不能替代细胞向量。|report.md；verification.json|
|协议边界|2个核心端点仅协议核对，模型评分0次；词面/分类/工作流指标不混排|benchmark-contract.csv|
|权限边界|不覆写L1/L2/冻结发布；只改本ticket；未分配人类执行者|用户指令；scope.md|
### 代码版本
构造脚本：maps/T23-crossmodal-understanding-brief/tickets/01-benchmark-contract/build_samples.py；实际解释器 /nas/nas8/users/wzc/envs/scinetics-data/bin/python。当前为未提交ticket脚本；不伪造Git commit。原scorer版本尚未全部固定，因此不开展benchmark结果比较。

## 输入
只需本目录 report.md、benchmark-contract.csv、examples.jsonl、verification.json；内含实际来源路径与限制。先选一个来源/实验，禁止扫描全库。跨源配方、连接键、单位、冲突与局部L2要求已在report展开。

## 交付物
examples.jsonl：科学输入/输出、source_id/record、版本/hash、许可、原split、父对象/暴露组、证据、缺失原因。verification.json：真实样本数、检查、失败及未执行范围。report.md记录方案与一轮结果；task.json保持真实执行身份与状态。

## 验收标准
- study+donor+cell+gene axis与完整向量绑定，训练来源且测试组隔离；研究摘要明确标study层。
- 每条校验必需字段、内容hash与原split；至少一个失败样例必须被拒绝。对无数据的能力如实报0，不以摘要或引用数补足。
- 通过例：study+donor+cell+gene axis与完整向量绑定，训练来源且测试组隔离；研究摘要明确标study层。
- 反例：top-20 study genes充当单细胞谱、batch充当donor、把疾病标签当干预或随机拆同donor。
- 不要求全库L2/准入审查通过，不重复全面review；只检查此样本范围的来源与测试隔离。

## 不做与约束
不训练、不批量下载、不越权限、不生成测试题改写；DDB仅评测，不读取/复制其题目答案rubric构造小样。不关闭ticket/map。新增下载/集群任务另需授权及资源流程。所有结论区分观测与推断，未知不补造。

## 资源与权限
assignee未指定，无账户路径可登记，不授予或假设新权限。仅本ticket写入；另一个ticket脚本的维护由协调者安排。既有来源只读；轻量点读可本机，重活须走executor。

## 汇报
仅向wzc/本任务协调者返回新增样本数、通过检查、阻塞、文件路径；不宣称科学能力提升。

## 时间点
开始：负责人指定且选定样本来源后。截止：未指定。先一轮小样反馈再决定扩展；不编造工时。

## 问题与决定记录
- 2026-11-13：保持draft；未指定assignee/reviewer，不注册assigned。因写范围仅ticket，未运行会改assignment REGISTER的注册器；正式任务书待协调者指定负责人后迁移并检查。
