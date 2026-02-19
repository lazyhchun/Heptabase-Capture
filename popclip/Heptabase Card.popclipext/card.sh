#!/bin/bash
# Heptabase Note Card — PopClip Shell Script
# 将选中文字保存为 Heptabase 笔记卡片

CONFIG_DIR="$HOME/.config/heptabase-local"
TOKEN_FILE="$CONFIG_DIR/token.json"
CARD_SCRIPT="$CONFIG_DIR/heptabase_card.py"

# ── 检查 Python 脚本是否已安装 ──
if [ ! -f "$CARD_SCRIPT" ]; then
    echo "❌ 未安装: 请先将 Python 脚本复制到 $CONFIG_DIR"
    exit 1
fi

# ── 检查是否已授权 ──
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ 未授权: 请在终端运行 python3 $CONFIG_DIR/heptabase_auth.py"
    exit 1
fi

# ── 保存为卡片 ──
echo "$POPCLIP_TEXT" | /usr/bin/python3 "$CARD_SCRIPT"
