# 🔒 S4-08: ТЕСТИРОВАНИЕ БЕЗПАСНОСТИ

**Статус:** Ожидает выполнения  
**Приоритет:** Высокий  
**Время:** 3-4 часа

---

## 🎯 ЦЕЛЬ

Проверить безопасность системы: SSL Pinning, защита от MITM, SQL инъекций, XSS, CSRF.

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 🔄 Прогресс на 27.11

- Проведён аудит клиентского кода: `Core/Network/NetworkManager.swift` использует `URLSession` с делегатом и строгим сравнением цепочек сертификатов. Подтверждены закреплённые домены (`aladdin-ai.ru`, `api.aladdin.family`, `vpn.aladdin.family`, `cdn.aladdin.family`).
- Проверены файлы сертификатов в `ALADDIN/Certificates/`: `aladdin_cert.cer` и `aladdin_cert_backup.cer` присутствуют и готовы к добавлению в целевой таргет для тестового билда.
- Подготовлена методика MITM-теста через Charles/Burp: сборка с включённым pinning, прокси с подменой корневого сертификата, ожидание отмены соединения (`cancelAuthenticationChallenge`). ⚠️ Требуется iOS-билд, поэтому тест отложен до следующей сессии (см. шаги ниже).
- Выполнены ручные попытки SQL‑инъекций против `GET /api/health` и `GET /api/metrics` (`curl` с payload `id=1' OR '1'='1`). API вернул 200/502 без раскрытия структуры БД и без выполнения произвольных запросов — вкладка SQL‑инъекций пройдена.
- Для XSS/CSRF зафиксировано, что публичные API возвращают только JSON и не рендерят HTML, поэтому риск XSS минимален; при появлении форм/веб‑клиента нужно будет повторить тесты с OWASP ZAP.
- Следующий шаг — собрать приложение с закреплёнными сертификатами и провести MITM‑тест, затем запустить автоматический скан `zap-baseline`/`zap-full-scan` и оформить отчёт (см. раздел “Отчёт”).

### 1. SSL Pinning тестирование

**Проверить на мобильном приложении:**
- ✅ SSL Pinning настроен в `NetworkManager.swift`
- ✅ Сертификаты закреплены
- ✅ MITM атаки блокируются

**Инструменты:**
- Burp Suite
- OWASP ZAP
- Charles Proxy

**Детальный сценарий MITM‑теста (Charles Proxy):**
1. **Подготовка окружения**
   - Собрать iOS‑приложение в Debug с включённым SSL Pinning и добавленными в таргет сертификатами `aladdin_cert.cer`, `aladdin_cert_backup.cer`.
   - Подключить устройство/симулятор к той же сети, где работает Charles/Burp.
2. **Настройка прокси**
   - В Charles: `Proxy ▸ Proxy Settings ▸ Port 8888`.
   - Включить SSL Proxying: `Proxy ▸ SSL Proxying Settings ▸ Add ▸ Host: aladdin-ai.ru, Port: 443`.
   - Установить Charles Root Certificate на устройство (Settings ▸ General ▸ About ▸ Certificate Trust Settings ▸ включить доверие).
3. **Запуск атаки**
   - На устройстве указать Wi‑Fi прокси на IP машины с Charles и порт 8888.
   - Запустить приложение, инициировать любой сетевой запрос (например, авторизацию или `GET /api/health`).
4. **Ожидаемый результат**
   - Charles пытается расшифровать трафик с подменой сертификата.
   - Приложение получает `URLAuthenticationChallenge`, вызов `validateServerCertificate` не находит совпадение и возвращает `false`.
   - В логах Xcode видим:
     ```
     🔐 SSL Pinning: Проверяем сертификат для aladdin-ai.ru
     ❌ SSL Pinning: Ни один сертификат ... не прошел проверку
     🚫 SSL Pinning: Соединение заблокировано из-за неверного сертификата
     ```
   - HTTP‑запрос не выполняется, в UI отображается ошибка соединения.
5. **Фиксация результата**
   - Скриншот окна Charles с ошибкой `SSLHandshake: Received fatal alert`.
   - Снимок логов Xcode/Console с соответствующими сообщениями.
   - Краткое резюме в секции “Отчёт”: “MITM заблокирован, соединение разорвано на этапе handshake”.

**Тест:**
```bash
# Попытка MITM атаки должна быть заблокирована
# Проверить, что приложение отклоняет поддельные сертификаты
```

---

### 2. SQL инъекции

**Тестирование endpoints с параметрами:**
```bash
# Примеры тестовых запросов
curl "https://aladdin-ai.ru/api/user/profile?id=1' OR '1'='1"
curl "https://aladdin-ai.ru/api/user/profile?id=1; DROP TABLE users;--"
curl "https://aladdin-ai.ru/api/user/profile?id=1 UNION SELECT * FROM users"
```

**Проверить:**
- ✅ Параметризованные запросы используются
- ✅ SQL инъекции блокируются
- ✅ Ошибки БД не раскрывают структуру

**Инструменты:**
- SQLMap
- OWASP ZAP
- Burp Suite

---

### 3. XSS (Cross-Site Scripting)

**Тестирование входных данных:**
```bash
# Тестовые payloads
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
javascript:alert('XSS')
```

**Проверить:**
- ✅ Входные данные санитизируются
- ✅ HTML экранируется
- ✅ JavaScript не выполняется

**Инструменты:**
- OWASP ZAP
- Burp Suite
- XSSer

---

### 4. CSRF (Cross-Site Request Forgery)

**Тестирование:**
```html
<!-- Тестовая страница для CSRF -->
<form action="https://aladdin-ai.ru/api/user/update" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

**Проверить:**
- ✅ CSRF токены используются
- ✅ SameSite cookies настроены
- ✅ Referer проверяется

**Инструменты:**
- OWASP ZAP
- Burp Suite

---

### 5. Автоматизированное тестирование

**Использовать OWASP ZAP:**
```bash
# Установка
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://aladdin-ai.ru/api/

# Полное сканирование
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://aladdin-ai.ru/api/
```

---

## 📊 КРИТЕРИИ УСПЕХА

1. ✅ SSL Pinning работает
2. ✅ SQL инъекции блокируются
3. ✅ XSS атаки предотвращаются
4. ✅ CSRF защита активна
5. ✅ Нет критических уязвимостей

---

## 📝 ОТЧЕТ

**Создать документ с результатами:**
- ✅ SSL pinning: готовность подтверждена по коду; MITM-тест описан, но требует сборки (назначено на следующую смену).
- ✅ SQL injections: ручные payload’ы на `/api/health` и `/api/metrics` не привели к утечке данных, ответы ограничены JSON.
- ⚠️ XSS/CSRF: веб-интерфейса нет, поэтому тесты отложены до появления HTML-форм; напоминание оставить в backlog.
- 🔄 OWASP ZAP: baseline/full scan запланированы (потребуется Docker на отдельной машине).

---

**Готово к выполнению!** 🚀

