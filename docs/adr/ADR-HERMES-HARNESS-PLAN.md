# ADR: Hermes server-side harness — финальный план

**Status:** Accepted (2026-06-07)  
**Scope:** VPS `149.154.65.180`, `security/`, Hermes `/root/.hermes/`, ops на Mac  
**Не в scope:** iOS IPA, Stars shop checkout, Ollama Phase 2 (отложено)

## Context

- Prod уже использует узкий Hermes-bridge (`hermes chat -Q -s aladdin-security-kb`), не полный autonomous agent.
- **Фаза 0** (OpenRouter, smoke, `deepseek-v4-flash`) — **считаем выполненной**.
- Главная цель: живые ответы в AI Assistant / Companion / `@AladdinchatAI_bot`, запасной SFM при сбое, модерация для детей — **без** self-improving и **без** Ollama до метрик.
- Hermes Desktop — инструмент **команды** на Mac, не продукт для семьи.

## Decision

### P0 — всегда

| ID | Задача | Статус |
|----|--------|--------|
| 0.x | Фаза 0: баланс OR, smoke, v4-flash | ✅ Done |
| G | Guardrails на каждый deploy (см. §Guardrails) | 🔄 Постоянно |

### P1 — делаем сейчас

| ID | Задача | Срок | DoD |
|----|--------|------|-----|
| 1.1 | Hermes Desktop на Mac (pin v0.5.8+) | Неделя 1 | Установлен, версия записана |
| 1.2 | SSH tunnel → `149.154.65.180` | Неделя 1 | Chat в Desktop отвечает |
| 1.3 | Runbook 5 вопросов (Desktop + VPS) | Неделя 1 | Таблица PASS/FAIL |
| 1.4 | Проверка 3 сценариев в iOS (логи Xcode) | Неделя 1 | `hermes:aladdin-security-kb` или живой текст |
| 2.1 | Лог `llm_path` в `ai_companion_router.py` | Неделя 2 | `hermes` \| `sfm` |
| 2.2 | Лог `llm_path` в `ai_assistant_router.py` | Неделя 2 | То же |
| 2.3 | Structured log + ротация | Неделя 2 | `/var/log/aladdin-backend/companion_llm.log` |
| 2.4 | Алерт SFM > 3%/час (TG или cron) | Неделя 2 | Срабатывает на тесте |
| 2.5 | Отчёт 7 дней (CSV) | Неделя 2 | % hermes, % sfm, p95 |
| 4.1 | Аудит KB `/opt/aladdin-hermes/knowledge/` | Параллельно | Список пробелов |
| 4.2 | Обновить топ-вопросы (тарифы, parental, VPN) | Параллельно | Smoke PASS |
| 4.3 | Skill `aladdin-security-kb` enabled | Параллельно | config.yaml |
| 4.4 | Skill `aladdin-sfm-tools` read-only | Параллельно | Только read tools |
| 4.6 | Запрет auto-skill / cron self-improve в prod | Параллельно | config проверен |

### ✅ Phase 2-lite (2026-06-07, без пополнения credits)

| ID | Задача | Статус |
|----|--------|--------|
| 2L | `openrouter_direct_client.py` — короткий prompt при Hermes 402 | ✅ prod |
| 2L | Цепочка: Hermes → **OpenRouter direct** → SFM | ✅ `FEATURE_OPENROUTER_DIRECT_FALLBACK=1` |

Smoke VPS (direct): `1+1` → 2; тарифы/parental — живой текст.

### ❌ Не делаем (зафиксировано)

| ID | Задача | Причина |
|----|--------|---------|
| 3.2.x | Ollama chain (Hermes → Ollama → SFM) | Отложено до анализа метрик Фазы 2; может не понадобиться |
| 3.2.5 | Shadow mode Ollama | Вместе с 3.2 |
| — | Self-improving / memory per user в Companion | Детская безопасность |
| — | Hermes в Stars checkout / invoice / VPN | Финансовый риск |
| — | Native Hermes TG gateway вместо proxy | PII / opt-in |
| — | Desktop семьям / App Store | Не продукт |
| — | Browser / MCP / Tavily на prod VPS | Attack surface |
| — | `deepseek-v4-pro` как default | 402 на tier |

### 🏁 Финальная фаза (вручную + credits — в самом конце)

| ID | Задача | DoD |
|----|--------|-----|
| 1.2 | Hermes One.app → SSH tunnel → VPS | Chat в Desktop отвечает |
| 1.4 | iOS: 3 сценария в Xcode | `docs/HERMES_IOS_SMOKE_CHECKLIST.md` |
| 2.5 | Отчёт 7 дней CSV | cron пн 09:00, нужен трафик |
| CR | Пополнить OpenRouter credits | Hermes CLI primary, runbook 5/5 PASS |

