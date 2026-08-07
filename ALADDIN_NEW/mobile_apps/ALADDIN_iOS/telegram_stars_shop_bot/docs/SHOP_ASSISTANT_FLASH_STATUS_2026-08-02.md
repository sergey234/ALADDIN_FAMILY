# Shop assistant Flash — Contabo 2026-08-02

**Host:** Contabo `185.225.233.150` (polling marker OK; MAIN 149.* must not poll).  
**Env:** `/opt/aladdin-telegram-shop-bot/shared/.env`  
**Backup:** `.env.bak_assistant_flash_*`

| Key | Value |
|-----|--------|
| `ASSISTANT_LLM_MODEL` | `deepseek/deepseek-v4-flash` |
| `ASSISTANT_LLM_FALLBACK_MODELS` | `deepseek/deepseek-chat` → free chain |
| `ASSISTANT_LLM_BASE_URL` | `https://openrouter.ai/api/v1` |

**Smoke:** `smoke_assistant_llm_failover.py` → `FAILOVER_SMOKE_OK`  
Observed: Flash+chat **402** (мало OpenRouter credits) → `openrouter/free` ответил «ок».  
Цепочка failover работает; для реальных ответов Flash — пополнить OpenRouter.
