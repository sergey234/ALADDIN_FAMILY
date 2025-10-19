# 🎯 АЛГОРИТМ ПЕРЕНОСА HTML WIREFRAMES В SWIFTUI

## 📋 Пошаговый алгоритм

### 1. **Анализ HTML структуры**
```html
<!-- HTML: 03_family_screen.html -->
<div class="main-content">
  <div class="family-overview">...</div>
  <div class="family-members">...</div>
  <div class="parental-controls">
    <div class="control-cards-grid">
      <div class="control-card-simple">...</div>
    </div>
  </div>
</div>
```

### 2. **Создание SwiftUI структуры**
```swift
// SwiftUI: FamilyScreen.swift
ScrollView {
  VStack {
    familyOverview
    familyMembersList
    parentalControlSection
  }
}
```

### 3. **Перенос CSS стилей в SwiftUI**

#### HTML CSS → SwiftUI
```css
/* HTML CSS */
.parental-controls {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

```swift
// SwiftUI
.background(
  RoundedRectangle(cornerRadius: 20)
    .fill(Color.white.opacity(0.1))
    .overlay(
      RoundedRectangle(cornerRadius: 20)
        .stroke(Color.white.opacity(0.2), lineWidth: 1)
    )
)
.padding(15)
```

### 4. **Перенос цветов**
```css
/* HTML CSS */
.title { color: #F59E0B; }
.status-light.green { color: #10B981; }
.status-light.red { color: #EF4444; }
```

```swift
// SwiftUI
.foregroundColor(.secondaryGold) // #F59E0B
.foregroundColor(.successGreen)  // #10B981
.foregroundColor(.dangerRed)     // #EF4444
```

### 5. **Перенос сетки 2×2**
```css
/* HTML CSS */
.control-cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
```

```swift
// SwiftUI
LazyVGrid(columns: [
  GridItem(.flexible(), spacing: 8),
  GridItem(.flexible(), spacing: 8)
], spacing: 8) {
  // Карточки
}
```

### 6. **Перенос интерактивности**
```html
<!-- HTML -->
<div class="control-card-simple" onclick="openModal('content')">
```

```swift
// SwiftUI
Button(action: {
  print("Открыть контент-фильтр")
}) {
  ParentalControlCard(...)
}
```

## 🚨 КРИТИЧЕСКИЕ ПРАВИЛА

1. **НЕ УПРОЩАТЬ** - переносить 1:1 из HTML
2. **СОХРАНЯТЬ ЦВЕТА** - использовать точные hex коды
3. **СОХРАНЯТЬ РАЗМЕРЫ** - padding, margin, font-size
4. **СОХРАНЯТЬ ИНТЕРАКТИВНОСТЬ** - все кнопки должны работать
5. **СОХРАНЯТЬ СТРУКТУРУ** - VStack, HStack, LazyVGrid

## 📝 Чек-лист переноса

- [ ] Прочитать HTML структуру
- [ ] Выделить основные секции
- [ ] Перенести CSS стили в SwiftUI
- [ ] Создать компоненты (карточки, кнопки)
- [ ] Добавить интерактивность
- [ ] Протестировать на симуляторе
- [ ] Сравнить с HTML wireframe

## 🎯 Результат

Полное соответствие HTML wireframe в SwiftUI:
- ✅ Точные цвета
- ✅ Точные размеры
- ✅ Рабочие кнопки
- ✅ Прокрутка
- ✅ Анимации
- ✅ Интерактивность

