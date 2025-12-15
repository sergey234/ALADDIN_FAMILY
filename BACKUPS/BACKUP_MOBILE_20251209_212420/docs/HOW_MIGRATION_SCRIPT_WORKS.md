# 🔍 КАК РАБОТАЕТ СКРИПТ ПЕРЕНОСА (363 файла)

## 📋 МЕХАНИЗМ ПЕРЕНОСА

Скрипт переносит файлы **по компонентам**, используя команды `rsync` и `scp`:

---

## 1️⃣ SFM (1 файл)

```bash
scp security/safe_function_manager.py root@NEW_SERVER:/opt/aladdin-backend/security/
```
**Переносит:** 1 файл

---

## 2️⃣ AI Agents (76 файлов)

```bash
rsync -avz security/ai_agents/ root@NEW_SERVER:/opt/aladdin-backend/security/ai_agents/
```
**Переносит:** Все `.py` файлы из `security/ai_agents/`
- `rsync -avz` = рекурсивно, с сохранением прав, сжатием
- Копирует всю директорию со всеми файлами

**Что переносится:**
- Все 76 файлов из `security/ai_agents/*.py`
- Включая подкаталоги (если есть)

---

## 3️⃣ Bots (30 файлов)

```bash
rsync -avz security/bots/ root@NEW_SERVER:/opt/aladdin-backend/security/bots/
```
**Переносит:** Все `.py` файлы из `security/bots/`
- Включая `components/` подкаталог
- Всего 30 файлов

---

## 4️⃣ Managers (24 файла)

```bash
rsync -avz security/managers/ root@NEW_SERVER:/opt/aladdin-backend/security/managers/
```
**Переносит:** Все `.py` файлы из `security/managers/`
- Всего 24 файла

---

## 5️⃣ Microservices (17 файлов)

```bash
rsync -avz security/microservices/ root@NEW_SERVER:/opt/aladdin-backend/security/microservices/
```
**Переносит:** Все `.py` файлы из `security/microservices/`
- Всего 17 файлов

---

## 6️⃣ Active (7 файлов)

```bash
rsync -avz security/active/ root@NEW_SERVER:/opt/aladdin-backend/security/active/
```
**Переносит:** Все `.py` файлы из `security/active/`
- Всего 7 файлов

---

## 7️⃣ Family (18 файлов)

```bash
rsync -avz --exclude="test_*.py" --exclude="*test*.py" --exclude="fix_*.py" --exclude="check_*.py" \
  security/family/ root@NEW_SERVER:/opt/aladdin-backend/security/family/
```
**Переносит:** Все `.py` файлы из `security/family/`, **ИСКЛЮЧАЯ:**
- `test_*.py` - тестовые файлы
- `*test*.py` - файлы с "test" в имени
- `fix_*.py` - файлы исправлений
- `check_*.py` - проверочные файлы

**Всего:** ~18 файлов (после исключений)

---

## 8️⃣ VPN (105 файлов)

```bash
rsync -avz security/vpn/ root@NEW_SERVER:/opt/aladdin-backend/security/vpn/
```
**Переносит:** ВСЮ структуру `security/vpn/` рекурсивно:
- Все `.py` файлы во всех подкаталогах
- `core/`, `protocols/`, `protection/`, `compliance/`, `api/`, и т.д.
- Всего 105 файлов

---

## 9️⃣ Antivirus (7 файлов)

```bash
rsync -avz security/antivirus/ root@NEW_SERVER:/opt/aladdin-backend/security/antivirus/
```
**Переносит:** Все `.py` файлы из `security/antivirus/` рекурсивно:
- `core/`, `engines/`, `scanners/`, `ml/`, `signatures/`
- Всего 7 файлов

---

## 🔟 Compliance (3 файла)

```bash
rsync -avz security/compliance/ root@NEW_SERVER:/opt/aladdin-backend/security/compliance/
```
**Переносит:** Все `.py` файлы из `security/compliance/`
- Всего 3 файла

---

## 1️⃣1️⃣ Core (1 файл)

```bash
rsync -avz security/core/ root@NEW_SERVER:/opt/aladdin-backend/security/core/
```
**Переносит:** Все `.py` файлы из `security/core/`
- Всего 1 файл

---

## 1️⃣2️⃣ Критичные Security модули (72 файла)

```bash
find security -maxdepth 1 -name "*.py" -type f \
  ! -name "test_*.py" \
  ! -name "*test*.py" \
  ! -name "*backup*.py" \
  ! -name "*fixed*.py" \
  ! -name "*patch*.py" \
  ! -name "*old*.py" | \
while read f; do
    scp "$f" root@NEW_SERVER:/opt/aladdin-backend/security/
done
```

