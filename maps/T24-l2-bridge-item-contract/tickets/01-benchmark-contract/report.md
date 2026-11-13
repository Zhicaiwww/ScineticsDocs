# 共享 L2 桥 → item：轻量研究契约

结论：能从来源内字段回答的条目直接 L1→item；只有答案确实依赖跨来源身份/关系时才消费桥。已有桥优先；缺桥则在本 ticket 用显式、可回放的局部 join 做小样，不等全库 L2。此契约是研究侧车，不改正式 L2/L3 schema、准入结论或源数据。[设计依据：data/v1/layers.md:15–28,46；data/v1/02-scientific-evidence/l2.md:9–14]

## 1. 路由（按每条答案，而非整个模态）
| route | 何时用 | 最少动作 | 不允许的捷径 |
|---|---|---|---|
| l1_direct | 一个来源的原文/原生字段已包含输入、条件和答案 | 保存 record/field/value 证据；实体只用来源内 ID；关系为空需写 not_required | 为凑齐层级补造实体同一性 |
| existing_l2 | 要把别库注释/测量归到本实体，已有可定位桥 | 固定桥文件与版本/哈希、行键、两端 record、方法与原状态；桥仍是 candidate | 把桥 PASS/唯一命中解释成科学 same_as |
| local_join | 缺桥或已有桥不覆盖当前小样 | 固定左右小范围清单、键、规则版本和候选集合；写 ticket 侧车；只渲染来源归属或候选关系 | 改写 L2、去掉异构体/版本、模糊名称匹配后直接给唯一答案 |

缺字段只降级/跳过依赖它的条目，保留其他可做条目。已有权限拒绝或 HOLD 不绕过；不以“研究”标签消除既有禁止。局部 join 不是正式 L2 单元，不要求全库 coverage 或全量注册表先验收。

## 2. 最小侧车字段（null 必须附 missing_reason，不伪造值）
| 对象 | 必需字段 | 连接方式 / 限定 |
|---|---|---|
| source_record | dataset, source_version, l1_record_id, locator, input_sha256, field_path, value_sha256 或短原值, source_split, access_state | locator 定位单元/分片/行；field_path 是 JSON 数组；版本未知显式 unknown；已有 L1 PASS 范围只读复用 |
| entity | entity_id, namespace, native_id, entity_type, source_refs, representation_ref | entity_id=namespace:native_id；没有正式锚点则仅来源记录型研究条目，不冒充生产 B 包 |
| join | join_id, route, left_ref, right_candidates, key_fields, key_values_raw, method, rule_version, match_status, candidate_count, bridge_ref, bridge_sha256 | direct 时 not_required；局部 join 用 local_join_ref；两端版本、命名空间必须保留；不确定集合不择首条 |
| relation / measurement | claim_id, subject_ref, predicate, object_refs/roles, assertion_type, evidence_refs, raw_value, comparator, unit_raw, conditions_raw | 无关系任务标 not_required；测量须有 metric_type；缺单位仅可原文解释，不能做数值比较；条件未知不补默认值 |
| normalization（仅发生时） | norm_value, norm_unit, conversion_rule/version, condition_mapping, validation_status | 原值不覆盖；Ki/Kd/IC50/EC50 不互换；温度、pH、物种、assay、批次、构建体不同不静默合并 |
| item / facets | item_id, anchor_ns/value, facet_refs, recipe_id/version/code_sha256, content_sha256, input_refs, target_refs, evidence_scope | 关系作为实体包 facet；没有必要不复制对端正文；研究侧车字段不是现有生产检查器已支持的声明 |
| isolation / usage | benchmark_ref/version, source_split, parent_ids, exposure_group, protection_state/reasons, protection_refs, allowed_use, admission | allowed_use=research_only；admission=not_evaluated 或继承 HOLD/REJECT；benchmark 版本/split/scorer 不明记 unknown，不宣称性能可比 |

对齐现有 facets：l1_dataset/l1_record_id、aux_record_id、l2_ref、facet_key、evidence_level、state、fragment_sha256；歧义刻面 level=5；withheld_protected 不保留可消费内容引用。敏感保护原因/来源指针仅放隔离侧车，不能回流正文。[data/v1/03-tasks-samples/training-item.md:63–106]

## 3. 六模态先做什么
| 模态 | L1 直建起步 | 只有以下目标才需要桥 / 局部 join | 条件/分组键 |
|---|---|---|---|
| 蛋白 | 本记录序列＋来源功能说明 | 外部 GO/结构/测量归属 | accession+isoform+sequence version；突变背景、构建体、物种 |
| DNA | 来源序列/坐标＋来源声明属性 | 外部基因/调控注释定位 | assembly+chrom+start/end+coordinate convention+strand；不补造序列 |
| RNA | 来源 RNA 序列及类型 | Ensembl transcript→RNAcentral/SILVA 候选 | transcript version+规范化序列哈希；相同序列不代表同一基因/物种 |
| 分子（含反应） | 来源 SMILES/结构＋原性质；来源反应参与角色 | BindingDB→PubChem 或蛋白→反应→参与物 | 完整 InChIKey/CID；立体/电荷/盐型；reaction ID+方向+角色+条件 |
| 细胞 | 一个实验的表达摘要/已声明细胞标签 | 跨实验基因、扰动、细胞类型对齐 | study+sample+donor+batch+feature namespace；计数/归一化空间；不按 barcode 跨批合并 |
| 材料 | 来源样本组成/结构＋来源性质 | 别库结构/测量归属 | dataset+source_index；结构/相/计算方法/温压；化学式不作唯一身份 |

