#!/usr/bin/env python3
"""
Heptabase API 模块 — Token 管理 + MCP JSON-RPC 2.0 调用

供 heptabase_append.py（和其他脚本）import 使用。
仅使用 Python 3 标准库。
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

# ── 常量 ──────────────────────────────────────────────
CONFIG_DIR = os.path.expanduser("~/.config/heptabase-local")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
MCP_URL = "https://api.heptabase.com/mcp"
TOKEN_URL = "https://api.heptabase.com/token"

# Token 提前 60 秒视为过期，留出余量
TOKEN_EXPIRY_BUFFER = 60


# ── Token 管理 ────────────────────────────────────────

def load_token() -> dict:
    """从 token.json 读取 token 数据"""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(
            f"token.json 不存在，请先运行 heptabase_auth.py 进行授权\n"
            f"  python3 {os.path.join(CONFIG_DIR, 'heptabase_auth.py')}"
        )
    with open(TOKEN_PATH, "r") as f:
        return json.load(f)


def save_token(data: dict) -> None:
    """写回 token.json"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)


def refresh_if_needed(token_data: dict) -> dict:
    """
    检查 token 是否过期，过期则用 refresh_token 刷新。
    返回（可能已更新的）token_data。
    """
    expires_at = token_data.get("expires_at", 0)

    if time.time() < expires_at - TOKEN_EXPIRY_BUFFER:
        # 尚未过期
        return token_data

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("Token 已过期且无 refresh_token，请重新授权")

    client_id = token_data.get("client_id", "")

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            new_data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"Token 刷新失败 ({e.code}): {body}")

    # 更新 token_data
    token_data["access_token"] = new_data["access_token"]
    token_data["expires_at"] = int(time.time()) + new_data.get("expires_in", 3600)

    # 服务端可能不返回新的 refresh_token，保留旧值
    if "refresh_token" in new_data:
        token_data["refresh_token"] = new_data["refresh_token"]

    save_token(token_data)
    return token_data


# ── MCP 调用 ──────────────────────────────────────────

def _mcp_request(access_token: str, method: str, params: dict) -> dict:
    """
    发送 MCP JSON-RPC 2.0 请求，处理 JSON 或 SSE 响应。
    """
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }).encode()

    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream;q=0.1",
            "Authorization": f"Bearer {access_token}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read().decode()

    # 解析响应
    if "text/event-stream" in content_type:
        # SSE 格式：逐行找 data: 前缀
        for line in body.splitlines():
            if line.startswith("data: "):
                json_str = line[6:]  # 去掉 "data: "
                mcp_resp = json.loads(json_str)
                break
        else:
            raise RuntimeError(f"SSE 响应中未找到 data: 行:\n{body}")
    else:
        # 普通 JSON
        mcp_resp = json.loads(body)

    # 检查 JSON-RPC error
    if "error" in mcp_resp and mcp_resp["error"]:
        err = mcp_resp["error"]
        raise RuntimeError(f"MCP 错误 ({err.get('code', '?')}): {err.get('message', '未知错误')}")

    return mcp_resp.get("result", {})


def _call_tool(tool_name: str, arguments: dict) -> dict:
    """
    通用 MCP tool 调用。

    完整流程：
    1. 加载 token
    2. 刷新 token（如果过期）
    3. POST JSON-RPC 调用指定 tool
    4. 401 时刷新 token 后重试一次

    Returns:
        MCP 响应的 result 字段
    """
    token_data = load_token()
    token_data = refresh_if_needed(token_data)

    params = {
        "name": tool_name,
        "arguments": arguments,
    }

    try:
        return _mcp_request(token_data["access_token"], "tools/call", params)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # Token 可能已失效，强制刷新后重试
            token_data["expires_at"] = 0  # 强制过期
            token_data = refresh_if_needed(token_data)
            return _mcp_request(token_data["access_token"], "tools/call", params)
        else:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"MCP 请求失败 ({e.code}): {body}")


def append_to_journal(content: str) -> dict:
    """追加内容到 Heptabase 今日日志。"""
    return _call_tool("append_to_journal", {"content": content})


def save_to_note_card(content: str) -> dict:
    """
    保存内容为 Heptabase 笔记卡片。

    第一行作为卡片标题，如果不以 '# ' 开头会自动添加。
    """
    content = content.strip()
    if not content.startswith("# "):
        lines = content.split("\n", 1)
        lines[0] = f"# {lines[0]}"
        content = "\n".join(lines)
    return _call_tool("save_to_note_card", {"content": content})

