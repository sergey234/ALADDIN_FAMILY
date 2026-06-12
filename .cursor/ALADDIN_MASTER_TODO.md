# ALADDIN — сводный мастер-план (все согласованные задачи)

**Версия:** 1.0 · **Дата:** 2026-06-11  
**Build:** 230 (`32387ab0`) · **Корень:** `ALADDIN_iOS`  
**Single source для Cursor todos:** этот файл + детали в связанных планах

| Документ | Содержание |
|----------|------------|
| **Этот файл** | Все задачи UX + perf + antifake + wellness — один реестр |
| `.cursor/UX_AUDIT_COMPANION_BATCHES_TODO.md` | Детали батчей 0–10, верификация отзыва |
| `.cursor/ANTIFAKE_MASTER_ROADMAP.md` | Antifake M1–M4, Apple limits, риски |
| `.cursor/ANTIFAKE_PRODUCTION_TODO.md` | 72 задачи `af-*` (сервер/ML/deploy) |
| `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` | Текст экрана «Ограничения Apple» |

---

## Сводка прогресса

| Категория | Всего | ✅ | 🟡 частично | ⬜ |
|-----------|-------|-----|-------------|-----|
| **Cursor track (батчи + ключевые id)** | **36** | **5** | **8** | **23** |
| UX audit (детальные id) | ~65 | ~25 | ~15 | ~25 |
| Antifake `af-*` | 72+ | ~25 | — | ~47 |
| **Итого уникальных id** | **~100+** | — | — | — |

**✅ Закрыто:** VPS IoT deploy, VisualLogger off, wellness readable input, build 230 UX-код (часть), iOS Antifake Hub BATCH2, backend antifake API.  
**🔴 Главные пробелы:** ux-1-06 (Hub на экране Защиты), perf-1 (главная 3.1 с), af-3/af-10 workers на VPS, device QA.

---

## Часть A — Cursor todos (36 пунктов — отслеживание в панели)

> Эти id **не удалять** — они соответствуют согласованному списку из обсуждений.

| # | Cursor id | Задача | P | Статус |
|---|-----------|--------|---|--------|
| 1 | `ux-verify-01` | QA build 230 + PERF-0: 8 пунктов отзыва на устройстве/симуляторе | P0 | ⬜ |
| 2 | `ux-2-iot` | VPS: `components.py` + `iot_security_agent` deploy | P0 | ✅ |
| 3 | `perf-0-logger` | VisualLogger overlay off по умолчанию (perf-0-01/02) | P0 | ✅ |
| 4 | `perf-0-03` | RELEASE: убрать дубли SETTINGS_DIAG + MasterLogger | P2 | ⬜ |
| 5 | `perf-1-main` | Главная: один bootstrap, skeleton, lazy init <300ms/<1s | P0 | ⬜ |
| 6 | `perf-2-support` | Support FPS: defer sync, metrics off main, FAQ spring | P1 | ⬜ |
| 7 | `fix-notif` | NotificationService через shared / AppCoordinator DI | P1 | ⬜ |
| 8 | `fix-sf` | SF Symbol fallbacks iOS 17 | P2 | ⬜ |
| 9 | `fix-settings` | Один debounced save notifications (не ×3) | P2 | ⬜ |
| 10 | `ux-1-antifake` | Batch 1 Antifake discoverability (umbrella) | P0 | 🟡 |
| 11 | `ux-3-support` | Batch 3 Support: lazy FAQ/debounce — device QA | P1 | 🟡 |
| 12 | `ux-4-contacts` | Batch 4: Telegram + убрать адрес | P1 | ✅ |
| 13 | `ux-5-back-nav` | Batch 5: wellness back → AI поддержка, не Main | P1 | 🟡 |
| 14 | `ux-5-04` | Assessments: `navigateToWellnessScreen` вместо `navigateTo` | P1 | ⬜ |
| 15 | `ux-5-05` | UITest: back Dreams/Reflective/Timeline → AI поддержка | P1 | ⬜ |
| 16 | `ux-6-dreams` | Batch 6 Сны: input ✅, API/offline/placeholder QA | P0 | 🟡 |
| 17 | `ux-7-hero` | Batch 7 Герой: spinner/mic ✅, чипы tooltip + контраст | P1 | 🟡 |
| 18 | `ux-8-reflective` | Batch 8 Глубокое исследование: copy + confirm sheet | P1 | 🟡 |
| 19 | `ux-9-legal` | Batch 9 Правила AI: offline ✅, серверный fetchLegal | P1 | 🟡 |
| 20 | `ux-10-perf` | Batch 10: глобальная nav perf <200ms | P1 | ⬜ |
| 21 | `ux-commit` | Commit + push PERF-0 и perf fixes (только по запросу) | — | ⬜ |
| 22 | `ux-6-input-global` | wellnessReadableInput глобально в WellnessMultilineField | P0 | ✅ |
| 23 | `ux-6-06` | Дневник снов «недоступен» — VPS FEATURE_WELLNESS_JUNG + offline | P0 | ⬜ |
| 24 | `ux-8-05` | Sheet «Продолжить в чате?» перед переходом в героя | P1 | ⬜ |
| 25 | `ux-1-06` | **P0** Карточка Antifake на `03_NetworkProtectionScreen` | P0 | ⬜ |
| 26 | `ux-1-07` | (опционально) строка в аккордеоне «Защита от угроз» | P2 | ⬜ |
| 27 | `ux-1-08` | Merge ThreatProtection ↔ NetworkProtection | P1 | ⬜ |
| 28 | `ux-1-09` | Инструкция Share Safari→ALADDIN в Помощь | P1 | ⬜ |
| 29 | `ux-8-07` | Info-блок на экране «Глубокое исследование» | P1 | ⬜ |
| 30 | `ux-8-04` | Subtitle + copy 5 карточек reflective (без «нет экрана») | P1 | ⬜ |
| 31 | `ux-1-10` | Честный copy: звонок = запись после, не автоблок | P1 | ⬜ |
| 32 | `af-m1-hub` | M1: Hub на Защите + workers ML (af-3, af-10, af-11) | P0 | 🟡 код ✅, VPS deploy ⬜ |
| 33 | `af-m2-calls` | M2: Call Directory + post-call push (af-4-02…05) | P1 | ⬜ |
| 34 | `af-m3-semi` | M3: виджет 5с голос + история (af-4-04, af-6-08) | P2 | ⬜ |
| 35 | `af-8-claims` | docs ANTIFAKE_USER_FACING_CLAIMS + af-8-07 экран Apple | P1 | ⬜ |
| 36 | `af-master-doc` | Мастер-доки: ROADMAP + APPLE_LIMITS + этот файл | — | ✅ |

