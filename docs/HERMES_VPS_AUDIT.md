# Hermes на VPS — аудит и чеклист (ALADDIN prod)

Дата проверки: 2026-05-21  
Сервер: `149.154.65.180`, backend `/opt/aladdin-backend`, Hermes `v0.14.0`.

## Два сценария (не путать)

| Сценарий | Цель | Что обязательно |
|----------|------|-----------------|
| **ALADDIN iOS** | AI в приложении: диалог + знание продукта + данные защиты | OpenRouter, Hermes, 2 skills, KB, баланс OR |
| **Гайд YouTube** | Личный ассистент: TG, скраперы, браузер, desktop | Всё из видео — **не нужно** для TestFlight |

---

## Базовый runtime

| Проверка | Требование | Факт | OK |
|----------|------------|------|-----|
| Node | 22+ | v22.22.2 | ✅ |
| Python | 3.11+ | 3.12.3 | ✅ |
| pnpm | есть (гайд) | нет на VPS | ⚪ не нужен для API |
| git | установлен | 2.43.0 | ✅ |
| Hermes CLI | venv | 0.14.0 | ✅ |

---

## ALADDIN prod (обязательно)

| # | Пункт | Статус | Действие |
|---|--------|--------|----------|
| 1 | `OPENROUTER_API_KEY` в `/root/.hermes/.env` и `/opt/aladdin-backend/.env` | ✅ | Ротировать ключ, если светился в чате |
| 2 | Баланс OpenRouter (не free-tier 402) | ⚠️ | [openrouter.ai/settings/credits](https://openrouter.ai/settings/credits) |
| 3 | Модель **`deepseek/deepseek-v4-flash`** (prod) | ✅ на VPS | V4 Pro на free-tier даёт **402** (лимит prompt ~11k > ~5.6k); V4 Flash проходит Hermes `-Q` |
| 4 | `model.max_tokens: 2048` | ✅ | избегает 402 на больших лимитах |
| 5 | Skills: `aladdin-security-kb` + `aladdin-sfm-tools` | ✅ в config | оба enabled |
| 6 | KB `/opt/aladdin-hermes/knowledge/` | ✅ | — |
| 7 | `AI_BACKEND=sfm` + Hermes first для `general` | ✅ в коде | — |
| 8 | SFM fallback `ai_sfm_http_chat.py` (1+1, off-topic) | ✅ задеплоено | — |

### Smoke после правок

```bash
# на VPS
/opt/aladdin-backend/venv/bin/hermes chat -q "1+1?" -Q -s aladdin-security-kb
/opt/aladdin-backend/venv/bin/hermes chat -q "Какие тарифы ALADDIN?" -Q -s aladdin-security-kb
systemctl restart aladdin-backend.service
```

В iOS в логах ожидаем: `AI source=cloud_api`, `tools=hermes:aladdin-security-kb` (или `hermes:...`), не только шаблон SFM.

---

## Гайд YouTube (опционально для ALADDIN)

| Пункт | Нужно для iOS? | Статус на VPS |
|-------|----------------|---------------|
| `hermes gateway setup` | ⚪ | ✅ state.db есть |
| TG / Discord / MatterMost | ❌ | ❌ pairing пусто |
| `hermes tools` (интерактив) | ❌ | не прогоняли (TTY) |
| Tavily, Firecrawl, GitHub keys | ❌ | ❌ |
| browser-use, playwright, desktop | ❌ | ❌ |
| Skills Hub (десятки skills) | ❌ | 0 hub, 2 local ALADDIN |
| Hermes cron | ❌ | папка cron пуста |
| pnpm на сервере | ❌ | нет |

---

## Модели OpenRouter (справка)

| Slug | Назначение |
|------|------------|
| `deepseek/deepseek-v4-flash` | **Prod на free-tier** — быстрый MoE, 1M context; Hermes + API `1+1` → `2` |
| `deepseek/deepseek-v4-pro` | Максимум качества; на free-tier **402** из‑за огромного agent-prompt Hermes |
| `deepseek/deepseek-v4-flash:free` | Бесплатный вариант; часто **429** rate limit |
| `deepseek/deepseek-chat-v3.1` | Запасной — стабильно в Hermes (`1+1 = 2`) |

Прямой OpenRouter (короткий prompt, `max_tokens: 64`): все четыре slug отвечают `2`.  
Разница проявляется в **Hermes CLI** (`hermes chat -Q -s aladdin-security-kb`): Pro → 402, Flash → OK.

[DeepSeek V4 Flash](https://openrouter.ai/deepseek/deepseek-v4-flash) — reasoning через параметр `reasoning` / `reasoning_details` (опционально).

---

## Почему «hermes tools» не через SSH-бота

Команда `hermes tools` открывает **интерактивное меню** (как `nano`). Через автоматический SSH без TTY Hermes пишет: *requires interactive terminal*.

**Что делать:** зайти на сервер вручную: `ssh root@...`, затем `hermes tools` — только если нужны Tavily/Firecrawl и т.д. Для ALADDIN iOS **не обязательно**.

---

## Скраперы (Tavily, Firecrawl, GitHub)

Нужны, если агент должен **искать в интернете** или ходить на сайты.  
ALADDIN отвечает из **KB + SFM aggregates** — без скраперов.

Добавление (опционально): ключи в `/root/.hermes/.env`, затем `hermes tools` интерактивно.

---

## iOS: настройки → онбординг

Отдельный фикс в коде (build 200+): `MainScreen` без `NavigationLink` на Settings, проверка онбординга по `UserDefaults`.

---

## История инцидентов

| Симптом | Причина |
|---------|---------|
| Шаблон «Я отвечаю по базе знаний…» | Hermes 402 → fallback SFM rules |
| HTTP 402 OpenRouter | free tier: мало credits или лимит prompt tokens (V4 Pro тяжелее) |
| «Не DeepSeek v4» | был `deepseek-chat` (V3) → сейчас **`deepseek-v4-flash`** (не Pro: 402 на free) |
| Hermes warning в тексте ответа | stderr Hermes попадает в stdout — косметика; ответ всё равно от модели |

---

## Контакты конфигов

- `/root/.hermes/config.yaml` — модель, skills, system_prompt  
- `/root/.hermes/.env` — секреты (OpenRouter)  
- `/opt/aladdin-backend/.env` — `AI_BACKEND`, `OPENROUTER_API_KEY` для systemd  

После изменений: `systemctl restart aladdin-backend.service`.
