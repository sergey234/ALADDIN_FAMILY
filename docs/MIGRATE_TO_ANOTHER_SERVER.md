# 🚀 ИНСТРУКЦИЯ: ПЕРЕНОС НА ДРУГОЙ СЕРВЕР

**Дата:** 2025-11-26  
**Текущий сервер:** root@149.154.65.180  
**Локальная машина:** Mac (файлы остались на месте)

---

## ✅ ПОДТВЕРЖДЕНИЕ: ЛОКАЛЬНЫЕ ФАЙЛЫ НА МЕСТЕ

**Мы использовали `rsync` и `scp` - это КОПИРОВАНИЕ, не перемещение!**

- ✅ Все файлы остались на вашем Mac
- ✅ Файлы были **скопированы** на сервер, не удалены
- ✅ Локальная структура не изменилась

**Проверка:**
```bash
# На вашем Mac:
ls -la security/safe_function_manager.py  # ✅ Существует
find security/ai_agents -name "*.py" | wc -l  # ✅ 76 файлов
```

---

## 🔄 ПЕРЕНОС НА ДРУГОЙ СЕРВЕР

### Вариант 1: С локального Mac на новый сервер

Если у вас есть доступ к локальным файлам на Mac, используйте тот же процесс:

#### Шаг 1: Подготовка нового сервера

```bash
# Подключитесь к новому серверу
ssh root@NEW_SERVER_IP

# Создайте структуру каталогов
mkdir -p /opt/aladdin-backend/security/{ai_agents,bots,managers,microservices,active,family,vpn,antivirus,compliance,core}
mkdir -p /opt/aladdin-backend/data/sfm
mkdir -p /opt/aladdin-backend/scripts
mkdir -p /opt/aladdin-backend/venvs

# Создайте виртуальное окружение
python3 -m venv /opt/aladdin-backend/venvs/main_env
source /opt/aladdin-backend/venvs/main_env/bin/activate
pip install --upgrade pip
```

#### Шаг 2: Перенос файлов с Mac

**На вашем Mac выполните:**

```bash
cd /Users/sergejhlystov/ALADDIN_NEW

# 1. SFM + Валидатор
scp security/safe_function_manager.py root@NEW_SERVER_IP:/opt/aladdin-backend/security/
scp scripts/sfm_structure_validator.py root@NEW_SERVER_IP:/opt/aladdin-backend/scripts/

# 2. AI Agents (76 файлов)
rsync -avz security/ai_agents/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/ai_agents/

# 3. Bots (30 файлов)
rsync -avz security/bots/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/bots/

# 4. Managers (24 файла)
rsync -avz security/managers/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/managers/

# 5. Microservices (17 файлов)
rsync -avz security/microservices/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/microservices/

# 6. Active (7 файлов)
rsync -avz security/active/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/active/

# 7. Family (18 файлов)
rsync -avz --exclude="test_*.py" --exclude="*test*.py" --exclude="fix_*.py" --exclude="check_*.py" security/family/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/family/

# 8. VPN (105 файлов)
rsync -avz security/vpn/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/vpn/

# 9. Antivirus (7 файлов)
rsync -avz security/antivirus/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/antivirus/

# 10. Compliance (3 файла)
rsync -avz security/compliance/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/compliance/

# 11. Core (1 файл)
rsync -avz security/core/ root@NEW_SERVER_IP:/opt/aladdin-backend/security/core/

# 12. Критичные security модули (72 файла)
find security -maxdepth 1 -name "*.py" -type f ! -name "test_*.py" ! -name "*test*.py" ! -name "*backup*.py" ! -name "*fixed*.py" ! -name "*patch*.py" ! -name "*old*.py" | while read f; do
    scp "$f" root@NEW_SERVER_IP:/opt/aladdin-backend/security/
done

# 13. function_registry.json
scp data/sfm/function_registry.json root@NEW_SERVER_IP:/opt/aladdin-backend/data/sfm/

# 14. requirements.txt
scp requirements.txt root@NEW_SERVER_IP:/opt/aladdin-backend/
```

#### Шаг 3: Установка зависимостей на новом сервере

```bash
# На новом сервере
ssh root@NEW_SERVER_IP
cd /opt/aladdin-backend
source venvs/main_env/bin/activate
pip install -r requirements.txt
```

