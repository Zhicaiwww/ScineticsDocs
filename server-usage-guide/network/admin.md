# 出站代理 · 管理员

**适用范围：** 上游中继 VPS、3x-ui / Xray、与枢纽 mihomo 的对接。  
**集群入口与防火墙：** [outbound-proxy.dev.md](./outbound-proxy.dev.md)。  
**普通用户：** [出站代理](./outbound-proxy.user.md)。

**禁止**将订阅 URL、VLESS UUID、面板路径口令、SSH 私钥、API `secret` 写入文档树。这些只放在 VPS `/etc/x-ui/` 与枢纽 `/etc/mihomo/`。

---

## 1. 上游机器（搬瓦工 / KiwiVM）

集群出站经枢纽 mihomo，默认节点为这台美国 VPS 上的 VLESS+REALITY，而不是计算节点各自翻墙。

| 项 | 值 | 备注 |
|----|-----|------|
| 厂商 | BandwagonHost（搬瓦工），面板 KiwiVM | 购买约 3 个月 |
| VEID | `2202335` | 面板 URL：`https://kiwivm.64clouds.com/2202335/main.php` |
| Node | `v2718` | 物理位置 US, California |
| 公网 IPv4 | `23.106.154.45` | 客户端与 REALITY 入站地址 |
| SSH | 端口 22，用户 `root` | 本机钥匙 `~/.ssh/id_rsa_banwagong`（注释 `id_rsa_banwagong`） |
| 系统 | AlmaLinux 9.7 | hostname `vital-ponies-1` |
| CPU | 4 vCPU（AMD EPYC-Genoa） | 与电商 4G 档规格一致 |
| 内存 | 约 4 GiB + 1 GiB swap | |
| 磁盘 | 约 80 GB ext4（`/`） | |
| 虚拟化 | KVM | |

**带宽与流量（两层，不要混用）**

| 层 | 限制 | 说明 |
|----|------|------|
| VPS 套餐（KiwiVM Bandwidth） | 按机内资源对应电商 **4C / 4G / 80G** 档：官方常见为 **端口 2.5 Gbps、月流量约 3 TB** | **以 KiwiVM 面板当月已用/剩余为准**。机器上未装 `vnstat`。超套餐流量会由厂商限速或停机，与 3x-ui 无关 |
| 3x-ui 客户端配额 | `total_gb = 0`、无到期 | **未**按用户再切流量。Mac 的 `wzc` 与枢纽的 `node3` 共用 VPS 月流量池 |
| 入站计数 | 3x-ui inbound `up`/`down` | 仅面板统计，不是套餐合同 |

应用层实测为**下行（下载）**（**2026-09-14 15:52 CST，枢纽 node-3** `host-10-200-1-3`，`curl -x http://127.0.0.1:7890` 拉取远端文件，出口 IP `23.106.154.45`）。**未测上行。**

| 源 | 大小 | 耗时 | 平均速度 |
|----|------|------|----------|
| Cloudflare | 20 MB | 2.57 s | 7.8 MB/s（约 **62 Mbps**） |
| Cloudflare | 50 MB | 3.79–4.20 s | 11.9–12.6 MB/s（约 **95–105 Mbps**） |
| Cachefly | 10 MB | 1.88 s | 5.6 MB/s（约 **45 Mbps**） |
| GitHub Release（git-lfs tarball，约 4.7 MB） | 4.7 MB | 2.61 s | 1.9 MB/s（约 **15 Mbps**） |

代表线路下行能力的是 Cloudflare 50 MB：**约 100 Mbps**。这是集群经中继把文件拉到 node-3 的速度，远低于 2.5 Gbps 端口标称。小文件（GitHub 单包）会明显更低。枢纽 `url-test` 延迟约 **1.1 s**。本机 Hiddify 同日 Cloudflare 50 MB 约 70 Mbps，低于枢纽（NAT 与个人 Wi-Fi 不同）。

KiwiVM 网页密码与 VPS root 密码不是同一套。SSH 以公钥为准，不要把 root 密码写进文档。

---

## 2. 中继软件

| 项 | 规定 |
|----|------|
| 面板 | 3x-ui v3.x，systemd `x-ui` |
| 内核 | **Xray 26.6.27**（路径 `/usr/local/x-ui/bin/xray-linux-amd64`） |
| 入站 | 一条：VLESS + REALITY + TCP **443**，flow `xtls-rprx-vision` |
| dest / SNI | `www.cloudflare.com`（不要用空的 `minClientVer`） |
| `minClientVer` | 显式 `1.0.0` | Xray 26.7.x 若留空会默认 `26.3.27`，Hiddify/sing-box/mihomo 表现为 `reality verification failed` |
| 订阅服务 | 面板 `2096`，路径 `/sub/`，明文（`subEncrypt=false`） |
| 管理面板 | `2053` + 随机 base path | 完整 URL 与账号只在 VPS `/etc/x-ui/install-result.env` |
| 二进制备份 | `xray-linux-amd64.bak-26.7.28` | 曾装 26.7.28，因第三方内核不兼容而降回 |

**不要**在未改 `minClientVer=1.0.0` 的情况下把内核升到 26.7.x。升内核后必须 `x-ui restart` 并确认 `config.json` 里仍有 `minClientVer` 与两个 client 的 `flow`。

