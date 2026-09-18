# 用户管理 · 运维规范

用户规范：[user.md](./user.md)。索引：[../README.md](../README.md)。

## 1. 开户

先保证实验室组存在（各节点 GID 必须同为 2000）：

```bash
groupadd -g 2000 lab
# 组已存在则跳过
```

`video`(44)、`render`(109) 为系统组，不要改 GID。

```bash
mkdir -p /nas/nas8/users
chmod 755 /nas/nas8/users

groupadd -g <uid> <name>
useradd -u <uid> -g <name> -d "/nas/nas8/users/<name>" -s /bin/bash \
  -G lab,video,render <name>
# 若目录已由管理员创建，不要使用 useradd -m
chmod u=rwx,go=rx "/nas/nas8/users/<name>"
# shared 保持全体可写（目录 1777 sticky）；勿把用户 HOME 设为他人可写
```

不要求预创建 `code/`、`envs/`。开户与授权公钥是两步：`useradd` 只写本机 `/etc/passwd`，sshd 仍要在该用户 `authorized_keys` 里看到对应公钥。见下一小节。

同一登录名必须在**所有要登录的节点**使用同一 UID 和同一登录组 GID。共享盘按数字鉴权，不按用户名。见第 2 节。

家目录已在 NAS 上时，在新节点开户只补本机账号映射，不要 `chown -R` 整棵家目录（除非确认属主错误）。

### 授权登录公钥

sshd 仅接受公钥（`PasswordAuthentication no`）。`$HOME/.ssh` 须为 `700`，`authorized_keys` 须为 `600`，属主为该用户。

**用户钥与 root 钥分开。** 实验室共用用户公钥注释为 `7-12-16`（指纹 `SHA256:W4cX544pGRfXGg07DETEObj6ZmXNGsphpubs2r5vjWw`），只写在各用户 `$HOME/.ssh/authorized_keys`。管理员 root 钥注释为 `cluster-root-admin`，**只写在四台 `/root/.ssh/authorized_keys`**，不要写入任何用户家目录。jumpserver、节点互信等其它 root 钥保留。

不要把 root 私钥放到使用者电脑或用户家目录。Cursor / ssh 日常 `User` 为本人账号；运维用单独的 root Host（本机 `node-*-root`）。

开户后将**用户公钥**追加到该用户 `authorized_keys`（已存在的同一公钥不重复）。使用者也可再追加本人电脑上的其它公钥。

对单个用户（以 `yjx` 为例），在枢纽以 root 执行（`USER_PUB` 为用户公钥文件，不是 root 钥）：

```bash
install -d -m 700 -o yjx -g yjx /nas/nas8/users/yjx/.ssh
umask 077
touch /nas/nas8/users/yjx/.ssh/authorized_keys
grep -F -q "$(awk '{print $1, $2}' "$USER_PUB")" /nas/nas8/users/yjx/.ssh/authorized_keys \
  || cat "$USER_PUB" >> /nas/nas8/users/yjx/.ssh/authorized_keys
chown yjx:yjx /nas/nas8/users/yjx/.ssh/authorized_keys
chmod 600 /nas/nas8/users/yjx/.ssh/authorized_keys
```

对 `/nas/nas8/users` 下已开户的全部登录名：

```bash
KEY_BODY=$(awk '{print $1, $2}' "$USER_PUB")
for home in /nas/nas8/users/*; do
  [ -d "$home" ] || continue
  name=$(basename "$home")
  getent passwd "$name" >/dev/null || continue
  install -d -m 700 -o "$name" -g "$name" "$home/.ssh"
  ak="$home/.ssh/authorized_keys"
  umask 077
  touch "$ak"
  grep -F -q "$KEY_BODY" "$ak" || cat "$USER_PUB" >> "$ak"
  chown "$name:$name" "$ak"
  chmod 600 "$ak"
done
```

检查（须用**用户**私钥，不能再用该钥登 root）：

```bash
ssh-keygen -lf /nas/nas8/users/yjx/.ssh/authorized_keys
ssh -o BatchMode=yes -o User=yjx node-3 'echo USER=$USER HOME=$HOME'
ssh -o BatchMode=yes -o User=root -i <用户私钥> node-3 true; echo "root 应失败"
```

预期：指纹列表含 `7-12-16`；用户钥可登本人账号，不能登 `root`。

## 2. 跨节点 UID

`/nas/nas8/users`、`/nas/nas1/shared` 等共享卷按 **UID/GID 数字** 做权限，不按登录名。

在 node3 创建 `wzc` 后，若在 node12 再执行不带 `-u` 的 `useradd wzc`，两台机器分到的 UID 通常不同。node3 上该账号写入的文件，在 node12 上不属于该节点的 `wzc`，表现为无法读取或无法写入。

**必须：** 先在一台机器上选定并记录 UID、GID，其余节点执行 `groupadd -g <gid> <name>`（组已存在则跳过）和 `useradd -u <uid> -g <gid> ...`。不要使用各节点自动分配的下一个空闲 UID。

`ls /nas/nas8/users` 把某目录显示成 `2101 2101` 而不是 `cqr cqr`，表示**当前节点**没有该登录名的 passwd 记录。磁盘属主数字仍正确；补开户后名字即恢复。

检查（每台要登录的节点上执行，数字必须一致）：

```bash
id wzc
getent passwd wzc
getent group wzc
getent group lab
```

`getent passwd <name>`：向本机账号库查询该登录名。无输出即本机未开户。`id` 同时列出附加组。

已冲突时：选定权威 UID/GID，确认该数字未被其他账号占用，再在错误节点上 `usermod -u` / `groupmod -g`，并对家目录 `chown -R <uid>:<gid>`。

### 第一批账号（权威数字）

下列数字为跨节点唯一依据。当前已在 `host-10-200-1-3`、`-7`、`-12`、`-16` 开户。

| 登录名 | UID | 主组 GID | 附加组 |
|--------|-----|----------|--------|
| `wzc` | 2100 | 2100 | `lab`、`video`、`render` |
| `cqr` | 2101 | 2101 | 同左 |
| `yjx` | 2102 | 2102 | 同左 |
| `xdc` | 2103 | 2103 | 同左 |
| `yzs` | 2104 | 2104 | 同左 |
| `xux` | 2105 | 2105 | 同左 |
| `lab`（组，非登录用户） | — | 2000 | — |

新节点按表逐个 `groupadd` / `useradd`，不要另分配数字。

## 3. 原则

| 规定 | 说明 |
|------|------|
| `$HOME`：`755`，属主本人 | 其它用户可读不可写 |
| `/nas/nas1/shared`：目录 `1777`，文件可全体读写 | 所有登录用户可写共享树 |
| 禁止 root 长期写入他人 `HOME` | 属主与审计清晰。开户时写入 `authorized_keys` 后属主仍为该用户 |
| 用户钥只写入用户 `authorized_keys`；root 钥只写入 `/root/.ssh` | 旧实验室钥不能再登 root |
| `data-workspace.sh` 只导出变量 | 不 chmod、不开户 |
| 代理与防火墙 | 见 [../network/outbound-proxy.dev.md](../network/outbound-proxy.dev.md) |
