# Локальный Hermes на Mac (задача 3.3)

**Для кого:** разработка и эксперименты. **Не prod**, не ключи с VPS.

## Зачем

- Тестировать skills/KB до выката на `149.154.65.180`
- Отлаживать промпты без SSH
- Не трогать `/root/.hermes/` на сервере

## Быстрый старт

```bash
cd mobile_apps/ALADDIN_iOS
./scripts/hermes_local_mac_setup.sh
```

Требуется **Python 3.11+** (скрипт ставит 3.12 через `uv`, если на Mac только 3.9).

Скрипт создаёт `~/.aladdin-hermes-dev/`:
- venv + `hermes-agent` (pip)
- symlink на `security/hermes_knowledge/` из репо
- `dev.env.example` — скопировать в `dev.env` и вставить **dev** OpenRouter key

## Первый запуск

```bash
source ~/.aladdin-hermes-dev/activate.sh
export HERMES_HOME=~/.aladdin-hermes-dev/hermes-home
hermes --version
hermes chat -q "1+1?" -Q
```

## Правила

| Можно | Нельзя |
|-------|--------|
| Свой dev-ключ OpenRouter | Prod-ключ с VPS |
| Копия KB из репо | `self-improving` / cron в dev → prod |
| `--skip-browser` install | Пушить `dev.env` в git |

## Связь с Desktop

**Hermes One.app** (задача 1.2) — tunnel к prod VPS.  
Локальный Hermes (3.3) — отдельный контур на Mac.

Обе задачи — **финальная фаза** вместе с 1.4, 2.5 и пополнением credits.

См. `docs/adr/ADR-HERMES-HARNESS-PLAN.md`