Серверный эквивалент 1.4: `scripts/hermes_harness_smoke_api.sh` (уже PASS).

### 🟡 Отложено — делаем по условию

| ID | Задача | Когда стартовать |
|----|--------|------------------|
| 1.5 | Документ «Hermes Desktop ops» (1 стр.) | ✅ Done |
| 3.1 | Апгрейд CLI 0.14 → 0.16 | 2 недели стабильного prod + метрики OK + бэкап venv |
| 3.3 | Локальный Hermes на Mac (dev keys) | ✅ scaffold: `scripts/hermes_local_mac_setup.sh` |
| 3.2 | Ollama fallback | **Только если** отчёт 2.5: SFM > 3–5% **или** OR > $25–40/мес |
| 4.5 | agentskills.io formal versioning | Когда skills > 5 активных |
| 5.x | Gateway API вместо subprocess | Месяц 2+; p95 latency — проблема; 3.2 stable |
| 5.5 | iOS streaming SSE | Отдельный продуктовый тикет |
| 6.x | Ops-агент Stars (read-only shop.db) | По запросу админов + security review |

## Guardrails — чеклист на каждый deploy

Перед `systemctl restart aladdin-backend` или merge в `security/`:

- [ ] Нет `self-improving` / user memory / Hermes cron в prod config
- [ ] Модель: `deepseek/deepseek-v4-flash`, не v4-pro
- [ ] Нет правок `telegram_stars_shop_bot/**` в iOS-релизном коммите  
      `git diff --cached --name-only | grep -E '^telegram_stars_shop_bot/|^\.env$'` → OK
- [ ] Нет Hermes в `shop.py` / payment / VPN delivery path
- [ ] `companion_post_llm_moderation` не отключена
- [ ] Prod-ключи не в git / не на Mac dev
- [ ] Support-бот: proxy (`telegram_ai_bot_router`), не native gateway
- [ ] Авто: `scripts/hermes_deploy_guardrails.sh` (на VPS после выката)
- [ ] Smoke после деплоя: `scripts/hermes_harness_smoke_api.sh` (+ Hermes CLI когда OR credits)

## Runbook Фазы 1 (кратко)

**SSH:** `ssh -i ~/.ssh/aladdin_server root@149.154.65.180`  
**Hermes:** `/opt/aladdin-backend/venv/bin/hermes`  
**Config:** `/root/.hermes/config.yaml`, `/root/.hermes/.env`

| # | Вопрос | PASS |
|---|--------|------|
| 1 | `1+1?` | `2` |
| 2 | `Какие тарифы ALADDIN?` | Текст из KB, не SFM-шаблон |
| 3 | `Как включить родительский контроль?` | Инструкция из KB |
| 4 | `Привет, как дела?` | Дружелюбный ответ |
| 5 | Вопрос ~500 символов | Без timeout 150s |

**iOS (без пересборки):** AI Assistant «тарифы»; Companion сказка; L3 — comfort, 0 шуток.

**Фаза 1:** не менять prod config без бэкапа `config.yaml{.bak}`.

## Критерии успеха (текущий трек)

| Метрика | Цель |
|---------|------|
| % SFM-fallback Companion | Измерить (2.5), цель < 3% |
| % SFM-fallback AI Assistant | Измерить (2.5), цель < 5% |
| Инциденты 402/неделя | 0 при нормальном балансе OR |
| L3 Companion | 0 шуток, moderation PASS |

## Timeline

```
Неделя 1   P1: Фаза 1 (Desktop + runbook 1.1–1.4)
           P1: Фаза 4.1–4.4, 4.6 (старт KB)
Неделя 2   P1: Фаза 2 (метрики 2.1–2.5, отчёт 7 дней)
           P1: Фаза 4 (дозаполнение KB)
После 2.5  Решение: нужен ли Ollama (3.2) — по данным, не по умолчанию
+2 недели  🟡 3.1 CLI upgrade (если метрики OK)
Месяц 2+   🟡 Фаза 5 Gateway (если latency — боль)
По запросу 🟡 Фаза 6 Ops Stars
```

## Consequences

- **Pros:** Решения на метриках; безопасный контур для детей; быстрая ops-диагностика через Desktop; KB улучшает ответы без self-learning.
- **Cons:** Ollama отложен — при частых 402 семья может ещё видеть SFM, пока не пополнят OR или не включат 3.2 по данным.
- **Revisit:** После отчёта 2.5 — go/no-go на Ollama; после 2 недель prod — go/no-go на 3.1.

## References

- `docs/HERMES_VPS_AUDIT.md`
- `docs/COMPANION_OLLAMA_PHASE2_HANDOFF.md` (Ollama — только при go после 2.5)
- `docs/MOBILE_CODEBASE_MAP.md` §11
- `security/services/hermes_client.py`
- `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
- `.cursor/rules/no-telegram-bot-in-ios-release.mdc`
