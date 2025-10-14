import SwiftUI

/**
 * 🎁 Referral Screen
 * Реферальная программа
 * 13_referral_screen из HTML
 */

struct ReferralScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var referralCode: String = "ALADDIN-SH2024"
    @State private var referralsCount: Int = 3
    @State private var earnedBonus: Int = 1500
    @State private var showShareSheet: Bool = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: "РЕФЕРАЛЬНАЯ ПРОГРАММА",
                    subtitle: "Приглашай друзей - получай бонусы",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                .padding(.bottom, Spacing.m)
                
                // Referral Stats
                VStack(spacing: Spacing.xl) {
                    Text("🎁")
                        .font(.system(size: Size.iconXLarge * 1.5))
                    
                    Text("Пригласи друзей")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    Text("Получи 500₽ за каждого друга")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    // Your Stats
                    HStack {
                        Spacer()
                        VStack {
                            Text("\(referralsCount)")
                                .font(.largeTitle)
                                .foregroundColor(.secondaryGold)
                            Text("Приглашено")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        VStack {
                            Text("\(earnedBonus)₽")
                                .font(.largeTitle)
                                .foregroundColor(.successGreen)
                            Text("Заработано")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                    }
                    .padding(Spacing.cardPadding)
                    .background(
                        LinearGradient.cardGradient
                            .appGlassmorphism()
                    )
                    .cornerRadius(CornerRadius.large)
                    .cardShadow()
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Your Referral Code
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("ВАШ РЕФЕРАЛЬНЫЙ КОД")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    HStack {
                        Text(referralCode)
                            .font(.h2)
                            .foregroundColor(.secondaryGold)
                        Spacer()
                        Button(action: {
                            UIPasteboard.general.string = referralCode
                            HapticFeedback.heavyImpact()
                        }) {
                            HStack(spacing: Spacing.xs) {
                                Image(systemName: "doc.on.doc.fill")
                                    .foregroundColor(.textPrimary)
                                Text("Копировать")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                            }
                            .padding(.vertical, Spacing.s)
                            .padding(.horizontal, Spacing.m)
                            .background(Color.primaryBlue)
                            .cornerRadius(CornerRadius.medium)
                        }
                    }
                    .padding(Spacing.cardPadding)
                    .background(
                        LinearGradient.cardGradient
                            .appGlassmorphism()
                    )
                    .cornerRadius(CornerRadius.large)
                    .cardShadow()
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Share Buttons
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("ПОДЕЛИТЬСЯ")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    PrimaryButton(title: "Поделиться с друзьями") {
                        showShareSheet = true
                    }
                    
                    SecondaryButton(title: "Отправить в WhatsApp", icon: nil) {
                        shareToWhatsApp()
                    }
                    
                    SecondaryButton(title: "Отправить в Telegram", icon: nil) {
                        shareToTelegram()
                    }
                    
                    SecondaryButton(title: "Отправить в VK", icon: nil) {
                        shareToVK()
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // How it Works
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("КАК ЭТО РАБОТАЕТ")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    VStack(spacing: Spacing.m) {
                        StepCard(number: 1, title: "Поделитесь кодом", description: "Отправьте ваш код друзьям")
                        StepCard(number: 2, title: "Друг регистрируется", description: "Друг использует ваш код при регистрации")
                        StepCard(number: 3, title: "Получите бонус", description: "Вы получаете 500₽, друг получает скидку 20%")
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Your Referrals List
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("ВАШИ ПРИГЛАШЕНИЯ")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    ReferralRow(name: "Александр К.", date: "15.10.2025", bonus: 500, status: .completed)
                    ReferralRow(name: "Мария С.", date: "12.10.2025", bonus: 500, status: .completed)
                    ReferralRow(name: "Иван П.", date: "10.10.2025", bonus: 500, status: .pending)
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(items: ["Присоединяйся к ALADDIN! Используй мой код: \(referralCode) и получи скидку 20%! https://aladdin.family/register?ref=\(referralCode)"])
        }
    }
    
    // MARK: - Actions
    
    private func shareToWhatsApp() {
        let text = "Присоединяйся к ALADDIN! Используй мой код: \(referralCode)"
        if let url = URL(string: "whatsapp://send?text=\(text.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") {
            UIApplication.shared.open(url)
        }
    }
    
    private func shareToTelegram() {
        let text = "Присоединяйся к ALADDIN! Код: \(referralCode)"
        if let url = URL(string: "tg://msg?text=\(text.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") {
            UIApplication.shared.open(url)
        }
    }
    
    private func shareToVK() {
        print("Share to VK")
    }
}

// MARK: - Step Card

struct StepCard: View {
    let number: Int
    let title: String
    let description: String
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text("\(number)")
                .font(.h1)
                .foregroundColor(.secondaryGold)
                .frame(width: 50, height: 50)
                .background(Color.surfaceDark)
                .cornerRadius(CornerRadius.medium)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
    }
}

// MARK: - Referral Row

struct ReferralRow: View {
    let name: String
    let date: String
    let bonus: Int
    let status: ReferralStatus
    
    enum ReferralStatus {
        case completed, pending
        
        var color: Color {
            switch self {
            case .completed: return .successGreen
            case .pending: return .warningOrange
            }
        }
        
        var text: String {
            switch self {
            case .completed: return "Получено"
            case .pending: return "Ожидание"
            }
        }
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                Text(date)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: Spacing.xxs) {
                Text("+\(bonus)₽")
                    .font(.bodyBold)
                    .foregroundColor(status.color)
                Text(status.text)
                    .font(.captionSmall)
                    .foregroundColor(status.color)
            }
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.medium)
        .cardShadow()
    }
}

// MARK: - Share Sheet

struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - Preview

struct ReferralScreen_Previews: PreviewProvider {
    static var previews: some View {
        ReferralScreen()
    }
}