---

## Часть B — UX Audit (детальные id по батчам)

### Batch 0 — QA baseline

| ID | Задача | Статус |
|----|--------|--------|
| ux-0-01 | Зафиксировать пути воспроизведения 8 пунктов отзыва | 🟡 `docs/UX_AUDIT_QA_BASELINE.md` |
| ux-0-02 | Screen recording IoT / Support / Wellness back | ⬜ |
| ux-0-03 | Backend smoke wellness/IoT/protection | 🟡 частично |

### Batch 1 — Antifake discoverability + AF-VISION

| ID | Задача | P | Статус |
|----|--------|---|--------|
| ux-1-01 | Кнопка «Открыть проверку» у Deepfakes | — | ✅ скрыт от пользователя |
| ux-1-02 | Карточка на ThreatProtectionScreen | — | ✅ скрыт |
| **ux-1-06** | **Карточка на 03_NetworkProtectionScreen** | **P0** | **⬜** |
| ux-1-07 | Строка в аккордеоне (если ux-1-06 мало) | P2 | ⬜ |
| ux-1-08 | Merge ThreatProtection ↔ NetworkProtection | P1 | ⬜ |
| ux-1-09 | Share инструкция в Помощь | P1 | ⬜ |
| ux-1-03 | Coachmark Hub (3 шага) | P2 | ⬜ |
| ux-1-04 | QA doc путь Главная→Защита→Проверить фейк | P2 | ⬜ |
| ux-1-05 | Device/Identity coverage без дубля | P2 | ⬜ |
| **ux-1-10** | **Честный copy звонков** | **P1** | **⬜** |
| af-8-07 | Экран «Ограничения Apple» | P1 | ⬜ |

**AF-VISION фазы:** M1 (ручная) → M2 (Call Directory) → M3 (5 сек виджет) → M4 (не обещаем PSTN intercept)

### Batch 2 — IoT

| ID | Задача | Статус |
|----|--------|--------|
| ux-2-01 | `iot_security_agent` в ALL_COMPONENTS VPS | ✅ deploy |
| ux-2-02 | Единый IoT путь / redirect Network Protection | 🟡 |
| ux-2-03 | Правильные ошибки IoT (не antifake job) | 🟡 |
| ux-2-04 | iotThreats → Device Hub IoT tab | ⬜ |

### Batch 3 — Support perf

| ID | Задача | Статус |
|----|--------|--------|
| ux-3-01 | LazyVStack FAQ 10+«ещё» | ✅ код |
| ux-3-02 | Debounce поиска 300ms | ✅ |
| ux-3-03 | Убрать glass с FAQ | ✅ |
| ux-3-04 | Instruments Time Profiler nav | ⬜ |
| ux-3-05 | Отложить `.task` после transition | ⬜ |
| ux-3-06 | Telegram кнопка выше FAQ / sticky | ✅ |

