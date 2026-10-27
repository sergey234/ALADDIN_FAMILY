# ALADDIN static knowledge base v1 (ru + en)

Статический корпус для RAG v1. **Без** чатов пользователей и ПД.

## Источники (R1.1)

| Источник | Файл в репо |
|----------|-------------|
| FAQ | `Screens/13_SupportScreen.swift` → `UnifiedFAQCatalog` |
| app_help / AI copy | `Core/Localization/LocalizationManager.swift` (`faq_ai_*`, `ai_*`) |
| Onboarding | локализация onboarding keys |
| Тарифы | локализация tariff/subscription keys |
| E2EE howto | `curated/family_chat_e2ee_e2ee_{ru,en}.json` — не статусы кнопок |

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
| `documents/*.json` | FAQ + curated (ru и en) |
| `curated/*.json` | советы, которые экспорт не имеет права затереть |
| `chunks.jsonl` | чанки для ingest; без `### ключ_локализации` |

## Скрипты

```bash
./tools/rebuild_kb_v1.sh
```

Скрипт экспортирует FAQ, поверх кладёт `curated/`, собирает `chunks.jsonl` и падает, если в чанке снова есть `### ключ_локализации` или статус «Could not decrypt». Статусы семейного чата в справочник не экспортируются.

## Следующий шаг (R1.3)

Embeddings + индекс `aladdin_kb_v1` на backend (pgvector/Qdrant), без ПД пользователей.
