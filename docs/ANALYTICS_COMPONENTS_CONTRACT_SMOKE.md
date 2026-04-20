# Analytics Components Contract Smoke

Запуск локально (транспорт **только stdlib**, пакет **`requests` не нужен**):

```bash
export ALADDIN_API_BASE="https://aladdin-ai.ru"
python3 tools/contract_tests_components.py
```

Для проверки конкретного хоста (пример):

```bash
ALADDIN_API_BASE=http://149.154.65.180:8002 python3 tools/contract_tests_components.py
```

Ожидания:
- После `POST /api/auth/register-device` — JWT и серия **GET** по списку ниже.
- **200** с телом без mock‑маркеров (`sfm_mock`, `sfm_fallback`, `sfm_error`, `mock_fallback`, `"source":"mock"`), либо **503** (если gateway заблокировал mock/fallback — считается проходом для данного URL).
- Форма ответа: либо **обёртка компонента** (`componentId` + `metrics`), либо **stats** с набором ключей вроде `total`, `blocked`, `allowed`, `last_24h`, `last_7d`, `last_30d` (см. `tools/contract_tests_components.py`).

Эндпойнты (read-only, канонические пути `/api/reports/...`):

- `/api/reports/driving/stats?period=week`
- `/api/reports/dark-web/stats`
- `/api/reports/identity-theft/stats`
- `/api/reports/privacy/location/stats`
- `/api/reports/privacy/cleanup/stats`
- `/api/reports/privacy/tracker/stats`
- `/api/reports/ai-categories/stats`

Успех: в консоли `Components contract: 7/7 passed` (или эквивалент `N/N`), код выхода `0`.
