# AI Assistant — источники ответов (Build 198)

## Порядок на клиенте

1. **FAQ локально** — `UnifiedFAQCatalog.bestMatch` → лог `AI source=faq_local`, без сети.
2. **Облачный API** — `POST` `aiAssistantChat` при включённом `ai_data_sharing_enabled`.
3. **Ошибка сети** — UI error, без локального «умного» fallback.

Hermes/SFM работают **на сервере**; iOS только получает JSON.

## Mock / SFM на проде

`NetworkManager` отклоняет envelope с `source` ∈ `sfm_mock`, `sfm_fallback`, `mock`.

Если декодирование прошло, но текст содержит маркеры вроде «реальный AI ALADDIN» / «1074 функций» — в логах:

`AI source=cloud_api_probable_mock`

Это **не** доказательство Hermes на устройстве; проверять VPS и `tools/smoke_ai_eval_top10_prod.py`.

## Настройки

- **Облачный AI-помощник** — `ai_data_sharing_enabled` (без согласия отправка блокируется).
- История чата — UserDefaults / локальное хранилище экрана, не «обучение» модели на устройстве.
