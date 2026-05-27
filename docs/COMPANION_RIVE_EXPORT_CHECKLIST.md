# HERO-3-07 — Rive export checklist (2D full-body)

**ADR:** [COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md)  
**План:** [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) §2.2 · §2.3 · §5  
**Figma Companion:** `vwKcGPUUEZjgayEHNn0BJM` — страницы `01`–`03`  
**Onboarding (read-only):** `KvkUdyb5Ll31Z9FSzCbpNl` — OB_01 / OB_02 / OB_05

---

## Цель export

Три файла в бандл iOS:

```
Resources/Companion/unicorn.riv
Resources/Companion/aladdin.riv
Resources/Companion/genie.riv
```

---

## Artboard (Rive Editor)

| Параметр | Значение |
|----------|----------|
| Размер | **360 × 480 pt** (`CompanionHeroLayout.riveArtboardSize`) |
| Формат | **2D** bust/full-body, прямоугольная сцена |
| Стиль | Иллюстрация как **OnboardingHero_01/02/05** (не 3D) |
| Safe zone лица | min **96 pt** короткая сторона (MIMIC-Q1) |

---

## State Machine

**Inputs (Number/String):**

- `emotion` — строки: `idle` · `happy` · `listening` · `speaking` · `alert` · `comfort` · `celebrate` · `thinking` · `sad` · `playful` · `curious` · `nostalgic` · `excited`
- `mouth_open` — **0…1** (speaking + TTS)

**12 контент-постеров** в Figma 02; `speaking` — фаза в Motion, не 13-й столбец сетки.

---

## По героям

| `character_id` | Референс онбординга | Особенности Motion |
|----------------|---------------------|-------------------|
| `unicorn` | OB_05 mood | Пружинный bob, без жёстких прыжков на sad |
| `aladdin` | OB_01 | Сдержанный; без дыма джина |
| `genie` | OB_02 (`103:53`) | Дым/искры только playful/speaking; **не** на sad/comfort |

---

## Export

1. Export → `.riv` per character.  
2. Положить в `ALADDIN_iOS/Resources/Companion/`.  
3. Проверка размера:

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
```

4. Xcode: файлы в target **Companion** folder (Copy Bundle Resources).  
5. Device: **HERO-3-08** — `CompanionHeroRiveHost` + `emotion` / `mouth_open`.  
6. QA: **HERO-3-11** — MOTION-Q1…Q2, MIMIC-Q1, D10.

---

## Текущее состояние бандла (2026-05-26)

| Файл | В `Resources/Companion/` | Size gate | Примечание |
|------|--------------------------|-----------|------------|
| `unicorn.riv` | ✅ ~15 KB | OK | placeholder — заменить production art |
| `aladdin.riv` | ✅ ~15 KB | OK | placeholder |
| `genie.riv` | ✅ ~15 KB | OK | placeholder — заменить production art |

**HERO-3-08:** `RiveRuntime` через **SPM** (`rive-ios` в `ALADDIN.xcodeproj`) или `pod install` + Podfile.

## DoD HERO-3-07

- [x] `unicorn.riv` в бандле, &lt;500 KB (placeholder ⏳ art)  
- [x] `aladdin.riv` в бандле, &lt;500 KB (placeholder ⏳ art)  
- [x] `genie.riv` в бандле, &lt;500 KB (placeholder ⏳ art)  
- [ ] size gate **22** — exit 0  
- [ ] На Conversation сцена **56%** показывает Rive (не emoji fallback)  
- [ ] `listening` / `thinking` / `speaking` различимы без текста  
- [ ] `mouth_open` виден при TTS ≥1 s  

---

## Fallback

Если `.riv` нет — `CompanionHeroAnimatedView` (процедурный 2D placeholder). После export fallback не должен срабатывать на production build.
