# vpn-13: секреты, узкий sudo, бэкапы (`aladdin-shop-vpn-api`)

Цель: **не** давать процессам Python широкий `sudo`, не хранить секреты в git, иметь **повторяемую** ротацию HMAC и **оффлайн-копии** `vpn.db` + каталога ключей клиентов.

Связано: **`VPN04_WIREGUARD_RUNBOOK.md`**, **`VPN_SHOP_INTEGRATION_PLAN.md`** §13, контракт **`VPN_SHOP_API.md`**.

---

## 1. Инвентарь секретов и чувствительных файлов

| Объект | Где | Назначение | Риск при утечке |
|--------|-----|------------|-----------------|
| `VPN_API_HMAC_SECRET` | `/opt/aladdin-shop-vpn-api/env`, зеркально **`VPN_API_HMAC_SECRET`** в `shared/.env` бота / partner API | HMAC внутренних `POST /internal/v1/*` | полный контроль над выдачей/отзывом VPN для магазина |
| `vpn.db` | `VPN_DB_PATH` (часто `/opt/aladdin-shop-vpn-api/var/vpn.db`) | аккаунты, `opaque_token`, WG-поля, jobs | deanonymization + токены подписки |
| `WG_KEYS_DIR/*.key` | по умолчанию `var/wg-keys` | приватные ключи клиентов WG | impersonation клиента |
| `/etc/wireguard/server_private.key` | вне дерева приложения | ключ сервера WG | новые «легитимные» сессии от имени сервера |
| Xray REALITY / подписка | см. **`VPN05_XRAY_SUBSCRIPTION_RUNBOOK.md`** | обход блокировок | отдельная поверхность атаки |
| OpenVPN PKI | см. **`VPN06_OPENVPN_FALLBACK_RUNBOOK.md`** | fallback | CA / tls-crypt |

**Правило:** в git только **`env.example`** без значений; на сервере **`chmod 640`** на `env`, владелец root или пользователь сервиса, группа `aladdin-shop-vpn` (см. ниже).

---

## 2. Пользователь сервиса (рекомендуется на проде)

Системный пользователь без shell (имя согласовано с префиксом `aladdin-shop-vpn-*`):

```bash
sudo useradd --system --shell /usr/sbin/nologin --home /nonexistent \
  --user-group aladdin-shop-vpn
```

Владение данными приложения (пути из вашего деплоя):

```bash
sudo chown -R aladdin-shop-vpn:aladdin-shop-vpn /opt/aladdin-shop-vpn-api/var
sudo chmod 750 /opt/aladdin-shop-vpn-api/var
sudo chmod 700 /opt/aladdin-shop-vpn-api/var/wg-keys 2>/dev/null || true
sudo install -d -m 750 -o aladdin-shop-vpn -g aladdin-shop-vpn /var/log/aladdin-shop-vpn-api
```

`venv` и код деплоя (`current`) — **root:root**, `755`; Python не должен перезаписывать артефакты релиза.

**`env`:** один из вариантов:

- `root:aladdin-shop-vpn`, `chmod 640` — сервис читает через группу; или  
- `aladdin-shop-vpn:aladdin-shop-vpn`, `chmod 600` — только unit этого пользователя.

Скрипты в `/opt/aladdin-shop-vpn-api/scripts/`: **`chown root:root`**, **`chmod 755`**, содержимое **только** из репозитория / CI, чтобы пользователь сервиса не мог подменить `wg-peer-up.sh` после получения узкого sudo.

---

## 3. Узкий sudo (только `wg set` / sqlite через фиксированные скрипты)

Python-воркер **не** вызывает `wg` напрямую; он вызывает **один** путь из `VPN_WG_POST_PROVISION_SCRIPT` / `VPN_WG_POST_EXPIRE_SCRIPT`.

### 3.1. Режим A — unit под `root` (MVP)

- В `env`: прямые пути на `wg-peer-up.sh` / `wg-peer-down.sh` (как в **`VPN04`**).
- `sudoers` **не** нужен для WG-хуков.
- Минус: компрометация API = root на хосте.

### 3.2. Режим B — `User=aladdin-shop-vpn` + обёртки `sudo -n` (рекомендуется)

1. Установите фрагмент sudoers (пример в репо: **`deploy/sudoers/aladdin-shop-vpn-api.sudoers.example`**):

   ```bash
   sudo install -m 0440 -o root -g root \
     /opt/aladdin-shop-vpn-api/current/deploy/sudoers/aladdin-shop-vpn-api.sudoers.example \
     /etc/sudoers.d/aladdin-shop-vpn-api
   sudo visudo -cf /etc/sudoers.d/aladdin-shop-vpn-api
   ```

2. В **`/opt/aladdin-shop-vpn-api/env`** укажите:

   ```bash
   VPN_SERVICE_USER=aladdin-shop-vpn
   VPN_WG_POST_PROVISION_SCRIPT=/opt/aladdin-shop-vpn-api/scripts/wg-peer-up-sudo.sh
   VPN_WG_POST_EXPIRE_SCRIPT=/opt/aladdin-shop-vpn-api/scripts/wg-peer-down-sudo.sh
   ```

   Внутренние скрипты `wg-peer-up.sh` / `wg-peer-down.sh` вызываются **только** через `sudo` и перечислены в sudoers **с полным путём**.