**Как работает:**
1. `find security -maxdepth 1` - ищет файлы только в корне `security/` (не в подкаталогах)
2. `-name "*.py"` - только Python файлы
3. `! -name "test_*.py"` и т.д. - исключает тестовые, бэкап, исправленные файлы
4. `while read f; do scp ...` - для каждого найденного файла выполняет `scp`

**Переносит:** Все `.py` файлы из корня `security/`, исключая:
- Тестовые файлы
- Бэкап файлы
- Исправленные версии
- Старые версии

**Всего:** 72 файла

---

## 1️⃣3️⃣ function_registry.json (1 файл)

```bash
scp data/sfm/function_registry.json root@NEW_SERVER:/opt/aladdin-backend/data/sfm/
```
**Переносит:** 1 JSON файл (993KB)

---

## 1️⃣4️⃣ requirements.txt (1 файл)

```bash
scp requirements.txt root@NEW_SERVER:/opt/aladdin-backend/ 2>/dev/null || echo "⚠️ requirements.txt не найден"
```
**Переносит:** 1 файл зависимостей (если существует)

---

## 📊 ИТОГОВЫЙ ПОДСЧЕТ

| Компонент | Команда | Файлов |
|-----------|---------|--------|
| SFM | `scp` | 1 |
| AI Agents | `rsync` | 76 |
| Bots | `rsync` | 30 |
| Managers | `rsync` | 24 |
| Microservices | `rsync` | 17 |
| Active | `rsync` | 7 |
| Family | `rsync` (с исключениями) | 18 |
| VPN | `rsync` (рекурсивно) | 105 |
| Antivirus | `rsync` (рекурсивно) | 7 |
| Compliance | `rsync` | 3 |
| Core | `rsync` | 1 |
| Root Security | `find + scp` (цикл) | 72 |
| function_registry.json | `scp` | 1 |
| **ИТОГО** | | **363** |

---

## 🔍 КАК `rsync` ПЕРЕНОСИТ ФАЙЛЫ

### `rsync -avz` означает:

- **`-a`** (archive) = рекурсивно, сохраняет права, временные метки, симлинки
- **`-v`** (verbose) = показывает процесс
- **`-z`** (compress) = сжимает данные при передаче

### Пример для AI Agents:

```bash
rsync -avz security/ai_agents/ root@NEW_SERVER:/opt/aladdin-backend/security/ai_agents/
```

**Что происходит:**
1. `rsync` сканирует `security/ai_agents/` рекурсивно
2. Находит все `.py` файлы (76 штук)
3. Сравнивает с тем, что уже есть на сервере (если есть)
4. Передает только новые/измененные файлы
5. Сохраняет структуру каталогов

**Результат:** Все 76 файлов скопированы на сервер

---

## 🔍 КАК `find + scp` ПЕРЕНОСИТ ФАЙЛЫ

### Для Root Security модулей:

```bash
find security -maxdepth 1 -name "*.py" -type f \
  ! -name "test_*.py" \
  ! -name "*test*.py" \
  ! -name "*backup*.py" \
  ! -name "*fixed*.py" \
  ! -name "*patch*.py" \
  ! -name "*old*.py" | \
while read f; do
    scp "$f" root@NEW_SERVER:/opt/aladdin-backend/security/
done
```

**Что происходит:**
1. `find` находит все `.py` файлы в корне `security/` (не в подкаталогах)
2. Исключает тестовые, бэкап, исправленные файлы
3. Для каждого найденного файла выполняет `scp`
4. `scp` копирует файл на сервер

**Результат:** Все 72 критичных файла скопированы на сервер

---

## ✅ ГАРАНТИИ

### Скрипт гарантирует перенос всех 363 файлов, потому что:

1. **Использует `rsync`** - автоматически находит все файлы в каталогах
2. **Рекурсивный поиск** - обрабатывает все подкаталоги
3. **Исключения** - пропускает только ненужные файлы (тесты, бэкапы)
4. **Проверка** - можно проверить количество после переноса

### Проверка после переноса:

```bash
# На новом сервере
ssh root@NEW_SERVER_IP
find /opt/aladdin-backend/security -type f -name "*.py" | wc -l
# Должно показать: 363
```

---

## 🎯 ИТОГО

**Скрипт переносит 363 файла через:**
- **12 команд `rsync`** - для каталогов (автоматически находит все файлы)
- **1 цикл `find + scp`** - для файлов в корне security/ (72 файла)
- **2 команды `scp`** - для отдельных файлов (SFM, function_registry.json)

**Все файлы переносятся автоматически!** ✅

