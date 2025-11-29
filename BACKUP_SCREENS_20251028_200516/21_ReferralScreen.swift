import SwiftUI

/// 🎁 Referral Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Реферальная программа с системой бонусов
/// Источник дизайна: /mobile/wireframes/13_referral_screen.html
struct ReferralScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @State private var referralCode: String = "ALADDIN-SH2024"
    @State private var referralsCount: Int = 3
    @State private var earnedBonus: Int = 1500
    @State private var showShareSheet: Bool = false
    @State private var showQRCode: Bool = false
    @State private var showRewards: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана реферальной программы")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Главный баннер
                        mainBanner
                        
                        // Ваша статистика
                        yourStats
                        
                        // Реферальный код
                        referralCodeSection
                        
                        // Способы приглашения
                        invitationMethods
                        
                        // Награды
                        rewardsSection
                        
                        // История рефералов
                        referralsHistory
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Реферальная программа")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(activityItems: [referralText])
        }
        .sheet(isPresented: $showQRCode) {
            QRCodeView(code: referralCode)
        }
        .sheet(isPresented: $showRewards) {
            RewardsView(earnedBonus: earnedBonus)
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "РЕФЕРАЛЬНАЯ ПРОГРАММА",
            subtitle: "Приглашай друзей - получай бонусы",
            showBackButton: true,
            onBack: { 
                dismiss() 
            }
        )
        .padding(.bottom, Spacing.m)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель реферальной программы")
    }
    
    // MARK: - Main Banner
    
    private var mainBanner: some View {
        VStack(spacing: Spacing.l) {
            Text("🎁")
                .font(.system(size: Size.iconXLarge * 1.5))
                .accessibilityLabel("Подарок")
            
            Text("Пригласи друзей")
                .font(.h1)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
            
            Text("Получи 500₽ за каждого друга")
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .accessibilityLabel("Получи 500 рублей за каждого друга")
            
            // Кнопка пригласить
            Button(action: {
                showShareSheet = true
            }) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "square.and.arrow.up")
                        .font(.system(size: 16))
                    
                    Text("Пригласить друзей")
                        .font(.bodyBold)
                }
                .foregroundColor(.white)
                .padding(.horizontal, Spacing.xl)
                .padding(.vertical, Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.button)
                        .fill(LinearGradient(
                            colors: [.primaryBlue, .secondaryBlue],
                            startPoint: .leading,
                            endPoint: .trailing
                        ))
                )
            }
            .accessibilityLabel("Пригласить друзей")
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Your Stats
    
    private var yourStats: some View {
        VStack(spacing: Spacing.m) {
            Text("ВАША СТАТИСТИКА")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.m) {
                statCard(
                    icon: "person.2.fill",
                    title: "Рефералов",
                    value: "\(referralsCount)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "rublesign.circle.fill",
                    title: "Заработано",
                    value: "\(earnedBonus)₽",
                    color: .successGreen
                )
                
                statCard(
                    icon: "gift.fill",
                    title: "Наград",
                    value: "\(referralsCount * 2)",
                    color: .warningOrange
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Referral Code Section
    
    private var referralCodeSection: some View {
        VStack(spacing: Spacing.m) {
            Text("ВАШ РЕФЕРАЛЬНЫЙ КОД")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.m) {
                // Код
                HStack {
                    Text(referralCode)
                        .font(.system(.title2, design: .monospaced))
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Button(action: {
                        UIPasteboard.general.string = referralCode
                    }) {
                        Image(systemName: "doc.on.doc")
                            .font(.system(size: 16))
                            .foregroundColor(.primaryBlue)
                    }
                    .accessibilityLabel("Скопировать код")
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Реферальный код: \(referralCode)")
                
                // Кнопки действий
                HStack(spacing: Spacing.s) {
                    Button(action: {
                        UIPasteboard.general.string = referralCode
                    }) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "doc.on.doc")
                            Text("Копировать")
                        }
                        .font(.body)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                    }
                    .accessibilityLabel("Скопировать код")
                    
                    Button(action: {
                        showQRCode = true
                    }) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "qrcode")
                            Text("QR код")
                        }
                        .font(.body)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                    }
                    .accessibilityLabel("Показать QR код")
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Invitation Methods
    
    private var invitationMethods: some View {
        VStack(spacing: Spacing.m) {
            Text("СПОСОБЫ ПРИГЛАШЕНИЯ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                invitationMethod(
                    icon: "message.fill",
                    title: "Сообщение",
                    subtitle: "Отправить код в сообщении",
                    action: {
                        showShareSheet = true
                    }
                )
                
                invitationMethod(
                    icon: "mail.fill",
                    title: "Email",
                    subtitle: "Отправить на почту",
                    action: {
                        showShareSheet = true
                    }
                )
                
                invitationMethod(
                    icon: "qrcode",
                    title: "QR код",
                    subtitle: "Показать QR код",
                    action: {
                        showQRCode = true
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Rewards Section
    
    private var rewardsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("НАГРАДЫ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Button(action: {
                    showRewards = true
                }) {
                    Text("Все награды")
                        .font(.body)
                        .foregroundColor(.primaryBlue)
                }
                .accessibilityLabel("Показать все награды")
            }
            
            HStack(spacing: Spacing.m) {
                rewardCard(
                    title: "1 реферал",
                    reward: "500₽",
                    icon: "rublesign.circle.fill",
                    isUnlocked: referralsCount >= 1
                )
                
                rewardCard(
                    title: "3 реферала",
                    reward: "2000₽",
                    icon: "gift.fill",
                    isUnlocked: referralsCount >= 3
                )
                
                rewardCard(
                    title: "5 рефералов",
                    reward: "5000₽",
                    icon: "crown.fill",
                    isUnlocked: referralsCount >= 5
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Referrals History
    
    private var referralsHistory: some View {
        VStack(spacing: Spacing.m) {
            Text("ИСТОРИЯ РЕФЕРАЛОВ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                ForEach(referralHistory, id: \.id) { referral in
                    referralRow(referral: referral)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func statCard(icon: String, title: String, value: String, color: Color) -> some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(color.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
    
    private func invitationMethod(icon: String, title: String, subtitle: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Image(systemName: icon)
                    .font(.system(size: 20))
                    .foregroundColor(.primaryBlue)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
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
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle)")
    }
    
    private func rewardCard(title: String, reward: String, icon: String, isUnlocked: Bool) -> some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(isUnlocked ? .successGreen : .textSecondary)
            
            Text(reward)
                .font(.h3)
                .foregroundColor(isUnlocked ? .textPrimary : .textSecondary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(isUnlocked ? Color.successGreen.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(reward), \(isUnlocked ? "разблокировано" : "заблокировано")")
    }
    
    private func referralRow(referral: ReferralHistory) -> some View {
        HStack(spacing: Spacing.m) {
            Circle()
                .fill(referral.status.color)
                .frame(width: 12, height: 12)
                .accessibilityLabel("Статус: \(referral.status.rawValue)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(referral.name)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text(referral.date)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text(referral.reward)
                .font(.bodyBold)
                .foregroundColor(.successGreen)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(referral.name), \(referral.date), награда \(referral.reward)")
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Computed Properties
    
    private var referralText: String {
        "Привет! Я использую ALADDIN для защиты моих устройств. Присоединяйся! Мой реферальный код: \(referralCode)"
    }
    
    private var referralHistory: [ReferralHistory] {
        [
            ReferralHistory(name: "Анна Петрова", date: "2 дня назад", reward: "500₽", status: .completed),
            ReferralHistory(name: "Михаил Иванов", date: "1 неделя назад", reward: "500₽", status: .completed),
            ReferralHistory(name: "Елена Сидорова", date: "2 недели назад", reward: "500₽", status: .pending)
        ]
    }
}

// MARK: - Models

struct ReferralHistory {
    let id = UUID()
    let name: String
    let date: String
    let reward: String
    let status: ReferralStatus
}

enum ReferralStatus: String, CaseIterable {
    case completed = "Завершено"
    case pending = "В ожидании"
    case cancelled = "Отменено"
    
    var color: Color {
        switch self {
        case .completed: return .successGreen
        case .pending: return .warningOrange
        case .cancelled: return .textSecondary
        }
    }
}

// MARK: - Placeholder Views

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

struct QRCodeView: View {
    let code: String
    
    var body: some View {
        VStack {
            Text("QR код")
                .font(.h2)
            
            Text(code)
                .font(.body)
        }
        .padding()
    }
}

struct RewardsView: View {
    let earnedBonus: Int
    
    var body: some View {
        VStack {
            Text("Все награды")
                .font(.h2)
            
            Text("Заработано: \(earnedBonus)₽")
                .font(.body)
        }
        .padding()
    }
}

// MARK: - Preview

struct ReferralScreen_Previews: PreviewProvider {
    static var previews: some View {
        ReferralScreen()
    }
}
