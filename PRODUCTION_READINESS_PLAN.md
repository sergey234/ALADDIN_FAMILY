# Production Readiness Plan (Analytics & Localization)

## 1. Локализация и данные
- [ ] AnalyticsViewModel подключён к production API, проверены success/empty/error сценарии.
- [ ] ChildRewardsScreen: все строки через `localizationManager`, данные подтягиваются из боевого эндпоинта.
- [ ] 07_ParentalControlScreen: убраны литералы, данные из API, обработаны загрузка/ошибка.
- [ ] AddMemberOptionsModal: локализация + реальные роли/навигация.
- [ ] Ручная проверка RU ↔ EN на навигации, аналитике, отчётах; зафиксировать скриншоты/заметки.

## 2. Код и тесты
- [ ] ALADDINUnitTests.swift: починен синтаксис, enum’ы FamilyRole/AgeGroup синхронизированы, добавлены тесты для новых ключей.
- [ ] `xcodebuild test` (минимум схема ALADDINUnitTests) выполнен без ошибок.
- [ ] Warnings: переписан `SecTrustEvaluate` на `SecTrustEvaluateWithError`, проверены остальные предупреждения.

## 3. Сборка и подпись
- [ ] Настроен Development Team и профили в Signing & Capabilities для релизной схемы.
- [ ] `xcodebuild -scheme ALADDIN -configuration Release archive` + проверка IPA.

## 4. Документация
- [ ] Гайд по локализации обновлён: «не использовать автоматические скрипты удаления дублей; `check_localization_duplicates.py` — только для отчёта».
- [ ] Документ по аналитике обновлён (новые ключи, API, порядок обновления данных).

## Итог
Все чекбоксы выполнены → можно переходить к финальному продакшн-релизу.
