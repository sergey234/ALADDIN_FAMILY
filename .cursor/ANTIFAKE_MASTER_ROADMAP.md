# Antifake — мастер-план ALADDIN (итоговый)

> **Единая точка входа:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)  
> **v4 SSOT (134 задачи, 111 ✅):** [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md)  
> Этот файл — **архитектура и legacy `af-3-*` ID**. Статусы v4 — только в REGISTRY + UNIFIED.

**Версия:** 1.3 · **Дата:** 2026-06-15 · **Build:** **232**  
**План v4.1:** `.cursor/ANTIFAKE_TOP_TIER_PLAN.md`  
**Cursor TODO ID:** `af-{TASK-ID}` (A-01…O-03)  
**Корень:** `ALADDIN_iOS`  
**Связанные файлы:**
- `.cursor/ANTIFAKE_PRODUCTION_TODO.md` — legacy `af-*` бэклог (не v4 ID)
- `.cursor/UX_AUDIT_COMPANION_BATCHES_TODO.md` — UX + perf + wellness
- `.cursor/IMPLEMENTATION_BATCHES_TODO.md` — BATCH 2 iOS ✅
- `docs/ANTIFAKE_PRODUCTION_PLAN.md` — техспек API
- `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` — текст для экрана в приложении

---

## 1. Резюме для команды

| Область | Сделано (~%) | Главный пробел |
|---------|--------------|----------------|
| **iOS Hub UI** | ~98% | Device QA Call Directory (D-batch) |
| **Backend API** | ~90% | Batch B hardening (nginx, cron, OpenAPI) |
| **Backend ML workers** | ~85% | B-04 verify, B-08 TTL cron on prod |
| **Copy / legal** | ~70% | G-batch marketing, N-01 manifest |
| **E2E prod QA** | ~75% | R-01 TestFlight checklist, D-batch |

**Критический путь сейчас:** Batch **B** → E → N → R → **Device D-01…D-04** → G-03 bypass off.

---

## 2. Что уже реализовано

### 2.1 iOS (мобильное приложение) ✅

| Компонент | Файлы | Статус |
|-----------|-------|--------|
| **Antifake Hub** — 4 вкладки: Текст, Голос, Видео, Звонок | `AntifakeHubScreen.swift` | ✅ BATCH 2 |
| Синхронная проверка текста/URL | `AntifakeTextCheckViewModel.swift`, `APIService` | ✅ |
| Асинхронная загрузка audio/video + poll job | `AntifakeMediaCheckViewModel.swift` | ✅ |
| Проверка звонка по **записи** + caller_id/display_name | `AntifakeMediaCheckView.swift` | ✅ |
| Verdict card, Premium gate | `AntifakeVerdictCard.swift`, `PremiumGateHandler` | ✅ |
| Share Extension «Проверить в ALADDIN» | `ALADDINAntifakeShare/` | ✅ |
| Deep link `aladdin://antifake/check` | `AntifakeDeepLinkRouter.swift`, `ALADDINApp` | ✅ |
| Навигация deepfakes → Hub (каталог) | `ThreatProtectionCategory.swift` | ✅ |
| Карточка «Проверить подлинность» | `ThreatProtectionScreen.swift` | ✅ **но экран скрыт от пользователя** |
| Кнопка «Открыть проверку» у Deepfakes | `ProtectionCategoryRow.swift` | ✅ на каталоге |
| Coverage rows → Hub | Device/Identity/Family Hub | ✅ |
| Локализация RU/EN antifake | `LocalizationManager.swift` | ✅ |
| Endpoints в AppConfig | `AppConfig.swift` | ✅ |
| Unit tests | `Antifake*Tests.swift`, `SecurityVerdictModelsTests` | ✅ |

### 2.2 iOS — НЕ сделано / не видно пользователю ⬜

