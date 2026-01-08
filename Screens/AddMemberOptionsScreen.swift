import SwiftUI

/**
 * 👨‍👩‍👧‍👦 Add Member Options Screen
 * Экран выбора способа добавления члена семьи
 * 
 * Варианты:
 * 1. Создать новую семью (MainScreenWithRegistration)
 * 2. Сканировать QR-код (QRScannerModal)
 * 3. Ввести код приглашения (InvitationCodeInputModal)
 */

struct AddMemberOptionsScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showCreateFamily: Bool = false
    @State private var showQRScanner: Bool = false
    @State private var showCodeInput: Bool = false
    @State private var scannedCode: String = ""
    @State private var familyCreated: Bool = false
    @State private var isProcessingCreateFamily: Bool = false // ✅ Защита от двойного клика
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 20) {
                // Кнопка назад
                HStack {
                    Button(action: {
                        // ✅ ИСПРАВЛЕНИЕ: Используем navigationManager.goBack() для правильной навигации
                        // как на других экранах, открытых через NavigationManager
                        navigationManager.goBack()
                    }) {
                        HStack {
                            Image(systemName: "chevron.left")
                                .foregroundColor(.white)
                            Text(localizationManager.localized("common_back"))
                                .foregroundColor(.white)
                        }
                    }
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                // Заголовок
                VStack(spacing: 8) {
                    Text(localizationManager.localized("add_member_title"))
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text(localizationManager.localized("add_member_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.8))
                }
                .padding(.top, 10)
                
                // Варианты добавления
                VStack(spacing: 12) {
                    // Вариант 1: Создать новую семью
                    optionButton(
                        icon: "plus.circle.fill",
                        title: localizationManager.localized("add_member_create_family"),
                        description: localizationManager.localized("add_member_create_family_desc"),
                        color: .orange
                    ) {
                        // ✅ ИСПРАВЛЕНИЕ: Предотвращаем двойной клик
                        guard !isProcessingCreateFamily && !showCreateFamily else {
                            print("⚠️ AddMemberOptionsModal: Попытка повторного открытия регистрации, игнорируем")
                            return
                        }
                        
                        isProcessingCreateFamily = true
                        print("✅ AddMemberOptionsModal: Открываем регистрацию семьи")
                        
                        // Сначала открываем регистрацию
                        showCreateFamily = true
                        
                        // ✅ ИСПРАВЛЕНИЕ: Не закрываем экран, просто открываем регистрацию
                        // Экран закроется автоматически после создания семьи через onChange
                    }
                    
                    // Вариант 2: Сканировать QR-код
                    optionButton(
                        icon: "qrcode.viewfinder",
                        title: localizationManager.localized("add_member_scan_qr"),
                        description: localizationManager.localized("add_member_scan_qr_desc"),
                        color: .blue
                    ) {
                        showQRScanner = true
                    }
                    
                    // Вариант 3: Ввести код
                    optionButton(
                        icon: "textformat.123",
                        title: localizationManager.localized("add_member_enter_code"),
                        description: localizationManager.localized("add_member_enter_code_desc"),
                        color: .green
                    ) {
                        showCodeInput = true
                    }
                }
                
                // Текст о конфиденциальности
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "lock.shield.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.blue)
                        Text(localizationManager.localized("add_member_privacy_title"))
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.primary)
                    }
                    
                    Text(localizationManager.localized("add_member_privacy_text"))
                        .font(.system(size: 12))
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(16)
                .background(Color.blue.opacity(0.05))
                .cornerRadius(12)
                
                Spacer()
                
                // Кнопка отмены
                Button(localizationManager.localized("add_member_cancel")) {
                    // ✅ ИСПРАВЛЕНИЕ: Используем navigationManager.goBack() для правильной навигации
                    navigationManager.goBack()
                }
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
                .padding(.bottom, 20)
            }
            .padding(.horizontal, 20)
            .id("add_member_screen_lang_\(localizationManager.currentLanguage.rawValue)")
        }
        .fullScreenCover(isPresented: $showCreateFamily) {
            MainScreenWithRegistration(
                registrationVM: FamilyRegistrationViewModel(),
                onComplete: {
                    print("✅ [AddMemberOptionsScreen] Регистрация завершена, закрываем модал")
                    showCreateFamily = false
                    isProcessingCreateFamily = false
                    
                    // ✅ НОВОЕ: Проверяем роль и навигируем на соответствующий интерфейс
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                        checkRoleAndNavigate()
                    }
                }
            )
        }
        .fullScreenCover(isPresented: $showQRScanner) {
            QRScannerModal { code in
                // После сканирования QR автоматически открываем ввод кода
                scannedCode = code
                showQRScanner = false
                // Открываем ввод кода после закрытия сканера
                DispatchQueue.main.async {
                    showCodeInput = true
                }
            }
        }
        .sheet(isPresented: $showCodeInput) {
            InvitationCodeInputModal(
                isPresented: $showCodeInput,
                initialCode: scannedCode.isEmpty ? nil : scannedCode
            )
        }
        .onChange(of: showCodeInput) { newValue in
            if !newValue {
                // Сбрасываем scannedCode после закрытия
                scannedCode = ""
            }
        }
        .onChange(of: showCreateFamily) { newValue in
            // ✅ ИСПРАВЛЕНИЕ: Когда модал закрывается, проверяем создание семьи и навигируем
            if !newValue {
                isProcessingCreateFamily = false
                print("✅ [AddMemberOptionsScreen] Регистрация закрыта")
                
                // Проверяем, создана ли семья
                DispatchQueue.main.async {
                    UserDefaults.standard.synchronize()
                    
                    if let familyID = UserDefaults.standard.string(forKey: "family_id"),
                       !familyID.isEmpty {
                        print("✅ [AddMemberOptionsScreen] Семья создана (family_id: \(familyID)), навигируем на экран семьи")
                        
                        // Закрываем текущий экран и навигируем на семью
                        dismiss()
                        
                        // Навигируем на экран семьи после небольшой задержки для завершения анимации закрытия
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            if navigationManager.navigationStack.isEmpty {
                                navigationManager.navigationStack = [.main]
                            }
                            navigationManager.navigateTo(.family)
                        }
                    } else {
                        print("⚠️ [AddMemberOptionsScreen] Семья не создана, остаемся на экране")
                    }
                }
            }
        }
    }
    
    // MARK: - Navigation After Registration
    
    private func checkRoleAndNavigate() {
        // Проверяем роль пользователя из UserDefaults
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
              let role = FamilyRole(rawValue: roleString) else {
            print("⚠️ [AddMemberOptionsScreen] Роль не найдена, навигируем на главный экран")
            navigateToMainScreen()
            return
        }
        
        print("✅ [AddMemberOptionsScreen] Роль найдена: \(role.rawValue)")
        
        // Закрываем текущий экран
        dismiss()
        
        // Навигируем на соответствующий интерфейс в зависимости от роли
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            if navigationManager.navigationStack.isEmpty {
                navigationManager.navigationStack = [.main]
            }
            
            switch role {
            case .child, .teenager:
                print("✅ [AddMemberOptionsScreen] Навигируем на детский интерфейс")
                navigationManager.navigateTo(.childRewards)
            case .elderly:
                print("✅ [AddMemberOptionsScreen] Навигируем на интерфейс 60+")
                navigationManager.navigateTo(.elderlyInterface)
            case .parent:
                print("✅ [AddMemberOptionsScreen] Навигируем на экран семьи")
                navigationManager.navigateTo(.family)
            }
        }
    }
    
    private func navigateToMainScreen() {
        dismiss()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            if navigationManager.navigationStack.isEmpty {
                navigationManager.navigationStack = [.main]
            }
            navigationManager.navigateTo(.main)
        }
    }
    
    // MARK: - Option Button
    
    private func optionButton(
        icon: String,
        title: String,
        description: String,
        color: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 28))
                    .foregroundColor(color)
                    .frame(width: 50, height: 50)
                    .background(
                        Circle()
                            .fill(color.opacity(0.15))
                    )
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text(description)
                        .font(.system(size: 13))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gray.opacity(0.05))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct AddMemberOptionsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AddMemberOptionsScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
