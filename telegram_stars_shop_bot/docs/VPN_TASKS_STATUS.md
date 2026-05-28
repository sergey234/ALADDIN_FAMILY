# VPN — реестр задач (vpn-00 … vpn-40) и статус

**Обновлено:** 2026-05-16 (выкат «всё кроме 2-й ноды / legal / Mini App»)  
**Канон:** `VPN_SHOP_INTEGRATION_PLAN.md` §13–§14 · **Handoff:** `VPN_ML_SYSTEM_HANDOFF.md`

## Исключено по решению продукта (не в этом спринте)

| ID | Причина |
|----|---------|
| **vpn-30** | Вторая нода / IP вне РФ — отдельный заказ хостера |
| **vpn-02-legal** | Юрист |
| **vpn-39** | Mini App |

---

## Сводка

| | |
|--|--|
| **Готово (single-node)** | **~95%** техники + UX |
| **Осталось** | vpn-30, legal, Mini App, UFW панель (ручн.), внешний cron smoke, drill с оплатой |

---

## Реестр vpn-xx

| ID | Задача | Статус |
|----|--------|--------|
| vpn-00 | SSOT документация | ✅ |
| vpn-01 | Readiness/liveness | ✅ |
| vpn-02 | Legal черновики + эндпоинты | ✅ |
| vpn-02-legal | Юрист | ⏸ исключено |
| vpn-03 | nginx + UFW VPN | ✅ |
| vpn-03-panel | UFW ispmanager | ⏳ вручную |
| vpn-04 | WG + NAT + hooks + /wg/conf | ✅ |
| vpn-05 | REALITY :8443 + /sub | ✅ |
| vpn-05-443 | Reality :443 | ⏳ опционально |
| vpn-06 | OpenVPN :1194 | ✅ |
| vpn-07–09 | DB, API, план | ✅ |
| vpn-10 | Бот funnel + авто-📥 + 🧪 | ✅ |
| vpn-11 | Оплата → provision | ✅ |
| vpn-12 | /r/{code} | ✅ |
| vpn-13–16 | Secrets, admin, obs, tests | ✅ |
| vpn-17–18 | Deploy, server tree | ✅ |
| vpn-19 | protocols/ extract | ⏳ низкий приор. |
| vpn-20–28 | Config, hub, CB, QR… | ✅ |
| vpn-29 | PUBLIC_SURFACE_REGISTRY | ✅ ведётся |
| vpn-30 | Вторая нода | ⏸ исключено |
| vpn-31 | /admin VPN | ✅ |
| vpn-32 | External smoke script | ✅ cron вне VPS ⏳ |
| vpn-33 | Blocklist playbook | ✅ |
| vpn-34 | Runbook + шаблоны постов | ✅ `VPN34_STATUS_POST_TEMPLATES.md` |
| vpn-34-posts | Регулярные посты | ⏳ процесс |
| vpn-36 | Рефералка | ✅ |
| vpn-37 | Локации UI + API + endpoint_host | ✅ single-node |
| vpn-37-peer | Peer на 2-й ноде | ⏸ с vpn-30 |
| vpn-38 | Хаб инструкций | ✅ |
| vpn-38-content | Контент + CTA, скриншоты-заглушки | ✅ |
| vpn-39 | Mini App | ⏸ исключено |
| vpn-40 | CTA на лендинге | ✅ в vpn-instructions.md |

---

## Выкат 2026-05-16

- Авто-📥, 🧪 Проверить VPN, checkout VPN без @username  
- IPv4-only AllowedIPs в WG  
- `endpoint_host` в каталоге локаций (merge_vpn30_env)  
- Инструкции + шаблоны статус-канала  

**Прод-релиз бота:** см. последний `releases/YYYYMMDD-*` в `/opt/aladdin-telegram-shop-bot`.
