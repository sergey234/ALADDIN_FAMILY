# ИНСТРУКЦИЯ: Работа с GitHub Actions Workflows для iOS

## 📋 ОГЛАВЛЕНИЕ
1. [Основные проблемы и их причины](#основные-проблемы)
2. [Структура workflow файлов](#структура-workflow-файлов)
3. [Критическое правило: лимит 21000 символов](#критическое-правило)
4. [Пошаговая инструкция по исправлению](#пошаговая-инструкция)
5. [Способы запуска workflow](#способы-запуска-workflow)
6. [Правильный процесс работы с workflows](#правильный-процесс)
7. [Чек-лист перед запуском](#чек-лист)

---

## 🔴 ОСНОВНЫЕ ПРОБЛЕМЫ

### Проблема 1: "Exceeded max expression length 21000"
**Причина:** GitHub Actions имеет жесткий лимит в 21000 символов на один блок `run:` в шаге workflow.

**Симптомы:**
- Ошибка: `(Line: X, Col: Y): Exceeded max expression length 21000`
- Workflow не запускается вообще
- GitHub показывает ошибку валидации YAML

**Решение:** Разбить длинный блок на несколько отдельных шагов.

### Проблема 2: Запускается не тот workflow
**Причина:** В проекте несколько workflow файлов, и легко запустить не тот.

**Симптомы:**
- Исправляете `check-secrets.yml`, а запускается `appstore.yml`
- Изменения не применяются
- Ошибки повторяются

**Решение:** Всегда проверяйте, какой workflow запускается, и исправляйте правильный файл.

### Проблема 3: Изменения не применяются
**Причина:** GitHub Actions запускает версию из репозитория, а не локальный файл.

**Симптомы:**
- Файл изменен локально, но workflow использует старую версию
- Ошибки не исчезают после исправления

**Решение:** Всегда коммитить и пушить изменения перед запуском workflow.

---

## 📁 СТРУКТУРА WORKFLOW ФАЙЛОВ

### ⚠️ КРИТИЧЕСКИ ВАЖНО: ОСНОВНОЙ WORKFLOW

**ОСНОВНОЙ WORKFLOW: `.github/workflows/check-secrets.yml`**

**Что это значит:**
- `check-secrets.yml` — **ЕДИНСТВЕННЫЙ** рабочий workflow для проверки секретов, профилей, сборки и загрузки в App Store
- Этот workflow используется для всех операций: проверка, сборка, загрузка
- **ВСЕ исправления делаются ТОЛЬКО в этом файле**

### Файлы в проекте:
1. **`.github/workflows/check-secrets.yml`** ⭐ **ОСНОВНОЙ** - проверка секретов, профилей, сборка и загрузка в App Store
2. **`.github/workflows/appstore.yml`** - **НЕ ИСПОЛЬЗУЕТСЯ**, можно игнорировать
3. Другие workflow файлы (ci.yml, deploy.yml и т.д.) - для других целей

### Правила работы:
- ✅ **РАБОТАТЬ ТОЛЬКО С `check-secrets.yml`**
- ❌ **НЕ трогать `appstore.yml`** (он не используется)
- ✅ Все исправления делаются **ТОЛЬКО в `check-secrets.yml`**
- ✅ При запуске workflow всегда использовать `check-secrets.yml`

### Как проверить какой workflow запустился:
```bash
# Проверить по номеру запуска
RUN_ID="19825343805"
curl -s -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/USER/REPO/actions/runs/$RUN_ID" | \
  python3 -c "import sys, json; r=json.load(sys.stdin); print(f'Workflow: {r[\"path\"]}')"
```

**Если запустился НЕ `check-secrets.yml` - это ошибка! Нужно запустить правильный workflow.**

---

## ⚠️ КРИТИЧЕСКОЕ ПРАВИЛО: ЛИМИТ 21000 СИМВОЛОВ

### Правило:
**Каждый блок `run:` в шаге workflow НЕ ДОЛЖЕН превышать 21000 символов.**

### Как проверить размер блока:
```bash
# Проверить размер блока "Setup Provisioning Profiles"
awk '/^    - name: Setup Provisioning Profiles/,/^    - name:/ {if(/^    - name:/ && !/Setup Provisioning Profiles/) exit; print}' .github/workflows/check-secrets.yml | wc -c
```

### Если блок превышает лимит:
**ОБЯЗАТЕЛЬНО разбить на несколько шагов!**

Пример разбиения:
- ❌ **Плохо:** Один шаг "Setup Provisioning Profiles" (42441 символов)
- ✅ **Хорошо:** 
  - "Decode App Profile" (1178 символов)
  - "Extract App Profile UUID" (2107 символов)
  - "Decode Extension Profile" (1238 символов)
  - "Extract Extension Profile UUID" (2211 символов)
  - "Verify Profiles" (1579 символов)

---

## 🔧 ПОШАГОВАЯ ИНСТРУКЦИЯ ПО ИСПРАВЛЕНИЮ

### Шаг 1: Определить проблемный блок
```bash
# Найти все шаги в workflow
grep "^    - name:" .github/workflows/check-secrets.yml

# Проверить размер каждого блока
for step in "Setup Provisioning Profiles" "Build Archive"; do
  size=$(awk -v step="$step" '/^    - name: '"$step"'/,/^    - name:/ {if(/^    - name:/ && !/'"$step"'/) exit; print}' .github/workflows/check-secrets.yml | wc -c)
  echo "$step: $size символов"
done
```

### Шаг 2: Разбить длинный блок
**Принцип разбиения:**
1. Логически разделить функциональность
2. Каждый новый шаг должен быть независимым
3. Использовать `$GITHUB_ENV` для передачи переменных между шагами

**Пример разбиения блока "Setup Provisioning Profiles":**

**Было (42441 символов):**
```yaml
- name: Setup Provisioning Profiles
  run: |
    # Весь код в одном блоке (42441 символов)
```

**Стало (5 шагов, каждый < 21000):**
```yaml
- name: Decode App Profile
  run: |
    # Декодирование app профиля (1178 символов)
    echo "APP_PROFILE_UUID=$UUID" >> $GITHUB_ENV

- name: Extract App Profile UUID
  run: |
    # Извлечение UUID (2107 символов)
    # Использует переменные из предыдущего шага

- name: Decode Extension Profile
  run: |
    # Декодирование extension профиля (1238 символов)

- name: Extract Extension Profile UUID
  run: |
    # Извлечение UUID extension (2211 символов)

- name: Verify Profiles
  env:
    APP_PROFILE_UUID: ${{ env.APP_PROFILE_UUID }}
    EXT_PROFILE_UUID: ${{ env.EXT_PROFILE_UUID }}
  run: |
    # Проверка профилей (1579 символов)
```

### Шаг 3: Проверить размеры всех блоков
```bash
# Проверить все блоки после разбиения
for step in "Decode App Profile" "Extract App Profile UUID" "Decode Extension Profile" "Extract Extension Profile UUID" "Verify Profiles"; do
  size=$(awk -v step="$step" '/^    - name: '"$step"'/,/^    - name:/ {if(/^    - name:/ && !/'"$step"'/) exit; print}' .github/workflows/check-secrets.yml | wc -c)
  if [ "$size" -gt 21000 ]; then
    echo "❌ $step: $size символов (ПРЕВЫШЕН ЛИМИТ!)"
  else
    echo "✅ $step: $size символов"
  fi
done
```

### Шаг 4: Применить изменения ТОЛЬКО к основному workflow
**ВАЖНО:** Работать ТОЛЬКО с `check-secrets.yml` (основной workflow)!

```bash
# Проверить ТОЛЬКО основной файл
echo "Проверяю .github/workflows/check-secrets.yml"
awk '/^    - name: Setup Provisioning Profiles/,/^    - name:/ {if(/^    - name:/ && !/Setup Provisioning Profiles/) exit; print}' .github/workflows/check-secrets.yml | wc -c

# НЕ проверять appstore.yml - он не используется!
```

### Шаг 5: Закоммитить и запушить изменения
```bash
# Закоммитить
git add .github/workflows/
git commit -m "fix: разбит блок на несколько шагов для избежания лимита 21000 символов"

# Запушить
git push origin master
```

### Шаг 6: Запустить ОСНОВНОЙ workflow
**ВАЖНО:** Всегда запускать ТОЛЬКО `check-secrets.yml`!

#### Способ 1: Через GitHub API (командная строка)

**Полный скрипт запуска с проверкой:**

```bash
# Настройки
GITHUB_TOKEN="ваш_токен_github"
REPO="sergey234/ALADDIN_FAMILY"  # формат: USER/REPO
BRANCH="master"
WORKFLOW="check-secrets.yml"  # ВСЕГДА основной workflow

# Шаг 1: Запустить workflow
echo "🚀 Запускаю $WORKFLOW..."
response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "204" ]; then
  echo "✅ Workflow успешно запущен!"
else
  echo "❌ Ошибка при запуске (HTTP $http_code)"
  echo "$body"
  exit 1
fi

# Шаг 2: Подождать несколько секунд для создания запуска
echo "⏳ Жду 5 секунд для создания запуска..."
sleep 5

# Шаг 3: Получить номер запуска и URL
echo ""
echo "📊 Получаю информацию о запуске..."
run_info=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/runs?workflow_id=$WORKFLOW&per_page=1")

run_number=$(echo "$run_info" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['workflow_runs'][0]['run_number'] if data.get('workflow_runs') else 'N/A')")
run_url=$(echo "$run_info" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['workflow_runs'][0]['html_url'] if data.get('workflow_runs') else 'N/A')")
run_status=$(echo "$run_info" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['workflow_runs'][0]['status'] if data.get('workflow_runs') else 'N/A')")

echo ""
echo "📊 Номер запуска: #$run_number"
echo "🔗 URL: $run_url"
echo "📋 Статус: $run_status"

# Шаг 4: Проверить что запустился правильный workflow
echo ""
echo "🔍 Проверяю что запустился правильный workflow..."
workflow_path=$(echo "$run_info" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['workflow_runs'][0]['path'] if data.get('workflow_runs') else 'N/A')")
echo "   Workflow файл: $workflow_path"

if [[ "$workflow_path" == *"check-secrets.yml"* ]]; then
  echo "   ✅ Запустился правильный workflow!"
else
  echo "   ❌ ОШИБКА: Запустился НЕ правильный workflow!"
  echo "   Ожидался: check-secrets.yml"
  echo "   Получен: $workflow_path"
fi
```

**Упрощенная версия (только запуск и номер):**

```bash
GITHUB_TOKEN="ваш_токен"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="check-secrets.yml"

# Запустить
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d '{"ref":"master"}'

# Получить номер запуска
sleep 5
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/runs?workflow_id=$WORKFLOW&per_page=1" | \
  python3 -c "import sys, json; r=json.load(sys.stdin)['workflow_runs'][0]; print(f'#{r[\"run_number\"]}'); print(r['html_url'])"
```

#### Способ 2: Через GitHub UI (веб-интерфейс)

1. Открыть репозиторий на GitHub
2. Перейти в раздел **Actions**
3. В левом меню выбрать **`check-secrets.yml`** (основной workflow)
4. Нажать кнопку **"Run workflow"**
5. Выбрать ветку **`master`**
6. Нажать **"Run workflow"**

**Проверка:**
- После запуска появится новый запуск с номером (например, #164)
- Можно открыть запуск и посмотреть логи

#### Способ 3: Через GitHub CLI (gh)

```bash
# Установить GitHub CLI (если не установлен)
# brew install gh

# Авторизоваться
gh auth login

# Запустить workflow
gh workflow run check-secrets.yml --ref master

# Посмотреть статус
gh run list --workflow=check-secrets.yml --limit 1
```

#### Проверка запущенного workflow

**Получить информацию о конкретном запуске:**

```bash
RUN_ID="19825343805"  # ID запуска (можно взять из URL)
GITHUB_TOKEN="ваш_токен"
REPO="sergey234/ALADDIN_FAMILY"

# Получить полную информацию
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID" | \
  python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f'Номер: #{r[\"run_number\"]}')
print(f'URL: {r[\"html_url\"]}')
print(f'Статус: {r[\"status\"]}')
print(f'Workflow: {r[\"path\"]}')
print(f'Коммит: {r[\"head_sha\"][:8]}')
print(f'Ветка: {r[\"head_branch\"]}')
"
```

**Проверить последние запуски:**

```bash
WORKFLOW="check-secrets.yml"
GITHUB_TOKEN="ваш_токен"
REPO="sergey234/ALADDIN_FAMILY"

# Получить последние 5 запусков
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/runs?workflow_id=$WORKFLOW&per_page=5" | \
  python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f'#{r[\"run_number\"]} - {r[\"status\"]} - {r[\"created_at\"]} - {r[\"html_url\"]}')
"
```

#### Открыть страницу запуска в браузере

**macOS (через команду open):**

```bash
# После получения URL
run_url="https://github.com/sergey234/ALADDIN_FAMILY/actions/runs/19825343805"
open -a "Google Chrome" "$run_url"
```

**Linux:**

```bash
xdg-open "$run_url"
```

**Windows:**

```bash
start "$run_url"
```

#### Важные моменты при запуске:

1. **Всегда проверяйте токен:**
   - Токен должен иметь права `repo` и `workflow`
   - Токен должен быть действительным

2. **Проверяйте ветку:**
   - Убедитесь что используете правильную ветку (обычно `master`)

3. **Проверяйте workflow файл:**
   - Всегда запускайте `check-secrets.yml` (основной)
   - Проверяйте что запустился правильный workflow

4. **Ждите создания запуска:**
   - После запуска через API нужно подождать 3-5 секунд
   - Только потом запрашивать информацию о запуске

5. **Проверяйте статус:**
   - `queued` - в очереди
   - `in_progress` - выполняется
   - `completed` - завершен
   - `failed` - ошибка

---

## 🚀 СПОСОБЫ ЗАПУСКА WORKFLOW

### Быстрый старт

**Самый простой способ (одна команда):**

```bash
GITHUB_TOKEN="ваш_токен"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="check-secrets.yml"

curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d '{"ref":"master"}' && \
sleep 5 && \
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/actions/runs?workflow_id=$WORKFLOW&per_page=1" | \
  python3 -c "import sys, json; r=json.load(sys.stdin)['workflow_runs'][0]; print(f'#{r[\"run_number\"]}'); print(r['html_url'])"
```

Эта команда:
1. Запускает workflow
2. Ждет 5 секунд
3. Выводит номер запуска и URL

---

## ✅ ПРАВИЛЬНЫЙ ПРОЦЕСС РАБОТЫ С WORKFLOWS

### 1. Перед началом работы:
```bash
# Проверить текущий статус
git status

# Убедиться что на правильной ветке
git branch

# Создать бэкап перед изменениями
mkdir -p backup_workflows
cp .github/workflows/check-secrets.yml backup_workflows/check-secrets.yml.backup_$(date +%Y%m%d_%H%M%S)
cp .github/workflows/appstore.yml backup_workflows/appstore.yml.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. При исправлении ошибок:
1. **Убедиться что работаете с ОСНОВНЫМ workflow:**
   - ⚠️ **ВСЕГДА работать ТОЛЬКО с `check-secrets.yml`**
   - Проверить какой workflow запускается (по номеру запуска)
   - Если запустился НЕ `check-secrets.yml` - это ошибка!

2. **Найти проблемный блок:**
   - Проверить размеры всех блоков в `check-secrets.yml`
   - Найти блоки > 21000 символов

3. **Разбить блок:**
   - Логически разделить функциональность
   - Создать несколько шагов
   - Использовать `$GITHUB_ENV` для передачи переменных

4. **Проверить размеры:**
   - Убедиться что все блоки < 21000
   - Проверить синтаксис YAML

5. **Применить изменения:**
   - ✅ Исправлять **ТОЛЬКО `check-secrets.yml`**
   - ❌ **НЕ трогать `appstore.yml`** (он не используется)

6. **Закоммитить и запушить:**
   - `git add .github/workflows/check-secrets.yml`
   - `git commit -m "описание изменений"`
   - `git push origin master`

7. **Запустить ОСНОВНОЙ workflow:**
   - Всегда запускать `check-secrets.yml`
   - Проверить номер запуска
   - Убедиться что запустился правильный workflow

### 3. После исправления:
```bash
# Проверить что изменения применены
git log -1 --oneline -- .github/workflows/

# Проверить что workflow запустился
# (проверить номер запуска в GitHub UI)
```

---

## 📝 ЧЕК-ЛИСТ ПЕРЕД ЗАПУСКОМ

### Перед каждым изменением workflow:
- [ ] Создан бэкап файла `check-secrets.yml`
- [ ] ⚠️ Убедился что работаю ТОЛЬКО с `check-secrets.yml` (основной)
- [ ] Проверены размеры всех блоков `run:` в `check-secrets.yml`
- [ ] Все блоки < 21000 символов
- [ ] Изменения применены ТОЛЬКО к `check-secrets.yml`
- [ ] Проверен синтаксис YAML (нет ошибок линтера)
- [ ] Изменения закоммичены и запушены
- [ ] Запущен workflow `check-secrets.yml` (основной)
- [ ] Проверен номер запуска
- [ ] Убедился что запустился правильный workflow (`check-secrets.yml`)

### При разбиении блока:
- [ ] Каждый новый шаг логически завершен
- [ ] Переменные передаются через `$GITHUB_ENV`
- [ ] Используется `env:` для чтения переменных из предыдущих шагов
- [ ] Каждый блок < 21000 символов
- [ ] Порядок шагов логичен

---

## 🚨 ЧАСТЫЕ ОШИБКИ И КАК ИХ ИЗБЕЖАТЬ

### Ошибка 1: "Exceeded max expression length"
**Причина:** Блок слишком длинный
**Решение:** Разбить на несколько шагов

### Ошибка 2: Изменения не применяются
**Причина:** Не закоммичены изменения
**Решение:** Всегда коммитить и пушить перед запуском

### Ошибка 3: Исправляю один файл, а запускается другой
**Причина:** Не проверили какой workflow запускается
**Решение:** 
- Всегда проверять номер запуска и какой файл используется
- **ВСЕГДА запускать ТОЛЬКО `check-secrets.yml`**
- Если запустился другой workflow - это ошибка!

### Ошибка 4: Исправил workflow, но ошибка осталась
**Причина:** Исправили не тот файл или не закоммитили изменения
**Решение:** 
- Исправлять **ТОЛЬКО `check-secrets.yml`** (основной)
- Всегда коммитить и пушить изменения
- Проверять что запустился правильный workflow

---

## 📊 ПРИМЕРЫ КОМАНД ДЛЯ ПРОВЕРКИ

### Проверить размеры всех блоков:
```bash
# Для одного файла
for step in $(grep "^    - name:" .github/workflows/check-secrets.yml | sed 's/.*name: //'); do
  size=$(awk -v step="$step" '/^    - name: '"$step"'/,/^    - name:/ {if(/^    - name:/ && !/'"$step"'/) exit; print}' .github/workflows/check-secrets.yml | wc -c)
  echo "$step: $size символов"
done
```

### Проверить какой workflow запустился:
```bash
RUN_ID="19825343805"  # номер запуска
curl -s -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/USER/REPO/actions/runs/$RUN_ID" | \
  python3 -c "import sys, json; r=json.load(sys.stdin); print(f'Workflow: {r[\"path\"]}'); print(f'Коммит: {r[\"head_sha\"][:8]}')"
```

### Сравнить локальный и удаленный файл:
```bash
git fetch origin
git diff HEAD origin/master -- .github/workflows/check-secrets.yml
```

---

## 🎯 ИТОГОВЫЕ РЕКОМЕНДАЦИИ

1. ⚠️ **ВСЕГДА работать ТОЛЬКО с `check-secrets.yml`** (основной workflow)
2. **Всегда проверяйте размеры блоков** перед коммитом
3. **Создавайте бэкапы** перед изменениями
4. **Коммитьте и пушите** перед запуском workflow
5. **Всегда запускать `check-secrets.yml`** (основной workflow)
6. **Проверяйте какой workflow запустился** по номеру запуска
7. **Используйте `$GITHUB_ENV`** для передачи переменных между шагами
8. **Разбивайте блоки логически**, не просто механически
9. ❌ **НЕ трогать `appstore.yml`** - он не используется

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- [GitHub Actions Limits](https://docs.github.com/en/actions/learn-github-actions/usage-limits-billing-and-administration)
- [GitHub Actions Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Environment Variables](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsenv)

---

**Дата создания:** 2025-12-01  
**Последнее обновление:** 2025-12-01

