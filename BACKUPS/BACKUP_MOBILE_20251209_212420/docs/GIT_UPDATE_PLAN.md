# 📋 ПЛАН ОБНОВЛЕНИЯ GIT: Что добавить и что исключить

**Дата:** 27 ноября 2025  
**Сравнение с бэкапом:** BACKUP_MOBILE_20251126_005838

---

## ✅ ЧТО БЫЛО В БЭКАПЕ (26 ноября)

В бэкапе `BACKUP_MOBILE_20251126_005838` были сохранены:
- ✅ Весь код приложения (Screens, Core, Components, ViewModels)
- ✅ Xcode проект (ALADDIN.xcodeproj)
- ✅ Assets и ресурсы
- ✅ Документация (docs/)
- ✅ Тесты

**НО НЕ были включены:**
- ❌ Backup файлы проекта (project.pbxproj.backup_*)
- ❌ User-specific файлы (xcuserdata/)
- ❌ Workspace user state
- ❌ .DS_Store файлы

---

## 🎯 ЧТО ДОБАВИТЬ В GIT СЕЙЧАС

### **✅ НОВЫЕ ФАЙЛЫ (важно для App Store):**

1. **`.github/workflows/appstore.yml`** ⭐
   - Workflow для автоматической сборки и загрузки в App Store
   - **ДОБАВИТЬ**

2. **`ExportOptions.plist`** (обновлённый)
   - Обновлён с Team ID `6CJVBBUGSN`
   - **ДОБАВИТЬ**

3. **Документация:**
   - `docs/GITHUB_ACTIONS_APP_STORE_SETUP.md`
   - `docs/GITHUB_SETUP_STEP_BY_STEP.md`
   - `docs/QUICK_START_APP_STORE.md`
   - **ДОБАВИТЬ**

---

## ❌ ЧТО НЕ ДОБАВЛЯТЬ В GIT

### **Backup файлы проекта:**
- ❌ `ALADDIN.xcodeproj/project.pbxproj.backup_20251102_032139`
- ❌ `ALADDIN.xcodeproj/project.pbxproj.backup_before_restore`
- ❌ `ALADDIN.xcodeproj/project.pbxproj.backup_tmp`
- ❌ `ALADDIN.xcodeproj/project.pbxproj.broken_20251111`

**Причина:** Это временные backup файлы, не нужны в репозитории.

---

### **User-specific файлы:**
- ❌ `ALADDIN.xcodeproj/project.xcworkspace/xcuserdata/`
- ❌ `ALADDIN.xcodeproj/xcuserdata/`
- ❌ `ALADDIN.xcodeproj/project.xcworkspace/contents.xcworkspacedata` (если содержит user-specific данные)

**Причина:** Эти файлы содержат персональные настройки Xcode, не должны быть в репозитории.

---

### **Системные файлы:**
- ❌ `.DS_Store`
- ❌ Любые другие временные файлы

---

## 📝 КОМАНДЫ ДЛЯ ОБНОВЛЕНИЯ

### **ШАГ 1: Исключить ненужные файлы**

```bash
# Убрать backup файлы из staging
git reset HEAD ALADDIN.xcodeproj/project.pbxproj.backup_*

# Убрать user-specific файлы из staging
git reset HEAD ALADDIN.xcodeproj/project.xcworkspace/xcuserdata/
git reset HEAD ALADDIN.xcodeproj/xcuserdata/

# Убрать .DS_Store
git reset HEAD .DS_Store
```

---

### **ШАГ 2: Добавить только нужные файлы**

```bash
# Добавить workflow для App Store
git add .github/workflows/appstore.yml

# Добавить обновлённый ExportOptions.plist
git add ExportOptions.plist

# Добавить документацию
git add docs/GITHUB_ACTIONS_APP_STORE_SETUP.md
git add docs/GITHUB_SETUP_STEP_BY_STEP.md
git add docs/QUICK_START_APP_STORE.md

# Добавить изменения в project.pbxproj (если они нужны)
# Но НЕ backup файлы!
git add ALADDIN.xcodeproj/project.pbxproj
```

---

### **ШАГ 3: Закоммитить и запушить**

```bash
# Закоммитить
git commit -m "Add GitHub Actions workflow for App Store upload

- Add .github/workflows/appstore.yml for automated build and upload
- Update ExportOptions.plist with Team ID 6CJVBBUGSN
- Add documentation for GitHub Actions setup"

# Запушить
git push origin master
```

---

## ✅ ИТОГОВЫЙ СПИСОК ФАЙЛОВ ДЛЯ КОММИТА

```
✅ .github/workflows/appstore.yml
✅ ExportOptions.plist
✅ docs/GITHUB_ACTIONS_APP_STORE_SETUP.md
✅ docs/GITHUB_SETUP_STEP_BY_STEP.md
✅ docs/QUICK_START_APP_STORE.md
✅ ALADDIN.xcodeproj/project.pbxproj (только если есть важные изменения)
```

---

## ⚠️ ВАЖНО

**НЕ коммитить:**
- Backup файлы проекта
- User-specific файлы Xcode
- .DS_Store
- Временные файлы

**Эти файлы должны быть в `.gitignore`:**

```gitignore
# Xcode
*.pbxproj.backup*
*.xcuserstate
xcuserdata/
.DS_Store
```

---

## 🎯 РЕЗУЛЬТАТ

После выполнения этих шагов:
- ✅ Workflow для App Store будет в репозитории
- ✅ ExportOptions.plist обновлён
- ✅ Документация добавлена
- ✅ Ненужные файлы исключены

**Готово к использованию!** 🚀

