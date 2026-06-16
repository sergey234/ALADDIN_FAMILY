# Antifake: гибридный UX вердикта + SFM smoke «раз и навсегда»

**Дата:** 2026-06-16  
**Контекст:** `12+12=24` → «Вероятно подлинное» + «Уверенность 15%» вводит в заблуждение.  
**Факт:** SFM ответил (`source=real_agent`), 15% = `fake_score`, не «агент недоступен».  
**Цель:** понятный UI + честный контракт API + мониторинг без ложных FAIL.

---

## 1. Гибридный подход (рекомендуемый)

### Принцип

| Слой | Ответственность | Почему |
|------|-----------------|--------|
| **Сервер** | Канон: `verdict`, `fake_risk` (0…1), `source`, `reasons` | Один источник правды для iOS, Telegram, family notify |
| **iOS** | Только **презентация**: подписи, цвет, бейдж, скрыть % при `insufficient_data` | Локализация RU/EN без дублирования ML-логики |
| **Smoke** | Контракт + golden cases | Регрессия не вернёт старый UX |

`confidence` в API **остаётся** (= `fake_risk`) для обратной совместимости.  
Новое поле `fake_risk` — явный дубликат с тем же значением (v1), позже можно deprecate `confidence` в OpenAPI.

### Что видит пользователь (всегда два уровня)

```
┌─────────────────────────────────────────┐
│ ✓ Вероятно подлинное      [Проверено AI]│  ← вердикт (главный заголовок)
│ Риск подделки: 15% · низкий             │  ← % + словесный уровень
│ ████░░░░░░░░░░░░░░░░                    │  ← полоса = fake_risk (не «уверенность»)
│ • текст слишком короткий для новостей   │  ← локализованные reasons
│ Оценка для новостей и мошенничества…    │  ← дисклеймер
└─────────────────────────────────────────┘
```

Для **likely_fake**:

```
⚠ Вероятно подделка          [Проверено AI]
Риск подделки: 87% · высокий
```

Для **insufficient_data** (новый вердикт):

```
? Недостаточно данных        [Проверено AI]
Текст слишком короткий — вставьте фрагмент новости или сообщения.
(без % и без полосы)
```

### Пороги уровня риска (iOS, `AntifakeVerdictPresentation`)

| `fake_risk` | Уровень (RU) | Цвет полосы |
|-------------|--------------|-------------|
| `< 0.35` | низкий | зелёный (если `likely_real`) |
| `0.35 … 0.65` | средний | оранжевый (`uncertain`) |
| `≥ 0.65` | высокий | красный (`likely_fake`) |

Вердикт и уровень **не противоречат**: заголовок из `verdict`, % всегда читается как **риск фейка**, не «подлинность».

### Бейдж источника (уже есть, усилить)

| `source` (нормализованный) | Бейдж |
|----------------------------|-------|
| `real_agent`, `real_sfm`, `local_ml` | **Проверено AI** |
| `rule_engine`, `heuristic_*` | **Проверено правилами** |
| `probe`, `heuristic` (media) | **Быстрая проверка** |

Исправить edge case: `real_sfm` в ответе SFM → iOS уже мапит на AI через `contains("sfm")`.

---

## 2. Где менять код

### P0 — iOS

| Файл | Изменение |
|------|-----------|
| `Core/Models/SecurityVerdictModels.swift` | `SecurityVerdictKind.insufficientData = "insufficient_data"`; computed `fakeRisk` (= `confidence`) |
| `Shared/Models/AntifakeVerdictPresentation.swift` | **NEW** — `riskLabel`, `riskLevelKey`, `showsRiskMeter`, `progressValue` |
| `Shared/Components/AntifakeVerdictCard.swift` | Заменить «Уверенность» на презентацию; серый стиль для `insufficient_data` |
| `Core/Localization/LocalizationManager.swift` | RU+EN: `antifake_verdict_fake_risk`, `antifake_risk_low/medium/high`, `antifake_verdict_insufficient_data`, reasons map, расширенный disclaimer |
| `ViewModels/AntifakeTextCheckViewModel.swift` | Подсказка при вводе < N символов (опционально) |
| `Tests/UnitTests/AntifakeVerdictPresentationTests.swift` | **NEW** — golden cases: scam, neutral short, neutral long |
| `Tests/UnitTests/SecurityVerdictModelsTests.swift` | decode `insufficient_data` |

