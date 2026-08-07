# Runbook: Помощник AiMonkey v1

**PRD:** `PLAN_AIMONKEY_ASSISTANT_V1_2026-07-15.md`  
**Сервис:** `aladdin-telegram-bot.service` (Contabo shop bot)  
**Не путать** с iOS Companion Hermes.

---

## Env (shared `.env`)

| Key | Meaning |
|-----|---------|
| `ASSISTANT_ENABLED` | `0/1` master |
| `ASSISTANT_ADMIN_ONLY` | `1` = только `ADMIN_IDS` |
| `ASSISTANT_LLM_BASE_URL` | OpenAI-compatible base |
| `ASSISTANT_LLM_API_KEY` | secret |
| `ASSISTANT_LLM_MODEL` | model id |
| `ASSISTANT_ADMIN_CHAT_ID` | куда слать тикеты (optional) |
| `ASSISTANT_TICKET_DAILY_LIMIT` | default 5 |
| `ASSISTANT_PAY_SLA_MIN` | default 30 |
| `ASSISTANT_DAILY_MSG_LIMIT` | default 40 |
| `ASSISTANT_SESSION_TTL_MIN` | default 30 |
| `ASSISTANT_MAX_OUT_TOKENS` | default 800 |
| `ASSISTANT_LLM_TIMEOUT_SEC` | default 45 |

На Contabo: OpenRouter + **auto-failover**.  
- `ASSISTANT_LLM_MODEL` — основная (prod 2026-08-02: `deepseek/deepseek-v4-flash`).  
- `ASSISTANT_LLM_FALLBACK_MODELS` — `deepseek/deepseek-chat` + `:free` / `openrouter/free` (при 402/429/5xx).  
- Пустой FALLBACK + `openrouter.ai` → встроенная free-цепочка в коде.  
- При низком балансе OpenRouter paid → 402 → free (ожидаемо; пополнить credits для Flash).  
Smoke: `scripts/smoke_assistant_llm_failover.py` / `scripts/smoke_assistant_contabo.py`.

Полный список — `env.example` после `as-1-env`.

---

## Включение (безопасный порядок)

1. Deploy кода с `ASSISTANT_ENABLED=0` → health OK.  
2. Прописать LLM keys.  
3. `ASSISTANT_ENABLED=1` + `ASSISTANT_ADMIN_ONLY=1` → restart bot.  
4. С ADMIN_IDS: сценарии T1–T7 из PRD §12.  
5. 3–7 дней без инцидентов → `ASSISTANT_ADMIN_ONLY=0`.

---

## Размещение Contabo

Помощник живёт **в том же** `aladdin-telegram-bot` на Contabo.  
Секреты: `/opt/aladdin-telegram-shop-bot/shared/.env`.  
Отдельный сервер / Docker-swarm / Hermes gateway на Contabo для v1 **не** поднимаем.

## Kill-switch

```bash
# на Contabo
# ASSISTANT_ENABLED=0 в shared/.env
sudo systemctl restart aladdin-telegram-bot.service
```

Старая «Поддержка» + `SUPPORT_URL` остаются.

---

## Тикеты

Таблица `assistant_tickets` + сообщение в admin chat + prefill в SUPPORT_URL.  
Write-actions (revoke/extend/refund/reprovision) — **только** ручные `/admin_vpn_*` / support, не из помощника.  
Будущий дизайн (не ship): `docs/DESIGN_ASSISTANT_WRITE_TOOLS_2026-08-02.md`.

---

## Инциденты

| Симптом | Действие |
|---------|----------|
| Галлюцинации how-to | OFF flag; проверить KB hash / SSOT |
| Утечка sub-link | OFF; проверить validator + masks |
| LLM timeout / 5xx | Юзеру «временно недоступен» + кнопка Человек; не падать polling |
| Cost spike | снизить daily limit / max tokens |
