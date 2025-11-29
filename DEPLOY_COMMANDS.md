# 🚀 Команды для загрузки лендинга на сервер

## Шаг 1: Загрузка файлов на сервер

Выполните в терминале (введите пароль `Sergio675` когда запросит):

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
rsync -avz --progress landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
```

**Что загружается:**
- ✅ `index.html` (222K) - обновлен с правильным API URL
- ✅ `consent.html` (13K) - новый файл согласия на обработку ПДн
- ✅ `privacy.html` (8.2K) - обновлена политика конфиденциальности
- ✅ `terms.html` (8.2K) - обновлена публичная оферта
- ✅ Все остальные файлы (CSS, JS, CMS и т.д.)

---

## Шаг 2: Настройка прав доступа на сервере

После загрузки подключитесь к серверу и выполните:

```bash
ssh root@149.154.65.180
```

Затем выполните команды:

```bash
chown -R www-data:www-data /var/www/aladdin-ai.ru
find /var/www/aladdin-ai.ru -type d -exec chmod 755 {} \;
find /var/www/aladdin-ai.ru -type f -exec chmod 644 {} \;
systemctl reload nginx
```

---

## Шаг 3: Проверка

1. Откройте в браузере: https://aladdin-ai.ru/
2. Проверьте, что все три документа доступны:
   - https://aladdin-ai.ru/consent.html
   - https://aladdin-ai.ru/privacy.html
   - https://aladdin-ai.ru/terms.html
3. Протестируйте форму оплаты:
   - Откройте https://aladdin-ai.ru/#pay
   - Заполните форму
   - Проверьте, что чекбокс согласия работает
   - Проверьте, что запрос идет на `https://aladdin-ai.ru/api/payments/create`

---

## Что было обновлено:

1. ✅ **API URL**: Лендинг теперь автоматически использует `https://aladdin-ai.ru` для API на продакшн-сервере
2. ✅ **Согласие ПДн**: Добавлен новый файл `consent.html` с полным текстом согласия
3. ✅ **Единый чекбокс**: Один чекбокс для согласия со всеми тремя документами
4. ✅ **Унифицированные документы**: Все три документа в едином стиле с одинаковыми контактами
5. ✅ **Компактный стиль**: Уменьшены отступы между строками для более компактного вида


