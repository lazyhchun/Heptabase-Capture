# Heptabase Capture Tools

快速将内容保存到 Heptabase 的本地工具集。

## 目录结构

```
heptabase-capture/
├── python-backend/              # Python 后端 (核心依赖)
│   ├── heptabase_auth.py        # OAuth 授权 (运行一次)
│   ├── heptabase_api.py         # API 核心模块
│   ├── heptabase_append.py      # CLI: 追加到日志
│   └── heptabase_card.py        # CLI: 保存为卡片
│
├── popclip/                     # PopClip 插件 (macOS)
│   ├── Heptabase Journal.popclipext/
│   └── Heptabase Card.popclipext/
│
├── drafts/                      # Drafts Actions (仅 Mac, 调用 Python)
│   ├── heptabase_setup.js
│   ├── heptabase_journal.js
│   └── heptabase_card.js
│
└── drafts-universal/            # Drafts Actions (Mac + iPhone, HTTP 直连)
    ├── heptabase_setup.js       # 导入 Token
    ├── heptabase_journal.js     # 追加到今日日志
    └── heptabase_card.js        # 保存为笔记卡片

└── shortcuts/                   # Apple 快捷指令 (iPhone)
    └── README.md                # 创建步骤指南
```

## 快速开始

### 1. 安装 Python 后端并授权

```bash
mkdir -p ~/.config/heptabase-local
cp python-backend/*.py ~/.config/heptabase-local/
python3 ~/.config/heptabase-local/heptabase_auth.py
```

### 2. 选择客户端

| 客户端 | 平台 | 说明 |
|---|---|---|
| **PopClip** | macOS | 选中文字 → 点击按钮，详见 [popclip/README.md](popclip/README.md) |
| **Drafts** (Mac版) | macOS | 调用 Python 后端，详见 [drafts/README.md](drafts/README.md) |
| **Drafts** (通用版) | Mac + iPhone | HTTP 直连 MCP API，详见 [drafts-universal/README.md](drafts-universal/README.md) |
| **快捷指令** | iPhone | 获取URL内容 → MCP API，详见 [shortcuts/README.md](shortcuts/README.md) |

## 功能

- **追加到今日日志**：将文本追加到 Heptabase 当天的 Journal
- **保存为笔记卡片**：将文本保存为 Heptabase 的 Note Card（第一行为标题）

## 已知限制

- 首次授权必须在 Mac 上完成（Python OAuth 流程）
- 日志日期由 Heptabase 服务器决定，凌晨时段可能显示为前一天（UTC 时区）
