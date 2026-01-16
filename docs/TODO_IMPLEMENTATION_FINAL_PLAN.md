# ✅ TODO — реализация финального плана (по 1 пункту за раз)
**Дата:** 2026‑01‑15  
**Источник требований:** `docs/PLAN_FINAL_APPROVAL_ADVANCED_SETTINGS.md`

Правила:
- Автосохранение сразу — только где нет “Сохранить”.
- С “Сохранить” — UX не меняем.
- Делаем по 1 изменению → проверяем “вышел/зашёл” и “kill app”.

---

## A) Advanced Settings (основной фокус)

### A1) Safari (2 карточки) — уже сделано ✅
- [x] Встроить аккордеон Safari в `Screens/AdvancedProtectionSettingsScreen.swift`
- [x] 2 карточки: “Фильтрация сайтов” + “Ограничение соцсетей”
- [x] `.sheet` → `FamilyContentBlockModal`
- [x] refresh статуса на `onAppear` и при возврате из background
- [x] RU/EN ключи для Safari‑блока добавлены в `LocalizationManager`

### A2) Контроль и мониторинг (семья) — в работе
- [ ] Добавить аккордеон “Контроль и мониторинг (семья)” в `AdvancedProtectionSettingsScreen`
- [ ] Карточка “Мониторинг активности”:
  - [ ] метрики sites/apps (server + fallback)
  - [ ] тумблеры: `parental_messages_monitoring`, `parental_screenshots_enabled`
  - [ ] `.sheet` → `FamilyMonitoringModal`
- [ ] Карточка “Контроль времени”:
  - [ ] метрики из `parental_time_stats`
  - [ ] `.sheet` → `FamilyTimeControlModal`
- [ ] Карточка “Лимиты приложений”:
  - [ ] метрика из `app_limits_settings`
  - [ ] `.sheet` → `AppLimitsSettingsModal`

### A3) “Блокировка угроз” (агрегатор 4 компонент)
- [ ] Добавить карточку “Блокировка угроз” (phishing/malware/mobile/network) в Advanced Settings
- [ ] Статус: Вкл/Частично/Выкл
- [ ] “Настроить” открывает существующие модалки (через `.sheet`)
- [ ] Проверка сохранения (кэш/сервер): toggle → выйти/зайти → kill app → состояние сохранилось

### A4) Локализация новых карточек (семья/угрозы)
- [ ] Добавить/проверить RU/EN ключи для:
  - [ ] заголовков/описаний “Контроль и мониторинг”
  - [ ] заголовка/статусов “Блокировка угроз” (если нужен отдельный нейминг)
- [ ] Пересобрать `docs/AUDIT_LOCALIZATION_MISSING_KEYS_ACTIVE.json`

---

## B) Документация и расхождения
- [ ] Обновить `docs/ПОЛНАЯ_КАРТА_42_КОМПОНЕНТОВ.md` по фактическим `componentId` в `ParentalControlScreen`

---

## C) Общий долг по локализации (как в общем чеклисте)
- [ ] Дожать missing keys до 0 (начиная с NetworkProtection + EnergyStats)
- [ ] Хардкод‑строки (Must‑fix) → 0
- [ ] Динамические ключи → детерминированные enum/table


