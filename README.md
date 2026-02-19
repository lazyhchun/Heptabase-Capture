# Heptabase Capture Tools

[Chinese (中文)](README_zh.md)

A local toolkit for quickly capturing content into [Heptabase](https://heptabase.com/) from anywhere — PopClip, Drafts, and Apple Shortcuts.

## Prerequisites

### Required

- [Heptabase](https://heptabase.com/) account (API access required)
- macOS (initial OAuth authorization must be completed on a Mac)
- Python 3.7+ (system built-in or install via [python.org](https://www.python.org/downloads/))

### Optional (depending on your client)

- [PopClip](https://www.popclip.app/) (macOS, paid app)
- [Drafts](https://getdrafts.com/) (Mac / iPhone)
- Apple Shortcuts (built into iPhone)

## Python Dependencies

This project uses **only the Python standard library** — no third-party packages required.

Standard library modules used:

| Module | Purpose |
|---|---|
| `urllib` | HTTP requests (API calls, OAuth flow) |
| `json` | Token and API data parsing |
| `hashlib` / `base64` / `secrets` | PKCE authorization flow |
| `http.server` | OAuth callback local server |
| `webbrowser` | Auto-open browser for authorization |
| `socket` / `threading` | Local server port management |

## Directory Structure

```
heptabase-capture/
├── python-backend/             # Python backend (core dependency)
│   ├── heptabase_auth.py       # OAuth authorization (run once)
│   ├── heptabase_api.py        # Core API module
│   ├── heptabase_append.py     # CLI: append to journal
│   └── heptabase_card.py       # CLI: save as card
│
├── popclip/                    # PopClip extensions (macOS)
│   ├── Heptabase Journal.popclipext/
│   └── Heptabase Card.popclipext/
│
├── drafts/                     # Drafts Actions (Mac only, calls Python)
│   ├── heptabase_setup.js
│   ├── heptabase_journal.js
│   └── heptabase_card.js
│
├── drafts-universal/           # Drafts Actions (Mac + iPhone, HTTP direct)
│   ├── heptabase_setup.js      # Import token
│   ├── heptabase_journal.js    # Append to today's journal
│   └── heptabase_card.js       # Save as note card
│
└── shortcuts/                  # Apple Shortcuts (iPhone)
    └── README.md               # Setup guide
```

## Quick Start

### 1. Install Python Backend & Authorize

```bash
mkdir -p ~/.config/heptabase-local
cp python-backend/*.py ~/.config/heptabase-local/
python3 ~/.config/heptabase-local/heptabase_auth.py
```

> **Security Tip**: After authorization, the token file is saved at `~/.config/heptabase-local/token.json`. It's recommended to set directory permissions to prevent other users from accessing it:
>
> ```bash
> chmod 700 ~/.config/heptabase-local
> ```
>
> Do not commit `token.json` to version control or share it with others. The token will auto-refresh when expired — no manual intervention needed.

### 2. Choose a Client

| Client | Platform | Status | Description |
|---|---|---|---|
| **PopClip** | macOS | ✅ Available | Select text → click button, see [popclip/README.md](popclip/README.md) |
| **Drafts** (Mac) | macOS | ✅ Available | Calls Python backend, see [drafts/README.md](drafts/README.md) |
| **Drafts** (Universal) | Mac + iPhone | ✅ Available | HTTP direct to MCP API, see [drafts-universal/README.md](drafts-universal/README.md) |
| **Shortcuts** | iPhone | ⚠️ Untested | Get URL contents → MCP API, see [shortcuts/README.md](shortcuts/README.md) |

## Features

- **Append to Today's Journal**: Append text to the current day's Heptabase Journal
- **Save as Note Card**: Save text as a Heptabase Note Card (first line becomes the title)

## Troubleshooting

### OAuth Authorization Failed

- Verify Python version ≥ 3.7: `python3 --version`
- Ensure your network can reach `api.heptabase.com`
- The browser will open automatically during authorization — do not close the terminal window
- If the port is occupied, the script will automatically try another available port

### PopClip / Drafts Cannot Call Python

- Confirm scripts are copied to `~/.config/heptabase-local/`
- Confirm `token.json` exists and is not expired (the script auto-refreshes)
- Test manually in terminal: `python3 ~/.config/heptabase-local/heptabase_append.py "test"`

### Drafts Universal Cannot Connect to API

- Confirm you've run the Setup Action in Drafts and imported the token correctly
- Ensure your device has network access to `https://api.heptabase.com/mcp`

## Known Limitations

- Initial authorization must be completed on a Mac (Python OAuth flow)
- Journal dates are determined by the Heptabase server; entries during early morning hours may appear as the previous day (UTC timezone)

## Contributing

Issues and Pull Requests are welcome!

If you encounter problems or have feature suggestions, please provide feedback via [Issues](https://github.com/lazyhchun/Heptabase-Capture/issues).

## License

[MIT](LICENSE)
