# Python 后端

PopClip 插件的本地 Python 后端，仅使用 Python 3 标准库，无需安装额外依赖。

## 安装

```bash
mkdir -p ~/.config/heptabase-local
cp *.py ~/.config/heptabase-local/
```

## 首次授权

```bash
python3 ~/.config/heptabase-local/heptabase_auth.py
```

浏览器会自动打开 Heptabase 授权页，授权后 Token 保存到 `~/.config/heptabase-local/token.json`。

## 文件说明

| 文件 | 说明 |
|---|---|
| `heptabase_auth.py` | OAuth 2.1 + PKCE 授权流程（运行一次） |
| `heptabase_api.py` | Token 管理 + MCP JSON-RPC 2.0 调用核心 |
| `heptabase_append.py` | CLI 入口：追加内容到今日日志 |
| `heptabase_card.py` | CLI 入口：保存内容为笔记卡片 |

## 命令行使用

```bash
# 追加到日志
echo "今天的笔记" | python3 ~/.config/heptabase-local/heptabase_append.py

# 保存为卡片（第一行自动作为标题）
echo "卡片标题\n卡片内容" | python3 ~/.config/heptabase-local/heptabase_card.py
```
