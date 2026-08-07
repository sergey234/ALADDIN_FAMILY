# План: один стартовый экран (канал + согласие)

**Дата:** 2026-07-30  
**Код:** `telegram_stars_shop_bot/`  
**Трекер:** [`ONBOARDING_COMBINED_TODO_TRACKER.md`](./ONBOARDING_COMBINED_TODO_TRACKER.md)

## Цель

Объединить два экрана первого запуска (оферта + подписка на канал) в один.  
Кнопка «✅ Проверить подписку» = проверка канала + запись `users.terms_accepted_at`.

## Путь

1. Язык (без изменений)  
2. **Один экран** канал + документы + «Проверить подписку»  
3. Капча онбординга (без изменений)  
4. Хаб  

## VPN

Повторный legal gate не показывается, если уже есть `terms_accepted_at`  
(`users_repo.has_vpn_legal_accepted`).

## Файлы

- `bot/services/marketing.py` — `onboarding_combined_caption_html`
- `bot/keyboards/shop_kb.py` — `onboarding_combined_kb`
- `bot/services/onboarding_gate.py` — pipeline
- `bot/handlers/common.py` — `onb:ch:check` → `accept_terms`
