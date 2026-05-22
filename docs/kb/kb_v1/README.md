# ALADDIN static knowledge base v1 (ru + en)

Статический корпус для RAG v1. **Без** чатов пользователей и ПД.

## Источники (R1.1)

| Источник | Файл в репо |
|----------|-------------|
| FAQ | `Screens/13_SupportScreen.swift` → `UnifiedFAQCatalog` |
| app_help / AI copy | `Core/Localization/LocalizationManager.swift` (`faq_ai_*`, `ai_*`) |
| Onboarding | локализация onboarding keys |
| Тарифы | локализация tariff/subscription keys |
| E2EE howto | локализация e2ee / family chat keys |

## Формат документа (ingest R1.2)

```json
{
  "id": "faq_tariff_premium_ru",
  "locale": "ru",
  "topic": "tariff",
  "title": "...",
  "body": "..."
}
```

## Правила

- `locale`: `ru` | `en` — оба с первого дня.
- Версия индекса на сервере: `aladdin_kb_v1`.
- Пользовательские данные в корпус **не** класть.

## Артефакты (сгенерировано)

| Файл | Описание |
|------|----------|
| `manifest.json` | Версия, счётчики, topics |
| `documents/*.json` | 78 документов (39 ru + 39 en) |
| `chunks.jsonl` | 87 чанков для ingest |

## Скрипты

```bash
python3 tools/export_kb_v1.py
python3 tools/ingest_kb_v1_chunks.py
```

## Следующий шаг (R1.3)

Embeddings + индекс `aladdin_kb_v1` на backend (pgvector/Qdrant), без ПД пользователей.
