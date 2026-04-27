# W4-1 — целевые переходы и UI-тесты

Цель: подтвердить стабильные переходы по стеку `NavigationManager` при едином `appContentTransition` на корневом `Group` в `ALADDINApp` (`navigationManager.currentScreen`).

## Корневые контейнеры (accessibility)

| Экран | Идентификатор |
|--------|----------------|
| Главная | `aladdin_root_01_MainScreen` |
| Семья | `aladdin_root_02_FamilyScreen` |
| Защита сети / антивирус | `aladdin_root_03_NetworkProtectionScreen` |
| AI помощник | `aladdin_root_06_AIAssistantScreen` |
| Тарифы | `aladdin_root_10_TariffsScreen` |
| Профиль | `aladdin_root_11_ProfileScreen` |

## Кнопки на главной (старт перехода)

- `main_nav_family_manage`
- `main_nav_network_protection`
- `main_nav_profile`
- `main_nav_ai_assistant`
- `main_nav_tariffs`

## Назад

- Семья: `family_nav_back`
- Экраны с `ALADDINNavigationBar`: `aladdin_nav_back`
- AI: `ai_assistant_nav_back`

## UI-тесты

Файл: `Tests/UITests/NavigationTransitionUITests.swift`. Аргумент запуска `-UITestSkipOnboarding` выставляет `hasCompletedOnboarding` до инициализации `NavigationManager` (см. `ALADDINApp` / `appStartLogger`).
