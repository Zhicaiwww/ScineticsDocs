# 出站代理

隶属 [网络](./README.md)。枢纽以 **mihomo** 提供统一 HTTP/SOCKS5 入口。

| 文档 | 适用范围 |
|------|----------|
| [outbound-proxy.user.md](./outbound-proxy.user.md) | 用户：地址、环境变量、命令与验收 |
| [outbound-proxy.dev.md](./outbound-proxy.dev.md) | 运维：路径、systemd、防火墙、部署与排障 |
| [admin.md](./admin.md) | 上游 VPS、带宽与月流量、3x-ui |

| 项 | 值 |
|----|-----|
| 枢纽内网 IP | `10.200.1.3`（以 `/etc/mihomo/listen.env` 为准） |
| 客户端入口（全员相同） | `10.200.1.3:7890`（HTTP 与 SOCKS5 同一端口） |
| 枢纽监听 | `0.0.0.0:7890`（绑定地址，不是客户端填写值） |
| 默认上游 | 搬瓦工美国加州 `23.106.154.45:443`（VLESS+REALITY） |
| VPS 带宽 / 月流量 | 端口约 2.5 Gbps；月流量约 3 TB（以 KiwiVM 为准） |
| 3x-ui 用户配额 | 未另设 GB 上限，与套餐月流量共用 |
| 实测下行吞吐 | 枢纽 node-3：Cloudflare 50 MB 约 **100 Mbps**（2026-09-14，未测上行） |

上级索引：[../README.md](../README.md)。
