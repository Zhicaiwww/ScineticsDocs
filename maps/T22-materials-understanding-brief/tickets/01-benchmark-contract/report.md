# 材料：fold_0来源内小样已实做

## 结果
- 交付3个Matbench v0.1端点契约与9条真实L1小样：steels/expt_gap/dielectric各3条。
- 所有样本只属于各任务**fold_0 train_val**，不是独立validation，也不是所有fold的共同train。
- `verification.json`：9/9条输入与标签逐项等于原生JSON；官方index→mbid→fold映射通过，三个任务的train/test ID交集均为0。
- 联合排除本轮3任务fold_0测试材料的1872个规范组成键；没有复制测试标签。其他10任务、其他fold、跨库晶体等价未宣称已清理。

## 原始协议与T14承接
T14入口：`maps/T14-sci-fm-survey/tickets/09-targets-benchmarks-datasets/matrix.csv` M2/M3；原生包交接见T2-36 `handoff-items.csv`。
- Matbench官方API区分每折train_val和test，超参选择只能使用train_val；不能把5fold的train并集作为统一训练集。[1][2]
- 官方元数据：steels输入composition、target=yield strength、单位MPa、312行；expt_gap输入composition、target=gap expt、eV、4604行；dielectric输入structure、target=n、无量纲、4764行。[3]
- 特别纠正命名误读：dielectric任务的n是折射率，不是直接预测介电常数。证据为T14-10已冻结的`results/matminer-metadata.json`中columns.n与description；本轮不做n²换算。
- 回归比较口径为原单位MAE；每外折分别训练/评测，最后报5fold结果。当前没有模型/scorer成绩，不引用不透明MatBench聚合百分数作基线。

## 能力→条目→整合
- steels：组成→屈服强度；expt_gap：组成→实验带隙；dielectric：完整晶格/原子种类/分数坐标→折射率。是性质理解而非结构生成。
- L1定位：`/nas/nas6/users/wzc/datasets/{matbench_steels,matbench_expt_gap,matbench_dielectric}/l1/20261112-t14/`。
- 本轮真实连接：L1 `src_source_index` → 原生JSON index → 官方mbid → 固定fold；不是物理行号直接冒充mbid。具体路径、行号、index、源文件/协议sha256逐条保存。
- 官方index+1生成mbid规则复用T14-10 `results/matbench-id-evidence.md`；源顺序和index分别保留，未重排或新建随机split。
- 组成键用于保守holdout排除，不宣称同化学式就是同晶体。跨Materials Project或其他实验库时，连接须有源ID/version、结构fingerprint/等价证据、性质与条件；冲突测量并存，不无证据平均。
- 温度、压力、加工/测量/计算条件在原行缺失时明确null+missing_reason；没有假设298K/常压。结构保存原lattice/sites，不裁剪为化学式。
- 每条输出仅包含一个原生性质值、原单位；性质名称和单位不可混用。原生字段已足够，不等待L2；只在跨源结构等价或单位语义推导时需要局部L2。

## 实测核验
| 端点 | fold_0 train_val | fold_0 test | 输出小样 | 原生输入/标签一致 |
|---|---:|---:|---:|---:|
| steels | 249 | 63 | 3 | 3 |
| expt_gap | 3683 | 921 | 3 | 3 |
| dielectric | 3811 | 953 | 3 | 3 |
- 用既有scinetics-data Python/pyarrow，仅读取这些小数据集的标识/输入以建mask，输出9条；不是全量L3构建。
- `build_examples.py`可重放；`verification.json`记录输入sha、fold协议sha、composition键分母与未知范围。
- 组成解析0失败；不支持的组成格式会中断，不静默漏掉保护集。
- 数据许可/生产准入未在本轮重审；只完成本地研究候选，不宣称训练授权或跨源融合已完成。

## 最小下一轮
- 固定fold_0，保持3任务测试材料联合屏蔽；仅对选中少量材料补必要条件或可信结构连接，继续独立迭代。
- 若要5fold实验，必须各自重新构造train_val视图并单独训练；若要13任务联合训练，先针对那13任务传播测试身份，不能沿用本轮3任务PASS。
- 人类负责人未指定；草案未登记正式assignment；ticket不关闭，map.md未修改。训练/发布/commit均未进行。

## Sources

[1] https://github.com/materialsproject/matbench/blob/main/README.md
[2] https://github.com/materialsproject/matbench/blob/main/matbench/task.py
[3] https://github.com/materialsproject/matbench/blob/main/matbench/matbench_v0.1_dataset_metadata.json
