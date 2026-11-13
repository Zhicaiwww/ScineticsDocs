---
id: T22-01-brief-draft
title: 材料组成与结构到性质的fold约束小样
assignee: null
reviewer: null
requester: wzc
status: draft
source: T22-01
created: 2026-11-13
due: null
access: ticket-only-write; L1-read-only
---
# 材料条目草案（非正式assigned任务）
## 目标
**场景**：Matbench v0.1的steels/expt_gap/dielectric，既有L1到本ticket，固定fold_0的9条研究小样。
**指标**：9/9源输入/标签相等；test ID及三个任务联合测试组成命中0；未来模型用原单位MAE，当前不虚报模型成绩。
**完成标志**：9条同时带结构或组成、性质、单位、条件缺失状态、L1定位及fold_0 train_val身份；不生成all-fold-train。
为何做：保持实验性质、计算性质、组成和晶体结构的边界，形成可复用的性质理解条目。
## 背景与依据
### 已知结论
| 结论 | 数字与适用范围 | 出处 |
|---|---|---|
| 真实小样 | 三端点各3，共9；全部fold_0 train_val | verification.json |
| 原生回读 | 输入与target相等9/9；三个任务1872个测试组成键联合排除 | verification.json |
| 官方fold_0 | steels249/63、expt_gap3683/921、dielectric3811/953（train_val/test） | 本地固定官方protocol |
| 性质与单位 | yield strength MPa；gap expt eV；n为无量纲折射率 | 官方metadata；T14 matminer快照 |
| 未覆盖 | 其他fold、其他10任务与跨库晶体等价不在此次保证内 | report.md |
### 代码版本
本ticket `build_examples.py`；既有scinetics-data Python/pyarrow，未改生产代码。协议SHA在verification.json；官方源blob在source-retrieval.json。
## 输入
benchmark-contract.csv；9条examples.jsonl；verification.json。L1根路径`/nas/nas6/users/wzc/datasets/<task>/l1/20261112-t14/`；原native JSON和fold protocol准确路径逐条记录。
## 交付物
report.md、benchmark-contract.csv、brief-draft.md、task.json、examples.jsonl、verification.json及构造脚本；下一轮只补这9条所需条件或局部连接，不发起全库构造。
## 验收标准
- 运行`python build_examples.py`，输出9条，三个端点各3，source_index→mbid→fold可重放；单独回读选定L1字段/原生JSON逐项相等。
- 通过例：fold_0 train_val中的材料，完整保存原组成或lattice/sites，target/unit保真，未知温压为null，联合test组成排除通过。
- 失败例：把fold_1 train样本加入fold_0而不查test；把五折train并集声明统一训练；将n说成介电常数；凭相同化学式断言同结构；擅填298K。拒绝该条，不要求全库审批。
- 来源内直接L1；跨库仅用可信源ID/结构等价证据+性质/条件连接，不把归一组成键当same_as。冲突值并列且留原条件，holdout沿连接传播。

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
