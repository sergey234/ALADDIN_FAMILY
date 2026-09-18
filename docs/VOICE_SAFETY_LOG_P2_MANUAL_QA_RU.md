# Voice Safety Log — P2 manual QA (RU)

Сборка: Xcode → scheme **ALADDIN** (+ extension **ALADDINWidgets**).

## P2-01 Недельная сводка
1. Запишите 2–3 заметки с тегами (скажите «проверка», «идея», «не забыть»).
2. Voice Notes → кнопка **Неделя** → sheet со статистикой за 7 дней.
3. Deep link / push: `aladdin://voice/weekly` → Settings → Voice Notes → sheet недели.
4. Воскресенье 19:00 — локальный push (после первого открытия Voice Notes).

## P2-02 Списки «идея» / «не забыть»
1. Фильтр меню: **Идеи** / **Не забыть**.
2. Заметки с `intent_idea` / `intent_remind` видны в соответствующем фильтре.

## P2-03 Локальные напоминания
1. Скажите «не забыть купить воду».
2. Через ~1 час — локальный push «Не забыть» (без EventKit).
3. Тап по push → `aladdin://voice/log`.

## P2-04 Виджет
1. Home Screen → Add Widget → **ALADDIN Widgets** → **Голосовой лог**.
2. После голосовой команды плашка обновляется (App Group `group.ai.aladdin`).
3. Тап по виджету → Voice Notes.

## Запреты (регресс)
- Нет истории буфера ×15, нет фонового pasteboard, нет слежки за ребёнком, нет EventKit.
