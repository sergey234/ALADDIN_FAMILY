# Analytics Components Contract Smoke

Запуск локально:

```bash
export ALADDIN_API_BASE="https://aladdin-ai.ru"
python3 tools/contract_tests_components.py
```

Ожидания:
- 200 OK с DTO:
  - `componentId`: строка
  - `metrics`: объект с нормализованными ключами
- Либо 503 (если gateway заблокировал mock/fallback).
- В ответах не должно быть `sfm_mock | sfm_fallback | sfm_error | mock_fallback | "source":"mock"`.

Эндпойнты (read-only):
- /api/reports/driving/stats?period=week
- /api/darkweb/stats
- /api/identity/stats
- /api/location/stats
- /api/data/cleanup/stats
- /api/reports/tracker/stats (если доступен)
- /api/ai/categories/stats

Успех: 7/7 PASS (или 6/7, если `tracker` недоступен), без падений и без mock‑маркеров.

