import SwiftUI

/**
 * 📋 Settings Accordion
 * Аккордеон для группировки компонентов в настройках
 * Используется для организации 42 компонентов по разделам
 */

struct SettingsAccordion<Content: View>: View {
    let icon: String
    let title: String
    let subtitle: String?
    @Binding var isExpanded: Bool
    let content: () -> Content
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    init(
        icon: String,
        title: String,
        subtitle: String? = nil,
        isExpanded: Binding<Bool>,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self._isExpanded = isExpanded
        self.content = content
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Заголовок (кликабельный)
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isExpanded.toggle()
                }
                HapticFeedback.impact(.light)
            }) {
                HStack(spacing: Spacing.m) {
                    Text(icon)
                        .font(.system(size: 24))
                        .accessibilityLabel("Icon \(icon)")
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(title)
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                            .accessibilityAddTraits(.isHeader)
                            .dynamicTypeSize(...DynamicTypeSize.accessibility5)
                            .accessibilityAddTraits(.isHeader)
                        
                        if let subtitle = subtitle {
                            Text(subtitle)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .dynamicTypeSize(...DynamicTypeSize.accessibility5)
                        }
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(subtitle != nil ? "\(title). \(subtitle!)" : title)
                    
                    Spacer()
                    
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.textSecondary)
                        .animation(.easeInOut(duration: 0.2), value: isExpanded)
                        .accessibilityHidden(true)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
            }
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel(
                isExpanded
                    ? String(format: localizationManager.localized("accordion_expanded"), title)
                    : String(format: localizationManager.localized("accordion_collapsed"), title)
            )
            .accessibilityHint(
                isExpanded
                    ? localizationManager.localized("accordion_collapse_hint")
                    : localizationManager.localized("accordion_expand_hint")
            )
            .accessibilityAddTraits(.isButton)
            
            // Содержимое (показывается только когда развернуто)
            if isExpanded {
                VStack(spacing: Spacing.s) {
                    content()
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.1))
                )
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.textSecondary.opacity(0.2), lineWidth: 1)
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
}

