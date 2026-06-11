# Hermes Desktop — ops (1 страница)

**Для кого:** команда (Mac), не пользователи ALADDIN.  
**VPS:** `ssh -i ~/.ssh/aladdin_server root@149.154.65.180`

## 1. Установка

1. DMG уже в репо: `tools/hermes_desktop/hermes-desktop-0.5.8-arm64.dmg` (или [releases](https://github.com/fathah/hermes-desktop/releases))
2. Открыть DMG → перетащить **Hermes One** в Applications (`/Applications/Hermes One.app`)
3. Записать версию в ADR / internal notes

## 2. SSH tunnel

| Поле | Значение |
|------|----------|
| Host | `149.154.65.180` |
| User | `root` |
| Key | `~/.ssh/aladdin_server` |
| Hermes binary | `/opt/aladdin-backend/venv/bin/hermes` |
| Config | `/root/.hermes/config.yaml` |
| Env | `/root/.hermes/.env` |

## 3. Runbook (5 вопросов)

| # | Вопрос | PASS |
|---|--------|------|
| 1 | `1+1?` | `2` |
| 2 | `Какие тарифы ALADDIN?` | Из KB |
| 3 | `Как включить родительский контроль?` | Инструкция |
| 4 | `Привет, как дела?` | Живой ответ |
| 5 | Длинный вопрос ~500 симв. | Без timeout |

Терминал (дубль Desktop):

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  '/opt/aladdin-backend/venv/bin/hermes chat -q "Какие тарифы ALADDIN?" -Q -s aladdin-security-kb'
```

## 4. OpenRouter ключ

```bash
# проверка на VPS
bash scripts/hermes_openrouter_key_check.sh /root/.hermes/.env

# обновление (на VPS, ключ в env — не в чат)
OPENROUTER_API_KEY='sk-or-v1-...' bash scripts/hermes_openrouter_key_update.sh
```

## 5. Guardrails + smoke (каждый deploy)

```bash
# на VPS после выката
bash /opt/aladdin-backend/scripts/hermes_deploy_guardrails.sh
bash /opt/aladdin-backend/scripts/hermes_harness_smoke_api.sh http://127.0.0.1:8002
```

Локальный выкат ops-скриптов: `./scripts/deploy_hermes_harness_ops.sh`

iOS ручная проверка (1.4): `docs/HERMES_IOS_SMOKE_CHECKLIST.md`

## 6. Не делать

- Не менять prod config без `.bak`
- Не ставить Desktop семье
- Не включать self-improving / cron / browser tools на prod

См. `docs/adr/ADR-HERMES-HARNESS-PLAN.md`
