import SwiftUI

/// 📋 Protection Level Explanation Modal
/// Модальное окно с объяснением уровней защиты

struct ProtectionLevelExplanationModal: View {
    
    @Binding var isPresented: Bool
    let currentLevel: Int
    @StateObject private var featuresManager = ProtectionFeaturesManager.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    VStack(spacing: Spacing.s) {
                        Text(localizationManager.localized("settings_levels_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("settings_levels_subtitle"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, Spacing.m)
                    
                    // Карточки уровней
                    VStack(spacing: Spacing.m) {
                        levelCard(
                            level: 0...25,
                            nameKey: "protection_level_low_name",
                            color: .red,
                            descriptionKey: "protection_level_low_desc",
                            icon: "shield.lefthalf.filled"
                        )
                        
                        levelCard(
                            level: 26...50,
                            nameKey: "protection_level_medium_name",
                            color: .orange,
                            descriptionKey: "protection_level_medium_desc",
                            icon: "shield.fill"
                        )
                        
                        levelCard(
                            level: 51...75,
                            nameKey: "protection_level_high_name",
                            color: .yellow,
                            descriptionKey: "protection_level_high_desc",
                            icon: "shield.checkered"
                        )
                        
                        levelCard(
                            level: 76...100,
                            nameKey: "protection_level_max_name",
                            color: .green,
                            descriptionKey: "protection_level_max_desc",
                            icon: "checkmark.shield.fill"
                        )
                    }
                }
                .padding(Spacing.m)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        .navigationTitle(localizationManager.localized("settings_levels_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                Button(localizationManager.localized("settings_levels_done")) {
                        isPresented = false
                    }
                    .foregroundColor(.primaryBlue)
                }
            }
        }
    }
    
    // MARK: - Level Card
    
    private func levelCard(level: ClosedRange<Int>, nameKey: String, color: Color, descriptionKey: String, icon: String) -> some View {
        let isCurrentLevel = level.contains(currentLevel)
        let levelInfo = featuresManager.getLevelDescription(level.lowerBound == 0 ? 25 : (level.lowerBound + level.upperBound) / 2)
        
        return VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок карточки
            HStack {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(color)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    HStack {
                        Text(localizationManager.localized(nameKey))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        if isCurrentLevel {
                            Text(localizationManager.localized("settings_levels_current"))
                                .font(.caption)
                                .foregroundColor(.primaryBlue)
                        }
                    }
                    
                    Text("\(level.lowerBound == 0 ? "0" : "\(level.lowerBound)")-\(level.upperBound)%")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if isCurrentLevel {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
            }
            
            // Описание
            Text(localizationManager.localized(descriptionKey))
                .font(.body)
                .foregroundColor(.textSecondary)
            
            Divider()
            
            // Список функций
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("settings_levels_includes"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                ForEach(levelInfo.features) { feature in
                    HStack(spacing: Spacing.s) {
                        Image(systemName: feature.icon)
                            .font(.system(size: 16))
                            .foregroundColor(color)
                            .frame(width: 20)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text(localizedFeatureName(feature))
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                            
                            Text(localizedFeatureDescription(feature))
                                .font(.captionSmall)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    .padding(.vertical, Spacing.xs)
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(isCurrentLevel ? 0.6 : 0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(isCurrentLevel ? color.opacity(0.5) : Color.clear, lineWidth: 2)
                )
        )
    }
    
    private func localizedFeatureName(_ feature: ProtectionFeature) -> String {
        localizationManager.localized("protection_feature_\(feature.id)_name")
    }
    
    private func localizedFeatureDescription(_ feature: ProtectionFeature) -> String {
        localizationManager.localized("protection_feature_\(feature.id)_desc")
    }
}

// MARK: - Preview

struct ProtectionLevelExplanationModal_Previews: PreviewProvider {
    static var previews: some View {
        ProtectionLevelExplanationModal(isPresented: .constant(true), currentLevel: 75)
            .environmentObject(LocalizationManager())
    }
}
