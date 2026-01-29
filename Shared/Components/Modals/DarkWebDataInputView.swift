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
        isScanning = true
        defer { isScanning = false }
        
        // Сохраняем данные для сканирования
        let scanEmail = email.isEmpty ? nil : email
        let scanPassword = password.isEmpty ? nil : password
        let scanPhone = phone.isEmpty ? nil : phone
        let scanPassport = passport.isEmpty ? nil : passport
        let scanSnils = snils.isEmpty ? nil : snils
        
        // Очистка данных после сканирования
        defer {
            email = ""
            password = ""
            phone = ""
            passport = ""
            snils = ""
        }
        
            if selectedMethod == .secure {
                // Безопасное сканирование (хеши)
                await viewModel.scanSecure(
                    email: scanEmail,
                    password: scanPassword
                )
            } else {
                // Быстрое сканирование (plaintext)
                await viewModel.scanFast(
                    email: scanEmail,
                    phone: scanPhone,
                    passport: scanPassport,
                    snils: scanSnils
                )
            }
            
            // Показываем результаты (обновляем модальное окно)
            isPresented = false
    }
    
    private func errorBanner(message: String) -> some View {
        Text(message)
            .font(.footnote)
            .foregroundColor(.white)
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(Color.dangerRed.opacity(0.9))
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            .shadow(radius: 6)
    }
}

