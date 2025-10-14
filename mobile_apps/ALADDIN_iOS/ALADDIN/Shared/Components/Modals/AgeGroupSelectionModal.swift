import SwiftUI

/**
 * 🎂 Age Group Selection Modal
 * Модальное окно выбора возрастной группы
 * Окно #2 в процессе регистрации
 */

struct AgeGroupSelectionModal: View {
    
    @Binding var isPresented: Bool
    @Binding var selectedAgeGroup: AgeGroup?
    
    var onAgeGroupSelected: (AgeGroup) -> Void
    
    // MARK: - Age Groups
    
    private let ageGroups: [(AgeGroup, String, String)] = [
        (.child_1_6, "1-6 лет", "Дошкольник"),
        (.child_7_12, "7-12 лет", "Школьник"),
        (.teen_13_17, "13-17 лет", "Подросток"),
        (.young_adult_18_23, "18-23 года", "Молодой взрослый"),
        (.adult_24_55, "24-55 лет", "Взрослый"),
        (.elderly_55_plus, "55+ лет", "Пожилой")
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
            
            // Modal content
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Text("🎂")
                        .font(.system(size: 40))
                    
                    Text("Ваша возрастная группа?")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(Color(hex: "#FCD34D"))  // Яркое золото из иконки!
                    
                    Text("(Для подбора защиты)")
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                }
                
                // Age options
                VStack(spacing: Spacing.m) {
                    ForEach(ageGroups, id: \.0) { ageGroup in
                        AgeOption(
                            ageRange: ageGroup.1,
                            description: ageGroup.2,
                            isSelected: selectedAgeGroup == ageGroup.0
                        ) {
                            selectAgeGroup(ageGroup.0)
                        }
                    }
                }
            }
            .padding(Spacing.xl)
            .frame(width: 340)
            .background(
                LinearGradient(
                    colors: [
                        Color(hex: "#0F172A"),  // Космический тёмный
                        Color(hex: "#1E3A8A"),  // Глубокий синий
                        Color(hex: "#3B82F6"),  // Электрический синий  
                        Color(hex: "#1E40AF")   // Королевский синий
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
        .transition(.asymmetric(
            insertion: .scale(scale: 0.8).combined(with: .opacity),
            removal: .scale(scale: 0.8).combined(with: .opacity)
        ))
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: isPresented)
    }
    
    // MARK: - Actions
    
    private func selectAgeGroup(_ ageGroup: AgeGroup) {
        selectedAgeGroup = ageGroup
        HapticFeedback.mediumImpact()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            onAgeGroupSelected(ageGroup)
        }
    }
}

// MARK: - Age Option Component

struct AgeOption: View {
    let ageRange: String
    let description: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                // Radio button
                ZStack {
                Circle()
                    .stroke(isSelected ? Color(hex: "#60A5FA") : Color.white.opacity(0.3), lineWidth: 2)  // Электрический синий!
                    .frame(width: 24, height: 24)
                
                if isSelected {
                    Circle()
                        .fill(Color(hex: "#60A5FA"))  // Электрический синий!
                        .frame(width: 14, height: 14)
                }
                }
                
                // Text
                VStack(alignment: .leading, spacing: 2) {
                    Text(ageRange)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.white)
                    
                    Text(description)
                        .font(.system(size: 13))
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            .frame(height: 40)
            .padding(.horizontal, Spacing.m)
            .background(
                isSelected
                    ? Color(hex: "#60A5FA").opacity(0.2)  // Электрический синий!
                    : Color.white.opacity(0.05)
            )
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        isSelected ? Color(hex: "#BAE6FD") : Color.white.opacity(0.1),  // Sirius голубой!
                        lineWidth: isSelected ? 2 : 1
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Age Group Enum

enum AgeGroup: String, Codable {
    case child_1_6 = "1-6"
    case child_7_12 = "7-12"
    case teen_13_17 = "13-17"
    case young_adult_18_23 = "18-23"
    case adult_24_55 = "24-55"
    case elderly_55_plus = "55+"
}

// MARK: - Preview

struct AgeGroupSelectionModal_Previews: PreviewProvider {
    static var previews: some View {
        AgeGroupSelectionModal(
            isPresented: .constant(true),
            selectedAgeGroup: .constant(nil),
            onAgeGroupSelected: { _ in }
        )
    }
}

