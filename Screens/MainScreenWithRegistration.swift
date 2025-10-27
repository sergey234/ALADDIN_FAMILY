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
    
    var body: some View {
        ZStack {
            // Main Screen (основной экран)
            MainScreen()
            
            // Progressive registration modals
            if registrationVM.showRoleModal {
                VStack {
                    Text("Выберите роль")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Button("Родитель") {
                        registrationVM.selectedRole = .parent
                        registrationVM.showRoleModal = false
                    }
                    .buttonStyle(.borderedProminent)
                    
                    Button("Отмена") {
                        registrationVM.showRoleModal = false
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                .background(Color.blue)
                .cornerRadius(10)
            }
            
            if registrationVM.showAgeGroupModal {
                VStack {
                    Text("Выберите возрастную группу")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Button("Взрослый") {
                        registrationVM.selectedAgeGroup = .adult
                        registrationVM.showAgeGroupModal = false
                    }
                    .buttonStyle(.borderedProminent)
                    
                    Button("Отмена") {
                        registrationVM.showAgeGroupModal = false
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                .background(Color.green)
                .cornerRadius(10)
            }
            
            if registrationVM.showLetterModal {
                VStack {
                    Text("Выберите букву")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Button("A") {
                        registrationVM.selectedLetter = "A"
                        registrationVM.showLetterModal = false
                    }
                    .buttonStyle(.borderedProminent)
                    
                    Button("Отмена") {
                        registrationVM.showLetterModal = false
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                .background(Color.orange)
                .cornerRadius(10)
            }
            
            if registrationVM.showFamilyCreatedModal,
               let familyID = registrationVM.familyID,
               let recoveryCode = registrationVM.recoveryCode {
                VStack {
                    Text("Семья создана!")
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Text("ID: \(familyID)")
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Text("Код: \(recoveryCode)")
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Button("Закрыть") {
                        registrationVM.showFamilyCreatedModal = false
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                .background(Color.purple)
                .cornerRadius(10)
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
        .accessibilityLabel("Главный экран с регистрацией семьи")
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 MainScreenWithRegistration загружен!")
            // Check if family already exists
            if !hasFamilyRegistration() {
                // Start progressive registration after 0.5 seconds
                try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
                registrationVM.startRegistration()
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func hasFamilyRegistration() -> Bool {
        // Check UserDefaults for family_id
        // TODO: В будущем заменить на Keychain для безопасности
        return UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.familyId) != nil
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



