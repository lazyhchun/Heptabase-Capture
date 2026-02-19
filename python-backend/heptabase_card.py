#!/usr/bin/env python3
"""
Heptabase 保存笔记卡片入口脚本

用法:
    echo "卡片内容" | python3 heptabase_card.py
    python3 heptabase_card.py "卡片标题\n卡片内容"

第一行作为卡片标题（自动添加 # 前缀）。
成功输出 OK 到 stdout，失败输出错误到 stderr 并 exit(1)。
"""

import sys
import os

# 确保可以 import 同目录下的 heptabase_api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from heptabase_api import save_to_note_card


def main() -> None:
    # 从命令行参数或 stdin 读取内容
    if len(sys.argv) > 1:
        content = " ".join(sys.argv[1:])
    else:
        content = sys.stdin.read()

    content = content.strip()

    if not content:
        print("错误: 内容为空", file=sys.stderr)
        sys.exit(1)

    try:
        save_to_note_card(content)
        print("OK")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
