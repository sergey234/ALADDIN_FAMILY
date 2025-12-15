# 🛠️ РЕШЕНИЕ: ПОШАГОВАЯ ИНСТРУКЦИЯ

**Для:** Другая ML система / Будущий AI ассистент  
**Задача:** Добавить 7 endpoints мониторинга в API Gateway  
**Проблема:** Не удается загрузить Python скрипт на сервер через `expect`

---

## 🎯 ЦЕЛЬ

Добавить в файл `/opt/aladdin-backend/security/microservices/api_gateway.py`:
- Инициализацию мониторинга (`startup_event_monitoring`)
- 7 endpoints для мониторинга (`/api/metrics`, `/api/metrics/cpu`, `/api/metrics/ram`, `/api/metrics/disk`, `/api/alerts`, `/api/alerts/active`, `/api/health`)

**Место вставки:** Перед строкой `if __name__ == "__main__":`

---

## 📋 ШАГ 1: ПОДГОТОВКА ФАЙЛА

**Файл уже создан:** `/tmp/add_endpoints.py`

**Проверка:**
```bash
ls -la /tmp/add_endpoints.py
cat /tmp/add_endpoints.py | head -20
```

**Если файла нет, создать:**
```bash
# См. содержимое в docs/PROBLEM_FILE_UPLOAD_DETAILED.md
```

---

## 📋 ШАГ 2: ЗАГРУЗКА НА СЕРВЕР

### Вариант A: Использовать `sshpass` (РЕКОМЕНДУЕТСЯ)

**Установка sshpass (если нет):**
```bash
# macOS
brew install hudochenkov/sshpass/sshpass

# Linux
sudo apt-get install sshpass
```

**Загрузка:**
```bash
sshpass -p 'Sergio675' scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

**Проверка:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 "ls -la /tmp/add_endpoints.py"
```

---

### Вариант B: Использовать SSH ключи

**Если SSH ключи настроены:**
```bash
scp /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

**Если SSH ключи НЕ настроены, настроить:**
```bash
# 1. Создать ключ
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aladdin_server -N ""

# 2. Скопировать на сервер
ssh-copy-id -i ~/.ssh/aladdin_server.pub root@149.154.65.180

# 3. Использовать ключ
scp -i ~/.ssh/aladdin_server /tmp/add_endpoints.py root@149.154.65.180:/tmp/add_endpoints.py
```

---

### Вариант C: Вручную через SSH

**Подключиться к серверу:**
```bash
ssh root@149.154.65.180
# Ввести пароль: Sergio675
```

**Создать файл на сервере:**
```bash
cd /tmp
nano add_endpoints.py
# Вставить содержимое файла (см. docs/PROBLEM_FILE_UPLOAD_DETAILED.md)
# Сохранить: Ctrl+O, Enter, Ctrl+X
```

---

## 📋 ШАГ 3: ВЫПОЛНЕНИЕ СКРИПТА

**С sshpass:**
```bash
sshpass -p 'Sergio675' ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"
```

**С SSH ключами:**
```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 /tmp/add_endpoints.py"
```

**Ожидаемый вывод:**
```
✅ Endpoints добавлены перед строкой 870
✅ Файл обновлен: 1040 строк
```

---

## 📋 ШАГ 4: ПРОВЕРКА РЕЗУЛЬТАТА

**Проверка синтаксиса:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && python3 -m py_compile api_gateway.py && echo '✅ Синтаксис правильный'"
```

**Проверка endpoints:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && grep -n '@app.get' api_gateway.py | grep -E '/api/metrics|/api/alerts|/api/health'"
```

**Ожидаемый вывод:**
```
870:@app.get("/api/metrics")
880:@app.get("/api/metrics/cpu")
890:@app.get("/api/metrics/ram")
900:@app.get("/api/metrics/disk")
910:@app.get("/api/alerts")
920:@app.get("/api/alerts/active")
930:@app.get("/api/health")
```

**Проверка инициализации:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && grep -n 'startup_event_monitoring' api_gateway.py"
```

**Ожидаемый вывод:**
```
860:async def startup_event_monitoring():
```

---

## 📋 ШАГ 5: ПРОВЕРКА РАБОТЫ API GATEWAY

**Перезапустить API Gateway:**
```bash
ssh root@149.154.65.180 "systemctl restart aladdin-api-gateway && systemctl status aladdin-api-gateway"
```

**Проверить логи:**
```bash
ssh root@149.154.65.180 "journalctl -u aladdin-api-gateway -n 20 --no-pager"
```

**Ожидаемый вывод:**
```
✅ Мониторинг и алерты инициализированы
```

**Проверить endpoints:**
```bash
curl https://aladdin-ai.ru/api/metrics
curl https://aladdin-ai.ru/api/alerts
curl https://aladdin-ai.ru/api/health
```

---

## 🔍 ДИАГНОСТИКА ПРОБЛЕМ

### Если скрипт не выполняется:

**Проверить права доступа:**
```bash
ssh root@149.154.65.180 "ls -la /tmp/add_endpoints.py"
# Должно быть: -rw-r--r-- или -rwxr-xr-x
```

**Проверить Python путь:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && source /opt/aladdin-backend/venvs/main_env/bin/activate && which python3"
```

**Проверить файл на сервере:**
```bash
ssh root@149.154.65.180 "head -20 /tmp/add_endpoints.py"
```

---

### Если endpoints не добавляются:

**Проверить, не добавлены ли уже:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && grep -n '@app.get(\"/api/metrics\")' api_gateway.py"
```

**Если уже добавлены, скрипт выведет:**
```
⚠️  Endpoints уже добавлены!
```

**Проверить место вставки:**
```bash
ssh root@149.154.65.180 "cd /opt/aladdin-backend/security/microservices && grep -n 'if __name__' api_gateway.py"
```

---

## ✅ КРИТЕРИИ УСПЕХА

1. ✅ Файл `/tmp/add_endpoints.py` загружен на сервер
2. ✅ Скрипт выполнен без ошибок
3. ✅ Синтаксис `api_gateway.py` правильный
4. ✅ 7 endpoints добавлены в файл
5. ✅ Инициализация `startup_event_monitoring` добавлена
6. ✅ API Gateway перезапущен и работает
7. ✅ Endpoints доступны через HTTPS

---

## 📝 ЗАМЕТКИ

- **Пароль:** `Sergio675`
- **Сервер:** `root@149.154.65.180`
- **Путь к файлу:** `/opt/aladdin-backend/security/microservices/api_gateway.py`
- **Виртуальное окружение:** `/opt/aladdin-backend/venvs/main_env/bin/activate`
- **Сервис:** `aladdin-api-gateway`

---

**Готово к выполнению!** 🚀

