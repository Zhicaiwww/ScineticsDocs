# 出站代理 · 运维规范

**适用范围：** 安装、变更配置、防火墙与验收。  
**普通用户说明：** [出站代理](./outbound-proxy.user.md)。

**禁止**将订阅 URL、VLESS UUID、API `secret` 写入本文档树；密钥仅存 `/etc/mihomo/`。

---

## 1. 架构约定

| 项 | 规定 | 为什么 |
|----|------|--------|
| 软件 | mihomo（Clash Meta），[MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo) | mixed-port + provider，适合全员单入口 |
| 包 | Release `linux-amd64-compatible`（不足再换 `linux-amd64`） | — |
| 拓扑 | **单中心**：仅枢纽运行 mihomo；其它节点只配环境变量 | 避免多份订阅占用与配置漂移 |
| 进程 | systemd 系统服务；用户 `mihomo`（`nologin`） | 可审计、可重启 |
| 入口 | mixed **7890**（HTTP + SOCKS5） | 一个端口覆盖常见客户端 |
| API | `127.0.0.1:9090` + `secret` | 不对局域网暴露控制面 |
| 入站模式 | 不开 TUN、不开透明代理、不改默认路由 | 降低系统级劫持风险 |
| 监听与放行 | 进程听 `0.0.0.0:7890`；客户端一律连 `10.200.1.3:7890`；防火墙仅放行 loopback + `clients.allow` | 默认拒绝未授权源；`profile.d` 全员相同 |

**禁止**

- `nohup` / `screen` / 用户 `$HOME` 下私装一份。
- 用 DNAT/socat 转发 7890 作为多机接入。
- 在其它内网节点再装 mihomo（离开本网另开变更流程）。
- 让客户端把代理写成 `0.0.0.0:7890`（那是绑定地址）。

**当前运行参数（变更时同步改本节）**

- 枢纽 IP：`PROXY_HUB_IP=10.200.1.3`
- 默认出站：`vless-bwg-node3` → 搬瓦工 `23.106.154.45:443`（VLESS+REALITY，客户端 email `node3`）
- 备用出站：静态 `vless-35102`（`45.78.73.163:35102`）；机场 `SUB-AUTO`
- 该 VPS 必须 `IP-CIDR,23.106.154.45/32,DIRECT`
- 上游机器、带宽/月流量、Xray 版本与排障：**[admin.md](./admin.md)**（密钥仍只在 `/etc/mihomo/` 与 VPS `/etc/x-ui/`）
- systemd mihomo：**未** `enable`（重启后需手动 `start`，除非另行决定开机自启）
- 防火墙脚本：`mihomo-firewall.service` **已** `enable`（开机套用 7890 放行）
- `clients.allow`：`10.200.1.0/24`、`10.10.10.0/24`（可写 CIDR，一行一个）
- 已部署同一份 `mihomo-proxy.sh` 的节点：`host-10-200-1-3`、`-7`、`-12`、`-16`

---

## 2. 路径与权限

下列路径**仅存在于枢纽**。其它计算节点无 `/etc/mihomo/`。

| 路径 | 属主 | 权限 | 内容 |
|------|------|------|------|
| `/usr/local/bin/mihomo` | `root:root` | `755` | 二进制 |
| `/etc/mihomo/` | `root:mihomo` | `750` | 配置目录 |
| `/etc/mihomo/config.yaml` | `root:mihomo` | `640` | 主配置（敏感） |
| `/etc/mihomo/subscription.url` | `root:mihomo` | `640` | 订阅 URL（可选） |
| `/etc/mihomo/listen.env` | `root:mihomo` | `640` | `PROXY_HUB_IP=` |
| `/etc/mihomo/clients.allow` | `root:mihomo` | `640` | 客户端 IP 或 CIDR，一行一个 |
| `/etc/mihomo/apply-firewall.sh` | `root:mihomo` | `750` | 按 allow 列表重写 7890 的 iptables |
| `/var/lib/mihomo/` | `mihomo:mihomo` | `750` | GeoIP、provider 缓存 |
| `/etc/systemd/system/mihomo.service` | `root:root` | `644` | mihomo 单元 |
| `/etc/systemd/system/mihomo-firewall.service` | `root:root` | `644` | 开机套用 7890 放行 |

各节点（含枢纽）均有：

| 路径 | 属主 | 权限 | 内容 |
|------|------|------|------|
| `/etc/profile.d/mihomo-proxy.sh` | `root:root` | `644` | 全员 `http://10.200.1.3:7890` |

日志：`journalctl -u mihomo`。

---

## 3. 部署要点

```bash
useradd --system --no-create-home --shell /usr/sbin/nologin mihomo
```

二进制置于 `/usr/local/bin/mihomo`，`chmod 755`。升级时保留 `mihomo.prev` 后替换并 `systemctl restart mihomo`。

`config.yaml` 必备项：

