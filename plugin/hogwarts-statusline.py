#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тематический statusline для Claude Code в стиле Гарри Поттера.

Раскладка "v2" (по умолчанию):
  🦁 aqua ⎇ fix-ios-sharing ⇡!1438✓ │ ctx 25% │ 5h █┃░░░ 18% ⟲2h16m │ 7d ██░░░ 47% ⟲3d5h │ ⊚ $8.12
     Сначала тест, потом заклинание         ← фраза дня; при тревоге её место занимает Howler

Раскладка "classic" — прежняя рамка ╭──╮ на семь строк.

Настройки (переменная окружения → ~/.claude/hogwarts-statusline.json → дефолт):
  house   CC_HOUSE            gryffindor | slytherin | ravenclaw | hufflepuff (префиксы и алиасы lion/snake/eagle/badger)
  layout  CC_HOGWARTS_LAYOUT  v2 | classic
  lang    CC_HOGWARTS_LANG    ru | en  (по умолчанию — из $LANG)
"""
import sys, json, re, os, time, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hogwarts_phrases import PHRASES, HOWLER

# ---------- настройки ----------
def load_cfg():
    try:
        with open(os.path.expanduser("~/.claude/hogwarts-statusline.json"), encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}

CFG = load_cfg()
def setting(env, key, default=None):
    return os.environ.get(env) or CFG.get(key) or default

HOUSES = {
    "gryffindor": dict(P=(174,  0,  1), A=(211,166, 37), Ab=(255,205, 60), name="Gryffindor", dat="Гриффиндору", emoji="🦁"),
    "slytherin":  dict(P=( 26, 71, 42), A=(170,172,178), Ab=(220,222,228), name="Slytherin",  dat="Слизерину",   emoji="🐍"),
    "ravenclaw":  dict(P=( 34, 47, 91), A=(176,141, 87), Ab=(208,170,112), name="Ravenclaw",  dat="Когтеврану",  emoji="🦅"),
    "hufflepuff": dict(P=(120, 92, 18), A=(236,185, 57), Ab=(255,216, 80), name="Hufflepuff", dat="Пуффендую",   emoji="🦡"),
}
ALIAS = {"lion": "gryffindor", "snake": "slytherin", "serpent": "slytherin",
         "eagle": "ravenclaw", "raven": "ravenclaw", "badger": "hufflepuff"}

def resolve_house(raw):
    k = (raw or "gryffindor").strip().lower()
    k = ALIAS.get(k, k)
    if k in HOUSES:
        return k
    for h in HOUSES:
        if k and h.startswith(k):
            return h
    return "gryffindor"

H = HOUSES[resolve_house(setting("CC_HOUSE", "house"))]
LAYOUT = "classic" if str(setting("CC_HOGWARTS_LAYOUT", "layout", "v2")).lower() == "classic" else "v2"
_lang = str(setting("CC_HOGWARTS_LANG", "lang") or ("ru" if os.environ.get("LANG", "").lower().startswith("ru") else "en")).lower()
LANG = "ru" if _lang.startswith("ru") else "en"

# ---------- цвета ----------
RESET = "\033[0m"; BOLD = "\033[1m"; ITALIC = "\033[3m"
def fg(c): return f"\033[38;2;{c[0]};{c[1]};{c[2]}m"
def bgc(c): return f"\033[48;2;{c[0]};{c[1]};{c[2]}m"
def lighten(c, k): return tuple(min(255, round(x * k)) for x in c)
def mix(a, b, t): return tuple(round(x * t + y * (1 - t)) for x, y in zip(a, b))

TERM_BG = (16, 20, 28)      # фон терминала неизвестен — приглушаем к типичному тёмному

TEXT    = fg((228,230,235))
MUTED   = fg((140,150,160))
WHISPER = fg(mix((140,150,160), TERM_BG, .42))
EMPTY   = fg((52, 56, 68))
WARN    = fg((235,200, 80))
ALERT   = fg((235, 90, 90))
GRN     = fg((110,210,120))
HOWL    = bgc((78, 20, 26)) + fg((255,214,214)) + BOLD
ACC     = fg(H["A"]); ACCB = fg(H["Ab"])
# Разделители приглушены к фону: иначе красный Гриффиндора и жёлтый Пуффендуя спорят с тревогой и вниманием.
SEPC    = fg(mix(lighten(H["P"], 2.0), TERM_BG, .5))
FRAME   = fg(lighten(H["P"], 2.4))      # classic: рамка яркая, как раньше

# ---------- ввод ----------
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

def g(*path, default=None):
    cur = data
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default

# ---------- форматтеры ----------
def kfmt(n):
    n = int(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:     return f"{n/1_000:.1f}k".replace(".0k", "k")
    return str(n)

def dur(ms):
    s = int((ms or 0) / 1000)
    if s < 60: return f"{s}s"
    m = s // 60
    if m < 60: return f"{m}m{s%60:02d}s"
    return f"{m//60}h{m%60:02d}m"

def mins_fmt(mins):
    mins = max(0, round(mins))
    if mins >= 1440:
        d, h = mins // 1440, (mins % 1440) // 60
        return f"{d}d{h}h" if h else f"{d}d"
    if mins >= 60:
        return f"{mins//60}h{mins%60:02d}m"
    return f"{mins}m"

def reset_in(ts):
    return mins_fmt((ts - time.time()) / 60) if ts else None

# Ранг — по изменённым строкам: счётчики токенов в контракте описывают только текущий контекст, а не сессию.
def wizard_rank(lines):
    for thr, name in [(50,"First-Year"), (200,"Student"), (600,"Prefect"),
                      (1500,"Auror"), (4000,"Professor")]:
        if lines < thr:
            return name
    return "Headmaster"

ESC_RE = re.compile(r"\033\[[0-9;]*m|\033\]8;[^\033]*\033\\")
# JetBrains JediTerm рисует эмодзи шириной 1, обычные терминалы — 2
EMOJI_W = 1 if "JetBrains" in os.environ.get("TERMINAL_EMULATOR", "") else 2
def vlen(s):
    w = 0
    for ch in ESC_RE.sub("", s):
        o = ord(ch)
        if o == 0xFE0F: continue
        w += EMOJI_W if o >= 0x1F000 else 1
    return w

def pad(s, w):
    d = w - vlen(s)
    return s + " " * d if d > 0 else s

def ellipsize(s, maxlen):
    return s if len(s) <= maxlen else s[:max(1, maxlen - 1)] + "…"

def link(url, text):                             # OSC 8: кликабельно в iTerm2/kitty/WezTerm, иначе просто текст
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\" if url else text

def bar(pct, width, color, mark=None):
    pct = max(0, min(100, pct))
    fill = round(pct / 100 * width)
    out = ""
    for i in range(width):
        if i == mark:
            out += f"{TEXT}{BOLD}┃{RESET}"
        else:
            out += f"{color}█" if i < fill else f"{EMPTY}░"
    return out + RESET

def git_branch(start):                            # вне worktree-сессии ветку JSON не отдаёт — читаем .git/HEAD
    d = os.path.abspath(start or ".")
    while True:
        gp = os.path.join(d, ".git")
        if os.path.exists(gp):
            break
        parent = os.path.dirname(d)
        if parent == d:
            return None, None
        d = parent
    root = d
    if os.path.isfile(gp):                        # worktree/submodule: ".git" — файл "gitdir: …"
        try:
            line = open(gp, encoding="utf-8").read().strip()
        except Exception:
            return None, root
        if line.startswith("gitdir:"):
            gp = os.path.normpath(os.path.join(d, line[7:].strip()))
    try:
        ref = open(os.path.join(gp, "HEAD"), encoding="utf-8").read().strip()
    except Exception:
        return None, root
    if ref.startswith("ref: refs/heads/"):
        return ref[16:], root
    return (ref[:7] if ref else None), root      # detached HEAD → короткий хэш

# ---------- данные ----------
model   = g("model", "display_name", default="Wizard")
ctx_sz  = g("context_window", "context_window_size", default=200000) or 200000
ctx_tok = g("context_window", "total_input_tokens", default=0) or 0
ctx_pct = g("context_window", "used_percentage")
ctx_pct = round(ctx_pct if ctx_pct is not None else (ctx_tok / ctx_sz * 100 if ctx_sz else 0))

effort  = g("effort", "level")
fast    = g("fast_mode", default=False)
cost    = g("cost", "total_cost_usd", default=0.0) or 0.0
dur_ms  = g("cost", "total_duration_ms", default=0) or 0
added   = g("cost", "total_lines_added", default=0) or 0
removed = g("cost", "total_lines_removed", default=0) or 0

cwd     = g("workspace", "current_dir") or g("cwd") or os.getcwd()
_head, git_root = git_branch(cwd)
branch  = g("worktree", "branch") or _head
pr      = g("pr", default={}) or {}

COLS  = int(os.environ.get("COLUMNS") or 0) or 120
WIDTH = max(30, COLS - 4)                         # запас под отступ, который добавляет сам Claude Code
NOW   = time.time()

def display_path():
    p = cwd
    wt = re.search(r"/\.claude/worktrees/[^/]+", p)
    if wt:                                        # worktree-сессия: показываем исходный репо, ветка скажет остальное
        p = p[:wt.start()] + p[wt.end():]
    home = os.path.expanduser("~")
    return "~" + p[len(home):] if p.startswith(home) else p

def repo_name():
    name = g("workspace", "repo", "name")
    if name:
        return name
    root = re.sub(r"/\.claude/worktrees/[^/]+.*$", "", git_root or cwd)
    return os.path.basename(root.rstrip("/")) or "/"

def short_path(p, maxlen):
    if len(p) <= maxlen:
        return p
    parts = p.split(os.sep)
    out = os.sep.join(parts[:1] + [s[:1] for s in parts[1:-1] if s] + parts[-1:])
    return out if len(out) <= maxlen else "…" + p[-(maxlen - 1):]

def pr_mark():
    if not pr.get("number"):
        return ""
    color, mark = {"approved": (GRN, "✓"), "changes_requested": (ALERT, "✗"),
                   "draft": (MUTED, "◌")}.get(pr.get("review_state"), (ACC, ""))
    num = f"{'!' if pr.get('kind') == 'mr' else '#'}{pr['number']}{mark}"
    return f" {color}{link(pr.get('url'), '⇡' + num)}{RESET}"

# ---------- лимиты ----------
WINDOW_5H = 5 * 3600

def limit(win):
    val = g("rate_limits", win, "used_percentage")
    if val is None:
        return None
    return dict(val=float(val), ts=g("rate_limits", win, "resets_at"))

def pace_5h(lim):
    """Темп только для 5h: окно короткое и почти целиком рабочее, линейная оценка ему подходит."""
    if not lim or not lim["ts"]:
        return None
    left = max(0.0, lim["ts"] - NOW)
    f = max(0.0, min(1.0, 1 - left / WINDOW_5H))
    p = dict(frac=f, delta=lim["val"] - f * 100, eta=None)
    if f >= 0.1 and lim["val"] > 0:               # первые 10% окна прогноз шумит
        rate = lim["val"] / (f * WINDOW_5H)
        eta = (100 - lim["val"]) / rate
        if eta < left:
            p["eta"] = eta
    return p

L5, L7, LS = limit("five_hour"), limit("seven_day"), limit("spend_limit")
P5 = pace_5h(L5)

def level_limit(lim, pace=None):
    if not lim:
        return 0
    if lim["val"] >= 85 or (pace and pace["eta"] is not None):
        return 2
    if lim["val"] >= 60 or (pace and pace["frac"] >= 0.1 and pace["delta"] > 5):
        return 1
    return 0

LV5, LV7, LVS = level_limit(L5, P5), level_limit(L7), level_limit(LS)
LVC = 2 if ctx_pct >= 80 else (1 if ctx_pct >= 60 else 0)
LEVEL_COLOR = {0: None, 1: WARN, 2: ALERT}

# ---------- v2 ----------
SEP = f" {SEPC}│{RESET} "

def num(v, lvl, w=3):
    c = LEVEL_COLOR[lvl]
    return f"{c}{BOLD}{round(v):>{w}}%{RESET}" if c else f"{TEXT}{round(v):>{w}}%{RESET}"

def seg_ctx():
    return f"{MUTED}ctx{RESET} {num(ctx_pct, LVC, 1)}"

def seg_lim(label, lim, lvl, tier, pace=None):
    if not lim:
        return None
    r = reset_in(lim["ts"])
    if tier == "wide":
        mark = min(4, round(pace["frac"] * 5)) if pace else None
        tail = f" {MUTED}⟲{r}{RESET}" if r else ""
        return f"{MUTED}{label}{RESET} {bar(lim['val'], 5, LEVEL_COLOR[lvl] or ACC, mark)} {num(lim['val'], lvl)}{tail}"
    out = f"{MUTED}{label}{RESET} {num(lim['val'], lvl, 1)}"
    if pace and pace["frac"] >= 0.1:
        d = round(pace["delta"])
        out += f"{WARN}▲{d}{RESET}" if d > 0 else f"{MUTED}▼{-d}{RESET}"
    return out

def seg_loc(tier, branch_max, path_max=40):
    crest = f"{H['emoji']} "
    br = f" {ACC}⎇{RESET} {TEXT}{ellipsize(branch, branch_max)}{RESET}" if branch else ""
    if tier == "wide":
        return f"{crest}{TEXT}{short_path(display_path(), path_max)}{RESET}{br}{pr_mark()}"
    if tier == "mid":
        return f"{crest}{TEXT}{ellipsize(repo_name(), 16)}{RESET}{br}{pr_mark()}"
    loc = crest + (br.lstrip() or f"{TEXT}{ellipsize(repo_name(), 16)}{RESET}")
    return loc if tier == "tiny" else loc + pr_mark()

def main_line(tier, branch_max):
    segs = [seg_loc(tier, branch_max), seg_ctx(), seg_lim("5h", L5, LV5, tier, P5)]
    if tier != "tiny" or LV7 == 2:                # совсем узко: 7d и spend — только когда горят
        segs.append(seg_lim("7d", L7, LV7, tier))
    if LS and (tier != "tiny" or LVS == 2):
        segs.append(seg_lim("spend", LS, LVS, tier))
    if tier in ("wide", "mid"):
        segs.append(f"{ACCB}⊚{RESET} {TEXT}${cost:.2f}{RESET}")
    return SEP.join(s for s in segs if s)

def pick_main():
    """Ширина: сначала ужимаем ветку, потом переходим на более компактную раскладку."""
    full = len(branch or "")
    for tier, floor in (("wide", 24), ("mid", 16), ("narrow", 8), ("tiny", 8)):
        for bm in range(max(full, floor), floor - 1, -1):
            line = main_line(tier, bm)
            if vlen(line) <= WIDTH:
                return tier, line
    return "tiny", main_line("tiny", 8)

def howler(tier):
    t = HOWLER[LANG]
    short = tier in ("narrow", "tiny")
    if LV5 == 2:
        r = reset_in(L5["ts"]) or "?"
        if P5 and P5["eta"] is not None and not short:
            return t["pace"].format(w="5h", p=round(L5["val"]), eta=mins_fmt(P5["eta"] / 60), r=r)
        return f"5h {round(L5['val'])}% ⟲{r}" if short else t["limit"].format(w="5h", p=round(L5["val"]), r=r)
    if LVC == 2:
        return f"ctx {ctx_pct}% /compact" if short else t["ctx"].format(p=ctx_pct)
    for w, lim, lv in (("7d", L7, LV7), ("spend", LS, LVS)):
        if lv == 2:
            r = reset_in(lim["ts"]) or "?"
            return f"{w} {round(lim['val'])}% ⟲{r}" if short else t["limit"].format(w=w, p=round(lim["val"]), r=r)
    return None

def phrase():
    seed = g("prompt_id") or g("session_id") or time.strftime("%Y-%m-%d")
    pool = PHRASES[LANG]
    i = int(hashlib.sha1(str(seed).encode()).hexdigest(), 16) % len(pool)
    return pool[i].format(house=H["name"], house_dat=H["dat"])

def render_v2():
    tier, line = pick_main()
    msg = howler(tier)
    if msg:
        second = f"{HOWL} 📜 {ellipsize(msg, WIDTH - 5)} {RESET}"
    else:
        indent = " " * (EMOJI_W + 1)              # фраза встаёт под текст, а не под эмодзи
        second = f"{indent}{WHISPER}{ITALIC}{ellipsize(phrase(), WIDTH - len(indent))}{RESET}"
    return [line, second]

# ---------- classic: прежняя рамка ----------
def render_classic():
    title = f"{ACCB}{BOLD}ϟ{RESET} {BOLD}{TEXT}{model}{RESET}"
    rank_line = f"{ACC}✦{RESET} {TEXT}{wizard_rank(added + removed)}{RESET}"
    if effort:
        rank_line += f" {MUTED}·{RESET} {BOLD}{TEXT}{effort}{RESET}"
    if fast:
        rank_line += f" {ACCB}{BOLD}ϟ{RESET}"

    def ctx_color(p): return GRN if p < 50 else (WARN if p < 80 else ALERT)
    def lim_color(p): return ACC if p < 85 else ALERT

    def lim_row(glyph, label, lim):
        if not lim:
            return f"{MUTED}{glyph} {label}  —{RESET}"
        r = reset_in(lim["ts"])
        tail = f"  {MUTED}⟲ {r}{RESET}" if r else ""
        v = lim["val"]
        return f"{ACC}{glyph}{RESET} {MUTED}{label}{RESET} {bar(v, 8, lim_color(v))} {lim_color(v)}{round(v):>3}%{RESET}{tail}"

    mid = [
        title,
        rank_line,
        f"{ctx_color(ctx_pct) if ctx_pct >= 80 else ACC}◈{RESET} {MUTED}ctx{RESET} {bar(ctx_pct, 8, ctx_color(ctx_pct))} {ctx_color(ctx_pct)}{ctx_pct:>3}%{RESET}",
        lim_row("⧗", "5h ", L5),
        lim_row("◐", "7d ", L7),
    ]
    mid = [pad(m, 30) for m in mid]

    pr_txt = f"{'!' if pr.get('kind') == 'mr' else '#'}{pr['number']}" if pr.get("number") else "—"
    stats = [
        ("◈", ACC,   "CTX",  f"{kfmt(ctx_tok)}/{kfmt(ctx_sz)}"),
        ("±", GRN,   "CODE", f"+{added}/-{removed}"),
        ("⧗", MUTED, "TIME", dur(dur_ms)),
        ("⊚", ACCB,  "GAL",  f"${cost:.2f}"),
        ("⇡", ACC,   "PR",   pr_txt),
    ]
    vw = max(len(v) for *_, v in stats)
    right = [f"{c}{i}{RESET} {MUTED}{l:<4}{RESET} {TEXT}{v:<{vw}}{RESET}" for i, c, l, v in stats]
    core = [f"{mid[i]}    {right[i]}" for i in range(5)]

    content_w = max(vlen(c) for c in core)
    deco = vlen("⌂ ") + (vlen("  ⎇ ") + len(branch) if branch else 0)
    loc = f"{MUTED}⌂{RESET} {TEXT}{short_path(display_path(), max(10, content_w - deco))}{RESET}"
    if branch:
        loc += f"  {ACC}⎇{RESET} {GRN}{branch}{RESET}"
    inner = max(content_w, vlen(loc))

    # Эмодзи только в верхней строке: если терминал рисует его не в 2 ячейки, сдвинется лишь правый верхний угол.
    label = f"──── {H['emoji']}  {H['name']} "
    dashes = max(0, (inner + 2) - vlen(label))
    top = f"{FRAME}╭────{RESET} {H['emoji']}  {ACCB}{BOLD}{H['name']}{RESET} {FRAME}{'─'*dashes}╮{RESET}"
    bottom = f"{FRAME}╰{'─'*(inner + 2)}╯{RESET}"
    boxed = lambda c: f"{FRAME}│{RESET} {pad(c, inner)} {FRAME}│{RESET}"
    return [top] + [boxed(c) for c in core] + [boxed(loc), bottom]

for row in (render_classic() if LAYOUT == "classic" else render_v2()):
    print(row)
