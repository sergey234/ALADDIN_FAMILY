# 🔍 ПОЛНЫЙ ПОИСК ENDPOINT'ОВ НА СЕРВЕРЕ

**Дата:** 2026-02-11  
**Цель:** Найти все endpoint'ы для создания семьи и авторизации по recovery code

---

## 🔍 РЕЗУЛЬТАТЫ ПОИСКА

### **1. Endpoint `/api/family/create`**

**Найдено:**
- ✅ Функция `create_family` существует в `security/family/family_registration.py`
- ❌ FastAPI endpoint НЕ найден в `app/routers/family.py`
- ❌ FastAPI endpoint НЕ найден в других роутерах

**Проверенные места:**
- `app/routers/family.py` - только `/stats`
- `security/family/family_registration.py` - функция есть, но не endpoint
- `security/family/family_integration_layer.py` - проверяется
- `security/family/register_family_system_in_sfm.py` - проверяется
- `security/api/routers/` - проверяется

---

### **2. Endpoint `/api/auth/login-by-recovery-code`**

**Найдено:**
- ❌ НЕ найден в `app/routers/auth_router.py`
- ❌ НЕ найден в других роутерах

**Проверенные места:**
- `app/routers/auth_router.py` - только `/login`, `/register`, `/refresh`, `/logout`
- Другие роутеры - проверяются

---

## 📋 ЧТО НАЙДЕНО

### **В app/routers/family.py:**
- ✅ `GET /api/family/stats` - работает

### **В app/routers/auth_router.py:**
- ✅ `POST /api/auth/login` - работает
- ✅ `POST /api/auth/register` - работает
- ✅ `POST /api/auth/refresh` - работает
- ✅ `POST /api/auth/logout` - работает

### **В security/family/:**
- ✅ Функция `create_family()` существует
- ❌ FastAPI endpoint не подключен

---

## 🎯 ВЫВОДЫ

**Проблема:**
- Функции существуют, но FastAPI endpoint'ы не подключены

**Решение:**
- Нужно добавить endpoint'ы в роутеры или подключить существующие

---

**Последнее обновление:** 2026-02-11  
**Статус:** 🔍 **ПОИСК В ПРОЦЕССЕ**
