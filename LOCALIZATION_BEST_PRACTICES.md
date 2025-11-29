# 📋 Руководство по работе с локализацией

## ⚠️ Проблема, которая была исправлена

### Что произошло:
Приложение падало с ошибкой `Fatal error: Dictionary literal contains duplicate keys` при запуске.

### Причина:
В словаре `translations` в файле `Core/Localization/LocalizationManager.swift` были найдены **дубликаты ключей** внутри одного и того же языка. Swift не позволяет иметь дубликаты ключей в словаре - это вызывает фатальную ошибку во время выполнения.

### Что было исправлено:
1. ✅ Удалены дубликаты ключей из русского словаря (блок строк 1088-1406)
2. ✅ Удалены дубликаты ключей из русского словаря (блок строк 2000-2398)
3. ✅ Удалены дубликаты ключей из английского словаря (ключ `vpn_protection` на строках 1654 и 1738)
4. ✅ Удалены дубликаты ключей из английского словаря (блок строк 2399-2731)
5. ✅ Словарь `translations` сделан `lazy` для оптимизации производительности

---

## 🛡️ Как предотвратить проблему в будущем

### 1. **Всегда проверяйте дубликаты перед коммитом**

Используйте скрипт проверки:
```bash
python3 scripts/check_localization_duplicates.py
```

### 2. **Правила добавления новых ключей**

- ✅ **ПРОВЕРЯЙТЕ** перед добавлением, что ключ еще не существует
- ✅ Используйте **уникальные имена** ключей
- ✅ Следуйте **конвенции именования**: `screen_section_item` (например: `vpn_protection_status`)
- ✅ Добавляйте ключи **во все языки** одновременно

### 3. **Структура словаря**

```swift
lazy var translations: [Language: [String: String]] = [
    .russian: [
        "key1": "Значение 1",
        "key2": "Значение 2",
        // ❌ НЕ ДОБАВЛЯЙТЕ ДУБЛИКАТЫ!
        // "key1": "Другое значение" // ❌ ОШИБКА!
    ],
    .english: [
        "key1": "Value 1",
        "key2": "Value 2",
    ],
    // ... другие языки
]
```

### 4. **Проверка перед коммитом**

Добавьте в `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python3 scripts/check_localization_duplicates.py
if [ $? -ne 0 ]; then
    echo "❌ Обнаружены дубликаты ключей! Исправьте их перед коммитом."
    exit 1
fi
```

### 5. **Использование IDE**

- Используйте **поиск по проекту** (Cmd+Shift+F) перед добавлением нового ключа
- Проверяйте, что ключ не используется в других местах

### 6. **Автоматическая проверка в CI/CD**

Добавьте проверку в ваш CI/CD pipeline:
```yaml
- name: Check localization duplicates
  run: python3 scripts/check_localization_duplicates.py
```

---

## 🔍 Как найти дубликаты вручную

### Метод 1: Поиск в Xcode
1. Откройте `Core/Localization/LocalizationManager.swift`
2. Используйте Cmd+F для поиска ключа
3. Если найдено более одного вхождения в одном языке - это дубликат!

### Метод 2: Терминал
```bash
# Найти все вхождения ключа
grep -n '"your_key":' Core/Localization/LocalizationManager.swift

# Найти дубликаты в русском словаре
grep -n '"your_key":' Core/Localization/LocalizationManager.swift | grep -A 5 -B 5 ".russian:"
```

### Метод 3: Скрипт проверки
```bash
python3 scripts/check_localization_duplicates.py
```

---

## 📝 Чеклист перед добавлением нового ключа

- [ ] Проверил, что ключ еще не существует (поиск по проекту)
- [ ] Добавил ключ во все языки (russian, english, chinese, arabic)
- [ ] Использовал правильную конвенцию именования
- [ ] Запустил скрипт проверки дубликатов
- [ ] Проверил, что проект компилируется без ошибок

---

## 🚨 Что делать, если нашли дубликат

1. **Найдите оба вхождения** ключа
2. **Определите, какое значение правильное**
3. **Удалите дубликат**, оставив только одно вхождение
4. **Проверьте**, что проект компилируется
5. **Запустите скрипт проверки** еще раз

---

## 💡 Полезные команды

```bash
# Проверка дубликатов
python3 scripts/check_localization_duplicates.py

# Поиск конкретного ключа
grep -n '"key_name":' Core/Localization/LocalizationManager.swift

# Подсчет количества ключей в русском словаре
grep -c '":' Core/Localization/LocalizationManager.swift
```

---

## 📚 Дополнительные ресурсы

- [Swift Dictionary Documentation](https://docs.swift.org/swift-book/LanguageGuide/CollectionTypes.html#ID113)
- [Localization Best Practices](https://developer.apple.com/documentation/xcode/localizing-and-varying-text-with-a-string-catalog)

---

**Последнее обновление:** 2025-11-06  
**Статус:** ✅ Проблема исправлена, скрипт проверки добавлен



