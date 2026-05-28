# HERO-3-07 — аудит «6 шляп» (целостность 100%)

**Дата:** 2026-05-28 · **Задача:** production `.riv` ×3  
**Краткий brief:** [COMPANION_RIVE_ANIMATOR_BRIEF.md](./COMPANION_RIVE_ANIMATOR_BRIEF.md)  
**Дополнение к плану:** [COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md)

---

## Вердикт (синяя шляпа)

| Критерий | Статус |
|----------|--------|
| PO lock masters | ✅ unicorn v2 · aladdin OB_01 · genie OB_03 |
| Figma 36 frames | ✅ |
| iOS host готов | ✅ `CompanionHeroRiveHost` |
| Имена state = iOS | ✅ 13 триггеров (см. supplement §3) |
| Motion/Mimic spec | ✅ sign-off 2026-05-26 |
| **Готовность к export** | ✅ **можно начинать 07** |

**Definition of Done 07:** 3 файла в `Resources/Companion/`, gate exit 0, device **11c** MIMIC-Q1, **GATE-EMO**.

---

## ⚪ Белая шляпа — факты

| Факт | Следствие для аниматора |
|------|-------------------------|
| Artboard **360×480 pt** | Совпадает с `CompanionHeroLayout.riveArtboardSize` |
| Один `.riv` на `character_id` | Не 12 файлов; 12+ фаз — **внутри** SM |
| iOS: `triggerInput` + `setInput("mouth_open")` | Имена **строго** как в supplement §3 |
| Figma v1.1 = 1 PNG × 12 имён | Лица/позы **рисуете в Rive**, не ждите 12 PNG |
| Placeholder ~15 KB в бандле | Заменить production; fallback отключится |
| Лимит **&lt; 500 KB** / файл | Оптимизация mesh/растров |
| child **не** видит genie | genie.riv всё равно для teen/parent |

---

## 🔴 Красная шляпа — что должен почувствовать пользователь

| Аудитория | Единорог | Аладдин | Джин |
|-----------|----------|---------|------|
| Ребёнок | Мягкий друг, не страшно | — (не его герой в child) | — |
| Teen | — | Наставник, без «клоунады» | Магия + умеренный юмор |
| Родитель | — | Спокойно, уважительно | Остроумие без насмешки |
| При грусти | comfort, **0** искр | то же | **0** дыма/шуток |

**Красная линия:** sad/comfort **никогда** не выглядят как playful (MIMIC-Q6, HERO-3-24).

---

## ⚫ Чёрная шляпа — риски и митигация

| Риск | Митигация |
|------|-----------|
| 12 state неразличимы на 96 pt | Лицо в верхних **45%** кадра; брови ±4°; скрин 11c |
| genie = OB_07 с UI семьи | Master только **OB_03 headfix**, без сферы |
| aladdin с дымом джина | Без дыма/искр; сдержанный motion |
| unicorn как космический страж | v2 **лавандовый пушистик**, не OB_05 HUD |
| `speaking` забыли в Rive | **Обязательный** trigger (iOS всегда шлёт) |
| `mouth_open` не привязан | Рот в state speaking + Number 0…1 |
| IPA раздувается | &lt; 500 KB, вектор где можно |
| Смешать speaking + sad в одном кадре | Фазы по очереди: speaking → затем content emotion |

---

## 🟡 Жёлтая шляпа — зачем это 100% продукта

- На «Главное» — **большой прямоугольник 56%** с живым героем (не кружок-заглушка).
- D10 / GATE-EMO закрываются только с production art.
- Три узнаваемых персонажа = бренд OB + Kids safety.
- Lip-sync + TTS = ощущение «говорит со мной».

---

## 🟢 Зелёная шляпа — как сделать красиво

1. **Один силуэт** на героя → варианты бровь/веко/рот (слои L1–L5 из плана §2.3).
2. **Cross-fade 200–300 ms** между state.
3. **Акценты по герою** (план §2.2 матрица): пружина / сдержанность / дым.
4. **idle** — лёгкое дыхание 2 s loop (Hub 96 pt тоже читается).
5. Скриншот-сетка **12 state** перед сдачей → приложить к PR/чату.

---

## 🔵 Синяя шляпа — порядок работ

```
День 1: unicorn.riv (проще формы, эталон SM)
День 2: aladdin.riv (сдержанный, без дыма)
День 3: genie.riv (OB_03 + дым только playful/speaking)
Сдача: 3 файла + gate + письмо «готово к 11c»
```

Детали: [PLAN_SUPPLEMENT](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md).

---

*Аудит согласован с [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) §2.2–2.3 и [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md).*
