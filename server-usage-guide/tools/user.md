# 系统工具

四台节点（node-3 / 7 / 12 / 16）已预装同一套命令行工具，登录后可直接执行，不必再按用户往 `$HOME` 里装一份系统级副本。Python 环境仍用 [账号与登录](../users/user.md) 里的 `uv venv`，装在本人 `$HOME/envs/`。调用外网 API 的 CLI 依赖 [出站代理](../network/outbound-proxy.user.md)。

版本会随运维升级变动；以本机 `命令 --version` 为准。下表为整理时的快照（2026-09-18）。

## 快速开始

前置条件：已用本人账号登录任意已配置节点。

1. 在终端执行：

```bash
command -v uv uvx claude cursor-agent agent codex gpustat nvtop git rg
uv --version
claude --version
cursor-agent --version
codex --version
gpustat --version
```

预期结果：上述命令均在 `PATH` 中（`uv` / `uvx` / `gpustat` / `cursor-agent` / `agent` / `codex` 在 `/usr/local/bin`，`claude` 在 `/usr/bin`）。

2. 不要执行 `curl … | sh` 再装一遍官方安装脚本到家目录，以免 `PATH` 里出现两套、版本互相覆盖。

## 清单

### 语言与环境

| 命令 | 位置 | 用途 |
|------|------|------|
| `uv` / `uvx` | `/usr/local/bin`（0.12.13） | 创建虚拟环境、装包。不要用 conda |
| `python3` | `/usr/bin`（3.10） | 系统 Python；项目代码用 `uv venv` 另建环境 |

创建环境的步骤见 [账号与登录](../users/user.md)。`uv pip` 拉包需要出站代理。

### 编码助手 CLI

登录态与密钥只放在本人 `$HOME`（如 `~/.claude`、`~/.cursor`、`~/.codex`），不要写入 `shared` 或他人家目录。首次使用按各 CLI 自己的登录流程，用**本人**账号。

| 命令 | 说明 |
|------|------|
| `claude` | Claude Code（约 2.1.x）。交互式助手 |
| `cursor-agent` | Cursor CLI（版本号形如 `2026.09.15-…`） |
| `agent` | 与 `cursor-agent` 同一二进制的别名 |
| `codex` | OpenAI Codex CLI（约 0.155.x） |

这些程序会访问境外模型接口，须已加载 `https_proxy=http://10.200.1.3:7890`。非登录 shell、cron、部分 IDE 终端需先 `source /etc/profile.d/mihomo-proxy.sh`。

### GPU 与进程观察

| 命令 | 用途 |
|------|------|
| `gpustat` | 每张卡的利用率、显存、占用用户（1.1.1） |
| `nvtop` | 交互式 GPU 监视（1.2.2） |
| `nvidia-smi` | NVIDIA 官方查询 |

整机占用总览也可用站点 [资源监控](/)。作业前先看卡是否已被占用。

```bash
gpustat -cpu
```

### 日常系统命令

各节点 apt 已装，登录即可用：

| 命令 | 用途 |
|------|------|
| `git` | 版本管理 |
| `rg`（ripgrep） | 代码搜索 |
| `tree` | 目录树 |
| `ncdu` | 交互式磁盘占用 |
| `unzip` | 解压 zip |
| `tmux` | 终端复用 |
| `htop` | 进程 |
| `iotop` / `iostat` | 磁盘 I/O |
| `nethogs` / `iftop` | 本机网络流量（部分功能可能需要额外权限） |

`git clone`、访问 GitHub 同样走 [出站代理](../network/outbound-proxy.user.md)。

## 约定

1. 系统工具由节点统一提供。缺命令时联系运维，不要在 `$HOME` 再铺一套全局安装前缀。
2. 项目依赖装进 `$HOME/envs/<项目>`，不要 `sudo pip install` 到系统 Python。
3. CLI 的 token、会话只属于当前 Linux 账号。
4. 不要把 `conda init` 写入 `bashrc` 抢占 `PATH` 里的 `uv` / `python3`。