六轨的 benchmark 名称/版本/split/metric/scorer 由实际任务配方填写；本 ticket 交付共用接口，不等待其他 workers、不替其编造协议。benchmark 题、答案、rubric 和改写不得用来生成训练正文。能力比较须先固定输入、监督设置和 scorer；缺协议可继续独立来源的结构化小样，但不得报基准提升。

## 4. 已有真实回执支持的三条路径（本次复核回执，不重跑全库）
1. **GO 来源注释 → UniProt 引用候选 → go_goa facet**：T9-10 `results/bridge_check.json` 的 `family-full-v1/prot_go__uniprot_reference` 抽查 200000 行，198867 same_anchor、1133 isoform HOLD；`replay_swissprot.json` 为 100/100 正文一致、2468 fragments/0 bad。后者是蛋白包总体样本，不是单独 GO 准确率。限定答案为“来源如何注释”，保留 qualifier/evidence，不把 GO 注释当功能实验真值。
2. **Ensembl transcript → 规范化序列 → RNAcentral/SILVA → gene/RNA facet**：T9-17 `verify_links_f.json` 抽查 400/400 序列相同；221369 hit pairs、221353 link pairs，差额 16 都属于 held（未保护却遗漏=0）。`replay_gene3.json` 520/520 正文一致，只证明所取样本回放。版本去除曾用于验证器辅助比较，不应由新契约自动沿用为身份合并；精确序列匹配仍保留跨源 candidate。
3. **BindingDB 来源测量 → CID/完整结构键候选 → PubChem bdb_measure facet**：T9-19 `replay_released_n400_zeroledger.json` 的 bdb_measure：400 items、3667 lines、0 mismatches。`r3_resolve.py:120–164` 有 CID/完整键、multi-CID、CID-key conflict 和 connectivity-only 分支；`relib.py:39–58` 保留 Ki/Kd/IC50/EC50、原单位、pH/温度和多链靶标。回执不是每个 join 分支的科学核验；旧代码无键但 CID 存在也标 full，新契约仅记 source_declared_cid，不能声称完整结构一致。仅骨架一致的行不能作为指定立体分子的测量答案。

上述文件均在 `maps/T9-item-card/tickets/` 下对应 `10-protein-bridge-facets`、`17-gene-rna-real-merging`、`19-relation-measurement-facets` 目录。本次脚本只读取这些真实 JSON、记录 SHA-256 并断言回执内部一致；未创建虚拟记录，未重新取 L1 原文、未证实全量桥现在可读，也不继承“released”字样为生产授权。特别保留 open-alphaseq 的 n=0 / population=0，不能写成成功回放样本。

## 5. 不确定连接与测试保护
- exact_key_unique 只说明声明键唯一；仍为 candidate。ambiguous 保留全部候选；unmatched 留原记录；conflict/版本不明隔离依赖该身份的 facet，来源内任务可继续。不可用多对多笛卡尔积制造独立实验数；去重同时保留 observation/source IDs。
- 保护沿 record→entity/representation→join 候选集合→claim/facet→item 传播，复合路径每跳合并保护原因；不以改名、改写、单位转换洗掉保护。身份候选的一端受保护则该候选支持的答案不进训练；普通关系边不把整个知识图谱无限扩张为同一实体隔离组。
- test/eval_reserved 优先；dev 按原协议保留，不混进 train；unknown 不当 train。协议指定的同源簇/家族/骨架/实验父对象隔离优先于按行随机 split。只对本次小样的依赖闭包检查，不要求全库图闭合；可继续制作与其无关的来源内条目。
- 训练样本不能消费测试题、答案、rubric；保护命中只记录状态，不渲染受保护正文。未核保护的小样标 inspection_only，不把测试内容拿来试生成答案。

## 6. 两张清单与复核入口
**研究小样（逐条，局部失败不阻塞别条）**：①来源与字段指针可查、既有访问状态允许；②只检查本条用到的键/端点/原值单位条件；③不确定性准确显示，答案不超出证据；④本样依赖闭包的 split/保护传播；⑤固定配方和正文哈希，成功/跳过/未知留账。直接来源无需先补桥；明确已有回执可复用，不重复做许可证/全库安全审查。
**生产验收（另行授权，不是本轮前置）**：正式 schema/manifest/配方冻结；全范围引用与回放、覆盖守恒；独立身份与单位规则核验；正式许可与准入结论；完整 benchmark 隔离与回归/撤回验证；消费端 patch/选择表一致；发布审批。research_only 不自动升级。

运行 `python3 maps/T24-l2-bridge-item-contract/tickets/01-benchmark-contract/verify_receipts.py`；产生本目录 `verification.json`。它验证 CSV 路由/六模态/三路径、真实回执数值及最小保护/歧义规则，不声称新的 L1 内容回放。通过例：读取真实 RNA 回执保持 candidate、400/400 仅标回执证据；反例：以此把跨物种 RNA 标 same_as 或把 held 16 条归 train。当前 ticket 保持 open。
