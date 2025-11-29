# 🌐 WEBSOCKET СЕРВЕР: ПРОСТОЕ ОБЪЯСНЕНИЕ

**Дата:** 2025-11-25  
**Язык:** Простой, без технических терминов

---

## 💬 ЧТО ТАКОЕ WEBSOCKET СЕРВЕР?

### **Простыми словами:**

**Обычный HTTP (как сейчас):**
```
📱 iOS → "Есть ли новые угрозы?" → 🖥️ Сервер
🖥️ Сервер → "Нет" → 📱 iOS
📱 iOS → (ждет 15 минут) → "Есть ли новые угрозы?" → 🖥️ Сервер
🖥️ Сервер → "Нет" → 📱 iOS
... и так каждые 15 минут
```

**WebSocket (как мессенджер):**
```
📱 iOS ←→ 🖥️ Сервер (постоянное соединение)
🖥️ Сервер → "Обнаружена угроза!" → 📱 iOS (мгновенно)
🖥️ Сервер → "Новый член семьи!" → 📱 iOS (мгновенно)
🖥️ Сервер → "VPN статус изменился!" → 📱 iOS (мгновенно)
```

**WebSocket сервер** - это программа на вашем сервере, которая:
1. Принимает постоянные соединения от iOS приложений
2. Отправляет сообщения мгновенно, когда что-то происходит
3. Работает параллельно с обычным HTTP API

---

## 🖥️ ВАШ СЕРВЕР: root@149.154.65.180

### **Можно ли использовать ваш сервер?**

**ДА! ✅** Ваш сервер подходит для WebSocket!

**Почему:**
- ✅ Это обычный Linux сервер (Ubuntu/Debian)
- ✅ На нем можно установить Python
- ✅ На нем можно установить Nginx (для WebSocket прокси)
- ✅ На нем можно запустить WebSocket сервер

---

## 🔧 ЧТО НУЖНО УСТАНОВИТЬ НА СЕРВЕРЕ

### **1. Python WebSocket библиотека**

**Что это:**
- Библиотека для создания WebSocket сервера на Python
- Например: `websockets`, `socketio`, `fastapi` с WebSocket

**Установка:**
```bash
pip install websockets
# или
pip install fastapi[websockets]
# или
pip install python-socketio
```

**Где установить:**
- На вашем сервере: `root@149.154.65.180`
- В виртуальном окружении: `/opt/aladdin-backend/venvs/main_env`

---

### **2. Nginx (для WebSocket прокси)**

**Что это:**
- Веб-сервер, который проксирует WebSocket соединения
- Уже будет установлен на этапе 3 (инфраструктура)

**Конфигурация:**
```nginx
# /etc/nginx/sites-available/aladdin
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

**Где настроить:**
- На вашем сервере: `/etc/nginx/sites-available/aladdin`

---

### **3. WebSocket сервер (Python скрипт)**

**Что это:**
- Python скрипт, который обрабатывает WebSocket соединения
- Отправляет уведомления iOS приложениям

**Где разместить:**
- На вашем сервере: `/opt/aladdin-backend/websocket/`
- Файл: `websocket_server.py`

**Пример структуры:**
```
/opt/aladdin-backend/
├── security/          (ваши 286 Python файлов)
├── websocket/         (НОВАЯ папка)
│   ├── websocket_server.py
│   └── handlers/
│       ├── threats.py
│       ├── family.py
│       └── vpn.py
└── venvs/
    └── main_env/
```

---

## 📋 КАК ЭТО БУДЕТ РАБОТАТЬ

### **Архитектура:**

```
📱 iOS App
    │
    │ WebSocket: wss://aladdin-ai.ru/ws
    │
    ▼
🌐 Nginx (на сервере 149.154.65.180)
    │
    │ Проксирует WebSocket
    │
    ▼
🐍 WebSocket Server (Python, порт 8000)
    │
    │ Обрабатывает соединения
    │
    ▼
🤖 AI Agents / Security Services
    │
    │ Обнаруживают угрозы
    │
    ▼
📢 WebSocket Server отправляет уведомление
    │
    │
    ▼
📱 iOS получает мгновенное уведомление
```

---

## ✅ ЧТО УЖЕ ЕСТЬ В ВАШЕМ ПЛАНЕ

### **Из ML_SYSTEM_IMPLEMENTATION_PLAN.md:**

**ЭТАП 3: Настроить инфраструктуру**
- ✅ Установить Nginx - будет установлен
- ✅ Настроить конфигурацию Nginx - можно добавить WebSocket
- ✅ Настроить SSL - будет настроен

**ЭТАП 2: Перенести на сервер**
- ✅ Перенести Python файлы - будет перенесено
- ✅ Установить зависимости - можно добавить websockets

---

## 🎯 ЧТО НУЖНО ДОБАВИТЬ К ПЛАНУ

### **В ЭТАП 2 (Миграция):**

**Добавить установку WebSocket библиотеки:**
```bash
# В /opt/aladdin-backend/venvs/main_env
pip install websockets
# или
pip install fastapi[websockets]
```

### **В ЭТАП 3 (Инфраструктура):**

**Добавить WebSocket конфигурацию в Nginx:**
```nginx
# В /etc/nginx/sites-available/aladdin
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**Добавить WebSocket сервер:**
```bash
# Создать папку
mkdir -p /opt/aladdin-backend/websocket

# Создать файл websocket_server.py
# (будет создан позже)
```

---

## 📝 ПРИМЕР WEBSOCKET СЕРВЕРА

### **Простой пример (websockets библиотека):**

