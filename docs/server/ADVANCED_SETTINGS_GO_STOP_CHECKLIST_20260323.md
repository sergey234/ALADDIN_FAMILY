# Advanced Settings GO/STOP Checklist

Этот чек-лист используется перед каждым билдом для страницы "Дополнительные настройки".

## Preconditions

- Есть валидный JWT (`TOKEN`).
- Сервер доступен (`BASE_URL`, обычно `https://aladdin-ai.ru`).
- На экране Advanced виден mini-log.

## GO/STOP Steps

1. **Safari: Фильтрация сайтов**
- Открыть "Настройка категорий", выбрать минимум 3 категории.
- Нажать "Применить правила".
- Ожидание: в mini-log есть `SAFARI APPLY start` и `SAFARI APPLY ok`.
- Если есть `failed`/`404`/`405`: **STOP**.

2. **Safari: Ограничение соцсетей**
- Включить тумблер и применить правила.
- Ожидание: UI лог + API start/result без ошибок.
- Если нет API result: **STOP**.

3. **Parental: Мониторинг сообщений**
- Переключить `parental_messages_monitoring`.
- Ожидание: `ADVANCED.UI` + `ADVANCED.API parental POST ok`.
- Если только UI без API: **STOP**.

4. **Parental: Скриншоты**
- Переключить `parental_screenshots_enabled`.
- Ожидание: `ADVANCED.UI` + `ADVANCED.API parental POST ok`.
- Если только UI без API: **STOP**.

5. **Time Management: Расписание доступа**
- Открыть "Настройки" карточки расписания, изменить время, сохранить.
- Ожидание: `ADVANCED.API schedule POST ok`.
- Ошибка POST: **STOP**.

6. **Time Management: Время сна**
- Изменить интервал сна и флаг экстренных вызовов, сохранить.
- Ожидание: `ADVANCED.API sleep POST ok`.
- Ошибка POST: **STOP**.

7. **Time Management: Лимиты приложений**
- Изменить лимит минимум для 1 приложения, сохранить.
- Ожидание: `ADVANCED.API appLimits POST ok`.
- Ошибка POST: **STOP**.

8. **GET Verify (сервер)**
- Выполнить:
  - `GET /api/components/configuration/browser_security_bot`
  - `GET /api/components/configuration/parental_control_bot`
- Ожидание: значения соответствуют последним изменениям.
- Несовпадение: **STOP**.

9. **UI reopen check**
- Закрыть и снова открыть Advanced.
- Ожидание: значения тумблеров/настроек не откатываются.
- Откат состояния: **STOP**.

10. **Итог**
- Все шаги PASS: **GO**.
- Любой FAIL/несовпадение: **STOP**, релиз блокируется до фикса.

## Automation

Для быстрой проверки используйте:

- `python3 docs/server/test_advanced_settings_smoke.py`

Переменные окружения:

- `BASE_URL`
- `TOKEN`

Результат скрипта:

- `[GO] Advanced Settings smoke passed` — можно идти дальше.
- `[STOP] ...` — найти и исправить причину.
