// ═══════════════════════════════════════════════════════════════
// Heptabase Setup for Drafts (Mac)
// ═══════════════════════════════════════════════════════════════
// 运行 Python 授权脚本，完成 Heptabase OAuth 登录。
// 授权成功后 token 保存在 ~/.config/heptabase-local/token.json
// ═══════════════════════════════════════════════════════════════

var PYTHON_DIR = "$HOME/.config/heptabase-local";
var AUTH_SCRIPT = PYTHON_DIR + "/heptabase_auth.py";

function main() {
    // 检查授权脚本是否存在
    var checkScript = ShellScript.create(
        "test -f " + AUTH_SCRIPT + " && echo 'OK' || echo 'MISSING'"
    );
    checkScript.execute();
    var checkResult = checkScript.standardOutput.trim();

    if (checkResult === "MISSING") {
        var p = Prompt.create();
        p.title = "⚠️ 未安装 Python 脚本";
        p.message =
            "请先在终端运行以下命令安装：\n\n" +
            "mkdir -p ~/.config/heptabase-local\n" +
            "cp python-backend/heptabase_*.py ~/.config/heptabase-local/";
        p.addButton("知道了");
        p.show();
        context.cancel();
        return;
    }

    // 检查是否已授权
    var tokenCheck = ShellScript.create(
        "test -f " + PYTHON_DIR + "/token.json && echo 'OK' || echo 'MISSING'"
    );
    tokenCheck.execute();

    if (tokenCheck.standardOutput.trim() === "OK") {
        // 已有 token，询问是否重新授权
        var p = Prompt.create();
        p.title = "Heptabase 授权状态";
        p.message = "已有授权 Token。是否重新授权？";
        p.addButton("重新授权");
        p.addButton("取消");
        if (!p.show() || p.buttonPressed === "取消") {
            app.displaySuccessMessage("✅ 已授权，无需操作");
            return;
        }
    }

    // 运行授权脚本
    app.displayInfoMessage("正在打开浏览器授权...");
    var authScript = ShellScript.create(
        "/usr/bin/python3 " + AUTH_SCRIPT
    );
    var success = authScript.execute();

    if (success) {
        app.displaySuccessMessage("✅ 授权成功！");
    } else {
        app.displayErrorMessage("❌ 授权失败: " + authScript.standardError);
    }
}

main();
