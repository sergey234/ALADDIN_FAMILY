import SwiftUI

/// 👤 Profile Screen
/// Экран профиля пользователя
/// Источник дизайна: /mobile/wireframes/11_profile_screen.html
struct ProfileScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showImagePicker: Bool = false
    @State private var selectedImage: UIImage?
    @State private var showTwoFactor: Bool = false
    @State private var showActiveSessions: Bool = false
    @State private var showDeleteAccount: Bool = false
    @State private var showEditProfile: Bool = false
    @State private var showAdultSafetyInstructions: Bool = false
    @State private var showReferralScreen: Bool = false
    @State private var registrationDate: String = ""
    
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
                Text("Сергей Хлыстов")
                    .font(.title2)
                    .foregroundColor(.white)
                
                Text("sergey@aladdin.family")
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }
            
            // Статус подписки
            HStack(spacing: Spacing.s) {
                Text("⭐")
                    .font(.system(size: 20))
                
                Text(localizationManager.localized("profile_premium"))
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
                infoRow(icon: "person", label: localizationManager.localized("profile_name"), value: "Сергей Хлыстов")
                infoRow(icon: "envelope", label: localizationManager.localized("profile_email"), value: "", optional: true)
                infoRow(icon: "phone", label: localizationManager.localized("profile_phone"), value: "", optional: true)
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
            formatter.locale = Locale(identifier: "ru_RU")
            registrationDate = formatter.string(from: savedDate)
        } else {
            // Если дата не сохранена, используем текущую дату
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMMM yyyy"
            formatter.locale = Locale(identifier: "ru_RU")
            registrationDate = formatter.string(from: Date())
        }
    }
    
    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        selectedImage = ProfileImageManager.shared.loadProfileImage()
    }
    
    private func saveProfileImage(_ image: UIImage) {
        _ = ProfileImageManager.shared.saveProfileImage(image)
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
    @State private var isEnabled: Bool = false
    
    var body: some View {
        NavigationView {
            Form {
                Toggle("Включить 2FA", isOn: $isEnabled)
                Text(isEnabled ? "Включена" : "Выключена")
                    .foregroundColor(isEnabled ? .green : .gray)
            }
            .padding()
            .navigationTitle("2FA")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Готово") { isPresented = false }
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
                    Text(localizationManager.localized("profile_delete_confirm_text"))
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Button(localizationManager.localized("delete_account_button")) {
                    if confirmText.uppercased() == confirmTextRequired {
                        isPresented = false
                    }
                }
                .buttonStyle(.borderedProminent)
                .foregroundColor(.red)
                .disabled(confirmText.uppercased() != confirmTextRequired)
            }
            .padding()
            .navigationTitle(localizationManager.localized("delete_account_title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("delete_account_cancel")) { isPresented = false }
                }
            }
            .id("delete_account_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }
}

struct EditProfileView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var name: String = "Сергей Хлыстов"
    @State private var email: String = "sergey@aladdin.family"
    @State private var phone: String = ""
    
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
                    TextField(localizationManager.localized("edit_profile_email"), text: $email)
                    TextField(localizationManager.localized("edit_profile_phone"), text: $phone)
                }
                
                Section {
                    Button(localizationManager.localized("edit_profile_reset_password")) {
                        // TODO: Реализовать сброс пароля
                    }
                    .foregroundColor(.blue)
                }
                
                Section {
                    Button(localizationManager.localized("edit_profile_save")) {
                        isPresented = false
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
                        isPresented = false
                    }
                }
            }
            .id("edit_profile_lang_\(localizationManager.currentLanguage.rawValue)")
        }
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
                    Button("Готово") {
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



