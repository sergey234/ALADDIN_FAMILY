import SwiftUI

struct ThreatProtectionCategoriesView: View {
    @Binding var expandedCategory: ThreatProtectionCategory?
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            ForEach(ThreatProtectionCategory.allCases) { category in
                categorySection(for: category)
            }
        }
    }
    
    private func categorySection(for category: ThreatProtectionCategory) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.2, dampingFraction: 0.8)) {
                    if expandedCategory == category {
                        expandedCategory = nil
                    } else {
                        expandedCategory = category
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.s) {
                    Text(category.emoji)
                        .font(.system(size: 20))
                    
                    Text(category.localizedTitle(localizationManager))
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    Text("(\(category.count))")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Image(systemName: expandedCategory == category ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.s)
            }
            
            if expandedCategory == category {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    ForEach(Array(category.localizedThreats(localizationManager).enumerated()), id: \.offset) { _, threat in
                        HStack(spacing: Spacing.xs) {
                            Circle()
                                .fill(Color.secondaryGold.opacity(0.3))
                                .frame(width: 4, height: 4)
                            
                            Text(threat)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(.leading, Spacing.l)
                .padding(.top, Spacing.xs)
                .padding(.bottom, Spacing.s)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(.vertical, Spacing.xs)
    }
}
