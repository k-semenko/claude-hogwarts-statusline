---
description: Сменить факультет Hogwarts-statusline (цвет рамки и эмодзи-зверя)
argument-hint: "[gryffindor|slytherin|ravenclaw|hufflepuff]"
---

# Смена факультета Hogwarts

Меняешь факультет тематического statusline. Выбор хранится в
`~/.claude/hogwarts-statusline.json` (поле `house`), статуслайн читает его
при следующей перерисовке.

Дома: **gryffindor** 🦁 · **slytherin** 🐍 · **ravenclaw** 🦅 · **hufflepuff** 🦡
(принимаются префиксы вроде `slyth` и алиасы `lion`/`snake`/`eagle`/`badger`).

Пользователь передал: `$ARGUMENTS`

## Что сделать

1. Определи факультет:
   - если аргумент задан — нормализуй его к одному из четырёх (учитывая префиксы и алиасы);
   - если аргумент пуст — спроси через AskUserQuestion (4 дома, эмодзи в подписях 🦁🐍🦅🦡).

2. Запиши выбор в `~/.claude/hogwarts-statusline.json`:
   - сделай Read файла, если он есть (сохрани прочие поля), иначе создай новый;
   - содержимое — JSON вида `{ "house": "<факультет>" }`.

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
       "padding": 0
     }
     ```
   - запиши файл обратно (Edit/Write), не трогая остальные поля.
   - проверь валидность JSON:
     `python3 -c "import json; json.load(open('/Users/YOUR_USER/.claude/settings.json')); print('OK')"`

4. Подтверди: какой факультет выбран, статуслайн активирован.
