import SwiftUI

/// 📋 Protection Level Explanation Modal
/// Модальное окно с объяснением уровней защиты

struct ProtectionLevelExplanationModal: View {
    
    @Binding var isPresented: Bool
    let currentLevel: Int
    @StateObject private var featuresManager = ProtectionFeaturesManager.shared
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    VStack(spacing: Spacing.s) {
                        Text("УРОВНИ ЗАЩИТЫ")
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                        
                        Text("Выберите уровень защиты, который подходит вашей семье")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, Spacing.m)
                    
                    // Карточки уровней
                    VStack(spacing: Spacing.m) {
                        levelCard(
                            level: 0...25,
                            name: "Низкий",
                            color: .red,
                            description: "Базовая защита с минимальными функциями. Подходит для взрослых пользователей.",
                            icon: "shield.lefthalf.filled"
                        )
                        
                        levelCard(
                            level: 26...50,
                            name: "Средний",
                            color: .orange,
                            description: "Стандартная защита для обычного использования. Блокировка основных угроз.",
                            icon: "shield.fill"
                        )
                        
                        levelCard(
                            level: 51...75,
                            name: "Высокий",
                            color: .yellow,
                            description: "Максимальная защита для детей и уязвимых пользователей. Полный контроль.",
                            icon: "shield.checkered"
                        )
                        
                        levelCard(
                            level: 76...100,
                            name: "Максимальный",
                            color: .green,
                            description: "Полная защита от всех угроз. Строгий контроль и мониторинг.",
                            icon: "checkmark.shield.fill"
                        )
                    }
                }
                .padding(Spacing.m)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationTitle("Уровни защиты")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        isPresented = false
                    }
                    .foregroundColor(.primaryBlue)
                }
            }
        }
    }
    
    // MARK: - Level Card
    
    private func levelCard(level: ClosedRange<Int>, name: String, color: Color, description: String, icon: String) -> some View {
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
                        Text(name)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        if isCurrentLevel {
                            Text("(Текущий)")
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
            Text(description)
                .font(.body)
                .foregroundColor(.textSecondary)
            
            Divider()
            
            // Список функций
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("Включает функции:")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                ForEach(levelInfo.features) { feature in
                    HStack(spacing: Spacing.s) {
                        Image(systemName: feature.icon)
                            .font(.system(size: 16))
                            .foregroundColor(color)
                            .frame(width: 20)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text(feature.name)
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                            
                            Text(feature.description)
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
}

// MARK: - Preview

struct ProtectionLevelExplanationModal_Previews: PreviewProvider {
    static var previews: some View {
        ProtectionLevelExplanationModal(isPresented: .constant(true), currentLevel: 75)
    }
}
