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
    
    @ObservedObject var registrationVM: FamilyRegistrationViewModel
    @State private var showTip: Bool = false
    
    var body: some View {
        ZStack {
            // Main Screen (основной экран)
            MainScreen()
            
            // Progressive registration modals
            if registrationVM.showRoleModal {
                RoleSelectionModal(
                    isPresented: $registrationVM.showRoleModal,
                    selectedRole: $registrationVM.selectedRole,
                    onRoleSelected: registrationVM.onRoleSelected
                )
            }
            
            if registrationVM.showAgeGroupModal {
                AgeGroupSelectionModal(
                    isPresented: $registrationVM.showAgeGroupModal,
                    selectedAgeGroup: $registrationVM.selectedAgeGroup,
                    onAgeGroupSelected: registrationVM.onAgeGroupSelected
                )
            }
            
            if registrationVM.showLetterModal {
                LetterSelectionModal(
                    isPresented: $registrationVM.showLetterModal,
                    selectedLetter: $registrationVM.selectedLetter,
                    onLetterSelected: registrationVM.onLetterSelected
                )
            }
            
            if registrationVM.showFamilyCreatedModal,
               let familyID = registrationVM.familyID,
               let recoveryCode = registrationVM.recoveryCode {
                FamilyCreatedModal(
                    isPresented: $registrationVM.showFamilyCreatedModal,
                    familyID: familyID,
                    recoveryCode: recoveryCode,
                    onContinue: {
                        registrationVM.showFamilyCreatedModal = false
                        
                        // Show tip after 5 seconds
                        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0) {
                            showTip = true
                            
                            // Auto-dismiss tip after 10 seconds
                            DispatchQueue.main.asyncAfter(deadline: .now() + 10.0) {
                                withAnimation {
                                    showTip = false
                                }
                            }
                        }
                    }
                )
            }
            
            if registrationVM.showSuccessModal {
                RegistrationSuccessModal(
                    isPresented: $registrationVM.showSuccessModal,
                    mode: .joined,
                    familyMembers: registrationVM.familyMembers,
                    onContinue: {
                        registrationVM.showSuccessModal = false
                    }
                )
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
        .onAppear {
            // Check if family already exists
            if !hasFamilyRegistration() {
                // Start progressive registration after 0.5 seconds
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    registrationVM.startRegistration()
                }
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
                }
                
                Text(message)
                    .font(.system(size: 13))
                    .foregroundColor(.white)
                    .fixedSize(horizontal: false, vertical: true)
                
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
                    
                    Button(action: {
                        withAnimation {
                            isPresented = false
                        }
                    }) {
                        Text("ПОЗЖЕ")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
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



