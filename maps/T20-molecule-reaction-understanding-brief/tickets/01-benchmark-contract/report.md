# 小分子/反应：先分轨交付，不等全库审查

## 结果
- 已交4个端点契约：小分子ESOL/Lipo，反应Buchwald–Hartwig/Suzuki–Miyaura；对应T14 matrix C1/C3。
- `examples.jsonl`有6条真实L1小分子性质候选，各端点3条；反应0条。没有把未知split冒充官方train，也没有产率填0。
- `verification.json`：6条通过固定ESOL/Lipo测试实体和Murcko scaffold排除；532个测试输入、530个scaffold键，输出不含测试题/答案。
- 小样不是生产训练准入：小分子train/validation membership未确认；反应还缺本地HTE训练身份与条件。此缺口不阻塞材料独立小样。

## 原始协议核实
T14入口：`maps/T14-sci-fm-survey/tickets/09-targets-benchmarks-datasets/matrix.csv` C1/C3；不重做综述。
1. SMolInstruct性质任务采用scaffold划分；同输入跨任务划分有一致性约束，不能拿random split的历史分数直接对比。[6]
2. 官方`compute_metrics.py`将ESOL/Lipo交给数值评分；`calculate_number_metrics`输出RMSE及总数、无答案、无效答案计数；RMSE只在可解析数值上计算，因此必须同时保留失败分母。[2][7]
3. ChemLLMBench原论文Appendix C把产率转成高产率二分类；每HTE集抽30 validation/100 test，ICL用random示例，比较k=4/8，报告5次均值/标准差；不等于连续产率回归。[5]
4. 官方仓库提供BH/Suzuki源链接；本轮已核论文与入口，但高产率精确阈值、可执行解析器及固定测试身份映射仍未知，不能自定阈值后冒称原协议。[3][4][5]

## 从能力反推条目
- 小分子：输入原始SMILES，输出实测性质、数值、原单位；保留测量条件缺失状态。ESOL只用measured字段，不能用ESOL predicted字段冒充实验金标。
- 反应：输入reactants/products、催化剂/配体/溶剂/碱等角色与条件，输出原生实验产率或经已确认阈值生成的类别；反应生成不作为本轨主目标。
- 当前L1：`/nas/nas6/users/wzc/datasets/l1-v3/f1/source-42887feb0c12/`。ESOL unit `9bcd27e10bede260e1fc`；Lipo unit `a69f48d636e04f671897`。每样本保留具体parquet、sha256、physical_row和来源ID。
- 整合键：来源内unit+ordinal+source ID；跨PubChem/ChEMBL使用显式ID映射和parent/stereochemistry，再加endpoint、单位和条件。名称相近不是same_as；不同测量并存，不能无证据平均。
- 反应跨源键：实验/批次+有角色的反应物/产物+条件；USPTO另保留patent ID。同反应SMILES不保证同实验，缺失产率不是零产率。
- 已读4个USPTO L1 unit元数据，均为pid/molecules/text，没有独立yield/conditions列；文本是否含可抽取产率未检查，不能把“无专列”说成“无产率”。详见reaction-source-inspection.json。
- 本轮没有实际跨库拼接，不需要全库L2。只有身份/反应角色/单位解释需要时消费局部L2证据，并把holdout身份沿连接传播。

## 实际核验与边界
- `build_examples.py`使用既有`/nas/nas8/users/wzc/envs/scinetics-data/bin/python`，pyarrow读取L1，RDKit形成派生筛选键，原SMILES未改写。
- ESOL扫描5行取得3条，拒绝2条测试实体或scaffold；Lipo扫描3行取得3条。不是完整数据可用量统计。
- 固定测试仅ESOL112/Lipo420的本地文件；sha256见verification。未扩称其他SMolInstruct任务或整个化学benchmark去污染。
- 尝试扩至其他性质任务时遇到带分号的非法SMILES表示；未修补源token或静默跳过，缩回已声明两核心端点。其他端点明确未覆盖。
- L1记录中的nas1旧原CSV路径不存在；6条可回读当前L1，但独立原CSV parity=0，不能声称已与原CSV核对。T2历史保真证据仅作上游引用。
- HF元数据直连SSL失败；通用网页extract后端不支持内容提取；改用官方GitHub API和arXiv HTML取得协议，未绕认证或权限。
- `source-retrieval.json`记录官方代码blob和内容哈希；论文与补充metrics文本保存在evidence，交付哈希另见artifact-manifest.json。

## 下一轮最小动作
1. 仅为ESOL/Lipo补官方train/validation身份，当前6条匹配不到train就不晋级；不新增全库审批。
2. 仅为两个HTE端点补本地train位置、固定test IDs、条件列、二分类阈值；先各构3条，缺数据就继续明确阻塞，不用USPTO无产率记录代替。
3. 模型训练、全量构造、发布、跨库大规模去污染均未运行；ticket保持open，人类负责人待指定。

## Sources

[2] https://github.com/OSU-NLP-Group/LLM4Chem/blob/main/compute_metrics.py
[3] https://github.com/ChemFoundationModels/ChemLLMBench/blob/main/README.md
[4] https://github.com/ChemFoundationModels/ChemLLMBench/blob/main/data/Readme.md
[5] https://arxiv.org/html/2305.18365v3
[6] https://arxiv.org/html/2402.09391v2
[7] https://github.com/OSU-NLP-Group/LLM4Chem/blob/main/utils/metrics.py
