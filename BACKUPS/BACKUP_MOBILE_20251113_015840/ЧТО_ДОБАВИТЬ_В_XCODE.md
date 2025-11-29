# 📋 ЧТО ДОБАВИТЬ В XCODE ПРОЕКТ

## ✅ ФАЙЛЫ ДЛЯ ДОБАВЛЕНИЯ В ПРОЕКТ:

### 1️⃣ **CollapsibleSection.swift**
**Путь:** `Shared/Components/CollapsibleSection.swift`

**Что это:** Компонент для раздвигающихся секций (accordion)

**Действие:** Добавить файл в Xcode проект, выбрать target "ALADDIN"

---

### 2️⃣ **RewardModels.swift** (УЖЕ ЕСТЬ, но нужно проверить наличие новых моделей)
**Путь:** `Shared/Models/RewardModels.swift`

**Что это:** Модели данных для геймификации:
- `EarningWay` - способы заработка единорогов
- `PunishmentReason` - причины наказания

**Действие:** Проверить, что файл добавлен в target "ALADDIN". Если нет - добавить.

---

## 📍 ДИРЕКТОРИИ (для справки):

1. **Shared/Components/** - компоненты UI
2. **Shared/Models/** - модели данных

---

## ✅ КАК ДОБАВИТЬ В XCODE:

1. Откройте проект в Xcode
2. Найдите папку `Shared/Components/` в навигаторе проекта
3. Правой кнопкой → "Add Files to ALADDIN..."
4. Выберите файл `CollapsibleSection.swift`
5. Убедитесь, что стоит галочка на target "ALADDIN"
6. Нажмите "Add"

**Повторите для `Shared/Models/RewardModels.swift` (если его нет в проекте)**

---

## 🔍 ПРОВЕРКА:

После добавления файлов в Xcode:
- `CollapsibleSection` должен быть виден в коде
- `EarningWay` и `PunishmentReason` должны быть доступны

**Если файлы уже есть в проекте, но ошибка остается:**
- Clean Build Folder (⇧⌘K)
- Пересоберите проект (⌘B)