- `mixed-port: 7890`，`bind-address: '*'`，`allow-lan: true`
- `mode: rule`，`ipv6: false`（未明确启用 IPv6 前）
- `external-controller: 127.0.0.1:9090`，`secret:` 随机
- DNS `enable: true`，`enhanced-mode: redir-host`
- 组名固定 **`PROXY`**；`rules` 末尾 `MATCH,PROXY`；内网 / `GEOIP,PRIVATE` 靠前
- 拉取订阅必须 DIRECT（provider `proxy: DIRECT`，并对订阅主机 DIRECT），避免空组套娃
- 过滤占位节点（名称含「防失联」、`server: 127.0.0.1` 等）

```bash
systemctl daemon-reload
systemctl start mihomo
# systemctl enable mihomo   # 仅在明确要求开机自启时执行
systemctl enable --now mihomo-firewall.service
```

无可用出口时，允许就位二进制与单元，**不得**宣称外网已开通。

新计算节点：拷贝与枢纽相同的 `/etc/profile.d/mihomo-proxy.sh`，确认源 IP 落在 `clients.allow` 网段（否则先改文件再执行 `apply-firewall.sh`）。不要在计算节点安装 mihomo。

---

## 4. 防火墙

TCP **7890**：默认丢弃；仅放行源 `127.0.0.1` 与 `clients.allow` 中的地址/网段。  
9090 仅绑 loopback。云安全组同步收窄。

变更客户端：改 `clients.allow` 后执行 `/etc/mihomo/apply-firewall.sh`（或 `systemctl restart mihomo-firewall`）。只改文件不等于已授权。  
禁止并列两套未协调的防火墙规则。

---

## 5. 环境变量与 Docker

| 对象 | 规定 |
|------|------|
| 全员 profile | `/etc/profile.d/mihomo-proxy.sh` → `http://10.200.1.3:7890`（枢纽与计算节点同一份） |
| `NO_PROXY` | 含 `localhost`、`127.0.0.1`、`10.0.0.0/8` |
| 不读 profile.d 的环境 | 任务内显式设置同一组变量 |
| Docker 拉镜像 | systemd drop-in `http-proxy.conf`，一律 `10.200.1.3:7890`；改后 `daemon-reload && restart docker` |

**禁止**未经评审把代理写入 `sudoers` 环境例外（避免 `apt` 等误走坏节点）。

---

## 6. 验收

1. `systemctl is-active mihomo` → `active`
2. `ss`：`*:7890`（即 `0.0.0.0:7890`）监听；`9090` 仅为 `127.0.0.1`
3. 任意已配置节点（含枢纽）：`echo "$https_proxy"` → `http://10.200.1.3:7890`
4. 任意已配置节点：`curl -sS -o /dev/null -w "%{http_code}" -x http://10.200.1.3:7890 https://github.com` → 2xx 类
5. 非白名单源访问 7890 失败
6. `journalctl -u mihomo -n 50 --no-pager` 无重启死循环

---

## 7. 日常操作

| 动作 | 命令 / 做法 |
|------|-------------|
| 状态 / 日志 | `systemctl status mihomo`，`journalctl -u mihomo -f` |
| 改配置 | 编辑 `/etc/mihomo/config.yaml` → `systemctl restart mihomo` |
| 换订阅 | 更新 `subscription.url` / provider `url`，端口与路径不变 |
| 增删客户端 | 改 `clients.allow` **并**执行 `apply-firewall.sh` |
| 开机自启 mihomo | `systemctl enable mihomo` |
| 停用 | `systemctl disable --now mihomo`（依赖节点同时失去代理） |

---

## 8. 已知故障模式

| 现象 | 原因要点 |
|------|----------|
| 订阅 403 `token is error` | token 不完整或失效 |
| 订阅域名 NXDOMAIN | CNAME 失效；改用面板仍存活的拉取地址 |
| provider 走 `PROXY[COMPATIBLE]` | 拉订阅未 DIRECT，空组套娃 |
| 连到 `127.0.0.1:80` | 订阅内占位节点；`exclude-filter` |
| 56xx 端口 i/o timeout | 机房出站限制；不得作默认节点 |
| `reality verification failed`（Hiddify/mihomo） | 见 [admin.md](./admin.md)：Xray 26.7 默认 `minClientVer`、SNI、flow |
| 枢纽出口不是 `23.106.154.45` | `PROXY` 未选 `vless-bwg-node3` |
| 7890 被占 | 残留用户态 mihomo；上线规范服务前须停掉 |
| 计算节点 `https_proxy` 指向 `127.0.0.1` | 旧 `profile.d`；应与枢纽同为 `10.200.1.3` |

---

## 9. 明确不做

- 不为每用户在 `$HOME` 再装 Clash
- 不在同一内网其它节点装第二份 mihomo
- 不用端口转发作为多机接入
- 不启用 TUN / 全局劫持
- 不把控制 API 绑到非本机
- 不把订阅 / UUID 写入 git 文档
- 未通过验收不承诺外网可用
