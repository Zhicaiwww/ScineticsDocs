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

## 2. 同步到飞书个人知识库

「Scinetics公司文档」是**飞书个人版**知识库，不能把应用机器人加成成员。同步以 **WangCharles 的 user_access_token** 写文档。

知识库 `space_id`：`7685660980340067514`。

### 开放平台（一次性）

1. 应用 **权限管理** 打开（用户身份）：`wiki:wiki`、`docs:document` / `docx:document`、`drive:drive` / `drive:file`、**`offline_access`**。
2. **安全设置 → 重定向 URL** 增加：`http://127.0.0.1:8765/callback`
3. 创建版本并发布。

### 本机授权与第一次同步

```bash
cd ~/Desktop/wzc-docs
cp .env.example .env   # 填 FEISHU_APP_ID / FEISHU_APP_SECRET
python3 scripts/feishu_oauth.py    # 浏览器登录飞书
python3 scripts/sync_feishu.py
```

Token 写在 `.feishu-user.json`（已 gitignore）。不要把 App Secret、token 提交进 git。

GitHub Actions 需要 Secrets：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_SPACE_ID`、`FEISHU_REFRESH_TOKEN`（oauth 成功后从 `.feishu-user.json` 的 `refresh_token` 拷贝）。refresh_token 用一次就会换新，CI 长期跑还要把新 token 写回 Secrets。
