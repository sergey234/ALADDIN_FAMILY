import SwiftUI
import Foundation

/// 👤 Profile Screen
/// Экран профиля пользователя
/// Источник дизайна: /mobile/wireframes/11_profile_screen.html
struct ProfileScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var tariffManager = TariffManager.shared
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    @State private var showTwoFactor: Bool = false
    @State private var showActiveSessions: Bool = false
    @State private var showDeleteAccount: Bool = false
    @State private var showEditProfile: Bool = false
    @State private var showAdultSafetyInstructions: Bool = false
    @State private var showReferralScreen: Bool = false
    @State private var registrationDate: String = ""
    @AppStorage("profile_name") private var profileName: String = ""
    @AppStorage("profile_alias") private var profileAlias: String = ""
    @AppStorage("profile_pin") private var profilePIN: String = ""
    
    // ✅ Согласие на обработку ПДн (152-ФЗ)
    @AppStorage("personal_data_consent_accepted") private var consentAccepted: Bool = false
    @AppStorage("personal_data_consent_date") private var consentDate: String = ""
    @State private var showConsentRevokeAlert: Bool = false
    
    // MARK: - Computed Properties
    
    /// Название текущего тарифа для отображения
    private var currentTariffDisplayName: String {
        switch tariffManager.currentTariff {
        case .free:
            return localizationManager.localized("tariffs_free")
        case .personal:
            return localizationManager.localized("tariffs_personal")
        case .family:
            return localizationManager.localized("tariffs_family")
        case .premium:
            return localizationManager.localized("tariffs_premium")
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель (как в других экранах)
                ALADDINNavigationBar(
                    title: localizationManager.localized("profile_title"),
                    subtitle: localizationManager.localized("profile_subtitle"),
                    showBackButton: true,
                    onBack: {
                        // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                        // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                        dismiss()
                        
                        // Дополнительно синхронизируем NavigationManager для корректной работы стека
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack()
                            }
                        }
                    }
                )
                
                // Кнопка редактирования профиля (вместо кнопки в header)
                HStack {
                    Spacer()
                    Button(action: { showEditProfile = true }) {
                        Image(systemName: "pencil")
                            .foregroundColor(.white)
                            .font(.system(size: 18))
                            .frame(width: 44, height: 44)
                            .background(
                                Circle()
                                    .fill(Color.blue.opacity(0.2))
                            )
                    }
                    .padding(.trailing)
                }
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Шапка профиля
                        profileHeader
                        
                        // Статистика
                        profileStats
                        
                        // Информация
                        profileInfo
                        
                        // Безопасность
                        securitySection
                        
                        // Согласие на обработку ПДн (152-ФЗ)
                        consentSection
                        
                        // Реферальная программа
                        referralSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.s)
                }
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("profile_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadRegistrationDate()
            loadProfileImage()
        }
        .sheet(isPresented: $showImagePicker) {
            ProfileImagePicker(selectedImage: $selectedImage)
        }
        .onChange(of: selectedImage) { newImage in
            if let image = newImage {
                saveProfileImage(image)
            }
        }
        .sheet(isPresented: $showTwoFactor) {
            TwoFactorAuthView(isPresented: $showTwoFactor)
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showActiveSessions) {
            ActiveSessionsView(isPresented: $showActiveSessions)
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDeleteAccount) {
            DeleteAccountView(isPresented: $showDeleteAccount)
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEditProfile) {
            EditProfileView(isPresented: $showEditProfile)
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAdultSafetyInstructions) {
            AdultSafetyInstructionsModal(isPresented: $showAdultSafetyInstructions)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showReferralScreen) {
            ReferralScreen()
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("profile_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Profile Header
    
    private var profileHeader: some View {
        VStack(spacing: Spacing.l) {
            // Большой аватар
            Button(action: {
                showImagePicker = true
            }) {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.primaryBlue, Color.blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 100, height: 100)
                    
                    if let selectedImage = selectedImage {
                        Image(uiImage: selectedImage)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 100, height: 100)
                            .clipShape(Circle())
                    } else {
                        Text("👨")
                            .font(.system(size: 60))
                    }
                    
                    // Иконка редактирования
                    VStack {
                        Spacer()
                        HStack {
                            Spacer()
                            Circle()
                                .fill(Color.secondaryGold)
                                .frame(width: 30, height: 30)
                                .overlay(
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 14))
                                        .foregroundColor(.white)
                                )
                        }
                    }
                }
            }
            
            // Имя и email
            VStack(spacing: Spacing.xs) {
                Text(profileName.isEmpty ? localizationManager.localized("profile_name_placeholder") : profileName)
                    .font(.title2)
                    .foregroundColor(.white)
                
                Text(profileAlias.isEmpty ? localizationManager.localized("profile_email_placeholder") : profileAlias)
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }
            
            // Статус подписки (показываем только для платных тарифов)
            if tariffManager.currentTariff != .free {
                HStack(spacing: Spacing.s) {
                    Text("⭐")
                        .font(.system(size: 20))
                    
                    Text(currentTariffDisplayName)
                        .font(.body.bold())
                        .foregroundColor(.yellow)
                    
                    Text(localizationManager.localized("profile_valid_until"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.horizontal, Spacing.l)
                .padding(.vertical, Spacing.s)
                .background(
                    Capsule()
                        .fill(Color.yellow.opacity(0.2))
                        .overlay(
                            Capsule()
                                .stroke(Color.yellow.opacity(0.5), lineWidth: 1)
                        )
                )
            }
        }
    }
    
    // MARK: - Profile Stats
    
    private var profileStats: some View {
        HStack(spacing: Spacing.m) {
            statCard(icon: "🛡️", value: "47", label: localizationManager.localized("profile_threats_blocked"))
            statCard(icon: "👥", value: "4", label: localizationManager.localized("profile_family_members"))
            statCard(icon: "📱", value: "8", label: localizationManager.localized("profile_devices"))
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func statCard(icon: String, value: String, label: String) -> some View {
        VStack(spacing: Spacing.s) {
            Text(icon)
                .font(.system(size: 28))
            
            Text(value)
                .font(.title2)
                .foregroundColor(.primaryBlue)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Profile Info
    
    private var profileInfo: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle(localizationManager.localized("profile_personal_info_title"))
            
            VStack(spacing: Spacing.s) {
                infoRow(icon: "person", label: localizationManager.localized("profile_name"), value: profileName.isEmpty ? "" : profileName, optional: profileName.isEmpty)
                infoRow(icon: "envelope", label: localizationManager.localized("profile_email"), value: profileAlias.isEmpty ? "" : profileAlias, optional: profileAlias.isEmpty)
                infoRow(icon: "key", label: localizationManager.localized("profile_phone"), value: profilePIN.isEmpty ? "" : String(repeating: "•", count: max(4, profilePIN.count)), optional: profilePIN.isEmpty)
                
                // ✅ НОВОЕ: ID пользователя с кнопкой копирования
                if let memberId = UserDefaults.standard.string(forKey: "your_member_id"), !memberId.isEmpty {
                    Button(action: {
                        UIPasteboard.general.string = memberId
                        let generator = UINotificationFeedbackGenerator()
                        generator.notificationOccurred(.success)
                    }) {
                        HStack(spacing: Spacing.m) {
                            Image(systemName: "number")
                                .font(.system(size: 20))
                                .foregroundColor(.primaryBlue)
                                .frame(width: 24)
                            
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text(localizationManager.localized("profile_user_id"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                HStack(spacing: 4) {
                                    Text(memberId)
                                        .font(.body)
                                        .foregroundColor(.textPrimary)
                                    
                                    Image(systemName: "doc.on.doc")
                                        .font(.system(size: 12))
                                        .foregroundColor(.primaryBlue)
                                }
                            }
                            
                            Spacer()
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.3))
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                
                infoRow(icon: "calendar", label: localizationManager.localized("profile_registration_date"), value: registrationDate.isEmpty ? localizationManager.localized("profile_not_set") : registrationDate)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle(localizationManager.localized("profile_security_title"))
            
            VStack(spacing: Spacing.s) {
                securityButton(icon: "🛡️", title: localizationManager.localized("profile_safety_instructions"), action: { showAdultSafetyInstructions = true })
                securityButton(icon: "📱", title: localizationManager.localized("profile_two_factor_auth"), action: { showTwoFactor = true })
                securityButton(icon: "🔑", title: localizationManager.localized("profile_active_sessions"), action: { showActiveSessions = true })
                securityButton(icon: "🗑️", title: localizationManager.localized("profile_delete_account"), color: .red, action: { showDeleteAccount = true })
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Consent Section (152-ФЗ)
    
    private var consentSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle(localizationManager.localized("profile_consent_title"))
            
            VStack(spacing: Spacing.s) {
                // Статус согласия
                HStack(spacing: Spacing.m) {
                    Image(systemName: consentAccepted ? "checkmark.circle.fill" : "xmark.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(consentAccepted ? .green : .red)
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(consentAccepted ? localizationManager.localized("profile_consent_provided") : localizationManager.localized("profile_consent_not_provided"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        if consentAccepted, !consentDate.isEmpty {
                            Text("\(localizationManager.localized("profile_consent_date")) \(formatConsentDate(consentDate))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    Spacer()
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                
                // Кнопки действий
                if consentAccepted {
                    // Просмотр документов
                    Button(action: {
                        URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/consent.html", tariffId: nil)
                    }) {
                        HStack(spacing: Spacing.m) {
                            Image(systemName: "doc.text")
                                .font(.system(size: 18))
                                .foregroundColor(.primaryBlue)
                            
                            Text(localizationManager.localized("profile_consent_view"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Image(systemName: "chevron.right")
                                .font(.system(size: 14))
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.3))
                        )
                    }
                    
                    Button(action: {
                        URLHelper.openWebsite(urlString: "https://aladdin-ai.ru/privacy.html", tariffId: nil)
                    }) {
                        HStack(spacing: Spacing.m) {
                            Image(systemName: "lock.shield")
                                .font(.system(size: 18))
                                .foregroundColor(.primaryBlue)
                            
                            Text(localizationManager.localized("profile_consent_privacy_policy"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Image(systemName: "chevron.right")
                                .font(.system(size: 14))
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.3))
                        )
                    }
                    
                    // Отзыв согласия
                    Button(action: {
                        showConsentRevokeAlert = true
                    }) {
                        HStack(spacing: Spacing.m) {
                            Image(systemName: "xmark.circle")
                                .font(.system(size: 18))
                                .foregroundColor(.red)
                            
                            Text(localizationManager.localized("profile_consent_revoke"))
                                .font(.body)
                                .foregroundColor(.red)
                            
                            Spacer()
                        }
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.red.opacity(0.1))
                        )
                    }
                } else {
                    Text(localizationManager.localized("profile_consent_required_description"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.3))
                        )
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .alert(localizationManager.localized("profile_consent_revoke_title"), isPresented: $showConsentRevokeAlert) {
            Button(localizationManager.localized("profile_consent_revoke_cancel"), role: .cancel) {}
            Button(localizationManager.localized("profile_consent_revoke_confirm"), role: .destructive) {
                consentAccepted = false
                consentDate = ""
                // TODO: Отправить запрос на сервер об отзыве согласия
            }
        } message: {
            Text(localizationManager.localized("profile_consent_revoke_message"))
        }
    }
    
    private func formatConsentDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .medium
            displayFormatter.timeStyle = .short
            // ✅ Используем текущий язык из LocalizationManager
            let localeIdentifier = localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US"
            displayFormatter.locale = Locale(identifier: localeIdentifier)
            return displayFormatter.string(from: date)
        }
        return dateString
    }
    
    // MARK: - Referral Section
    
    private var referralSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle(localizationManager.localized("profile_referral_program"))
            
            VStack(spacing: Spacing.s) {
                Button(action: {
                    showReferralScreen = true
                }) {
                    HStack(spacing: Spacing.m) {
                        Text("🎁")
                            .font(.system(size: 24))
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text(localizationManager.localized("profile_invite_friends"))
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Text(localizationManager.localized("profile_invite_discount"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 14))
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Helper Views
    
    private func sectionTitle(_ title: String) -> some View {
        Text(title)
            .font(.h3)
            .foregroundColor(.textPrimary)
            .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func infoRow(icon: String, label: String, value: String, optional: Bool = false) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(.primaryBlue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                if value.isEmpty && optional {
                    Text(localizationManager.localized("profile_not_specified"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .italic()
                } else {
                    Text(value)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                }
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func securityButton(icon: String, title: String, color: Color = .textPrimary, action: @escaping () -> Void = {}) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 24))
                
                Text(title)
                    .font(.body)
                    .foregroundColor(color)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(color)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Load Registration Date
    
    private func loadRegistrationDate() {
        if let savedDate = UserDefaults.standard.object(forKey: "registration_date") as? Date {
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMMM yyyy"
            // ✅ Используем текущий язык из LocalizationManager
            let localeIdentifier = localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US"
            formatter.locale = Locale(identifier: localeIdentifier)
            registrationDate = formatter.string(from: savedDate)
        } else {
            // Если дата не сохранена, используем текущую дату
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMMM yyyy"
            // ✅ Используем текущий язык из LocalizationManager
            let localeIdentifier = localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US"
            formatter.locale = Locale(identifier: localeIdentifier)
            registrationDate = formatter.string(from: Date())
        }
    }
    
    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        selectedImage = ProfileImageManager.shared.loadProfileImage(for: .main)
    }
    
    private func saveProfileImage(_ image: UIImage) {
        _ = ProfileImageManager.shared.saveProfileImage(image, for: .main)
    }
}

// MARK: - Image Picker

struct ProfileImagePicker: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ProfileImagePicker
        
        init(_ parent: ProfileImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.selectedImage = image
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

// MARK: - Modal Views

struct TwoFactorAuthView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let apiService = APIService.shared
    private let toastManager = ToastManager.shared
    
    // ✅ ИСПРАВЛЕНО: Заменено @State на @AppStorage для сохранения между сессиями
    @AppStorage("profile_2fa_enabled") private var isEnabled: Bool = false
    
    var body: some View {
        NavigationView {
            Form {
                Toggle(localizationManager.localized("profile_2fa_enable"), isOn: Binding(
                    get: { isEnabled },
                    set: { newValue in
                        isEnabled = newValue
                        sync2FAStatusToServer(enabled: newValue)
                    }
                ))
                Text(isEnabled ? localizationManager.localized("profile_2fa_enabled") : localizationManager.localized("profile_2fa_disabled"))
                    .foregroundColor(isEnabled ? .green : .gray)
            }
            .padding()
            .navigationTitle(localizationManager.localized("profile_2fa_title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("profile_2fa_done")) { isPresented = false }
                }
            }
            .id("2fa_lang_\(localizationManager.currentLanguage.rawValue)")
            .onAppear {
                load2FAStatusFromServer()
            }
        }
    }
    
    // MARK: - Server Synchronization
    
    /// Загружает статус 2FA с сервера
    private func load2FAStatusFromServer() {
        Task {
            do {
                let status = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<TwoFactorAuthStatusResponse, Error>) in
                    apiService.get2FAStatus { result in
                        continuation.resume(with: result)
                    }
                }
                
                await MainActor.run {
                    isEnabled = status.enabled
                }
            } catch {
                print("⚠️ TwoFactorAuthView: Ошибка загрузки статуса 2FA: \(error)")
                // Используем локальное значение из @AppStorage
            }
        }
    }
    
    /// Синхронизирует статус 2FA с сервером
    private func sync2FAStatusToServer(enabled: Bool) {
        Task {
            do {
                _ = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<APIResponse<Bool>, Error>) in
                    apiService.update2FAStatus(enabled: enabled) { result in
                        continuation.resume(with: result)
                    }
                }
                
                await MainActor.run {
                    toastManager.showSuccess(localizationManager.localized("settings_saved"))
                }
            } catch {
                await MainActor.run {
                    toastManager.showError(localizationManager.localized("settings_save_error"))
                    // Откатываем изменение при ошибке
                    isEnabled = !enabled
                }
            }
        }
    }
}

struct ActiveSessionsView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            List {
                ForEach(0..<3, id: \.self) { index in
                    HStack {
                        VStack(alignment: .leading) {
                            Text("iPhone 13")
                                .font(.headline)
                            HStack {
                                Text(localizationManager.localized("active_sessions_location"))
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                Text("•")
                                Text(localizationManager.localized("active_sessions_now"))
                                    .font(.caption)
                                    .foregroundColor(.green)
                            }
                            Spacer()
                            Button(localizationManager.localized("active_sessions_logout")) { }
                        }
                    }
                }
            }
            .navigationTitle(localizationManager.localized("active_sessions_title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("active_sessions_done")) { isPresented = false }
                }
            }
            .id("active_sessions_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }
}

struct DeleteAccountView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var confirmText: String = ""
    @State private var isDeleting: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showSuccessAlert: Bool = false
    
    private var confirmTextRequired: String {
        localizationManager.currentLanguage == .russian ? "УДАЛИТЬ" : "DELETE"
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("profile_delete_warning"))) {
                    Text(localizationManager.localized("profile_delete_message"))
                        .foregroundColor(.red)
                }
                Section(header: Text(localizationManager.localized("profile_delete_confirm"))) {
                    TextField(localizationManager.localized("delete_account_confirm_placeholder"), text: $confirmText)
                        .disabled(isDeleting)
                    Text(localizationManager.localized("profile_delete_confirm_text"))
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                
                if let errorMessage = errorMessage {
                    Section {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
                
                Button(localizationManager.localized("delete_account_button")) {
                    deleteAccount()
                }
                .buttonStyle(.borderedProminent)
                .foregroundColor(.red)
                .disabled(confirmText.uppercased() != confirmTextRequired || isDeleting)
                .overlay {
                    if isDeleting {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    }
                }
            }
            .padding()
            .navigationTitle(localizationManager.localized("delete_account_title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("delete_account_cancel")) {
                        isPresented = false
                    }
                    .disabled(isDeleting)
                }
            }
            .id("delete_account_lang_\(localizationManager.currentLanguage.rawValue)")
            .alert(localizationManager.localized("delete_account_success_title"), isPresented: $showSuccessAlert) {
                Button("OK") {
                    handleAccountDeleted()
                }
            } message: {
                Text(localizationManager.localized("delete_account_success_message"))
            }
        }
    }
    
    // MARK: - Delete Account Logic
    
    private func deleteAccount() {
        guard confirmText.uppercased() == confirmTextRequired else {
            return
        }
        
        isDeleting = true
        errorMessage = nil
        
        let apiService = APIService.shared
        apiService.deleteAccount(confirmationCode: confirmText.uppercased()) { [self] result in
            DispatchQueue.main.async {
                isDeleting = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        // Успешное удаление
                        clearLocalData()
                        showSuccessAlert = true
                    } else {
                        errorMessage = response.message ?? localizationManager.localized("delete_account_error_generic")
                    }
                    
                case .failure(let error):
                    // Обработка ошибок
                    if let networkError = error as? NetworkError {
                        switch networkError {
                        case .unauthorized:
                            errorMessage = localizationManager.localized("delete_account_error_unauthorized")
                        case .internalServerError(let message), .badGateway(let message), .serviceUnavailable(let message):
                            errorMessage = message ?? localizationManager.localized("delete_account_error_server")
                        case .noConnection, .timeout, .serverUnavailable, .dnsResolutionFailed:
                            errorMessage = localizationManager.localized("delete_account_error_network")
                        default:
                            errorMessage = networkError.localizedDescription.isEmpty ? localizationManager.localized("delete_account_error_generic") : networkError.localizedDescription
                        }
                    } else {
                        errorMessage = error.localizedDescription
                    }
                }
            }
        }
    }
    
    private func clearLocalData() {
        // Очистка локальных данных
        StorageManager.shared.clearAllData()
        
        // Очистка токена авторизации
        AppConfig.authToken = nil
        
        // Очистка кэша (если есть)
        // CacheManager очищается через StorageManager.clearAllData()
        
        print("✅ DeleteAccountView: Все локальные данные очищены")
    }
    
    private func handleAccountDeleted() {
        // Закрываем модальное окно
        isPresented = false
        
        // Навигация на главный экран (который покажет экран входа, если пользователь не авторизован)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            // Сбрасываем навигацию на главный экран
            navigationManager.navigationStack.removeAll()
            navigationManager.currentScreen = .main
            
            // Отправляем уведомление о удалении аккаунта (для обработки в AppDelegate или главном экране)
            NotificationCenter.default.post(name: NSNotification.Name("UserAccountDeleted"), object: nil)
        }
    }
}

struct EditProfileView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @AppStorage("profile_name") private var storedName: String = ""
    @AppStorage("profile_alias") private var storedAlias: String = ""
    @AppStorage("profile_pin") private var storedPIN: String = ""
    @State private var name: String = ""
    @State private var alias: String = ""
    @State private var pin: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text(localizationManager.localized("edit_profile_photo"))) {
                    Button(action: {
                        // TODO: Реализовать выбор фото
                    }) {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .font(.system(size: 60))
                                .foregroundColor(.gray)
                            Text(localizationManager.localized("edit_profile_photo_hint"))
                                .font(.body)
                                .foregroundColor(.primary)
                            Spacer()
                        }
                    }
                }
                
                Section(header: Text(localizationManager.localized("edit_profile_info"))) {
                    TextField(localizationManager.localized("edit_profile_name"), text: $name)
                    TextField(localizationManager.localized("edit_profile_email"), text: $alias)
                    TextField(localizationManager.localized("edit_profile_phone"), text: $pin)
                }
                
                Section {
                    Button(localizationManager.localized("edit_profile_reset_password")) {
                        // TODO: Реализовать сброс пароля
                    }
                    .foregroundColor(.blue)
                }
                
                Section {
                    Button(localizationManager.localized("edit_profile_save")) {
                        saveProfile()
                    }
                    .buttonStyle(.borderedProminent)
                    .frame(maxWidth: .infinity)
                }
                .padding()
            }
            .navigationTitle(localizationManager.localized("edit_profile_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("edit_profile_cancel")) { isPresented = false }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("edit_profile_save")) {
                        saveProfile()
                    }
                }
            }
            .onAppear {
                name = storedName
                alias = storedAlias
                pin = storedPIN
            }
            .id("edit_profile_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }
    
    // MARK: - Save Profile
    
    private func saveProfile() {
        storedName = name.trimmingCharacters(in: .whitespacesAndNewlines)
        storedAlias = alias.trimmingCharacters(in: .whitespacesAndNewlines)
        storedPIN = pin.trimmingCharacters(in: .whitespacesAndNewlines)
        isPresented = false
    }
}

// MARK: - Adult Safety Instructions Modal

struct AdultSafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text(localizationManager.localized("profile_safety_reminder"))
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("profile_dont_trust_calls"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("profile_dont_trust_authorities"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("profile_dont_trust_services"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("profile_correct_behavior"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("profile_safety_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Опасные ссылки
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("profile_dangerous_links"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("profile_dont_click"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("profile_correct_behavior"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("profile_link_safety"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Защита детей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("profile_child_protection"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("profile_device_control"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("profile_device_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text(localizationManager.localized("profile_communication"))
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text(localizationManager.localized("profile_communication_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Финансовая безопасность
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("profile_financial_safety"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("profile_financial_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Экстренные ситуации
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text(localizationManager.localized("profile_emergency"))
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(localizationManager.localized("profile_emergency_rules"))
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("profile_safety_done")) {
                        isPresented = false
                    }
                }
            }
        }
    }
}

// MARK: - Preview

struct ProfileScreen_Previews: PreviewProvider {
    static var previews: some View {
        ProfileScreen()
    }
}