### P0 — Сервер

| Файл | Изменение |
|------|-----------|
| `app/services/antifake_service.py` | В `_normalize_local_ml_text_result`: если `too_short` и нет pattern_hits → `verdict=insufficient_data`, `fake_risk=0`, reason `text_too_short`. В `_analyze_text_heuristic`: len < 40 и нет hits → то же |
| `app/routers/antifake.py` | OpenAPI enum + 200 для `insufficient_data` |
| `backend_tests/test_antifake_f12_fallback.py` | short text → insufficient_data |
| `docs/server/test_antifake_prod_smoke.py` | Разрешить `insufficient_data`; golden `12+12=24` → insufficient_data; scam text → likely_fake + real_agent |

### P1 — SFM smoke (exit 22) — **корневая причина найдена**

**Симптом:** `aladdin-sfm-prod-smoke.service` → `status=22` каждые 15 мин.  
**Причина:** `sfm_prod_smoke.sh` строка 12 — `curl -sf` на POST unknown function. SFM **корректно** отдаёт HTTP **503**, но `curl -f` трактует 503 как ошибку → **exit 22** до проверки кода.

Проверка на prod (2026-06-16):

```bash
# truth check — OK
bash sfm_truth_check.sh  # exit 0, overall PASS

# broken step
curl -sf ... __smoke_nonexistent__  # exit 22 при HTTP 503

# expected behavior
curl -s ...  # http:503, body success:false — это PASS
```

| Файл | Фикс |
|------|------|
| `docs/server/sfm_prod_smoke.sh` | Убрать `-f` у curl unknown-fn; `HTTP=$(curl -s -o file -w '%{http_code}' ...)`; exit 1 только если `HTTP != 503` |
| `docs/server/sfm_truth_check.sh` | Аналогично убрать `-f` на probe execute (строка 44) — превентивно |
| `backend_tests/test_sfm_prod_smoke_script.sh` | **NEW** — локальный shellcheck + mock curl |
| Deploy | `scp` + `systemctl restart aladdin-sfm-prod-smoke.service` на VPS |

### P1 — Self-healing и мониторинг

```
┌──────────────────────┐     every 15m      ┌─────────────────────────┐
│ aladdin-sfm-prod-    │ ─────────────────► │ sfm_truth_check PASS    │
│ smoke.timer          │                    │ + unknown fn → 503      │
└──────────────────────┘                    └───────────┬─────────────┘
                                                        │ FAIL
┌──────────────────────┐                                ▼
│ aladdin-security-    │◄── aggregates ────  journalctl + Telegram ops
│ prod-smoke.timer     │     antifake +      (уже B-OPS-22)
└──────────────────────┘     all domains
```

| ID | Действие |
|----|----------|
| `af-smoke-04` | После фикса curl — smoke PASS 24h в journalctl |
| `af-smoke-05` | `RUNBOOK_SFM_ML_DEGRADED.md` — добавить § «exit 22 = curl -f bug» |
| `af-smoke-06` | On-fail: `systemctl restart aladdin-sfm-core` **только** если `/api/sfm/status` → `sfm_loaded:false` (не blind restart) |
| `af-smoke-07` | Единый `docs/server/verify_prod_smoke_all.sh` — sfm + antifake smoke exit 0 |

### P2 — Продукт

| Задача | Файл |
|--------|------|
| `bypassPremiumGate = false` перед TestFlight | `Core/Config/AntifakeAccessPolicy.swift` |
| Device QA Call Directory | `docs/ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md`, `DEVICE_QA_RECORD.json` |

---

## 3. Контракт API (v1.1)

