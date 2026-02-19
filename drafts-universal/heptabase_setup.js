// ═══════════════════════════════════════════════════════════════
// Heptabase Setup — 导入 Token (Mac + iPhone)
// ═══════════════════════════════════════════════════════════════

var TOKEN_TAG = "heptabase-token";

function showMsg(title, msg) {
    var p = Prompt.create();
    p.title = title;
    // 用 textView 让内容可复制
    p.addTextView("info", "", msg, { height: 200 });
    p.addButton("确定");
    p.show();
}

function getTokenDraft() {
    var results = Draft.query("", "archive", [TOKEN_TAG]);
    if (results.length > 0) return results[0];
    results = Draft.query("", "inbox", [TOKEN_TAG]);
    if (results.length > 0) return results[0];
    return null;
}

function saveTokenToDraft(jsonStr) {
    try {
        var parsed = JSON.parse(jsonStr);
        if (!parsed.access_token) {
            showMsg("❌ 导入失败", "JSON 中缺少 access_token 字段。\n\n收到内容:\n" + jsonStr.substring(0, 200));
            return false;
        }
    } catch (e) {
        showMsg("❌ 导入失败", "无效的 JSON 格式: " + e.message + "\n\n收到内容:\n" + jsonStr.substring(0, 200));
        return false;
    }

    var d = getTokenDraft();
    if (!d) {
        d = new Draft();
        d.addTag(TOKEN_TAG);
    }
    d.content = jsonStr;
    d.update();
    if (!d.isArchived) {
        d.isArchived = true;
        d.update();
    }
    return true;
}

function tryReadFromFile() {
    if (typeof ShellScript === "undefined") return null;
    try {
        var cmd = ShellScript.create("/bin/sh -c 'cat \"$HOME/.config/heptabase-local/token.json\" 2>&1'");
        var success = cmd.execute();
        var output = cmd.standardOutput ? cmd.standardOutput.trim() : "";
        var errOutput = cmd.standardError ? cmd.standardError.trim() : "";

        if (success && output.length > 10) {
            return output;
        }
        // 显示 shell 结果帮助调试
        if (!success || errOutput) {
            showMsg("Shell 调试", "execute: " + success + "\nstdout: " + output.substring(0, 100) + "\nstderr: " + errOutput.substring(0, 100));
        }
    } catch (e) {
        // iPhone 或沙盒
    }
    return null;
}

function main() {
    // 检查是否已有 token
    var existing = getTokenDraft();
    if (existing) {
        try {
            var t = JSON.parse(existing.content);
            if (t.access_token) {
                var p = Prompt.create();
                p.title = "已有 Token";
                p.message = "Token 已存在 (expires_at: " + (t.expires_at || "未知") + ")\n重新导入？";
                p.addButton("重新导入");
                p.addButton("取消");
                if (!p.show() || p.buttonPressed === "取消") {
                    return;
                }
            }
        } catch (e) { }
    }

    // 尝试自动读取
    var tokenJson = tryReadFromFile();

    if (tokenJson) {
        if (saveTokenToDraft(tokenJson)) {
            app.displaySuccessMessage("✅ Token 已自动导入");
        }
        return;
    }

    // 手动输入
    var p = Prompt.create();
    p.title = "导入 Heptabase Token";
    p.message = "Mac 终端运行:\ncat ~/.config/heptabase-local/token.json | pbcopy\n\n然后粘贴:";
    p.addTextView("token", "token.json 内容", "", { height: 120 });
    p.addButton("导入");
    p.addButton("取消");

    if (!p.show() || p.buttonPressed === "取消") {
        context.cancel();
        return;
    }

    tokenJson = p.fieldValues["token"].trim();
    if (!tokenJson) {
        showMsg("❌ 错误", "Token 内容为空");
        return;
    }

    if (saveTokenToDraft(tokenJson)) {
        app.displaySuccessMessage("✅ Token 已导入");
    }
}

main();
