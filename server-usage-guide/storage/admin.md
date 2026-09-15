# 存储 · 运维规范

用户规范：[user.md](./user.md)。索引：[../README.md](../README.md)。  
脚本：`/etc/profile.d/data-workspace.sh`。

---

## 1. 磁盘组织

| 层级 | 规定 |
|------|------|
| 节点本地 | `/data`、`/data0` |
| 集群名 | `/nas/nasN` → 对应导出盘 |
| 对外路径 | 仅使用 `/nas/nasN/...` |
| **默认共享根** | **`/nas/nas1/shared`**（本机 `/data0/shared`） |

共享根树：

```text
/nas/nas1/shared/
├── huggingface/
├── modelscope/
├── torch/
├── models/
├── datasets/
└── tools/          # 可选
```

本机运维可进入 `/data0/shared`。**profile 与对外文档必须写 `/nas/nas1/shared`。**  
**禁止**在 `/data`（`/nas/nas2`）下再挂 `shared` 软链冒充共享根。

**`/nas` 写权限：** 默认可读、不可写。普通账号仅可写 `/nas/nas1/shared` 与 `/nas/nas8/users/<本人>`。`/nas/nas1` 根、`/nas/nas8` 根、他人家目录、以及 nas2–nas7，普通账号只读。  
**白名单：** 额外对 `/nas/nas2` … `/nas/nas7` 可读写。当前：`wzc`、`yjx`、`xdc`（谢东初）。增删后同步 [user.md](./user.md) 与本文。实现：各**导出节点**盘根 POSIX ACL（`setfacl -m u:<name>:rwx`），不递归已有子目录；普通账号仍为 `755` 只读。不要改 nas8（`10.10.10.16:/data`）盘根。
**`shared` 形态：** 目录 `1777`（sticky），文件 `666`。属组可为 `lab`。  
**家目录形态：** `/nas/nas8/users/<name>` 为 `755`，属主本人，他人可读不可写。

家目录根：`/nas/nas8/users/<name>`。各节点须能挂载 `/nas/nas8`。

轻度使用（代码、uv 环境、公共缓存）只写入 nas8 家目录与 nas1 的 `shared`。避免非白名单把作业输出写到 `/data`（本枢纽即 nas2）。

---

## 2. 环境变量导出值

| 变量 | 值 |
|------|-----|
| `PATH_SHARED` | `/nas/nas1/shared` |
| `PATH_SHARED_MODELS` / `PATH_SHARED_DATASETS` | `/nas/nas1/shared/models`、`.../datasets` |
| `HF_HOME` 及 HF_* | `/nas/nas1/shared/huggingface` 及子路径 |
| `MODELSCOPE_CACHE` / `TORCH_HOME` | `/nas/nas1/shared/modelscope`、`.../torch` |
| `PATH_USERS` | `/nas/nas8/users` |
| `HF_TOKEN_PATH` | `$HOME/.config/huggingface/token` |

个人 XDG / PATH：仅当 `HOME` 匹配约定前缀。  
变更脚本后同步本文档与用户规范。禁止将 token 写入 profile。

---

## 3. NAS 映射（本枢纽）

主机：`host-10-200-1-3`。

| NAS | 来源 | 角色 |
|-----|------|------|
| `/nas/nas1` | 本机 `/data0` | 共享（`shared`） |
| `/nas/nas2` | 本机 `/data` | 超量 |
| `/nas/nas3` | `10.10.10.7:/data0` | 超量 |
| `/nas/nas4` | `10.10.10.7:/data` | 超量 |
| `/nas/nas5` | `10.10.10.12:/data0` | 超量 |
| `/nas/nas6` | `10.10.10.12:/data` | 超量 |
| `/nas/nas7` | `10.10.10.16:/data0` | 超量 |
| `/nas/nas8` | `10.10.10.16:/data` | 家目录 |

作业与文档只使用 `/nas/nasN`。共享根换盘时：先定新路径，再改 profile 与文档，后搬数据。

### nas2–nas7 写白名单（POSIX ACL）

在**导出该卷的节点**上对盘根授权（枢纽 NFS 客户端上 `getfacl` 可能看不到 named user，以 `sudo -u <name> touch` 为准）。各节点需已安装 `acl`。

| NAS | 导出节点与路径 |
|-----|----------------|
| nas2 | node-3 `/data` |
| nas3 | node-7 `/data0` |
| nas4 | node-7 `/data` |
| nas5 | node-12 `/data0` |
| nas6 | node-12 `/data` |
| nas7 | node-16 `/data0` |

```bash
# 例：给当前白名单开 nas2（在 node-3）
setfacl -m u:wzc:rwx -m u:yjx:rwx -m u:xdc:rwx /data
# 收回某人：setfacl -x u:<name> <盘根>
# 核对：getfacl -p <盘根>；枢纽上 sudo -u xdc touch /nas/nas2/.t && rm /nas/nas2/.t
```

白名单只获得**盘根创建目录/文件**的权限。他人已有子目录仍按其属主权限，不会因本 ACL 被整树改写。

---

## 4. 禁止非法软链（强制）

在 **`/data`、`/data0`、任意 `/nas/nasN` 的直接子级**：

| 允许 | 禁止 |
|------|------|
| `/nas/nas8/users/...`、`/data/<人名或项目>/...` | `/data/data`、`/data/data0` |
| `/nas/nas1/shared/...`（约定共享根，实目录） | `/nas/nas2/shared -> …`、其它 `nasN` 根下伪造 `shared` |
| `/nas/nas2/wzc/...` | `/nas/nas2/data -> …`、跨卷伪装路径的软链 |

**必须：** 发现盘根下非法 `data` / `data0` / 非约定 `shared` 软链时删除，改为文档与脚本引用真实 `/nas/nasN/...` 路径。清理前确认无作业依赖该短路径。

**为什么：** 与盘名或默认共享根同名的软链会造成路径歧义与错卷读写。

---

## 5. 边界

- 开户 → [../users/admin.md](../users/admin.md)
- 代理 → [../network/outbound-proxy.dev.md](../network/outbound-proxy.dev.md)
- 不写节点密钥与订阅 URL
