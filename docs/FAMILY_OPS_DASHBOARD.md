# Family API — логи и метрики для дашборда (P2)

Канонический роутер: `app/routers/family.py` (деплой на хост API, не дубли в архивных папках).

## События для подсчёта / алертов

| Строка в логе (structlog / JSON) | Смысл |
|----------------------------------|--------|
| `metric_family_members_get_ok` | Успешный `GET /api/family/members`. Поля: `family_id`, `count`, `user_id`. |
| `metric_family_members_get_409` | Конфликт query `familyId` с семьёй по JWT. Поля: `query_family_id`, `resolved_family_id`, `user_id`. |
| `family_members_family_id_mismatch` | То же 409, уровень warning (деталь диагностики). |
| `metric_family_members_count` | Ранее: gauge по числу участников (можно строить рядом с `get_ok`). |

## Заголовки ответа

- `X-Resolved-Family-Id` — семья, для которой отдан полный список строк из БД.

## Примеры запросов к логам (Loki / CloudWatch / grep)

```text
{app="aladdin"} |= "metric_family_members_get_409"
{app="aladdin"} |= "metric_family_members_get_ok"
```

**Алерт (рекомендация):** rate(`metric_family_members_get_409`) > N за 5m на фоне стабильного трафика → проверить версию iOS / кэш `family_id` / миграции аккаунтов.

## OpenAPI после деплоя

```bash
curl -s -S -m 12 "http://<HOST>:8002/openapi.json" | jq '.paths["/api/family/members"]'
```

Ожидается query-параметр `familyId` (optional) у `GET /api/family/members` после выката.
