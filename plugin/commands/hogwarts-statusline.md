---
description: Настроить Hogwarts-statusline — факультет, раскладку (v2/classic) и язык фраз (ru/en)
argument-hint: "[gryffindor|slytherin|ravenclaw|hufflepuff] [v2|classic] [ru|en]"
---

# Настройка Hogwarts-statusline

Настройки хранятся в `~/.claude/hogwarts-statusline.json`, статуслайн читает их
при следующей перерисовке.

| Поле | Значения | По умолчанию |
|---|---|---|
| `house` | **gryffindor** 🦁 · **slytherin** 🐍 · **ravenclaw** 🦅 · **hufflepuff** 🦡 (префиксы вроде `slyth` и алиасы `lion`/`snake`/`eagle`/`badger`) | `gryffindor` |
| `layout` | `v2` — строка данных с эмодзи факультета, под ней фраза дня или предупреждение; `classic` — прежняя рамка на семь строк | `v2` |
| `lang` | `ru` · `en` — язык фраз дня и предупреждений | по `$LANG` |

Пользователь передал: `$ARGUMENTS`

## Что сделать

1. Разбери аргументы в любом порядке:
   - имя факультета (с учётом префиксов и алиасов) → `house`;
   - `v2` или `classic` → `layout`;
   - `ru` или `en` → `lang`.
   Если аргументов нет — спроси через AskUserQuestion факультет (4 дома, эмодзи в подписях 🦁🐍🦅🦡)
   и раскладку (`v2` / `classic`).

2. Запиши выбор в `~/.claude/hogwarts-statusline.json`:
   - сделай Read файла, если он есть, и сохрани поля, которые пользователь не менял; иначе создай новый;
   - пример: `{ "house": "slytherin", "layout": "v2", "lang": "ru" }`.

3. Пропиши `statusLine` в `~/.claude/settings.json`:
   - найди путь к установленному скрипту:
     ```bash
     find ~/.claude/plugins/cache/hogwarts-statusline -name "hogwarts-statusline.py" | sort -V | tail -1
     ```
   - прочитай `~/.claude/settings.json` (Read), добавь или замени поле `statusLine`:
     ```json
     "statusLine": {
       "type": "command",
       "command": "python3 \"/абсолютный/путь/к/hogwarts-statusline.py\"",
       "padding": 0,
       "refreshInterval": 60
     }
     ```
     `refreshInterval` нужен, чтобы метка темпа и отсчёты до сброса лимитов тикали и в простое.
   - запиши файл обратно (Edit/Write), не трогая остальные поля.
   - проверь валидность JSON:
     `python3 -c "import json, os; json.load(open(os.path.expanduser('~/.claude/settings.json'))); print('OK')"`

4. Подтверди: какой факультет, раскладка и язык выбраны.
