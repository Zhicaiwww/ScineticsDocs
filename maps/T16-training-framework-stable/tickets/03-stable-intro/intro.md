# 训练框架稳定版本介绍

**稳定对象**：`ScineticsAI/scinetics` origin/main `35f9646`（含 PR #3 `1c862c3`、PR #4 `d377bdd`）。本页区分本 map 的 2026-11-13 短测与沿用旧记录。

## 能力
- 统一入口 `train.py train RECIPE --runtime RUNTIME`：Qwen3.5-0.8B、2B（以及 9B 配方）的语言 CPT，严格模型 profile、冻结数据 reader、完整状态保存与恢复、原生权重导出。
- 精度：BF16 默认；TE 2.8.0 delayed FP8 显式开启（`fp8:` 与 `fp8_performance:` 两段 runtime 配置）。FP8 区域：0.8B 66 个，2B 90 个。
- 推荐性能组合：reader cache64、workers2 / prefetch8、Liger64 fused linear CE、仅 MLP 重计算、TE 原生 amax。
- 续训与迁移（PR #4）：`continuation.py` + `reshard_zero1.py`，冻结单 flat stage 的 TE FP8 ZeRO-1 检查点可跨布局迁移（已有 2B 8→24 卡实例）；可选 `stability_eval` 外部评测 hook。
- 配置入口：`configs/pt/`（recipe）、`configs/runtime/`（runtime）、`configs/deepspeed/pt_zero1.json`；0.8B 有 BF16/FP8 smoke 配方。

## 已有验证（旧记录，指向仓库文档）
| 项 | 结果 | 边界 |
|---|---|---|
| 0.8B BF16 / FP8 | 本 map 短测四卡各 10 步，loss/grad 有限；FP8 `run/fp8-coverage.json` 为 66/66（24 fused MLP + 42 other linear），终点 train_loss 2.4401/2.4475，相对差 0.303% | 本次未重跑 step2→10 与 473 张量导出；恢复/导出沿用旧记录 |
| 2B TE FP8 | 四卡 11.69 小时至 step4706，step2→4 恢复，导出前向通过 | 绑定当时的数据、环境、源码 |
| 2B 跨布局续训 | 8→24 卡，状态样本匹配，继续更新至 phase 3795，loss/grad 有限 | 改 batch 后轨迹不等价；被外部 SIGTERM 停止，最近完整保存点 3500 |
| CPU | 100 项单测（98 通过，2 跳过），221 文件身份通过 | 禁用 GPU |

## 未覆盖
- 4B 无实测；H100 多节点（跨节点）训练效率无实测（见任务书 B-20261113-03）。
- 新版本代码恢复旧 47 文件版本的 checkpoint 不被允许（源码哈希不同），须用原冻结提交。
- 新 0.8B 跨拓扑迁移无 GPU 验收；2B 续训 checkpoint 500–3500 的外部评测因空生成中断，生成质量待验收。
- `feat/tool-sft-runtime-20261028`（工具调用 SFT）不在稳定范围。
- 不含 ADT 与近期 RMSNorm / FLA 实验候选。