```json
{
  "verdict": "insufficient_data",
  "confidence": 0.0,
  "fake_risk": 0.0,
  "reasons": ["text_too_short"],
  "source": "real_agent",
  "agent": "fake_news_detection_agent",
  "job_id": "...",
  "model_version": "..."
}
```

Правила:

- `fake_risk` === `confidence` для всех sync ответов (media jobs — то же).
- `verdict=likely_real` + `fake_risk=0.15` → UI: «подлинное» + «риск 15% низкий» (не инверсия в 85% — пользователь просил явно **риск фейка**).
- Запрещено: `likely_real` + `fake_risk` без пояснения в UI.

---

## 4. Локализация reasons (iOS map)

| `reason` (server) | RU |
|-------------------|-----|
| `text_too_short` / `too_short` | Текст слишком короткий для анализа новостей |
| `no_suspicious_patterns` | Подозрительных паттернов не найдено |
| `scam` / `financial_scam` | Признаки финансового мошенничества |
| `sensationalism` | Сенсационные формулировки |

---

## 5. Тест-план

| # | Ввод | Ожидание |
|---|------|----------|
| T1 | `шокирующая правда — переведите деньги срочно` | likely_fake, риск высокий, AI |
| T2 | `12+12=24` | insufficient_data, без % |
| T3 | Нейтральный абзац новости | likely_real, риск низкий |
| T4 | `sfm_prod_smoke.sh` на VPS | exit 0 |
| T5 | `test_antifake_prod_smoke.py` | pass:true |

---

## 6. Порядок внедрения (фазы)

```
Фаза A (1 PR): af-smoke-01..03 — фикс sfm_prod_smoke.sh + deploy VPS
Фаза B (1 PR): af-ux-20..25 — server insufficient_data + fake_risk field
Фаза C (1 PR): af-ux-26..32 — iOS AntifakeVerdictPresentation + card + l10n + tests
Фаза D: af-smoke-04..07 — 24h мониторинг + runbook + aggregate script
Фаза E (pre-TF): af-p2-01..02 — premium gate + device QA
```

---

## 7. Cursor TODO IDs

См. `.cursor/ANTIFAKE_VERDICT_UX_TODO.md` и трекер в Cursor Tasks.

| ID | Приоритет | Задача |
|----|-----------|--------|
| af-smoke-01 | P0 | Fix `curl -f` → `curl -s` в `sfm_prod_smoke.sh` |
| af-smoke-02 | P0 | Fix probe curl в `sfm_truth_check.sh` |
| af-smoke-03 | P0 | Deploy на VPS + verify smoke PASS |
| af-ux-20 | P0 | Server: `insufficient_data` для too_short |
| af-ux-21 | P0 | Server: поле `fake_risk` в `_build_response` |
| af-ux-22 | P0 | iOS: `AntifakeVerdictPresentation` |
| af-ux-23 | P0 | iOS: `AntifakeVerdictCard` — риск + уровень |
| af-ux-24 | P0 | iOS: l10n RU/EN + reasons map |
| af-ux-25 | P0 | Tests: presentation + insufficient_data decode |
| af-smoke-04 | P1 | Обновить `test_antifake_prod_smoke.py` golden cases |
| af-smoke-05 | P1 | Runbook exit 22 |
| af-smoke-06 | P1 | Conditional sfm-core restart on sfm_loaded:false |
| af-smoke-07 | P1 | `verify_prod_smoke_all.sh` |
| af-p2-01 | P2 | `bypassPremiumGate = false` |
| af-p2-02 | P2 | Device QA Call Directory (af-ux-10) |

---

## 8. Критерий «идеально работает»

- [ ] Пользователь **никогда** не видит «Уверенность 15%» без контекста.
- [ ] Короткий/нейтральный текст → **Недостаточно данных**, не ложное «подлинное».
- [ ] `aladdin-sfm-prod-smoke` → **exit 0** стабильно 7+ дней.
- [ ] `test_antifake_prod_smoke.py` → pass после изменения контракта.
- [ ] При падении SFM — smoke FAIL + runbook, не silent fallback.
