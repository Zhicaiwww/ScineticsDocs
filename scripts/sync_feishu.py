#!/usr/bin/env python3
"""把仓库内 Markdown 导入/更新到飞书知识库。

首次：云空间导入 md → 迁入知识库，并把 token 写入 feishu-mapping.json。
再次：删除旧 wiki 节点后重新导入（飞书没有稳定的「整篇 md 覆盖」接口）。

需要环境变量：FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_SPACE_ID。
可选：FEISHU_PARENT_NODE_TOKEN。
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "feishu-mapping.json"
API = os.environ.get("FEISHU_ENDPOINT", "https://open.feishu.cn").rstrip("/")
SKIP_DIRS = {".git", ".github", "scripts", "__pycache__"}


def req(method: str, url: str, token: str | None = None, body: dict | bytes | None = None, content_type: str | None = None):
    data = None
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if isinstance(body, dict):
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json; charset=utf-8"
    elif isinstance(body, (bytes, bytearray)):
        data = body
        if content_type:
            headers["Content-Type"] = content_type
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw.decode() or "{}")
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} -> {e.code}: {err}") from e


def tenant_token(app_id: str, secret: str) -> str:
    out = req(
        "POST",
        f"{API}/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": app_id, "app_secret": secret},
    )
    token = out.get("tenant_access_token")
    if not token:
        raise RuntimeError(f"get tenant_access_token failed: {out}")
    return token


def iter_markdown() -> list[Path]:
    files = []
    for p in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        files.append(p)
    return sorted(files)


def upload_md(token: str, path: Path) -> str:
    size = path.stat().st_size
    name = path.name
    prep = req(
        "POST",
        f"{API}/open-apis/drive/v1/medias/upload_all",
        token,
        body={
            "file_name": name,
            "parent_type": "explorer",
            "size": str(size),
        },
    )
    # Some tenants use /drive/v1/files/upload_all. Prefer media upload_prepare + upload.
    # Fallback: files upload_all multipart is more portable.
    raise NotImplementedError(prep)


def upload_file_multipart(token: str, path: Path) -> str:
    boundary = "----wzcDocsBoundary"
    file_name = path.name
    payload = path.read_bytes()
    parts = []

    def add(name: str, value: str):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )

    add("file_name", file_name)
    add("parent_type", "explorer")
    add("size", str(len(payload)))
    parts.append(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{file_name}\"\r\n"
            "Content-Type: text/markdown\r\n\r\n"
        ).encode()
        + payload
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    out = req(
        "POST",
        f"{API}/open-apis/drive/v1/files/upload_all",
        token,
        body=body,
        content_type=f"multipart/form-data; boundary={boundary}",
    )
    if out.get("code") not in (0, None) and "data" not in out:
        raise RuntimeError(f"upload failed: {out}")
    data = out.get("data") or {}
    file_token = data.get("file_token") or data.get("token")
    if not file_token:
        raise RuntimeError(f"upload missing token: {out}")
    return file_token


def import_md(token: str, file_token: str) -> str:
    out = req(
        "POST",
        f"{API}/open-apis/drive/v1/import_tasks",
        token,
        body={
            "file_extension": "md",
            "file_token": file_token,
            "type": "docx",
            "point": {"mount_type": 1, "mount_key": ""},
        },
    )
    ticket = (out.get("data") or {}).get("ticket")
    if not ticket:
        raise RuntimeError(f"import_tasks failed: {out}")
    for _ in range(30):
        time.sleep(1)
        st = req("GET", f"{API}/open-apis/drive/v1/import_tasks/{ticket}", token)
        data = st.get("data") or {}
        result = data.get("result") or {}
        job = data.get("job_status")
        if job == 0:
            doc_token = result.get("token")
            if not doc_token:
                raise RuntimeError(f"import done without token: {st}")
            return doc_token
        if job not in (1, 2, None) and job != 0:
            # 1/2 often mean pending depending on API version
            extra = data.get("job_error_msg") or st
            if job not in (1, 2):
                raise RuntimeError(f"import failed: {st}")
    raise RuntimeError("import timeout")


def wiki_move(token: str, space_id: str, doc_token: str, parent: str) -> str:
    body = {
        "obj_type": "docx",
        "obj_token": doc_token,
        "parent_wiki_token": parent or "",
    }
    out = req(
        "POST",
        f"{API}/open-apis/wiki/v2/spaces/{space_id}/nodes/move_docs_to_wiki",
        token,
        body=body,
    )
    data = out.get("data") or {}
    wiki_token = data.get("wiki_token")
    if wiki_token:
        return wiki_token
    task_id = data.get("task_id")
    if not task_id:
        raise RuntimeError(f"move_docs_to_wiki failed: {out}")
    for _ in range(30):
        time.sleep(1)
        st = req("GET", f"{API}/open-apis/wiki/v2/tasks/{task_id}", token)
        wiki_token = (st.get("data") or {}).get("wiki_token") or (
            (st.get("data") or {}).get("task") or {}
        ).get("wiki_token")
        if wiki_token:
            return wiki_token
    raise RuntimeError(f"wiki move timeout: {task_id}")


def wiki_delete(token: str, space_id: str, wiki_token: str) -> None:
    try:
        req(
            "DELETE",
            f"{API}/open-apis/wiki/v2/spaces/{space_id}/nodes/{wiki_token}",
            token,
        )
    except RuntimeError as e:
        print(f"warn: delete wiki node {wiki_token}: {e}", file=sys.stderr)


def main() -> int:
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    space_id = os.environ.get("FEISHU_SPACE_ID", "").strip()
    parent = os.environ.get("FEISHU_PARENT_NODE_TOKEN", "").strip()
    if not all([app_id, secret, space_id]):
        print(
            "缺少 FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_SPACE_ID。\n"
            "在飞书开放平台建自建应用，开通云文档/知识库权限，把应用机器人加成知识库成员。\n"
            "凭证放进 GitHub Secrets，不要写入仓库。",
            file=sys.stderr,
        )
        return 2

    token = tenant_token(app_id, secret)
    mapping = {}
    if MAPPING_PATH.exists():
        mapping = json.loads(MAPPING_PATH.read_text() or "{}")

    files = iter_markdown()
    if not files:
        print("no markdown files")
        return 0

    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        print(f"sync {rel}")
        old = mapping.get(rel) or {}
        if old.get("wiki_token"):
            wiki_delete(token, space_id, old["wiki_token"])
        file_token = upload_file_multipart(token, path)
        doc_token = import_md(token, file_token)
        wiki_token = wiki_move(token, space_id, doc_token, parent)
        mapping[rel] = {
            "doc_token": doc_token,
            "wiki_token": wiki_token,
            "title": path.stem,
        }

    MAPPING_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {MAPPING_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
