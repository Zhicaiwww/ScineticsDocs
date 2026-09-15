# 网络

使用者先读 [users](../users/user.md) 与 [storage](../storage/user.md)，再读本节。

| 文档 | 适用范围 |
|------|----------|
| [outbound-proxy.md](./outbound-proxy.md) | 出站代理索引 |
| [outbound-proxy.user.md](./outbound-proxy.user.md) | 使用者：概述、快速开始、命令与排查 |
| [outbound-proxy.dev.md](./outbound-proxy.dev.md) | 枢纽 mihomo、防火墙、profile.d |
| [admin.md](./admin.md) | 上游搬瓦工 VPS、带宽/流量、3x-ui / Xray |

## 约定摘要

| 约定 | 为什么 |
|------|--------|
| 全员入口：`http://10.200.1.3:7890` | 单中心；枢纽与计算节点 `profile.d` 相同 |
| 枢纽进程监听 `0.0.0.0:7890` | 内网各节点连同一 IP:端口；客户端不要写 `0.0.0.0` |
| `/etc/profile.d/mihomo-proxy.sh` 注入代理变量 | 登录 shell 默认生效 |
| 禁止公网暴露 7890；计算节点不装 mihomo | 缩小攻击面，配置一处维护 |
| 默认上游：美国加州 VPS `23.106.154.45`（VLESS+REALITY） | 集群经枢纽出网；套餐流量见 KiwiVM |

外网下载落盘路径见 [storage](../storage/)。带宽、月流量与中继细节见 [admin.md](./admin.md)。
