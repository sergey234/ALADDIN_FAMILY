# Wellness Rive (r100-7-07) — **HERO-3-07b: те же 3 героя**

**Дата:** 2026-06-04 (PO unified)  
**Задача:** `r100-7-07` · батч **7**  
**Статус:** iOS **07b wired** ✅ · production `.riv` — блокер **HERO-3-07**

> **Единый план Rive (старт здесь):** [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md)  
> **Art / export:** [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) → 02b → 07  
> **Не делать:** 4× `wellness_*.riv` · 160×160

---

## Почему убрали 4 wellness `.riv` и 160×160

| Было в черновике r100-7-07 | Почему убрали | Что вместо |
|--------------------------|---------------|------------|
| 4 файла `wellness_*_hero.riv` | **Не согласовано PO** (canon + HERO-3 — только 3 героя) | Те же 3 `.riv` |
| Artboard 160×160 | Дублирует уже согласованный **Hub 96pt** / масштаб из **360×480** | **48pt** на карточке (`CompanionHeroAvatarView` hubThumbnail) |
| `WellnessPillarRiveHost` | Второй хост = два контракта SM | `CompanionHeroRiveHost` |
| Отдельный «4-й персонаж» на дорожку | Риск: «Принять себя = только единорог» | **Один выбранный герой** на всех карточках; дорожка = **текст + цвет + эмоция** |

**Функционал 4 дорожек не убираем** — убираем только **второй набор картинок**.

---

## Наилучший способ (PO ✅ = согласованный HERO-3)

### Продукт

1. Пользователь **уже выбрал героя** для чата (`companion_selected_character_id`).
2. На **каждой** карточке Wellness — **тот же герой**, но:
   - **Заголовок** = тип помощи («Разобрать мысли»…);
   - **Обводка** = цвет pillar (`color_hex` из API);
   - **Микро-эмоция** = из уже согласованных 12 states Rive.

### Маппинг pillar → `CompanionHeroEmotion` (канон)

| `pillar` | RU (Hub) | Эмоция на превью | API `companion_emotion` |
|----------|----------|------------------|-------------------------|
| `cognitive` | Разобрать мысли | `thinking` | `thinking` |
| `behavioral` | Маленькие шаги | `happy` | `happy` |
| `humanistic` | Принять себя | `comfort` | `comfort` |
| `jung` | Понять себя | `curious` | `curious` |

iOS: `WellnessPillar.companionHubPreviewEmotion` · BE: `wellness_pillar_rive.py`.

**На плитке:** без `mouth_open` (голос — только в чате).

### Техника (уже в коде)

| Файл | Роль |
|------|------|
| `WellnessPillarEmotionView.swift` | 48pt `CompanionHeroAvatarView` + обводка цвета pillar |
| `WellnessHubScreen.pillarCard` | вставка превью над заголовком |
| `wellness_pillar_rive.py` | `companion_emotion`, `rive_source: companion_bundle` |

**Блокер визуала:** пока нет production `.riv` — на карточке fallback (процедурный/PNG), как в Hub Companion. После **07** — живой Rive автоматически.

---

## Что рисуем (один раз)

Только по [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md):

- Figma 36 кадров 360×480 × 3 героя  
- Export **HERO-3-07** → `Resources/Companion/*.riv`  
- **Не рисуем** ничего в `Resources/Wellness/` для Rive

---

## DoD r100-7-07 (после HERO-3-07)

| # | Проверка |
|---|----------|
| 1 | 3 production `.riv` в бандле (riv gate) |
| 2 | Wellness Hub: на карточке **выбранный** герой, разные **цвета/подписи** по pillar |
| 3 | Child: 2 карточки — **тот же** единорог (если выбран), не «другой персонаж на дорожку» |
| 4 | Чат Companion не сломан (тот же бандл) |
| 5 | `GET /pillar/rive` → `companion_emotion` совпадает с iOS |

---

## Handoff ML

```text
r100-7-07 = HERO-3-07b (не отдельный art).
Сделать: HERO-3-07 (3 riv) по COMPANION_HERO_ART_CANON.md.
Wellness: код 07b готов; QA Wellness Hub после riv в бандле.
Не делать: wellness_*_hero.riv, WellnessPillarRiveHost, 160×160 export.
```

---

## DEPRECATED — черновик «4 отдельных riv» (не использовать)

<details>
<summary>Старая ветка плана (архив)</summary>

Отдельные `wellness_{pillar}_hero.riv`, artboard 160×160, `WellnessPillarRiveHost` — **отменено PO 2026-06-04** в пользу 3 героев HERO-3.

</details>

---

*Согласовано с COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md · Hub 96pt · Conversation 56%.*