### 客户端（同一入站，两个 UUID）

| 3x-ui email | 用途 | 枢纽侧名称 |
|--------------|------|------------|
| `wzc` | 本机 Hiddify 等个人客户端 | 不进 mihomo |
| `node3` | 集群枢纽出站 | `vless-bwg-node3`，provider `bwg-node3` |

增客户端：在 3x-ui 同一 inbound 上加 client + `flow_override=xtls-rprx-vision`，**不要**再开一条 443 入站。然后 `x-ui restart`，确认 `/usr/local/x-ui/bin/config.json` 的 `clients` 数组变长。

REALITY 公钥、shortId、UUID、订阅 ID 以面板/数据库为准，不写入本文。

---

## 3. 与枢纽 mihomo 的对接

配置文件：`/etc/mihomo/config.yaml`（`640`，含密钥）。

| 项 | 现状 |
|----|------|
| 默认 `PROXY` | `vless-bwg-node3`（本 VPS） |
| 备用 | 原静态 `vless-35102`；机场 `SUB-AUTO` |
| provider | `bwg-node3` → 本 VPS 订阅（`proxy: DIRECT`）；种子文件 `/var/lib/mihomo/providers/bwg-node3.yaml` |
| 直连该 VPS | `IP-CIDR,23.106.154.45/32,DIRECT`（避免系统代理套娃） |
| 分流 | 仍为 Loyalsoldier `rule-providers`（jsdelivr，`proxy: DIRECT`） |

面板订阅在 UA=`clash.meta` 时仍可能返回 `vless://` 单行，而不是 Clash YAML。因此 **静态节点 + 本地 provider 文件** 必须保留；不要只依赖 HTTP provider 自动转换。

改出站后：

```bash
systemctl restart mihomo
# 确认默认节点（9090 仅本机，需 secret）
curl -sS -H "Authorization: Bearer <secret>" http://127.0.0.1:9090/proxies/PROXY
curl -sS -x http://127.0.0.1:7890 https://api.ipify.org   # 期望 23.106.154.45
```

API `secret` 在 `config.yaml`，不要贴进文档。

---

## 4. 本机 Hiddify（对照枢纽规则）

个人流量走客户端 `wzc`，**不要**用 `node3` 的 UUID。规则应对齐枢纽：国内/苹果/iCloud 直连，Google、GFW、非国内 TLD、Telegram 走代理；`23.106.154.45` 直连。

Clash 规则副本（不含集群密钥）：枢纽文档机上的 Hiddify 目录 `node3-rules-clash.yaml` 由管理员在工作站维护。Hiddify 图形界面里换订阅再连接会覆盖 raw 配置，需要时按副本重新导入。

日志：`~/Library/Application Support/app.hiddify.com/data/box.log`。`outbound/direct` 为直连，`outbound/vless` 为走节点。

---

## 5. 端口与防火墙（VPS）

| 端口 | 进程 | 暴露 |
|------|------|------|
| 22 | sshd | 公钥登录 |
| 443 | xray REALITY | 公网入站 |
| 2053 | 3x-ui 面板 | 公网但依赖秘密路径；勿写入用户文档 |
| 2096 | 订阅 | HTTP；勿对无关方传播 URL |

集群 **7890 不得**映射到这台 VPS。计算节点只连 `10.200.1.3:7890`。

---

## 6. 验收与排障

| 检查 | 期望 |
|------|------|
| `ssh -i ~/.ssh/id_rsa_banwagong -o IdentitiesOnly=yes root@23.106.154.45` | 免密进入 |
| VPS `ss` | `*:443` 为 xray；`x-ui` 在 2053/2096 |
| `xray-linux-amd64 version` | 26.6.27 |
| `config.json` clients | 含 `wzc` 与 `node3`，均有 `flow` |
| REALITY | `minClientVer` 为 `1.0.0`；dest 为 `www.cloudflare.com:443` |
| 枢纽出口 | `curl -x http://10.200.1.3:7890 https://api.ipify.org` → `23.106.154.45` |
| 国内站 | 枢纽规则下百度等应 `DIRECT`，不应消耗 VPS 月流量 |

| 现象 | 处理要点 |
|------|----------|
| `reality verification failed` | 核对 SNI/pbk/sid/flow；Xray≥26.7 检查 `minClientVer` |
| Hiddify 一直超时 | 系统代理不要把 `23.106.154.45` 再送进 `127.0.0.1:12334`；更新订阅 |
| 枢纽仍出旧 IP | `PROXY` 未选中 `vless-bwg-node3`；用 Clash API `PUT` 或重启后确认 `now` |
| KiwiVM 登录失败 | 网页密码 ≠ root 密码 |
| 月流量耗尽 | 只看 KiwiVM，不看 3x-ui `total_gb` |

---

## 7. 日常

| 动作 | 做法 |
|------|------|
| 看套餐流量 | KiwiVM → Bandwidth / usage |
| 看面板流量 | 3x-ui inbound / client 统计（非合同配额） |
| 重启中继 | VPS：`x-ui restart` |
| 重启集群入口 | 枢纽：`systemctl restart mihomo` |
| 换 REALITY dest | 改 inbound `stream_settings` 后重启；客户端必须更新订阅（SNI 一并变） |