#### Шаг 4: Проверка компиляции

```bash
# На новом сервере
source /opt/aladdin-backend/venvs/main_env/bin/activate
python3 -m compileall /opt/aladdin-backend/security
```

---

### Вариант 2: С текущего сервера на новый сервер

Если хотите скопировать с текущего сервера (149.154.65.180) на новый:

#### Шаг 1: Прямое копирование между серверами

```bash
# На вашем Mac (как мост)
# Или на текущем сервере, если есть доступ между серверами

# С текущего сервера на новый
rsync -avz -e ssh root@149.154.65.180:/opt/aladdin-backend/ root@NEW_SERVER_IP:/opt/aladdin-backend/
```

#### Шаг 2: Создание архива и перенос

```bash
# На текущем сервере (149.154.65.180)
ssh root@149.154.65.180
cd /opt/aladdin-backend
tar -czf /tmp/aladdin-backend-backup.tar.gz security/ data/ scripts/ requirements.txt

# Скачать архив на Mac
scp root@149.154.65.180:/tmp/aladdin-backend-backup.tar.gz ~/Downloads/

# Загрузить на новый сервер
scp ~/Downloads/aladdin-backend-backup.tar.gz root@NEW_SERVER_IP:/tmp/

# На новом сервере распаковать
ssh root@NEW_SERVER_IP
cd /opt
tar -xzf /tmp/aladdin-backend-backup.tar.gz
```

---

## 📋 АВТОМАТИЗИРОВАННЫЙ СКРИПТ ДЛЯ ПЕРЕНОСА

Создайте скрипт `migrate_to_new_server.sh`:

```bash
#!/bin/bash
# migrate_to_new_server.sh
# Использование: ./migrate_to_new_server.sh NEW_SERVER_IP

NEW_SERVER=$1
if [ -z "$NEW_SERVER" ]; then
    echo "Использование: $0 NEW_SERVER_IP"
    exit 1
fi

echo "🚀 Начинаем перенос на сервер: $NEW_SERVER"
echo "📁 Локальный путь: /Users/sergejhlystov/ALADDIN_NEW"
echo ""

cd /Users/sergejhlystov/ALADDIN_NEW

# Создание структуры на новом сервере
echo "📂 Создание структуры каталогов..."
ssh root@$NEW_SERVER "mkdir -p /opt/aladdin-backend/security/{ai_agents,bots,managers,microservices,active,family,vpn,antivirus,compliance,core} && mkdir -p /opt/aladdin-backend/data/sfm && mkdir -p /opt/aladdin-backend/scripts"

# Перенос файлов
echo "📦 Перенос SFM..."
scp security/safe_function_manager.py root@$NEW_SERVER:/opt/aladdin-backend/security/

echo "📦 Перенос AI Agents (76 файлов)..."
rsync -avz security/ai_agents/ root@$NEW_SERVER:/opt/aladdin-backend/security/ai_agents/

echo "📦 Перенос Bots (30 файлов)..."
rsync -avz security/bots/ root@$NEW_SERVER:/opt/aladdin-backend/security/bots/

echo "📦 Перенос Managers (24 файла)..."
rsync -avz security/managers/ root@$NEW_SERVER:/opt/aladdin-backend/security/managers/

echo "📦 Перенос Microservices (17 файлов)..."
rsync -avz security/microservices/ root@$NEW_SERVER:/opt/aladdin-backend/security/microservices/

echo "📦 Перенос Active (7 файлов)..."
rsync -avz security/active/ root@$NEW_SERVER:/opt/aladdin-backend/security/active/

echo "📦 Перенос Family (18 файлов)..."
rsync -avz --exclude="test_*.py" --exclude="*test*.py" --exclude="fix_*.py" --exclude="check_*.py" security/family/ root@$NEW_SERVER:/opt/aladdin-backend/security/family/

echo "📦 Перенос VPN (105 файлов)..."
rsync -avz security/vpn/ root@$NEW_SERVER:/opt/aladdin-backend/security/vpn/

echo "📦 Перенос Antivirus (7 файлов)..."
rsync -avz security/antivirus/ root@$NEW_SERVER:/opt/aladdin-backend/security/antivirus/

echo "📦 Перенос Compliance (3 файла)..."
rsync -avz security/compliance/ root@$NEW_SERVER:/opt/aladdin-backend/security/compliance/

echo "📦 Перенос Core (1 файл)..."
rsync -avz security/core/ root@$NEW_SERVER:/opt/aladdin-backend/security/core/

echo "📦 Перенос критичных security модулей (72 файла)..."
find security -maxdepth 1 -name "*.py" -type f ! -name "test_*.py" ! -name "*test*.py" ! -name "*backup*.py" ! -name "*fixed*.py" ! -name "*patch*.py" ! -name "*old*.py" | while read f; do
    scp "$f" root@$NEW_SERVER:/opt/aladdin-backend/security/
done

echo "📦 Перенос function_registry.json..."
scp data/sfm/function_registry.json root@$NEW_SERVER:/opt/aladdin-backend/data/sfm/

echo "📦 Перенос requirements.txt..."
scp requirements.txt root@$NEW_SERVER:/opt/aladdin-backend/ 2>/dev/null || echo "⚠️ requirements.txt не найден"

echo ""
echo "✅ Перенос завершен!"
echo "📋 Следующие шаги на новом сервере:"
echo "   1. Создать виртуальное окружение: python3 -m venv /opt/aladdin-backend/venvs/main_env"
echo "   2. Активировать: source /opt/aladdin-backend/venvs/main_env/bin/activate"
echo "   3. Установить зависимости: pip install -r /opt/aladdin-backend/requirements.txt"
echo "   4. Проверить компиляцию: python3 -m compileall /opt/aladdin-backend/security"
```

