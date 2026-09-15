# 存储（使用者）

接续 [用户账号与家目录](../users/user.md)。集群把个人文件和共享文件分开放置，避免每人各下一份 Hugging Face 与 ModelScope 缓存。登录脚本会设置环境变量，使库默认写入共享缓存。访问令牌仍保存在家目录。

`$HOME`（`/nas/nas8/users/<用户名>`）与 `/nas/nas1/shared` 都在共享存储上：各节点将导出盘挂到同一 `/nas/nasN`。枢纽上的导出对应关系见 [admin.md](./admin.md) 第 3 节。总则见 [README.md](./README.md)。

## 快速开始

前置条件：已用本人账号登录，且 shell 会加载 `/etc/profile.d/`。

1. 在终端执行：

```bash
echo "HOME=$HOME"
echo "PATH_SHARED=$PATH_SHARED"
echo "HF_HOME=$HF_HOME"
ls -ld "$HOME" /nas/nas1/shared
```

预期结果：

- `HOME` 为 `/nas/nas8/users/<用户名>`。
- `PATH_SHARED` 为 `/nas/nas1/shared`。
- `HF_HOME` 为 `/nas/nas1/shared/huggingface`。
- 两个路径均可列出。

失败时：执行 `source /etc/profile.d/data-workspace.sh`，或重新登录后再执行上述命令。变量仍为空时，联系管理员。

## 磁盘拓扑

每台机器上的本地 SSD 同时出现在集群路径 `/nas/nasN` 下。作业脚本、多机任务和文档使用 `/nas/...`。`/data` 与 `/data0` 仅用于本机交互，不要写入跨节点脚本。

本枢纽对应关系如下。其他节点以现场挂载为准。

| 集群路径 | 本枢纽入口 | 用途 |
|----------|------------|------|
| `/nas/nas1` | `/data0` | 共享数据与下载缓存。可写范围仅 `shared` |
| `/nas/nas2` … `/nas/nas7` | 枢纽上 `/data` 对应 nas2；其余见 [admin.md](./admin.md) | 超量数据 |
| `/nas/nas8` | 见 admin 映射 | 家目录。可写范围仅 `users/<本人>` |

`/nas` 默认只读。普通账号**仅**对以下两处可写：

1. `/nas/nas1/shared`
2. `/nas/nas8/users/<本人>`（即 `$HOME`）

其余路径（含 `/nas` 根、`/nas/nas1` 除 `shared` 以外、`/nas/nas8` 除本人家目录以外、以及 nas2–nas7）均为只读。

白名单账号在上述两处之外，对 `/nas/nas2` … `/nas/nas7` 可读写。第一批白名单：`wzc`、`yjx`。需要写入超量盘时，向管理员申请加入白名单。

轻度使用（代码、环境、日常实验、公共缓存与中小规模共享数据）优先 **nas8 家目录** 与 **nas1 的 shared**。不要把日常项目写到 nas2–nas7。

枢纽上 `/data` 即 `/nas/nas2`，属于超量盘，不是家目录。非白名单不可写。

预期布局：

```text
/nas/nas8/users/<用户名>/     个人：代码、虚拟环境、实验、访问令牌
/nas/nas1/shared/             共享：下载缓存与主动放入的公共模型和数据
├── huggingface/              Hugging Face 缓存（HF_HOME）
├── modelscope/               ModelScope 缓存
├── torch/                    torch.hub 等
├── models/                   放入的公共权重
├── datasets/                 放入的公共数据集
└── tools/                    可选，公共工具
```

减少重复缓存依赖 `/etc/profile.d/data-workspace.sh`：各账号的 `HF_HOME`、`MODELSCOPE_CACHE` 等指向同一棵 `shared` 树。一名使用者已下载的 Hub 模型，其他账号再次 `from_pretrained` 时读取共享缓存，而不是再下载到各自的家目录。

访问令牌不放入 `shared`。`HF_TOKEN_PATH` 为 `$HOME/.config/huggingface/token`。使用 `huggingface-cli login`。不要把令牌写入系统脚本或共享目录。

## 分步操作

### 个人文件

1. 将代码、uv 环境、实验日志、Cursor 与 CLI 配置保存在 `$HOME`。目录建议见 [用户说明](../users/user.md)。
2. 将未公开的微调权重和数据保存在 `$HOME`，不要复制到 `shared`。
3. 不要在 `/data`、`/data0`、`/nas/nasN` 的盘根下另建家目录。
4. 非白名单账号不要向 `/nas/nas2` … `/nas/nas7` 写入。大体积数据且已在白名单时，再使用这些路径。

### 公共数据