| Компонент | ID | Приоритет |
|-----------|-----|-----------|
| Карточка Antifake на **реальном** экране Защиты | `ux-1-06` | **P0** | 🟡 accordion ux-1-07 ✅ |
| Честный copy (звонок = после записи, не автоблок) | `ux-1-10` | P1 | ⬜ |
| Экран «Ограничения Apple» в Hub / Помощь | `af-8-07` | P1 | ⬜ |
| Call Directory Extension (метка «мошенник») | `af-4-02` | P1 | ✅ build 232 · device ⏸ |
| Post-call push «Проверить запись?» | `af-4-03` | P1 | 🟡 build 232 |
| Виджет «5 сек — проверить голос» | `af-4-04` | P2 | ✅ build 232 |
| История 50 проверок | `af-6-08` | P2 | ✅ build 232 |
| AI Assistant tool antifake | `af-7-03`, `af-7-04` | P2 |
| Вкладка «Документ» в Hub (отдельно от видео) | `af-9-06` | P2 |
| Paste/clipboard prompt | M2 | P2 |
| QR-сканер ссылок | M3 | P3 |
| Синк settings deepfakes с сервером | `af-5-01`…`af-5-03` | P1 |

### 2.3 Backend (сервер) ✅

| Компонент | Файл | Статус |
|-----------|------|--------|
| Router `/api/antifake/*` | `app/routers/antifake.py` | ✅ |
| `POST /check/text`, `/check/url` sync | antifake.py | ✅ |
| `POST /check/audio|video|document` → job | antifake.py | ✅ |
| `POST /call/analyze` | antifake.py | ✅ |
| `GET /jobs/{id}` poll | antifake.py | ✅ |
| Premium gate 402/403 | `antifake_premium.py` | ✅ |
| Jobs store (in-memory/DB scaffold) | `antifake_jobs_store.py` | ✅ частично |
| Service + agents wiring | `antifake_service.py` | ✅ |
| Rate limit scaffold | `antifake_rate_limit.py` | ✅ |
| Worker scaffold | `app/workers/antifake_ml_worker.py` | ✅ код есть |
| Wildcard block, no mock guard | main.py gateway | ✅ BATCH 0 |
| `user_protection_settings` DB | migrations | ✅ BATCH 0 |
| Smoke script | `docs/server/test_antifake_prod_smoke.py` | ✅ |

### 2.4 Backend — НЕ сделано / не на prod ⬜

| Компонент | ID | Приоритет |
|-----------|-----|-----------|
| Redis/RQ worker systemd на VPS | `af-3-01`, `af-10-03` | **P0** |
| Таблица `antifake_jobs` persistent | `af-3-02` | P0 |
| Реальный ML pipeline audio/video (не stub) | `af-3-03`, `af-3-04`, `af-1-05` | P0 |
| `GET /api/antifake/metrics` на prod | `af-3-06` | P1 |
| nginx 100MB + timeout для upload | `af-10-01`, `af-10-02` | P0 |
| Deploy script + rollback | `af-10-04`, `af-10-05` | P0 |
| Caller spoof heuristics | `af-4-05` | P1 |
| Чёрный список номеров → Call Directory sync API | `af-4-09` (новая) | P1 |
| Prod QA gate | `af-11-01`…`af-11-06` | P0 |

---

## 3. Apple: что разрешено и что запрещено

> **Текст для экрана в приложении** — полная версия: `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md`  
> Показывать: Hub → ℹ️ «Как это работает» + Помощь → FAQ Antifake.

### ✅ Apple позволяет

| Действие | Как в ALADDIN |
|----------|---------------|
| Проверка текста/ссылки **по запросу пользователя** | Hub → Текст / Ссылка |
| Share Extension из Safari, Telegram | «Поделиться» → Проверить в ALADDIN |
| Загрузка файла голоса/видео/записи звонка | Hub → вкладки |
| **Call Directory** — метка/блок **известных** номеров из списка | M2 `af-4-02` |
| Push **после** звонка с предложением проверить | M2 `af-4-03` |
| Запись 3–5 с **по нажатию кнопки** во время разговора | M3 `af-4-04` |
| VoIP внутри своего приложения | не в scope ALADDIN PSTN |

### ❌ Apple не позволяет (и мы не обещаем)

| Действие | Почему |
|----------|--------|
| Слушать **все** сотовые (SIM) звонки в фоне | Sandbox iOS, приватность |
| Автоматически класть трубку по нейросети | Нет доступа к PSTN audio + риск ложных срабатываний |
| Перехват FaceTime, Zoom, WhatsApp video | Закрытые приложения |
| Читать SMS/WhatsApp без Share/действия пользователя | Запрет iOS |
| 100% точность «это фейк» без оговорки | ML даёт вероятность, не приговор |

### Формулировка для пользователя (короткая)

