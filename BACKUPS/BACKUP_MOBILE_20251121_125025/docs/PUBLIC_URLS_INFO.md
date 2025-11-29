# 🌐 ПУБЛИЧНЫЕ URL - ИНФОРМАЦИЯ

**Дата:** 15 ноября 2025  
**Для:** App Store Connect → App Information

---

## 📋 НЕОБХОДИМЫЕ URL

### 1. Privacy Policy URL (Политика конфиденциальности)

**Требуется:** ✅ **ДА** (обязательно)

**Файл:** `20_full_privacy_policy.html` или `docs/PRIVACY_POLICY_FULL_152FZ.md`

**Рекомендуемый URL:**
```
https://aladdin.family/privacy-policy
```
или
```
https://www.aladdin.family/privacy-policy.html
```

**Что нужно сделать:**
1. Загрузить HTML файл на ваш сервер
2. Убедиться, что URL доступен публично
3. Указать URL в App Store Connect

---

### 2. Terms of Service URL (Условия использования)

**Требуется:** ✅ **ДА** (обязательно)

**Файл:** `20_terms_of_service.html`

**Рекомендуемый URL:**
```
https://aladdin.family/terms-of-service
```
или
```
https://www.aladdin.family/terms-of-service.html
```

**Что нужно сделать:**
1. Загрузить HTML файл на ваш сервер
2. Убедиться, что URL доступен публично
3. Указать URL в App Store Connect

---

## 📁 ФАЙЛЫ ДЛЯ ЗАГРУЗКИ

### Privacy Policy:

**Локальный файл:** 
- `20_full_privacy_policy.html` (HTML версия)
- `docs/PRIVACY_POLICY_FULL_152FZ.md` (Markdown версия)

**Содержание:**
- Полная политика конфиденциальности
- Соответствие 152-ФЗ
- NO-LOGS политика
- Информация о шифровании

---

### Terms of Service:

**Локальный файл:**
- `20_terms_of_service.html` (HTML версия)

**Содержание:**
- 12 разделов условий использования
- Информация о платежах (QR и IAP)
- Политика удаления аккаунта
- VPN и безопасность

---

## 🔧 ИНСТРУКЦИИ ПО ЗАГРУЗКЕ

### Вариант 1: Загрузка на ваш сервер

1. **Подготовить файлы:**
   - `20_full_privacy_policy.html` → переименовать в `privacy-policy.html`
   - `20_terms_of_service.html` → переименовать в `terms-of-service.html`

2. **Загрузить на сервер:**
   - Использовать FTP/SFTP
   - Или через панель управления хостингом
   - Или через Git (если сайт на GitHub Pages)

3. **Проверить доступность:**
   - Открыть в браузере: `https://aladdin.family/privacy-policy.html`
   - Открыть в браузере: `https://aladdin.family/terms-of-service.html`
   - ✅ Убедиться, что страницы открываются

---

### Вариант 2: GitHub Pages (бесплатно)

1. **Создать репозиторий:**
   - Создать публичный репозиторий на GitHub
   - Название: `aladdin-privacy-terms`

2. **Загрузить файлы:**
   - Загрузить `20_full_privacy_policy.html` как `privacy-policy.html`
   - Загрузить `20_terms_of_service.html` как `terms-of-service.html`

3. **Включить GitHub Pages:**
   - Settings → Pages
   - Source: main branch
   - Folder: / (root)

4. **URL будут:**
   - `https://yourusername.github.io/aladdin-privacy-terms/privacy-policy.html`
   - `https://yourusername.github.io/aladdin-privacy-terms/terms-of-service.html`

---

### Вариант 3: Временный хостинг

Если нет своего сервера, можно использовать:
- **Netlify** (бесплатно)
- **Vercel** (бесплатно)
- **GitHub Pages** (бесплатно)

---

## ✅ ЧЕКЛИСТ

### Перед загрузкой:

- [ ] Файлы подготовлены (HTML формат)
- [ ] Файлы проверены (открываются в браузере)
- [ ] Нет ошибок в HTML

### После загрузки:

- [ ] URL доступны публично
- [ ] Страницы открываются в браузере
- [ ] Контент отображается правильно
- [ ] HTTPS работает (обязательно!)

### В App Store Connect:

- [ ] Privacy Policy URL указан
- [ ] Terms of Service URL указан
- [ ] URL проверены (открываются)

---

## ⚠️ ВАЖНЫЕ ТРЕБОВАНИЯ

1. **HTTPS обязателен:** URL должны начинаться с `https://`
2. **Публичный доступ:** Страницы должны быть доступны без авторизации
3. **Актуальность:** Контент должен соответствовать приложению
4. **Язык:** Минимум English, желательно также русский

---

## 📝 ПРИМЕР URL В APP STORE CONNECT

**Privacy Policy URL:**
```
https://aladdin.family/privacy-policy.html
```

**Terms of Service URL:**
```
https://aladdin.family/terms-of-service.html
```

---

**Дата создания:** 15 ноября 2025  
**Статус:** ✅ **ГОТОВО К ЗАГРУЗКЕ**



