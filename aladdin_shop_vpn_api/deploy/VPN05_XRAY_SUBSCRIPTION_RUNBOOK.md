# vpn-05: Xray / VLESS+Reality и `GET /sub/<opaque_token>`

## Цель продукта

Клиент (sing-box / v2rayN / и т.д.) получает **подписку по URL** без query string: `GET /sub/<opaque_token>`. Токен проверяется в `vpn.db`; при **`vpn_expired`** — **403**.

## Фаза A (уже в коде)

- Переменная **`VPN_SUBSCRIBE_BODY_FILE`**: путь к UTF-8 файлу; в тексте допускается плейсхолдер **`{opaque_token}`**. Если файл задан и существует, ответ **`200`** `text/plain`. Иначе — **501** и комментарий в теле (генератор подписки не настроен).
- Оператор вручную или скриптом обновляет файл после смены outbound (Reality, SNI, shortId и т.д.). См. `deploy/VPN04_WIREGUARD_RUNBOOK.md` для WG.

## Фаза B: установка Xray (VLESS+Reality)

**Прод (пример):** бинарь в `/opt/xray/`, unit `xray.service`, конфиг `/opt/xray/config.json`, inbound **TCP 8443** (чтобы не пересечься с nginx на **443**), `ufw allow 8443/tcp`. Ключи и UUID — **только на сервере**, не в git.

1. Отдельный порт inbound (например **8443** или **443** на отдельном IP) — не конфликтовать с nginx.  
2. Генерация ключей Reality (`xray x25519`), `serverNames`, `dest`/`xver` по актуальной документации Xray.  
3. **Не логировать** path `/sub/...` с opaque в access-логах (см. `VPN03_INFRA_UFW_TLS_RUNBOOK.md`).

## Обновления

- Runbook релиза: остановка → замена конфига → проверка `xray run -test` → запуск.  
- После смены UUID/Reality параметров — обновить **`VPN_SUBSCRIBE_BODY_FILE`** или включить генератор в коде (отдельный PR).

## Связанные задачи

- **`vpn-23`**: rate limit и маскирование логов на edge.  
- **`vpn-29`**: заполнить публичный URL в **`VPN_PUBLIC_SURFACE_REGISTRY.md`**.
