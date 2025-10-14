# 🛡️ CLOUDFLARE: ПОШАГОВАЯ ИНСТРУКЦИЯ

## 📋 ЧТО НУЖНО СДЕЛАТЬ (ПО ПОРЯДКУ)

### ✅ ЭТАП 1: Регистрация на Cloudflare (5 минут)

1. Откройте https://cloudflare.com
2. Нажмите **Sign Up**
3. Введите email: `admin@aladdin.family`
4. Создайте пароль
5. Подтвердите email

**Статус:** Аккаунт создан ✅

---

### ✅ ЭТАП 2: Добавление домена (10 минут)

1. В dashboard нажмите **Add Site**
2. Введите домен: `aladdin.family`
3. Выберите план: **FREE** (бесплатно!)
4. Нажмите **Continue**

**Что получите бесплатно:**
- ✅ DDoS защита (до 100 Гбит/с)
- ✅ SSL сертификат (автоматически)
- ✅ CDN (ускорение)
- ✅ WAF (базовые правила)
- ✅ Analytics

**Статус:** Домен добавлен ✅

---

### ✅ ЭТАП 3: Смена NS записей (15-30 минут)

#### Cloudflare покажет 2 nameserver:

```
ns1.cloudflare.com
ns2.cloudflare.com
```

#### Действия:

1. Зайдите к вашему регистратору домена (где купили aladdin.family)
2. Найдите раздел **DNS Management** или **Nameservers**
3. Замените текущие NS на:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
4. Сохраните изменения

**Ожидание:** 5 минут - 48 часов (обычно 30 минут)

**Статус:** NS обновлены ✅

---

### ✅ ЭТАП 4: SSL/TLS настройки (2 минуты)

После активации домена:

1. Перейдите в **SSL/TLS**
2. Выберите режим: **Full (strict)**
3. Включите:
   - ✅ **Always Use HTTPS**
   - ✅ **Automatic HTTPS Rewrites**
   - ✅ **TLS 1.3**

**Статус:** SSL настроен ✅

---

### ✅ ЭТАП 5: Firewall Rules (10 минут)

#### Перейдите в **Security → WAF**

#### Правило 1: Блокировка плохих ботов
```
Rule name: Block Bad Bots
Expression: (cf.client.bot) and not (cf.verified_bot_category in {"Search Engine Crawler"})
Action: Block
```

#### Правило 2: Rate Limit на логин
```
Rule name: Rate Limit Login
Expression: (http.request.uri.path eq "/api/auth/login")
Action: Challenge
Rate: 5 requests per 60 seconds
```

#### Правило 3: Защита API
```
Rule name: Protect API
Expression: (http.request.uri.path contains "/api/")
Action: Managed Challenge
```

#### Правило 4: Блокировка SQL Injection
```
Rule name: Block SQL Injection
Expression: (http.request.uri.query contains "UNION" or http.request.uri.query contains "SELECT")
Action: Block
```

#### Правило 5: Разрешить мобильные приложения
```
Rule name: Allow Mobile Apps
Expression: (http.user_agent contains "ALADDIN-iOS" or http.user_agent contains "ALADDIN-Android")
Action: Skip
Skip: All remaining WAF rules
```

**Статус:** Firewall настроен ✅

---

### ✅ ЭТАП 6: Rate Limiting (5 минут)

Перейдите в **Security → Rate Limiting Rules**

#### Правило 1: API Global Limit
```
Name: API Global Rate Limit
URL: aladdin.family/api/*
Threshold: 300 requests per 60 seconds
Action: Block
Duration: 3600 seconds (1 час)
```

#### Правило 2: Registration Limit
```
Name: Registration Rate Limit
URL: aladdin.family/api/family/create
Threshold: 3 requests per 3600 seconds (1 час)
Action: Block
Duration: 86400 seconds (24 часа)
```

#### Правило 3: Login Limit
```
Name: Login Rate Limit
URL: aladdin.family/api/auth/*
Threshold: 10 requests per 300 seconds (5 минут)
Action: Challenge
Duration: 900 seconds (15 минут)
```

**Статус:** Rate Limiting настроен ✅

---

### ✅ ЭТАП 7: Caching (3 минуты)

Перейдите в **Caching → Configuration**

#### Настройки:

1. **Cache Level:** Standard
2. **Browser Cache TTL:** 4 hours
3. **Always Online:** ON

#### Page Rules (Caching → Page Rules):

**Rule 1: Кэширование статики**
```
URL: aladdin.family/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 day
  - Browser Cache TTL: 1 day
```

**Rule 2: НЕ кэшировать API**
```
URL: aladdin.family/api/*
Settings:
  - Cache Level: Bypass
```

**Rule 3: Кэширование HTML**
```
URL: aladdin.family/*.html
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 hour
```

**Статус:** Кэширование настроено ✅

---

### ✅ ЭТАП 8: Security Headers (5 минут)

Перейдите в **Security → Settings**

