# Antifake v4 — реестр 134 задач (SSOT для Cursor TODO)

**Версия:** 4.3 · **Дата:** 2026-06-15  
**Единая точка входа:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md) (~280 задач, архитектура, gates)  
**Индекс документов:** [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md)  
**Главный план:** [ANTIFAKE_TOP_TIER_PLAN.md](./ANTIFAKE_TOP_TIER_PLAN.md)  
**Корень iOS:** `ALADDIN_iOS` · **Build:** 232+ · **iOS min:** 15.2

---

## Как пользоваться (люди и ML-агенты)

1. **Единственный источник ID задач antifake v4** — этот файл + `ANTIFAKE_TOP_TIER_PLAN.md`.
2. **Cursor TODO ID** = `af-{TASK-ID}` (пример: `af-D-04`, `af-F-01`). Всего **134** пунктов (**131** активных без cancelled O-01…O-03).
3. **Индекс всех документов:** [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md)
4. **Порядок работы Фазы 1:** `D → C → A → F → J → B → E → N → R`.
4. **Не путать** с `IMPLEMENTATION_BATCHES_TODO.md` (R-07, B2-09) и `ANTIFAKE_PRODUCTION_TODO.md` (af-1…af-11) — там **старая** нумерация.
5. При закрытии задачи: статус ✅ здесь → строка в плане → Cursor todo `completed` (**merge: true**, список не пересоздавать).

**Workflow:** [ANTIFAKE_V4_WORKFLOW.md](./ANTIFAKE_V4_WORKFLOW.md) — **134 todos не удалять**; **Device (D-01…D-04) — в самом конце.**

### Приоритет точности + Apple Review (v4.2)

```
F-01 → F-12 → F-08 → Q-06 → F-05/R-03 green
A-06 + A-07 + A-13 + A-15 + G-01 + G-04 + G-05 + N-01 + J-02 + Q-05
M-01…M-05 (параллельно)
G-03 + Q-01 — ✅ код + static gates (`verify_antifake_bypass_off.py`)
```

**P1 (CD только база, no PSTN, uncertain, ingest ≥0.72)** — не отдельные code-todos; покрыты **A-06**, **A-07**, **G-01**, **J-02**, **C-04**, **I-04**.

### Порядок СЕЙЧАС (без iPhone)

```
C (✅) → A (✅) → F (✅) → J (✅) → B (✅) → E (✅ кроме E-06 device) → N (✅) → R (✅ кроме R-02 device) → Ф2 (✅) → G-03/Q-01 (✅) → **DEVICE** (D-01…04, D-09, E-06, R-02)
```

### Стратегия (зачем всё это)

Семейный antifake на iOS 15.2+: проверка ссылок / голоса / видео / записи звонка + метки на входящих (Call Directory) + честная privacy. **Не** клон Truecaller. PIR (iOS 18+) и выключение QA Premium — **в самом конце**, когда решим.

### Пропуски в нумерации (намеренно)

| ID | Пояснение |
|----|-----------|
| **A-12** | Не используется в v4 |
| **E-04** | Не используется в v4 |
| **D-05** | В секции Done, не дублируется в открытых задачах Batch D |

---

## Сводка по статусам

| Статус | Кол-во | Cursor |
|--------|--------|--------|
| ✅ Done | 111 | `completed` |
| ⬜ Open | 7 | `pending` (device QA only) |
| 🟡 In progress | 0 | — |
| ⏸ Deferred | 13 | `pending` (H + K; Ф3) |
| ❌ Cancelled | 3 | `cancelled` |
| **Итого** | **134** | **131 активных** (минус O-01…O-03) |

---

## Порядок батчей

```
ФАЗА 1: D → C → A → F → J → B → E → N → R
ФАЗА 2: I → L → M → P → G-marketing → Q
ФАЗА 3: G-03/B-10/Q-01 (bypass) → H (PIR) → K (on-device)
ОТМЕНЕНО: O (Safari filter)
```

---

## Полный реестр (134 задачи)

**Колонки:** Cursor ID · Task ID · Фаза · Batch · Статус · Зачем (простым языком)

