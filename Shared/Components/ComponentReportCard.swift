import SwiftUI

/**
 * 📊 Component Report Card
 * Карточка компонента для отображения краткой статистики в Аналитике
 * Используется в разделе "Компоненты защиты"
 */

struct ComponentReportCard: View {
    
    // MARK: - Properties
    
    let componentId: String
    let icon: String
    let title: String
    let metrics: [(String, String)] // [(ключ, значение)]
    let color: Color
    let badgeCount: Int? // Количество новых событий (для Badge)
    let onTap: () -> Void
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            // Анимация нажатия
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                onTap()
            }
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка с badge
                iconWithBadge
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                    
                    // Метрики (максимум 2)
                    ForEach(Array(metrics.prefix(2)), id: \.0) { key, value in
                        HStack(spacing: Spacing.xs) {
                            Text(key)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text(value)
                                .font(.captionBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityHint(accessibilityHint)
    }
    
    // MARK: - Icon with Badge
    
    private var iconWithBadge: some View {
        ZStack {
            // Фон иконки
            Circle()
                .fill(color.opacity(0.2))
                .frame(width: 50, height: 50)
            
            // Иконка
            Text(icon)
                .font(.system(size: 24))
            
            // Badge для новых событий
            if let count = badgeCount, count > 0 {
                Text("\(count)")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .padding(4)
                    .frame(minWidth: 18, minHeight: 18)
                    .background(Color.dangerRed)
                    .clipShape(Circle())
                    .overlay(
                        Circle()
                            .stroke(Color.backgroundDark, lineWidth: 2)
                    )
                    .offset(x: 18, y: -18)
                    .accessibilityLabel("\(count) новых событий")
            }
        }
    }
    
    // MARK: - Accessibility
    
    private var accessibilityLabel: String {
        var label = title
        for (key, value) in metrics.prefix(2) {
            label += ", \(key): \(value)"
        }
        if let count = badgeCount, count > 0 {
            label += ", \(count) новых событий"
        }
        return label
    }
    
    private var accessibilityHint: String {
        return localizationManager.localized("component_report_card_accessibility_hint")
    }
}

// MARK: - Preview

#if DEBUG
struct ComponentReportCard_Previews: PreviewProvider {
    static var previews: some View {
    ZStack {
        LinearGradient.backgroundGradient
            .ignoresSafeArea()
        
        VStack(spacing: Spacing.m) {
            ComponentReportCard(
                componentId: "driving_reports_agent",
                icon: "🚗",
                title: "Отчеты о вождении",
                metrics: [
                    ("Поездок", "12"),
                    ("Безопасность", "8.5/10")
                ],
                color: .primaryBlue,
                badgeCount: 3,
                onTap: { print("Tapped") }
            )
            
            ComponentReportCard(
                componentId: "dark_web_monitoring_agent",
                icon: "🌑",
                title: "Мониторинг Дарк вэб",
                metrics: [
                    ("Утечек найдено", "3"),
                    ("Новых за неделю", "0")
                ],
                color: .dangerRed,
                badgeCount: 1,
                onTap: { print("Tapped") }
            )
            
            ComponentReportCard(
                componentId: "identity_theft_protection_agent",
                icon: "🛡️",
                title: "Защита кражи личности",
                metrics: [
                    ("Попыток кражи", "0"),
                    ("Заблокировано", "47")
                ],
                color: .primaryBlue,
                badgeCount: nil,
                onTap: { print("Tapped") }
            )
        }
        .padding()
    }
    .environmentObject(LocalizationManager())
    }
}
#endif

