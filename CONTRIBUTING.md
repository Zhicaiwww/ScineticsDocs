# 文档如何改、如何上飞书

日常在 NAS 这份目录改 Markdown（枢纽：`/nas/nas8/users/wzc/docs`）。不要把订阅 URL、UUID、面板口令提交进 git。

## 1. Git（已启用）

在枢纽：

```bash
cd /nas/nas8/users/wzc/docs
git status
git add -A
git commit -m "docs: 说明本次改了什么"
git push origin main
```

本机已有一份 clone：`~/Desktop/wzc-docs`（origin 暂指向 NAS）。GitHub 仓库建好后：

```bash
# 在 GitHub 网页用账号 Zhicaiwww 建私有仓库 wzc-docs（不要勾选自动加 README）
cd /nas/nas8/users/wzc/docs
git remote add github git@github.com:Zhicaiwww/wzc-docs.git
git push -u github main

cd ~/Desktop/wzc-docs
git remote add github git@github.com:Zhicaiwww/wzc-docs.git
# 日常：NAS 继续当 origin；github 只用来触发 Actions
```

建议：**NAS 为集群现用稿，GitHub 为历史与 CI。**

## 2. GitHub Actions → 飞书

路线：`push main` → workflow `Sync docs to Feishu` → `scripts/sync_feishu.py` 调开放平台，把 `.md` 导入知识库。

你需要先做一次飞书侧配置（本仓库无法代你点完授权）：

1. 打开 [飞书开放平台](https://open.feishu.cn/app) → 创建**企业自建应用**。
2. 开通权限（至少）：
   - `drive:drive` / 云空间文件上传与导入
   - `docs:document` / 云文档
   - `wiki:wiki` / 知识库
3. 应用添加**机器人**能力并发布。
4. 在目标**知识库设置 → 成员**里，把该机器人加成可编辑成员（或管理员）。
5. 记下知识库 `space_id`（知识库设置 URL 或 API 可查）。
6. 在 GitHub 仓库 **Settings → Secrets and variables → Actions** 添加：
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`
   - `FEISHU_SPACE_ID`
   - 可选 `FEISHU_PARENT_NODE_TOKEN`（挂到某个目录节点下）

凭证只放 Secrets，不要写入 Markdown。本地试跑可复制 `.env.example` 为 `.env`（已 gitignore）。

首次同步会生成 `feishu-mapping.json`（文档路径 ↔ 飞书 token），CI 会回写进仓库。之后同一路径会先删旧知识库节点再导入，相当于整篇替换。

## 3. 还不能自动同步时

飞书 Secrets 未配时，Actions 会失败；**git 版本管理仍然可用**。配好 Secrets 后在 Actions 里 **Run workflow** 即可补同步。
