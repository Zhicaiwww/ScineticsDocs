---
id: T20-01-brief-draft
title: 小分子性质与反应产率分轨构造
assignee: null
reviewer: null
requester: wzc
status: draft
source: T20-01
created: 2026-11-13
due: null
access: ticket-only-write; L1-read-only
---
# 小分子与反应条目草案（非正式assigned任务）
## 目标
**场景**：既有L1到独立ticket小样；SMolInstruct ESOL/Lipo与ChemLLMBench两类HTE分轨。
**指标**：字段回读一致率100%、指定test实体/scaffold命中0；模型比较口径分别为RMSE和分类accuracy，本轮不设或虚报效果提升。
**完成标志**：交6条可追溯性质候选和两端点反应契约；下一轮只有官方train身份确认的记录才晋级训练候选，反应每端点先3条。
为何做：分子性质理解与反应条件理解需要不同输入证据，不能用主题标签或生成流畅度替代。
## 背景与依据
### 已知结论
| 结论 | 数字与适用范围 | 出处 |
|---|---|---|
| 小分子真实小样 | ESOL3、Lipo3；保护test112/420；不代表官方train | verification.json |
| 本地可回源范围 | 当前L1可读；原nas1 CSV不存在；独立原CSV parity=0 | verification.json、report.md |
| 官方性质协议 | scaffold；RMSE仅解析成功回答，必须同时报失败计数 | LlaSMol论文v2；LLM4Chem metrics.py |
| 反应协议 | 高产率二分类；validation30/test100；原阈值未知 | ChemLLMBench论文v3 Appendix C |
| 反应小样 | 0；HTE训练身份与条件尚缺，不以USPTO无产率替代 | report.md |
### 代码版本
项目`/nas/nas8/users/wzc/code/scinetics-data`未改；本ticket `build_examples.py`为唯一小样入口。依赖版本和输出SHA见verification.json；官方代码snapshot/blob见source-retrieval.json；不把未冻结HEAD当版本证据。
## 输入
`benchmark-contract.csv`、`examples.jsonl`、`verification.json`；L1 source-42887feb0c12两个unit准确路径已逐条写入provenance。T14 matrix C1/C3是目标依据。
## 交付物
本轮：report.md、benchmark-contract.csv、brief-draft.md、task.json、examples.jsonl、verification.json和构造脚本。
下一轮：给6条记录补official train/validation membership；仅在有可读HTE train与固定test IDs时追加真实反应小样，每条保存角色、条件、yield原值/单位、来源ID与划分。
## 验收标准
- 运行`python build_examples.py`：目前6条，SMILES/实测性质/单位/provenance齐全；不选择ESOL predicted列。
- 通过例：某L1实测性质行不命中两核心test实体或scaffold，split诚实标为research candidate，可通过小样验收但不是训练准入。
- 失败例：把test答案改写成解释；把“非test”写成“官方train”；缺失反应yield填0；按名字合并CID/ChEMBL；任一项即拒绝该条，不阻塞其他独立条目。
- 跨源合并才使用局部L2，记录ID桥、parent/stereo、endpoint、条件及冲突；holdout沿桥传播。无跨源join不得宣称多源融合已完成。

## 不做与约束
不训练、不全量构建、不发布、不commit；不改map.md或共享脚本，不覆盖L1/L2/冻结L3。测试题/标签及改写禁止成为训练输出；不新增全库审批关卡。
## 资源与权限
执行者待指定，assignee=null；本轮只有本ticket内小样写权限，所有来源只读。使用既有`/nas/nas8/users/wzc/envs/scinetics-data/bin/python`，不安装依赖，不承诺新权限。
## 汇报
报告实际样本数、来源回读、测试隔离范围、未知和阻塞；不把agent完成等同实验成功，不把research sample等同training-ready。
## 时间点
本轮已形成草案和本地小样；下一轮按下述最小增量推进，负责人/截止时间待用户指定，不虚构承诺。
## 问题与决定记录
2026-11-13：采用用户快速迭代要求，仅追溯、固定测试隔离、独立输出和显式未知；ticket保持open。正式任务书待负责人指定后由协调者移入assignment并运行register，本轮不运行会写外部目录的登记器。
