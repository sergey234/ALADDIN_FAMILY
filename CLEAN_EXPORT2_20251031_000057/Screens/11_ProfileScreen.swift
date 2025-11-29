import SwiftUI

/// 👤 Profile Screen
/// Экран профиля пользователя
/// Источник дизайна: /mobile/wireframes/11_profile_screen.html
struct ProfileScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
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
                    title: "ПРОФИЛЬ",
                    subtitle: "Личный кабинет",
                    showBackButton: true,
                    onBack: {
                        // Умная навигация назад: проверяем стек навигации
                        // Если есть стек - используем goBack(), иначе dismiss()
                        if navigationManager.canGoBack {
                            print("🔙 Возврат через NavigationManager.goBack()")
                            navigationManager.goBack()
                        } else {
                            print("🔙 Возврат через dismiss()")
                            dismiss()
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
        .onAppear {
            loadRegistrationDate()
        }
        .sheet(isPresented: $showImagePicker) {
            ProfileImagePicker(selectedImage: $selectedImage)
        }
        .sheet(isPresented: $showTwoFactor) {
            TwoFactorAuthView(isPresented: $showTwoFactor)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showActiveSessions) {
            ActiveSessionsView(isPresented: $showActiveSessions)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showDeleteAccount) {
            DeleteAccountView(isPresented: $showDeleteAccount)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showEditProfile) {
            EditProfileView(isPresented: $showEditProfile)
                .environmentObject(navigationManager)
        }
        .sheet(isPresented: $showAdultSafetyInstructions) {
            AdultSafetyInstructionsModal(isPresented: $showAdultSafetyInstructions)
        }
        .sheet(isPresented: $showReferralScreen) {
            ReferralScreen()
        }
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
                
                Text("Premium")
                    .font(.body.bold())
                    .foregroundColor(.yellow)
                
                Text("до 31.12.2025")
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
            statCard(icon: "🛡️", value: "47", label: "Угроз\nзаблокировано")
            statCard(icon: "👥", value: "4", label: "Членов\nсемьи")
            statCard(icon: "📱", value: "8", label: "Устройств")
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
            sectionTitle("ЛИЧНАЯ ИНФОРМАЦИЯ")
            
            VStack(spacing: Spacing.s) {
                infoRow(icon: "person", label: "Имя", value: "Сергей Хлыстов")
                infoRow(icon: "envelope", label: "Email", value: "", optional: true)
                infoRow(icon: "phone", label: "Телефон", value: "", optional: true)
                infoRow(icon: "calendar", label: "Дата регистрации", value: registrationDate.isEmpty ? "Не установлена" : registrationDate)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle("БЕЗОПАСНОСТЬ")
            
            VStack(spacing: Spacing.s) {
                securityButton(icon: "🛡️", title: "Инструкции безопасности", action: { showAdultSafetyInstructions = true })
                securityButton(icon: "📱", title: "Двухфакторная аутентификация", action: { showTwoFactor = true })
                securityButton(icon: "🔑", title: "Активные сеансы", action: { showActiveSessions = true })
                securityButton(icon: "🗑️", title: "Удалить аккаунт", color: .red, action: { showDeleteAccount = true })
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Referral Section
    
    private var referralSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle("РЕФЕРАЛЬНАЯ ПРОГРАММА")
            
            VStack(spacing: Spacing.s) {
                Button(action: {
                    showReferralScreen = true
                }) {
                    HStack(spacing: Spacing.m) {
                        Text("🎁")
                            .font(.system(size: 24))
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text("Пригласить друзей")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Text("Получи -20% скидку на 1 месяц")
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
                    Text("Не указано")
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
    
    var body: some View {
        NavigationView {
            List {
                ForEach(0..<3, id: \.self) { index in
                    HStack {
                        VStack(alignment: .leading) {
                            Text("iPhone 13")
                                .font(.headline)
                            HStack {
                                Text("Москва, Россия")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                Text("•")
                                Text("Сейчас")
                                    .font(.caption)
                                    .foregroundColor(.green)
                            }
                            Spacer()
                            Button("Выйти") { }
                        }
                    }
                }
            }
            .navigationTitle("Активные сеансы")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Готово") { isPresented = false }
                }
            }
        }
    }
}

struct DeleteAccountView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var confirmText: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Внимание!")) {
                    Text("Удаление аккаунта необратимо. Все ваши данные будут удалены.")
                        .foregroundColor(.red)
                }
                Section(header: Text("Подтверждение")) {
                    TextField("Введите УДАЛИТЬ", text: $confirmText)
                    Text("Введите слово УДАЛИТЬ заглавными буквами для подтверждения")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Button("Удалить аккаунт") {
                    if confirmText == "УДАЛИТЬ" {
                        isPresented = false
                    }
                }
                .buttonStyle(.borderedProminent)
                .foregroundColor(.red)
                .disabled(confirmText != "УДАЛИТЬ")
            }
            .padding()
            .navigationTitle("Удалить аккаунт")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") { isPresented = false }
                }
            }
        }
    }
}