3. Проверка от пользователя сервиса:

   ```bash
   sudo -u aladdin-shop-vpn /opt/aladdin-shop-vpn-api/scripts/wg-peer-up-sudo.sh 123456789
   ```

Ожидание: без запроса пароля (`sudo -n`), только если `123456789` — тестовый существующий `telegram_user_id` в `vpn.db`; иначе скрипт завершится с ошибкой — это нормально для проверки sudo.

**Запрещено:** `NOPASSWD: ALL`, `sudo` на `/usr/bin/bash`, на каталог скриптов с маской, на `tee`, на `python` без аргументов.

---

## 4. Ротация `VPN_API_HMAC_SECRET`

Секрет должен быть **одинаковым** в:

- `/opt/aladdin-shop-vpn-api/env` (`VPN_API_HMAC_SECRET` = имя как в **`aladdin_shop_vpn_api/settings.py`**),
- `shared/.env` магазина / partner API (**`VPN_API_HMAC_SECRET`**, см. `telegram_stars_shop_bot/bot/config.py`).

**Порядок (короткое окно недоступности внутренних вызовов допустимо):**

1. Сгенерировать новый секрет (≥ 32 случайных байта в hex/base64):  
   `openssl rand -hex 32`
2. Остановить воркер и API (или наоборот: сначала бот — зависит от допустимого простоя оплат):
   - `systemctl stop aladdin-shop-vpn-worker.timer` (и при необходимости сервис воркера)
   - `systemctl stop aladdin-shop-vpn-api`
   - `systemctl stop aladdin-telegram-bot` (или ваш unit бота)
3. Атомарно обновить оба `env` (или один общий файл, если вынесли в общий include — тогда один источник правды).
4. Запустить в обратном порядке; проверить один `POST /internal/v1/...` из стенда или `curl` с подписью по **`VPN_SHOP_API.md`**.
5. Старый секрет **не** оставлять в бэкапах на общих носителях без шифрования (см. §5).

---

## 5. Бэкапы

Скрипт **`deploy/scripts/vpn-db-backup.sh`** — логический бэкап SQLite через `sqlite3 .backup` (консистентная копия без остановки API, при активной записи предпочтительнее короткое окно `systemctl stop` для полного снапшота файла).

Пример ежедневного таймера (от root):

```bash
# /etc/systemd/system/aladdin-shop-vpn-backup.service
[Service]
Type=oneshot
ExecStart=/opt/aladdin-shop-vpn-api/scripts/vpn-db-backup.sh /var/backups/aladdin-shop-vpn
```

Каталог бэкапов: `chmod 700`, владелец root или отдельный `backup` без доступа к ssh.

**Что класть в бэкап:**

| Данные | Частота | Примечание |
|--------|---------|------------|
| `vpn.db` | ежедневно + перед миграциями | обязательно |
| `var/wg-keys/` | при изменении или ежедневно | **секрет**; шифровать off-site |
| `env` | **не** копировать в открытый S3 | только менеджер секретов / зашифрованный архив |

Восстановление: остановить API/воркер → заменить `vpn.db` → проверить права `aladdin-shop-vpn` → старт; затем при необходимости `wg-resync-active-peers.sh` от root после `wg-quick@wg0`.

---

## 6. Чеклист после инцидента (компрометация хоста / утечка env)

1. Считать скомпрометированными: `VPN_API_HMAC_SECRET`, все `*.key` в `WG_KEYS_DIR`, при необходимости server WG private + Xray keys.  
2. Ротация по §4; перевыпуск серверных ключей по **`VPN04`** / **`VPN05`**.  
3. `revoke` / массовый отзыв peer через админ-процедуры (см. будущий **`vpn-14`**).  
4. Пересоздать `opaque_token` в БД — только если модель угроз требует (обычно достаточно HMAC + отзыв peer).

---

## 7. Связка с systemd

Примеры unit: **`deploy/aladdin-shop-vpn-api.service.example`**, **`deploy/aladdin-shop-vpn-worker.service.example`**.  
Для режима B задайте `User=` / `Group=` и пути на **`*-sudo.sh`** в `env`.

---

## 8. Ссылки на артефакты в репозитории

| Файл | Назначение |
|------|------------|
| `deploy/sudoers/aladdin-shop-vpn-api.sudoers.example` | шаблон для `/etc/sudoers.d/` |
| `deploy/scripts/wg-peer-up-sudo.sh` | `sudo -n` → `wg-peer-up.sh` |
| `deploy/scripts/wg-peer-down-sudo.sh` | `sudo -n` → `wg-peer-down.sh` |
| `deploy/aladdin-shop-vpn-backup.service.example` + `.timer.example` | ежедневный вызов `vpn-db-backup.sh` |

После правок sudoers **всегда** `visudo -cf`.
