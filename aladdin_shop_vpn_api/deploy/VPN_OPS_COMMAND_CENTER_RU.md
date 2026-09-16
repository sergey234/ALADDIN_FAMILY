# AiMonkey OPS Command Center ×3 (ADMIN_IDS)

**Статус:** ✅ live на 🇩🇪 Brain — Contabo / мозг (`…150`) · timer `aladdin-vpn-ops-command-center.timer`  
**Канон скрипта:** `/opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.py`  
**Репо (Mac):** `aladdin_shop_vpn_api/deploy/scripts/vpn_ops_command_center.py`

## Слоты (МСК) → всем ADMIN_IDS

| Слот | МСК | systemd (CEST на Brain) |
|------|-----|-------------------------|
| утро | 09:00 | ~08:00 CEST |
| обед | 14:00 | ~13:00 CEST |
| вечер | 21:00 | ~20:00 CEST |

Срочные 🔴 — сразу, тем же fan-out.

## Что в отчёте (канон 2026-09-17)

- Заголовок: **`🛡 AiMonkey OPS`** (не ALADDIN)
- **🚪 Двери:** Brain, Mouth (рот Contabo `…12`), NEW×3, MAIN, REG×2, Яндекс — медиана 3 TCP-проб
- **🔗 WG:** NEW, MAIN, REG, SG (двор), Яндекс — «связь N назад»
- **🛡 Guard:** только **платные + триал** (без ссылок друзьям `9901*`, без tid≤0)
- **⚡ Скорость** + **🧩 Сервисы** (bot/vpn-api/partner на Brain + MAIN API) + **📌 Внимание**

### Флот 7

| # | Сервер | Провайдер | Роль |
|---|--------|-----------|------|
| 1 | Brain `…150` | Contabo | мозг (бот) |
| 2 | Mouth `…12` | Contabo | рот (Telegram) |
| 3 | SG `…78` | Contabo | двор Asia |
| 4 | NEW `…98` | FirstVDS | мост |
| 5 | MAIN `…180` | FirstVDS | Аладдин |
| 6 | REG `…63` | REG.RU | запас |
| 7 | Яндекс NLB `…20` | Яндекс.Облако | Обход-ночь |

## Как не потерять

1. **Brain:** скрипт на месте + `.bak.*` рядом; timer `active`
2. **Git:** коммит файлов ниже в `ALADDIN_iOS`
3. **Смоук:**  
   `python3 …/vpn_ops_command_center.py --slot evening --print-only`  
   тест в бот: digest с ключом `ops-cc-test-…` (не трогает dedupe утро/обед/вечер)

## Файлы

- `deploy/scripts/vpn_ops_command_center.py`
- `deploy/scripts/vpn_ops_command_center.sh`
- `deploy/scripts/vpn_ops_notify.sh`
- `deploy/systemd/aladdin-vpn-ops-command-center.{service,timer}`
- `tests/test_vpn_ops_command_center.py`
- `.cursor/rules/vpn-server-naming-speak.mdc`

## Ручной тест в бот

```bash
# на Brain — уникальный ключ, чтобы не съел dedupe слота
source /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_notify.sh
vpn_ops_load_env
REPORT="$(python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.py --slot evening --print-only)"
vpn_ops_digest "ops-cc-test-$(TZ=Europe/Moscow date +%Y%m%d-%H%M%S)" "$REPORT"
```

## Rollback

```bash
# вернуть .bak на Brain
cp -a /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.py.bak.YYYYMMDD-HHMMSS \
      /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.py
```

## Пороги v1

- Дверь: TCP fail → 🔴; RTT ≥ 200ms → 🟡 (по медиане 3 проб)
- WG: >10м → 🔴; >3м → 🟡
- Guard: errors/stale → 🔴; desired≠active → 🟡
- Скорость: tunnel rc≠0 → 🔴; NEW ≪ Brain → 🟡
