# P1.4 KB / gold — 2026-08-02

**Без Flash API:** обновление вручную из `products.yaml` + runbooks.

## Changes

| Что | Где |
|-----|-----|
| KB chunk `kb.catalog` | `bot/assistant/kb.py` ← `catalog_kb_plain()` из `products.yaml` |
| Topic `catalog` | orchestrator `_guess_topic`, `TOPIC_TO_KB`, gold few-shots |
| Gold T11 prices | `brand_gold_answers.py` — цены → меню/каталог; no uptime 100% |
| Brand voice fix | `AIMONKEY_ASSISTANT_BRAND_VOICE.md` — реферальный ≠ «только VPN» |
| Tests | `tests/test_assistant_gold_kb.py` |

## Rules for assistant prices

- VPN fixed ₽ only if `price_rub` in YAML (e.g. 30д = 200 ₽).
- Stars/Premium: name package + «смотрите меню»; не выдумывать ₽.
- Ban: 100% uptime, гарантии скорости, «примерно всегда».

## Review

Человек: сверить `kb.catalog` текст с актуальным `bot/products.yaml` после смены прайса.
