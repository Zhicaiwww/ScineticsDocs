# DNA / RNA 分轨：契约草案与真实小样

## 结果
- 已构造 **3 条真实来源小样**：DNA 2 条来自 NT revised `splice_sites_acceptors/train.parquet`；RNA 1 条从 T9 RNAcentral 锚点经当前 L1 reader 点读。
- DNA 保留原生 train 序列、任务和数值标签；**0/1 标签语义映射尚未核验**，不把它们解释成特定生物学结论。RNA 为输入冒烟，`target=null`；没有捏造 RBP/MRL/ncRNA家族标签。
- `verification.json`：双次重建相同，JSONL回读相同；DNA train文件hash等于已有原始manifest。RNA 411 nt，原始序列与L1 payload一致，T→U只作可追溯显示转换。
- 未读取测试记录或答案。RNA 对既有 T9 157569 个保护hash作原始/T→U/反向互补的有限检查，0命中；这不是全库同源或所有benchmark审计。DNA沿用原生train和T14先前跨split精确交集0的记录，不声称已核反向互补或同基因边界。

## 原始来源核对
|来源|已核内容|证据限制|
|---|---|---|
|GenomicBenchmarks官方 `experiments/README.md` 在线搜索结果|官方表使用accuracy/F1；不同模型独立结果表|搜索返回原始官方页面内容，不是当前源码commit验收|
|T9-36 `coordinate-contract.md`|官方commit 605d8539830e16c85abe7826990958303ffc5e1c；loc2seq为0-based end-exclusive，负链reverse-complement；保留原参考字符|继承前票源码核验，未在本票重下载或执行参考窗口重建|
|本地 NT revised `MANIFEST.json` 与仅train文件|revision 851f9946252e90c665cdb3cc3eedb78f1f26197c；train SHA256已重算一致|数据版本可回源，scorer与0/1语义未在线全文核验|
|T14-08 `code-evidence/terry-r123--RNABenchmark.md`|已保存官方BEACON README：NoncodingRNAFamily、MeanRibosomeLoading等任务独立存在|原始官方实现缓存，当前线上全文获取失败；scorer/split待锁|
|T14-09 matrix D1/D2/D3|promoter v0、NT revised与旧版分轨；BEACON MRL原生r²仅独立端点|继承研究结论，不是本票运行的benchmark分数|

## 能力合同与优先顺序
1. **DNA-D-SPLICE**：DNA上下文→剪接类别，固定acceptor任务，不把分类MCC/F1冒充SpliceAI定位top-k/PRAUC。先补标签字典，再从同一train文件扩少量双类样本。
2. **DNA-D-PROMOTER**：参考组装上的定向序列窗口→启动子二分类。坐标条目不等于序列输入；本地release97参考构造未完成核验，故没有用release116替代，也没有捏造序列。
3. **RNA-R-NCRNA**：RNA序列→非编码RNA家族。RNAcentral只提供来源内rRNA描述，不能直接替代BEACON家族金标；当前样例只验证序列和回源。
4. **RNA-R-MRL**：5′UTR序列及实验上下文→mean ribosome loading。不得用RNA长度/家族/转录本表达量充当MRL；需要官方train测量值和实验条件。

## 条目配方
|配方|来源/键|条件与单位|冲突/缺失|通过例 / 失败例|
|---|---|---|---|---|
|splice类别|NT revision+task+native split+row/name+sequence hash|保留原始label，语义表版本；窗口方向、基因/坐标可缺但必须注明|同序列跨子任务不得当独立证据；label未知不造语义|通过：train文件原值+hash匹配；失败：把所有splice任务合并并随机切分|
|promoter|GenomicBenchmarks v0 train区间+assembly+chrom+start/end+strand|0-based半开区间；nt；严格对应GRCh38 release97参考|缺参考则不生成序列；保留原字符及单独normalization|通过：end-start等于重建长度且负链翻转正确；失败：用release116或闭区间偷偷替代|
|RNA家族|RNAcentral来源内ID+raw hash；官方family train ID另列|RNA原始T保留，显示U为派生；明确完整/截断|rRNA粗类不是细粒度family；缺标签target=null|通过：原字段可重放且不补标签；失败：看序列猜家族当金标|
|MRL|官方train记录ID+UTR sequence hash+experiment/batch|源定义的MRL标度及细胞/文库/条件；转换记录规则|缺值不是0；重复UTR不同条件不平均|通过：同一实验原生值与单位可回源；失败：以TPM替MRL或把test测量值写入监督|

只有实际跨来源连接才需L2：例如坐标到参考窗口要求组装一致；RNAcentral→家族标签必须有明确ID/版本或已核序列映射。当前RNA点读与NT train条目不需要全库桥。

## 可复现与验收
项目根执行：`PYTHONDONTWRITEBYTECODE=1 /nas/nas8/users/wzc/envs/scinetics-data/bin/python maps/T19-dna-rna-understanding-brief/tickets/01-benchmark-contract/build_examples.py`。

脚本上限：一个约9MB的DNA train文件hash、首2行；一个RNA点读；一个已有15MB保护hash文件；小型catalog定位。没有扫描生物数据全库，没有读取native test parquet。来源真实数据与合成/改写区分：本轮没有LLM生成答案。

小样验收是可回源与结构正确，不等于生产准入。DNA标签语义补齐前不计为语义验收通过；RNA目标为null不计监督数据。后续只做目标任务需要的局部同源/坐标/反向互补核验，不等待全库L2或全库审核。

## 缺口与阻塞
- 在线关键原文/源码复核部分未完成：直连和文档代理SSL EOF；提取工具为search-only；浏览器缺libatk；一次后续检索存证调用待批准，未重试绕过。
- 标签映射、scorer版本、BEACON原生split/许可、真实RNA监督样本、promoter参考序列未完成。
- RNA旧T9短key点读最初KeyError；已从现有catalog唯一匹配到完整key并记录完整record_id，不是自行补零或改原标识符。
- 未指定人类负责人；草案不注册assigned，不关闭ticket/map，不修改源库/冻结发布。
