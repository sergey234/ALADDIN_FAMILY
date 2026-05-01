# TODO: Локализация, аналитика, навигация, угрозы, AI / Family Chat

**Дата:** 1 мая 2026  
**Назначение:** единый список задач для Cursor и ревью. Сюда входит разбор «найдено в коде → план» по пунктам 1–7 и **согласованная политика** из `TODO_REALTIME_COLLABORATION_PLAN.md` (раздел «Продуктовые решения»).

**Связанный документ:** `docs/TODO_REALTIME_COLLABORATION_PLAN.md` (realtime/offline; там же зафиксированы решения по меню / языку / аналитике).

---

## Согласованная политика (кратко)

| Тема | Решение |
|------|---------|
| Меню навигации в настройках | В **production** скрыть служебные маршруты из списка; отладка — `#if DEBUG` или whitelist. |
| AI + Family Chat | **Язык ответов и UI-строк = язык приложения** (`LocalizationManager`); проброс в API где нужно. |
| Экран аналитики | **Честно различать** состояния: «событий не было» vs «не удалось загрузить» + повтор vs офлайн/кэш — **разный текст и цвет**. |

---

## Порядок реализации (рекомендованный)

1. Быстрые локализации и меню: **п.1, п.6, п.5**  
2. Функциональный баг: **п.2** (угрозы / JSON)  
3. Поведение: **п.3** (AI язык), **п.4 и п.7** (аналитика)

---

## 1) Главная (Main): «Семейный чат» при EN

| Найдено | `Screens/01_MainScreen.swift` — захардкожено `"Семейный чат"` (ветки `destination == .family`, `current == .family`). |
| План | 1.1 Ключи RU/EN (`main_home_chat_segment_family` или рядом с `family_chat_title`) в `LocalizationManager` / prоj strings. 1.2 Заменить обе строки на `localized`. 1.3 Проверить ветку «AI чат» на русский без ключа. |

- [ ] 1.1–1.3 Main: локализация сегмента Family / AI чата

---

## 2) Устройства → Угрозы: DecodingError + смешанный RU/EN текст

| Найдено | `DeviceThreatsView` в `Screens/22_DeviceDetailScreen.swift` → `getTopThreats` → `AppConfig.Endpoint.topThreats` (`/api/analytics/top-threats`). Модель: `[ThreatItem]` в `Core/Models/APIModels.swift`. Ошибка: типично `DecodingError` + префикс из `error.decoding_error` / `NetworkError`. |
| План | 2.1 Зафиксировать реальный JSON ответа. 2.2 Обёртка/маппинг в `[ThreatItem]` при расхождении. 2.3 Одна локализованная ошибка по типу, без склейки RU + Foundation `localizedDescription` для decoding. 2.4 Регрессия: пусто / ошибка / данные. |

- [ ] 2.1–2.4 Device threats: контракт API + локализованные ошибки

---

## 3) AI: язык = язык приложения

| Найдено | `AIAssistantViewModel` → `AIStreamingService.streamMessage` (контекст `"general"`, язык может не пробрасываться). `loadInitialMessages()` на русском. `06_AIAssistantScreen`: `ru_RU` у форматтера и `SFSpeechRecognizer`. Бэкенд fallback может быть RU. |
| План | 3.1 Цепочка до тела SSE/API. 3.2 `responseLanguage` / заголовок из `currentLanguage`. 3.3 Локализация приветствий и ошибок. 3.4 Бэкенд: учёт языка в fallback/SFM (отдельно при необходимости). |

- [ ] 3.1–3.4 AI: язык приложения end-to-end

---

## 4) Аналитика: «Нет данных» / пропали зелёные цифры

| Найдено | `04_AnalyticsScreen.swift`: пустые `threatCategories` → `analytics_no_threats`. Сверху `DebouncedDataSourceIndicator` + `analytics_data_source_*`. Данные: `RemoteAnalyticsService` + `AnalyticsViewModel` (`DataSource`, токены, фильтры). |
| План | 4.1 Логи: `dataSource`, ошибки. 4.2 API + фильтры из настроек. 4.3 Разные ключи: «нет событий за период» vs «не загрузилось» vs офлайн (см. политику выше). |

- [ ] 4.1–4.3 Analytics: диагностика + раздельные состояния UX

---

## 5) Настройки: меню навигации — RU при EN, пустые экраны

| Найдено | `ALADDINNavigationBar.swift`: `allCases` + `localizedTitle` → `navigationLocalizationKey()`; при отсутствии ключа — `displayName` в `NavigationManager.swift` (**русские строки**). Нет ключей для `settings_test*`, `loading`/`joinDevice` → `default` → `nav_screen_unknown`. |
| План | 5.1 **Production:** whitelist экранов для меню, служебное скрыть (согласовано). 5.2 Для оставшихся пунктов — полные `nav_screen_*` RU+EN и явные `case` для `.loading`, `.joinDevice`, `.invitationCode`. 5.3 Проверка маппинга в `ALADDINApp` для видимых маршрутов. |

- [ ] 5.1–5.3 Settings nav: production whitelist + локализация видимых пунктов

---

## 6) Семья → родитель → 7 карточек: русские метрики при EN

| Найдено | `02_FamilyScreen.swift` — `parentalControlsSection`: `metric` / `statusText` с русским («Точность: 50м», «Smart DNS Активен», OFF bypass и т.д.). |
| План | 6.1 Инвентаризация литералов + модалки (Bypass, мониторинг). 6.2 Ключи в `LocalizationManager`. 6.3 Правило: только `localized`. |

- [ ] 6.1–6.3 Family parental cards: полная локализация метрик/статусов

---

## 7) Аналитика: зелёный текст на русском при EN при обновлении

| Найдено | Вероятно `DebouncedDataSourceIndicator` / `analytics_data_source_*`; точная строка «Контент обновлён» в коде не найдена — нужна фиксация текста при воспроизведении. |
| План | 7.1 Точный текст + grep. 7.2 RU/EN для `analytics_data_source_*` по языку приложения. 7.3 Если тост/SyncEngine — локализовать источник. |

- [ ] 7.1–7.3 Analytics refresh indicator: найти источник + локализация

---

## Family Chat: язык как у приложения (доп. к п.3)

Согласовано: **то же правило**, что для AI — приоритет языка из настроек приложения для отображаемых строк и, где применимо, для запросов к API.

- [ ] FC.1 Проброс/ключи для системных сообщений Family Chat + согласование с контрактом API  
  - **Mock `getMockMessages()`:** в **Release** не подставляются при ошибке загрузки (только `#if DEBUG`). Убрать = не показывать пользователю фейковый русскоязычный диалог; в Debug мок остаётся для разработки.

---

**Как отмечать прогресс:** галочки `- [ ]` → `- [x]` в этом файле; в Cursor — связанный список задач (Todo).