### ✅ Done — ранние 8 (полный список ✅ см. батчи ниже)

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-A-01` | A-01 | — | A | ✅ | 3 строки на карточке «Проверить подлинность» |
| `af-A-02` | A-02 | — | A | ✅ | Sheet «Как включить» Call Directory (4 шага) |
| `af-A-03` | A-03 | — | A | ✅ | Кнопки CD вертикально — текст не ломается |
| `af-A-04` | A-04 | — | A | ✅ | Понятные ошибки sync (сеть, 404, Premium) |
| `af-B-01` | B-01 | — | B | ✅ | `/api/antifake/call-directory` на prod |
| `af-D-05` | D-05 | — | D | ✅ | CI/Fastlane подписывает Call Directory extension |
| `af-E-01` | E-01 | — | E | ✅ | CallKit observer — видим конец звонка |
| `af-E-02` | E-02 | — | E | ✅ | Push «Проверить звонок?» после звонка |

---

### ФАЗА 1 · Batch D — iPhone + метка — 9 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-D-01` | D-01 | 1 | D | ⬜ | Archive build 232+ с extension |
| `af-D-02` | D-02 | 1 | D | ⬜ | TestFlight → real iPhone |
| `af-D-03` | D-03 | 1 | D | ⬜ | Extension ON → Sync → тестовый входящий |
| `af-D-04` | D-04 | 1 | D | ⬜ | **Must:** метка «Возможный мошенник?» на экране звонка |
| `af-D-06` | D-06 | 1 | D | ✅ | QA-док `ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md` + static gate |
| `af-D-07` | D-07 | 1 | D | ✅ | Unit tests identified[] vs blocked[] + handler |
| `af-D-08` | D-08 | 1 | D | ✅ | Extension OFF → orange banner UI (device sign-off в чеклисте) |
| `af-D-09` | D-09 | 1 | D | ⬜ | Sync после airplane mode / reboot (**device**) |
| `af-D-10` | D-10 | 1 | D | ✅ | EN/RU labels via `AntifakeCallDirectoryLabelPolicy` |

---

### ФАЗА 1 · Batch C — Fraud DB — 11 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-C-01` | C-01 | 1 | C | ✅ | DDL таблица `antifake_scam_numbers` |
| `af-C-02` | C-02 | 1 | C | ✅ | Service `antifake_call_directory_store.py` |
| `af-C-03` | C-03 | 1 | C | ✅ | **Must:** убрать 2 seed, API только из БД |
| `af-C-04` | C-04 | 1 | C | ✅ | Auto-ingest из call analyze + reports |
| `af-C-05` | C-05 | 1 | C | ✅ | CLI CSV import для ops |
| `af-C-06` | C-06 | 1 | C | ✅ | iOS: «Синхронизировано N номеров · дата» |
| `af-C-07` | C-07 | 1 | C | ✅ | Unit tests store + API contract |
| `af-C-08` | C-08 | 1 | C | ✅ | **Must:** ≥100 RU номеров (1000 = M2) |
| `af-C-09` | C-09 | 1 | C | ✅ | Delta sync `?since=timestamp` |
| `af-C-10` | C-10 | 1 | C | ✅ | max_entries guard + rollback snapshot |
| `af-C-11` | C-11 | 1 | C | ✅ | QA-номера `source=qa` для D-03 |

---

### ФАЗА 1 · Batch A — UX & Copy — 10 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-A-05` | A-05 | 1 | A | ✅ | Accordion — те же 3 строки что карточка |
| `af-A-06` | A-06 | 1 | A | ✅ | Help/FAQ из `ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` |
| `af-A-07` | A-07 | 1 | A | ✅ | App Store Review Notes (+ P1 limits: CD/PSTN/uncertain) |
| `af-A-08` | A-08 | 1 | A | ✅ | Onboarding extension: GIF + retry switches |
| `af-A-09` | A-09 | 1 | A | ✅ | Path iOS 18+: Settings → Apps → Phone |
| `af-A-10` | A-10 | 1 | A | ✅ | VoiceOver labels |
| `af-A-11` | A-11 | 1 | A | ✅ | CD label EN/RU (не hardcode RU) |
| `af-A-13` | A-13 | 1 | A | ✅ | Call Directory entitlement doc для Review |
| `af-A-14` | A-14 | 1 | A | ✅ | Empty Hub: честный paywall без fake demo |
| `af-A-15` | A-15 | 1 | A | ✅ | **Must Review:** media tabs honesty copy (probe ≠ full deepfake ML); badge probe vs AI |

---

