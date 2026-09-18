# 文档

树根：`/nas/nas8/users/wzc/docs`。枢纽上 `/data/wzc/docs` 为指向该树的软链。

本目录用 **git** 做版本管理；`git push` 到 GitHub `main` 后，Actions 把 Markdown 同步到飞书知识库（需已配置 Secrets）。操作说明见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

枢纽站点两个标签：[资源监控](/) · [使用文档](/docs/server-usage-guide/users/user)。内网入口 `http://10.200.1.3:18080/`。

| 项目 | 路径 |
|------|------|
| [资源监控](/) | GPU / 存储占用与账号分配 |
| [使用文档](/docs/server-usage-guide/users/user) | 账号与登录、存储与路径、出站代理、系统工具 |

