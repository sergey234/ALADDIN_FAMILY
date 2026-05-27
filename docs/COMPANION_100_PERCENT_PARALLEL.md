# Companion → 100%: план · факт · остаток

**Обновлено:** 2026-05-27 · build **210+**

---

## Сводка «кто что закрывает»

| Зона | До 100% продукта | Статус |
|------|------------------|--------|
| **iOS код** (layout 56%, TTS, Hub Rive-превью, voice) | ✅ build 210 | **Готово** |
| **08b** Rive на device | ✅ PASS (user) | **Готово** |
| **11a** pytest | ✅ 46 tests | **Готово** |
| **11b** QA на placeholder | ⏳ ~15 мин iPhone | **Вы** |
| **07** Figma 360×480 → `.riv` ×3 | ⏳ аниматор | **Дизайн** |
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

1. Открыть Figma Companion `01`–`03`, сетка 12 emotions.
2. Rive Editor: artboard **360×480**, SM inputs `emotion` (triggers) + `mouth_open` (0…1).
3. Export → три файла в `Resources/Companion/`.
4. `python3 scripts/companion_riv_size_gate.py --dir Resources/Companion`
5. Device smoke → **11c**.
