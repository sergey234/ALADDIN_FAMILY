# 🔑 КАК ПОЛУЧИТЬ GITHUB ТОКЕН ДЛЯ ЗАПУСКА WORKFLOW

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Откройте настройки токенов
```
https://github.com/settings/tokens
```

Или:
1. Зайдите на GitHub
2. Нажмите на ваш аватар (правый верхний угол)
3. Выберите **Settings**
4. В левом меню найдите **Developer settings**
5. Выберите **Personal access tokens** → **Tokens (classic)**

### Шаг 2: Создайте новый токен

1. Нажмите **"Generate new token"** → **"Generate new token (classic)"**

2. **Название токена:** (любое, например "Workflow Launcher")

3. **Срок действия:** Выберите срок (например, 90 дней или No expiration)

4. **Права (scopes):** Выберите:
   - ✅ **`workflow`** - для запуска workflows
   
   (Можно также выбрать `repo` для полного доступа к репозиториям)

5. Нажмите **"Generate token"** внизу страницы

### Шаг 3: Скопируйте токен

⚠️ **ВАЖНО:** Токен показывается только один раз! Скопируйте его сразу.

Токен будет выглядеть примерно так:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Шаг 4: Вставьте токен в скрипт

1. Откройте файл `запустить_workflow_api.sh`

2. Найдите строку:
   ```bash
   GITHUB_TOKEN="YOUR_TOKEN_HERE"
   ```

3. Замените `YOUR_TOKEN_HERE` на ваш токен:
   ```bash
   GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

4. Сохраните файл

### Шаг 5: Запустите скрипт

```bash
./запустить_workflow_api.sh
```

---

## 🔒 БЕЗОПАСНОСТЬ

⚠️ **НЕ коммитьте токен в git!**

Токен должен оставаться только в локальном файле. Если случайно закоммитили:
1. Удалите токен из GitHub (настройки токенов)
2. Создайте новый токен
3. Добавьте файл в `.gitignore`:
   ```bash
   echo "запустить_workflow_api.sh" >> .gitignore
   ```

---

## ✅ ПРОВЕРКА

После запуска скрипта вы должны увидеть:
```
✅ Workflow успешно запущен!

Проверьте статус:
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

---

## 🎯 БЫСТРАЯ ССЫЛКА

**Создать токен:**
```
https://github.com/settings/tokens/new
```

**Выберите права:** `workflow`

