# 📋 ДЕТАЛЬНЫЙ ПЛАН ЛОКАЛИЗАЦИИ SUPPORT SCREEN

## 🔍 АНАЛИЗ ТЕКУЩЕЙ СИТУАЦИИ

### Подсчет элементов на странице Support Screen:

**Всего элементов: 49**

1. **Навигационная панель (3 элемента):**
   - Кнопка "Назад"
   - Заголовок "ПОДДЕРЖКА"
   - Подзаголовок "Мы всегда рядом"

2. **Поиск (1 элемент):**
   - Карточка поиска с плейсхолдером

3. **Способы связи (4 элемента):**
   - Заголовок "СВЯЗАТЬСЯ С НАМИ"
   - Карточка "Чат поддержки"
   - Карточка "AI-помощник"
   - Карточка "Телефон"

4. **FAQ (41 элемент):**
   - Заголовок "ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ"
   - 40 вопросов-карточек (каждая с вопросом и ответом)

---

## 📊 СТАТИСТИКА ЛОКАЛИЗАЦИИ

### FAQ Ключи:
- **Всего нужно:** 80 ключей (40 вопросов + 40 ответов)
- **В русской секции:** ✅ 80 ключей (100%)
- **В английской секции:** ❌ 4 ключа (5%)
  - ✅ `faq_how_network_protection_works` + answer
  - ✅ `faq_unsafe_wifi` + answer
  - ❌ **Остальные 76 ключей отсутствуют!**

### Support ключи:
- **Всего нужно:** 28 ключей (заголовки, кнопки, accessibility labels)
- **В русской секции:** ✅ 28 ключей (100%)
- **В английской секции:** ✅ 28 ключей (100%)

---

## ❌ ПРОБЛЕМА

**Почему переводы не работают:**
1. В английской секции отсутствуют 76 из 80 FAQ ключей
2. Когда пользователь переключается на английский язык, `LocalizationManager` не находит английские версии
3. Система возвращает русские версии как fallback (из-за логики в `localized()` методе)

---

## ✅ ПЛАН ДЕЙСТВИЙ

### ШАГ 1: Добавить все недостающие английские FAQ ключи

**Нужно добавить 76 ключей (38 вопросов + 38 ответов):**

#### 📋 ОБЩИЕ ВОПРОСЫ (4 вопроса - 8 ключей):
1. `faq_what_protects` + answer
2. `faq_protect_children` + answer
3. `faq_protect_elderly` + answer
4. `faq_data_safe` + answer

#### 🛡️ КИБЕРУГРОЗЫ (6 вопросов - 12 ключей):
5. `faq_viruses_trojans` + answer
6. `faq_ransomware` + answer
7. `faq_spyware` + answer
8. `faq_phishing_sites` + answer
9. `faq_fake_apps` + answer
10. `faq_malicious_links` + answer

#### 💰 МОШЕННИЧЕСТВО (5 вопросов - 10 ключей):
11. `faq_phone_scam` + answer
12. `faq_financial_scam` + answer
13. `faq_social_engineering` + answer
14. `faq_fake_banks` + answer
15. `faq_phishing_emails` + answer

#### 👶 ДЕТСКИЕ УГРОЗЫ (5 вопросов - 10 ключей):
16. `faq_inappropriate_content` + answer
17. `faq_cyberbullying` + answer
18. `faq_dangerous_contacts` + answer
19. `faq_gaming_addiction` + answer
20. `faq_accidental_purchases` + answer

#### 🔒 УТЕЧКИ ДАННЫХ (2 вопроса - 4 ключа):
21. `faq_password_theft` + answer
22. `faq_privacy_violation` + answer

#### 🎭 ПОДДЕЛКИ (3 вопроса - 6 ключей):
23. `faq_deepfake` + answer
24. `faq_fake_voices` + answer
25. `faq_fake_news` + answer

#### 🌐 ИНТЕРНЕТ-УГРОЗЫ (4 вопроса - 8 ключей):
26. `faq_dangerous_sites` + answer
27. `faq_suspicious_downloads` + answer
28. `faq_unsafe_wifi` + answer ✅ (уже есть)
29. `faq_mitm_attacks` + answer

#### 📱 МОБИЛЬНЫЕ УГРОЗЫ (3 вопроса - 6 ключей):
30. `faq_malicious_apps` + answer
31. `faq_sms_scam` + answer
32. `faq_location_threats` + answer

#### 🏠 СЕМЕЙНЫЕ УГРОЗЫ (2 вопроса - 4 ключа):
33. `faq_domestic_violence` + answer
34. `faq_emotional_problems` + answer

#### 🔐 ВОЕННАЯ ЗАЩИТА (3 вопроса - 6 ключей):
35. `faq_aes256` + answer
36. `faq_anonymity` + answer
37. `faq_critical_infrastructure` + answer

#### 💻 ТЕХНИЧЕСКИЕ ВОПРОСЫ (3 вопроса - 6 ключей):
38. `faq_how_network_protection_works` + answer ✅ (уже есть)
39. `faq_parental_control_setup` + answer
40. `faq_cancel_subscription` + answer

---

### ШАГ 2: Проверить правильность использования локализации

**Проверить:**
- ✅ Все строки в `SupportScreen.swift` используют `localizationManager.localized()`
- ✅ Нет захардкоженных строк
- ✅ Все accessibility labels локализованы

---

### ШАГ 3: Добавить английские переводы

**Место добавления:** После строки 4779 в `LocalizationManager.swift` (после `faq_unsafe_wifi_answer`)

**Формат:**
```swift
"faq_what_protects": "What does the system protect?",
"faq_what_protects_answer": "ALADDIN protects against 100+ types of dangers on the internet...",
// и так далее для всех 76 ключей
```

---

## 📝 ПРИОРИТЕТЫ

1. **КРИТИЧНО:** Добавить все 76 недостающих английских FAQ ключей
2. **ВАЖНО:** Проверить, что все ключи добавлены правильно
3. **ПРОВЕРИТЬ:** Тестирование переключения языка в приложении

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения плана:
- ✅ Все 80 FAQ ключей будут на русском и английском
- ✅ Все 28 Support ключей уже есть на обоих языках
- ✅ При переключении на английский язык все тексты будут отображаться на английском
- ✅ Никаких fallback на русский язык

---

## ⚠️ ВАЖНО

**Почему раньше переводили, но сейчас нет:**
- Вероятно, английские версии FAQ были удалены или не были добавлены изначально
- В английской секции остались только 2 FAQ ключа из 80
- Нужно добавить все недостающие переводы

