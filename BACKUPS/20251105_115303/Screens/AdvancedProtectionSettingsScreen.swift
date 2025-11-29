import SwiftUI

/// ⚙️ Advanced Protection Settings Screen
/// Экран расширенных настроек защиты с переключателями функций

struct AdvancedProtectionSettingsScreen: View {
    
    @Environment(\.dismiss) private var dismiss
    @StateObject private var featuresManager = ProtectionFeaturesManager.shared
    @State private var currentLevel: Double = UserDefaults.standard.double(forKey: "protectionLevel")
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    Text("Расширенные настройки")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Color.clear.frame(width: 40, height: 40)
                }
                .padding()
                .background(Color.black.opacity(0.5))
                
                // Основной контент
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Информация о текущем уровне
                        currentLevelInfo
                        
                        // Список функций
                        featuresList
                        
                        // Подсказка
                        infoCard
                    }
                    .padding(Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            if currentLevel == 0 {
                currentLevel = 75
            }
            featuresManager.applyProtectionLevel(Int(currentLevel))
        }
    }
    
    // MARK: - Current Level Info
    
    private var currentLevelInfo: some View {
        let levelInfo = featuresManager.getLevelDescription(Int(currentLevel))
        
        return VStack(spacing: Spacing.m) {
            HStack {
                Text("Текущий уровень")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text("\(Int(currentLevel))%")
                    .font(.h2)
                    .foregroundColor(protectionColor)
            }
            
            Text(levelInfo.name)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            
            Text(levelInfo.description)
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    // MARK: - Features List
    
    private var featuresList: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ФУНКЦИИ ЗАЩИТЫ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                ForEach(featuresManager.features) { feature in
                    featureRow(feature: feature)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    // MARK: - Feature Row
    
    private func featureRow(feature: ProtectionFeature) -> some View {
        let isRecommended = feature.isEnabledAtLevel(Int(currentLevel))
        
        return HStack(alignment: .top, spacing: Spacing.m) {
            // Иконка
            Image(systemName: feature.icon)
                .font(.system(size: 24))
                .foregroundColor(feature.isEnabled ? .primaryBlue : .textSecondary)
                .frame(width: 40, alignment: .leading)
            
            // Информация - выровнено по левому краю, без переносов
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                // Название функции - без переносов по слогам, выровнено по левому краю
                HStack(alignment: .firstTextBaseline, spacing: Spacing.xs) {
                    Text(feature.name)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    if isRecommended && !feature.isEnabled {
                        Text("(Рекомендуется)")
                            .font(.caption)
                            .foregroundColor(.orange)
                            .lineLimit(1)
                            .fixedSize(horizontal: true, vertical: false)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                // Описание - без переносов слов по слогам, выровнено по левому краю
                Text(feature.description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(nil)
                    .fixedSize(horizontal: false, vertical: true)
                    .multilineTextAlignment(.leading)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            // Переключатель
            ALADDINToggle(isOn: Binding(
                get: { feature.isEnabled },
                set: { newValue in
                    featuresManager.toggleFeature(id: feature.id)
                }
            ))
            .padding(.leading, Spacing.s)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(feature.isEnabled ? 
                      Color.primaryBlue.opacity(0.1) : 
                      Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Image(systemName: "info.circle.fill")
                    .foregroundColor(.primaryBlue)
                
                Text("Информация")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Text("Вы можете включать и выключать функции защиты вручную. Однако мы рекомендуем использовать рекомендованные функции для вашего уровня защиты.")
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.primaryBlue.opacity(0.1))
        )
    }
    
    // MARK: - Helper
    
    private var protectionColor: Color {
        switch currentLevel {
        case 0...25: return .red
        case 26...50: return .orange
        case 51...75: return .yellow
        case 76...100: return .green
        default: return .primaryBlue
        }
    }
}

// MARK: - Preview

struct AdvancedProtectionSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AdvancedProtectionSettingsScreen()
    }
}
