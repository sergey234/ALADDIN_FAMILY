import SwiftUI

/**
 * ℹ️ Dark Web Scan Explanation View
 * Подробные объяснения методов сканирования
 */

struct DarkWebScanExplanationView: View {
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.l) {
                    // Безопасное сканирование
                    explanationSection(
                        title: localizationManager.localized("dark_web_explanation_secure_title"),
                        icon: "lock.shield.fill",
                        color: .successGreen,
                        content: localizationManager.localized("dark_web_explanation_secure_content")
                    )
                    
                    // Быстрое сканирование
                    explanationSection(
                        title: localizationManager.localized("dark_web_explanation_fast_title"),
                        icon: "bolt.fill",
                        color: .warningOrange,
                        content: localizationManager.localized("dark_web_explanation_fast_content")
                    )
                    
                    // Рекомендации
                    recommendationsSection
                }
                .padding(Spacing.screenPadding)
            }
            .navigationTitle(localizationManager.localized("dark_web_explanation_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        dismiss()
                    }) {
                        Text(localizationManager.localized("common_done"))
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
        }
    }
    
    private func explanationSection(
        title: String,
        icon: String,
        color: Color,
        content: String
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                Text(title)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            
            Text(content)
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    private var recommendationsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("dark_web_explanation_recommendations_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                recommendationItem(
                    text: localizationManager.localized("dark_web_explanation_recommendation_1")
                )
                recommendationItem(
                    text: localizationManager.localized("dark_web_explanation_recommendation_2")
                )
                recommendationItem(
                    text: localizationManager.localized("dark_web_explanation_recommendation_3")
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.primaryBlue.opacity(0.1))
        )
    }
    
    private func recommendationItem(text: String) -> some View {
        HStack(alignment: .top, spacing: Spacing.xs) {
            Image(systemName: "checkmark.circle.fill")
                .font(.caption)
                .foregroundColor(.successGreen)
            Text(text)
                .font(.body)
                .foregroundColor(.textSecondary)
        }
    }
}

