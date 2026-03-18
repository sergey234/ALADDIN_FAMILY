# ⚡ БЫСТРАЯ ПАМЯТКА: Подключение к серверу

## 🔐 Параметры
- **Сервер**: `root@149.154.65.180`
- **Пароль**: **НЕ ХРАНИТЬ В РЕПОЗИТОРИИ** (использовать SSH-ключи / секреты)

## 📝 Базовая команда

```bash
expect -c "
set timeout 60
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"ВАША_КОМАНДА\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## 📤 Копирование файла

```bash
expect -c "
set timeout 60
set password \"$env(ALADDIN_SSH_PASSWORD)\"
spawn scp /local/file.txt root@149.154.65.180:/remote/file.txt
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## 🗄️ Работа с PostgreSQL

```bash
expect -c "
set timeout 60
# SECURITY: не хранить пароли БД в репозитории. Используйте секреты/ENV.
set db_password \"$env(ALADDIN_DB_PASSWORD)\"
spawn ssh root@149.154.65.180 \"PGPASSWORD='\$db_password' psql -h localhost -U aladdin_user -d aladdin_db -c 'ВАША_SQL_КОМАНДА'\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

## 📄 Шаблон скрипта

```bash
#!/usr/bin/expect -f
set timeout 60
set password "$env(ALADDIN_SSH_PASSWORD)"
set server "root@149.154.65.180"

spawn ssh $server "команда"
expect "password:" { send "$password\r" }
expect eof
```

## ✅ Чеклист
- [ ] `expect` установлен: `which expect`
- [ ] Сервер доступен: `ping 149.154.65.180`
- [ ] Timeout установлен (60-120 сек)
- [ ] Скрипт исполняемый: `chmod +x script.sh`

---
📖 **Полная инструкция**: `ML_SYSTEM_SERVER_ACCESS_GUIDE.md`


