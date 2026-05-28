# AiMonkeyVPN — информационная архитектура (UX)

## Уровни

| Уровень | Колбэк входа | Содержимое | «Назад» |
|---------|--------------|------------|---------|
| **1 Витрина** | `nav:vpn` | Приветствие, 4 карточки, 🟢 Оплата, новости | Hub |
| **2 Оплата** | `vpn:legal:gate` | **Карточка тарифов сверху**, затем политика + соглашение (2 галочки), кнопки сроков | `nav:vpn` |
| **3 Пульт** | `vpn:flow:main` | Тарифы, 📥📷🧪, Помощь, Запасные, локации, AUP | Hub |
| **Помощь** | `vpn:instr:menu` | Чеклист, файл/QR, OS, Happ, OpenVPN | `vpn:flow:main` |

## Навигация «Назад»

- Карточки L1 (`vpn:y:*`) → **✅ Понятно** → `nav:vpn` (L1).
- Подпункты Помощи → **⬅️ К меню помощи** → `vpn:instr:menu` → **⬅️ К подключению** → L3.
- Запасные подпункты → **⬅️ К запасным способам** → `vpn:fallback:menu` → L3.

## Legal

- **L2:** тарифы видны сразу; две галочки обязательны перед покупкой (`buy:`) и перед пультом.
- **L1/L3:** без URL-кнопок политики магазина; L3 только AUP.
- **Hub «Политика Stars / Premium»** — отдельно от VPN (`/vpn-data`, `/vpn-terms`).

## Аналитика (`analytics_events`)

| event_type | Когда |
|------------|--------|
| `vpn_nav_marketing` | Открыт раздел VPN (витрина) |
| `vpn_legal_gate_open` | 🟢 Оплата → экран галочек |
| `vpn_legal_continue` | Галочки OK → тарифы |
| `vpn_marketing_card` | meta.card: speed/dev/priv/bypass |
| `vpn_help_menu_open` | 📖 Помощь |

## Деплой

`ROOT=/opt/aladdin-telegram-shop-bot`, rsync `telegram_stars_shop_bot/`, restart три systemd unit'а бота.
