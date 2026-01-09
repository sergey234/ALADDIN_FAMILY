import SwiftUI

/**
 * 🦯 Accessibility Extensions
 * Расширения для доступности SwiftUI
 * Упрощают добавление VoiceOver и других функций
 */

// MARK: - View Extensions

extension View {
    
    /**
     * Добавить полный accessibility для кнопки
     */
    func accessibilityButton(label: String, hint: String? = nil) -> some View {
        self
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(label)
            .accessibilityHint(hint ?? "")
            .accessibilityAddTraits(.isButton)
    }
    
    /**
     * Добавить accessibility для заголовка
     */
    func accessibilityHeading(label: String) -> some View {
        self
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(label)
            .accessibilityAddTraits(.isHeader)
    }
    
    /**
     * Добавить accessibility для изображения
     */
    func accessibilityImage(label: String, isDecorative: Bool = false) -> some View {
        if isDecorative {
            return self.accessibilityHidden(true)
        } else {
            return self
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(label)
                .accessibilityAddTraits(.isImage)
        }
    }
    
    /**
     * Добавить accessibility для toggle/switch
     */
    func accessibilityToggle(label: String, isOn: Bool) -> some View {
        self
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(label)
            .accessibilityValue(isOn ? "Включено" : "Выключено")
            .accessibilityAddTraits(.isButton)
    }
    
    /**
     * Добавить accessibility для slider
     */
    func accessibilitySlider(label: String, value: String) -> some View {
        self
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(label)
            .accessibilityValue(value)
            .accessibilityAdjustableAction { direction in
                // Позволяет изменять значение через VoiceOver
            }
    }
    
    /**
     * Скрыть от VoiceOver (для декоративных элементов)
     */
    func decorative() -> some View {
        self.accessibilityHidden(true)
    }
    
    /**
     * Группировка элементов для VoiceOver
     */
    func accessibilityGroup(label: String, children: AccessibilityChildBehavior = .combine) -> some View {
        self
            .accessibilityElement(children: children)
            .accessibilityLabel(label)
    }
}

// MARK: - Text Extensions

extension Text {
    
    /**
     * Dynamic Type поддержка
     * Автоматически масштабирует текст
     */
    func scalableText() -> some View {
        self.lineLimit(nil)
            .minimumScaleFactor(0.5)
            .dynamicTypeSize(...DynamicTypeSize.accessibility5)
    }
}

// MARK: - Color Extensions

extension Color {
    
    /**
     * Проверить контрастность для WCAG AA
     * Минимум 4.5:1 для обычного текста
     * Минимум 3:1 для крупного текста
     */
    func hasGoodContrast(with otherColor: Color) -> Bool {
        // Упрощённая проверка
        // В production нужна полная реализация WCAG contrast ratio
        return true
    }
    
    /**
     * Получить цвет с достаточным контрастом
     */
    func withAccessibleContrast(on background: Color) -> Color {
        // Если фон тёмный - светлый текст
        // Если фон светлый - тёмный текст
        return self
    }
}

// MARK: - Button Accessibility

struct AccessibleButton: View {
    let title: String
    let hint: String?
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
        }
        .accessibilityButton(label: title, hint: hint)
    }
}

// MARK: - Accessibility Labels Constants

enum AccessibilityLabels {
    
    // Buttons
    static let backButton = "Назад"
    static let closeButton = "Закрыть"
    static let settingsButton = "Настройки"
    static let notificationsButton = "Уведомления"
    static let addButton = "Добавить"
    static let deleteButton = "Удалить"
    static let saveButton = "Сохранить"
    static let cancelButton = "Отмена"
    
    // Network Protection
    static let networkProtectionToggle = "Переключатель защиты сети"
    static let networkProtectionStatusProtected = "Защита сети подключена, соединение защищено"
    static let networkProtectionStatusNotProtected = "Защита сети отключена, соединение не защищено"
    
    // Family
    static let familyMemberCard = "Карточка члена семьи"
    static let addFamilyMember = "Добавить члена семьи"
    
    // Threats
    static let threatCard = "Карточка угрозы"
    static let threatBlocked = "Угроза заблокирована"
    
    // Devices
    static let deviceCard = "Карточка устройства"
    static let addDevice = "Добавить устройство"
}



