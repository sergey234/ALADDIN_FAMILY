# Companion Sprint 5 — MVP env (без реального Search API)

**Обновлено:** 2026-05-29

| Переменная | MVP на проде | Смысл |
|------------|--------------|--------|
| `FEATURE_WEB_SEARCH_ENABLED` | **`0`** (по умолчанию) | Поиск = заглушка: при `1` — citations из `companion_web_search.py`, без внешнего Search API |
| `FEATURE_IMAGE_GEN_ENABLED` | **`0`** | Картинки/видео не обещаем в UI |
| `FEATURE_WORKSPACES_ENABLED` | **`1`** при UI папок | Workspaces API + «Моё» |

**MVP 5.1:** достаточно `FEATURE_WEB_SEARCH_ENABLED=0` и этой заметки. Реальный Search API — отдельный этап.

**Stream = Chat:** `POST /stream` вызывает тот же `companion_chat()` → family hint, long context, social bridge — один путь (audit 5.5 ✅).

---

## Media / image gen (5.9 stub)

| Переменная | MVP | UI |
|------------|-----|-----|
| `FEATURE_IMAGE_GEN_ENABLED` | **`0`** | Нет кнопки «Сгенерировать картинку» в companion |
| `FEATURE_VIDEO_GEN_ENABLED` | **`0`** | Нет video в Kids |

**Поведение:** `companion_media_gen.py` на бэкенде возвращает 503 при `0`; iOS не вызывает media endpoints. Визуал героев — **PNG/Rive**, не generative media.

**Premium TTS (отдельно):** см. [COMPANION_NEURO_TTS_ENV.md](./COMPANION_NEURO_TTS_ENV.md) — не путать с `media_gen`.
