"""Write bounded benchmark tables and unassigned draft briefs."""
from pathlib import Path
import csv,json,hashlib,subprocess,datetime
R=Path('/nas/nas8/users/wzc/docs/maps')
P={n:R/n/'tickets/01-benchmark-contract' for n in ['T21-cell-understanding-brief','T23-crossmodal-understanding-brief']}
fields=['benchmark','t14_anchor','scientific_capability','input','output','observation_or_intervention','original_metrics','split','sample_unit','author_result','scorer','version','source_url','evidence_file','source_sha256','evidence_level','minimal_training_recipe','minimal_l2_bridge','isolation','open_gap','scorer_executed']
rows={
'T21-cell-understanding-brief':[
['scGPT hPancreas annotation','S1','跨研究细胞类型识别；不是研究摘要分类','cell gene-expression profile; 3000 gene axis','cell type label','observational','accuracy; precision; recall; macro-F1','reference Baron/Muraro 10600 cells 13 classes; query Xin/Segerstolpe/Lawlor 4218 cells 11 classes; train/validation from reference','cell prediction; study split; donor independence unverified','No v2 result extracted; do not reuse T14 old 96.7% as this version','paper S.5.1 sklearn implementations; exact code commit unknown','bioRxiv 2023.04.30.538439v2','https://www.biorxiv.org/content/10.1101/2023.04.30.538439v2.full','scgpt-preprint.txt','', 'primary full paper retrieved; protocol read; data/scorer not run','native train H5AD + study/donor/cell metadata; no synthetic tensors','gene namespace/label ontology only if mapping needed','query protected; group study/donor; fit preprocessing on train; new diagnostic separate from native protocol','exact H5AD unavailable in bounded candidates; donor manifest and unknown-label mapping not verified','false'],
['Geneformer heart disease classification','S2','心肌表达状态识别；非治疗或因果推断','cardiomyocyte rank-value gene expression encoding','non-failing / hypertrophic / dilated cardiomyopathy','observational classification; in-silico perturbation is separate','accuracy; precision; recall; averaging not reverified','training non-failing9/HCM11/DCM9 hearts 93589 cells; out-of-sample4/4/2 hearts 39006 cells','cell prediction; heart/donor holdout','Fig6b accuracy90%; precision82%; recall87%; author only','Geneformer original classification pipeline; scorer commit unknown','Nature 2023 Fig6b author manuscript PMC10949956','https://pmc.ncbi.nlm.nih.gov/articles/PMC10949956/figure/F6/','geneformer-fig6.txt','','primary figure legend retrieved; no reproduction','training hearts expression + phenotype/donor map','stable gene ids + disease label mapping; do not infer intervention','all cells of a heart stay together; preserve original heldout; study reuse tracked','native donor list/tensors/license and metric averaging not checked','false']
],
'T23-crossmodal-understanding-brief':[
['ChEBI-20 molecule captioning / MolT5','X1','分子表示到自然语言功能描述；词面相似度不是事实证明','molecule SMILES (graph serialization)','natural-language molecular description','not applicable; source annotation','BLEU-2; BLEU-4; ROUGE-1/2/L F1; METEOR; Text2Mol','paper 33010 pairs 80/10/10%; local release 33008; official train only for sample; original split preserved','molecule-description pair; molecule/scaffold isolation for additional diagnostic','MolT5-Large Table1 BLEU4=0.508; author only','official MolT5 caption evaluation code; commit/dependency pin pending; not executed','arXiv:2204.11817v3; local T9-24 source + T9-26 review3 pinned manifest','https://arxiv.org/html/2204.11817v3','molt5-paper-v3.txt','','primary paper + official repo; 3 local scoped-train samples checked','native ChEBI20 paired SMILES/description; preserve source fields','none for native pair; cross-source CID/structure/stereo bridge only when joining','T9-26 review3 item_id+hash+train+ADMIT_SCOPED_TRAIN; no heldout rewrite','paper/local total differs by2; exact scorer version and global contamination not verified','false'],
['DrugDiscoveryBench','X4','工具与独立证据约束的多步药物发现工作流；不自动算模态理解','evaluation task prompt plus actual scientific files/tools; no task payload accessed here','final answer plus trace and external-tool evidence','task dependent; not inferred from capability name','README reward.json 0-100 and grades_detail per criterion; outcome/process rubric aggregation formula not reverified','82 eval-only tasks; no train/dev split claimed or constructed','execution-grounded task; repeat/budget/judge fixed when evaluated','No model baseline verified; no score produced','Harbor 0.13.1; image1.0.2-lightweight per README; task judge not read','official README snapshot hash; main is not immutable task release','https://github.com/scaleapi/DrugDiscoveryBench','ddb-repo.txt','','primary README only; no prompt/answer/rubric download','independent sources only: conditional assay records and real tool traces; not DDB-derived','local identity/unit/evidence bridges only; no global L2 prerequisite','evaluation only by user instruction; prompts/answers/rubrics/canary excluded from training; independent-source overlap unknown','immutable task/scorer release and aggregation not verified; access approval required separately; no task-level read','false']
]}
for n,rr in rows.items():
 p=P[n]
 for row in rr:
  assert len(row)==len(fields)
  row[14]=hashlib.sha256((p/'sources'/row[13]).read_bytes()).hexdigest()
 with (p/'benchmark-contract.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(fields);w.writerows(rr)
 cell=n.startswith('T21');id='T21-01' if cell else 'T23-01'
 goal=('将细胞表达谱和研究摘要分开，补一个合法训练研究的原生表达格式小样' if cell else '将分子—文本配对扩展成少量独立来源的科学证据条目')
 known=('已核2个原始端点；3个真实研究摘要、0个表达谱；hPancreas/CINEMA精确候选目录无H5AD。摘要不能替代细胞向量。' if cell else '已核2个核心端点；3个真实ChEBI20 train配对通过字段/hash检查。6,407是已读历史有界准入侧表的行数，不是本轮新准入；DDB题/答案/rubric未读取。')
 nextgoal=('3–10个cell-profile-label样本；数据不可达则明确0条和来源阻塞，保留现有3个study_summary，不造表达值' if cell else '在现有3个molecule_text_pair之外，从独立许可来源构造3–10条带条件/单位/证据的测量条目；有真实工具执行后才添加trace')
 passed=('study+donor+cell+gene axis与完整向量绑定，训练来源且测试组隔离；研究摘要明确标study层' if cell else '真实SMILES和原描述配对，train及双键准入匹配；独立测量保留原单位/条件，工具证据可重放')
 failed=('top-20 study genes充当单细胞谱、batch充当donor、把疾病标签当干预或随机拆同donor' if cell else '纯文本QA冒充跨模态、test改train、DDB题/rubric改写训练、未执行的工具轨迹')
 text=f'''---
id: {id}-brief-draft
title: {goal}
assignee: null
reviewer: null
requester: wzc
status: draft
source: {id}
created: 2026-11-13
due: null
access: 仅指定ticket写；既有数据只读；内部非商业研究
---

## 目标
**场景**：独立研究小样；不接生产L1/L2/L4、不训练、不等待全库整理。{goal}。
**指标**：样本数逐类精确计数；来源、原split、hash和字段校验零失败；原benchmark指标单列，基线为未经融合的原生来源条目。本票不报告模型性能或容忍度。
**完成标志**：交付{nextgoal}，并以可运行检查与明确阻塞记录证明结果。
原因：先验证科学对象和证据能否正确输入任务，再扩大构造，避免把覆盖量当能力。

## 背景与依据
### 已知结论
|结论|数字与适用范围|出处|
|---|---|---|
|当前证据|{known}|report.md；verification.json|
|协议边界|2个核心端点仅协议核对，模型评分0次；词面/分类/工作流指标不混排|benchmark-contract.csv|
|权限边界|不覆写L1/L2/冻结发布；只改本ticket；未分配人类执行者|用户指令；scope.md|
### 代码版本
构造脚本：maps/T23-crossmodal-understanding-brief/tickets/01-benchmark-contract/build_samples.py；实际解释器 /nas/nas8/users/wzc/envs/scinetics-data/bin/python。当前为未提交ticket脚本；不伪造Git commit。原scorer版本尚未全部固定，因此不开展benchmark结果比较。

## 输入
只需本目录 report.md、benchmark-contract.csv、examples.jsonl、verification.json；内含实际来源路径与限制。先选一个来源/实验，禁止扫描全库。跨源配方、连接键、单位、冲突与局部L2要求已在report展开。

## 交付物
examples.jsonl：科学输入/输出、source_id/record、版本/hash、许可、原split、父对象/暴露组、证据、缺失原因。verification.json：真实样本数、检查、失败及未执行范围。report.md记录方案与一轮结果；task.json保持真实执行身份与状态。

## 验收标准
- {passed}。
- 每条校验必需字段、内容hash与原split；至少一个失败样例必须被拒绝。对无数据的能力如实报0，不以摘要或引用数补足。
- 通过例：{passed}。
- 反例：{failed}。
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
'''
 (p/'brief-draft.md').write_text(text)
 s='/nas/nas8/users/wzc/.hermes/skills/research/grounded-citations/scripts/sources.py'
 subprocess.run(['python3',s,'--ledger',str(p/'sources/ledger.json'),'render','--replace-in',str(p/'report.md')],check=True)
 subprocess.run(['python3',s,'--ledger',str(p/'sources/ledger.json'),'verify',str(p/'report.md')],check=True)
 print(n,len(rr),'benchmark rows; unassigned draft written')
