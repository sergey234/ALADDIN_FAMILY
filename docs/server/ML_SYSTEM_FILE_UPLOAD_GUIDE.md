# 📤 Инструкция для ML системы: Загрузка файлов на сервер

## 🎯 Цель
Автоматическая загрузка обновленных файлов на сервер через SSH/SCP с использованием `expect`.

## 🔐 Параметры подключения
- **Сервер**: `root@149.154.65.180`
- **Пароль**: **НЕ ХРАНИТЬ В РЕПОЗИТОРИИ** (использовать SSH-ключи / секреты)
- **Таймаут**: 90 секунд
- **Путь на сервере**: `/var/www/aladdin-ai.ru/`

## 📋 Базовый шаблон команды

### Загрузка одного файла (SCP)
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp /путь/к/локальному/файлу \$server:/путь/на/сервере/файл
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Выполнение команды на сервере (SSH)
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"ВАША_КОМАНДА\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## 📝 Примеры использования

### 1. Загрузка privacy.html
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp landing/privacy.html \$server:/var/www/aladdin-ai.ru/privacy.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 2. Загрузка terms.html
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp landing/terms.html \$server:/var/www/aladdin-ai.ru/terms.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 3. Проверка загрузки (подсчет разделов)
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"echo '=== Privacy ===' && grep -c '<h2' /var/www/aladdin-ai.ru/privacy.html && echo '=== Terms ===' && grep -c '<h2' /var/www/aladdin-ai.ru/terms.html && echo '=== Размеры файлов ===' && ls -lh /var/www/aladdin-ai.ru/privacy.html /var/www/aladdin-ai.ru/terms.html\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 4. Проверка на сайте (через curl)
```bash
curl -H "Cache-Control: no-cache" https://aladdin-ai.ru/privacy.html 2>/dev/null | grep -c "<h2"
curl -H "Cache-Control: no-cache" https://aladdin-ai.ru/terms.html 2>/dev/null | grep -c "<h2"
```

## 🔄 Полный процесс обновления политик

### Шаг 1: Загрузка privacy.html
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp landing/privacy.html \$server:/var/www/aladdin-ai.ru/privacy.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Шаг 2: Загрузка terms.html
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp landing/terms.html \$server:/var/www/aladdin-ai.ru/terms.html
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Шаг 3: Проверка на сервере
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"echo '=== Privacy ===' && grep -c '<h2' /var/www/aladdin-ai.ru/privacy.html && echo '=== Terms ===' && grep -c '<h2' /var/www/aladdin-ai.ru/terms.html\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

**Ожидаемый результат:**
```
=== Privacy ===
16
=== Terms ===
16
```

### Шаг 4: Проверка на сайте
```bash
curl -H "Cache-Control: no-cache" https://aladdin-ai.ru/privacy.html 2>/dev/null | grep -c "<h2"
curl -H "Cache-Control: no-cache" https://aladdin-ai.ru/terms.html 2>/dev/null | grep -c "<h2"
```

**Ожидаемый результат:** оба должны показать `16`

## 📂 Другие полезные команды

### Загрузка любого файла из landing/
```bash
# Замените FILENAME на имя файла
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn scp landing/FILENAME \$server:/var/www/aladdin-ai.ru/FILENAME
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Проверка размера файла на сервере
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"ls -lh /var/www/aladdin-ai.ru/privacy.html\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Создание резервной копии перед обновлением
```bash
expect -c "
set timeout 90
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"cp /var/www/aladdin-ai.ru/privacy.html /var/www/aladdin-ai.ru/privacy.html.backup && cp /var/www/aladdin-ai.ru/terms.html /var/www/aladdin-ai.ru/terms.html.backup && echo 'Backup created'\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## ⚠️ Важные замечания

1. **Таймаут**: Установлен на 90 секунд. Если файлы большие, можно увеличить до 120.

2. **Путь к файлам**: Всегда используйте абсолютные пути или убедитесь, что находитесь в правильной директории перед выполнением команды.

3. **Права доступа**: Файлы на сервере принадлежат `www-data:www-data`. После загрузки права обычно сохраняются.

4. **Проверка**: Всегда проверяйте результат загрузки, особенно количество разделов в HTML файлах.

5. **Кеш**: Используйте `Cache-Control: no-cache` при проверке через curl, чтобы получить актуальную версию.

## 🐛 Решение проблем

### Ошибка "Connection refused" или "Permission denied"
- Проверьте доступность сервера: `ping 149.154.65.180`
- Убедитесь, что настроены SSH-ключи / переменные окружения (пароли не хранить в репозитории)
- Проверьте, что `expect` установлен: `which expect`

### Файл не загружается
- Увеличьте таймаут до 120 секунд
- Проверьте размер файла: `ls -lh landing/privacy.html`
- Убедитесь, что путь на сервере правильный

### Неправильное количество разделов после загрузки
- Проверьте локальный файл: `grep -c "<h2" landing/privacy.html`
- Проверьте файл на сервере: используйте команду проверки из Шага 3
- Очистите кеш браузера или используйте curl с `Cache-Control: no-cache`

## 📚 Связанные документы
- `QUICK_REFERENCE.md` - Быстрая справка по командам
- `ML_SYSTEM_SERVER_ACCESS_GUIDE.md` - Полное руководство по доступу к серверу
- `UPDATE_POLICIES_ON_SERVER.md` - Специфичная инструкция для обновления политик

## ✅ Чеклист успешной загрузки

- [ ] Файл успешно загружен (видно "100%" в выводе scp)
- [ ] Проверка на сервере показывает правильное количество разделов (16)
- [ ] Проверка на сайте показывает правильное количество разделов (16)
- [ ] Размеры файлов на сервере соответствуют локальным
- [ ] Сайт отображает обновленную версию

---
**Последнее обновление**: 24 ноября 2025  
**Автор**: ML System (Auto)


