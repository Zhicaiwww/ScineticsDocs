#!/usr/bin/env python3
"""本机弹出飞书登录，换取 user_access_token / refresh_token。

开放平台必须配置重定向 URL：
  http://127.0.0.1:8765/callback

权限里打开 offline_access，以及云文档 / 云空间 / 知识库（用户身份）。
凭证放仓库根目录 .env（已 gitignore），不要提交。
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATH = ROOT / ".feishu-user.json"
REDIRECT = "http://127.0.0.1:8765/callback"
SCOPES = " ".join(
    [
        "offline_access",
        "wiki:wiki",
        "docs:document",
        "docx:document",
        "drive:drive",
        "drive:file",
    ]
)


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def exchange(app_id: str, secret: str, code: str) -> dict:
    body = json.dumps(
        {
            "grant_type": "authorization_code",
            "client_id": app_id,
            "client_secret": secret,
            "code": code,
            "redirect_uri": REDIRECT,
        }
    ).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/authen/v2/oauth/token",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        out = json.loads(resp.read().decode())
    if out.get("code") not in (0, None) or not out.get("access_token"):
        raise RuntimeError(f"token exchange failed: {out}")
    return out


def main() -> int:
    load_env()
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    if not app_id or not secret:
        print("请在 .env 里填写 FEISHU_APP_ID 和 FEISHU_APP_SECRET，或 export 后再跑。", file=sys.stderr)
        return 2

    state = secrets.token_urlsafe(16)
    q = urllib.parse.urlencode(
        {
            "client_id": app_id,
            "response_type": "code",
            "redirect_uri": REDIRECT,
            "scope": SCOPES,
            "state": state,
        }
    )
    auth_url = f"https://accounts.feishu.cn/open-apis/authen/v1/authorize?{q}"
    holder: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("state", [""])[0] != state:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"state mismatch")
                holder["error"] = "state mismatch"
                return
            code = qs.get("code", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<html><body><p>授权完成，可以关闭此页回到终端。</p></body></html>".encode()
            )
            holder["code"] = code

    server = HTTPServer(("127.0.0.1", 8765), Handler)
    print("请在开放平台「安全设置 → 重定向 URL」加入：", REDIRECT)
    print("即将打开飞书授权页…")
    webbrowser.open(auth_url)
    while "code" not in holder and "error" not in holder:
        server.handle_request()
    if "error" in holder or not holder.get("code"):
        print("未拿到 authorization code", file=sys.stderr)
        return 1

    tokens = exchange(app_id, secret, holder["code"])
    TOKEN_PATH.write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n")
    os.chmod(TOKEN_PATH, 0o600)
    print(f"已写入 {TOKEN_PATH}")
    print("scope:", tokens.get("scope"))
    print("access_token 约", tokens.get("expires_in"), "秒后过期；refresh_token 约", tokens.get("refresh_token_expires_in"), "秒")
    print("下一步：python3 scripts/sync_feishu.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
