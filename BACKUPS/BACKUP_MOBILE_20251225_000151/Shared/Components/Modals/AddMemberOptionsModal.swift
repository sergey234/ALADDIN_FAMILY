import SwiftUI

/**
 * 👨‍👩‍👧‍👦 Add Member Options Modal
 * Модальное окно выбора способа добавления члена семьи
 * 
 * Варианты:
 * 1. Создать новую семью (MainScreenWithRegistration)
 * 2. Сканировать QR-код (QRScannerModal)
 * 3. Ввести код приглашения (InvitationCodeInputModal)
 */

struct AddMemberOptionsModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
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
        NavigationView {
            VStack(spacing: 20) {
                // Заголовок
                VStack(spacing: 8) {
                    Text(localizationManager.localized("add_member_title"))
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.primary)
                    
                    Text(localizationManager.localized("add_member_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 20)
                
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
                        
                        // Закрываем основной модал после открытия регистрации
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                            // Сбрасываем флаг через небольшую задержку
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                                isProcessingCreateFamily = false
                            }
                        }
                    }
                    
                    // Вариант 2: Сканировать QR-код
                    optionButton(
                        icon: "qrcode.viewfinder",
                        title: localizationManager.localized("add_member_scan_qr"),
                        description: localizationManager.localized("add_member_scan_qr_desc"),
                        color: .blue
                    ) {
                        showQRScanner = true
                        // Закрываем основной модал после открытия сканера
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                        }
                    }
                    
                    // Вариант 3: Ввести код
                    optionButton(
                        icon: "textformat.123",
                        title: localizationManager.localized("add_member_enter_code"),
                        description: localizationManager.localized("add_member_enter_code_desc"),
                        color: .green
                    ) {
                        showCodeInput = true
                        // Закрываем основной модал после открытия ввода кода
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                            isPresented = false
                        }
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
                    isPresented = false
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
            .navigationBarHidden(true)
            .id("add_member_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        }
        .fullScreenCover(isPresented: $showCreateFamily) {
            MainScreenWithRegistration(
                registrationVM: FamilyRegistrationViewModel(),
                onComplete: {
                    print("✅ AddMemberOptionsModal: Регистрация завершена")
                    // После завершения регистрации закрываем оба модала
                    showCreateFamily = false
                    isPresented = false
                    isProcessingCreateFamily = false
                    
                    // Навигация на нужный экран по роли
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        if let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
                           let role = FamilyRole(storageValue: roleString) {
                            print("✅ AddMemberOptionsModal: Навигация на экран для роли: \(role.rawValue)")
                            switch role {
                            case .parent:
                                navigationManager.navigateTo(.parentalControl)
                            case .child, .teenager:
                                navigationManager.navigateTo(.childInterface)
                            case .elderly:
                                navigationManager.navigateTo(.elderlyInterface)
                            }
                        } else {
                            print("⚠️ AddMemberOptionsModal: Роль не найдена, остаёмся на главной")
                        }
                    }
                }
            )
        }
        .fullScreenCover(isPresented: $showQRScanner) {
            QRScannerModal(isPresented: $showQRScanner) { code in
                // После сканирования QR автоматически открываем ввод кода
                scannedCode = code
                showCodeInput = true
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
            // ✅ Сбрасываем флаг обработки при закрытии регистрации
            if !newValue {
                isProcessingCreateFamily = false
                print("✅ AddMemberOptionsModal: Регистрация закрыта, сбрасываем флаг обработки")
            }
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

struct AddMemberOptionsModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        AddMemberOptionsModal(isPresented: $isPresented)
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
