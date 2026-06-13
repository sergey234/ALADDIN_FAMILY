# Anti-Fake Production — Cursor Todo (100% deepfakes)

**Создано:** 2026-06-09 · **Обновлено:** 2026-06-13 · **Build:** **232**  
**SSOT:** `docs/release/MASTER_STATUS_INDEX.md`  
**Мастер-план (single source):** `.cursor/ANTIFAKE_MASTER_ROADMAP.md`  
**Тексты Apple limits:** `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md`  
**Цель:** полноценная прод-защита от фейков (голос · видео · звонки · новости · документы · URL) **без mock / wildcard / пустых `result`**.  
**Синхронизация:** `.cursor/SECURITY_138_MASTER_TODO.md` § AF — **обновлять оба файла** при закрытии `af-*` задач.  
**Общий план 138:** `docs/SECURITY_138_GAP_ANALYSIS.md`  
**Связанный аудит:** разговор 2026-06-09 (прод-тесты SSH `~/.ssh/aladdin_server`, `aladdin-ai.ru`).  
**Полный техспек:** `docs/ANTIFAKE_PRODUCTION_PLAN.md`  
**Prod policy:** `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` § PRODUCTION HARD RULE — `sfm_mock`, `mock_fallback`, `3.0.0-mock-real-protection` **запрещены** для antifake.

**Счёт:** **38 / 72** задач ✅ (backend + Hub B2 + **build 232 M2/M3**)

---

## Архитектура (целевое состояние)

```
iOS Premium
  ├─ Antifake Hub (8 угроз → 4 пайплайна: text · audio · video · call)
  ├─ Share Extension → check-text / check-url
  ├─ Call Directory + CallKit (post-call / live audio chunk)
  ├─ AI Assistant tool: antifake_check_*
  └─ Local History (UserDefaults/SQLite, без PII на сервере)

FastAPI (явные роутеры, OpenAPI)
  ├─ POST /api/antifake/check/text      sync
  ├─ POST /api/antifake/check/url       sync
  ├─ POST /api/antifake/check/audio     → job_id
  ├─ POST /api/antifake/check/video     → job_id
  ├─ POST /api/antifake/check/document  → job_id
  ├─ GET  /api/antifake/jobs/{id}       poll
  ├─ POST /api/antifake/call/analyze    → job_id (запись звонка / chunk)
  └─ GET  /api/antifake/metrics         (admin + user summary)

Workers (Redis/RQ или Celery — тот же стек, что на VPS)
  ├─ fake_news_detection_agent (transformers, lazy load)
  ├─ deepfake_protection_system (audio/video)
  ├─ fake_documents_agent (cv2)
  └─ caller_spoof_heuristics (metadata + optional HIBP-style lists)

PostgreSQL
  ├─ user_protection_settings (persist categories, incl. deepfakes)
  ├─ antifake_jobs (status, verdict, latency_ms, no raw media)
  └─ antifake_metrics_daily (aggregates per user/family)
```

### Единый контракт ответа (все check-API)

```json
{
  "verdict": "likely_fake | uncertain | likely_real",
  "confidence": 0.0,
  "reasons": ["string"],
  "source": "real_agent",
  "agent": "fake_news_detection_agent",
  "job_id": null,
  "checked_at": "ISO8601",
  "premium_required": false
}
```

Async: `POST` → `{ "job_id": "uuid", "status": "queued" }` · `GET /jobs/{id}` → контракт выше + `status: completed|failed`.

**Запрещено в prod:** `result: ""`, `version: 3.0.0-mock-real-protection`, `source: sfm_mock`, wildcard на `/api/deepfake/*`, `/api/fake-news/*`.

---

## Batch 0 — Prod safety & инфра (P0) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-0-01` | `protection.py`: импорт `logger`, `enable`/`disable` → 200 | ✅ |
| `af-0-02` | Миграция `user_protection_settings` (user_id, categories JSONB, updated_at) | ✅ |
| `af-0-03` | `get/update_protection_settings_from_db` — реальный UPSERT, не stub | ✅ |
| `af-0-04` | Выровнять **канонический список category ID** (iOS 9 + server legacy → один enum в shared doc) | ✅ |
| `af-0-05` | `main.py`: hard-block wildcard для `/api/deepfake/*`, `/api/fake-news/*`, `/api/antifake/*` mutations | ✅ |
| `af-0-06` | Gateway guard: 503 если `mock-real-protection` / пустой `result` на antifake paths | ✅ |
| `af-0-07` | Deprecate redirect: старые URL → 301 doc или 410 Gone (не wildcard) | ⬜ |
| `af-0-08` | Smoke script `docs/server/test_antifake_prod_smoke.py` (JWT + no-mock assert) | ✅ |

