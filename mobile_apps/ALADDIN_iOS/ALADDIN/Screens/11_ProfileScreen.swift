import SwiftUI

/// 👤 Profile Screen
/// Экран профиля пользователя
/// Источник дизайна: /mobile/wireframes/11_profile_screen.html
struct ProfileScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "ПРОФИЛЬ",
                    subtitle: "Личная информация",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    },
                    rightButtons: [
                        .init(icon: "pencil") {
                            print("Редактировать профиль")
                        }
                    ]
                )
                
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
                    .padding(.top, Spacing.l)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Profile Header
    
    private var profileHeader: some View {
        VStack(spacing: Spacing.l) {
            // Большой аватар
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.primaryBlue, Color.secondaryBlue],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 100, height: 100)
                
                Text("👨")
                    .font(.system(size: 60))
            }
            
            // Имя и email
            VStack(spacing: Spacing.xs) {
                Text("Сергей Хлыстов")
                    .font(.h2)
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
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                Text("до 31.12.2025")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            .padding(.horizontal, Spacing.l)
            .padding(.vertical, Spacing.s)
            .background(
                Capsule()
                    .fill(Color.secondaryGold.opacity(0.2))
                    .overlay(
                        Capsule()
                            .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
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
                .font(.h2)
                .foregroundColor(.primaryBlue)
            
            Text(label)
                .font(.captionSmall)
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
                infoRow(icon: "envelope", label: "Email", value: "sergey@aladdin.family")
                infoRow(icon: "phone", label: "Телефон", value: "+7 (999) 123-45-67")
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
                securityButton(icon: "🔐", title: "Изменить пароль")
                securityButton(icon: "📱", title: "Двухфакторная аутентификация")
                securityButton(icon: "🔑", title: "Активные сеансы")
                securityButton(icon: "🗑️", title: "Удалить аккаунт", color: .dangerRed)
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
    
    private func infoRow(icon: String, label: String, value: String) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(.primaryBlue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.body)
                    .foregroundColor(.textPrimary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    private func securityButton(icon: String, title: String, color: Color = .textPrimary) -> some View {
        Button(action: {
            print(title)
        }) {
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

// MARK: - Preview

#if DEBUG
struct ProfileScreen_Previews: PreviewProvider {
    static var previews: some View {
        ProfileScreen()
    }
}
#endif




