# План: оптимизация меню Monkey Stars (UI-only)

**Дата:** 2026-07-30  
**Код:** `telegram_stars_shop_bot/`  
**ТЗ:** только меню/отображение — без оплаты, API, БД-схемы, выдачи Stars/Premium/VPN.

## Как устроено сейчас

| Место | Файл |
|-------|------|
| Главное меню | `bot/keyboards/shop_kb.py` → `hub_menu_kb` |
| Профиль | `bot/handlers/hub.py` → `nav_profile` + `profile_inline_kb_rows_prefix` |
| Тарифы VPN | `bot/services/vpn_tariffs.py` (`270` = 9 месяцев) |
| Согласие 1-й старт | `onboarding` → `users.terms_accepted_at` |
| Повтор в VPN | `bot/services/vpn_legal_gate.py` → `vpn_*_accepted_at` |
| AI кнопка | `assistant_menu_visible` в `hub_menu_kb` |

## Целевое главное меню

⭐ Stars · 💎 Premium · 🛡 VPN · 👤 Профиль · 👥 Пригласить друга

## Изменения

1. Hub: убрать Заказы/Конкурс/Новости/Пополнить/AI; Support→профиль; Partners/Gifts/API→профиль (если флаги).
2. Профиль: Заказы, Конкурс, Новости, Пополнить (+ Поддержка).
3. VPN legal: если `terms_accepted` на онбординге — не показывать gate снова.
4. UI-filter: не показывать тариф `270` дней (9 мес.); продукт в каталоге остаётся.
5. AI: не рисовать кнопку; handlers/код оставить.

## Тест / деплой

- `pytest tests/test_ux_ab_hub.py` + точечные assert меню
- rsync/restart shop bot на Contabo/MAIN по существующему runbook
