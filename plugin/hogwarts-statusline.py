#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тематический statusline для Claude Code в стиле Гарри Поттера (Hogwarts HUD).
Рамка в цвете факультета; в заголовке — эмодзи-зверь и название факультета
(🦁/🐍/🦅/🦡), внутри — бары (ctx=контекст, ⧗5h / ◐7d = лимиты со временем
сброса) и характеристики справа (галлеоны=стоимость, ранг волшебника=«уровень»).
Эмодзи-зверь изолирован в заголовке (инфо-строки — глифы ширины 1), поэтому
его непредсказуемая в разных терминалах ширина не «двигает» рамку — в худшем
случае чуть сместится лишь правый верхний угол.

Факультет выбирается (в порядке приоритета):
  1) переменной окружения CC_HOUSE;
  2) полем "house" в ~/.claude/hogwarts-statusline.json (меняется командой /hogwarts-statusline);
  3) по умолчанию — gryffindor.
Любой регистр; работают полные имена, префиксы и алиасы-животные:
  gryffindor | slytherin | ravenclaw | hufflepuff
  lion       | snake     | eagle/raven | badger        (алиасы)

Запускается плагином автоматически (statusLine в settings.json плагина).
Сменить факультет проще всего командой /hogwarts-statusline.
В инфо-строках — только глифы ширины 1, чтобы колонки не разъезжались.
"""
import sys, json, re, os, time

# ---------- ANSI ----------
RESET = "\033[0m"; BOLD = "\033[1m"
def fg(r, g, b): return f"\033[38;2;{r};{g};{b}m"
def lighten(c, k=2.4):                          # осветляем тёмный primary: иначе тонкие линии рамки
    return tuple(min(255, round(x * k)) for x in c)  # (#1A472A и т.п.) сглаживаются в серый на тёмном фоне

# ---------- факультеты ----------
# Эмодзи-зверь живёт только в заголовке (справа от него — линия, выравнивать
# нечего), поэтому его непредсказуемая ширина не ломает инфо-строки.
HOUSES = {
    "gryffindor": dict(P=(174,  0,  1), A=(211,166, 37), Ab=(255,205, 60), name="Gryffindor", emoji="🦁"),
    "slytherin":  dict(P=( 26, 71, 42), A=(170,172,178), Ab=(220,222,228), name="Slytherin",  emoji="🐍"),
    "ravenclaw":  dict(P=( 34, 47, 91), A=(176,141, 87), Ab=(208,170,112), name="Ravenclaw",  emoji="🦅"),
    "hufflepuff": dict(P=(120, 92, 18), A=(236,185, 57), Ab=(255,216, 80), name="Hufflepuff", emoji="🦡"),
}
ALIAS = {"lion": "gryffindor", "snake": "slytherin", "serpent": "slytherin",
         "eagle": "ravenclaw", "raven": "ravenclaw", "badger": "hufflepuff"}

def resolve_house(raw):
    k = (raw or "gryffindor").strip().lower()
    k = ALIAS.get(k, k)
    if k in HOUSES:
        return k
    for h in HOUSES:                       # допускаем префикс: "gryf", "slyth"…
        if k and h.startswith(k):
            return h
    return "gryffindor"

def house_pref():                          # CC_HOUSE → конфиг-файл → дефолт
    env = os.environ.get("CC_HOUSE")
    if env:
        return env
    cfg = os.path.expanduser("~/.claude/hogwarts-statusline.json")
    try:
        with open(cfg, encoding="utf-8") as f:
            return json.load(f).get("house")
    except Exception:
        return None

H = HOUSES[resolve_house(house_pref())]
PRIM  = fg(*lighten(H["P"]));  ACC = fg(*H["A"]);  ACCB = fg(*H["Ab"])  # PRIM используется только в рамке
HOUSE_NAME = H["name"];  HOUSE_EMOJI = H["emoji"]

WHITE = fg(228,230,235)
GREY  = fg(140,150,160)
RED   = fg(235, 90, 90)
YEL   = fg(235,200, 80)
GRN   = fg(110,210,120)
EMPTY = fg(58, 60, 70)      # незаполненная часть бара

# ---------- ввод ----------
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

def g(d, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default

model_name = g(data, "model", "display_name", default="Wizard")
model_id   = g(data, "model", "id", default="")
ctx_size   = g(data, "context_window", "context_window_size", default=200000) or 200000
is_1m      = "1m" in model_id.lower() or ctx_size > 400000

effort   = g(data, "effort", "level")
thinking = g(data, "thinking", "enabled", default=False)

cw       = g(data, "context_window", default={}) or {}
in_tok   = cw.get("total_input_tokens", 0) or 0
out_tok  = cw.get("total_output_tokens", 0) or 0
used_pct = cw.get("used_percentage")
if used_pct is None:
    used_pct = round((in_tok + out_tok) / ctx_size * 100) if ctx_size else 0

cost   = g(data, "cost", "total_cost_usd", default=0.0) or 0.0
dur_ms = g(data, "cost", "total_duration_ms", default=0) or 0
lim5    = g(data, "rate_limits", "five_hour", "used_percentage")
lim7    = g(data, "rate_limits", "seven_day", "used_percentage")
lim5_ts = g(data, "rate_limits", "five_hour", "resets_at")
lim7_ts = g(data, "rate_limits", "seven_day", "resets_at")

cwd      = g(data, "cwd") or g(data, "workspace", "current_dir") or os.getcwd()

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

def wizard_rank(out):
    for thr, name in [(3000,"First-Year"), (10000,"Student"), (30000,"Prefect"),
                      (60000,"Auror"), (120000,"Professor")]:
        if out < thr:
            return name
    return "Headmaster"

def reset_in(ts):                                # сколько осталось до сброса лимита (resets_at — epoch-сек)
    if not ts:
        return None
    mins = max(0, round((ts - time.time()) / 60))
    if mins >= 1440:
        d, h = mins // 1440, (mins % 1440) // 60
        return f"{d}d{h}h" if h else f"{d}d"
    if mins >= 60:
        return f"{mins//60}h{mins%60:02d}m"
    return f"{mins}m"

ANSI_RE = re.compile(r"\033\[[0-9;]*m")
# JetBrains JediTerm рисует эмодзи шириной 1, обычные терминалы — 2
EMOJI_W = 1 if "JetBrains" in os.environ.get("TERMINAL_EMULATOR", "") else 2
def vlen(s):                                   # эмодзи = EMOJI_W ячеек, селектор VS16 = 0, прочее = 1
    s = ANSI_RE.sub("", s); w = 0
    for ch in s:
        o = ord(ch)
        if o == 0xFE0F: continue
        w += EMOJI_W if o >= 0x1F000 else 1
    return w
def pad(s, w):
    d = w - vlen(s)
    return s + " " * d if d > 0 else s

def bar(pct, width, color):
    pct = max(0, min(100, pct))
    fill = round(pct / 100 * width)
    return color + "█" * fill + EMPTY + "░" * (width - fill) + RESET

def ctx_color(p): return GRN if p < 50 else (YEL if p < 80 else RED)
def lim_color(p): return ACC if p < 85 else RED      # лимит на исходе → тревога

def short_path(p, maxlen):
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    if len(p) <= maxlen:
        return p
    parts = p.split(os.sep)
    head, tail = parts[:1], parts[-2:]
    mid = [s[:1] for s in parts[1:-2] if s]
    out = os.sep.join(head + mid + tail)
    return out if len(out) <= maxlen else "…" + p[-(maxlen-1):]

def git_branch(start):                            # ветку JSON не отдаёт — читаем .git/HEAD сами
    d = os.path.abspath(start or ".")
    while True:
        gp = os.path.join(d, ".git")
        if os.path.exists(gp):
            break
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    if os.path.isfile(gp):                        # worktree/submodule: ".git" — файл "gitdir: …"
        try:
            line = open(gp, encoding="utf-8").read().strip()
        except Exception:
            return None
        if line.startswith("gitdir:"):
            gp = os.path.normpath(os.path.join(d, line[7:].strip()))
    try:
        ref = open(os.path.join(gp, "HEAD"), encoding="utf-8").read().strip()
    except Exception:
        return None
    if ref.startswith("ref: refs/heads/"):
        return ref[16:]                           # имя ветки
    return ref[:7] if ref else None               # detached HEAD → короткий хэш

# ---------- центр: титул, ранг/усилие, бары ----------
MID_W = 30
title = f"{ACCB}{BOLD}ϟ{RESET} {BOLD}{WHITE}{model_name}{RESET}"   # имя модели — как пришло из JSON

rank = wizard_rank(out_tok)
rank_line = f"{ACC}✦{RESET} {WHITE}{rank}{RESET}"
if effort:
    rank_line += f" {GREY}·{RESET} {BOLD}{WHITE}{effort}{RESET}"  # effort — как пришло из JSON
if thinking:
    rank_line += f" {ACC}✦{RESET}"

def lim_row(glyph, label, val, ts):
    if val is None:
        return f"{GREY}{glyph} {label}  —{RESET}"
    r = reset_in(ts)
    tail = f"  {GREY}⟲ {r}{RESET}" if r else ""          # ⟲ = время до сброса лимита
    return f"{ACC}{glyph}{RESET} {GREY}{label}{RESET} {bar(val,8,lim_color(val))} {lim_color(val)}{round(val):>3}%{RESET}{tail}"

mid = [
    title,
    rank_line,
    f"{ctx_color(used_pct) if used_pct>=80 else ACC}◈{RESET} {GREY}ctx{RESET} {bar(used_pct,8,ctx_color(used_pct))} {ctx_color(used_pct)}{used_pct:>3}%{RESET}",
    lim_row("⧗", "5h ", lim5, lim5_ts),
    lim_row("◐", "7d ", lim7, lim7_ts),
]
mid = [pad(m, MID_W) for m in mid]

# ---------- справа: характеристики (метки по левому краю, значения по правому) ----------
stats = [
    ("↓", GRN,  "IN",   kfmt(in_tok)),
    ("↑", ACC,  "OUT",  kfmt(out_tok)),
    ("◈", ACC,  "CTX",  f"{kfmt(in_tok+out_tok)}/{'1M' if is_1m else str(ctx_size//1000)+'k'}"),
    ("⧗", GREY, "TIME", dur(dur_ms)),
    ("⊚", ACCB, "GAL",  f"${cost:.2f}"),                                       # галлеоны Гринготтса
]
vw = max(len(v) for *_, v in stats)            # ширина значения = самое длинное (CTX часто шире 7)
right = [f"{c}{i}{RESET} {GREY}{l:<4}{RESET} {WHITE}{v:<{vw}}{RESET}" for i, c, l, v in stats]
# ---------- сборка строк ----------
core = [f"{mid[i]}    {right[i]}" for i in range(5)]

# ---------- строка-локация ----------
branch = git_branch(cwd)
content_w = max(vlen(c) for c in core)
deco = vlen("⌂ ") + (vlen("  ⎇ ") + len(branch) if branch else 0)
path = short_path(cwd, max(10, content_w - deco))
loc  = f"{GREY}⌂{RESET} {WHITE}{path}{RESET}"
if branch:
    loc += f"  {ACC}⎇{RESET} {GRN}{branch}{RESET}"

INNER = max(content_w, vlen(loc))

# ---------- рамка в цвете факультета; эмодзи-зверь — в заголовке ----------
# Инфо-строки состоят из глифов ширины 1 → рамка по ним сходится в любом терминале.
# Эмодзи есть только в верхней строке: если терминал рисует его не в 2 ячейки,
# сдвинется лишь правый ВЕРХНИЙ угол, а остальная рамка остаётся ровной.
label  = f"──── {HOUSE_EMOJI}  {HOUSE_NAME} "         # 4 дефиса слева + 2 пробела после эмодзи
dashes = max(0, (INNER + 2) - vlen(label))
top    = f"{PRIM}╭────{RESET} {HOUSE_EMOJI}  {ACCB}{BOLD}{HOUSE_NAME}{RESET} {PRIM}{'─'*dashes}╮{RESET}"
bottom = f"{PRIM}╰{'─'*(INNER + 2)}╯{RESET}"
def boxed(c):
    return f"{PRIM}│{RESET} {pad(c, INNER)} {PRIM}│{RESET}"

# ---------- вывод ----------
print(top)
for c in core:
    print(boxed(c))
print(boxed(loc))
print(bottom)