### ФАЗА 1 · Batch F — Настоящий AI — 12 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-F-01` | F-01 | 1 | F | ✅ | SFM 422 purge + restart; prod via `local_ml`/`real_agent` |
| `af-F-02` | F-02 | 1 | F | ✅ | Video/deepfake worker cv2/torch; **DoD:** probe не → `likely_fake` без ML source |
| `af-F-03` | F-03 | 1 | F | ✅ | Call recording full pipeline |
| `af-F-04` | F-04 | 1 | F | ✅ | Latency SLA + progress UX |
| `af-F-05` | F-05 | 1 | F | ✅ | Gate af-11 (6 checks); af-11-02 pass on prod |
| `af-F-06` | F-06 | 1 | F | ✅ | Metrics dashboard |
| `af-F-07` | F-07 | 1 | F | ✅ | Model versioning + rollback |
| `af-F-08` | F-08 | 1 | F | ✅ | Golden RU/EN; obvious scam → must `likely_fake` |
| `af-F-09` | F-09 | 1 | F | ✅ | 25MB iOS/API/nginx + UI hint |
| `af-F-10` | F-10 | 1 | F | ✅ | **Must:** badge «AI» / «Правила» (`source`) |
| `af-F-11` | F-11 | 1 | F | ✅ | Audio worker: file bytes; **DoD:** probe hint only |
| `af-F-12` | F-12 | 1 | F | ✅ | Tier-2: local_ml + heuristic merge; financial_scam patterns |

### ФАЗА 1 · Batch F (продолжение) — ML 100% на prod — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-F-13` | F-13 | 1 | F | ✅ | **Must:** torch+transformers в prod venv → SFM BERT → `source: real_agent` |
| `af-F-14` | F-14 | 1 | F | ✅ | Fix `aladdin-sfm-core.service` restart (ExecStartPost grace 15s) |
| `af-B-11` | B-11 | 1 | B | ✅ | Deploy smoke: `/api/sfm/status` sfm_loaded + active_executions OK |
| `af-Q-07` | Q-07 | 2 | Q | ✅ | If sfm_loaded → golden scam must `real_agent` (strict tier after F-13) |
| `af-P-06` | P-06 | 2 | P | ✅ | Runbook: SFM degraded, torch OOM, fallback local_ml vs rule_engine |

**Handoff для ML-агента:** [ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md](./ANTIFAKE_ML_HANDOFF_FOR_NEXT_AGENT.md)

---

### ФАЗА 1 · Batch J — Понятный результат — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-J-01` | J-01 | 1 | J | ✅ | Verdict v2: confidence bar + top-3 reasons |
| `af-J-02` | J-02 | 1 | J | ✅ | Disclaimer «не юридическое заключение» |
| `af-J-03` | J-03 | 1 | J | ✅ | **Must:** «Что делать дальше» по типу scam |
| `af-J-04` | J-04 | 1 | J | ✅ | History export PDF (`AntifakeCheckHistoryPDFExporter`) |
| `af-J-05` | J-05 | 1 | J | ✅ | **Must:** spoof hints UI |

---

### ФАЗА 1 · Batch B — Backend prod — 8 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-B-02` | B-02 | 1 | B | ✅ | **Must:** call-directory в smoke script |
| `af-B-03` | B-03 | 1 | B | ✅ | OpenAPI media routes + smoke 202 |
| `af-B-04` | B-04 | 1 | B | ✅ | Verify worker audio/video jobs prod |
| `af-B-05` | B-05 | 1 | B | ✅ | Persistent `antifake_jobs` PostgreSQL |
| `af-B-06` | B-06 | 1 | B | ✅ | nginx 25MB + timeout 300s prod |
| `af-B-07` | B-07 | 1 | B | ✅ | Deploy script + rollback runbook |
| `af-B-08` | B-08 | 1 | B | ✅ | Media TTL 15 min + cron prod |
| `af-B-09` | B-09 | 1 | B | ✅ | Rate limit + iOS 429 + unit test |

---

### ФАЗА 1 · Batch E — Post-call — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-E-03` | E-03 | 1 | E | ✅ | Tap push → Hub «Звонок» (deep link) |
| `af-E-05` | E-05 | 1 | E | ✅ | Toggle «напоминать после звонка» |
| `af-E-06` | E-06 | 1 | E | ⬜ | **Must:** device QA post-call ≤2 taps |
| `af-E-07` | E-07 | 1 | E | ✅ | Prefill caller_id from last call |
| `af-E-08` | E-08 | 1 | E | ✅ | Cooldown 1 push / 15 min |

---

