import SwiftUI
import CryptoKit

/**
 * 📝 Dark Web Data Input View
 * Форма для ввода данных для сканирования темной сети
 */

struct DarkWebDataInputView: View {
    
    @Binding var isPresented: Bool
    @ObservedObject var viewModel: DarkWebMonitoringViewModel
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var selectedMethod: DarkWebScanMethod = .secure
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var phone: String = ""
    @State private var passport: String = ""
    @State private var snils: String = ""
    @State private var isScanning: Bool = false
    @State private var showResults: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Выбор метода
                        DarkWebScanMethodSelector(selectedMethod: $selectedMethod)
                            .padding(.horizontal, Spacing.screenPadding)
                            .padding(.top, Spacing.m)
                        
                        // Форма ввода данных
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("dark_web_scan_data_input_title"))
                                .font(.h2)
                                .foregroundColor(.textPrimary)
                            
                            // Email
                            dataInputField(
                                title: localizationManager.localized("dark_web_scan_data_email"),
                                value: $email,
                                placeholder: "user@example.com",
                                icon: "envelope.fill",
                                isSecure: false,
                                keyboardType: .emailAddress,
                                explanation: selectedMethod == .secure
                                    ? localizationManager.localized("dark_web_scan_data_email_secure_explanation")
                                    : localizationManager.localized("dark_web_scan_data_email_fast_explanation")
                            )
                            
                            // Password (всегда хешируется)
                            dataInputField(
                                title: localizationManager.localized("dark_web_scan_data_password"),
                                value: $password,
                                placeholder: "••••••••",
                                icon: "lock.fill",
                                isSecure: true,
                                keyboardType: .default,
                                explanation: localizationManager.localized("dark_web_scan_data_password_explanation")
                            )
                            
                            // Phone (только для быстрого сканирования)
                            if selectedMethod == .fast {
                                dataInputField(
                                    title: localizationManager.localized("dark_web_scan_data_phone"),
                                    value: $phone,
                                    placeholder: "+7 999 123-45-67",
                                    icon: "phone.fill",
                                    isSecure: false,
                                    keyboardType: .phonePad,
                                    explanation: localizationManager.localized("dark_web_scan_data_phone_explanation")
                                )
                            }
                            
                            // Passport (только для быстрого сканирования)
                            if selectedMethod == .fast {
                                dataInputField(
                                    title: localizationManager.localized("dark_web_scan_data_passport"),
                                    value: $passport,
                                    placeholder: "1234 567890",
                                    icon: "person.text.rectangle.fill",
                                    isSecure: false,
                                    keyboardType: .default,
                                    explanation: localizationManager.localized("dark_web_scan_data_passport_explanation")
                                )
                            }
                            
                            // SNILS (только для быстрого сканирования)
                            if selectedMethod == .fast {
                                dataInputField(
                                    title: localizationManager.localized("dark_web_scan_data_snils"),
                                    value: $snils,
                                    placeholder: "123-456-789 01",
                                    icon: "doc.text.fill",
                                    isSecure: false,
                                    keyboardType: .default,
                                    explanation: localizationManager.localized("dark_web_scan_data_snils_explanation")
                                )
                            }
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        // Кнопка сканирования
                        Button(action: {
                            Task {
                                await startScan()
                            }
                        }) {
                            HStack {
                                if isScanning {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Image(systemName: "magnifyingglass")
                                    Text(localizationManager.localized("dark_web_scan_start_button"))
                                }
                            }
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(Color.primaryBlue)
                            )
                        }
                        .disabled(isScanning || !hasAnyData)
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.bottom, Spacing.l)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("dark_web_scan_data_input_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Text(localizationManager.localized("common_done"))
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
            .overlay(alignment: .center) {
                if isScanning {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
                        .padding()
                        .background(Color.backgroundMedium.opacity(0.85))
                        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                }
            }
            .overlay(alignment: .bottom) {
                if let error = viewModel.errorMessage {
                    errorBanner(message: error)
                        .padding(.bottom, Spacing.l)
                }
            }
            // ✅ ИСПРАВЛЕНИЕ: Добавляем VisualLogView на модальное окно
            .withVisualLogger()
        }
    }
    
    private func dataInputField(
        title: String,
        value: Binding<String>,
        placeholder: String,
        icon: String,
        isSecure: Bool,
        keyboardType: UIKeyboardType,
        explanation: String
    ) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.primaryBlue)
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            ALADDINTextField(
                placeholder,
                text: value,
                icon: icon,
                keyboardType: keyboardType,
                isSecure: isSecure
            )
            
            // Объяснение
            HStack(alignment: .top, spacing: Spacing.xs) {
                Image(systemName: "info.circle")
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                Text(explanation)
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
            }
        }
    }
    
    private var hasAnyData: Bool {
        !email.isEmpty || !password.isEmpty || !phone.isEmpty || !passport.isEmpty || !snils.isEmpty
    }
    
    private func startScan() async {
        print("🔍 DarkWebDataInputView: Начало сканирования, метод: \(selectedMethod == .secure ? "secure" : "fast")")
        MasterLogger.shared.log(.info, category: .business, message: "🔍 DarkWebDataInputView: Начало сканирования")
        
        isScanning = true
        defer { 
            isScanning = false
            print("🔍 DarkWebDataInputView: Сканирование завершено")
        }
        
        // Сохраняем данные для сканирования
        let scanEmail = email.isEmpty ? nil : email
        let scanPassword = password.isEmpty ? nil : password
        let scanPhone = phone.isEmpty ? nil : phone
        let scanPassport = passport.isEmpty ? nil : passport
        let scanSnils = snils.isEmpty ? nil : snils
        
        // ✅ ИСПРАВЛЕНИЕ: Проверяем наличие данных перед сканированием
        let hasData = scanEmail != nil || scanPassword != nil || scanPhone != nil || scanPassport != nil || scanSnils != nil
        guard hasData else {
            print("❌ DarkWebDataInputView: Нет данных для сканирования")
            MasterLogger.shared.log(.error, category: .business, message: "❌ DarkWebDataInputView: Нет данных для сканирования")
            viewModel.errorMessage = localizationManager.localized("dark_web_scan_error_no_data")
            return
        }
        
        print("✅ DarkWebDataInputView: Данные для сканирования: email=\(scanEmail != nil ? "есть" : "нет"), password=\(scanPassword != nil ? "есть" : "нет"), phone=\(scanPhone != nil ? "есть" : "нет")")
        
        do {
            if selectedMethod == .secure {
                // Безопасное сканирование (хеши)
                print("🔐 DarkWebDataInputView: Запуск безопасного сканирования")
                MasterLogger.shared.log(.info, category: .business, message: "🔐 DarkWebDataInputView: Запуск безопасного сканирования")
                await viewModel.scanSecure(
                    email: scanEmail,
                    password: scanPassword
                )
            } else {
                // Быстрое сканирование (plaintext)
                print("⚡ DarkWebDataInputView: Запуск быстрого сканирования")
                MasterLogger.shared.log(.info, category: .business, message: "⚡ DarkWebDataInputView: Запуск быстрого сканирования")
                await viewModel.scanFast(
                    email: scanEmail,
                    phone: scanPhone,
                    passport: scanPassport,
                    snils: scanSnils
                )
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Проверяем наличие ошибок перед закрытием модального окна
            if viewModel.errorMessage == nil {
                print("✅ DarkWebDataInputView: Сканирование успешно завершено")
                MasterLogger.shared.log(.info, category: .business, message: "✅ DarkWebDataInputView: Сканирование успешно завершено")
                
                // Очистка данных после успешного сканирования
                email = ""
                password = ""
                phone = ""
                passport = ""
                snils = ""
                
                // Обновляем данные в ViewModel
                await viewModel.loadData()
                
                // Показываем результаты (обновляем модальное окно)
                isPresented = false
            } else {
                print("⚠️ DarkWebDataInputView: Сканирование завершено с ошибкой: \(viewModel.errorMessage ?? "неизвестная ошибка")")
                MasterLogger.shared.log(.warn, category: .business, message: "⚠️ DarkWebDataInputView: Сканирование завершено с ошибкой: \(viewModel.errorMessage ?? "неизвестная ошибка")")
                // Не закрываем модальное окно при ошибке - пользователь должен видеть ошибку
            }
        } catch {
            print("❌ DarkWebDataInputView: Критическая ошибка сканирования: \(error.localizedDescription)")
            MasterLogger.shared.log(.error, category: .business, message: "❌ DarkWebDataInputView: Критическая ошибка сканирования: \(error.localizedDescription)")
            viewModel.errorMessage = localizationManager.localized("dark_web_scan_error_no_data")
        }
    }
    
    private func errorBanner(message: String) -> some View {
        HStack {
            Text(message)
                .font(.footnote)
                .foregroundColor(.white)

            Spacer()

            Button(action: {
                Task {
                    await startScan()
                }
            }) {
                Text(localizationManager.localized("dark_web_retry_scan"))
                    .font(.caption)
                    .foregroundColor(.primaryBlue)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.white.opacity(0.2))
                    .clipShape(Capsule())
            }
        }
        .padding(.horizontal, Spacing.m)
        .padding(.vertical, Spacing.s)
        .background(Color.dangerRed.opacity(0.9))
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        .shadow(radius: 6)
    }
}

