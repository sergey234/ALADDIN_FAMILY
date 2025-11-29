import SwiftUI

/// 🎁 Referral Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Реферальная программа с системой бонусов
/// Источник дизайна: /mobile/wireframes/13_referral_screen.html
struct ReferralScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
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
                .accessibilityLabel(localizationManager.localized("referral_background"))
            
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
                .accessibilityLabel(localizationManager.localized("referral_background"))
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
            title: localizationManager.localized("referral_title"),
            subtitle: localizationManager.localized("referral_subtitle"),
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
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
        .padding(.bottom, Spacing.m)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("referral_nav_accessibility"))
    }
    
    // MARK: - Main Banner
    
    private var mainBanner: some View {
        VStack(spacing: Spacing.l) {
            Text("🎁")
                .font(.system(size: Size.iconXLarge * 1.5))
                .accessibilityLabel(localizationManager.localized("referral_gift_icon"))
            
            Text(localizationManager.localized("referral_invite_friends_title"))
                .font(.h1)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
            
            Text(localizationManager.localized("referral_invite_friends_desc"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .accessibilityLabel(localizationManager.localized("referral_invite_friends_desc"))
            
            // Кнопка пригласить
            Button(action: {
                showShareSheet = true
            }) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: "square.and.arrow.up")
                        .font(.system(size: 16))
                    
                    Text(localizationManager.localized("referral_invite_button"))
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
            .accessibilityLabel(localizationManager.localized("referral_invite_button"))
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Your Stats
    
    private var yourStats: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("referral_stats_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.m) {
                statCard(
                    icon: "person.2.fill",
                    title: localizationManager.localized("referral_stats_invited"),
                    value: "\(referralsCount)",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "checkmark.circle.fill",
                    title: localizationManager.localized("referral_stats_paid"),
                    value: "\(paidReferralsCount)",
                    color: .successGreen
                )
                
                statCard(
                    icon: "percent",
                    title: localizationManager.localized("referral_stats_discount"),
                    value: "\(paidReferralsCount)/3",
                    color: .warningOrange
                )
            }
            
            // Прогресс до 30% скидки
            if paidReferralsCount < 3 {
                VStack(spacing: Spacing.xs) {
                    Text(localizationManager.localized("referral_progress_30_title"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ProgressView(value: Double(paidReferralsCount), total: 3.0)
                        .progressViewStyle(LinearProgressViewStyle(tint: .secondaryGold))
                    
                    Text(String(format: localizationManager.localized("referral_progress_30_remaining"), 3 - paidReferralsCount))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .trailing)
                }
                .padding(.top, Spacing.s)
            } else {
                HStack {
                    Image(systemName: "crown.fill")
                        .foregroundColor(.secondaryGold)
                    Text(localizationManager.localized("referral_progress_30_achieved"))
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
                    Text(localizationManager.localized("referral_progress_month_title"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ProgressView(value: Double(paidReferralsCount), total: 10.0)
                        .progressViewStyle(LinearProgressViewStyle(tint: .primaryBlue))
                    
                    Text(String(format: localizationManager.localized("referral_progress_month_remaining"), 10 - paidReferralsCount))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .trailing)
                }
                .padding(.top, Spacing.s)
            } else {
                HStack {
                    Image(systemName: "sparkles")
                        .foregroundColor(.primaryBlue)
                    Text(localizationManager.localized("referral_progress_month_achieved"))
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
            Text(localizationManager.localized("referral_code_title"))
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
                    .accessibilityLabel(localizationManager.localized("referral_code_copy_accessibility"))
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel(String(format: localizationManager.localized("referral_code_accessibility"), referralCode))
                
                // Кнопки действий
                HStack(spacing: Spacing.s) {
                    Button(action: {
                        UIPasteboard.general.string = referralCode
                    }) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "doc.on.doc")
                            Text(localizationManager.localized("referral_copy_button"))
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
                    .accessibilityLabel(localizationManager.localized("referral_code_copy_accessibility"))
                    
                    Button(action: {
                        showQRCode = true
                    }) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "qrcode")
                            Text(localizationManager.localized("referral_qr_button"))
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
                    .accessibilityLabel(localizationManager.localized("referral_qr_show_accessibility"))
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
                        Text(localizationManager.localized("referral_how_it_works_title"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text(localizationManager.localized("referral_how_it_works_subtitle"))
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
            Text(localizationManager.localized("referral_methods_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                invitationMethod(
                    icon: "message.fill",
                    title: localizationManager.localized("referral_method_whatsapp"),
                    subtitle: localizationManager.localized("referral_method_whatsapp_subtitle"),
                    action: {
                        openMessenger(type: .whatsapp)
                    }
                )
                
                invitationMethod(
                    icon: "paperplane.fill",
                    title: localizationManager.localized("referral_method_telegram"),
                    subtitle: localizationManager.localized("referral_method_telegram_subtitle"),
                    action: {
                        openMessenger(type: .telegram)
                    }
                )
                
                invitationMethod(
                    icon: "network",
                    title: localizationManager.localized("referral_method_vk"),
                    subtitle: localizationManager.localized("referral_method_vk_subtitle"),
                    action: {
                        openMessenger(type: .vk)
                    }
                )
                
                invitationMethod(
                    icon: "square.and.arrow.up",
                    title: localizationManager.localized("referral_method_more"),
                    subtitle: localizationManager.localized("referral_method_more_subtitle"),
                    action: {
                        openMessenger(type: .systemShare)
                    }
                )
                
                invitationMethod(
                    icon: "link",
                    title: localizationManager.localized("referral_method_copy_link"),
                    subtitle: localizationManager.localized("referral_method_copy_link_subtitle"),
                    action: {
                        copyToClipboard(text: referralLink, type: .link)
                    }
                )
                
                invitationMethod(
                    icon: "doc.on.doc",
                    title: localizationManager.localized("referral_method_copy_code"),
                    subtitle: localizationManager.localized("referral_method_copy_code_subtitle"),
                    action: {
                        copyToClipboard(text: referralCode, type: .code)
                    }
                )
                
                invitationMethod(
                    icon: "qrcode",
                    title: localizationManager.localized("referral_method_qr"),
                    subtitle: localizationManager.localized("referral_method_qr_subtitle"),
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
                Text(localizationManager.localized("referral_rewards_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Button(action: {
                    showRewards = true
                }) {
                    Text(localizationManager.localized("referral_rewards_all"))
                        .font(.body)
                        .foregroundColor(.primaryBlue)
                }
                .accessibilityLabel(localizationManager.localized("referral_rewards_all_accessibility"))
            }
            
            HStack(spacing: Spacing.m) {
                rewardCard(
                    title: localizationManager.localized("referral_reward_1_title"),
                    reward: localizationManager.localized("referral_reward_1_amount"),
                    icon: "percent.circle.fill",
                    isUnlocked: paidReferralsCount >= 1,
                    subtitle: localizationManager.localized("referral_reward_1_subtitle")
                )
                
                rewardCard(
                    title: localizationManager.localized("referral_reward_3_title"),
                    reward: localizationManager.localized("referral_reward_3_amount"),
                    icon: "crown.fill",
                    isUnlocked: paidReferralsCount >= 3,
                    subtitle: localizationManager.localized("referral_reward_3_subtitle")
                )
                
                rewardCard(
                    title: localizationManager.localized("referral_reward_10_title"),
                    reward: localizationManager.localized("referral_reward_10_amount"),
                    icon: "star.fill",
                    isUnlocked: paidReferralsCount >= 10,
                    subtitle: localizationManager.localized("referral_reward_10_subtitle")
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
            Text(localizationManager.localized("referral_history_title"))
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
        .accessibilityLabel("\(title): \(reward), \(isUnlocked ? localizationManager.localized("referral_unlocked") : localizationManager.localized("referral_locked"))")
    }
    
    private func referralRow(referral: ReferralHistory) -> some View {
        HStack(spacing: Spacing.m) {
            Circle()
                .fill(referral.status.color)
                .frame(width: 12, height: 12)
                .accessibilityLabel("\(referral.status.localizedTitle)")
            
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
        String(format: localizationManager.localized("referral_text_template"), referralCode, referralCode)
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
                title: localizationManager.localized("referral_step1_title"),
                description: localizationManager.localized("referral_step1_desc")
            ),
            HowItWorksStep(
                number: 2,
                title: localizationManager.localized("referral_step2_title"),
                description: localizationManager.localized("referral_step2_desc")
            ),
            HowItWorksStep(
                number: 3,
                title: localizationManager.localized("referral_step3_title"),
                description: localizationManager.localized("referral_step3_desc")
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
    case completed = "completed"
    case pending = "pending"
    case cancelled = "cancelled"
    
    var color: Color {
        switch self {
        case .completed: return .successGreen
        case .pending: return .warningOrange
        case .cancelled: return .textSecondary
        }
    }
    
    var localizedTitle: String {
        let localizationManager = LocalizationManager()
        switch self {
        case .completed: return localizationManager.localized("referral_status_completed")
        case .pending: return localizationManager.localized("referral_status_pending")
        case .cancelled: return localizationManager.localized("referral_status_cancelled")
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack {
            Text(localizationManager.localized("referral_qr_view_title"))
                .font(.h2)
            
            Text(code)
                .font(.body)
        }
        .padding()
    }
}

struct RewardsView: View {
    let paidReferralsCount: Int
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack {
            Text(localizationManager.localized("referral_rewards_view_title"))
                .font(.h2)
            
            Text(String(format: localizationManager.localized("referral_rewards_view_subtitle"), paidReferralsCount))
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
