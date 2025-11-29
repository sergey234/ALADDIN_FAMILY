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
    @State private var showPasswordChange: Bool = false
    @State private var showTwoFactor: Bool = false
    @State private var showActiveSessions: Bool = false
    @State private var showDeleteAccount: Bool = false
    @State private var showEditProfile: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: { 
                        print("🔍 DEBUG: Кнопка 'Назад' нажата в ProfileScreen")
                        navigationManager.goBack()
                        print("🔍 DEBUG: NavigationManager.goBack() вызван")
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(
                                Circle()
                                    .fill(Color.blue.opacity(0.2))
                            )
                    }
                    .accessibilityLabel("Назад")
                    
                    Spacer()
                    
                    Text("ПРОФИЛЬ")
                        .font(.headline)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Button(action: { showEditProfile = true }) {
                        Image(systemName: "pencil")
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                }
                .padding()
                .background(Color.black.opacity(0.5))
                
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
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.s)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showImagePicker) {
            ProfileImagePicker(selectedImage: $selectedImage)
        }
        .sheet(isPresented: $showPasswordChange) {
            ChangePasswordView(isPresented: $showPasswordChange)
                .environmentObject(navigationManager)
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
                infoRow(icon: "calendar", label: "Дата регистрации", value: "15 сентября 2025")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            sectionTitle("БЕЗОПАСНОСТЬ")
            
            VStack(spacing: Spacing.s) {
                securityButton(icon: "🔐", title: "Изменить пароль", action: { showPasswordChange = true })
                securityButton(icon: "📱", title: "Двухфакторная аутентификация", action: { showTwoFactor = true })
                securityButton(icon: "🔑", title: "Активные сеансы", action: { showActiveSessions = true })
                securityButton(icon: "🗑️", title: "Удалить аккаунт", color: .red, action: { showDeleteAccount = true })
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

struct ChangePasswordView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var currentPassword: String = ""
    @State private var newPassword: String = ""
    @State private var confirmPassword: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Текущий пароль")) {
                    SecureField("Введите текущий пароль", text: $currentPassword)
                }
                Section(header: Text("Новый пароль")) {
                    SecureField("Введите новый пароль", text: $newPassword)
                    SecureField("Подтвердите новый пароль", text: $confirmPassword)
                }
                Button("Изменить пароль") {
                    isPresented = false
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            .navigationTitle("Изменить пароль")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") { isPresented = false }
                }
            }
        }
    }
}

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

// MARK: - Preview

struct ProfileScreen_Previews: PreviewProvider {
    static var previews: some View {
        ProfileScreen()
    }
}



