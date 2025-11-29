# 🚀 КРАТКОЕ РУКОВОДСТВО: Как я загрузил файлы на сервер

## 📝 Краткое резюме процесса

### Проблема:
Команды `rsync` и `ssh` запрашивают пароль интерактивно, что блокирует автоматизацию в скриптах.

### Решение:
Использовал **expect** — инструмент для автоматизации интерактивных программ.

---

## 🔧 Что было сделано:

### 1. Проверил наличие expect:
```bash
which expect
# ✅ /usr/bin/expect (уже установлен)
```

### 2. Создал expect-скрипт `deploy_with_password.sh`:
```bash
#!/usr/bin/expect -f
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/.../landing/"
set remote_path "/var/www/aladdin-ai.ru/"

spawn rsync -avz --progress $local_path $server:$remote_path/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof { puts "✅ Загрузка завершена!" }
}
wait
```

### 3. Выполнил скрипт:
```bash
chmod +x deploy_with_password.sh
./deploy_with_password.sh
```

**Результат:** Файлы загружены на сервер автоматически!

### 4. Настроил права доступа:
Создал `fix_permissions.sh` для автоматической настройки прав через SSH.

### 5. Проверил результат:
```bash
curl -s -o /dev/null -w "%{http_code}" https://aladdin-ai.ru/consent.html
# ✅ 200 OK
```

---

## 🎯 Ключевые моменты для ML моделей:

1. **expect** автоматизирует интерактивные диалоги
2. **spawn** запускает команду и перехватывает ввод/вывод
3. **expect** ожидает определенные строки (например, "password:")
4. **send** отправляет ответ автоматически
5. **\r** — это символ Enter (возврат каретки)

---

## 📚 Полное руководство:
См. `docs/SERVER_DEPLOYMENT_DETAILED_GUIDE.md` (666 строк)

---

**Дата:** 19 ноября 2025