**Использование:**
```bash
chmod +x migrate_to_new_server.sh
./migrate_to_new_server.sh NEW_SERVER_IP
```

---

## 📊 ЧТО НУЖНО ДЛЯ ПЕРЕНОСА

### Минимальные требования:

1. **Доступ к новому серверу:**
   - SSH доступ (root или sudo)
   - Python 3.8+ установлен
   - ~2GB свободного места

2. **Локальные файлы на Mac:**
   - Все файлы в `/Users/sergejhlystov/ALADDIN_NEW/`
   - Или архив с текущего сервера

3. **Сетевой доступ:**
   - Интернет для установки зависимостей
   - Доступ к новому серверу по SSH

---

## 🔐 БЕЗОПАСНОСТЬ

### Рекомендации:

1. **Используйте SSH ключи** вместо паролей:
   ```bash
   ssh-keygen -t rsa -b 4096
   ssh-copy-id root@NEW_SERVER_IP
   ```

2. **Проверьте целостность файлов:**
   ```bash
   # На Mac
   find security -type f -name "*.py" -exec md5 {} \; > local_checksums.txt
   
   # На новом сервере
   find /opt/aladdin-backend/security -type f -name "*.py" -exec md5sum {} \; > server_checksums.txt
   
   # Сравнить
   diff local_checksums.txt server_checksums.txt
   ```

3. **Создайте бэкап перед переносом:**
   ```bash
   tar -czf ~/backups/aladdin-backend-$(date +%Y%m%d).tar.gz /opt/aladdin-backend/
   ```

---

## ✅ ПРОВЕРКА ПОСЛЕ ПЕРЕНОСА

```bash
# На новом сервере
ssh root@NEW_SERVER_IP

# Проверка структуры
find /opt/aladdin-backend/security -type f -name "*.py" | wc -l  # Должно быть ~363

# Проверка компиляции
source /opt/aladdin-backend/venvs/main_env/bin/activate
python3 -m compileall /opt/aladdin-backend/security

# Проверка function_registry.json
ls -lh /opt/aladdin-backend/data/sfm/function_registry.json  # Должно быть ~993KB
```

---

## 📝 ИТОГО

**Ответы на ваши вопросы:**

1. ✅ **Да, мы просто скопировали файлы** - использовали `rsync` и `scp`
2. ✅ **На локальном Mac все осталось** - файлы не удалялись
3. ✅ **Для переброски на другой сервер:**
   - Используйте тот же процесс (rsync/scp)
   - Или создайте архив и перенесите
   - Или используйте скрипт `migrate_to_new_server.sh`

**Все файлы остались на вашем Mac и готовы для переноса на любой другой сервер!**

