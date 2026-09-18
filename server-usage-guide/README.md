# Server usage guide

集群使用指南：Linux 账号、存储路径和出站代理。

实时占用与分配见同一站点的 [资源看板](/)。

适用对象：登录集群的使用者。管理员与运维步骤见各目录下的 `admin.md`、`outbound-proxy.dev.md`。

路径：`/nas/nas8/users/wzc/docs/server-usage-guide`（枢纽上 `/data/wzc/docs/server-usage-guide`）。上级索引：[../README.md](../README.md)。`/data/README.md` 跳转到文档树。

| 部分 | 目录 | 内容 |
|------|------|------|
| 用户 | [users/](./users/) | 账号、共享家目录、跨节点约定 |
| 存储 | [storage/](./storage/) | `/nas` 路径、共享目录 `/nas/nas1/shared`、环境变量 |
| 网络 | [network/](./network/) | 出站代理 |

## 从哪里开始读

| 角色 | 阅读顺序 |
|------|----------|
| 使用者 | [users/user.md](./users/user.md) → [storage/user.md](./storage/user.md) → [network/outbound-proxy.user.md](./network/outbound-proxy.user.md) |
| 管理员 | [users/admin.md](./users/admin.md) → [storage/admin.md](./storage/admin.md) → [network/admin.md](./network/admin.md) → [network/outbound-proxy.dev.md](./network/outbound-proxy.dev.md) → `/etc/profile.d/*` |

使用者文档结构：概述、快速开始、分步操作。
