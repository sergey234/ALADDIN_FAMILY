# Rive — комфортный путь без зависаний PNG (HERO-3-07)

> **2026-06-04** · Исследование: docs Rive, changelog, community.rive.app, Rive 101, GitHub.  
> **Вывод:** Mac **Rive.app 0.8.4941** у части пользователей **зависает на импорте raster** (Assets/Design/⌘V). Это **известный класс багов** редактора, не ошибка наших PNG.

**Cadet на rive.app** — ваш оплаченный unlimited export. **Веб-редактор** стабильнее десктопа.

---

## 1. Что мы выяснили (форумы + официальные источники)

| Факт | Источник |
|------|----------|
| Raster: **Assets → drag → Generate Artboard** или **⌘V** (PNG из буфера) | [Rive 101 Import Raster](https://www.youtube.com/watch?v=hPbgPGJNE78) |
| **Figma → Copy as PNG → ⌘V в Rive** — рекомендованный быстрый путь | [Rive blog Figma paste](https://rive.app/blog/copy-and-paste-from-figma-to-rive) |
| **`.riv` runtime нельзя открыть в Editor** для правки (с Dec 2023) | [GitHub rive-flutter #209](https://github.com/rive-app/rive-flutter/issues/209) |
| **`.rev`** — backup для повторного открытия в Editor (Cadet export/import) | Rive Export menu |
| Зависание import: **audio/image assets get stuck during import** — фиксы в changelog | [rive.app/changelog](https://rive.app/changelog) |
| **⌘⌃⌥⇧.** (Cmd+Ctrl+Alt+Shift+period) — **очистка кэша** редактора | Changelog v0.8.677+ |
| SVG import иногда не виден до **перезапуска** Editor | Changelog Oct 2024 |
| Файлы **>5000×5000** — проблемы памяти; наши **360×480** — OK | Changelog v0.8.428 |

### Почему у вас не грузит (сводка)

1. **Desktop Rive.app** — sandbox + баги импорта с **Disk** (`/Volumes/…`) и иногда с любыми drag-drop.
2. **Маленький тест 64×64 прошёл** — редактор жив, **большой raster** застревает на re-processing.
3. **JPEG/PNG с Desktop/Disk** — тот же симптом → нужен **веб** или **Figma paste** или **сброс кэша + update app**.

---

## 2. ✅ Рекомендуемый путь — **rive.app (браузер)**

> Самый стабильный для Cadet. Не зависит от Mac Rive.app sandbox.

### Шаги (unicorn → aladdin → genie)

1. Откройте **https://editor.rive.app/** (Chrome/Safari).
2. **Log in** — аккаунт **Cadet**.
3. **Personal Files** → **+ New file** → имя `ALADDIN_unicorn`.
4. **Импорт картинки** (выберите **один** способ):

   **A — Upload (предпочтительно в вебе)**  
   - Панель **Assets** → кнопка **+** / **Upload**  
   - Файл: `~/Documents/ALADDIN_Rive_Heroes/unicorn/import.jpg`  
   - Дождаться превью в списке (30–60 сек)  
   - **Правый клик** → **Generate Artboard**

   **B — Figma paste (если upload висит)**  
   - Figma: [Companion Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes)  
   - Страница **01_Unicorn** → frame **360×480** → **Copy as PNG** (`⇧⌘C`)  
   - В Rive web: клик по stage → **⌘V** → artboard создаётся автоматически

   **C — Paste из Preview**  
   - Preview → `import.jpg` → **⌘A ⌘C**  
   - Rive web → **⌘V**

5. Artboard **360×480**, лицо вверху. **Export to RIV** включён на asset (Inspector).
6. **Animate** → State Machine **HeroSM** → 13 triggers + `mouth_open` — см. [5 STEPS](./COMPANION_RIVE_EDITOR_5_STEPS.md).
7. **Export:**
   - **Runtime (.riv)** → скачать → положить в `Resources/Companion/unicorn.riv`
   - **Backup (.rev)** → скачать → `~/Documents/ALADDIN_Rive_Heroes/unicorn/unicorn_source.rev`
8. Повторить для **aladdin**, **genie**.

### После export (ML / терминал)

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_07_verify_unicorn_riv.py unicorn
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion --min-kb 25
```

---

## 3. Если хотите остаться на **Mac Rive.app**

### ⚠️ Обновление не идёт — причины (Mac)

| # | Причина | Ваш Mac |
|---|---------|---------|
| 1 | **Диск заполнен** (нужно ~15+ GB) | **Data 99%**, ~**5.5 GB** free — **главная причина** |
| 2 | Старый **DMG** (`Install Rive`) смонтирован | Finder → Eject «Install Rive» |
| 3 | Auto-update (Sparkle) не распаковал | Ставить **вручную:** https://rive.app/downloads → mac |
| 4 | **Quarantine** (установка из Chrome) | После install: `xattr -cr /Applications/Rive.app` |

**Освободить место:** Trash, `~/Downloads` (~21 GB), Xcode DerivedData (~2.4 GB).

**Ручная переустановка:** закрыть Rive → rive.app/downloads → Production mac → Replace в Applications → `xattr -cr /Applications/Rive.app`.

Если места мало — **не обновляйте Mac app**, работайте в **editor.rive.app** (§2).

### Настройка после установки

1. **Log in** Cadet.
2. **Сброс кэша:** **⌘⌃⌥⇧.** — [changelog](https://rive.app/changelog).
3. Import из `~/Documents/ALADDIN_Rive_Heroes/`, не с Disk.
4. Если import висит → **веб** (§2).

---

## 4. Контракт iOS (не менять)

| Параметр | Значение |
|----------|----------|
| Artboard | **360×480** |
| State Machine | **HeroSM** |
| Triggers ×13 | `idle` … `alert` (см. PATH_A) |
| Number | **`mouth_open`** 0…1 |
| Export | **Runtime .riv** ≥25 KB, <500 KB |
| Backup | **.rev** — хранить локально |

---

## 5. Чего не делать

| ❌ | Почему |
|----|--------|
| Открывать `unicorn.riv` / `aladdin.riv` / `genie.riv` в Editor | Runtime only — серые / не редактируются |
| Drag PNG с **/Volumes/Disk/** | Sandbox + зависания |
| Ждать 10+ минут спиннер | Force quit → другой способ (§2A/B) |
| Vectorize весь герой | Cancel — raster + слои лица достаточно для MVP→100% |

---

## 6. Локальные файлы (готовы)

```text
~/Documents/ALADDIN_Rive_Heroes/
  unicorn/import.jpg + PNG
  aladdin/import.jpg  + PNG
  genie/import.jpg    + PNG
```

Дубликат на Disk: `/Volumes/Disk/герои/герой 3/` — для архива; **для Rive используйте Documents**.

---

## 7. Связанные документы

- [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md) — SM + мимики
- [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) — export в бандл
- [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md §2.3](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) — 12 эмоций
- [COMPANION_RIVE_CADET_MCP_STATUS.md](./COMPANION_RIVE_CADET_MCP_STATUS.md) — Cadet vs MCP

---

*При успешном import в вебе напишите в чат: **«unicorn в вебе OK»** — дальше HeroSM по шагам.*
