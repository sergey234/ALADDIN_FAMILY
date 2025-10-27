# 🗺️ СХЕМА НАВИГАЦИИ МЕЖДУ УЧАСТНИКАМИ СЕМЬИ

## 📊 ВИЗУАЛЬНАЯ СХЕМА

```
┌─────────────────────────────────────────────────────────────┐
│                     📱 FAMILY SCREEN                         │
│                  (02_FamilyScreen.swift)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           👨‍👩‍👧‍👦 Участники семьи                  │    │
│  │                                                    │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │    │
│  │  │  👨 Папа │  │  👩 Мама │  │  👶 Маша │    ... │    │
│  │  │ Родитель │  │ Родитель │  │  Ребёнок │         │    │
│  │  │          │  │          │  │          │         │    │
│  │  │ [КАРТОЧКА]  [КАРТОЧКА]    [КАРТОЧКА]         │    │
│  │  └─────┬────┘  └─────┬────┘  └─────┬────┘         │    │
│  │        │             │             │              │    │
│  │        ▼             ▼             ▼              │    │
│  └────────┼─────────────┼─────────────┼──────────────┘    │
│           │             │             │                   │
└───────────┼─────────────┼─────────────┼───────────────────┘
            │             │             │
            ▼             ▼             ▼
    ┌────────────┐  ┌────────────┐  ┌─────────────────┐
    │ПАРЕНТ      │  │ПАРЕНТ      │  │  CHILD          │
    │КОНТРОЛЬ    │  │КОНТРОЛЬ    │  │  ИНТЕРФЕЙС      │
    │            │  │            │  │                 │
    │ 📊 Стат.   │  │ 📊 Стат.   │  │ 🎮 Игры         │
    │ ⏰ Время    │  │ ⏰ Время    │  │ 📚 Учёба         │
    │ 🛡️ Защита  │  │ 🛡️ Защита  │  │ 🦄 Награды      │
    │            │  │            │  │ ⏰ Таймер       │
    │(Parental   │  │(Parental   │  │                 │
    │Control)    │  │Control)    │  │(ChildInterface) │
    └────────────┘  └────────────┘  └─────────────────┘
```

---

## 🔄 ДЕТАЛЬНАЯ СХЕМА НАВИГАЦИИ

### 1️⃣ **FamilyScreen (Главный экран семьи)**
```
Role: parent
  ↓ tap on card
ParentalControlScreen (Родительский контроль)
  ├─ Выбор ребёнка (Маша, Петя, Аня)
  ├─ Система вознаграждений 🦄
  ├─ Настройки контроля
  └─ Статистика за неделю

Role: child
  ↓ tap on card
ChildInterfaceScreen (Детский интерфейс)
  ├─ Приветствие с именем
  ├─ Возрастные табы (1-6, 7-12, 13-17 лет)
  ├─ Большие кнопки: Игры 🎮, Учёба 📚, Творчество 🎨
  ├─ Время экрана (таймер)
  └─ Награды (при нажатии на аватар) → ChildRewardsScreen

Role: elderly
  ↓ tap on card
ElderlyInterfaceScreen (Интерфейс для пожилых)
  ├─ Приветствие "Здравствуйте!"
  ├─ Статус защиты (✅ ВСЁ ХОРОШО)
  ├─ Большие кнопки: Позвонить, Безопасность, Инструкции
  └─ Кнопка SOS 🚨
```

---

## 📝 АРХИТЕКТУРА РЕАЛИЗАЦИИ

### Компоненты:

```
┌─────────────────────────────────────────────────────┐
│  FamilyScreen.swift                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │  FamilyMemberCard (x4)                      │   │
│  │  └─ action: navigateToMemberScreen()        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  FamilyNavigationHelper                              │
│  ┌─────────────────────────────────────────────┐   │
│  │  func navigateToMember(role: FamilyRole)    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  NavigationManager.swift                             │
│  ┌─────────────────────────────────────────────┐   │
│  │  navigate(to: .parentalControl)             │   │
│  │  navigate(to: .childInterface)              │   │
│  │  navigate(to: .elderlyInterface)            │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 КОД РЕАЛИЗАЦИИ

### Шаг 1: Создать helper функцию в FamilyScreen

```swift
// FamilyScreen.swift

@EnvironmentObject private var navigationManager: NavigationManager

// Helper функция для навигации
private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
    // Haptic feedback
    let generator = UIImpactFeedbackGenerator(style: .medium)
    generator.impactOccurred()
    
    // Навигация по роли
    switch role {
    case .parent:
        navigationManager.navigateTo(.parentalControl)
    case .child:
        navigationManager.navigateTo(.childInterface)
    case .teenager:
        navigationManager.navigateTo(.childInterface) // Упрощенный интерфейс
    case .elderly:
        navigationManager.navigateTo(.elderlyInterface)
    }
}
```

### Шаг 2: Обновить FamilyMemberCard

```swift
// В FamilyScreen.swift - обновить карточки участников

FamilyMemberCard(
    name: "Папа",
    role: .parent,
    avatar: "👨",
    status: .protected,
    threatsBlocked: 15,
    lastActive: "2 мин назад",
    action: {
        navigateToMemberScreen(role: .parent)
    }
)

FamilyMemberCard(
    name: "Маша",
    role: .child,
    avatar: "👧",
    status: .protected,
    threatsBlocked: 5,
    lastActive: "30 мин назад",
    action: {
        navigateToMemberScreen(role: .child)
    }
)

FamilyMemberCard(
    name: "Бабушка",
    role: .elderly,
    avatar: "👵",
    status: .protected,
    threatsBlocked: 3,
    lastActive: "1 час назад",
    action: {
        navigateToMemberScreen(role: .elderly)
    }
)
```

---

## ✅ ПРЕИМУЩЕСТВА СХЕМЫ

1. **🎯 Простота**
   - Одна функция `navigateToMemberScreen(role:)`
   - Все логика в одном месте

2. **🔒 Типобезопасность**
   - Используем enum `FamilyRole`
   - Swift компилятор проверяет все случаи

3. **📱 Haptic Feedback**
   - Тактильная обратная связь при нажатии
   - Улучшает UX

4. **🚀 Расширяемость**
   - Легко добавить новые роли
   - Просто изменить логику навигации

---

## 🔄 ПОТОК ДАННЫХ

```
User taps card
    ↓
FamilyMemberCard.action
    ↓
FamilyScreen.navigateToMemberScreen(role:)
    ↓
Haptic Feedback
    ↓
NavigationManager.navigate(to: screen)
    ↓
Destination screen opens (ParentalControl / ChildInterface / ElderlyInterface)
```

---

*Схема создана: 2025-01-26*