---

## Batch 1 — Зависимости & агенты на сервере (P0) · 9 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-1-01` | `security.core` / `security.base` — единый пакет, PYTHONPATH в gunicorn unit | ⬜ |
| `af-1-02` | `venv`: `opencv-python-headless`, `transformers`, `torch` CPU, `librosa`, `soundfile` | ⬜ |
| `af-1-03` | Lazy-load моделей (singleton + warm on worker start, не на каждый request) | ✅ B2-10 |
| `af-1-04` | `fake_news_detection_agent`: импорт без цепочки `fake_documents` → cv2 | ✅ B2-10 |
| `af-1-05` | `deepfake_protection_system`: убрать заглушки `analyze_video/audio`, реальный pipeline | ⬜ |
| `af-1-06` | `fake_documents_agent`: отдельный worker path (cv2 только здесь) | ✅ B2-10 |
| `af-1-07` | **Не поднимать** полный SFM — только registry `ANTIFAKE_AGENTS` + explicit invoke | ⬜ |
| `af-1-08` | Unit-тесты агентов на сервере (`pytest security/ai_agents/test_antifake_*.py`) | ⬜ |
| `af-1-09` | Политика хранения: raw media **не пишем** в БД; только hash + temp file TTL 15 min | ⬜ |

---

## Batch 2 — API роутеры antifake (P0) · 10 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-2-01` | `app/routers/antifake.py` — router prefix `/api/antifake` | ✅ |
| `af-2-02` | `POST /check/text` — sync, fake news + scam patterns + URL extract | ✅ |
| `af-2-03` | `POST /check/url` — phishing/fake site (redirect chain, domain age heuristics) | ✅ |
| `af-2-04` | `POST /check/audio` — multipart → queue job | ✅ |
| `af-2-05` | `POST /check/video` — multipart → queue job (max size env) | ✅ |
| `af-2-06` | `POST /check/document` — image/pdf → queue job | ✅ |
| `af-2-07` | `GET /jobs/{id}` — poll + unified verdict contract | ✅ |
| `af-2-08` | Premium gate: `subscription.level in (premium, trial_premium)` → 402/403 JSON | ✅ |
| `af-2-09` | Rate limits: text 60/min, media 10/h per user (slowapi) | ⬜ deferred — slowapi 422 on body routes |
| `af-2-10` | OpenAPI: все antifake paths в `openapi.json` (не wildcard) | ✅ sync paths; multipart `include_in_schema=False` |

---

## Batch 3 — Async workers & метрики (P0) · 7 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-3-01` | Job queue (Redis + RQ worker unit `aladdin-antifake-worker.service`) | ✅ код |
| `af-3-02` | Таблица `antifake_jobs` (id, user_id, type, status, verdict JSON, latency_ms) | ✅ |
| `af-3-03` | Worker: audio → voice cloning score | ✅ via SFM + rule_engine fallback |
| `af-3-04` | Worker: video → deepfake face/voice sync score | ✅ via SFM + rule_engine fallback |
| `af-3-05` | Worker: document → fake_documents_agent | ✅ lazy loader path |
| `af-3-06` | `GET /api/antifake/metrics` — checks_total, fake_detected, p95_latency (user scope) | ✅ by_type |
| `af-3-07` | Prometheus/Grafana или structured logs + daily rollup cron | ⬜ |

---

## Batch 4 — Звонки & spoofing (P1, iOS hard) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-4-01` | Продуктовый scope doc: что именно обещаем по «фейковым звонкам» | ✅ `docs/ANTIFAKE_CALLS_PRODUCT_SCOPE.md` |
| `af-4-02` | `CallKit` / **Call Directory Extension** target в Xcode | ✅ build 232 |
| `af-4-03` | Post-call flow: local push → Hub (запись → analyze опционально) | ✅ build 232 |
| `af-4-04` | Live chunk: AVAudioEngine 5 s quick voice (вкладка Audio) | ✅ build 232 |
| `af-4-05` | Caller ID spoof heuristics server-side | ✅ build 232 |
| `af-4-06` | Email spoof: `POST /check/text` mode=email_headers | ⬜ |
| `af-4-07` | Dating profile: `check/text` + image URL | ⬜ |
| `af-4-08` | Entitlements + App Store Privacy manifest для микрофона/звонков | 🟡 Call Directory entitlements ✅ |
| `af-4-09` | Call Directory sync API + App Group blacklist | ✅ build 232 |

