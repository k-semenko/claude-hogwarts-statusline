# 🪄 Hogwarts Statusline for Claude Code

A Harry Potter–themed [statusline](https://code.claude.com/docs/en/statusline) for
[Claude Code](https://claude.com/claude-code): your house crest and colours, context and
rate-limit usage with a **pace marker**, session cost in *galleons*, and a quiet line of
Hogwarts wisdom that turns into a **Howler** when something needs your attention.

```
🐍 ~/work/project ⎇ feature/login ⇡#1438✓ │ ctx 25% │ 5h █░┃░░  18% ⟲2h16m │ 7d ██░░░  47% ⟲3d5h │ ⊚ $8.12
   Test first, cast later
```

When a limit is about to run out, the bottom line becomes a Howler:

```
🐍 ~/work/project ⎇ feature/login ⇡#1438✓ │ ctx 25% │ 5h ██┃█░  70% ⟲3h30m │ 7d ██░░░  47% ⟲3d5h │ ⊚ $8.12
 📜 5h 70% — at this pace runs out in 39m, resets in 3h30m
```

## ✨ Features

- **Two lines** — data with your house crest up front, and a phrase or warning below.
- **Pace marker** on the 5-hour limit: `┃` shows where usage would be if spent evenly until
  the reset. Fill past the marker means you're burning faster than the window refills.
- **Howler** — when the 5-hour limit will run out before it resets, a limit passes 85% or
  the context passes 80%, the bottom line turns into a one-line warning.
- **Phrase of the day** — a dim line of original Hogwarts-flavoured advice, new on every prompt.
- **Adapts to terminal width** (`$COLUMNS`): shortens the branch first, then switches to
  compact layouts (`5h 70%▲40` = 40 points ahead of pace). A burning limit always stays visible.
- **Clickable links** in terminals with OSC 8 support (iTerm2, kitty, WezTerm): the path or repo
  name opens the repository, the branch opens its page, and the pull / merge request
  (`⇡#123`, `⇡!123` for GitLab) opens the request, coloured by review state.
- **Classic layout** — the original seven-line boxed HUD, still available.
- **English and Russian** phrases and warnings.

## 🖥️ Terminal compatibility

The script auto-detects **JetBrains IDEs** (Rider, IntelliJ IDEA, PyCharm, etc.) via
`TERMINAL_EMULATOR=JetBrains-JediTerm` and counts the crest emoji as 1 cell there
(2 cells everywhere else) when fitting the line to the terminal width.

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

## 🎓 Settings

```text
/hogwarts-statusline:hogwarts-statusline                      # interactive picker
/hogwarts-statusline:hogwarts-statusline slytherin            # set the house
/hogwarts-statusline:hogwarts-statusline ravenclaw classic en # house, layout and language at once
```

Settings live in `~/.claude/hogwarts-statusline.json`; environment variables take priority:

| Setting  | Values                                             | Env                  | Default        |
|----------|----------------------------------------------------|----------------------|----------------|
| `house`  | `gryffindor` · `slytherin` · `ravenclaw` · `hufflepuff` | `CC_HOUSE`       | `gryffindor`   |
| `layout` | `v2` · `classic`                                   | `CC_HOGWARTS_LAYOUT` | `v2`           |
| `lang`   | `en` · `ru`                                        | `CC_HOGWARTS_LANG`   | from `$LANG`   |

House names are case-insensitive; prefixes (`slyth`) and animal aliases
(`lion` / `snake` / `eagle`/`raven` / `badger`) work too.

## 🧭 What it shows

| Element               | Meaning                                                      |
|-----------------------|--------------------------------------------------------------|
| `🦁` … / `⎇`          | House crest and working directory / git branch               |
| `⇡#123` / `⇡!123`     | Open PR / MR: `✓` approved, `✗` changes requested, `◌` draft |
| `ctx`                 | Context-window usage                                         |
| `5h`                  | 5-hour limit, `┃` pace marker, `⟲` time until reset          |
| `7d`                  | 7-day limit and time until reset (no pace: the week isn't spent evenly) |
| `spend`               | Spend limit behind a Claude apps gateway                     |
| `⊚`                   | Session cost (galleons)                                      |
| `📜`                  | Howler: what's running out and when                          |

## 🔧 Manual install (without the plugin system)

1. Copy `plugin/hogwarts-statusline.py` and `plugin/hogwarts_phrases.py` into the same folder, e.g. `~/.claude/`.
2. In `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "CC_HOUSE=slytherin python3 /absolute/path/to/hogwarts-statusline.py",
    "padding": 0,
    "refreshInterval": 60
  }
}
```

Change `CC_HOUSE` to your house (or drop it and use the config file).

## 📜 License

[MIT](LICENSE) — do what you will, mischief managed. 🪄
