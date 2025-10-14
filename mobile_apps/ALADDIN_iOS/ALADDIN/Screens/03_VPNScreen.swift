import SwiftUI

/// 🛡️ VPN Screen
/// Экран VPN защиты - управление VPN подключением
/// Источник дизайна: /mobile/wireframes/02_protection_screen.html
struct VPNScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isVPNEnabled: Bool = true
    @State private var selectedServer: String = "Россия • Москва"
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "VPN ЗАЩИТА",
                    subtitle: isVPNEnabled ? "Подключено" : "Отключено",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    },
                    rightButtons: [
                        .init(icon: "gearshape") {
                            print("Настройки VPN")
                        }
                    ]
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // VPN Status (большая карточка)
                        vpnStatusCard
                        
                        // Кнопка включения VPN
                        vpnToggleButton
                        
                        // Выбор сервера
                        serverSelection
                        
                        // Статистика
                        statisticsSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - VPN Status Card
    
    private var vpnStatusCard: some View {
        VStack(spacing: Spacing.l) {
            // Иконка и статус
            VStack(spacing: Spacing.m) {
                // Анимированная иконка щита
                ZStack {
                    Circle()
                        .fill(
                            isVPNEnabled ?
                            Color.successGreen.opacity(0.2) :
                            Color.textSecondary.opacity(0.2)
                        )
                        .frame(width: 120, height: 120)
                    
                    Text(isVPNEnabled ? "🛡️" : "🔒")
                        .font(.system(size: 60))
                }
                
                // Статус текст
                VStack(spacing: Spacing.xs) {
                    Text(isVPNEnabled ? "ЗАЩИЩЕНО" : "НЕ ЗАЩИЩЕНО")
                        .font(.h1)
                        .foregroundColor(isVPNEnabled ? .successGreen : .dangerRed)
                    
                    Text(isVPNEnabled ? "Ваше соединение зашифровано" : "Включите VPN для защиты")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
            }
            
            // IP адрес
            if isVPNEnabled {
                HStack(spacing: Spacing.s) {
                    Text("🌐")
                        .font(.system(size: 20))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text("Ваш IP адрес")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Text("192.168.1.147")
                            .font(.bodyBold)
                            .foregroundColor(.primaryBlue)
                    }
                    
                    Spacer()
                    
                    Button(action: {
                        print("Копировать IP")
                    }) {
                        Image(systemName: "doc.on.doc")
                            .font(.system(size: 18))
                            .foregroundColor(.primaryBlue)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(
                            isVPNEnabled ?
                            Color.successGreen.opacity(0.3) :
                            Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - VPN Toggle Button
    
    private var vpnToggleButton: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                isVPNEnabled.toggle()
            }
        }) {
            HStack(spacing: Spacing.m) {
                Image(systemName: isVPNEnabled ? "stop.circle.fill" : "play.circle.fill")
                    .font(.system(size: 28))
                
                Text(isVPNEnabled ? "Отключить VPN" : "Включить VPN")
                    .font(.buttonText)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: Size.buttonHeight)
            .background(
                LinearGradient(
                    colors: isVPNEnabled ?
                        [Color.dangerRed, Color(hex: "#DC2626")] :
                        [Color.successGreen, Color(hex: "#16A34A")],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(CornerRadius.large)
            .cardShadow()
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Server Selection
    
    private var serverSelection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("СЕРВЕР")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Кнопка выбора сервера
            Button(action: {
                print("Выбрать сервер")
            }) {
                HStack(spacing: Spacing.m) {
                    // Флаг
                    Text("🇷🇺")
                        .font(.system(size: 32))
                    
                    // Текст
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(selectedServer)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        HStack(spacing: Spacing.xs) {
                            Circle()
                                .fill(Color.successGreen)
                                .frame(width: 8, height: 8)
                            
                            Text("Ping: 12 ms")
                                .font(.caption)
                                .foregroundColor(.successGreen)
                        }
                    }
                    
                    Spacer()
                    
                    // Стрелка
                    Image(systemName: "chevron.right")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.textSecondary)
                }
                .padding(Spacing.cardPadding)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                .cardShadow()
            }
            .buttonStyle(PlainButtonStyle())
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Statistics Section
    
    private var statisticsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("СТАТИСТИКА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Карточки статистики
            VStack(spacing: Spacing.s) {
                statCard(
                    icon: "⬇️",
                    title: "Загружено",
                    value: "2.4 GB",
                    subtitle: "За сегодня"
                )
                
                statCard(
                    icon: "⬆️",
                    title: "Отправлено",
                    value: "1.2 GB",
                    subtitle: "За сегодня"
                )
                
                statCard(
                    icon: "⏱️",
                    title: "Время сессии",
                    value: "4:37:21",
                    subtitle: "Активная сессия"
                )
                
                statCard(
                    icon: "🛡️",
                    title: "Заблокировано",
                    value: "47",
                    subtitle: "Угроз за неделю"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func statCard(
        icon: String,
        title: String,
        value: String,
        subtitle: String
    ) -> some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
            
            // Текст
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Text(subtitle)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}

// MARK: - Preview

#if DEBUG
struct VPNScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNScreen()
    }
}
#endif




