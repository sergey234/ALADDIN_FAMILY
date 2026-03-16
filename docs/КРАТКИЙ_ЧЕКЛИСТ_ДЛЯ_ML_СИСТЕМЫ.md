# ✅ КРАТКИЙ ЧЕКЛИСТ ДЛЯ ML СИСТЕМЫ - BUILD 121

## 🎯 ГЛАВНАЯ ЗАДАЧА

**Деплой исправления:** `app/auth/auth.py` → `/opt/aladdin-backend/app/auth/auth.py`

---

## 📋 ЧТО УЖЕ СДЕЛАНО ✅

- ✅ Проблема найдена и исправлена локально
- ✅ Все файлы исправлены и протестированы
- ✅ Проект компилируется без ошибок
- ✅ Защита от ложного удаления токенов реализована

---

## ⏳ ЧТО НУЖНО СДЕЛАТЬ

### 1. ДЕПЛОЙ НА СЕРВЕР (КРИТИЧНО)

**Файл:** `app/auth/auth.py`  
**Путь на сервере:** `/opt/aladdin-backend/app/auth/auth.py`

**Команды:**
```bash
# Вариант 1: Через SCP
scp app/auth/auth.py root@149.154.65.180:/opt/aladdin-backend/app/auth/auth.py

# Вариант 2: Через SSH
ssh root@149.154.65.180
cd /opt/aladdin-backend/app/auth
cp auth.py auth.py.backup_$(date +%Y%m%d_%H%M%S)
# Загрузить файл через scp/sftp
python3 -m py_compile auth.py
systemctl restart aladdin-backend
```

### 2. ПРОВЕРКА

```bash
# Проверить синтаксис
python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py

# Проверить статус
systemctl status aladdin-backend

# Протестировать API
curl -H "Authorization: Bearer TOKEN" https://aladdin-ai.ru/api/family/stats
```

---

## 📊 КРИТЕРИИ УСПЕХА

- ✅ `/api/family/stats` возвращает `200 OK` (было: `401`)
- ✅ Device tokens работают корректно
- ✅ User tokens продолжают работать (обратная совместимость)

---

## 📁 ДОКУМЕНТАЦИЯ

- `docs/ПОЛНЫЙ_ПЛАН_ДЕЙСТВИЙ_ДЛЯ_ML_СИСТЕМЫ_BUILD_121.md` - полный план
- `docs/ДЕПЛОЙ_ЧЕРЕЗ_NGINX_SSL_SYSTEMD.md` - инструкции по деплою
- `docs/РУЧНОЙ_ДЕПЛОЙ_ИСПРАВЛЕНИЯ_401.md` - альтернативные методы

---

**Статус:** ✅ Готово к деплою
