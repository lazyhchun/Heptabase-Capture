# Drafts Actions — 通用版 (Mac + iPhone)

通过 HTTP.request 直接调用 Heptabase MCP API，**不依赖 Python**。
Token 存储在 Drafts 的 archived Draft 中，通过 iCloud 自动同步到所有设备。

## 前提条件

需要先在 Mac 上完成一次 Python 授权，生成 `token.json`：

```bash
python3 ~/.config/heptabase-local/heptabase_auth.py
```

## 创建 Actions

在 Drafts 中为以下每个脚本创建一个 Action：

| Action 名称 | 脚本文件 | 功能 |
|---|---|---|
| Heptabase Setup | `heptabase_setup.js` | 导入 Token（首次 + 过期后） |
| Append to Journal | `heptabase_journal.js` | 追加内容到今日日志 |
| Save to Card | `heptabase_card.js` | 保存内容为笔记卡片 |

**创建步骤：**
1. Drafts → Manage Actions → + 新建 Action
2. 添加步骤 → Script
3. 粘贴对应 `.js` 文件的全部内容
4. 保存

## 首次使用

1. 先在 Mac 上运行 **Heptabase Setup** Action
   - Mac 会自动读取 `~/.config/heptabase-local/token.json`
   - iPhone 需要手动粘贴 token.json 内容（从 Mac 复制）
2. Token 会保存到 archived Draft，通过 iCloud 自动同步

## 日常使用

1. 在 Drafts 中写好内容
2. 运行对应 Action
3. 显示 ✅ 即成功

## 与 `drafts/` 的区别

| | `drafts/` (Mac 版) | `drafts-universal/` (通用版) |
|---|---|---|
| 平台 | 仅 Mac | Mac + iPhone |
| 依赖 | Python 后端 | 无（纯 HTTP 请求） |
| Token 来源 | Python 直接调用 | Drafts archived Draft (iCloud 同步) |
