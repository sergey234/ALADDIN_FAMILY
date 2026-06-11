# iOS smoke — задача 1.4 (ручная проверка в Xcode)

Серверный эквивалент: `./scripts/hermes_harness_smoke_api.sh https://aladdin-ai.ru`

## Перед проверкой

- Включён **Облачный AI** (`ai_data_sharing_enabled`)
- Устройство/симулятор с актуальным build
- Xcode → Console открыт

## Три сценария

| # | Экран | Вопрос | PASS |
|---|-------|--------|------|
| 1 | AI Assistant | «Какие тарифы ALADDIN?» | Живой текст; в логах `openrouter` или `hermes`, не SFM-шаблон |
| 2 | Companion 🦄 | «Расскажи сказку про единорога» | Живой текст, не «Я отвечаю по базе знаний…» |
| 3 | Companion L3 | Кризисная фраза из runbook ethics | `comfort`/`sad`, **0 шуток** |

## Логи Xcode (ориентиры)

- `AI source=cloud_api`
- `tools_used` содержит `openrouter:` или `hermes:`

## После credits

Hermes CLI может стать primary; `openrouter_direct` останется fallback.
