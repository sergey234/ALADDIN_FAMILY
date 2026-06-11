# Hermes harness — статус (без локального Hermes)

**Обновлено:** 2026-06-07  
**План:** `docs/adr/ADR-HERMES-HARNESS-PLAN.md`  
**VPS:** `149.154.65.180` · backend `/opt/aladdin-backend` · Hermes `/root/.hermes/`

---

## Цель одной фразой

Живые ответы в **iOS AI Assistant**, **Companion** и **@AladdinchatAI_bot** через server-side harness на VPS — с запасным путём при сбое, без self-improving и без Ollama (пока).

**Локальный Hermes на Mac (3.3) — не делаем.** Достаточно VPS + Hermes One.app (финал).

---

## ✅ Сделано

### P0 — стабильность

| Что | Детали |
|-----|--------|
| Фаза 0 | OpenRouter key на VPS, `deepseek-v4-flash`, smoke |
| Guardrails | `scripts/hermes_deploy_guardrails.sh` — PASS на VPS |
| Phase 2-lite | `openrouter_direct_client.py` в prod, `FEATURE_OPENROUTER_DIRECT_FALLBACK=1` |

**Цепочка в prod сейчас:**

```
Companion:   Hermes CLI (402 на free tier) → OpenRouter direct → SFM
Assistant:   kb_rag (тарифы) / Hermes → OpenRouter direct → SFM
Support-бот: тот же stack, что Assistant (proxy, не native gateway)
```

### P1 — Фаза 1 (авто)

| ID | Статус | Что |
|----|--------|-----|
| 1.1 | ✅ | Hermes One.app v0.5.8 в `/Applications` |
| 1.3 | ✅ | Runbook: direct OR PASS; Hermes CLI ждёт credits |
| 1.5 | ✅ | `docs/HERMES_DESKTOP_OPS.md` |

### P1 — Фаза 2 (метрики)

| ID | Статус | Что |
|----|--------|-----|
| 2.1 | ✅ | `llm_path` в `ai_companion_router.py` |
| 2.2 | ✅ | `llm_path` в `ai_assistant_router.py` |
| 2.3 | ✅ | `companion_llm.log` + logrotate |
| 2.4 | ✅ | Алерт SFM > 3%/час — cron |

### P1 — Фаза 4 (KB)

| ID | Статус | Что |
|----|--------|-----|
| 4.1–4.2 | ✅ | Аудит + KB тарифы/parental/VPN на VPS |
| 4.3–4.4 | ✅ | Skills `aladdin-security-kb`, `aladdin-sfm-tools` |
| 4.6 | ✅ | Cron self-improve пустой |

### Дополнительно

| Что | Файл |
|-----|------|
| Server smoke | `scripts/hermes_harness_smoke_api.sh` — PASS |
| Support-бот smoke | `scripts/telegram_support_bot_smoke.sh` — PASS |
| Unit tests | `Tests/security/test_openrouter_direct_client.py` — 4/4 |
| Latency baseline | `scripts/companion_llm_latency_baseline.sh` |
| Ops deploy | `scripts/deploy_hermes_harness_ops.sh` |
| iOS чеклист | `docs/HERMES_IOS_SMOKE_CHECKLIST.md` |

---

## 🏁 Осталось — финал (вручную, в конце)

| ID | Задача | DoD |
|----|--------|-----|
| **1.2** | Hermes One → SSH tunnel | Chat в Desktop |
| **1.4** | iOS 3 сценария в Xcode | `HERMES_IOS_SMOKE_CHECKLIST.md` |
| **2.5** | Отчёт 7 дней CSV | cron пн 09:00 + трафик |
| **CR** | Пополнить OpenRouter | Hermes CLI 5/5, не 402 |

---

## 🟡 По условию (не сейчас)

| ID | Когда |
|----|-------|
| **3.1** CLI 0.14→0.16 | +2 нед prod |
| **3.2** Ollama | Только если SFM > 3–5% или OR > $25–40 |
| **4.5** skills versioning | skills > 5 |
| **5.x** Gateway API | p95 > 15s стабильно |
| **6.x** Stars ops | По запросу админов |

---

## ❌ Не делаем

- Локальный Hermes Mac (3.3)
- Self-improving / cron в prod
- Hermes в Stars / VPN
- Native TG gateway
- Ollama до метрик

---

## Команды

```bash
bash /opt/aladdin-backend/scripts/hermes_deploy_guardrails.sh
bash /opt/aladdin-backend/scripts/hermes_harness_smoke_api.sh http://127.0.0.1:8002
./scripts/telegram_support_bot_smoke.sh
./scripts/deploy_hermes_harness_ops.sh
```

**SSH:** `ssh -i ~/.ssh/aladdin_server root@149.154.65.180`

---

## Старый Hermes и старый API — нужны ли?

**Коротко: да, оба нужны.** Мы их **не выкинули** — **улучшили обвязку** вокруг них. iOS и бот ходят в **те же URL**, что и раньше.

### Что осталось «старым» и зачем

| Компонент | Файл / endpoint | Роль сейчас | Убираем? |
|-----------|-----------------|-------------|----------|
| **Hermes CLI bridge** | `security/services/hermes_client.py` | Primary LLM: `hermes chat -Q -s aladdin-security-kb` | ❌ Нет — станет primary после credits |
| **SFM fallback** | `security/services/ai_sfm_http_chat.py` | Последний запасной путь (шаблоны без «1074 функций») | ❌ Нет — safety net |
| **KB-RAG** | `kb_rag_service` | Тарифы/FAQ из markdown без LLM | ❌ Нет — быстро и дёшево |
| **Публичный API** | `/api/ai/assistant/chat`, `/api/ai/companion/chat`, `/api/telegram/bot/chat` | Контракт для iOS и support-бота | ❌ Нет — приложение не пересобирали |

### Что добавили (улучшение harness)

| Новое | Зачем |
|-------|-------|
| `openrouter_direct_client.py` | Короткий prompt при Hermes **402** (free tier) — живой ответ без тяжёлого CLI |
| `companion_llm_metrics.py` + `companion_llm.log` | Видим `llm_path`: hermes / openrouter_direct / sfm / kb_rag |
| Расширенная KB на VPS | Тарифы, parental, VPN |
| Guardrails + smoke scripts | Безопасный deploy |
| `hermes_key_rotator.py` | Ротация ключей OR при 401/429 |

### Цепочки после улучшения

**AI Assistant:**
```
intent → kb_rag (если FAQ) → Hermes CLI → OpenRouter direct → SFM
```

**Companion:**
```
Hermes CLI → OpenRouter direct → SFM (+ модерация, age policy — как было)
```

**Support-бот:** тот же `ai_assistant_chat` через proxy (`telegram_ai_bot_router`).

### Когда «старый» Hermes можно будет ослабить

Только **5.x Gateway API** (условно, месяц 2+): subprocess `hermes chat` заменить на HTTP к Hermes gateway — **если** p95 latency станет проблемой. SFM fallback **всё равно оставляем**.

### Итог простым языком

- **Старый API** — тот же «телефонный номер» для приложения. Меняли **мозг на сервере**, не контракт.
- **Старый Hermes CLI** — по-прежнему главный путь; сейчас упирается в 402, поэтому работает **OpenRouter direct**.
- **Старый SFM** — страховка на случай полного сбоя LLM. Без него семья снова увидит пустоту или ошибку.

**Локальный Hermes на Mac не нужен** — prod на VPS + Hermes One (финал) достаточно.
