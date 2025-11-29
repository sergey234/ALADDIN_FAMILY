# Инструкция по обновлению политик на сервере

## Цель
Загрузить обновленные версии `privacy.html` и `terms.html` (16 разделов вместо 7) на сервер.

## Файлы для загрузки
- `landing/privacy.html` → `/var/www/aladdin-ai.ru/privacy.html`
- `landing/terms.html` → `/var/www/aladdin-ai.ru/terms.html`

## Команды для выполнения в сетевом терминале

### 1. Загрузка privacy.html
```bash
expect -c "
set timeout 90
set password \"Sergio675\"
set server \"root@149.154.65.180\"
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/privacy.html \$server:/var/www/aladdin-ai.ru/privacy.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 2. Загрузка terms.html
```bash
expect -c "
set timeout 90
set password \"Sergio675\"
set server \"root@149.154.65.180\"
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/terms.html \$server:/var/www/aladdin-ai.ru/terms.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 3. Проверка загрузки
```bash
expect -c "
set timeout 90
set password \"Sergio675\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"ls -lh /var/www/aladdin-ai.ru/privacy.html /var/www/aladdin-ai.ru/terms.html && echo '---' && grep -c '<h2' /var/www/aladdin-ai.ru/privacy.html && grep -c '<h2' /var/www/aladdin-ai.ru/terms.html\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 4. Очистка кеша (если используется)
```bash
expect -c "
set timeout 90
set password \"Sergio675\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"curl -H 'Cache-Control: no-cache' https://aladdin-ai.ru/privacy.html | grep -c '<h2' && curl -H 'Cache-Control: no-cache' https://aladdin-ai.ru/terms.html | grep -c '<h2'\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## Ожидаемый результат
- `privacy.html`: должно быть 16 разделов (grep покажет 16)
- `terms.html`: должно быть 16 разделов (grep покажет 16)

## Примечание
Выполняйте команды в терминале с сетевым доступом (не в репозитории).


