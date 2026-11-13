# 细胞：先保住对象层级，再补表达谱小样

## 结果
- 已从 T14 S1/S2 反查原论文，核定 **2 个核心端点**：hPancreas 跨研究注释、Geneformer 心肌疾病状态分类。定义见 `benchmark-contract.csv`；没有运行模型或评分器。
- 实际点读并保存 **3 个研究摘要条目，0 个细胞表达谱条目，0 个本目标训练就绪样本**。`examples.jsonl` 不是细胞注释训练集；正文哈希、许可侧表、来源引用与字段检查通过，误提升为可训练的负控制被拒绝。证据在 `verification.json`。
- 不等待全库 L2/准入。小样可先独立构造；当前具体阻塞是选定 benchmark 的原生张量及 donor/study 映射，不是全库审查。没有写 L1/L2、冻结发布、map.md 或 ticket.md。

## 两个核心 benchmark
1. **hPancreas：表达谱→细胞类型。** 本次读到 scGPT 预印本 v2：3,000 genes，reference 10,600 cells、13 类；query 4,218 cells、11 类；按研究来源划分，reference 为 Baron/Muraro，query 为 Xin/Segerstolpe/Lawlor。原文把 Baron 误拼为 Braon；这里对应其参考文献实体，不修改任何来源标识。[4]
   原指标包括 accuracy、precision、recall、macro-F1；reference 内训练/验证，query 评分。query 出现 MHC class II 而 reference 标签集不同，必须从官方映射或 scorer 确认未知类处理，不能静默删样本。本轮不沿用 T14 的旧预印本 96.7% 当 v2 或 2024 checkpoint 分数。[4]
2. **Geneformer heart：心肌表达排序→non-failing/HCM/DCM。** Fig.6b 明确训练 9/11/9 hearts、93,589 cells；留出 4/4/2 hearts、39,006 cells。作者 accuracy 90%、precision 82%、recall 87%，只是这组疾病分类，不是治疗效果。本次未重新运行或确认 precision/recall 的具体 averaging 实现。[3]

原始 donor 清单、scorer commit、精确细胞排除清单仍缺，CSV 明确标 unknown；不为得到完整表格而编造。scGPT 期刊的数据可用性指向 TOSICA 及作者 Figshare，Zenodo 代码包不是表达数据。[1]

## 三种独立条目与最小桥
|配方|输入→输出 / 科学能力|来源与连接键|条件、冲突与最小 L2|
|---|---|---|---|
|cell-profile-label|单细胞基因轴+数值向量→类型/疾病标签；观测性状态识别|官方 train H5AD + 同研究 metadata；study_id + donor_id + cell_barcode；gene_id + species|保留 raw/normalized/log/rank 类型与预处理 fit scope；同名 barcode 不跨研究 join。缺 donor 不假造；gene symbol 多义仅候选映射；只在基因版本/本体转换时补 L2|
|study-evidence-summary|研究描述+设计+聚合统计→有来源的研究摘要；不测细胞识别|Expression Atlas IDF/design/matrix summary；experiment accession + source unit/ref|统计单位为 study/group，不冒称 cell；不同矩阵处理版本不能互换；冲突并列并追源。可 L1→独立条目，不强制 L2|
|perturbation-response（下一迭代）|对照表达+实验干预条件→响应表达/基因程序；不是疾病分类改名|CINEMA-OT/Dong 官方训练实验 + condition/donor manifest；study+donor+condition+time+dose|必须有实验分配/对照证据才标 intervention；dose/time 原单位不可猜。组合留出与 donor 留出分别报告；不同单位需有证据的 L2 转换桥，缺测不填 0|

表达谱条目最少字段：`source/version/license, study_id, donor_id, cell_id, gene_axis, values, value_scale, condition, observation_or_intervention, source_split, exposure_group, provenance, preprocessing_fit_scope`。研究摘要单列 `item_kind=study_summary`，其 `cell_id/donor_id` 可空但不得升级表达谱输入。

多来源扩展只使用选定训练研究：Atlas 设计/表达字段与对应论文经明确 accession/DOI 连接；本体、基因注释经 species+stable gene ID+版本连接。论文的文字结论不能反向编造细胞向量；本文未声称这些桥已经建成。冲突不以最后一条覆盖。

## 真实小样与阻塞
- 只从既有 T9 `items/exp/items.parquet` 取首批 3 个 `mode=single_cell, split=train` 条目，连接 `patch/license_retag_t913/items_all.parquet` 的 `CLEAN_ALLOW`；保留正文、实验身份、facet refs、规则和原 hash。T9 历史 train 标签不等于 hPancreas/heart/scQA 隔离已经完成，故这 3 条固定为 `research_only_not_training`。
- T9 `L3-asset-summary.csv` 的 cell 包是 71,974 个实验/基因/run 摘要，不是细胞数量；本次未重数全包，不用其大规模 cited 数宣称有表达谱输入。
- 对 `_incoming-t14/hpancreas`、`hpancreas_figshare_v1`、`cinema_ot` 三个已定位目录检查：没有 `.h5ad`。历史日志分别为 Google 超时、Figshare 403、Dryad 403；这是本次读回的失败证据，不是本次下载结果。未扩大扫描，不能推断所有本地来源都没有数据。
- 本轮 HTTP 读取 Figshare API 亦 403，未绕过访问控制；原论文网页成功。没有重下 GB 级归档。

## 下一轮最短交付与通过/失败例
- 先指定一个可读、合法、独立训练研究的完整 cell→gene 向量及 donor metadata，取 **3–10 个细胞**做格式小样，不用稀疏矩阵几个非零格冒充完整细胞。保留已选测试研究/供者隔离；尚未识别测试身份就维持研究预览，不训练。
- 通过：同一 study/donor/cell 与 gene axis 一一对应，向量有限数且长度一致，原处理尺度可追源；摘要明确标 study 层。
- 失败：拿 top-20 study genes 当单细胞谱、以 batch 代 donor、把疾病关联当干预效果、按 cell 随机切分掩盖 donor 重叠、把 query 标签用于改写训练。
- 成本控制：不训练、不全库扫描、不做新一轮全面审查；仅检查所选样本字段/来源/测试组。不变更原 benchmark 的指标与分母；任何新 donor-disjoint 诊断另命名。

## 可复跑与边界
构造脚本在同伴票 `T23-crossmodal-understanding-brief/tickets/01-benchmark-contract/build_samples.py`，使用 `/nas/nas8/users/wzc/envs/scinetics-data/bin/python`；只读已定位小表，输出仅这两个 ticket。3 条是方便样本而非随机代表样本，未量化生物学正确性、泛化或训练效果。任务书仍为 draft，负责人未指定，不登记 assigned、不关闭票。

## Sources

[1] https://www.nature.com/articles/s41592-024-02201-0 — scgpt-paper
[3] https://pmc.ncbi.nlm.nih.gov/articles/PMC10949956/figure/F6 — geneformer-fig6
[4] https://www.biorxiv.org/content/10.1101/2023.04.30.538439v2.full — scgpt-preprint
