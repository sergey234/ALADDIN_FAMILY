# Companion → 100%: план · факт · остаток

**Обновлено:** 2026-05-28 · build **210+**  
**Завтра:** [COMPANION_PLAN_TOMORROW_2026-05-29.md](./COMPANION_PLAN_TOMORROW_2026-05-29.md)  
**Rive / Node / MCP:** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md) · **ML handoff:** [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md)

---

## Сводка «кто что закрывает»

| Зона | До 100% продукта | Статус |
|------|------------------|--------|
| **iOS код** (layout 56%, TTS, Hub Rive-превью, voice) | ✅ build 210 | **Готово** |
| **08b** Rive на device | ✅ PASS (user) | **Готово** |
| **11a** pytest | ✅ 46 tests | **Готово** |
| **11b** QA на placeholder | ⏳ ~15 мин iPhone | **Вы** |
| **02b** Figma 3 страницы × 12 frames | ✅ 36/36 · PO lock OB_03 | **Готово** |
| **07** Rive 360×480 → `.riv` ×3 | ⏳ Editor + [5 steps](./COMPANION_RIVE_EDITOR_5_STEPS.md); MCP черновик `.rev` есть | **Аниматор** |
| **Rive infra** Node + RiveMCP | ✅ 2026-05-28 | [CONNECT doc](./COMPANION_RIVE_CONNECT_NODE_MCP.md) |
| **11c** MIMIC после 07 | ⏳ после export | **Вы + QA** |
| **GATE-P0 / GATE-EMO** | ⏳ после 11b + 07 | **Приёмка** |

**Визуал «полноценный герой» = только HERO-3-07.** До export production `.riv` на «Главное» остаётся placeholder (круг/простая фигура в Rive), не OB_01/02/05.

---

## План vs факт (детально)

| Пункт плана | План | Факт (2026-05-27) |
|-------------|------|-------------------|
| Сцена **56%** прямоугольник | `CompanionHeroLayout` + `conversationFullBody` | ✅ код |
| **3 героя** в API/Hub | unicorn, aladdin, genie (genie не child) | ✅ |
| **Rive** на device | `.riv` + `CompanionHeroRiveHost` | ✅ 08b PASS |
| **Арт героя** full-body | Figma 360×480 → `.riv` | 🟡 placeholder ~15 KB |
| Hub не только emoji | Превью Rive 88pt | ✅ build 210 |
| **Герой говорит** (текст) | TTS на ответ | ✅ `companion_response_tts_enabled` (Моё) |
| **Герой говорит** (mic) | WS + AVSpeech | ✅ |
| Lip-sync | `mouth_open` + TTS | ✅ код; заметность ↑ после **07** |
| **11b** D10/MOTION/SPEECH | device | ⏳ |
| **11c** MIMIC pixel-perfect | после **07** | ⏳ |

---

## Размеры (Figma → Rive → экран)

| Слой | Размер |
|------|--------|
| **Rive artboard** | **360 × 480 pt** |
| **Сцена «Главное»** | ~**56%** высоты, ширина экран − 24 pt, `cornerRadius` 20 |
| **Лицо на экране** | короткая сторона ≥ **96 pt** (MIMIC-Q1) |
| **Hub карточка** | превью **88×88** (круг clip) |
| **Файл** | `< 500 KB` каждый |

Чеклист export: [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)  
Figma: `vwKcGPUUEZjgayEHNn0BJM` · страницы `01`–`03` · **12 эмоций** × 3 героя.

---

## После HERO-3-07 (что изменится на телефоне)

1. Замена `Resources/Companion/{unicorn,aladdin,genie}.riv`.
2. На **«Главное»** — **большой прямоугольник** с иллюстрацией как онбординг (не кружок-заглушка).
3. **12 state** + `mouth_open` в Rive SM — MIMIC-Q / D10 по-настоящему.
4. **11c** — скриншот-сетка 12 эмоций.
5. **GATE-EMO** — закрытие.

Код host/layout **не переписываем** — меняется содержимое `.riv`.

---

## Ваши шаги (QA)

1. **Build 210+** → Мир героев → **Главное**: отправить текст → **слышен голос** (если в «Моё» включено «Озвучивать ответы»).
2. **11b** — [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md).
3. Передать аниматору **07** (Figma + чеклист export).

---

## Дизайн (07) — handoff аниматору

1. Создать в Figma страницы `01`–`03` (сейчас только `00_Spec` — см. [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md)).
2. Сетка 12 emotions × 3 героя (36 фреймов 360×480).
2. Rive Editor: artboard **360×480**, SM inputs `emotion` (triggers) + `mouth_open` (0…1).
3. Export → три файла в `Resources/Companion/`.
4. `python3 scripts/companion_riv_size_gate.py --dir Resources/Companion`
5. Device smoke → **11c**.