struct EditProfileView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var name: String = "Сергей Хлыстов"
    @State private var email: String = "sergey@aladdin.family"
    @State private var phone: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Личная информация")) {
                    TextField("Имя", text: $name)
                    TextField("Email", text: $email)
                    TextField("Телефон", text: $phone)
                }
                Section {
                    Button("Сохранить") {
                        isPresented = false
                    }
                    .buttonStyle(.borderedProminent)
                    .frame(maxWidth: .infinity)
                }
                .padding()
            }
            .navigationTitle("Редактировать профиль")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") { isPresented = false }
                }
            }
        }
    }
}

// MARK: - Adult Safety Instructions Modal

struct AdultSafetyInstructionsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    Text("🛡️ Памятка безопасности для родителей")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.primary)
                    
                    // Защита от мошенников
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🚫 НЕ ВЕРИТЕ звонкам от:")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("• Сотрудников ФСБ, Прокуратуры, Начальства")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("• Банков, Соцсетей, Незнакомцев")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Никогда не называйте пароли\n• Не переводите деньги\n• Не устанавливайте программы\n• Сразу кладите трубку")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Опасные ссылки
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🔗 Опасные ссылки")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("❌ НЕ НАЖИМАЙТЕ на: Ссылки в SMS, WhatsApp, письмах, неизвестные сайты")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("✅ ПРАВИЛЬНО:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.green)
                            .padding(.top, Spacing.s)
                        
                        Text("• Используйте кнопку 'Проверить сайт'\n• Проверяйте адрес сайта\n• Не вводите данные на подозрительных сайтах")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                    }
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Защита детей
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("👶 Защита детей")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("📱 Контроль устройств:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text("• Используйте родительский контроль\n• Ограничивайте время экрана\n• Проверяйте историю браузера\n• Блокируйте нежелательные сайты")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                        
                        Text("💬 Общение с детьми:")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.purple)
                            .padding(.top, Spacing.s)
                        
                        Text("• Объясняйте правила безопасности\n• Рассказывайте о мошенниках\n• Учите не доверять незнакомцам\n• Поощряйте рассказывать о подозрительных сообщениях")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.purple.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Финансовая безопасность
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("💰 Финансовая безопасность")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("• Никогда не переводите деньги по телефону\n• Проверяйте номера карт перед операциями\n• Используйте только официальные приложения банков\n• Не храните пароли в открытом виде")
                            .font(.system(size: 16))
                            .foregroundColor(.primary)
                            .padding(.vertical, Spacing.xs)
                    }
                    .padding()
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Экстренные ситуации
                    VStack(alignment: .leading, spacing: Spacing.m) {
                        Text("🚨 Экстренные ситуации")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text("• При подозрении на мошенничество - сразу блокируйте карты\n• Сохраняйте скриншоты подозрительных сообщений\n• Обращайтесь в банк и полицию\n• Используйте функцию экстренного звонка в приложении")
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