### Batch 4 — Контакты Telegram

| ID | Статус |
|----|--------|
| ux-4-01…04 | ✅ код build 230 |

### Batch 5 — Wellness back navigation

| ID | Задача | Статус |
|----|--------|--------|
| ux-5-01 | `finishWellnessFlow()` на subpages | ✅ 7 экранов |
| ux-5-02 | Persist companionHome tab | ⬜ |
| ux-5-03 | UITest Dreams → hub | ⬜ |
| **ux-5-04** | Assessments navigateToWellnessScreen | ⬜ |
| **ux-5-05** | UITest back nav расширить | ⬜ |

### Batch 6 — Сны и образы

| ID | Задача | Статус |
|----|--------|--------|
| ux-6-01 | Readable input глобально | ✅ |
| ux-6-01b | Audit Values Form contrast | ⬜ |
| **ux-6-06** | API FEATURE_WELLNESS_JUNG + offline save | ⬜ |
| ux-6-02 | Disclaimer 1 строка + sheet | ✅ |
| ux-6-03 | Placeholder поля сна | ⬜ |
| ux-6-04 | Сохранение + список | ⬜ |
| ux-6-05 | Coachmark первый визит | P2 ⬜ |

### Batch 7 — Разговор с героем

| ID | Задача | Статус |
|----|--------|--------|
| ux-7-01 | ProgressView loadState | ✅ |
| ux-7-02 | Spinner isSending | ✅ |
| ux-7-03 | Mic hint «Нажми микрофон» | ✅ |
| ux-7-04 | Tooltip / copy чипов | ⬜ |
| ux-7-05 | Контраст StormMesh глобально | ⬜ |

### Batch 8 — Глубокое исследование

| ID | Задача | Статус |
|----|--------|--------|
| ux-8-01 | Smoke VPS wellness pillar | ⬜ |
| ux-8-02 | Offline pillar fallback | ✅ |
| ux-8-03 | Back returnTo reflective | ✅ |
| **ux-8-04** | Copy 5 карточек + subtitle | ⬜ |
| **ux-8-07** | Info-блок вверху экрана | ⬜ |
| **ux-8-05** | Confirm sheet перед чатом | ⬜ |
| ux-8-06 | Промпт внутри карточки (опционально) | P2 ⬜ |

### Batch 9 — Правила AI

| ID | Статус |
|----|--------|
| ux-9-01…03 offline | ✅ |
| ux-9-04 product review | ⬜ |
| Серверный fetchLegal | 🟡 |

### Batch PERF-0 — VisualLogger

| ID | Статус |
|----|--------|
| perf-0-01, perf-0-02 | ✅ локально |
| perf-0-03 | ⬜ |
| perf-0-04 | ⬜ doc |

### Batch PERF-1 — Главная cold start

| ID | Задача | Статус |
|----|--------|--------|
| perf-1-01 | Один bootstrap | ⬜ |
| perf-1-02 | endScreenLoad по первому кадру | ⬜ |
| perf-1-03 | Skeleton / кеш | ⬜ |
| perf-1-04 | Lazy AntivirusManager | ⬜ |
| perf-1-05 | Defer MetricsService +2s | ⬜ |
| perf-1-06 | Defer subscription sync | ⬜ |

### Batch PERF-2 — Support FPS

| ID | perf-2-01…04 | ⬜ |

### Batch FIX-NOTIF / FIX-SF / FIX-SETTINGS

| Batch | ID | Статус |
|-------|-----|--------|
| FIX-NOTIF | fix-notif-01…03 | ⬜ |
| FIX-SF | fix-sf-01…02 | ⬜ |
| FIX-SETTINGS | fix-settings-01…02 | ⬜ |

### Batch 10 — Nav perf

| ID | ux-10-01…04 | ⬜ |

---

## Часть C — Antifake (фазы M1–M4)

### Apple: можем / не можем

| Ожидание | Можем? | Когда |
|----------|--------|-------|
| Предупреждение при звонке мошенника | Частично | M2 — номер в базе |
| Распознать поддельный голос в эфире | Полuавто | M3 — кнопка 5 с |
| Автоматически положить трубку | Только список | M2 Call Directory |
| Блок спама по номеру | Да | M2 |
| Проверка фейковых новостей | Да | M1 текст, M2 Share |
| Deepfake видео | Да (файл) | M1, не live |
| Тумблеры «Защита» = перехват звонка | **Нет** | серверные агенты |

### M1 — «Работает руками» (2–3 нед) ← ТЕКУЩИЙ ФОКУС

