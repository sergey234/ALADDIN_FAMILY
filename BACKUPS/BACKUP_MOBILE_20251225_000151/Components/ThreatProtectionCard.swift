import SwiftUI

struct ThreatProtectionCard: View {
    let icon: String
    let title: String
    let subtitle: String
    @Binding var isExpanded: Bool
    @Binding var expandedCategory: ThreatProtectionCategory?
    var allowCollapse: Bool = true
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 0) {
            header
            
            if isExpanded {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    ThreatProtectionCategoriesView(expandedCategory: $expandedCategory)
                        .padding(.horizontal, Spacing.m)
                        .padding(.bottom, Spacing.m)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
    
    @ViewBuilder
    private var header: some View {
        let content = HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.leading)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.leading)
                
                // ✅ ЛЕГЕНДА: Объяснение цветовых индикаторов (все на одной строке)
                if isExpanded {
                    HStack(spacing: Spacing.s) {
                        // 🟢 Включено
                        HStack(spacing: Spacing.xxs) {
                            Circle()
                                .fill(Color.successGreen)
                                .frame(width: 8, height: 8)
                            Text(localizationManager.localized("protection_status_available"))
                                .font(.caption2)
                                .foregroundColor(.textTertiary)
                        }
                        
                        // 🟡 Доступно
                        HStack(spacing: Spacing.xxs) {
                            Circle()
                                .fill(Color.warningOrange)
                                .frame(width: 8, height: 8)
                            Text(localizationManager.localized("protection_status_partial"))
                                .font(.caption2)
                                .foregroundColor(.textTertiary)
                        }
                        
                        // 🔴 Нужен тариф
                        HStack(spacing: Spacing.xxs) {
                            Circle()
                                .fill(Color.dangerRed)
                                .frame(width: 8, height: 8)
                            Text(localizationManager.localized("protection_status_unavailable"))
                                .font(.caption2)
                                .foregroundColor(.textTertiary)
                        }
                        
                        Spacer()
                    }
                    .padding(.top, Spacing.xxs)
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
            
            Spacer()
            
            if allowCollapse {
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .foregroundColor(.secondaryGold)
                    .font(.headline)
                    .frame(width: 24)
            }
        }
        .padding(Spacing.m)
        
        if allowCollapse {
            Button(action: toggleExpanded) {
                content
            }
        } else {
            content
        }
    }
    
    private func toggleExpanded() {
        withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
            isExpanded.toggle()
        }
        HapticFeedback.selection()
    }
}
