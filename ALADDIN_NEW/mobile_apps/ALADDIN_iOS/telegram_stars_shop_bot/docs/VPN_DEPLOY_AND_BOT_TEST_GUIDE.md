# Deploy + тест в боте (пошагово)

**Когда:** после legal 1.1 в репо, перед Integration Week на телефоне.  
**Бот:** @AiMonkeyStars_bot · **Команда:** `/vpn`

---

## Часть A — Deploy (ops)

### A1. VPN API + legal (Contabo)

```bash
ssh aladdin-contabo
cd /opt/aladdin-shop-vpn-api
git pull   # или rsync legal_docs + deploy
sudo systemctl restart aladdin-shop-vpn-api
curl -fsS https://aladdin-ai.ru/v1/legal/vpn-terms | grep "28 июня 2026"
curl -fsS https://aladdin-ai.ru/v1/legal/vpn-data | grep -i Cloudflare
python3 deploy/scripts/vpn_prod_smoke.py
bash deploy/scripts/vpn_dns_verify.sh
```

### A2. Telegram-бот (MAIN)

```bash
ssh aladdin-server
cd /opt/aladdin-stars-shop-bot   # путь по факту
git pull
# deploy по вашему runbook (systemd / docker)
bash /opt/aladdin-shop-vpn-api/deploy/scripts/main_bot_post_deploy_guard.sh
```

### A3. Smoke с Mac

```bash
bash aladdin_shop_vpn_api/deploy/scripts/vpn_external_smoke_cron.sh
python3 aladdin_shop_vpn_api/deploy/scripts/vpn_pre_ga_audit.py   # на Contabo
```

---

## Часть B — Тест в боте (клик за кликом)

Используйте **тестовый аккаунт** с активной VPN-подпиской и **второй** без подписки.

### B1. Вход и меню

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 1 | Открыть [@AiMonkeyStars_bot](https://t.me/AiMonkeyStars_bot) | Бот отвечает |
| 2 | `/start` или `/menu` | Главное меню (если канал — подписаться) |
| 3 | Нажать **🌐 AiMonkeyVPN** (или `/vpn`) | Экран VPN: тарифы, тексты |

### B2. Legal gate (новый пользователь / сброс галочек)

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 4 | На экране VPN — блок **«📋 Документы перед оплатой»** | Ссылки на политику и соглашение |
| 5 | Нажать ссылку **Политика конфиденциальности** | Открывается `…/v1/legal/vpn-data`, есть Cloudflare / RU relay |
| 6 | Назад в бот → ссылка **Пользовательское соглашение** | `…/v1/legal/vpn-terms`, §2.5 маршрутизация |
| 7 | Нажать **☐ Политика** (галочка) | Статус: политика ✅ |
| 8 | Нажать **☐ Соглашение** (галочка) | Обе ✅, «Можно выбрать тариф» |
| 9 | Ссылка **AUP** внизу | `…/v1/legal/vpn-aup` |

### B3. Тарифы и кнопки (активная подписка)

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 10 | Прокрутить тарифы | Кнопки `🌐 30 дней — … ₽` и т.д. |
| 11 | Под тарифами — **отдельные строки** (не обрезаны): | |
| | **📋 VPN-подписка** | Копирует `https://…/sub/…` |
| | **👥 Пригласить друга** | Копирует `https://t.me/…?start=ref_…` |
| | **📷 QR + v2RayTun** | Приходит QR в чат |
| 12 | Нажать **📋 VPN-подписка** → вставить в заметки | URL `/sub/` валидный |
| 13 | **👥 Пригласить друга** — вставить в заметки | `ref_`, **не** `/sub/` |

### B4. Подключение (инструкции в боте)

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 14 | **📱 iPhone (HitWave)** или **🤖 Android (v2rayNG)** | Пошаговый гайд |
| 15 | **🔀 Запасные способы** | OpenVPN / WireGuard — «только Wi‑Fi» |
| 16 | **🧪 Проверить VPN** | Подсказка / smoke (если есть доступ) |

### B5. После оплаты (если тестируете покупку)

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 17 | Выбрать тариф → оплата | Заказ создаётся |
| 18 | Подождать 2–5 мин | Сообщение: ссылка + QR + 3 шага |
| 19 | Кнопки **📋 VPN-подписка** под сообщением | Те же короткие подписи |

### B6. Пульт активной подписки

| Шаг | Действие | Ожидание |
|-----|----------|----------|
| 20 | **🌐 AiMonkeyVPN** при `vpn_active` | «✅ Подписка активна», дата до |
| 21 | **📋 VPN-подписка** снова | Работает |
| 22 | **Продлить** / тариф | Checkout без ошибок |

---

## Часть C — Тест на телефоне (4G, в конце)

**Wi‑Fi выкл.** HitWave → **Обновить подписку** (Auto Update).

| # | Профиль в HitWave | Сеть | PASS если |
|---|-----------------|------|-----------|
| 1 | **Мобильный мост** | 4G | интернет 5+ мин, fast.com ≥1 Mbit/s |
| 2 | **Мобильный интернет** | 4G | то же |
| 3 | **Мобильный CDN** | 4G | то же (`cdn` DNS → 149.154.65.180) |
| 4 | **Домашний Wi‑Fi** | Wi‑Fi | то же |
| 5 | OpenVPN (запасной) | Wi‑Fi only | подключается |

По каждому оператору (MF, MTS, Beeline, Tele2) — заполнить `operator_block_matrix` в journal.

---

## Часть D — Автопроверки (после deploy)

```bash
# Contabo
python3 deploy/scripts/vpn_prod_smoke.py
python3 deploy/scripts/vpn_bridge_hop_smoke.py
python3 deploy/scripts/vpn_cdn_health.py
bash deploy/scripts/vpn_g4_gate.sh
```

Ожидание: infra **PASS**, journal **PENDING** (пока нет телефона).

---

## Чеклист «всё готово»

- [ ] Legal URLs 28.06.2026 на prod
- [ ] Бот: кнопки не обрезаны
- [ ] `dig cdn.aladdin-ai.ru` → 149.154.65.180
- [ ] smoke 10/10
- [ ] Юрист sign-off (vpn-54, vpn-77)
- [ ] 4G ×4 в journal (последний шаг)