Включите:
- ✅ **Browser Integrity Check**
- ✅ **Privacy Pass Support**
- ✅ **Security Level:** High

#### Transform Rules → HTTP Response Headers:

Добавьте headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Статус:** Security Headers настроены ✅

---

### ✅ ЭТАП 9: Bot Management (2 минуты)

Перейдите в **Security → Bots**

1. **Bot Fight Mode:** ON
2. **Super Bot Fight Mode:** ON (если доступно)
3. **Verified Bots:** Allow (Google, Yandex, Bing)

**Статус:** Bot Protection настроен ✅

---

### ✅ ЭТАП 10: Performance (3 минуты)

Перейдите в **Speed → Optimization**

Включите:
- ✅ **Auto Minify:** HTML, CSS, JavaScript
- ✅ **Brotli Compression**
- ✅ **Early Hints**
- ✅ **HTTP/2**
- ✅ **HTTP/3 (QUIC)**
- ❌ **Rocket Loader:** OFF (для мобильных приложений)

**Статус:** Performance настроен ✅

---

### ✅ ЭТАП 11: Analytics & Alerts (5 минут)

#### Включите Analytics:

1. **Web Analytics:** ON
2. **Firewall Analytics:** ON

#### Настройте Alerts (Notifications):

**Alert 1: DDoS Attack**
```
Type: DDoS Attack Detected (HTTP/HTTPS)
Notification: Email to security@aladdin.family
```

**Alert 2: High Error Rate**
```
Type: Origin Error Rate Alert
Threshold: 100 errors in 5 minutes
Notification: Email to devops@aladdin.family
```

**Alert 3: SSL Expiry**
```
Type: Universal SSL Certificate
Event: Validation, Issuance, Renewal
Notification: Email to admin@aladdin.family
```

**Статус:** Мониторинг настроен ✅

---

## 📊 ИТОГОВЫЙ ЧЕКЛИСТ

После завершения всех этапов проверьте:

```
☑ Cloudflare аккаунт создан
☑ Домен aladdin.family добавлен
☑ NS записи обновлены у регистратора
☑ SSL/TLS: Full (strict) mode
☑ Always Use HTTPS: ON
☑ 5 Firewall Rules созданы
☑ 3 Rate Limiting Rules созданы
☑ 3 Page Rules для кэширования
☑ Security Headers добавлены
☑ Bot Fight Mode: ON
☑ Performance оптимизации: ON
☑ 3 Alert настроены
```

---

## 🎯 ЧТО ПОЛУЧИТЕ ПОСЛЕ НАСТРОЙКИ

### 🛡️ Безопасность:
- ✅ Защита от DDoS атак (до 100 Гбит/с)
- ✅ WAF (защита от SQL injection, XSS)
- ✅ Rate Limiting (защита от brute-force)
- ✅ Bot protection (блокировка плохих ботов)
- ✅ SSL сертификат (автоматический)

### ⚡ Производительность:
- ✅ CDN (контент ближе к пользователям)
- ✅ Кэширование (быстрее загрузка)
- ✅ Сжатие (Brotli, Gzip)
- ✅ HTTP/3 (быстрее соединение)

### 📊 Мониторинг:
- ✅ Analytics (статистика)
- ✅ Alerts (уведомления о проблемах)
- ✅ Firewall logs (логи атак)

---

## ⏱️ ОБЩЕЕ ВРЕМЯ: 60-90 минут

- Регистрация: 5 мин
- Добавление домена: 10 мин
- NS записи: 15-30 мин (ожидание)
- SSL/TLS: 2 мин
- Firewall: 10 мин
- Rate Limiting: 5 мин
- Caching: 3 мин
- Headers: 5 мин
- Bots: 2 мин
- Performance: 3 мин
- Alerts: 5 мин

---

## 💰 СТОИМОСТЬ

**FREE план:** $0/месяц
- ✅ Достаточно для старта
- ✅ До 100K пользователей
- ✅ Базовый DDoS protection

**PRO план:** $20/месяц (когда нужно будет)
- 🚀 Приоритетная поддержка
- 🚀 Расширенные WAF правила
- 🚀 Image optimization
- 🚀 Mobile optimization

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

После настройки Cloudflare:

1. ✅ Протестировать защиту (security.cloudflare.com/scan)
2. ✅ Проверить SSL (ssllabs.com/ssltest)
3. ✅ Проверить скорость (webpagetest.org)
4. ✅ Мониторить логи первую неделю

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- Dashboard: https://dash.cloudflare.com
- Analytics: https://dash.cloudflare.com/analytics
- Firewall: https://dash.cloudflare.com/firewall
- Docs: https://developers.cloudflare.com

---

## ⚠️ ВАЖНО

Эта инструкция для **РУЧНОЙ** настройки через веб-интерфейс Cloudflare.

Автоматическая настройка через API или Terraform **НЕ ИСПОЛЬЗУЕТСЯ**.

Делаем всё медленно, по шагам, проверяя каждый этап! ✅