| # | Задача | ID | Статус |
|---|--------|-----|--------|
| 1 | Карточка на экране Защиты | ux-1-06 | ⬜ |
| 2 | Честные тексты | ux-1-10 | ⬜ |
| 3 | Экран Apple limits | af-8-07 | ⬜ |
| 4 | Workers ML на VPS | af-3-*, af-10-* | ⬜ |
| 5 | Prod smoke | af-11-* | ⬜ |

**Критерий M1:** Главная → Защита → карточка → Hub 4 вкладки → вердикт без mock.

### M2 — «Проактивная защита» (+4–6 нед)

| # | Задача | ID |
|---|--------|-----|
| 1 | Call Directory Extension | af-4-02 |
| 2 | Post-call push | af-4-03 |
| 3 | Spoof heuristics | af-4-05 |
| 4 | Синк чёрного списка | af-4-09 |
| 5 | Share help | ux-1-09 |
| 6 | Marketing claims | af-8-06 |

### M3 — «Почти автомат» (+6–8 нед)

| # | Задача | ID |
|---|--------|-----|
| 1 | Виджет 5 сек голос | af-4-04 |
| 2 | История 50 проверок | af-6-08 |
| 3 | AI tool antifake | af-7-03, af-7-04 |
| 4 | Clipboard opt-in | af-7-06 |
| 5 | Семейные алерты | af-12-05 |

### M4 — не обещаем (маркетинг запрещён)

- Прослушивание всех PSTN в фоне  
- Автосброс по ML без списка  
- Перехват FaceTime / видеочатов  
- 100% без `uncertain`

### Чёрная шляпа — риски

| Риск | Последствие | Митигация |
|------|-------------|-----------|
| Обещать автоперехват PSTN | App Store reject, иски | af-8-06, af-8-07, ux-1-10 |
| Авто-сброс по ML | Блок банка/врача | Только Call Directory список |
| Фоновый микрофон | Privacy manifest | Только по кнопке |
| Ложный «фейк» на новости | Потеря доверия | uncertain + reasons[] |
| Нагрузка VPS видео | Падение сервера | af-3 очередь, af-10 nginx |
| Hub не найти | «140 задач — где?» | ux-1-06 |

### Antifake iOS — уже в коде ✅

Hub 4 вкладки, Share Extension, deep link, APIService, verdict cards, ThreatProtection card (скрыт), unit tests.

### Antifake server — уже в коде ✅ / не на prod ⬜

| ✅ API routers | ⬜ prod gap |
|----------------|------------|
| check text/url/audio/video/call | af-3 workers Redis/RQ |
| premium gate, jobs scaffold | af-10 nginx 100MB |
| smoke script | af-11 QA gate |

**Полный реестр 72 `af-*`:** `.cursor/ANTIFAKE_PRODUCTION_TODO.md`

---

## Часть D — Приоритет выполнения (рекомендуемый порядок)

```
Неделя 1:
  ux-1-06 → ux-1-10 → af-8-07
  af-10 + af-3 deploy worker
  af-11 smoke
  ux-verify-01 device QA

Неделя 2:
  perf-1-main (главная 3.1с)
  ux-6-06 dream journal API
  fix-notif

Неделя 3–4:
  af-4-02 Call Directory
  af-4-03 post-call
  ux-1-09 Share help

Неделя 5+:
  perf-2, ux-8-04/05/07, ux-5-04/05
  af-m3 widget + history
```

---

## Часть E — Ответы на 8 пунктов отзыва (статус)

| # | Проблема | Вердикт |
|---|----------|---------|
| 1 | Antifake не найти | 🔴 нужен ux-1-06 |
| 2 | IoT ресурс не найден | 🟡 VPS ✅, проверить на 230 |
| 3 | Support зависает | 🟡 код ✅, PERF-2 ⬜ |
| 4 | Контакты Telegram | ✅ код |
| 5 | Микрофон / чипы | 🟡 mic ✅, ux-7-04 ⬜ |
| 6 | Сны белый текст | ✅ ux-6-01; API ⬜ |
| 7 | Правила AI | 🟡 offline ✅ |
| 8 | Назад → Main | 🟡 код ✅, QA ⬜ |
| 9 | Глубокое исследование | 🟡 offline ✅, copy ⬜ |

---

## Как обновлять

1. Менять статус в **этом файле** (таблица A — Cursor ids).  
2. Детали UX — `UX_AUDIT_COMPANION_BATCHES_TODO.md`.  
3. Детали antifake — `ANTIFAKE_PRODUCTION_TODO.md`.  
4. Cursor todos — **36 id из таблицы A**, не удалять при добавлении af-*.

---

*ALADDIN Master TODO v1.0 · объединяет все согласованные задачи 2026-06-09…2026-06-11*