---

## Batch 5 — iOS: sync & settings (P0) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-5-01` | `ProtectionSettings` Codable ↔ server `{ categories, globalLevel }` adapter | ⬜ |
| `af-5-02` | Раскомментировать + починить `loadSettingsFromServer()` | ⬜ |
| `af-5-03` | `saveSettingsToServer` — POST schema match; conflict resolution server wins | ⬜ |
| `af-5-04` | `enableProtectionCategory("deepfakes")` при Premium activate | ✅ build 232 |
| `af-5-05` | `AppConfig.Endpoint` — все `/api/antifake/*` | ✅ B2-00 |
| `af-5-06` | Unit tests: encode/decode settings round-trip | ⬜ |

---

## Batch 6 — iOS: Antifake Hub UI (P1) · 10 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-6-01` | `AntifakeHubScreen` — Storm Mesh `.shield`, 4 входа | ✅ B2 |
| `af-6-02` | `AntifakeTextCheckView` — ввод / paste → verdict card | ✅ B2 |
| `af-6-03` | `AntifakeAudioCheckView` — запись или файл → job poll UI | ✅ B2 |
| `af-6-04` | `AntifakeVideoCheckView` — picker → upload progress → poll | ✅ B2 |
| `af-6-05` | `AntifakeCallCheckView` — import recording + spoof tips | ✅ B2 |
| `af-6-06` | Navigation: deepfakes → **AntifakeHub** | ✅ B2 + bypass build 232 |
| `af-6-07` | Premium gate UI + paywall CTA | ✅ B2 · TEMP bypass QA |
| `af-6-08` | `AntifakeHistoryStore` — локально последние 50 проверок | ✅ build 232 |
| `af-6-09` | Локализация RU/EN всех строк antifake | ✅ B2-11 / `docs/LOCALIZATION_BATCH_GATE.md` |
| `af-6-10` | `27_ProtectionStatsScreen` — подтянуть реальные metrics с `/api/antifake/metrics` | ⬜ |

---

## Batch 7 — iOS: Share Extension & AI (P1) · 5 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-7-01` | Share Extension target «Проверить в ALADDIN» (text, url) | ✅ |
| `af-7-02` | App Group для JWT / deep link в AntifakeTextCheck | ✅ |
| `af-7-03` | AI Assistant tool `antifake_check_text` в `ai_assistant_router` | ⬜ |
| `af-7-04` | iOS: assistant вызывает tool → рендер verdict в чате | ⬜ |
| `af-7-05` | VoiceNotes: опция «проверить на подделку» после записи | ⬜ |

---

## Batch 8 — Copy, legal, App Store (P1) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-8-01` | Onboarding p.6 — убрать «в реальном времени»; честные формулировки | ⬜ |
| `af-8-02` | FAQ deepfake / fake_voices / fake_news — только то, что в билде | ⬜ |
| `af-8-03` | `tariffs_premium_features_5–7` — привязка к Antifake Hub | ⬜ |
| `af-8-04` | App Store screenshot + review notes: демо Antifake Hub | ⬜ |
| `af-8-05` | Privacy Nutrition Labels: audio/video upload disclosure | ⬜ |
| `af-8-06` | `docs/ANTIFAKE_USER_FACING_CLAIMS.md` — approved marketing list | ⬜ |
| `af-8-07` | In-app экран «Ограничения Apple» (Hub ℹ️ + Помощь) — текст из `docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` | ⬜ |

---

## Batch 9 — 8 угроз deepfakes → feature matrix (P1) · 8 задач

