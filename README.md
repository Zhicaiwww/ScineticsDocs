# 文档

树根：`/nas/nas8/users/wzc/docs`。枢纽上 `/data/wzc/docs` 为指向该树的软链。

本目录用 **git** 做版本管理；`git push` 到 GitHub `main` 后，Actions 把 Markdown 同步到飞书知识库（需已配置 Secrets）。操作说明见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

枢纽上文档与资源看板同站：看板 [`/`](/)，使用指南 [`/docs/server-usage-guide/`](/docs/server-usage-guide/)。内网入口 `http://10.200.1.3:18080/`。

| 项目 | 路径 |
|------|------|
| [资源看板](/) | GPU / 存储占用与账号分配 |
| [Server usage guide](./server-usage-guide/) | 集群账号、存储、出站代理 |

