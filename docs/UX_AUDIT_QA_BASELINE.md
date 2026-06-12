# UX Audit — QA Baseline (build 229)

**Дата:** 2026-06-12 · **Статус:** Batch 0 зафиксирован перед правками.

## ux-0-01 — Шаги воспроизведения

| # | Проблема | Шаги | Ожидание сейчас | Файл |
|---|----------|------|-----------------|------|
| 1 | Antifake не найти | Главная → Защита → Deepfakes | Только тумблер | `ProtectionCategoryRow.swift` |
| 2 | IoT ресурс не найден | Защита → IoT ИЛИ Сеть → IoT Security | Красная ошибка / 404 | `DeviceIoTPanelViewModel`, `components.py` |
| 3 | Support зависает | Настройки → Помощь и поддержка | Лаг при открытии/скролле | `13_SupportScreen.swift` |
| 4 | Медленная навигация | Любой переход между экранами | 1–2 с задержка | `NavigationManager.swift` |
| 5 | Контакты | Политика → Контакты | Email + адрес Самара | `LocalizationManager` |
| 6 | Сны: белый текст | Мир героев → AI поддержка → Сны | Текст в поле не виден | `WellnessDreamJournalScreen.swift:65` |
| 7 | Назад из wellness | AI поддержка → Сны → Назад | Попадаем на Главную (разговор) | `goBack()` vs `finishWellnessFlow()` |
| 8 | Глубокое исследование | AI поддержка → Глубокое → карточка | «Не удалось выбрать направление» | `WellnessReflectiveModeScreen` pillar API |

## ux-0-02 — Evidence «до»

- [ ] Screen recording: IoT toggle fail
- [ ] Screen recording: Support scroll freeze
- [ ] Screen recording: Wellness back → Main

## ux-0-03 — Backend smoke (2026-06-12)

| Endpoint | Результат из CI-агента |
|----------|------------------------|
| `GET /api/health` | ⏱ timeout (8s) — проверить с Mac/VPS |
| `GET /api/wellness/reflective/modes` | ⏱ timeout |
| `GET /api/iot/status/home_default` | ⏱ timeout |

**Действие:** повторить локально: `curl -s -m 8 http://149.154.65.180:8002/api/health`

---

*Обновлять после каждого batch: PASS/FAIL в колонке «после правки».*