### ФАЗА 1 · Batch N — Privacy — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-N-01` | N-01 | 1 | N | ✅ | **Must:** `PrivacyInfo.xcprivacy` main + extensions |
| `af-N-02` | N-02 | 1 | N | ✅ | Hash phone in logs/local history |
| `af-N-03` | N-03 | 1 | N | ✅ | Delete antifake data on account delete |
| `af-N-04` | N-04 | 1 | N | ✅ | Privacy policy section antifake |
| `af-N-05` | N-05 | 1 | N | ✅ | Consent before first media upload |

---

### ФАЗА 1 · Batch R — Release checklist — 3 задачи

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-R-01` | R-01 | 1 | R | ✅ | TestFlight checklist + `verify_antifake_release_readiness.py` (code gate) |
| `af-R-02` | R-02 | 1 | R | ⬜ | QA sign-off device: скрин метки + sync N (template+`qa_signoff/` ✅) |
| `af-R-03` | R-03 | 1 | R | ✅ | Prod smoke pass + Q-06 on VPS |

---

### ФАЗА 2 · Batch I — Crowd reports — 8 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-I-01` | I-01 | 2 | I | ✅ | UI «Сообщить о мошеннике» |
| `af-I-02` | I-02 | 2 | I | ✅ | API report + moderation queue |
| `af-I-03` | I-03 | 2 | I | ✅ | Approved reports → fraud DB |
| `af-I-04` | I-04 | 2 | I | ✅ | Label default; block only high confidence |
| `af-I-05` | I-05 | 2 | I | ✅ | Whitelist contacts |
| `af-I-06` | I-06 | 2 | I | ✅ | Appeal «не мошенник» |
| `af-I-07` | I-07 | 2 | I | ✅ | Rate limit reports |
| `af-I-08` | I-08 | 2 | I | ✅ | Report only after completed check |

---

### ФАЗА 2 · Batch L — Family moat — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-L-01` | L-01 | 2 | L | ✅ | Parent push: child `likely_fake` |
| `af-L-02` | L-02 | 2 | L | ✅ | Elderly one-tap «проверить звонок» |
| `af-L-03` | L-03 | 2 | L | ✅ | Family shared scam reports |
| `af-L-04` | L-04 | 2 | L | ✅ | Onboarding + FAQ alignment |
| `af-L-05` | L-05 | 2 | L | ✅ | (P2) Parent dashboard CD status |

---

### ФАЗА 2 · Batch M — Security — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-M-01` | M-01 | 2 | M | ✅ | TLS pinning antifake API |
| `af-M-02` | M-02 | 2 | M | ✅ | Funnel metrics enable→sync→check |
| `af-M-03` | M-03 | 2 | M | ✅ | Pen-test upload/SSRF |
| `af-M-04` | M-04 | 2 | M | ✅ | PII-safe logging |
| `af-M-05` | M-05 | 2 | M | ✅ | Secret scan App Group |

---

### ФАЗА 2 · Batch P — Ops & SRE — 5 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-P-01` | P-01 | 2 | P | ✅ | Alert job failure >5% — `antifake_ops_alerts.py --check-jobs` + cron |
| `af-P-02` | P-02 | 2 | P | ✅ | Alert queue depth >50 — `--check-queue` + cron |
| `af-P-03` | P-03 | 2 | P | ✅ | Runbook worker OOM + SFM 422 (`RUNBOOK_ANTIFAKE_WORKER_OOM.md`) |
| `af-P-04` | P-04 | 2 | P | ✅ | Mass false positive DB rollback script + runbook |
| `af-P-05` | P-05 | 2 | P | ✅ | Post-deploy checklist + `antifake_post_deploy_check.sh` |

---

### ФАЗА 2 · Batch G — Marketing — 6 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-G-01` | G-01 | 2 | G | ✅ | No «real-time all calls» — `verify_antifake_marketing_claims.py` |
| `af-G-02` | G-02 | 2 | G | ✅ | Landing + kb sync (`sync_antifake_marketing_kb.py`) |
| `af-G-03` | G-03 | 2 | G | ✅ | iOS: `bypassPremiumGate = false` + `verify_antifake_bypass_off.py` |
| `af-G-04` | G-04 | 2 | G | ✅ | Premium paywall honest limits (tariffs 5–8 + footnote) |
| `af-G-05` | G-05 | 2 | G | ✅ | App Privacy labels doc + PrivacyInfo alignment |
| `af-G-06` | G-06 | 2 | G | ✅ | (P2) Comparison vs Truecaller — honest doc |
| `af-G-07` | G-07 | 2 | G | ✅ | Policy: no contact harvest (`privacy` content_5) |

