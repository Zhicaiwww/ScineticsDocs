# 跨模态：先做分子—文本真配对，工作流评测独立

## 结果
- 从 T14 X1/X4 回到 **2 个核心 benchmark**：ChEBI-20/MolT5 captioning、DrugDiscoveryBench（DDB）。前者考查分子输入到描述；后者是多步证据工作流评测，不自动等于模态理解。`benchmark-contract.csv` 保留原输入、输出、指标、split、scorer 与未知项。
- 已构造 **3 条真实 SMILES→原描述小样**，全部来自既有 ChEBI-20 官方 train，并按 `item_id + content_sha256` 连接 T9-26 **review3** 的 `ADMIT_SCOPED_TRAIN`；实际读取该范围 6,407 个准入侧表条目，未消费旧 HOLD 判断。3/3 正文 hash 与图解析通过，误用 test 的负控制被拒绝。不是全库准入，也不是模型能力成绩。
- DDB **题目、答案、rubric 读取数为 0，训练小样数为 0**。仅读取公共仓库 README 的接口说明；未 clone repo、未进入 tasks、未访问 gated 内容、未运行评测。

## 反查原始协议：不要沿用不透明聚合
- MolT5 使用 SMILES 输入生成自然语言描述；原 captioning 指标为 BLEU-2/4、ROUGE-1/2/L、METEOR、Text2Mol。原论文表 1 的 MolT5-Large BLEU-4 为 0.508，不能改称事实正确率；反向 text→molecule generation 是另一任务，本票不以其结构生成作为目标。[1]
- **版本差异明确保留：** MolT5 论文 v3 写 33,010 对、80/10/10%；本地 T9/T14 已处理 release 是 33,008（train 26,407、validation/test 共 6,601）。本次仅点读训练小样及侧表，不重新计数所有 split，更不补造两条“修复”论文差异。[1] 本地数字依据 `maps/T9-item-card/tickets/26-t14-leakage-admission/report.md`，不是本轮全量测量。
- MoleculeQA 原仓库说明每题一个正确项和三个负项，围绕分子描述事实；可作为后续事实诊断的参考，不能据此认定 ChEBI 的词面分就是事实能力。本轮未核其完整 scorer/split，故不增列第三个“已核”核心端点。[3]
- DDB README 明确 **82 个 Harbor 任务**、LLM judge、逐 criterion grades、reward 0–100；reference answers/rubrics 放 gated HF。README 当前指定 Harbor 0.13.1、镜像 1.0.2-lightweight。本轮只钉 README 内容 hash，不把浮动 main 当冻结 benchmark release；T14 的 outcome/process 细分仍需以后在授权评测会话确认具体 scorer 聚合，本票没有读 rubric 来补表。[2]

## 两条轨道，不能互相冒充
|轨道|能力与输入|最小对照 / 指标解释|
|---|---|---|
|真实跨模态理解|SMILES 图、蛋白序列或真实实验向量 + 文本任务→可追溯功能/证据描述|必须保留对象载荷；新增诊断可做遮蔽/打乱模态对照，分别报告，不替换原 BLEU 等指标；只有分子名字或纯文本 QA 不算本轨|
|证据约束科学推理|给定公开独立科学记录、工具可见结果及问题→结论+证据+限制|DDB 仅作外部评测目标；训练配方必须来自独立来源，不使用 DDB prompt、答案、rubric、canary或改写。当前 3 个配对样本没有多步轨迹，不冒称已建工作流训练集|

T14 X2 的 PubMedQA、X3 的 SciQ 可讨论文本证据推理，但不能充作模态输入，也不在本轮拿来凑跨模态样本。DDB 总分不可与 caption BLEU 或选择题 accuracy 混排。[1][2]

## 多来源条目与必要 L2（设计，不是假称已融合）
|配方|科学内容与来源|连接键 / 条件 / 冲突|L2 是否必须|
|---|---|---|---|
|molecule-text-native（已做3条）|ChEBI-20 同记录 SMILES→description，保留原字段|来源 record_id+CID+body hash；来源配对原样继承；不把 CID 相同即当性质一致|不需要新 L2；原生配对可直接构造独立条目|
|molecule-assay-evidence|非测试 PubChem/ChEBI 结构 + ChEMBL/BindingDB 实验条件→活性证据摘要|canonical structure+stereo+salt policy + assay/target + units；IC50/Ki 不互换；不同条件并列，冲突不平均；未测不写0|实体合并、target映射、单位换算时需要局部 L2；保存原值与规则证据|
|sequence-function-evidence|非测试 UniProt 序列 + GO/InterPro 证据→功能解释|accession+sequence hash+annotation version+evidence code；同名蛋白不等同；同源/实体测试组隔离|只为跨源身份/证据连接建桥；不先建全库|
|independent-analysis-trace|独立合法测量记录→预先定义的筛选/比较/结论+工具轨迹|记录每次查询输入、实际输出、hash和失败；问题由该训练源与能力目标制定，不参考DDB题目/rubric|只对确需解释的实体/单位建立局部桥；未做真实工具调用就不能写成功轨迹|

这些配方只说明如何服务理解目标，不以统一模板代替对象/条件。科学结论只来自引用字段或可重算操作；未知/冲突必须呈现，不生成未经验证的机制答案。

## 本次实际构造与隔离
`examples.jsonl` 的 input 是真实分子 SMILES，output 是原始描述；没有从描述反推并伪造结构。额外 `derived_check.heavy_atom_count` 由 RDKit 实际计算，只是图解析诊断，不是新生物学标签。
准入来源：`/nas/nas6/users/wzc/datasets/training-items-v1/t9-26-leakage-20261112/review3/admission-manifest.json`；原条目来自 manifest 指定 T9-24 base。实际验证 selection SHA 与 manifest 相符，并逐例核 source_split、双键连接、body SHA、SMILES 可解析。
该历史范围为 `t9-26-local-reference-v1`，含原 ChEBI heldout 与其已声明外部参考，不能推广为全局无污染。新加入 DDB 时**不声称已经检查其题目或来源交集**；在本轮研究样本不训练的条件下保留此边界，不让全库审查阻止构造。禁止以后拿这些小样直接宣称 DDB 泛化已得到保护。

## 通过/失败与下一轮
- 通过：SMILES、原描述、源行、许可、原 train、准入侧表和 hash 都绑定；任务输入不含目标描述；若做独立分析，证据是实际工具输出。
- 失败：以 PubMedQA 文本替代图/序列；把 caption BLEU 当事实正确率；test→train；绕过原 HOLD；把 DDB rubric 改写成训练题；给未知实验单位补默认值。
- 下一轮只加少量独立来源条件化测量样本与 **实际**分析轨迹，先保留原数值/单位/证据，再决定是否需要局部 L2。基线为原生配对或未融合证据，不先启动训练，不做全库扫描。

## 运行与局限
`build_samples.py` 可复跑；`verification.json` 是真实执行结果。样本是首批符合条件的3条方便样本，没有随机代表性；没有 benchmark scorer 运行、模型训练或性能提升。公共 raw GitHub TLS 失败后使用同一官方 GitHub 页面，MolT5 猜测 v5 URL 404 后定位原论文 v3；失败未伪装成功。人类负责人未指定，brief 保持 draft；没有动 map.md、ticket.md、L1/L2/冻结发布。

## Sources

[1] https://arxiv.org/html/2204.11817v3 — molt5-paper-v3
[2] https://github.com/scaleapi/DrugDiscoveryBench — ddb-repo
[3] https://github.com/IDEA-XL/MoleculeQA — moleculeqa-repo
