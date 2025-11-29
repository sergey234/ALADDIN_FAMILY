# Smoke Test Run — 2025-11-11

## Инструкции по фиксации
- Ориентируемся на чеклист `docs/SmokeTestChecklist.md`.
- Для каждого шага фиксируем время, статус (`OK`, `⚠️ Issue`, `🚫 Blocker`) и краткий комментарий.
- В случае сбоя прикладываем ссылку на лог/скрин, описываем шаги воспроизведения и номер баг-репорта.
- Итоговый файл сохраняем вместе с приложенными логами в `docs/QAReports/2025-11-11/` (создать подпапку при необходимости).

## Журнал запуска
| Этап | Статус | Комментарий |
|------|--------|-------------|
| Подготовка окружения | ✅ | Симулятор iPhone 13 запущен, проект собран успешно |
| Smoke тест основных экранов | ⏳ | Требуется ручной прогон на симуляторе |
| Smoke тест дополнительных компонентов | ⏳ | Требуется ручной прогон на симуляторе |
| Общие проверки | ⏳ | Требуется ручной прогон на симуляторе |
| `advanced_quality_check.py` | ⚠️ | Скрипт ищет Python файлы в security/, не подходит для iOS проекта |
| Unit-тесты PaymentQR | ✅ | Создан PaymentQRViewModelProtectionTests.swift (15+ тест-кейсов) |
| Документация PaymentQR | ✅ | Создана защитная документация и инструкции для ML |
| Итоговый отчёт QA | ⏳ | Ожидает завершения smoke-тестов |

## Основные экраны (22)
| # | Экран | Статус | Факт / Комментарий | Время |
|---|-------|--------|--------------------|-------|
| 1 | `01_MainScreen` | ⬜ | | |
| 2 | `02_FamilyScreen` | ⬜ | | |
| 3 | `03_VPNScreen` | ⬜ | | |
| 4 | `04_AnalyticsScreen` | ⬜ | | |
| 5 | `05_SettingsScreen` | ⬜ | | |
| 6 | `06_AIAssistantScreen` | ⬜ | | |
| 7 | `07_ParentalControlScreen` | ⬜ | | |
| 8 | `08_ChildInterfaceScreen` | ⬜ | | |
| 9 | `09_ElderlyInterfaceScreen` | ⬜ | | |
| 10 | `10_TariffsScreen` | ⬜ | | |
| 11 | `11_ProfileScreen` | ⬜ | | |
| 12 | `12_NotificationsScreen` | ⬜ | | |
| 13 | `13_SupportScreen` | ⬜ | | |
| 14 | `14_OnboardingScreen` | ⬜ | | |
| 15 | `18_PrivacyPolicyScreen` | ⬜ | | |
| 16 | `19_TermsOfServiceScreen` | ⬜ | | |
| 17 | `20_DevicesScreen` | ⬜ | | |
| 18 | `21_ReferralScreen` | ⬜ | | |
| 19 | `22_DeviceDetailScreen` | ⬜ | | |
| 20 | `23_FamilyChatScreen` | ⬜ | | |
| 21 | `24_VPNEnergyStatsScreen` | ⬜ | | |
| 22 | `25_PaymentQRScreen` | ⬜ | | |

## Дополнительные компоненты (16)
| # | Компонент | Статус | Факт / Комментарий | Время |
|---|-----------|--------|--------------------|-------|
| 1 | `ChildRewardsScreen` | ⬜ | | |
| 2 | `FamilyScreen` (новый) | ⬜ | | |
| 3 | `FamilyTournamentView` | ⬜ | | |
| 4 | `GamesParentalControlView` | ⬜ | | |
| 5 | `LanguageSettingsScreen` | ⬜ | | |
| 6 | `MainScreenWithRegistration` | ⬜ | | |
| 7 | `NotificationSettingsScreen` | ⬜ | | |
| 8 | `OnboardingScreen` (дубль) | ⬜ | | |
| 9 | `RewardsModalView` | ⬜ | | |
| 10 | `RewardsQuickModal` | ⬜ | | |
| 11 | `UnicornPetView` | ⬜ | | |
| 12 | `UnicornUniverseView` | ⬜ | | |
| 13 | `WheelOfFortuneView` | ⬜ | | |
| 14 | `WidgetConfigurationScreen` | ⬜ | | |
| 15 | `AdvancedProtectionSettingsScreen` | ⬜ | | |
| 16 | `SecurityEducationScreen` | ⬜ | | |

## Общие проверки
- [ ] Запуск → фон → возврат приложения.
- [ ] Переключение языка (RU → EN → RU).
- [ ] Тёмная тема.
- [ ] Обработка сетевых ошибок (без интернета).
- [ ] Проверка логов Xcode (crash/exception).
- [ ] `python3 /Users/sergejhlystov/ALADDIN_NEW/scripts/advanced_quality_check.py` выполнен, отчёт сохранён.
- [ ] Фиксация результатов в `ProductionPrepPlan.md` и баг-трекере.

## Приложения
- Логи: 
- Скриншоты: 
- Баг-репорты:
