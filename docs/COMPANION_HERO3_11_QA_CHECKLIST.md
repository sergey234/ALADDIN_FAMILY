# HERO-3-11 — QA: D10 + MOTION-Q + MIMIC-Q + SPEECH-Q

**Обновлено:** 2026-05-27  
**Зависимости:** build **209+** · [08b](./COMPANION_08B_DEVICE_CHECKLIST.md) PASS на **реальном iPhone** · [HERO-3-17](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md) sign-off  
**Параллельно:** [HERO-3-07](./COMPANION_RIVE_EXPORT_CHECKLIST.md) (Figma → Rive → production `.riv`) — улучшает MIMIC-Q/D10, но **не блокирует** старт 11 на placeholder `.riv`

**Трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) · **D10 полный:** [FINAL_PLAN § GATE-DIALOG](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md)

---

## Сводка подзадач

| ID | Что | Где | Статус |
|----|-----|-----|--------|
| **11a** | Автотесты BE (SPEECH-Q5 + companion pytest) | CI / локально | ✅ 46 passed (2026-05-27) |
| **11b** | Device: MOTION-Q1–5, MIMIC-Q1–6, **D10** | iPhone, Мир героев | ⏳ |
| **11c** | Повтор MIMIC-Q1 после **HERO-3-07** (production art) | device | ⏳ после 07 |

---

## Протокол (заполнить после 11b)

| Поле | Значение |
|------|----------|
| Дата | |
| Тестер | |
| Устройство | |
| iOS | |
| Build | 209 |
| Герои проверены | unicorn · aladdin · genie (genie только teen/parent) |
| Итог 11b | PASS / FAIL |
| Ссылка на скриншоты/запись | |

---

## 11a — автоматика (до устройства)

```bash
cd mobile_apps/ALADDIN_iOS
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
PYTHONPATH=. python3 -m pytest Tests/test_companion*.py -q
```

**SPEECH-Q5** покрыт pytest (`test_companion_persona_speech.py` и связанные).  
**Критерий 11a PASS:** exit 0, без skip критичных тестов.

---

## Навигация (device)

1. **Kids → Игры → Мир героев** → вкладка **Главное**.
2. Для **MOTION-Q4 / D10** — по очереди герои: вкладка **Герои** → выбор → **Главное**.
3. **genie** — только профиль teen/parent (child не должен видеть в списке).

---

## D10 — спектр эмоций (5 мин × герой)

Отправить по одной реплике, фиксировать **подпись эмоции** на сцене и **лицо Rive** (placeholder допустим, но **движение/state должны меняться**).

| # | Реплика | Ожидаемый state (контент) | PASS если |
|---|---------|---------------------------|-----------|
| 1 | «Ура, я получил пятёрку!» | happy / excited / celebrate | Не alert, не только idle |
| 2 | «Мне грустно сегодня» | sad / comfort | **Без** playful / ✨ overlay |
| 3 | «Расскажи анекдот!» | playful / happy | В тексте есть лёгкий юмор PG |
| 4 | «Мне пришло подозрительное письмо со ссылкой» | alert | Не happy |

**FAIL:** все 4 реплики выглядят одинаково; краш; только emoji без Rive.

---

## MOTION-Q (движение / фазы)

| ID | Действие | PASS |
|----|----------|------|
| **MOTION-Q1** | Нажать mic → в &lt;300 ms «слушает» (listening); отпустить → thinking | ✅ / ❌ |
| **MOTION-Q2** | Ответ с озвучкой → speaking + рот/движение ≥1 s | ✅ / ❌ |
| **MOTION-Q3** | После «Мне грустно» — sad/comfort, без весёлого прыжка | ✅ / ❌ |
| **MOTION-Q4** | Скрин listening у unicorn / aladdin / genie — **различимы** | ✅ / ❌ |
| **MOTION-Q5** | D10 на **каждом** доступном герое — 4 разных state | ✅ / ❌ |

---

## MIMIC-Q (лицо / 12 state)

> На placeholder `.riv` проверяем **смену state и отсутствие wrong overlay**; pixel-perfect MIMIC-Q1–6 — повтор после **07**.

| ID | Проверка | PASS |
|----|----------|------|
| **MIMIC-Q1** | happy vs sad vs playful vs alert — **визуально разные** (скрин) | ✅ / ❌ |
| **MIMIC-Q2** | playful: есть «игривость»; happy без wink-эффекта playful | ✅ / ❌ |
| **MIMIC-Q3** | sad vs comfort — различимы (не один и тот же M6) | ✅ / ❌ |
| **MIMIC-Q4** | thinking — не путается с curious | ✅ / ❌ |
| **MIMIC-Q5** | speaking — рот/движение при TTS или stream | ✅ / ❌ |
| **MIMIC-Q6** | sad/comfort — **нет** ✨ playful overlay (HERO-3-24) | ✅ / ❌ |

---

## SPEECH-Q (текст / тон — device)

| ID | Сценарий | PASS |
|----|----------|------|
| **SPEECH-Q1** | child + unicorn: «расскажи шутку» — PG, без едкости | ✅ / ❌ |
| **SPEECH-Q2** | teen + genie: 2 msg — ≥1 каламбур, без насмешки над ребёнком | ✅ / ❌ |
| **SPEECH-Q3** | teen + genie: «мне грустно» — comfort, **0 шуток** | ✅ / ❌ |
| **SPEECH-Q4** | parent + aladdin: обычный вопрос — без навязанного юмора | ✅ / ❌ |
| **SPEECH-Q5** | pytest (11a) | ✅ auto |
| **SPEECH-Q6** | Текст в чат → **слышен TTS** (Моё: «Озвучивать ответы» вкл.) | ✅ / ❌ |

---

## Связь с HERO-3-07 (Figma → `.riv`)

| Этап | Что даёт для 11 |
|------|------------------|
| Сейчас (placeholder `.riv`) | MOTION-Q, D10, базовый MIMIC-Q6/24 |
| После production `.riv` | **11c** — полный MIMIC-Q1 сетка 12 state, GATE-EMO EMO-2 |
| Figma не готов | **не блокирует** 11b на placeholder |

---

## Закрытие в трекере

- [ ] **11b PASS** на device → `[x]` **HERO-3-11**
- [ ] Обновить [матрицу](./COMPANION_HERO3_READINESS_MATRIX.md)
- [ ] Следующий шаг: **GATE-HERO-3-IOS-α** (если ещё не закрыт) → **GATE-EMO** после **07** → TestFlight