```python
# /opt/aladdin-backend/websocket/websocket_server.py
import asyncio
import websockets
import json

# Хранилище подключенных клиентов
connected_clients = set()

async def handle_client(websocket, path):
    """Обрабатывает подключение клиента"""
    connected_clients.add(websocket)
    print(f"✅ Клиент подключен: {websocket.remote_address}")
    
    try:
        # Отправляем приветствие
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Подключено к ALADDIN WebSocket"
        }))
        
        # Слушаем сообщения от клиента
        async for message in websocket:
            data = json.loads(message)
            print(f"📨 Получено: {data}")
            
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Клиент отключен: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def broadcast_threat(threat_data):
    """Отправляет уведомление о угрозе всем клиентам"""
    message = json.dumps({
        "type": "threat_detected",
        "data": threat_data
    })
    
    # Отправляем всем подключенным клиентам
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except:
            disconnected.add(client)
    
    # Удаляем отключенных клиентов
    connected_clients -= disconnected

# Запуск сервера
async def main():
    server = await websockets.serve(
        handle_client,
        "localhost",  # Только локально (через Nginx)
        8000
    )
    print("🚀 WebSocket сервер запущен на порту 8000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 КАК ЗАПУСТИТЬ WEBSOCKET СЕРВЕР

### **Вариант 1: systemd сервис (рекомендуется)**

**Создать файл:** `/etc/systemd/system/aladdin-websocket.service`

```ini
[Unit]
Description=ALADDIN WebSocket Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend/websocket
Environment="PATH=/opt/aladdin-backend/venvs/main_env/bin"
ExecStart=/opt/aladdin-backend/venvs/main_env/bin/python websocket_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Команды:**
```bash
# Загрузить сервис
systemctl daemon-reload

# Запустить сервис
systemctl start aladdin-websocket

# Включить автозапуск
systemctl enable aladdin-websocket

# Проверить статус
systemctl status aladdin-websocket
```

---

### **Вариант 2: Через screen/tmux (для тестирования)**

```bash
# Установить screen
apt-get install screen

# Создать сессию
screen -S websocket

# Активировать виртуальное окружение
source /opt/aladdin-backend/venvs/main_env/bin/activate

# Запустить сервер
cd /opt/aladdin-backend/websocket
python websocket_server.py

# Отключиться: Ctrl+A, затем D
# Подключиться: screen -r websocket
```

---

## 🔐 БЕЗОПАСНОСТЬ

### **Что нужно настроить:**

1. **SSL/TLS (WSS вместо WS):**
   - WebSocket через HTTPS: `wss://aladdin-ai.ru/ws`
   - Nginx уже будет настроен с SSL (этап 3)

2. **Аутентификация:**
   - Проверка JWT токена при подключении
   - Отключение неавторизованных клиентов

3. **Firewall:**
   - WebSocket сервер слушает только `localhost:8000`
   - Доступ только через Nginx (порт 443)

---

## 📊 ИНТЕГРАЦИЯ С ВАШИМИ КОМПОНЕНТАМИ

### **Как WebSocket сервер будет работать с вашими компонентами:**

**1. AI Agents обнаруживают угрозу:**
```python
# security/ai_agents/threat_detection_agent.py
def detect_threat(self, data):
    threat = self.analyze(data)
    
    # Отправляем через WebSocket
    websocket_server.broadcast_threat({
        "threat_id": threat.id,
        "type": threat.type,
        "severity": threat.severity
    })
```

**2. Family Bot отправляет сообщение:**
```python
# security/bots/family_bot.py
def send_family_message(self, message):
    # Отправляем через WebSocket
    websocket_server.broadcast_family_message({
        "from": message.from_user,
        "text": message.text,
        "timestamp": message.timestamp
    })
```

**3. VPN статус изменился:**
```python
# security/managers/vpn_manager.py
def update_vpn_status(self, status):
    # Отправляем через WebSocket
    websocket_server.broadcast_vpn_status({
        "status": status,
        "server": self.current_server
    })
```

---

## ✅ ВЫВОД

### **Ваш сервер подходит для WebSocket:**

1. ✅ **Сервер:** `root@149.154.65.180` - подходит
2. ✅ **ОС:** Linux (Ubuntu/Debian) - подходит
3. ✅ **Python:** Будет установлен (этап 2) - подходит
4. ✅ **Nginx:** Будет установлен (этап 3) - подходит
5. ✅ **SSL:** Будет настроен (этап 3) - подходит

### **Что нужно добавить:**

1. ⚠️ **WebSocket библиотека** - добавить в `requirements.txt`
2. ⚠️ **WebSocket сервер** - создать Python скрипт
3. ⚠️ **Nginx конфигурация** - добавить `/ws` location
4. ⚠️ **systemd сервис** - для автозапуска

### **Когда добавлять:**

- **Сейчас:** НЕ нужно (не критично для первого релиза)
- **Позже:** После этапа 3 (инфраструктура)
- **Когда:** Если понадобятся мгновенные обновления

---

## 📋 ПЛАН ДЕЙСТВИЙ (если решите добавить)

### **Шаг 1: Установить библиотеку (этап 2)**
```bash
# В /opt/aladdin-backend/venvs/main_env
pip install websockets
```

### **Шаг 2: Создать WebSocket сервер (после этапа 2)**
```bash
# Создать папку
mkdir -p /opt/aladdin-backend/websocket

# Создать файл websocket_server.py
# (код будет предоставлен)
```

### **Шаг 3: Настроить Nginx (этап 3)**
```bash
# Добавить в /etc/nginx/sites-available/aladdin
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### **Шаг 4: Создать systemd сервис (этап 3)**
```bash
# Создать /etc/systemd/system/aladdin-websocket.service
# Запустить сервис
systemctl start aladdin-websocket
```

---

**Дата:** 2025-11-25  
**Вывод:** Ваш сервер **подходит** для WebSocket, но это **не критично** для первого релиза. Можно добавить позже.

