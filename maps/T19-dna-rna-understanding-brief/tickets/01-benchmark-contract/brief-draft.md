---
id: null
title: DNA与RNA分轨的能力条目小样
assignee: null
reviewer: null
requester: wzc
status: draft
source: T19-01
created: 2026-11-13
due: null
access: ticket-only; source-read-only
---

## 目标
**场景**：DNA剪接/启动子识别与RNA家族/MRL分轨，先用本地训练来源完成小样，不训练模型。
**指标**：当前DNA 2条原生train标签样例、RNA 1条输入样例；来源字节/字段核验100%，重建一致100%，测试记录/答案读取0。没有已运行模型baseline。
**完成标志**：DNA标签语义和scorer钉扎；RNA从原生train取得至少一条真实目标值/标签；所有例可按源版本重放，局部测试隔离明确。
原因：序列理解应有可验证任务目标，不能用主题或来源header替代实验标签。

## 背景与依据
### 已知结论
|结论|数字与适用范围|出处|
|小样已真实构造|DNA2、RNA1；DNA标签原值存在但语义未核，RNA target=null|verification.json|
|NT版本已钉数据|revision 851f9946252e90c665cdb3cc3eedb78f1f26197c；只读acceptors train首2行|本地NT MANIFEST及重新计算hash|
|RNA有字段回源与有限隔离|411nt；既有157569保护hash原始/T→U/RC检查0命中|verification.json|
|promoter参考不可替换|GRCh38 release97；0-based半开区间，负链RC|T9-36 coordinate-contract.md|
|RNA benchmark有不同能力|ncRNA家族是分类，MRL是回归；RNAcentral rRNA描述不能当MRL|T14-08官方BEACON README缓存、T14-09 matrix|
### 代码版本
仓库：/nas/nas8/users/wzc/docs；未commit。本票build_examples.py；实际Python和脚本hash记录在task.json/verification.json。scorer commit未核实，不能以当前默认分支冒充冻结版。

## 输入
本票report.md、benchmark-contract.csv、examples.jsonl；已有NT train文件与manifest；T9 RNAcentral锚点和只含hash的保护清单。不得取用评测题答案补目标。

## 交付物
report.md、benchmark-contract.csv、examples.jsonl、verification.json、task.json、可重建脚本；字段含来源版本、原生split、原值、变换规则、目标证据及不确定项。

## 验收标准
- 通过例：native train原标签保真且官方0/1映射有证据；RNA原T与显示U可逆追溯；重放逐字节一致。
- 失败例：以RNAcentral header猜BEACON家族；用TPM当MRL；以release116替代promoter release97；把unknown split改train。
- 标注能力和输入表示；DNA与RNA统计分别给分母。当前RNA不能计监督样例，DNA语义验收仍未通过。

## 不做与约束
不训练、不全库扫描/下载，不改源库、冻结发布、map.md或ticket状态。先做局部目标隔离，不要求全库L2；仅跨源坐标/实体连接需要桥。许可未知不编造，只作内部研究，生产另验。

## 资源与权限
assignee和reviewer待指定，账户路径null；仅本ticket写，来源只读。现有scinetics-data Python，小型本地执行，不虚构executor任务。遇访问拒绝停下报告。

## 汇报
给真实样本数、目标标签可用数、路径、核验范围和未完成项；不把清单存在当无泄漏，不把构造成功当效果提升。

## 时间点
草案2026-11-13；分配/截止待指定，状态draft。

## 问题与决定记录
- 2026-11-13：快速构造已完成；NT标签语义、原生RNA监督和源码在线复核仍待补。
- 不写assignment/register；正式分配后再用task-brief checker，不能为通过checker虚构账户。