1. 全组使用的权重放到 `/nas/nas1/shared/models/<项目或模型名>/`。
2. 全组使用的数据集放到 `/nas/nas1/shared/datasets/<数据集名>/`。
3. 由 Hugging Face、ModelScope、torch.hub 自动下载的文件无需再指定路径。环境变量已指向 `shared` 下对应缓存目录。
4. 在目录名或文件名中标明版本（例如 `foo-v1`），避免覆盖正在使用的文件。

本机交互可以使用 `/data0/shared/...`（在与 nas1 同树时）。作业脚本使用 `/nas/nas1/shared/...`。

### 权限

`/nas` 整树默认可读、不可写，仅下列例外。

| 路径 | 普通账号 | 白名单（第一批 `wzc`、`yjx`） |
|------|----------|------------------------------|
| `/nas/nas1/shared` | 读写（目录 sticky，不要删除他人文件） | 同左 |
| `/nas/nas8/users/<本人>`（`$HOME`） | 读写；建议 `755`，其他人只读 | 同左 |
| `/nas/nas8/users/<他人>` | 只读 | 只读 |
| `/nas/nas2` … `/nas/nas7` | 只读 | 读写 |
| `/nas` 根、`/nas/nas1` 除 `shared` 外、`/nas/nas8` 除各用户家目录外 | 只读 | 只读 |

不要使用他人账号向其家目录写入。不要请 root 长期向用户家目录堆积文件。

若 SSH 因权限过开而拒绝登录，将 `$HOME/.ssh` 改为 `700`。这是 sshd 在 `StrictModes yes` 时的限制，不是存储约定本身。

检查（普通账号预期：前两处可写，nas2 不可写）：

```bash
[ -w "$HOME" ] && echo "home 可写"
[ -w /nas/nas1/shared ] && echo "shared 可写"
[ -w /nas/nas2 ] && echo "nas2 可写" || echo "nas2 只读"
touch "$HOME/.perm_test" && rm "$HOME/.perm_test"
touch /nas/nas1/shared/.perm_test_$USER && rm /nas/nas1/shared/.perm_test_$USER
```

白名单账号检查 nas2 时，`[ -w /nas/nas2 ]` 应为可写。不要向 `/nas/nas1` 根目录或他人家目录做 `touch` 测试。

### 环境变量

来源：`/etc/profile.d/data-workspace.sh`。新登录会话或执行 `source` 后生效。

当 `HOME=/nas/nas8/users/<用户名>` 时，脚本还会设置 `XDG_*`、`HF_TOKEN_PATH`，并在 `$HOME/.local/bin`、`$HOME/envs/bin` 等目录存在时将其加入 `PATH`。

| 变量 | 值 | 用途 |
|------|-----|------|
| `PATH_USERS` | `/nas/nas8/users` | 家目录根 |
| `PATH_SHARED` | `/nas/nas1/shared` | 共享根 |
| `PATH_SHARED_MODELS` | `/nas/nas1/shared/models` | 公共权重 |
| `PATH_SHARED_DATASETS` | `/nas/nas1/shared/datasets` | 公共数据 |
| `HF_HOME` | `/nas/nas1/shared/huggingface` | Hugging Face 缓存根 |
| `HF_HUB_CACHE` | `$HF_HOME/hub` | Hub 仓库 |
| `TRANSFORMERS_CACHE` | `$HF_HOME/transformers` | transformers |
| `HF_DATASETS_CACHE` | `$HF_HOME/datasets` | datasets 库 |
| `MODELSCOPE_CACHE` | `/nas/nas1/shared/modelscope` | ModelScope |
| `TORCH_HOME` | `/nas/nas1/shared/torch` | torch.hub 等 |
| `HF_TOKEN_PATH` | `$HOME/.config/huggingface/token` | 按账号保存的登录态 |

cron、systemd 与部分 CI 不读取 `profile.d`。在此类任务中设置同等的 `Environment=`。

### 禁止的软链

盘名表示一块盘。下列做法会造成 `/data/data/...`，或使共享根所在磁盘不明确：

1. 在 `/data`、`/data0`、`/nas/nasN` 根下创建名为 `data` 或 `data0` 的目录或软链。
2. 在不是 nas1 的盘根下创建名为 `shared` 的目录或软链，冒充全局共享。
3. 用软链把 A 盘路径伪装成 B 盘路径。

允许使用人名或项目名作为子目录。路径写完整，例如 `/nas/nas1/shared/...`。

### 外网下载

访问 GitHub 与部分镜像站时，使用公司出站代理。见 [出站代理（使用者）](../network/outbound-proxy.user.md)。同地域 OSS 内网通常直连，不必经过 HTTP 代理。
