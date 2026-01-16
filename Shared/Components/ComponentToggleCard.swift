import SwiftUI

/**
 * 🎴 Component Toggle Card
 * Карточка для отображения компонента с тумблером и описанием
 * Используется для компонентов, которые требуют только тумблер
 */

struct ComponentToggleCard: View {
    let componentId: String
    let title: String
    let description: String
    @Binding var isEnabled: Bool
    let icon: String?
    let onToggle: (Bool) -> Void
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    init(
        componentId: String,
        title: String,
        description: String,
        isEnabled: Binding<Bool>,
        icon: String? = nil,
        onToggle: @escaping (Bool) -> Void
    ) {
        self.componentId = componentId
        self.title = title
        self.description = description
        self._isEnabled = isEnabled
        self.icon = icon
        self.onToggle = onToggle
    }
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            if let icon = icon {
                Text(icon)
                    .font(.system(size: 32))
                    .frame(width: 50, height: 50)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                    .accessibilityLabel("Icon \(icon)")
            }
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.title3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                    .dynamicTypeSize(...DynamicTypeSize.accessibility5)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(3)
                    .dynamicTypeSize(...DynamicTypeSize.accessibility5)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title). \(description)")
            
            Spacer()
            
            ALADDINToggle(isOn: Binding(
                get: { isEnabled },
                set: { newValue in
                    // ВАЖНО: не делаем "двойное переключение".
                    // Источник истины — binding, а onToggle получает целевое значение и сохраняет его.
                    isEnabled = newValue
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
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(isEnabled ? Color.green.opacity(0.3) : Color.textSecondary.opacity(0.1), lineWidth: 1)
                )
        )
        .accessibilityElement(children: .combine)
    }
}

