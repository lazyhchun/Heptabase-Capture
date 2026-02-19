# Drafts Actions (Mac)

将 Heptabase 内容捕获集成到 Drafts App。  
通过 Python 后端调用 API，与 PopClip 使用相同的方式。

## 前提条件

需要先完成 Python 后端安装和授权，参见项目根目录 README。

## 创建 Actions

在 Drafts 中为以下每个脚本创建一个 Action：

| Action 名称 | 脚本文件 | 功能 |
|---|---|---|
| Heptabase Setup | `heptabase_setup.js` | 运行 Python 授权（首次使用） |
| Append to Journal | `heptabase_journal.js` | 追加内容到今日日志 |
| Save to Card | `heptabase_card.js` | 保存内容为笔记卡片 |

**创建步骤：**
1. Drafts → Manage Actions → + 新建 Action
2. 添加步骤 → Script
3. 粘贴对应 `.js` 文件的全部内容
4. 保存

## 日常使用

1. 在 Drafts 中写好内容
2. 运行对应 Action
3. 显示 ✅ 即成功

> **注意：** 仅支持 Mac，因为依赖 ShellScript 调用 Python 后端。
