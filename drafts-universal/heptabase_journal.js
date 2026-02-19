// ═══════════════════════════════════════════════════════════════
// Heptabase Journal — 追加到今日日志 (Mac + iPhone)
// ═══════════════════════════════════════════════════════════════

var TOKEN_TAG = "heptabase-token";
var MCP_URL = "https://api.heptabase.com/mcp";
var TOKEN_URL = "https://api.heptabase.com/token";

// ── 工具函数 ──

function showMsg(title, msg) {
    var p = Prompt.create();
    p.title = title;
    p.addTextView("info", "", msg, { height: 200 });
    p.addButton("确定");
    p.show();
}

// ── Token 管理 ──

function getTokenDraft() {
    var results = Draft.query("", "archive", [TOKEN_TAG]);
    if (results.length > 0) return results[0];
    results = Draft.query("", "inbox", [TOKEN_TAG]);
    if (results.length > 0) return results[0];
    return null;
}

function loadToken() {
    var d = getTokenDraft();
    if (!d) {
        showMsg("❌ Token 未找到", "请先运行 Heptabase Setup 导入 Token。");
        return null;
    }
    try {
        var data = JSON.parse(d.content);
        if (!data.access_token) {
            showMsg("❌ Token 无效", "Token Draft 内容缺少 access_token:\n\n" + d.content.substring(0, 200));
            return null;
        }
        return data;
    } catch (e) {
        showMsg("❌ Token 解析失败", "内容不是有效 JSON:\n\n" + d.content.substring(0, 200));
        return null;
    }
}

function saveToken(data) {
    var d = getTokenDraft();
    if (!d) {
        d = new Draft();
        d.addTag(TOKEN_TAG);
    }
    d.content = JSON.stringify(data, null, 2);
    d.update();
    if (!d.isArchived) { d.isArchived = true; d.update(); }
}

function refreshIfNeeded(tokenData) {
    var now = Math.floor(Date.now() / 1000);
    if (now < (tokenData.expires_at || 0) - 60) {
        return tokenData;
    }
    if (!tokenData.refresh_token) {
        showMsg("❌ Token 过期", "Token 已过期且没有 refresh_token，请重新运行 Setup。");
        return null;
    }

    var http = HTTP.create();
    var resp = http.request({
        url: TOKEN_URL,
        method: "POST",
        encoding: "form",
        data: {
            client_id: tokenData.client_id || "",
            refresh_token: tokenData.refresh_token,
            grant_type: "refresh_token"
        },
        headers: { "Accept": "application/json" }
    });

    if (resp.success && resp.statusCode === 200) {
        try {
            var newData = JSON.parse(resp.responseText);
            tokenData.access_token = newData.access_token;
            tokenData.expires_at = Math.floor(Date.now() / 1000) + (newData.expires_in || 3600);
            if (newData.refresh_token) tokenData.refresh_token = newData.refresh_token;
            saveToken(tokenData);
            return tokenData;
        } catch (e) {
            showMsg("❌ 刷新解析失败", resp.responseText);
            return null;
        }
    } else {
        showMsg("❌ Token 刷新失败",
            "Status: " + resp.statusCode + "\n" +
            "Response: " + (resp.responseText || "(空)").substring(0, 300));
        return null;
    }
}

// ── MCP 调用 ──

function callMCP(accessToken, toolName, args) {
    var http = HTTP.create();
    var payload = {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/call",
        params: {
            name: toolName,
            arguments: args
        }
    };

    var resp = http.request({
        url: MCP_URL,
        method: "POST",
        encoding: "json",
        data: payload,
        headers: {
            "Accept": "application/json, text/event-stream",
            "Authorization": "Bearer " + accessToken
        }
    });

    if (!resp.responseText) {
        return { error: "无响应 (status " + resp.statusCode + ")" };
    }

    var text = resp.responseText.trim();

    // SSE 格式解析
    if (text.indexOf("data:") >= 0) {
        var lines = text.split("\n");
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (line.indexOf("data:") === 0) {
                var jsonStr = line.substring(5).trim();
                if (jsonStr && jsonStr !== "[DONE]") {
                    try {
                        var sseResult = JSON.parse(jsonStr);
                        if (sseResult.error) {
                            return { error: sseResult.error.message };
                        }
                        return { success: true, result: sseResult.result };
                    } catch (e) { }
                }
            }
        }
        return { error: "SSE 解析失败" };
    }

    // 普通 JSON
    try {
        var result = JSON.parse(text);
        if (result.error) {
            return { error: result.error.message };
        }
        return { success: true, result: result.result };
    } catch (e) {
        return { error: "解析失败" };
    }
}

// ── 主逻辑 ──

function main() {
    var content = draft.content.trim();
    if (!content) {
        app.displayErrorMessage("❌ 内容为空");
        return;
    }

    var tokenData = loadToken();
    if (!tokenData) return;

    tokenData = refreshIfNeeded(tokenData);
    if (!tokenData) return;

    var result = callMCP(tokenData.access_token, "append_to_journal", {
        content: content
    });

    if (result.success) {
        app.displaySuccessMessage("✅ 已追加到日志");
        return;
    }

    // 可能 401，刷新重试
    tokenData.expires_at = 0;
    tokenData = refreshIfNeeded(tokenData);
    if (tokenData) {
        result = callMCP(tokenData.access_token, "append_to_journal", { content: content });
        if (result.success) {
            app.displaySuccessMessage("✅ 已追加到日志");
            return;
        }
    }
    app.displayErrorMessage("❌ 失败: " + (result.error || "未知错误"));
}

main();