> ALADDIN проверяет текст, ссылки и файлы **когда вы сами отправляете их на проверку**.  
> Для звонков: можно проверить **запись после разговора**; предупреждение на экране входящего — только для **известных** подозрительных номеров.  
> Apple не разрешает приложениям незаметно слушать обычные телефонные звонки.

---

## 4. Чёрная шляпа — риски и митигация

| Риск | Последствие | Митигация |
|------|-------------|-----------|
| Обещать автоперехват PSTN | Отказ App Store, иски | `af-8-06`, экран Apple limits, `ux-1-10` |
| Авто-сброс по ML | Блок банка/врача/школы | Только Call Directory **список**, не ML-hangup |
| Фоновый микрофон | Privacy manifest, негатив отзывов | Только по кнопке; Privacy Nutrition Labels `af-8-05` |
| Ложный «фейк» на новости | Потеря доверия | UI: `likely_fake / uncertain / likely_real` + reasons[] |
| Нагрузка VPS на видео | Падение сервера | Очередь `af-3`, nginx limits `af-10`, rate limit |
| Hub не найти | «140 задач — где?» | `ux-1-06` на NetworkProtection |
| Onboarding «в реальном времени» | Misleading | `af-8-01` правка page 6 |
| 25MB лимит iOS upload | Fail на видео | nginx 100MB server-side; сжатие hint в UI |

---

## 5. Дорожная карта M1 → M4

### M1 — «Работает руками» (2–3 нед) — **ТЕКУЩИЙ ФОКУС**

| # | Задача | ID |
|---|--------|-----|
| 1 | Карточка на экране Защиты | `ux-1-06` |
| 2 | Честные тексты карточки + Hub | `ux-1-10` |
| 3 | Экран ограничений Apple | `af-8-07` |
| 4 | Worker ML на VPS | `af-3-01`…`af-3-05`, `af-10-*` |
| 5 | Prod smoke | `af-11-*` |

**Критерий M1:** Главная → Защита Aladdin → карточка → 4 вкладки Hub → вердикт без mock на prod.

### M2 — «Проактивная защита» (+4–6 нед)

| # | Задача | ID |
|---|--------|-----|
| 1 | Call Directory Extension | `af-4-02` |
| 2 | Post-call push | `af-4-03` |
| 3 | Spoof heuristics (номер ≠ имя) | `af-4-05` |
| 4 | API синк чёрного списка номеров | `af-4-09` |
| 5 | Инструкция Share в Помощь | `ux-1-09` |
| 6 | Marketing claims doc | `af-8-06` |

### M3 — «Почти автомат» (+6–8 нед)

| # | Задача | ID |
|---|--------|-----|
| 1 | Виджет / Live Activity «5 сек голос» | `af-4-04` |
| 2 | История проверок | `af-6-08` |
| 3 | AI tool в ассистенте | `af-7-03`, `af-7-04` |
| 4 | Clipboard opt-in | `af-7-06` (новая) |
| 5 | Семейные алерты | `af-12-05` (новая) |

### M4 — не обещаем

- Прослушивание всех PSTN в фоне  
- Автосброс по ML без списка  
- Перехват FaceTime / видеочатов  
- 100% без `uncertain`

---

## 6. По типам угроз: сейчас → идеал

### 📰 Фейковые новости / текст

| Уровень | Как | UI | Статус |
|---------|-----|-----|--------|
| M1 | Вставить → Проверить → 1–3 с | Hub → Текст | ✅ код |
| M2 | Share из Safari/TG | Extension | ✅ код, ⬜ инструкция |
| M2 | Paste prompt opt-in | баннер | ⬜ |
| M3 | AI «это правда?» | Companion | ⬜ |
| Нельзя | Читать все SMS в фоне | — | запрет iOS |

### 🔗 Поддельные сайты

| M1 | Hub → Ссылка | ✅ |
| M2 | Share Safari | ✅ |
| M3 | QR в Hub | ⬜ |

### 🎤 Поддельный голос (файл)

| M1 | Hub → Голос → файл | ✅ код, ⬜ worker prod |
| M2 | Share голосового | ✅ |
| M3 | Виджет 5 сек по кнопке | ⬜ |
| Нельзя | Фоновое прослушивание | — |

### 🎬 Deepfake-видео

| M1 | Hub → Видео | ✅ код, ⬜ worker prod |
| M2 | Share видео | ✅ |
| M3 | Hint: запись экрана видеозвонка | ⬜ copy |
| Нельзя | Live перехват FaceTime | — |

