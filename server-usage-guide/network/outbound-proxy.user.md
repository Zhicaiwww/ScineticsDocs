# 出站代理

接续 [账号与登录](../users/user.md) 与 [存储与路径](../storage/user.md)。集群节点默认不能直连公网。不使用代理时，Cursor CLI、Claude Code 等依赖国外模型接口的工具会失败，GitHub、pip 与部分数据下载会超时或极慢。公司在枢纽上提供统一的 HTTP/SOCKS 代理。登录脚本会注入环境变量。

## 快速开始

前置条件：已用本人账号登录任意已配置节点（登录 shell 会加载 `/etc/profile.d/`）。枢纽上 `mihomo` 须为 `active`（由管理员维护）。

1. 在终端执行：

```bash
echo "$https_proxy"
curl -I https://github.com
```

预期结果：

- `https_proxy` 为 `http://10.200.1.3:7890`。
- `curl` 对 GitHub 返回 `200` 或 `301`/`302`（经代理时常见 `HTTP/1.1 200 Connection established`）。

失败时：

1. 若变量为空，执行 `source /etc/profile.d/mihomo-proxy.sh`，或重新登录（非登录 shell、cron、部分 IDE 不会自动加载 `profile.d`）。
2. 若 `curl` 超时，联系管理员检查枢纽 `mihomo` 与防火墙。不要再安装一份 Clash 或 mihomo。

## 分步操作

### 代理地址

所有节点（含枢纽）使用同一地址：

| 项 | 值 |
|----|-----|
| 客户端 | `http://10.200.1.3:7890`（HTTP 与 SOCKS5 同一端口） |
| 枢纽进程监听 | `0.0.0.0:7890` |

1. 外网 HTTP(S) 经上述入口访问。
2. 不要把代理写成 `http://0.0.0.0:7890`。`0.0.0.0` 只表示枢纽「在所有网卡上接听」，客户端必须填能路由到的 IP `10.200.1.3`。
3. 不要使用 `127.0.0.1:7890`。该地址指向**当前机器**本机；计算节点上没有 mihomo，会连接失败。枢纽为与其它节点保持同一套 `profile.d`，也走 `10.200.1.3:7890`。
4. 不要在家目录或计算节点另行安装 Clash / mihomo，不要占用其他端口。
5. 不要将端口 7890 映射或暴露到公网。

### 环境变量

各节点同一份 `/etc/profile.d/mihomo-proxy.sh`。已打开的终端不会自动更新。

| 变量 | 值 |
|------|-----|
| `http_proxy` / `HTTP_PROXY` | `http://10.200.1.3:7890` |
| `https_proxy` / `HTTPS_PROXY` | `http://10.200.1.3:7890` |
| `ALL_PROXY` / `all_proxy` | `socks5://10.200.1.3:7890` |
| `NO_PROXY` / `no_proxy` | `localhost,127.0.0.1,::1,.local,10.0.0.0/8` |

cron、部分 IDE 与 CI 不加载该脚本。在任务中自行 `export` 或写入同一组变量。

### 常用命令

环境变量缺失时显式指定（任意节点相同）：

```bash
curl -I -x http://10.200.1.3:7890 https://github.com
wget -e use_proxy=yes -e https_proxy=http://10.200.1.3:7890 URL
pip install --proxy http://10.200.1.3:7890 PACKAGE
```

| 场景 | 做法 |
|------|------|
| git HTTPS 远程 | 读取 `https_proxy` |
| git SSH 远程（`git@…`） | 不经过本 HTTP 代理 |
| Cursor CLI / Claude Code | 在已设置 `https_proxy` 的 shell 中启动 |
| 单次不使用代理 | `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy` 后接原命令 |
| 内网地址被误送入代理 | `NO_PROXY` 已含 `10.0.0.0/8`；仍误走代理时联系管理员 |

### 计算节点

已放行网段内的节点登录后即可使用，无需本机再配端口。

1. 不要在计算节点安装第二份 mihomo 或 Clash。
2. 不要自行修改枢纽 iptables 或 firewalld。
3. 新节点若源 IP 不在 `10.200.1.0/24` 或 `10.10.10.0/24`，须由管理员写入 `clients.allow` 并更新防火墙。


### 上游与配额（普通用户需知）

集群入口仍是 `10.200.1.3:7890`。枢纽默认把境外流量送到一台美国加州中继（搬瓦工），不是你本机再配订阅。

| 项 | 说明 |
|----|------|
| 位置 | 美国加州，IPv4 `23.106.159.223`（当前默认；旧机 `23.106.154.45` 备用） |
| 协议 | VLESS + REALITY（443） |
| 端口带宽 | 套餐标称约 **2.5 Gbps**|
| 月流量 | 套餐常见约 **3 TB/月**，**全员共用** |
| 3x-ui 单用户限额 | 目前未再切 GB，超限只会发生在 **VPS 月流量** 用尽时 |
| 实际速度 | **下行**：枢纽实测 Cloudflare 约 **100 Mbps**（50 MB 文件）；小文件/GitHub 会更低。上行未测。不要按 2.5 Gbps 预期下载 |

国内站点按规则直连，一般不走这台 VPS，不计入其中继流量。GitHub、pip、模型接口等境外访问会走中继。月流量由运维在套餐面板查看；普通用户无法从 `https_proxy` 读出剩余流量。

### Docker

1. 宿主机 shell 中的 `export` 不会自动作用于 Docker 守护进程拉取镜像。守护进程代理由管理员配置。
2. 容器内访问外网时，在 `docker run -e` 或 Compose 中设置与上文相同的 `http_proxy` 等变量（同样使用 `10.200.1.3:7890`）。

### 故障排查

| 现象 | 检查 | 判断 | 处理 |
|------|------|------|------|
| `https_proxy` 为空 | 当前是否为登录 shell | 未加载 `profile.d` | `source` 脚本或重新登录 |
| `https_proxy` 为 `127.0.0.1:7890` | 是否仍为旧脚本 | 脚本未统一 | 联系管理员更新 `mihomo-proxy.sh` |
| `curl` 访问 GitHub 超时 | 枢纽 `systemctl is-active mihomo` | 服务未运行 | 联系管理员启动服务 |
| 机器重启后代理不可用 | 枢纽是否已 `enable` mihomo | 当前可以不启用开机自启 | 由管理员执行 `systemctl start mihomo` |
| 连接被拒绝或超时 | 源 IP 是否在放行网段 | 未放行 | 联系管理员。不要自改防火墙 |

原因未证实时，不要将「服务未运行」写成唯一确定原因。网络、节点与订阅均可能导致超时。

不要读取 `/etc/mihomo/config.yaml`。该文件含有节点密钥。
