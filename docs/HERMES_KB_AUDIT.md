# Hermes KB — аудит (задача 4.1)

**Дата:** 2026-06-07  
**Путь prod:** `/opt/aladdin-hermes/knowledge/`

## Было (до 4.2)

| Файл | Тема | Пробел |
|------|------|--------|
| AI_PRODUCT_CAPABILITY_MATRIX.md | Возможности продукта | ✅ |
| AI_RESPONSE_POLICY.md | Политика ответов | ✅ |
| E1_E2EE_FAMILY_CHAT_DESIGN.md | Семейный чат E2EE | ✅ |
| README_ALADDIN_KB.md | Индекс | ✅ |
| — | **Тарифы / подписки** | ❌ не было |
| — | **Родительский контроль how-to** | ❌ не было |
| — | **VPN (app vs shop)** | ❌ не было |

## Добавлено (4.2)

| Файл | Источник в репо |
|------|-----------------|
| ALADDIN_TARIFFS_AND_SUBSCRIPTIONS.md | `security/hermes_knowledge/` |
| ALADDIN_PARENTAL_CONTROL.md | `security/hermes_knowledge/` |
| ALADDIN_VPN_PRODUCT.md | `security/hermes_knowledge/` |
| manifest.json | обновлён |

Деплой: `./scripts/deploy_hermes_kb.sh`

## Smoke после ключа OpenRouter

```bash
hermes chat -q "Какие тарифы ALADDIN?" -Q -s aladdin-security-kb
hermes chat -q "Как включить родительский контроль?" -Q -s aladdin-security-kb
```

**Статус smoke:** BLOCKED — OpenRouter 401 `User not found` (ключ на VPS недействителен).
