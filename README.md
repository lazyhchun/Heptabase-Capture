# Heptabase Capture Tools

快速将内容保存到 Heptabase 的本地工具集。

## 前置条件

### 必需

- [Heptabase](https://heptabase.com/) 账号（需要 API 访问权限）
- macOS（首次 OAuth 授权必须在 Mac 上完成）
- Python 3.7+（系统自带或通过 [python.org](https://www.python.org/downloads/) 安装）

### 可选（根据你选择的客户端）

- [PopClip](https://www.popclip.app/)（macOS 付费应用）
- [Drafts](https://getdrafts.com/)（Mac / iPhone）
- Apple 快捷指令（iPhone 内置）

## Python 依赖

本项目 **仅使用 Python 标准库**，无需安装任何第三方包。

用到的标准库模块：

| 模块 | 用途 |
|---|---|
| `urllib` | HTTP 请求（API 调用、OAuth 流程） |
| `json` | Token 和 API 数据解析 |
| `hashlib` / `base64` / `secrets` | PKCE 授权流程 |
| `http.server` | OAuth 回调本地服务器 |
| `webbrowser` | 自动打开浏览器进行授权 |
| `socket` / `threading` | 本地服务器端口管理 |

## 目录结构

```
heptabase-capture/
├── python-backend/                # Python 后端（核心依赖）
│   ├── heptabase_auth.py          # OAuth 授权（运行一次）
│   ├── heptabase_api.py           # API 核心模块
│   ├── heptabase_append.py        # CLI：追加到日志
│   └── heptabase_card.py          # CLI：保存为卡片
│
├── popclip/                       # PopClip 插件（macOS）
│   ├── Heptabase Journal.popclipext/
│   └── Heptabase Card.popclipext/
│
├── drafts/                        # Drafts Actions（仅 Mac，调用 Python）
│   ├── heptabase_setup.js
│   ├── heptabase_journal.js
│   └── heptabase_card.js
│
├── drafts-universal/              # Drafts Actions（Mac + iPhone，HTTP 直连）
│   ├── heptabase_setup.js         # 导入 Token
│   ├── heptabase_journal.js       # 追加到今日日志
│   └── heptabase_card.js          # 保存为笔记卡片
│
└── shortcuts/                     # Apple 快捷指令（iPhone）
    └── README.md                  # 创建步骤指南
```

## 快速开始

### 1. 安装 Python 后端并授权

```bash
mkdir -p ~/.config/heptabase-local
cp python-backend/*.py ~/.config/heptabase-local/
python3 ~/.config/heptabase-local/heptabase_auth.py
```

> **安全提示**：授权完成后，Token 文件保存在 `~/.config/heptabase-local/token.json`。建议设置目录权限以防止其他用户访问：
>
> ```bash
> chmod 700 ~/.config/heptabase-local
> ```
>
> 请勿将 `token.json` 提交到版本控制或分享给他人。Token 过期后会自动刷新，无需手动干预。

### 2. 选择客户端

| 客户端 | 平台 | 状态 | 说明 |
|---|---|---|---|
| **PopClip** | macOS | ✅ 可用 | 选中文字 → 点击按钮，详见 [popclip/README.md](popclip/README.md) |
| **Drafts**（Mac版） | macOS | ✅ 可用 | 调用 Python 后端，详见 [drafts/README.md](drafts/README.md) |
| **Drafts**（通用版） | Mac + iPhone | ✅ 可用 | HTTP 直连 MCP API，详见 [drafts-universal/README.md](drafts-universal/README.md) |
| **快捷指令** | iPhone | ⚠️ 未测试 | 获取URL内容 → MCP API，详见 [shortcuts/README.md](shortcuts/README.md) |

## 功能

- **追加到今日日志**：将文本追加到 Heptabase 当天的 Journal
- **保存为笔记卡片**：将文本保存为 Heptabase 的 Note Card（第一行为标题）

## 故障排查

### OAuth 授权失败

- 确认 Python 版本 ≥ 3.7：`python3 --version`
- 确认网络可以访问 `api.heptabase.com`
- 授权过程中浏览器会自动打开，请勿关闭终端窗口
- 如果端口被占用，脚本会自动尝试其他可用端口

### PopClip / Drafts 无法调用 Python

- 确认脚本已复制到 `~/.config/heptabase-local/` 目录
- 确认 `token.json` 存在且未过期（脚本会自动刷新）
- 在终端中手动运行 `python3 ~/.config/heptabase-local/heptabase_append.py "测试"` 验证

### Drafts Universal 无法连接 API

- 确认已在 Drafts 中运行 Setup Action 并正确导入 Token
- 确认设备网络正常，可以访问 `https://api.heptabase.com/mcp`

## 已知限制

- 首次授权必须在 Mac 上完成（Python OAuth 流程）
- 日志日期由 Heptabase 服务器决定，凌晨时段可能显示为前一天（UTC 时区）

## 贡献

欢迎提交 Issue 和 Pull Request！

如果你在使用过程中遇到问题或有功能建议，请通过 [Issues](https://github.com/lazyhchun/Heptabase-Capture/issues) 反馈。

## 许可证

[MIT](LICENSE)
