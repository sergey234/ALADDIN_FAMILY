import SwiftUI

/**
 * 🔄 Smart Toggle Row
 * Умный тумблер с логикой переключения и логированием
 * Заменяет обычный ToggleRow во всех модальных окнах настроек
 */

struct SmartToggleRow: View {
    let componentId: String
    let settingKey: String
    let title: String
    @Binding var isOn: Bool
    let onValueChanged: ((Bool) -> Void)?

    @EnvironmentObject private var localizationManager: LocalizationManager

    // Analytics для логирования
    private let componentAnalytics = ComponentAnalytics.shared

    var body: some View {
        HStack {
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            Spacer()
            Toggle("", isOn: $isOn)
                .onChange(of: isOn) { newValue in
                    // ✅ BUILD 111: Гарантируем выполнение аналитики на main thread асинхронно
                    // Это предотвращает рекурсию и блокировку UI
                    DispatchQueue.main.async {
                        // Логируем событие переключения
                        componentAnalytics.trackSettingToggle(
                            componentId: componentId,
                            settingKey: settingKey,
                            enabled: newValue
                        )
                    }

                    // Вызываем колбэк если есть
                    onValueChanged?(newValue)

                    print("🔄 SmartToggleRow: \(componentId).\(settingKey) = \(newValue)")
                }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.white.opacity(0.05))
        )
    }
}

// MARK: - Convenience Initializers

extension SmartToggleRow {
    /// Простой инициализатор без колбэка
    init(
        componentId: String,
        settingKey: String,
        title: String,
        isOn: Binding<Bool>
    ) {
        self.componentId = componentId
        self.settingKey = settingKey
        self.title = title
        self._isOn = isOn
        self.onValueChanged = nil
    }

    /// Инициализатор с колбэком
    init(
        componentId: String,
        settingKey: String,
        title: String,
        isOn: Binding<Bool>,
        onValueChanged: @escaping (Bool) -> Void
    ) {
        self.componentId = componentId
        self.settingKey = settingKey
        self.title = title
        self._isOn = isOn
        self.onValueChanged = onValueChanged
    }
}
