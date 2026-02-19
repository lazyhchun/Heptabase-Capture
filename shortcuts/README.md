# Apple 快捷指令 — Heptabase Capture (iPhone)

最简实现：用「获取URL内容」直接 POST 到 MCP API，和 PopClip/Drafts 同一原理。

## 前提

在 Mac 终端获取 access_token：

```bash
cat ~/.config/heptabase-local/token.json | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
```

复制输出的 token 备用。

---

## 快捷指令 1：追加到日志

创建步骤（iPhone 快捷指令 App）：

1. **接收** → 从「共享工作表」接收「文字」
2. **文本** → 写入以下 JSON（把 `YOUR_TOKEN` 替换为你的 token）：
   ```json
   {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"append_to_journal","arguments":{"content":"快捷指令输入"}}}
   ```
   > ⚠️ 关键：把 `快捷指令输入` 替换为变量「快捷指令输入」（点击文本中的位置 → 选择变量）
3. **获取URL内容**：
   - URL：`https://api.heptabase.com/mcp`
   - 方法：POST
   - 请求体：文件
   - 文件：选择上一步的「文本」
   - 头部：
     - `Content-Type` → `application/json`
     - `Accept` → `application/json, text/event-stream`
     - `Authorization` → `Bearer YOUR_TOKEN`
4. **显示通知** → `✅ 已追加到日志`

---

## 快捷指令 2：保存为卡片

和上面基本一样，只改 JSON：

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"save_to_note_card","arguments":{"content":"# 快捷指令输入"}}}
```

> 注意：卡片内容前加 `# ` 作为标题。

---

## Token 过期处理

access_token 有效期约 1 小时。过期后需要：
1. Mac 上运行 `python3 ~/.config/heptabase-local/heptabase_auth.py`（如果 refresh 也过期）
2. 或直接用 Python 刷新：
   ```bash
   python3 -c "
   import json, urllib.request, urllib.parse
   t = json.load(open('$HOME/.config/heptabase-local/token.json'))
   data = urllib.parse.urlencode({'client_id': t['client_id'], 'refresh_token': t['refresh_token'], 'grant_type': 'refresh_token'}).encode()
   r = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.heptabase.com/token', data)).read())
   t['access_token'] = r['access_token']
   json.dump(t, open('$HOME/.config/heptabase-local/token.json','w'))
   print(r['access_token'])
   "
   ```
3. 把新 token 更新到快捷指令的 Authorization 头部
