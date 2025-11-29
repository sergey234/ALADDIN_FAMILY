import SwiftUI

/// 🎁 Referral Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Реферальная программа с системой бонусов
/// Источник дизайна: /mobile/wireframes/13_referral_screen.html
struct ReferralScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @State private var referralCode: String = "ALADDIN-SH2024"
    @State private var referralsCount: Int = 3
    @State private var paidReferralsCount: Int = 2 // Оплатившие друзья
    @State private var showShareSheet: Bool = false
    @State private var showQRCode: Bool = false
    @State private var showRewards: Bool = false
    @State private var showHowItWorks: Bool = false
    
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
                        
                        // Как это работает
                        howItWorksCard
                        
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
            RewardsView(paidReferralsCount: paidReferralsCount)
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
            
            Text("Вы и друг получите -20% скидку на 1 месяц")
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .accessibilityLabel("Вы и друг получите 20% скидку на 1 месяц")
            
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
                    title: "Приглашено",
                    value: "\(referralsCount)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "checkmark.circle.fill",
                    title: "Оплатили",
                    value: "\(paidReferralsCount)",
                    color: .successGreen
                )
                
                statCard(
                    icon: "percent",
                    title: "До 30%",
                    value: "\(paidReferralsCount)/3",
                    color: .warningOrange
                )
            }
            
            // Прогресс до 30% скидки
            if paidReferralsCount < 3 {
                VStack(spacing: Spacing.xs) {
                    Text("Прогресс до скидки 30%")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ProgressView(value: Double(paidReferralsCount), total: 3.0)
                        .progressViewStyle(LinearProgressViewStyle(tint: .secondaryGold))
                    
                    Text("Осталось пригласить: \(3 - paidReferralsCount)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .trailing)
                }
                .padding(.top, Spacing.s)
            } else {
                HStack {
                    Image(systemName: "crown.fill")
                        .foregroundColor(.secondaryGold)
                    Text("Вы достигли скидки 30%!")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .padding(Spacing.s)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.secondaryGold.opacity(0.2))
                )
                .padding(.top, Spacing.s)
            }
            
            // Прогресс до 10 рефералов (1 месяц бесплатно)
            if paidReferralsCount < 10 {
                VStack(spacing: Spacing.xs) {
                    Text("Прогресс до 1 месяца бесплатно")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ProgressView(value: Double(paidReferralsCount), total: 10.0)
                        .progressViewStyle(LinearProgressViewStyle(tint: .primaryBlue))
                    
                    Text("Осталось: \(10 - paidReferralsCount)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .trailing)
                }
                .padding(.top, Spacing.s)
            } else {
                HStack {
                    Image(systemName: "sparkles")
                        .foregroundColor(.primaryBlue)
                    Text("Вы получили 1 месяц бесплатно!")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .padding(Spacing.s)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.primaryBlue.opacity(0.2))
                )
                .padding(.top, Spacing.s)
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
    
    // MARK: - How It Works Card
    
    private var howItWorksCard: some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    showHowItWorks.toggle()
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.m) {
                    Text("❓")
                        .font(.system(size: 28))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text("КАК ЭТО РАБОТАЕТ")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text("3 простых шага к бонусам")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.leading)
                    }
                    
                    Spacer()
                    
                    Image(systemName: showHowItWorks ? "chevron.up" : "chevron.down")
                        .foregroundColor(.primaryBlue)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            if showHowItWorks {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    ForEach(howItWorksSteps, id: \.number) { step in
                        HStack(alignment: .top, spacing: Spacing.m) {
                            ZStack {
                                Circle()
                                    .fill(Color.primaryBlue.opacity(0.2))
                                    .frame(width: 32, height: 32)
                                
                                Text("\(step.number)")
                                    .font(.bodyBold)
                                    .foregroundColor(.primaryBlue)
                            }
                            
                            VStack(alignment: .leading, spacing: Spacing.xxs) {
                                Text(step.title)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Text(step.description)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                        }
                    }
                }
                .padding(.horizontal, Spacing.m)
                .padding(.bottom, Spacing.m)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
                )
        )
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
                    title: "WhatsApp",
                    subtitle: "Открыть WhatsApp",
                    action: {
                        openMessenger(type: .whatsapp)
                    }
                )
                
                invitationMethod(
                    icon: "paperplane.fill",
                    title: "Telegram",
                    subtitle: "Открыть Telegram",
                    action: {
                        openMessenger(type: .telegram)
                    }
                )
                
                invitationMethod(
                    icon: "network",
                    title: "VK",
                    subtitle: "Открыть VK",
                    action: {
                        openMessenger(type: .vk)
                    }
                )
                
                invitationMethod(
                    icon: "square.and.arrow.up",
                    title: "Еще способы",
                    subtitle: "Открыть системный шар",
                    action: {
                        openMessenger(type: .systemShare)
                    }
                )
                
                invitationMethod(
                    icon: "link",
                    title: "Копировать ссылку",
                    subtitle: "Скопировать приглашение",
                    action: {
                        copyToClipboard(text: referralLink, type: .link)
                    }
                )
                
                invitationMethod(
                    icon: "doc.on.doc",
                    title: "Копировать код",
                    subtitle: "Скопировать только код",
                    action: {
                        copyToClipboard(text: referralCode, type: .code)
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
                    title: "1 оплата",
                    reward: "-20%",
                    icon: "percent.circle.fill",
                    isUnlocked: paidReferralsCount >= 1,
                    subtitle: "Вам + другу"
                )
                
                rewardCard(
                    title: "3 оплаты",
                    reward: "-30%",
                    icon: "crown.fill",
                    isUnlocked: paidReferralsCount >= 3,
                    subtitle: "Ваша скидка"
                )
                
                rewardCard(
                    title: "10 оплат",
                    reward: "1 месяц",
                    icon: "star.fill",
                    isUnlocked: paidReferralsCount >= 10,
                    subtitle: "Бесплатно"
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
    
    private func rewardCard(title: String, reward: String, icon: String, isUnlocked: Bool, subtitle: String = "") -> some View {
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
            
            if !subtitle.isEmpty {
                Text(subtitle)
                    .font(.system(size: 10))
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
            }
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
        "🎁 Присоединяйся к ALADDIN! Мы оба получим скидку -20% на 1 месяц после тестового периода!\n\nИспользуй мой код: \(referralCode)\n\nСкачай: https://aladdin.family/invite/\(referralCode)\n\nС тобой на защите! 🛡️"
    }
    
    private var referralLink: String {
        "https://aladdin.family/invite/\(referralCode)"
    }
    
    // MARK: - Helper Functions
    
    private func openMessenger(type: MessengerType) {
        let message = referralText.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let encodedLink = referralLink.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        
        var urlString: String
        
        switch type {
        case .whatsapp:
            // WhatsApp Web link
            urlString = "https://wa.me/?text=\(message)"
        case .telegram:
            // Telegram Web Share (fallback to https if deep link fails)
            urlString = "https://t.me/share/url?url=\(encodedLink)&text=\(message)"
            // Try deep link first: tg://msg?text=\(message)
        case .vk:
            // VK Share
            urlString = "vk://share?url=\(encodedLink)"
        case .systemShare:
            showShareSheet = true
            return
        }
        
        if let url = URL(string: urlString) {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
            } else {
                // Fallback to system share
                showShareSheet = true
            }
        }
    }
    
    private func copyToClipboard(text: String, type: ClipboardType) {
        UIPasteboard.general.string = text
        HapticFeedback.selection()
    }
    
    private var referralHistory: [ReferralHistory] {
        [
            ReferralHistory(name: "Реферал #1", date: "2 дня назад", reward: "-20%", status: .completed),
            ReferralHistory(name: "Реферал #2", date: "1 неделя назад", reward: "-20%", status: .completed),
            ReferralHistory(name: "Реферал #3", date: "2 недели назад", reward: "Ожидает", status: .pending)
        ]
    }
    
    private var howItWorksSteps: [HowItWorksStep] {
        [
            HowItWorksStep(
                number: 1,
                title: "Поделитесь кодом",
                description: "Отправьте ваш реферальный код друзьям через WhatsApp, Telegram, VK или другие мессенджеры"
            ),
            HowItWorksStep(
                number: 2,
                title: "Друг регистрируется",
                description: "Друг использует ваш код при регистрации в ALADDIN и оформит любую платную подписку в течение 6 месяцев"
            ),
            HowItWorksStep(
                number: 3,
                title: "Получите бонусы",
                description: "Вы и друг получаете -20% скидку на 1 месяц! При 3 оплатах → -30% для вас! При 10 оплатах → 1 месяц бесплатно!"
            )
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

struct HowItWorksStep {
    let number: Int
    let title: String
    let description: String
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

enum MessengerType {
    case whatsapp
    case telegram
    case vk
    case systemShare
}

enum ClipboardType {
    case link
    case code
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
    let paidReferralsCount: Int
    
    var body: some View {
        VStack {
            Text("Все награды")
                .font(.h2)
            
            Text("Оплативших друзей: \(paidReferralsCount)")
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
