# 用户账号与家目录（使用者）

每名登录者使用独立的 Linux 账号。要使用的节点上均已注册同一套账号，同一登录名使用同一 UID 与主组 GID，因此对共享盘上的文件权限一致。开户数字见 [admin.md](./admin.md)。索引见 [README.md](./README.md)。

家目录不在各节点本地盘上。`$HOME` 固定为 `/nas/nas8/users/<用户名>`，位于共享存储：各节点把本机或其它节点导出的磁盘挂到同一路径 `/nas/nasN`。nas8 存放家目录；个人代码、uv 环境、实验与配置都在这棵树上。公共缓存与共享数据在 `/nas/nas1/shared`。存储路径、写权限与环境变量见 [存储（使用者）](../storage/user.md)。各卷从哪台机器导出、如何挂到 `/nas`，见 [存储 · 运维](../storage/admin.md) 中的 NAS 映射。

因此：在一台节点写入的 `$HOME` 与 `/nas` 上的数据，在其它已开户节点上是同一份文件。作业只要使用 `$HOME` 与 `/nas/...`，换节点后不必拷贝代码、环境或数据，理论上即可继续执行。不要把依赖写进只存在于某一节点本地、且未进入 `/nas` 的路径。

`$HOME` 其他人可读、不可写。

## 快速开始

前置条件：已用本人账号登录当前节点。

1. 在终端执行：

```bash
echo "USER=$USER  HOME=$HOME  UID=$(id -u)"
getent passwd "$USER"
ls -ld "$HOME"
```

预期结果：

- `getent passwd` 有一行输出，说明本机已开户。
- `HOME` 为 `/nas/nas8/users/<用户名>`，且与 `USER` 一致。
- `ls -ld` 显示属主为当前账号，模式为 `drwxr-xr-x`（`755`）。

`HOME` 与账号不一致时，联系管理员。不要在 `/data` 盘根另建家目录。

2. 可选：创建建议目录（不创建也不影响登录）：

```bash
mkdir -p "$HOME"/{code,envs,docs,tmp}
ls "$HOME"
```

预期结果：列出 `code`、`envs`、`docs`、`tmp`。

## 分步操作

### 代码位置

1. 将个人仓库、笔记本和实验脚本保存在 `$HOME`，建议放在 `$HOME/code/`。
2. 不要在 `/nas/nas1/shared` 中 clone 作为个人项目。该路径用于共享数据与缓存。
3. 不要在 `/data` 或 `/nas/nasN` 盘根堆放项目目录。
4. 身份以 `USER` 与 UID 为准。不要使用他人账号写入文件。

### 权限

`/nas` 默认可读、不可写。普通账号仅对 `/nas/nas1/shared` 与 `/nas/nas8/users/<本人>` 可写。白名单额外对 `/nas/nas2` … `/nas/nas7` 可写。细则见 [存储（使用者）](../storage/user.md)。

| 对象 | 普通账号 | 白名单（`wzc`、`yjx`、`xdc`） |
|------|----------|------------------------------|
| `$HOME` | 读写（`755`，其他人只读） | 同左 |
| `/nas/nas8/users/<他人>` | 只读 | 只读 |
| `/nas/nas1/shared` | 读写（sticky） | 同左 |
| `/nas/nas2` … `/nas/nas7` | 只读 | 读写 |
| `/nas` 其余路径 | 只读 | 只读 |
| `/tmp` | 读写 | 读写 |

不要使用他人账号向其家目录写入。不要请 root 长期向用户家目录堆积文件。

若 `.ssh` 权限过开导致无法登录，将 `$HOME/.ssh` 改为 `700`。

检查：

```bash
[ -w "$HOME" ] && echo "home 可写"
[ -w /nas/nas1/shared ] && echo "shared 可写"
[ -w /nas/nas2 ] && echo "nas2 可写" || echo "nas2 只读"
```

### 建议的家目录结构

下列布局不强制。按此划分便于协作和清理。以账号 `wzc` 为例，`$HOME` 为 `/nas/nas8/users/wzc`。若本机仍显示 `/data/wzc`，以 `echo $HOME` 为准。

```text
$HOME/
├── code/     源代码与 git 仓库，例如 code/LlamaFactory
├── envs/     虚拟环境，每个项目一个目录，使用 uv 创建，例如 envs/llamafactory
├── docs/     说明文档
├── tmp/      临时文件与一次性解压结果；可整目录删除
├── .config/  登录态与编辑器配置（Hugging Face 令牌在此，不进入 shared）
└── .local/   用户级可执行文件（目录存在时加入 PATH）
```

| 目录 | 用途 | 不要放入 |
|------|------|----------|
| `code/` | clone、修改代码、提交 git | 虚拟环境、数 GB 权重、下载缓存 |
| `envs/` | `uv venv` 生成的环境，一项目一目录 | 完整 `.git` 仓库 |
| `docs/` | 实验说明与规范 | 数据集 |
| `tmp/` | 可删除的暂存 | 唯一一份原始数据（需保留的放到 `code` 或 `shared`） |

将 `code` 与 `envs` 分开后，同一份代码可对应多个环境。环境损坏时删除 `envs/<名称>` 即可，不必重新 clone。登录脚本在 `$HOME/envs/bin` 存在时将其加入 `PATH`。

### 使用 uv，不使用 conda

使用 [uv](https://docs.astral.sh/uv/) 创建和管理 Python 环境。不要再用 conda 或 Miniconda 铺一套前缀。

原因示例：conda 环境是完整前缀，安装一次 PyTorch 通常再复制数 GB；多个 `conda env` 即多份重复拷贝，依赖求解也较慢。uv 虚拟环境是轻量前缀，wheel 缓存在本用户缓存中复用。已在 `envs/llamafactory` 安装过某一版本的 `torch` 后，再建 `envs/exp2` 并安装同一版本时，通常命中缓存，无需再次从外网下载。外网下载仍须经过出站代理。

集群已在 `/usr/local/bin` 安装 `uv` 与 `uvx`，登录后即可直接执行 `uv`，不必再按用户安装。`uv pip` 仍须能访问外网，见 [出站代理](../network/outbound-proxy.user.md)。

创建环境并安装项目（示例）：

```bash
mkdir -p "$HOME/envs"
uv venv "$HOME/envs/llamafactory" --python 3.11
source "$HOME/envs/llamafactory/bin/activate"
cd "$HOME/code/LlamaFactory"
uv pip install -e .
```

以后启动该环境：

```bash
source "$HOME/envs/llamafactory/bin/activate"
```

不要把 `conda init` 写入 `bashrc` 以抢占默认 Python。不要把系统级工具装进 conda `base`。

### 下一步

1. 存储路径与共享缓存：[存储（使用者）](../storage/user.md)
2. 外网下载与 `uv pip` / `git clone`：[出站代理（使用者）](../network/outbound-proxy.user.md)
