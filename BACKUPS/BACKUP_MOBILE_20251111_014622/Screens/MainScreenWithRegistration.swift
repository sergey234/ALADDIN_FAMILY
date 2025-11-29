import SwiftUI

/**
 * 📱 Main Screen with Progressive Registration
 * Обёртка для MainScreen с прогрессивной регистрацией
 * 
 * Показывает модальные окна регистрации поверх MainScreen:
 * - Окно #1: Выбор роли (через 0.5 сек)
 * - Окно #2: Выбор возраста (через 1 сек после роли)
 * - Окно #3: Выбор буквы (через 1 сек после возраста)
 * - Окно #4: Семья создана! (через 2 сек после буквы)
 * - Notification: Подсказка (через 5 сек после создания)
 */

struct MainScreenWithRegistration: View {
    
    @StateObject var registrationVM: FamilyRegistrationViewModel
    @State private var showTip: Bool = false
    var onComplete: (() -> Void)? = nil
    
    var body: some View {
        ZStack {
            // Фон вместо MainScreen
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            // Кнопка отмены (всегда видна)
            VStack {
                HStack {
                    Spacer()
                    Button("Отмена") {
                        onComplete?()
                    }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(Color.black.opacity(0.3))
                    .cornerRadius(20)
                }
                .padding(.top, 20)
                .padding(.horizontal, 20)
                Spacer()
            }
            
            // Consent Modal (показывается первым)
            if registrationVM.showConsentModal {
                ConsentModal(
                    isPresented: Binding(
                        get: { registrationVM.showConsentModal },
                        set: { registrationVM.showConsentModal = $0 }
                    ),
                    onConsentGiven: {
                        registrationVM.acceptConsent()
                    }
                )
            }
            
            // Progressive registration modals
            if registrationVM.showRoleModal {
                RoleSelectionModal(
                    isPresented: Binding(
                        get: { registrationVM.showRoleModal },
                        set: { registrationVM.showRoleModal = $0 }
                    ),
                    onRoleSelected: { role in
                        registrationVM.onRoleSelected(role)
                    }
                )
            }
            
            if registrationVM.showAgeGroupModal {
                VStack(spacing: 30) {
                    Text("Выберите возраст")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                    
                    // Показываем категории в зависимости от роли
                    if let role = registrationVM.selectedRole {
                        VStack(spacing: 16) {
                            ForEach(getAgeGroups(for: role), id: \.self) { ageGroup in
                                Button(action: {
                                    print("🚨 Нажата кнопка возраста - вызываю onAgeGroupSelected(.\(ageGroup.rawValue))")
                                    registrationVM.onAgeGroupSelected(ageGroup)
                                }) {
                                    HStack {
                                        Text(getAgeGroupLabel(ageGroup, for: role))
                                            .foregroundColor(.white)
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                            .foregroundColor(.white.opacity(0.7))
                                    }
                                    .padding(20)
                                    .background(Color.white.opacity(0.15))
                                    .cornerRadius(12)
                                }
                            }
                        }
                        .padding(.horizontal, 30)
                    }
                }
                .padding(30)
                .background(Color.black.opacity(0.3))
                .cornerRadius(20)
            }
            
            if registrationVM.showLetterModal {
                VStack(spacing: 30) {
                    Text("Выберите букву")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                    
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: 12) {
                        ForEach(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"], id: \.self) { letter in
                            Button(action: {
                                registrationVM.onLetterSelected(letter)
                            }) {
                                Text(letter)
                                    .font(.system(size: 20, weight: .bold))
                                    .foregroundColor(.white)
                                    .frame(width: 50, height: 50)
                                    .background(Color.white.opacity(0.15))
                                    .cornerRadius(12)
                            }
                        }
                    }
                }
                .padding(30)
                .background(Color.black.opacity(0.3))
                .cornerRadius(20)
            }
            
            // Recovery Code Modal (full-screen)
            if registrationVM.showFamilyCreatedModal,
               let familyID = registrationVM.familyID,
               let recoveryCode = registrationVM.recoveryCode {
                RecoveryCodeModal(
                    isPresented: Binding(
                        get: { registrationVM.showFamilyCreatedModal },
                        set: { registrationVM.showFamilyCreatedModal = $0 }
                    ),
                    recoveryCode: recoveryCode,
                    familyID: familyID,
                    onComplete: {
                        // После закрытия RecoveryCodeModal вызываем onComplete
                        onComplete?()
                        print("✅ RecoveryCodeModal закрыт, семья создана")
                    }
                )
            }
            
            if registrationVM.showSuccessModal {
                VStack {
                    Text("Регистрация успешна!")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Text("Добро пожаловать в семью!")
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Button("Продолжить") {
                        registrationVM.showSuccessModal = false
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                .background(Color.green)
                .cornerRadius(10)
            }
            
            // Tip notification
            if showTip {
                VStack {
                    TipNotification(
                        isPresented: $showTip,
                        message: "Хотите добавить членов семьи?\n→ Настройки → Семья → \"Добавить члена семьи\""
                    )
                    .padding(.top, 60)
                    
                    Spacer()
                }
                .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Экран регистрации семьи")
        .task {
            print("🚨 MainScreenWithRegistration загружен!")
            // Start registration immediately without checking
            try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
            print("🚨 Вызываю startRegistration()...")
            registrationVM.startRegistration()
            print("✅ Регистрация запущена, showRoleModal = \(registrationVM.showRoleModal)")
        }
    }
    
    // MARK: - Helper Methods
    
    private func hasFamilyRegistration() -> Bool {
        // Check UserDefaults for family_id
        // TODO: В будущем заменить на Keychain для безопасности
        return UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.familyId) != nil
    }
    
    // MARK: - Age Groups Helpers
    
    private func getAgeGroups(for role: FamilyRole) -> [AgeGroup] {
        switch role {
        case .parent:
            return [.adult]
        case .child:
            return [.toddler, .child]
        case .teenager:
            return [.teen]
        case .elderly:
            return [.senior]
        }
    }
    
    private func getAgeGroupLabel(_ ageGroup: AgeGroup, for role: FamilyRole) -> String {
        switch role {
        case .parent:
            return "18+"
        case .child:
            switch ageGroup {
            case .toddler: return "1-6 лет"
            case .child: return "7-12 лет"
            case .teen: return "13-17 лет"
            case .adult: return "18-22 лет"
            case .senior: return "50+"
            }
        case .teenager:
            return "13-17 лет"
        case .elderly:
            return "60+"
        }
    }
}

// MARK: - Tip Notification Component

struct TipNotification: View {
    
    @Binding var isPresented: Bool
    let message: String
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Text("💡 Совет")
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.white)
                        .accessibilityLabel("Совет")
                    
                    Spacer()
                    
                    Button(action: {
                        withAnimation {
                            isPresented = false
                        }
                    }) {
                        Image(systemName: "xmark")
                            .font(.system(size: 12))
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel("Закрыть совет")
                    .accessibilityHint("Нажмите для закрытия уведомления")
                }
                
                Text(message)
                    .font(.system(size: 13))
                    .foregroundColor(.white)
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityLabel("Совет: \(message)")
                
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        // Navigate to settings
                        isPresented = false
                    }) {
                        Text("ПОКАЖИТЕ КАК")
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.white.opacity(0.2))
                            .cornerRadius(8)
                    }
                    .accessibilityLabel("Покажите как")
                    .accessibilityHint("Нажмите для перехода к настройкам семьи")
                    
                    Button(action: {
                        withAnimation {
                            isPresented = false
                        }
                    }) {
                        Text("ПОЗЖЕ")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    .accessibilityLabel("Позже")
                    .accessibilityHint("Нажмите для отложения совета")
                }
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: 340)
        .background(
            Color.secondaryGold.opacity(0.95)
                .blur(radius: 10)
        )
        .cornerRadius(16)
        .shadow(color: Color.secondaryGold.opacity(0.3), radius: 10)
        .padding(.horizontal, Spacing.m)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Уведомление с советом")
    }
}

// MARK: - Preview

struct MainScreenWithRegistration_Previews: PreviewProvider {
    static var previews: some View {
        MainScreenWithRegistration(
            registrationVM: FamilyRegistrationViewModel()
        )
    }
}



