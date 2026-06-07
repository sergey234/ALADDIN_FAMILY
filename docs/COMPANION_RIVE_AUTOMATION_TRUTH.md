# Rive — что можно автоматизировать, а что нет (честно)

> **2026-06-04** · Ответ на «надо ли всё рисовать в Rive?» и «сделай сам».

---

## Короткий ответ

**Нет — не нужно заново рисовать трёх героев с нуля в Rive.**

**Да — 12 разных мимик «как в Disney» без участия человека или платного RiveMCP сейчас автоматизировать нельзя** (нет 12 разных картинок в Figma, нет API к вашему файлу `editor.rive.app/.../2319314`).

---

## Что ML уже сделала автоматически (без ваших кликов)

| Что | Как | Статус |
|-----|-----|--------|
| `unicorn.riv` production | HeroSM + 13 triggers + `mouth_open` | ✅ ~158 KB |
| `aladdin.riv` / `genie.riv` | Скрипт подставил **свой PNG** в SM единорога | ✅ ~295 / ~223 KB |
| Gate iOS | ≥25 KB, <500 KB, триггеры в файле | ✅ PASS |
| PNG masters | 360×480 в repo + Documents + Disk | ✅ |

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/companion_07_automated_pipeline.sh
```

**iOS уже умеет:** `triggerInput("happy")` + `mouth_open` — см. `CompanionHeroRiveHost.swift`.

---

## Что НЕ может сделать Cursor / ML сейчас

| Блокер | Почему |
|--------|--------|
| Ваш файл [editor.rive.app/.../2319314](https://editor.rive.app/file/untitled/2319314) | Нет доступа к **вашему** Cadet-логину и облаку Rive |
| RiveMCP | **3/3 free exports исчерпаны** — нужен `RIVEMCP_LICENSE_KEY` |
| 12 разных лиц из Figma | v1.1 = **одна** картинка на 12 имён эмоций |
| Runtime `.riv` → правка | Editor **не открывает** runtime для edit |

---

## Три пути (лучший для плана — **A**)

### A — Автоматический (рекомендуем сейчас) ✅

1. Оставить **3 `.riv` в бандле** (скрипт выше).
2. Приложение показывает **Rive** на iPhone (не placeholder PNG).
3. Эмоции переключаются по triggers; **12 визуально разных мимик** — улучшение v2 (Editor или RiveMCP).

**Для HERO-3-07 MVP→production bundle:** этого достаточно для инженерии и device QA.

### B — RiveMCP (~$10/мo) — ML делает SM в Cursor

1. Ключ: [rivemcp.stunning.gg](https://rivemcp.stunning.gg) → `RIVEMCP_LICENSE_KEY` в `~/.cursor/mcp.json`.
2. Reload Window → Agent вызывает `user-rivemcp-*` (create SM, triggers, export).
3. **Не рисует** OB-art 1:1 — нужен PNG import + доработка.

### C — Минимум в веб-редакторе (вы уже начали)

Только если нужны **12 различимых лиц** для GATE-EMO:

- Не redraw всего героя — **слои рот/брови** или **Generate Artboard** + HeroSM.
- Export `.riv` → `Resources/Companion/`.
- Сохранить `.rev` backup.

---

## Ваш веб-проект `ALADDIN_unicorn`

Картинка на сцене — **хорошо**. Дальше **не обязательно** рисовать тело:

1. **Animate → HeroSM** (если пусто — скопировать логику из production `unicorn.riv` нельзя напрямую).
2. Или **не трогать** веб-файл — использовать **уже готовый** `Resources/Companion/unicorn.riv` в iOS.

---

## Итог одной фразой

**ML уже собрала 3 production `.riv` для iPhone автоматически; ручная отрисовка в Rive нужна только для «12 разных лиц» уровня GATE-EMO — или купить RiveMCP / нанять 2–4 ч аниматора.**
