import SwiftUI

/**
 * 🔒 Security Feature Row
 * Строка для отображения компонента безопасности с тумблером
 * Используется для всех 42 компонентов
 */

struct SecurityFeatureRow: View {
    let componentId: String
    let title: String
    let description: String
    @Binding var isEnabled: Bool
    let hasSettings: Bool
    let onToggle: (Bool) -> Void
    let onSettingsTap: (() -> Void)?
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    init(
        componentId: String,
        title: String,
        description: String,
        isEnabled: Binding<Bool>,
        hasSettings: Bool = false,
        onToggle: @escaping (Bool) -> Void,
        onSettingsTap: (() -> Void)? = nil
    ) {
        self.componentId = componentId
        self.title = title
        self.description = description
        self._isEnabled = isEnabled
        self.hasSettings = hasSettings
        self.onToggle = onToggle
        self.onSettingsTap = onSettingsTap
    }
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                    .dynamicTypeSize(...DynamicTypeSize.accessibility5)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
                    .dynamicTypeSize(...DynamicTypeSize.accessibility5)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title). \(description)")
            
            Spacer()
            
            if hasSettings, let onSettingsTap = onSettingsTap {
                Button(action: {
                    HapticFeedback.impact(.light)
                    onSettingsTap()
                }) {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 18))
                        .foregroundColor(.textSecondary)
                }
                .accessibilityLabel(localizationManager.localized("component.settings"))
                .accessibilityHint(localizationManager.localized("component_settings_hint"))
                .accessibilityAddTraits(.isButton)
            }
            
            ALADDINToggle(isOn: Binding(
                get: { self.isEnabled },
                set: { newValue in
                    // Передаем новое значение напрямую в ViewModel без изменения локального состояния
                    onToggle(newValue)
                }
            ))
            .accessibilityLabel(title)
            .accessibilityHint(
                isEnabled
                    ? localizationManager.localized("component_toggle_enabled_hint")
                    : localizationManager.localized("component_toggle_disabled_hint")
            )
            .accessibilityValue(
                isEnabled
                    ? localizationManager.localized("component_enabled")
                    : localizationManager.localized("component_disabled")
            )
            .accessibilityAddTraits(.isButton)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.2))
        )
        .accessibilityElement(children: .combine)
    }
}

