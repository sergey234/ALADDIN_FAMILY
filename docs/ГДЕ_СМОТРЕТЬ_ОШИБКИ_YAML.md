# 📍 ГДЕ СМОТРЕТЬ ОШИБКИ YAML В GITHUB

## 🔍 МЕСТА, ГДЕ GITHUB ПОКАЗЫВАЕТ ОШИБКИ YAML

### 1. **На странице файла workflow (самое очевидное место)**

**Ссылка:**
```
https://github.com/sergey234/ALADDIN_FAMILY/blob/master/.github/workflows/appstore.yml
```

**Что искать:**
- 🔴 **Желтая/красная полоса вверху страницы** с текстом типа:
  - "This workflow file has syntax errors"
  - "Invalid workflow file"
  - "YAML syntax error"
- 🔴 **Подсветка строки с ошибкой** - GitHub подсветит проблемную строку
- 🔴 **Сообщение об ошибке** прямо в коде файла

**Как проверить:**
1. Откройте ссылку выше
2. Посмотрите вверху страницы - есть ли предупреждение?
3. Прокрутите файл - GitHub подсветит строки с ошибками красным

---

### 2. **В разделе Actions (если workflow пытался запуститься)**

**Ссылка:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions
```

**Что искать:**
- 🔴 **Красный крестик** рядом с названием workflow
- 🔴 **Сообщение "Workflow file is invalid"** или "Invalid workflow syntax"
- 🔴 **Желтый треугольник** с предупреждением

**Как проверить:**
1. Откройте `Actions`
2. Посмотрите на список workflows слева
3. Если `appstore.yml` есть в списке, но с красным крестиком - откройте его
4. Внутри будет детальное описание ошибки

---

### 3. **В настройках репозитория (Settings → Actions)**

**Ссылка:**
```
https://github.com/sergey234/ALADDIN_FAMILY/settings/actions
```

**Что искать:**
- 🔴 **Секция "Workflow errors"** или "Invalid workflows"
- 🔴 **Список workflows с ошибками**

**Как проверить:**
1. Зайдите в `Settings` → `Actions`
2. Прокрутите вниз - может быть секция с ошибками
3. Или проверьте вкладку "Workflow permissions" - там могут быть предупреждения

---

### 4. **При попытке запустить workflow вручную**

**Что искать:**
- Если нажимаете "Run workflow" и появляется ошибка:
  - 🔴 "This workflow file has errors"
  - 🔴 "Invalid workflow syntax"
  - 🔴 "Cannot run workflow due to errors"

**Как проверить:**
1. Зайдите в `Actions` → выберите workflow
2. Нажмите "Run workflow"
3. Если есть ошибка - GitHub покажет её сразу

---

### 5. **В логах последнего запуска (если workflow запускался)**

**Ссылка:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

**Что искать:**
- 🔴 **Красный статус** последнего запуска
- 🔴 **Ошибка в шаге "Validate workflow"** или "Parse workflow"
- 🔴 **Детальные логи** с указанием строки и столбца ошибки

**Как проверить:**
1. Откройте список запусков workflow
2. Найдите последний запуск (даже если он упал)
3. Откройте его - там будут детальные логи

---

## 🎯 БЫСТРАЯ ПРОВЕРКА (ПОШАГОВО)

### Шаг 1: Откройте файл напрямую
```
https://github.com/sergey234/ALADDIN_FAMILY/blob/master/.github/workflows/appstore.yml
```

**Проверьте:**
- ✅ Файл открывается?
- ✅ Есть ли желтая/красная полоса вверху?
- ✅ Есть ли подсветка ошибок в коде?

### Шаг 2: Проверьте Actions
```
https://github.com/sergey234/ALADDIN_FAMILY/actions
```

**Проверьте:**
- ✅ Виден ли workflow "Build and Upload to App Store" в списке?
- ✅ Есть ли красный крестик или предупреждение?
- ✅ Есть ли кнопка "Run workflow"?

### Шаг 3: Если workflow виден, но с ошибкой
1. Нажмите на workflow
2. Откройте последний запуск (если есть)
3. Посмотрите логи - там будет детальное описание ошибки

---

## 📋 ТИПИЧНЫЕ ОШИБКИ YAML В GITHUB

### Ошибка 1: "Invalid YAML syntax"
**Где видна:** Вверху страницы файла, в Actions
**Причина:** Неправильный синтаксис YAML (отступы, кавычки, скобки)

### Ошибка 2: "Invalid workflow file"
**Где видна:** В Actions, при попытке запуска
**Причина:** Неправильная структура workflow (нет `on:`, `jobs:`, и т.д.)

### Ошибка 3: "Workflow file is too large"
**Где видна:** В Actions, при попытке запуска
**Причина:** Файл превышает лимит GitHub (обычно 1MB)

### Ошибка 4: "Invalid trigger syntax"
**Где видна:** В Actions, в логах запуска
**Причина:** Неправильный формат триггеров (`on:` секция)

---

## 🔧 КАК ИСПРАВИТЬ ОШИБКИ

1. **Если ошибка в файле:**
   - GitHub покажет строку и столбец ошибки
   - Исправьте ошибку локально
   - Сделайте commit и push

2. **Если ошибка не видна:**
   - Проверьте файл через YAML валидатор локально
   - Используйте `yamllint` или онлайн валидатор

3. **Если файл слишком большой:**
   - Разделите workflow на несколько файлов
   - Используйте `workflow_call` для связи

---

## 🎯 ПРЯМЫЕ ССЫЛКИ ДЛЯ ПРОВЕРКИ

1. **Файл workflow:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/blob/master/.github/workflows/appstore.yml
   ```

2. **Все workflows:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions
   ```

3. **Конкретный workflow:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
   ```

4. **Настройки Actions:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/settings/actions
   ```

---

## ✅ ЧЕКЛИСТ ПРОВЕРКИ

- [ ] Открыл файл `.github/workflows/appstore.yml` в GitHub
- [ ] Проверил, нет ли желтой/красной полосы вверху
- [ ] Проверил, нет ли подсветки ошибок в коде
- [ ] Открыл раздел `Actions`
- [ ] Проверил, виден ли workflow в списке
- [ ] Проверил, нет ли красного крестика или предупреждения
- [ ] Если workflow виден - попробовал нажать "Run workflow"
- [ ] Если есть ошибка - прочитал детальное описание