---

### ФАЗА 2 · Batch Q — Release gates — 6 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-Q-01` | Q-01 | 2 | Q | ✅ | CI assert bypass off — `verify_antifake_bypass_off.py` |
| `af-Q-02` | Q-02 | 2 | Q | ✅ | XCUITest Hub 4 tabs + `verify_antifake_q_static.sh` |
| `af-Q-03` | Q-03 | 2 | Q | ✅ | Contract test call-directory JSON |
| `af-Q-04` | Q-04 | 2 | Q | ✅ | TestFlight beta criteria doc |
| `af-Q-05` | Q-05 | 2 | Q | ✅ | Pre-submit grep: `verify_antifake_no_mock_pre_submit.py` |
| `af-Q-06` | Q-06 | 2 | Q | ✅ | Smoke + af-11: golden scam → `real_agent`\|`local_ml`, `likely_fake` |

---

### ФАЗА 3 ⏸ · Bypass off — 1 задача (G-03/Q-01 ✅)

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-G-03` | G-03 | 3 | G/B | ✅ | iOS: `bypassPremiumGate = false` |
| `af-B-10` | B-10 | 3 | G/B | ✅ | Server: `ANTIFAKE_ALLOW_FREE=0` + smoke secret |
| `af-Q-01` | Q-01 | 3 | G/B | ✅ | CI assert bypass off — см. Batch Q |

*Q-01/G-03 закрыты кодом; device QA остаётся в D/E/R.*

---

### ФАЗА 3 ⏸ · Batch H — PIR/OHTTP — 10 задач

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-H-01` | H-01 | 3 | H | ⏸ | Spike Apple PIR + Privacy Pass |
| `af-H-02` | H-02 | 3 | H | ⏸ | Backend PIR server |
| `af-H-03` | H-03 | 3 | H | ⏸ | iOS LiveCallerIDLookup extension |
| `af-H-04` | H-04 | 3 | H | ⏸ | Fallback PIR → Call Directory |
| `af-H-05` | H-05 | 3 | H | ⏸ | Min iOS 18 gate UI |
| `af-H-06` | H-06 | 3 | H | ⏸ | 2nd extension evaluate |
| `af-H-07` | H-07 | 3 | H | ⏸ | BGAppRefresh auto-sync |
| `af-H-08` | H-08 | 3 | H | ⏸ | CD entry limits perf (100k+) |
| `af-H-09` | H-09 | 3 | H | ⏸ | Apple OHTTP relay request |
| `af-H-10` | H-10 | 3 | H | ⏸ | PIR ops → P-03 runbook |

---

### ФАЗА 3 ⏸ · Batch K — On-device — 3 задачи

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-K-01` | K-01 | 3 | K | ⏸ | CoreML voice classifier research |
| `af-K-02` | K-02 | 3 | K | ⏸ | UI toggle «Проверить на устройстве» |
| `af-K-03` | K-03 | 3 | K | ⏸ | On-device uncertain → cloud check |

---

### ❌ Cancelled · Batch O — 3 задачи

| Cursor ID | ID | Ф | Batch | Статус | Зачем |
|-----------|-----|---|-------|--------|-------|
| `af-O-01` | O-01 | — | O | ❌ | Safari URL filter research — cancelled |
| `af-O-02` | O-02 | 2 | O | ❌ | NEURLFilter implementation — cancelled |
| `af-O-03` | O-03 | 2 | O | ❌ | Hub integration — cancelled (дублирует Hub) |

---

## Definition of Done (TestFlight)

**Must — функционал + точность:**

- D-04 · C-03 + C-08 · **F-01 + F-12 + F-10** · **F-08 strict** · **Q-06 pass** · F-05/R-03 green · J-03 + J-05 · E-03 + E-06 · A-05 + A-09 + A-11 · B-02 · N-01 · 9 routes prod green · R-01 pass · **G-03 + Q-01 ✅**

**Must — Apple Review (Guideline 2.3.1 / 5.1.1 / 3.1.2):**

- A-06 + A-07 + A-13 + **A-15** + G-01 + G-04 + G-05 + N-01 + N-05 + J-02 + A-14 + Q-05

**Осталось только device QA (iPhone):**

- D-01…D-04 · D-09 · E-06 · R-02

**Later — v2 (не v1):** batch **H** (PIR), batch **K** (on-device ML).

---

*При изменении статуса — обновить эту таблицу и `ANTIFAKE_TOP_TIER_PLAN.md`.*
