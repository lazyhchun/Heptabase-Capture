// ═══════════════════════════════════════════════════════════════
// Heptabase Card — 保存为笔记卡片 (Mac)
// ═══════════════════════════════════════════════════════════════
// 通过 Python 后端调用 Heptabase API，与 PopClip 相同方式。
// ═══════════════════════════════════════════════════════════════

var CARD_SCRIPT = "$HOME/.config/heptabase-local/heptabase_card.py";

function main() {
    var content = draft.content.trim();
    if (!content) {
        app.displayErrorMessage("内容为空");
        return;
    }

    // 用 ShellScript 调用 Python，内容通过 stdin 传递
    var cmd = "echo " + shellEscape(content) + " | /usr/bin/python3 " + CARD_SCRIPT;
    var script = ShellScript.create(cmd);
    var success = script.execute();

    if (success && script.standardOutput.trim() === "OK") {
        app.displaySuccessMessage("✅ 已保存为卡片");
    } else {
        var err = script.standardError.trim() || script.standardOutput.trim() || "未知错误";
        app.displayErrorMessage("❌ " + err);
    }
}

// Shell 转义：用单引号包裹，内部单引号用 '\'' 替换
function shellEscape(s) {
    return "'" + s.replace(/'/g, "'\\''") + "'";
}

main();
