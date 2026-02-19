#!/bin/bash
# Heptabase Journal — PopClip Shell Script
# 将选中文字追加到 Heptabase 今日日志

CONFIG_DIR="$HOME/.config/heptabase-local"
TOKEN_FILE="$CONFIG_DIR/token.json"
APPEND_SCRIPT="$CONFIG_DIR/heptabase_append.py"

# ── 检查 Python 脚本是否已安装 ──
if [ ! -f "$APPEND_SCRIPT" ]; then
    echo "❌ 未安装: 请先将 Python 脚本复制到 $CONFIG_DIR"
    echo "运行: mkdir -p $CONFIG_DIR && cp heptabase_*.py $CONFIG_DIR/"
    exit 1
fi

# ── 检查是否已授权（token.json 存在） ──
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ 未授权: 请在终端运行以下命令完成首次授权"
    echo "python3 $CONFIG_DIR/heptabase_auth.py"
    exit 1
fi

# ── 发送内容 ──
echo "$POPCLIP_TEXT" | /usr/bin/python3 "$APPEND_SCRIPT"
