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
    @EnvironmentObject private var localizationManager: LocalizationManager
    var onComplete: (() -> Void)? = nil
    
    var body: some View {
        ZStack {
            backgroundView
            cancelButtonView
            
            registrationModalsView
            loadingOrErrorView
            recoveryCodeModalView
            successModalView
            tipNotificationView
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
    
    // MARK: - Helper Views
    
    private var backgroundView: some View {
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
    }
            
    private var cancelButtonView: some View {
            VStack {
                HStack {
                    Spacer()
                    Button(localizationManager.localized("common_cancel")) {
                        print("✅ [MainScreenWithRegistration] Кнопка 'Отмена' нажата, вызываем onComplete")
                        onComplete?()
                    }
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(Color.black.opacity(0.3))
                    .cornerRadius(20)
                    .accessibilityLabel(localizationManager.localized("common_cancel"))
                }
                .padding(.top, 20)
                .padding(.horizontal, 20)
                Spacer()
            }
    }
    
    private var loadingView: some View {
        VStack(spacing: 20) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                .scaleEffect(1.5)
            
            Text(localizationManager.localized("registration_creating_family"))
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(.white)
            
            if let role = registrationVM.selectedRole, role == .teenager {
                Text("Создание семьи для подростка...")
                    .font(.system(size: 14))
                    .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding(40)
        .background(Color.black.opacity(0.5))
        .cornerRadius(20)
    }
    
    private var registrationModalsView: some View {
        Group {
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
                ageGroupSelectionView
            }
            
            if registrationVM.showLetterModal {
                letterSelectionView
            }
        }
    }
    
    private var ageGroupSelectionView: some View {
                VStack(spacing: 30) {
                    Text(localizationManager.localized("registration_select_age"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                    
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
            
    private var letterSelectionView: some View {
                VStack(spacing: 30) {
                    Text(localizationManager.localized("registration_select_letter"))
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
            
    private var loadingOrErrorView: some View {
        Group {
            if registrationVM.isLoading || registrationVM.currentStep == .creatingFamily {
                loadingView
            }
            
            if let errorMessage = registrationVM.errorMessage, !errorMessage.isEmpty {
                errorView(errorMessage: errorMessage)
            }
        }
    }
    
    private var recoveryCodeModalView: some View {
        Group {
            if registrationVM.showFamilyCreatedModal,
               let familyID = registrationVM.familyID,
               let recoveryCode = registrationVM.recoveryCode {
                RecoveryCodeModal(
                    isPresented: Binding(
                        get: { registrationVM.showFamilyCreatedModal },
                        set: { newValue in
                            registrationVM.showFamilyCreatedModal = newValue
                            if !newValue {
                                print("✅ RecoveryCodeModal закрыт через setter")
                            }
                        }
                    ),
                    recoveryCode: recoveryCode,
                    familyID: familyID,
                    onComplete: {
                        UserDefaults.standard.synchronize()
                        onComplete?()
                        print("✅ RecoveryCodeModal: onComplete вызван")
                    }
                )
            }
        }
            }
            
    private var successModalView: some View {
        Group {
            if registrationVM.showSuccessModal {
                VStack {
                    Text(localizationManager.localized("registration_success_title"))
                        .font(.title)
                        .foregroundColor(.white)
                    
                    Text(localizationManager.localized("registration_success_message"))
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Button(localizationManager.localized("common_continue")) {
                        registrationVM.showSuccessModal = false
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                .background(Color.green)
                .cornerRadius(10)
            }
        }
            }
            
    private var tipNotificationView: some View {
        Group {
            if showTip {
                VStack {
                    TipNotification(
                        isPresented: $showTip,
                        message: localizationManager.localized("registration_tip_add_members")
                    )
                    .environmentObject(localizationManager)
                    .padding(.top, 60)
                    
                    Spacer()
                }
                .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
    }
    
    private func errorView(errorMessage: String) -> some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 48))
                .foregroundColor(.red)
            
            Text(localizationManager.localized("registration_error_title"))
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.white)
            
            Text(errorMessage)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.9))
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            Button(localizationManager.localized("common_retry")) {
                // Повторяем создание семьи
                if let role = registrationVM.selectedRole,
                   let ageGroup = registrationVM.selectedAgeGroup,
                   let letter = registrationVM.selectedLetter {
                    registrationVM.errorMessage = nil
                    registrationVM.createFamily()
                }
            }
            .buttonStyle(.borderedProminent)
            .padding(.top, 10)
            
            Button(localizationManager.localized("common_cancel")) {
                registrationVM.errorMessage = nil
                onComplete?()
            }
            .foregroundColor(.white.opacity(0.8))
        }
        .padding(30)
        .background(Color.black.opacity(0.7))
        .cornerRadius(20)
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
            // ✅ ИСПРАВЛЕНИЕ: Добавлены все возрастные группы для детей
            return [.toddler, .child, .teen, .adult]
        case .teenager:
            return [.teen]
        case .elderly:
            return [.senior]
        }
    }
    
    private func getAgeGroupLabel(_ ageGroup: AgeGroup, for role: FamilyRole) -> String {
        switch role {
        case .parent:
            return localizationManager.localized("age_group_adult_short")
        case .child:
            switch ageGroup {
            case .toddler: return localizationManager.localized("age_group_toddler_short")
            case .child: return localizationManager.localized("age_group_child_short")
            case .teen: return localizationManager.localized("age_group_teen_short")
            case .adult: return localizationManager.localized("age_group_adult_short")
            case .senior: return localizationManager.localized("age_group_senior_short")
            }
        case .teenager:
            return localizationManager.localized("age_group_teen_short")
        case .elderly:
            return localizationManager.localized("age_group_elderly_short")
        }
    }
}

// MARK: - Tip Notification Component

struct TipNotification: View {
    
    @Binding var isPresented: Bool
    let message: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Text(localizationManager.localized("tip_title"))
                        .font(.system(size: 14, weight: .bold))
                        .foregroundColor(.white)
                        .accessibilityLabel(localizationManager.localized("tip_title"))
                    
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
                        Text(localizationManager.localized("tip_show_how"))
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.m)
                            .padding(.vertical, Spacing.xs)
                            .background(Color.white.opacity(0.2))
                            .cornerRadius(8)
                    }
                    .accessibilityLabel(localizationManager.localized("tip_show_how"))
                    .accessibilityHint(localizationManager.localized("tip_show_how_hint"))
                    
                    Button(action: {
                        withAnimation {
                            isPresented = false
                        }
                    }) {
                        Text(localizationManager.localized("tip_later"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                    .accessibilityLabel(localizationManager.localized("tip_later"))
                    .accessibilityHint(localizationManager.localized("tip_later_hint"))
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



