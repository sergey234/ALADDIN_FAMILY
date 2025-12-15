# ОБЪЯСНЕНИЕ ПРОБЛЕМЫ С /privacy И /terms

**Дата:** 11 декабря 2025

---

## ❓ В ЧЕМ ПРОБЛЕМА?

### Текущая ситуация:

1. ✅ `https://aladdin-ai.ru/privacy.html` - **РАБОТАЕТ** (показывает Privacy Policy)
2. ✅ `https://aladdin-ai.ru/terms.html` - **РАБОТАЕТ** (показывает Terms of Use)
3. ❌ `https://aladdin-ai.ru/privacy` - **НЕ РАБОТАЕТ** (показывает главную страницу)
4. ❌ `https://aladdin-ai.ru/terms` - **НЕ РАБОТАЕТ** (показывает главную страницу)

---

## 🎯 ПОЧЕМУ НУЖНЫ КОРОТКИЕ URL?

### Требования Apple:

**Apple требует в App Store Connect указать:**
- Privacy Policy URL: `https://aladdin-ai.ru/privacy` (БЕЗ `.html`)
- Terms of Use URL: `https://aladdin-ai.ru/terms` (БЕЗ `.html`)

**Почему:**
- ✅ Профессиональный вид
- ✅ Соответствие стандартам
- ✅ Удобство для пользователей
- ✅ Требование Apple

**НЕ подходит:**
- ❌ `https://aladdin-ai.ru/privacy.html` - Apple может отклонить
- ❌ `https://aladdin-ai.ru/terms.html` - Apple может отклонить

---

## 🔧 РЕШЕНИЕ:

### Что нужно сделать:

Настроить nginx так, чтобы:
- `/privacy` → показывал содержимое `privacy.html` **НАПРЯМУЮ** (без редиректа)
- `/terms` → показывал содержимое `terms.html` **НАПРЯМУЮ** (без редиректа)

### Правильная конфигурация nginx:

```nginx
# В блоке server { listen 443 ssl; ... }
location = /privacy {
    alias /var/www/aladdin-ai.ru/privacy.html;
}

location = /terms {
    alias /var/www/aladdin-ai.ru/terms.html;
}
```

**ВАЖНО:**
- Блоки должны быть **ВНУТРИ** HTTPS server блока (порт 443)
- Должны быть **ПЕРЕД** `location / {`
- Используется `alias` (не `try_files`)

---

## ⚠️ ТЕКУЩАЯ ПРОБЛЕМА:

Location блоки добавлены, но:
- ❌ Показывают главную страницу вместо privacy.html/terms.html
- ❌ Возможно находятся не в том server блоке
- ❌ Или перехватываются другим location блоком

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА:

После исправления должно быть:

```bash
curl -s https://aladdin-ai.ru/privacy | grep -i '<title>'
# Ожидается: <title>Политика конфиденциальности — ALADDIN AI</title>

curl -s https://aladdin-ai.ru/terms | grep -i '<title>'
# Ожидается: <title>Условия использования / Публичная оферта — ALADDIN AI</title>
```

**НЕ должно быть:**
- ❌ `<title>ALADDIN AI — Оплата подписки</title>` (это главная страница)

---

**Дата создания:** 11 декабря 2025