### 📞 Звонки мошенников

| Уровень | UX | Техника | Статус |
|---------|-----|---------|--------|
| M1 | После звонка → загрузить запись | `call/analyze` | ✅ код |
| M2a | «Возможный мошенник» на входящем | Call Directory | ⬜ |
| M2b | Push после звонка | CallKit ended | ⬜ |
| M2c | Номер ≠ имя «Банк» | heuristics | ⬜ |
| M3 | Live Activity кнопки | 5s sample | ⬜ |
| Частично | Блок только из списка | Directory block | ⬜ |
| Нельзя | Слушать SIM + ML hangup | — | — |

---

## 7. UX-задачи (из обсуждений)

| ID | Задача | P | Статус |
|----|--------|---|--------|
| `ux-1-06` | Карточка Antifake на `03_NetworkProtectionScreen` (между securityFeaturesCard и componentsSections) | P0 | ⬜ |
| `ux-1-10` | Честный copy звонков | P1 | ⬜ |
| `ux-1-09` | Share инструкция в Помощь | P1 | ⬜ |
| `ux-1-08` | Merge ThreatProtection ↔ NetworkProtection | P1 | ⬜ |
| `ux-1-03` | Coachmark Hub | P2 | ⬜ |
| `ux-1-04` | QA path doc | P2 | ⬜ |
| `af-8-07` | Экран «Ограничения Apple» в приложении | P1 | ⬜ |

---

## 8. Полный реестр задач `af-*` (72)

См. `.cursor/ANTIFAKE_PRODUCTION_TODO.md` — обновлять счётчик при закрытии.

**Сводка по батчам:**

| Batch | Название | Done | Open |
|-------|----------|------|------|
| AF-0 | Prod safety | 7/8 | af-0-07 |
| AF-1 | Agents/deps | 3/9 | af-1-01,02,05,07,08,09 |
| AF-2 | API routers | 9/10 | af-2-09 rate limits deferred |
| AF-3 | Workers | 0/7 | **критический** |
| AF-4 | Звонки | 0/8 | M2 |
| AF-5 | iOS settings sync | 1/6 | af-5-01…04,06 |
| AF-6 | Hub UI | 2/10 | iOS код ~8/10, todo file устарел |
| AF-7 | Share & AI | 2/5 | af-7-03…05 |
| AF-8 | Copy/legal | 0/7 | + af-8-07 Apple screen |
| AF-9 | 8 угроз matrix | 0/8 | E2E на prod |
| AF-10 | Deploy/nginx | 0/5 | **критический** |
| AF-11 | QA gate | 0/6 | перед TF |
| AF-12 | Monitoring | 0/4 | P2 |

---

## 9. Связанные задачи (perf, wellness — не antifake)

| Batch | Фокус | Файл |
|-------|-------|------|
| PERF-0…2 | Скорость UI, VisualLogger | UX_AUDIT |
| FIX-NOTIF/SF | Настройки | UX_AUDIT |
| ux-6, ux-8 | Wellness | UX_AUDIT |
| VPS-IoT | components.py | ✅ |

---

## 10. Критический путь (рекомендация senior iOS)

```
Неделя 1–2:
  ux-1-06 + ux-1-10 + af-8-07 (вход + честность)
  af-10 deploy worker + af-3 queue
  af-11 smoke на prod

Неделя 3–4:
  af-4-02 Call Directory (entitlement review параллельно)
  af-4-03 post-call
  ux-1-09 Share help

Неделя 5–8:
  af-4-04 widget
  af-6-08 history
  af-7-03 AI tool
```

**Не начинать** с live audio до закрытия M1 smoke и App Store copy review.

---

## 11. Как обновлять прогресс

1. Меняй статус в этом файле (секция 2) при крупных вехах.  
2. Детальные `af-*` — в `ANTIFAKE_PRODUCTION_TODO.md` (⬜→✅).  
3. Cursor todos — **36 id** из `.cursor/ALADDIN_MASTER_TODO.md` (таблица A), не сокращать.  
4. Commit prefix: `feat(antifake): …`  
5. Smoke после деплоя: `python3 docs/server/test_antifake_prod_smoke.py`

---

*Antifake Master Roadmap v1.0 · single source of truth для продукта и инженерии*
