#!/usr/bin/env python3
"""
Heptabase OAuth 2.1 + PKCE 一次性授权脚本

运行方式:
    python3 heptabase_auth.py

流程:
    1. 发现 OAuth 端点
    2. 动态客户端注册
    3. 生成 PKCE code_verifier + code_challenge
    4. 启动临时本地 HTTP 服务器
    5. 打开浏览器进行授权
    6. 接收 callback，交换 token
    7. 保存 token.json
"""

import hashlib
import base64
import secrets
import json
import os
import sys
import socket
import time
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# ── 路径 ──────────────────────────────────────────────
CONFIG_DIR = os.path.expanduser("~/.config/heptabase-local")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")

# ── OAuth 端点 ────────────────────────────────────────
WELL_KNOWN_URL = "https://api.heptabase.com/.well-known/oauth-authorization-server"
SCOPES = "openid profile email space:read space:write offline_access"


def _find_free_port() -> int:
    """找一个可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _discover_endpoints() -> dict:
    """GET well-known 端点，返回 {authorization_endpoint, token_endpoint, registration_endpoint}"""
    req = urllib.request.Request(WELL_KNOWN_URL)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _register_client(registration_endpoint: str, redirect_uri: str) -> str:
    """动态客户端注册，返回 client_id"""
    payload = json.dumps({
        "client_name": "Heptabase-Local-Tools",
        "redirect_uris": [redirect_uri],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }).encode()

    req = urllib.request.Request(
        registration_endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data["client_id"]


def _generate_pkce() -> tuple:
    """生成 PKCE code_verifier 和 code_challenge (S256)"""
    code_verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


def _exchange_token(token_endpoint: str, client_id: str,
                    code: str, code_verifier: str, redirect_uri: str) -> dict:
    """用 authorization code 交换 access_token + refresh_token"""
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode()

    req = urllib.request.Request(
        token_endpoint,
        data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _save_token(client_id: str, token_data: dict) -> None:
    """保存 token 到 token.json"""
    os.makedirs(CONFIG_DIR, exist_ok=True)

    expires_in = token_data.get("expires_in", 3600)
    to_save = {
        "client_id": client_id,
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", ""),
        "expires_at": int(time.time()) + expires_in,
    }
    with open(TOKEN_PATH, "w") as f:
        json.dump(to_save, f, indent=2)


def main() -> None:
    print("🔐 Heptabase OAuth 授权")
    print("=" * 40)

    # 1. 发现 OAuth 端点
    print("→ 发现 OAuth 端点...")
    endpoints = _discover_endpoints()
    auth_endpoint = endpoints["authorization_endpoint"]
    token_endpoint = endpoints["token_endpoint"]
    reg_endpoint = endpoints.get("registration_endpoint")

    if not reg_endpoint:
        print("❌ 服务器不支持动态客户端注册", file=sys.stderr)
        sys.exit(1)

    # 2. 找可用端口 & 构建 redirect_uri
    port = _find_free_port()
    redirect_uri = f"http://127.0.0.1:{port}/callback"

    # 3. 动态客户端注册
    print("→ 注册客户端...")
    client_id = _register_client(reg_endpoint, redirect_uri)
    print(f"  client_id: {client_id[:16]}...")

    # 4. 生成 PKCE
    code_verifier, code_challenge = _generate_pkce()

    # 5. 构建授权 URL
    auth_params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    })
    auth_url = f"{auth_endpoint}?{auth_params}"

    # 6. 启动临时 HTTP 服务器接收 callback
    received_code = [None]  # 用 list 使内部函数可修改
    received_error = [None]

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if parsed.path == "/callback":
                if "code" in params:
                    received_code[0] = params["code"][0]
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        "<!DOCTYPE html><html><body>"
                        "<h2>✅ 授权成功！</h2>"
                        "<p>你可以关闭此窗口并返回终端。</p>"
                        "</body></html>".encode()
                    )
                elif "error" in params:
                    received_error[0] = params.get("error_description",
                                                    params["error"])[0]
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        f"<!DOCTYPE html><html><body>"
                        f"<h2>❌ 授权失败</h2>"
                        f"<p>{received_error[0]}</p>"
                        f"</body></html>".encode()
                    )
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            """静默日志"""
            pass

    server = HTTPServer(("127.0.0.1", port), CallbackHandler)

    # 在后台线程启动服务器，等待一次请求
    def serve_once():
        server.handle_request()

    thread = Thread(target=serve_once, daemon=True)
    thread.start()

    # 7. 打开浏览器
    print(f"→ 打开浏览器进行授权...")
    print(f"  如果浏览器没有自动打开，请手动访问：")
    print(f"  {auth_url}")
    webbrowser.open(auth_url)

    # 等待 callback
    print("→ 等待授权回调...")
    thread.join(timeout=300)  # 最多等 5 分钟
    server.server_close()

    if received_error[0]:
        print(f"❌ 授权失败: {received_error[0]}", file=sys.stderr)
        sys.exit(1)

    if not received_code[0]:
        print("❌ 超时：未收到授权回调", file=sys.stderr)
        sys.exit(1)

    # 8. 交换 token
    print("→ 交换 Token...")
    token_data = _exchange_token(
        token_endpoint, client_id,
        received_code[0], code_verifier, redirect_uri,
    )

    # 9. 保存
    _save_token(client_id, token_data)
    print(f"→ Token 已保存到 {TOKEN_PATH}")
    print()
    print("✅ 授权成功！你现在可以使用 PopClip 和 Drafts 追加日志了。")


if __name__ == "__main__":
    main()
