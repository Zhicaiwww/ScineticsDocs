# 蛋白理解：契约草案与真实输入小样

## 结果
- 已构造 **2 条真实来源小样、1 个来源实体**：蛋白序列 1 条，结构输入 1 条。两条均为输入/字段冒烟，`target=null`；**功能监督小样 0 条**，不能当作 EC/GO 训练数据或能力提升证据。
- `examples.jsonl` 来自 T9 已保存的 PDB 3EFW 样例，不下载数据、不读 benchmark 答案。结构仅保留模型1、A链、2个 CA 点，显式 `partial_structure=true`；不是完整结构，也不是 SaProt 3Di token。
- `verification.json` 记录真实执行：双次重建字节一致、JSONL 回读一致、序列长度267 aa；所有小样均排除训练消费。
- 原始协议核对 **部分完成**。T14-08 保存的 SaProt 原论文抽取可复用；本轮在线检索到官方 issue 对 scorer 的实质修正。官方源码直读失败，不能宣称已锁定或运行 scorer。

## 原始来源核对与关键纠偏
|证据|已看到的内容|边界|
|---|---|---|
|T14-08 `results/source-snapshots/03-protein.csv`|SaProt 的 DeepFRI EC、GO-MF 和 DeepLoc 输入/划分/指标；EC 13089/1465/1604，GO 26224/2904/3350，DeepLoc 8747/2191/2747|继承的论文抽取，不是本票重新核验完整论文|
|在线官方 `westlake-repl/SaProt/issues/23`，搜索返回作者评论|作者指出其数据预处理改变了 EC/GO 数据集；2024-04-18 评论指出评测前 flatten 导致形状错误，已改为按蛋白二维张量；2024-04-19称结果已更新|搜索返回官方原文摘要，未成功打开当前源码；不能直接引用旧 Fmax 为已验证 baseline|
|T9 `08-build-wwpdb-structure-pack/samples/v1_3EFW.txt`|267 aa、坐标与 Å 单位、entity/chain/model 定位|本票核验保存样例字节与解析；没有声称重新核验完整 wwPDB 原件|

决定：先锁能力和条目合同，不等待全库 L2；生产对比前必须钉 scorer commit、Fmax 聚合和结构过滤版。原 DeepFRI、SaProt 过滤版、纯序列、结构增强四者不能混排。旧论文数值不是本票验收阈值。

## 能力而非主题
1. **P-EC-SEQ / P-GO-SEQ**：仅给氨基酸序列，输出 EC/GO-MF 多标签概率；检验序列蕴含的功能信息。蛋白名称、EC、GO、功能文本不能出现在输入。
2. **P-EC-STRUCT / P-GO-STRUCT**：同一评测身份集加入实际结构表示，输出同一标签；与纯序列轨分开统计缺结构分母，不能把预测结构当实验结构。目标不是生成结构。
3. **P-LOC-SEQ**：仅序列判断细胞区室。定位注释可作标签，但不能同时塞进 prompt。单/多标签语义须服从锁定的 DeepLoc 版本。

## 条目配方
|配方|来源与连接键|条件/单位|冲突与缺失|通过例/失败例|
|---|---|---|---|---|
|序列→EC/GO|官方 train ID + accession + sequence hash + annotation release；同源簇为曝光组|标签字典版本、GO aspect、ECO证据、注释日期；概率无量纲|缺标签不是负例；冲突标签保留版本与证据，不多数投票|通过：train ID对应完整序列和同版标签；失败：名称相同但序列不同直接合并|
|结构增强→同标签|来源内 entity/chain/model；跨 PDB-UniProt 才需要有版本残基映射的 L2 桥|Å；实验方法/分辨率或预测来源及置信度分别记录|缺链/残基/坐标标缺失；不填0坐标、不把3Di当原子坐标|通过：链映射与序列一致且结构类型已知；失败：仅PDB标题却标结构模型输入|
|序列→定位|官方 train ID与标签映射，保留父蛋白和isoform|区室本体与多标签约定|冲突isoform单列，不把推断等同实测|通过：输入去掉定位文本；失败：把亚细胞定位注释放入输入|

来源内字段足够时直接 L1→小样；不要求全库 L2。只有结构-序列跨来源配对才要求桥；无明确映射时分别出条目，不假配对。

## 隔离与验收
- 当前小样没有 EC、GO、定位答案；只是独立研究文件，不宣称该蛋白已从所有 benchmark 排除。`target=null` 不意味着生产可用。
- 真正监督小样下一步只从官方 train 或已核明非测试实体取标签；测试 accession/同源簇/注释及其改写不进入样本。保护清单只需身份或hash，不需要题目答案。
- 小样合格：来源、字段定位、真实字节hash、输入轨、目标证据和原生split齐；重放一致。当前两条满足输入冒烟，不满足功能监督验收。
- 生产准入另验：锁定 scorer 和数据版本、目标任务同源边界、许可、完整输入表示、缺失/失败分母。不先要求全库泄漏审核。

## 运行与未完成
复现：在项目根运行 `PYTHONDONTWRITEBYTECODE=1 /nas/nas8/users/wzc/envs/scinetics-data/bin/python maps/T19-dna-rna-understanding-brief/tickets/01-benchmark-contract/build_examples.py`。脚本写入两票允许目录，没有训练、全量扫描或executor任务。

未完成：官方源码/论文在线全文复核与commit；真实EC/GO/定位监督样本；完整结构输入；局部benchmark实体排除。直接HTTPS与文档指定代理均SSL EOF，网页提取后端不支持提取，浏览器缺libatk；一次后续检索+存证工具调用待用户批准，未绕过或重发。任务书人类负责人待指定，ticket/map保持open。
