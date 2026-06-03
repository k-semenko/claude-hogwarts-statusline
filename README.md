# 🪄 Hogwarts Statusline for Claude Code

A Harry Potter–themed [statusline](https://code.claude.com/docs/en/statusline) for
[Claude Code](https://claude.com/claude-code): your **house crest and colours**,
context & rate-limit bars with **reset countdowns**, session cost in *galleons*,
and a **wizard rank** that grows with your output.

```
╭──── 🐍  Slytherin ───────────────────────────────╮
│ ϟ Opus 4.8 (1M context)           ↓ IN   471.1k  │
│ ✦ First-Year · xhigh              ↑ OUT  2.9k    │
│ ◈ ctx ████░░░░  47%               ◈ CTX  474k/1M │
│ ⧗ 5h  ██░░░░░░  19%  ⟲ 1h40m      ⧗ TIME 23h28m  │
│ ◐ 7d  █░░░░░░░  17%  ⟲ 3d4h       ⊚ GAL  $70.63  │
│ ⌂ ~/work/project  ⎇ main                         │
╰──────────────────────────────────────────────────╯
```

> Frame is rendered in your house colours — scarlet & gold for Gryffindor,
> green & silver for Slytherin, blue & bronze for Ravenclaw, yellow & black for
> Hufflepuff.

## ✨ Features

- **Four houses** with authentic colours and crest emoji: 🦁 Gryffindor ·
  🐍 Slytherin · 🦅 Ravenclaw · 🦡 Hufflepuff.
- **Context bar** (`ctx`) with green→yellow→red load colours.
- **5-hour & 7-day rate-limit bars** with a **reset countdown** (`⟲ 1h40m`,
  `⟲ 3d4h`); turns red when a limit is nearly exhausted.
- **Wizard rank** by output tokens: First-Year → Student → Prefect → Auror →
  Professor → Headmaster.
- **Galleons** = session cost, plus IN/OUT tokens, elapsed time, context usage.
- **Model name & effort shown verbatim** — new models / effort levels need no code changes.
- **Robust alignment** — the only emoji lives in the header, so its
  unpredictable terminal width never breaks the frame.

## 🖥️ Terminal compatibility

The script auto-detects **JetBrains IDEs** (Rider, IntelliJ IDEA, PyCharm, etc.) via the
`TERMINAL_EMULATOR=JetBrains-JediTerm` environment variable that JediTerm sets automatically.
JediTerm renders emoji at 1-cell width instead of the standard 2 — without this correction the
top-right corner of the frame drifts by one column. No configuration needed.

All other terminals (iTerm2, kitty, Alacritty, WezTerm, macOS Terminal, …) are treated as
standard 2-cell-wide emoji and need no adjustment.

## 📦 Requirements

- [Claude Code](https://claude.com/claude-code)
- `python3` available on your `PATH` (no third-party packages)
- A terminal with a Unicode / Nerd-friendly monospace font

## 🚀 Install (as a plugin)

```text
/plugin marketplace add k-semenko/claude-hogwarts-statusline
/plugin install hogwarts-statusline@hogwarts-statusline
```

The statusline activates automatically (the plugin ships a `settings.json` that
wires it up via `${CLAUDE_PLUGIN_ROOT}`). If it doesn't appear immediately, run
`/reload-plugins` or restart Claude Code.

## 🎓 Choose your house

```text
/hogwarts-statusline             # interactive picker (Gryffindor / Slytherin / Ravenclaw / Hufflepuff)
/hogwarts-statusline slytherin   # set directly (also accepts prefixes & animal aliases)
```

The choice is stored in `~/.claude/hogwarts-statusline.json` and read on the next
redraw. You can also force a house with the `CC_HOUSE` environment variable
(it takes priority over the file).

## 🧭 What it shows

| Element            | Meaning                                                        |
|--------------------|----------------------------------------------------------------|
| Header             | House crest + name, frame in house colours                     |
| `ϟ <model>`        | Model display name (verbatim)                                  |
| `✦ <rank> · <effort>` | Wizard rank (by output tokens) and current effort           |
| `◈ ctx`            | Context-window usage                                           |
| `⧗ 5h` / `◐ 7d`    | Rate limits + `⟲` time until reset                             |
| `⊚ GAL`            | Session cost (galleons)                                        |
| `↓ IN` / `↑ OUT`   | Input / output tokens                                          |
| `⧗ TIME`           | Elapsed session time                                           |
| `◈ CTX`            | Tokens used / context-window size                              |
| `⌂` / `⎇`          | Working directory / git branch                                 |

## 🔧 Manual install (without the plugin system)

1. Copy `plugin/hogwarts-statusline.py` somewhere, e.g. `~/.claude/`.
2. In `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "CC_HOUSE=slytherin python3 /absolute/path/to/hogwarts-statusline.py",
    "padding": 0
  }
}
```

Change `CC_HOUSE` to your house (or drop it and use the config file).

## 🛠️ How the house is resolved

1. `CC_HOUSE` environment variable (if set), then
2. `house` field in `~/.claude/hogwarts-statusline.json`, then
3. default → `gryffindor`.

Names are case-insensitive; prefixes (`slyth`) and animal aliases
(`lion` / `snake` / `eagle`/`raven` / `badger`) work too.

## 📜 License

[MIT](LICENSE) — do what you will, mischief managed. 🪄
