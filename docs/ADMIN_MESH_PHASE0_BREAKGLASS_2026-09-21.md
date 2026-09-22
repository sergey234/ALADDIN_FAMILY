# Phase 0 — Break-glass (запасной вход)

**Дата:** 2026-09-21  
**Статус:** после keys-only на MAIN + Brain  
**Важно:** ежедневный вход **не менялся** — только ключ с Mac.

---

## Обычный вход (как сейчас)

| Сервер | Команда | Ключ |
|--------|---------|------|
| 🇷🇺 MAIN FirstVDS (`…180`) Аладдин | `ssh aladdin-server` | `~/.ssh/aladdin_server` |
| 🇩🇪 Brain Contabo (`…150`) бот/касса | `ssh aladdin-contabo` | `~/.ssh/aladdin_server` |

Пароль SSH с интернета: **выключен** на обоих.

---

## Если ключ потеряли / Mac недоступен

Не ломиться паролем (его нет). Использовать **консоль хостинга**:

| Узел | Панель | Действие |
|------|--------|----------|
| MAIN | FirstVDS → VNC / веб-консоль VPS | Зайти как root с панели → временно `PasswordAuthentication yes` **или** дописать новый pubkey в `~/.ssh/authorized_keys` → `systemctl reload ssh` |
| Brain | Contabo → VNC / веб-консоль | То же |

Бэкапы sshd на серверах:

- MAIN: `/root/aladdin_phase0_bak/` + `40-hosting.conf.bak-phase0`
- Brain: `/root/aladdin_phase0_bak/`

Файлы keys-only:

- MAIN: `/etc/ssh/sshd_config.d/00-aladdin-keys-only.conf` (+ правки в `40-hosting.conf`)
- Brain: `/etc/ssh/sshd_config.d/00-aladdin-keys-only.conf` (+ `50-cloud-init.conf` = no)

---

## Чего не делать без отдельного GO

- Закрывать порт 22 в UFW / «только Tailscale»
- Трогать VPN/HTTPS/бот порты
- Ставить Tailscale (следующая фаза)

---

## Следующий шаг плана

`GO Tailscale admin` — когда захотите частную сеть Mac↔MAIN↔Brain (старый SSH по IP оставим).
