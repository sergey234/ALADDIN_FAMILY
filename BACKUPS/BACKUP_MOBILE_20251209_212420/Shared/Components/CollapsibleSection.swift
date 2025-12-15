import SwiftUI

/// Раздвигающаяся секция (Accordion) для RewardsModalView
struct CollapsibleSection<Content: View>: View {
    let icon: String
    let title: String
    let subtitle: String?
    @Binding var isExpanded: Bool
    let content: () -> Content
    
    init(icon: String, title: String, subtitle: String? = nil, isExpanded: Binding<Bool>, @ViewBuilder content: @escaping () -> Content) {
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
                HStack {
                    Text(icon)
                        .font(.system(size: 20))
                        .accessibilityLabel("Иконка \(icon)")
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(title)
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                        
                        if let subtitle = subtitle {
                            Text(subtitle)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    Spacer()
                    
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.textSecondary)
                        .animation(.easeInOut(duration: 0.2), value: isExpanded)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
            }
            .buttonStyle(PlainButtonStyle())
            
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