| # | Угроза (каталог) | Реализация | ID | Статус |
|---|------------------|------------|-----|--------|
| 1 | Deepfake-видео | `/check/video` + Hub | `af-9-01` | ⬜ |
| 2 | Поддельные голоса | `/check/audio` + Hub | `af-9-02` | ⬜ |
| 3 | Спуфинг номеров | Call flow + heuristics | `af-9-03` | ⬜ |
| 4 | Поддельные сайты | `/check/url` + Share | `af-9-04` | ⬜ |
| 5 | Фейковые новости | `/check/text` | `af-9-05` | ⬜ |
| 6 | Поддельные документы | `/check/document` | `af-9-06` | ⬜ |
| 7 | Фейковые профили знакомств | text + image pipeline | `af-9-07` | ⬜ |
| 8 | Email spoofing | text mode email | `af-9-08` | ⬜ |

---

## Batch 10 — Деплой & nginx (P0) · 5 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-10-01` | `client_max_body_size` для `/api/antifake/check/*` (env, default 100MB video) | ✅ snippet |
| `af-10-02` | Timeout proxy_read 300s только для antifake upload paths | ✅ snippet |
| `af-10-03` | systemd: `aladdin-antifake-worker` + restart policy | ✅ example + deploy script |
| `af-10-04` | Deploy script + rollback; rsync antifake modules | ✅ `scripts/deploy_antifake_m1.sh` |
| `af-10-05` | Post-deploy: `test_antifake_prod_smoke.py` на prod (SSH) | ✅ в deploy script |

---

## Batch 11 — QA & acceptance (P0 gate) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-11-01` | Prod: `enable deepfakes` → 200, settings persist после reload | ⬜ |
| `af-11-02` | Prod: fake news text → `verdict != uncertain` на явном фейке | ⬜ |
| `af-11-03` | Prod: audio sample → job completed < 120s | ⬜ |
| `af-11-04` | Prod: video sample → job completed < 300s | ⬜ |
| `af-11-05` | iOS TestFlight: полный flow Premium user на все 4 Hub вкладки | ⬜ |
| `af-11-06` | Audit: grep prod logs 24h — zero `mock-real-protection` on antifake | ⬜ |

---

## Batch 12 — Мониторинг & ops (P2) · 4 задач

| ID | Задача | Статус |
|----|--------|--------|
| `af-12-01` | Alert: antifake job failure rate > 5% | ⬜ |
| `af-12-02` | Alert: worker queue depth > 50 | ⬜ |
| `af-12-03` | Dashboard: checks_total / fake_detected / latency p95 | ⬜ |
| `af-12-04` | Runbook: model OOM, disk temp cleanup | ⬜ |

---

## Порядок выполнения (критический путь)

```
Batch 0 → Batch 1 → Batch 2 → Batch 3 → Batch 5 (параллельно с 2–3)
         ↘ Batch 10 (деплой после 2)
Batch 6–7 (iOS) после Batch 2 контракт заморожен
Batch 4 (звонки) параллельно Batch 6, но CallKit review раньше submit
Batch 8–9 — непрерывно с UI
Batch 11 — gate перед App Store submit
```

**Оценка:** ~6–8 недель при 1 backend + 1 iOS (при наличии CallKit entitlement review).

---

## Блокеры → решение (чеклист)

| Блокер | Решение | Batch |
|--------|---------|-------|
| `logger` 500 на enable | `af-0-01` | 0 |
| Settings не persist | `af-0-02`, `af-0-03` | 0 |
| iOS ↔ server schema | `af-5-01`, `af-0-04` | 0, 5 |
| Wildcard mock | `af-0-05`, `af-0-06` | 0 |
| SFM не импортируется | Explicit routers, не SFM (`af-1-07`) | 1–2 |
| cv2 / transformers | `af-1-02`, lazy load `af-1-03` | 1 |
| loadSettingsFromServer stub | `af-5-02` | 5 |
| Фейковые звонки FAQ | CallKit + честный copy `af-4-*`, `af-8-*` | 4, 8 |
| Video 25MB chat limit | Отдельный nginx path 100MB `af-10-01` | 10 |
| BERT cold start | Async jobs `af-3-*` | 3 |
| App Store claims | Hub demo `af-8-04`, matrix `af-9-*` | 8, 9 |

---

## Как обновлять этот файл

1. Меняй `⬜` → `✅` и счётчик в шапке.  
2. После каждого батча — commit с префиксом `feat(antifake): batch N`.  
3. Smoke: `python3 docs/server/test_antifake_prod_smoke.py` (после `af-0-08`).
