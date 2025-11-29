# SUCCESS PAGE DEPLOY GUIDE

Алгоритм для ML‑системы, чтобы обновлять `success.html` на сервере `aladdin-ai.ru`.

## 1. Подготовка локального файла
- Рабочий репозиторий: `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`.
- Целевой файл: `landing/success.html`.
- Убедиться, что:
  - Остались только состояния `loadingState`, `codeState`, `pendingState`, `manualTransferState`, `errorState`.
  - Полностью удалены форма `Payment ID / Alias / PIN`, состояние `retrieveState`, логика `retrieveCode`.
  - Все ошибки показываются через `showError(...)`.
  - Для `manual_transfer` страница остаётся с картой при любых ошибках.

## 2. Проверка инструмента expect (локально)
```bash
which expect   # должно вывести /usr/bin/expect; если нет — установить
```

## 3. Загрузка файла на боевой сервер
Скопировать файл на промежуточную директорию `/opt/aladdin-backend` на сервере `root@149.154.65.180`:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 120
set password \"Sergio675\"
puts \"📤 Копируем обновленный success.html на backend-сервер...\"
spawn scp landing/success.html root@149.154.65.180:/opt/aladdin-backend/success.html
expect \"password:\" { send \"\$password\r\" }
expect eof
"
```

## 4. Обновление боевых копий
На сервере используются две реальные копии файла:
- `/var/www/html/success.html`
- `/var/www/aladdin-ai.ru/success.html`

Обе нужно перезаписать:
```bash
expect -c "
set timeout 120
set password \"Sergio675\"
puts \"📤 Обновляем success.html в /var/www/html...\"
spawn ssh root@149.154.65.180 \"cp /opt/aladdin-backend/success.html /var/www/html/success.html && md5sum /var/www/html/success.html\"
expect \"password:\" { send \"\$password\r\" }
expect eof
"

expect -c "
set timeout 120
set password \"Sergio675\"
puts \"📤 Обновляем success.html в /var/www/aladdin-ai.ru...\"
spawn ssh root@149.154.65.180 \"cp /opt/aladdin-backend/success.html /var/www/aladdin-ai.ru/success.html && md5sum /var/www/aladdin-ai.ru/success.html\"
expect \"password:\" { send \"\$password\r\" }
expect eof
"
```
MD5 обеих файлов должен совпадать с локальным (`md5sum landing/success.html`).

## 5. Очистка кэшей
- Если используется CDN (Cloudflare): выполнить purge пути `/success.html`.
- На локальной машине/браузере — жёсткое обновление страницы (`Cmd/Ctrl + Shift + R`).

## 6. Проверка результата
1. Убедиться, что сервер отдаёт новую версию без формы:
   ```bash
   curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" https://aladdin-ai.ru/success.html | grep -n \"Получить код\"
   ```
   Результат должен быть пустым.
2. Проверить manual_transfer сценарий:
   ```bash
   curl -s -H "Cache-Control: no-cache" \"https://aladdin-ai.ru/success.html?paymentId=TEST&method=manual_transfer&amount=490\" | grep -n \"Получить код\"
   ```
   Тоже пусто.
3. Убедиться, что в DOM нет блока формы (можно открыть страницу в браузере с отключённым кэшем).

## 7. Диагностика, если снова появляется старая версия
- Найти все копии файла: `ssh root@149.154.65.180 "find /var/www -name 'success.html' -print"`.
- Удостовериться, что нет других папок с устаревшим HTML. При необходимости обновить каждую:
  ```bash
  cp /opt/aladdin-backend/success.html /path/to/old/success.html
  ```
- Сравнить MD5: `md5sum /path/to/success.html`.
- Снова выполнить purge/жёсткое обновление.

## 8. Проверка логики
- В логах браузера/панели отладки не должно быть запросов к `/api/payments/status/undefined`.
- При `method=manual_transfer` страница не должна переключаться со страницы с картой.
- При ошибках (404, network) должен запускаться `showError(...)`, а polling останавливаться.

## 9. Полезные команды
```bash
# Проверить наличие expect
which expect

# Скопировать файл на сервер
scp landing/success.html root@149.154.65.180:/opt/aladdin-backend/success.html

# Копировать в каталог статики
ssh root@149.154.65.180 "cp /opt/aladdin-backend/success.html /var/www/html/success.html"

# Проверить текст в отдаваемой странице
curl -s -H "Cache-Control: no-cache" https://aladdin-ai.ru/success.html | grep -n \"Получить код\"
```

Следуя этим шагам, ML‑система сможет гарантированно обновить страницу и убедиться, что пользователи видят актуальную версию.

## 10. Post-payment checklist (что сделать до реальных оплат)

| Шаг | Действия |
| --- | --- |
| Автоподтверждение | Подключить вебхук `POST /api/payments/confirm` или админ-инструмент, который переводит платеж в `paid` и создаёт `ActivationCode`. Проверить цепочку PSP → вебхук → `/api/payments/status` → success.html → мобильное приложение. |
| Скрипт `manual_mark_paid.py` | Лежит в `/opt/aladdin-backend/manual_mark_paid.py`. Использовать только для тестов (`./venv/bin/python3 manual_mark_paid.py <payment_id>`). Решить, оставляем ли в проде; при необходимости ограничить доступ. |
| Очистка localStorage | После `showCode()` удалить `payment_id`, `payment_alias`, `payment_pin`, чтобы следующая оплата не подхватывала старые данные. |
| API Key | `/api/payments/status` теперь публичный (убран `verify_api_key`). Убедиться, что nginx не вырезает заголовки и endpoint доступен для success.html без ключа. |
| Мобильное приложение | Протестировать сценарии: свежий код → “Активация успешна”; повторный ввод → “already_redeemed”; UI скрывает кнопку “Ввести код”. Зафиксировать результат (скрин уже есть). |
| Реферальная логика | Если используется `referralCode`, убедиться, что поле сохраняется в `payments` и бонусы начисляются при подтверждении (см. `app/referral_*.py`). |
| Мониторинг | Настроить логи/уведомления (`journalctl -u payment_service | grep "/api/payments/status"`), добавить алерты при всплеске 404/500, при необходимости подключить Prometheus/ELK. |
| Бэкапы | Регулярно создавать архив `/root/aladdin_backup_YYYYMMDD.tgz` (success.html, backend, БД) и хранить копии локально/в облаке. |
| Коммиты/доки | Все изменения фиксировать в Git; `SUCCESS_PAGE_DEPLOY_GUIDE.md` поддерживать актуальным. |

## 11. Быстрые команды

```bash
# Проверить статус платежа
curl -s -H "X-API-Key: PUBLIC_CLIENT_KEY" https://aladdin-ai.ru/api/payments/status/<PAYMENT_ID> | python3 -m json.tool

# Перезапустить backend
ssh root@149.154.65.180 "systemctl restart payment_service && systemctl status payment_service --no-pager | head -n 20"

# Создать тестовый код
ssh root@149.154.65.180 "cd /opt/aladdin-backend && ./venv/bin/python3 manual_mark_paid.py <payment_id>"
```
