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
    @Environment(\.dismiss) private var dismiss  // ✅ ИСПРАВЛЕНИЕ: Добавляем dismiss для правильного закрытия
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
                // ✅ ИСПРАВЛЕНИЕ: Кнопка "Назад" в верхней части
                HStack {
                    Button(action: {
                        print("✅ [AddMemberOptionsModal] Кнопка 'Назад' нажата")
                        isPresented = false
                        dismiss()
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: "chevron.left")
                                .font(.system(size: 16, weight: .semibold))
                            Text(localizationManager.localized("common_back"))
                                .font(.system(size: 16, weight: .medium))
                        }
                        .foregroundColor(.blue)
                    }
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                
                // Заголовок
                VStack(spacing: 8) {
                    Text(localizationManager.localized("add_member_title"))
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.primary)
                    
                    Text(localizationManager.localized("add_member_subtitle"))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
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
                        
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #6: Не закрываем основной модал сразу
                        // Сначала открываем регистрацию
                        showCreateFamily = true
                        
                        // Закрываем основной модал после открытия регистрации с задержкой
                        // чтобы регистрация успела полностью открыться
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
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
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #6: Не закрываем основной модал сразу
                        // Закрываем только после того, как QR сканер полностью откроется
                        showQRScanner = true
                        // Закрываем основной модал с задержкой, чтобы QR сканер успел открыться
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
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
                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #6: Не закрываем основной модал сразу
                        // Закрываем только после того, как модал ввода кода полностью откроется
                        showCodeInput = true
                        // Закрываем основной модал с задержкой, чтобы модал ввода кода успел открыться
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
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
                    // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #5: Закрываем модал с правильной обработкой
                    print("✅ [AddMemberOptionsModal] Кнопка 'Отмена' нажата")
                    isPresented = false
                    dismiss()  // ✅ ИСПРАВЛЕНИЕ: Используем dismiss для правильного закрытия
                }
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
                .padding(.bottom, 20)
                .accessibilityLabel(localizationManager.localized("add_member_cancel"))
            }
            .padding(.horizontal, 20)
            .navigationBarHidden(true)
            .id("add_member_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        }
        .fullScreenCover(isPresented: $showCreateFamily) {
            MainScreenWithRegistration(
                registrationVM: FamilyRegistrationViewModel(),
                onComplete: {
                    print("✅ [AddMemberOptionsModal] Регистрация завершена, начинаем закрытие модалов")
                    print("🔍 [AddMemberOptionsModal] Текущий экран: \(navigationManager.currentScreen)")
                    print("🔍 [AddMemberOptionsModal] Стек навигации: \(navigationManager.navigationStack)")
                    
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Увеличиваем задержки для TestFlight
                    // В TestFlight модалы закрываются медленнее, чем в симуляторе
                    showCreateFamily = false
                    
                    // ✅ ИСПРАВЛЕНИЕ: Закрываем основной sheet после большей задержки для TestFlight
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
                        isPresented = false
                        isProcessingCreateFamily = false
                        
                        // ✅ ИСПРАВЛЕНИЕ: Навигация на нужный экран по роли после закрытия всех модалов
                        // Увеличиваем задержку для TestFlight (там модалы закрываются медленнее)
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                            // ✅ ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ: Убеждаемся, что UserDefaults синхронизирован
                            UserDefaults.standard.synchronize()
                            
                            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверяем несколько раз с задержкой для TestFlight
                            // В TestFlight данные могут сохраняться медленнее
                            let maxAttempts = 3
                            
                            func checkAndNavigate(attempt: Int) {
                                DispatchQueue.main.async {
                                    // ✅ ПРОВЕРКА: Убеждаемся, что семья создана
                                    let familyID = UserDefaults.standard.string(forKey: "family_id")
                                    print("🔍 [AddMemberOptionsModal] Попытка \(attempt)/\(maxAttempts): Проверяем family_id: \(familyID ?? "nil")")
                                    
                                    // Пробуем прочитать роль из UserDefaults
                                    let roleString = UserDefaults.standard.string(forKey: "current_user_role")
                                    print("🔍 [AddMemberOptionsModal] Читаем роль из UserDefaults: \(roleString ?? "nil")")
                                    print("🔍 [AddMemberOptionsModal] Текущий экран перед навигацией: \(self.navigationManager.currentScreen)")
                                    
                                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Всегда навигируем на экран семьи после создания семьи
                                    if let familyID = familyID, !familyID.isEmpty {
                                        print("✅ [AddMemberOptionsModal] Семья создана (family_id: \(familyID))")
                                        
                                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #6: Проверяем, откуда был открыт модал
                                        // Если мы уже на экране .family, не нужно навигировать туда снова
                                        let currentScreen = self.navigationManager.currentScreen
                                        print("🔍 [AddMemberOptionsModal] Текущий экран: \(currentScreen)")
                                        
                                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #2: Проверяем роль и навигируем по роли, а не на .family
                                        // Если семья создана, но пользователь добавил ребенка/60+, нужно навигировать на соответствующий интерфейс
                                        let roleString = UserDefaults.standard.string(forKey: "current_user_role")
                                        if let roleString = roleString,
                                           let role = FamilyRole(storageValue: roleString) {
                                            print("🔍 [AddMemberOptionsModal] Роль найдена: \(role.rawValue), навигируем по роли")
                                            
                                            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убеждаемся, что стек навигации правильный
                                            if self.navigationManager.navigationStack.isEmpty {
                                                self.navigationManager.navigationStack = [.main]
                                                print("✅ [AddMemberOptionsModal] Стек навигации инициализирован: [.main]")
                                            }
                                            
                                            // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #2: Навигация по роли для iPad и iPhone
                                            switch role {
                                            case .parent:
                                                // Если родитель, остаемся на экране семьи или переходим на родительский контроль
                                                if currentScreen != .family {
                                                    self.navigationManager.navigateTo(.family)
                                                }
                                                print("✅ [AddMemberOptionsModal] Родитель - остаемся на экране семьи")
                                            case .child, .teenager:
                                                self.navigationManager.navigateTo(.childInterface)
                                                print("✅ [AddMemberOptionsModal] Навигация на .childInterface для ребенка/подростка")
                                            case .elderly:
                                                self.navigationManager.navigateTo(.elderlyInterface)
                                                print("✅ [AddMemberOptionsModal] Навигация на .elderlyInterface для пожилого")
                                            }
                                        } else if currentScreen != .family {
                                            // Если роль не найдена, но мы не на экране семьи - навигируем на .family
                                            if self.navigationManager.navigationStack.isEmpty {
                                                self.navigationManager.navigationStack = [.main]
                                                print("✅ [AddMemberOptionsModal] Стек навигации инициализирован: [.main]")
                                            }
                                            
                                            self.navigationManager.navigateTo(.family)
                                            print("✅ [AddMemberOptionsModal] Навигация на .family выполнена")
                                        } else {
                                            print("✅ [AddMemberOptionsModal] Уже на экране .family, навигация не требуется")
                                            // Обновляем данные на текущем экране (если нужно)
                                            NotificationCenter.default.post(name: NSNotification.Name("FamilyMembersUpdated"), object: nil)
                                        }
                                        print("🔍 [AddMemberOptionsModal] Текущий экран после навигации: \(self.navigationManager.currentScreen)")
                                        print("🔍 [AddMemberOptionsModal] Стек навигации после навигации: \(self.navigationManager.navigationStack)")
                                    } else if attempt < maxAttempts {
                                        // Если семья еще не создана, пробуем еще раз через задержку
                                        print("⚠️ [AddMemberOptionsModal] Семья еще не создана, пробуем еще раз через 0.5 сек...")
                                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                                            checkAndNavigate(attempt: attempt + 1)
                                        }
                                    } else if let roleString = roleString,
                                              let role = FamilyRole(storageValue: roleString) {
                                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #2: Если семья не создана после всех попыток, но роль есть - навигируем по роли
                                        print("⚠️ [AddMemberOptionsModal] Семья не создана после \(maxAttempts) попыток, но роль найдена: \(role.rawValue)")
                                        
                                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убеждаемся, что стек навигации правильный
                                        if self.navigationManager.navigationStack.isEmpty {
                                            self.navigationManager.navigationStack = [.main]
                                        }
                                        
                                        // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #2: Навигация по роли для iPad и iPhone
                                        switch role {
                                        case .parent:
                                            self.navigationManager.navigateTo(.parentalControl)
                                            print("✅ [AddMemberOptionsModal] Навигация на .parentalControl для родителя")
                                        case .child, .teenager:
                                            self.navigationManager.navigateTo(.childInterface)
                                            print("✅ [AddMemberOptionsModal] Навигация на .childInterface для ребенка/подростка")
                                        case .elderly:
                                            self.navigationManager.navigateTo(.elderlyInterface)
                                            print("✅ [AddMemberOptionsModal] Навигация на .elderlyInterface для пожилого")
                                        }
                                    } else {
                                        // Если ничего не найдено - навигируем на главный экран
                                        print("⚠️ [AddMemberOptionsModal] Роль и семья не найдены после \(maxAttempts) попыток - навигируем на главный экран")
                                        self.navigationManager.navigateTo(.main)
                                    }
                                }
                            }
                            
                            // Начинаем проверку
                            checkAndNavigate(attempt: 1)
                        }
                    }
                }
            )
        }
        .fullScreenCover(isPresented: $showQRScanner) {
            QRScannerModal { code in
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
