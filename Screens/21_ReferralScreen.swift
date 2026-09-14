import SwiftUI
import Foundation
import CoreImage.CIFilterBuiltins

/// 🎁 Referral Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Реферальная программа с системой бонусов
/// Источник дизайна: /mobile/wireframes/13_referral_screen.html
struct ReferralScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var referralCode: String = ""
    @State private var referralURL: String?
    @State private var referralsCount: Int = 0
    @State private var paidReferralsCount: Int = 0
    @State private var conversionRate: Double = 0
    @State private var rewardItems: [ReferralRewardItem] = []
    @State private var rewardTotalConverted: Int = 0
    @State private var showShareSheet: Bool = false
    @State private var showQRCode: Bool = false
    @State private var showRewards: Bool = false
    @State private var showHowItWorks: Bool = false
    @State private var referralHistoryItems: [ReferralHistory] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isCaregiverAccess: Bool = true
    @State private var aTier: String = "none"
    @State private var aQualified: Int = 0
    @State private var aProtectionDays: Int = 0
    @State private var aProgressCurrent: Int = 0
    @State private var aProgressNext: Int? = 1
    @State private var aProgressRemaining: Int = 1
    @State private var aLedger: [FamilyReferralALedgerItem] = []
    @State private var showLevelUp: Bool = false
    @State private var lastSeenTier: String = UserDefaults.standard.string(forKey: "referral_a_last_tier") ?? "none"
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh premium light (Batch 4)
            StormMeshBackground(variant: .premium)
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("referral_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: Spacing.l) {
                        if !isCaregiverAccess {
                            caregiverOnlyCard
                        } else {
                        if let errorMessage = errorMessage {
                            Text(errorMessage)
                                .font(.caption)
                                .foregroundColor(.red)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal, Spacing.m)
                                .padding(.vertical, Spacing.xs)
                                .background(Color.red.opacity(0.1))
                                .cornerRadius(CornerRadius.medium)
                        }
                        
                        // Главный баннер
                        mainBanner

                        familyInviteTierCard
                        
                        // Ваша статистика
                        yourStats
                        
                        // Реферальный код
                        referralCodeSection
                        
                        // Как это работает
                        howItWorksCard

                        referralFAQCard
                        
                        // Способы приглашения
                        invitationMethods
                        
                        // Награды
                        rewardsSection

                        familyInviteLedgerCard
                        
                        // История рефералов
                        referralsHistory
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("referral_background"))
            }
            
            if isLoading {
                Color.black.opacity(0.15)
                    .ignoresSafeArea()
                    .allowsHitTesting(false)
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle())
            }
        }
        .navigationBarHidden(true)
        .id("referral_screen_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(activityItems: [referralText])
        }
        .sheet(isPresented: $showQRCode) {
            QRCodeView(code: referralCode)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showRewards) {
            RewardsView(rewardItems: rewardItems, totalConverted: max(rewardTotalConverted, paidReferralsCount, aQualified))
                .environmentObject(localizationManager)
        }
        .overlay {
            if showLevelUp {
                levelUpOverlay
            }
        }
        .task {
            resolveCaregiverAccess()
            FamilyReferralAnalytics.track(.screenOpen)
            if isCaregiverAccess {
                loadReferralData()
            }
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("referral_a_title"),
            subtitle: localizationManager.localized("referral_a_subtitle"),
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
            
            Text(localizationManager.localized("referral_a_invite_title"))
                .font(.h1)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
            
            Text(localizationManager.localized("referral_a_invite_desc"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .accessibilityLabel(localizationManager.localized("referral_a_invite_desc"))
            
            // Кнопка пригласить
            Button(action: {
                FamilyReferralAnalytics.track(.inviteTap, parameters: ["method": "banner"])
                AnalyticsManager.shared.trackReferralShare(method: "banner")
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
            .buttonStyle(PlainButtonStyle())
            .accessibilityLabel(localizationManager.localized("referral_invite_button"))
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    // MARK: - Family Invite Pro (A)
    
    private var caregiverOnlyCard: some View {
        VStack(spacing: Spacing.m) {
            Text("👨‍👩‍👧")
                .font(.system(size: 40))
            Text(localizationManager.localized("referral_a_caregiver_only_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            Text(localizationManager.localized("referral_a_caregiver_only_desc"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .onAppear {
            FamilyReferralAnalytics.track(.caregiverBlocked)
        }
    }

    private var familyInviteTierCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("referral_a_tier_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)

            HStack {
                Text(tierDisplayName(aTier))
                    .font(.bodyBold)
                    .foregroundColor(.primaryBlue)
                Spacer()
                if aProtectionDays > 0 {
                    Text(String(format: localizationManager.localized("referral_a_tier_days"), aProtectionDays))
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
            }

            Text(String(format: localizationManager.localized("referral_a_qualified_count"), aQualified))
                .font(.caption)
                .foregroundColor(.textSecondary)

            if let next = aProgressNext {
                ProgressView(value: Double(aProgressCurrent), total: Double(max(next, 1)))
                    .tint(.primaryBlue)
                Text(String(format: localizationManager.localized("referral_a_progress_remaining"), aProgressRemaining))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                Text(localizationManager.localized("referral_a_progress_max"))
                    .font(.caption)
                    .foregroundColor(.successGreen)
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private var familyInviteLedgerCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("referral_a_ledger_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)

            if aLedger.isEmpty {
                Text(localizationManager.localized("referral_a_ledger_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                ForEach(aLedger.prefix(8)) { item in
                    HStack(alignment: .top, spacing: Spacing.s) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(ledgerReasonLabel(item.reason))
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            Text(item.createdAt ?? "")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        VStack(alignment: .trailing, spacing: 2) {
                            if item.referrerProtectionDays > 0 {
                                Text("+\(item.referrerProtectionDays) \(localizationManager.localized("referral_a_days_short"))")
                                    .font(.caption)
                                    .foregroundColor(.successGreen)
                            }
                            Text("−\(item.friendDiscountPercent)%")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .padding(.vertical, Spacing.xxs)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private var referralFAQCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("referral_a_faq_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)

            faqRow(q: "referral_a_faq_q1", a: "referral_a_faq_a1")
            faqRow(q: "referral_a_faq_q2", a: "referral_a_faq_a2")
            faqRow(q: "referral_a_faq_q3", a: "referral_a_faq_a3")
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func faqRow(q: String, a: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xxs) {
            Text(localizationManager.localized(q))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized(a))
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
    }

    private var levelUpOverlay: some View {
        ZStack {
            Color.black.opacity(0.35).ignoresSafeArea()
            VStack(spacing: Spacing.m) {
                Text("✨")
                    .font(.system(size: 56))
                    .scaleEffect(showLevelUp ? 1.15 : 0.8)
                    .animation(.spring(response: 0.45, dampingFraction: 0.55), value: showLevelUp)
                Text(localizationManager.localized("referral_a_level_up_title"))
                    .font(.h2)
                    .foregroundColor(.white)
                Text(tierDisplayName(aTier))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                Button(localizationManager.localized("referral_qr_done")) {
                    showLevelUp = false
                }
                .foregroundColor(.white)
                .padding(.top, Spacing.s)
            }
            .padding(Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.primaryBlue.opacity(0.95))
            )
        }
        .onTapGesture { showLevelUp = false }
    }

    private func resolveCaregiverAccess() {
        let roster = UnifiedFamilyRoster.load()
        FamilyLocalStore.alignCurrentUserRoleFromPersistedRoster(roster)
        FamilyAccessPolicy.syncCurrentUserRoleDefaults(members: roster)
        let ok = FamilyAccessPolicy.isCaregiver(members: roster)
        isCaregiverAccess = ok
        if !ok {
            FamilyReferralAnalytics.track(.caregiverBlocked)
        }
    }

    private func tierDisplayName(_ raw: String) -> String {
        switch raw.lowercased() {
        case "bronze": return localizationManager.localized("referral_a_tier_bronze")
        case "silver": return localizationManager.localized("referral_a_tier_silver")
        case "gold": return localizationManager.localized("referral_a_tier_gold")
        case "platinum": return localizationManager.localized("referral_a_tier_platinum")
        default: return localizationManager.localized("referral_a_tier_none")
        }
    }

    private func ledgerReasonLabel(_ reason: String) -> String {
        switch reason {
        case "qualify_paid": return localizationManager.localized("referral_a_reason_paid")
        case "qualify_active_days": return localizationManager.localized("referral_a_reason_active")
        default: return reason
        }
    }

    private func applyAOverview(_ overview: FamilyReferralAOverviewResponse) {
        aQualified = overview.qualifiedFamilies
        aTier = overview.tier
        aProtectionDays = overview.referrerProtectionDaysCurrentTier
        aProgressCurrent = overview.progress.current
        aProgressNext = overview.progress.nextTierAt
        aProgressRemaining = overview.progress.remaining
        aLedger = overview.ledger
        paidReferralsCount = max(paidReferralsCount, overview.qualifiedFamilies)

        let prev = lastSeenTier
        if overview.tier != "none", overview.tier != prev,
           ["bronze", "silver", "gold", "platinum"].contains(overview.tier.lowercased()) {
            let order = ["none", "bronze", "silver", "gold", "platinum"]
            let pi = order.firstIndex(of: prev.lowercased()) ?? 0
            let ni = order.firstIndex(of: overview.tier.lowercased()) ?? 0
            if ni > pi {
                showLevelUp = true
                FamilyReferralAnalytics.track(.levelUp, parameters: ["tier": overview.tier])
                if overview.referrerProtectionDaysCurrentTier > 0 {
                    FamilyReferralInviteRouter.notifyGrantIfNeeded(
                        days: overview.referrerProtectionDaysCurrentTier,
                        tier: overview.tier
                    )
                }
            }
        }
        lastSeenTier = overview.tier
        UserDefaults.standard.set(overview.tier, forKey: "referral_a_last_tier")
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
                    value: "\(max(paidReferralsCount, aQualified))",
                    color: .successGreen
                )
                
                statCard(
                    icon: "tag.fill",
                    title: localizationManager.localized("referral_stats_friend_discount"),
                    value: "−20%",
                    color: .warningOrange
                )
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
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
                        HapticFeedback.selection()
                    }) {
                        Image(systemName: "doc.on.doc")
                            .font(.system(size: 16))
                            .foregroundColor(.primaryBlue)
                    }
                    .buttonStyle(PlainButtonStyle())
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
                        HapticFeedback.selection()
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
                    .buttonStyle(PlainButtonStyle())
                    .accessibilityLabel(localizationManager.localized("referral_code_copy_accessibility"))
                    
                    Button(action: {
                        showQRCode = true
                        HapticFeedback.selection()
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
                    .buttonStyle(PlainButtonStyle())
                    .accessibilityLabel(localizationManager.localized("referral_qr_show_accessibility"))
                }
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
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
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
        )
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
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    // MARK: - Rewards Section (Family Invite Pro A — days, not escalating %)
    
    private var rewardsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("referral_a_rewards_title"))
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

            Text(localizationManager.localized("referral_a_rewards_caption"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: Spacing.s) {
                familyARewardRow(
                    title: localizationManager.localized("referral_a_reward_friend_title"),
                    value: localizationManager.localized("referral_a_reward_friend_value"),
                    subtitle: localizationManager.localized("referral_a_reward_friend_subtitle"),
                    icon: "tag.fill",
                    unlocked: true
                )
                familyARewardRow(
                    title: localizationManager.localized("referral_a_reward_bronze_title"),
                    value: localizationManager.localized("referral_a_reward_bronze_value"),
                    subtitle: localizationManager.localized("referral_a_reward_bronze_subtitle"),
                    icon: "shield.fill",
                    unlocked: familyInviteQualifiedCount >= 1
                )
                familyARewardRow(
                    title: localizationManager.localized("referral_a_reward_silver_title"),
                    value: localizationManager.localized("referral_a_reward_silver_value"),
                    subtitle: localizationManager.localized("referral_a_reward_silver_subtitle"),
                    icon: "shield.lefthalf.filled",
                    unlocked: familyInviteQualifiedCount >= 3
                )
                familyARewardRow(
                    title: localizationManager.localized("referral_a_reward_gold_title"),
                    value: localizationManager.localized("referral_a_reward_gold_value"),
                    subtitle: localizationManager.localized("referral_a_reward_gold_subtitle"),
                    icon: "crown.fill",
                    unlocked: familyInviteQualifiedCount >= 5
                )
                familyARewardRow(
                    title: localizationManager.localized("referral_a_reward_platinum_title"),
                    value: localizationManager.localized("referral_a_reward_platinum_value"),
                    subtitle: localizationManager.localized("referral_a_reward_platinum_subtitle"),
                    icon: "star.fill",
                    unlocked: familyInviteQualifiedCount >= 10
                )
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }

    private func familyARewardRow(
        title: String,
        value: String,
        subtitle: String,
        icon: String,
        unlocked: Bool
    ) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(unlocked ? .successGreen : .textTertiary)
                .frame(width: 28)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }

            Spacer()

            Text(value)
                .font(.bodyBold)
                .foregroundColor(unlocked ? .successGreen : .textSecondary)

            Text(unlocked
                 ? localizationManager.localized("referral_unlocked")
                 : localizationManager.localized("referral_locked"))
                .font(.caption2)
                .foregroundColor(unlocked ? .successGreen : .textTertiary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(unlocked ? Color.successGreen.opacity(0.08) : Color.backgroundMedium.opacity(0.25))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value), \(unlocked ? localizationManager.localized("referral_unlocked") : localizationManager.localized("referral_locked"))")
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
                if referralHistoryItems.isEmpty {
                    Text(localizationManager.localized("referral_invite_friends_desc"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(Spacing.m)
                        .frame(maxWidth: .infinity)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.backgroundMedium.opacity(0.3))
                        )
                } else {
                    ForEach(referralHistoryItems) { referral in
                        referralRow(referral: referral)
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
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
        .buttonStyle(PlainButtonStyle())
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
                .accessibilityLabel(referral.status.localizedTitle(localizationManager))
            
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
                .foregroundColor(referral.status == .completed ? .successGreen : .textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: localizationManager.localized("referral_history_accessibility"),
                referral.name,
                referral.status.localizedTitle(localizationManager)
            ) + ", \(referral.reward)"
        )
    }
    
    // MARK: - Computed Properties
    
    private var referralText: String {
        let code = referralCode.isEmpty ? "ALADDIN" : referralCode
        return String(format: localizationManager.localized("referral_text_template"), code, code)
    }
    
    private var referralLink: String {
        if let referralURL = referralURL, !referralURL.isEmpty {
            return referralURL
        }
        let code = referralCode.isEmpty ? "ALADDIN" : referralCode
        return "https://aladdin-ai.ru/invite/\(code)"
    }

    private var familyInviteQualifiedCount: Int {
        max(paidReferralsCount, aQualified)
    }
    
    // MARK: - Helper Functions
    
    private func loadReferralData() {
        isLoading = true
        errorMessage = nil
        let service = APIService.shared
        let group = DispatchGroup()
        
        group.enter()
        service.getReferralOverview { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let overview):
                    referralCode = overview.referralCode
                    referralURL = overview.referralURL
                    if referralsCount == 0 {
                        referralsCount = overview.invitationsCount
                    }
                    // ✅ Сохранить referralCode в UserDefaults для использования при оплате
                    if !overview.referralCode.isEmpty {
                        UserDefaults.standard.set(overview.referralCode, forKey: "referral_code")
                        print("✅ ReferralScreen: Сохранен referralCode: \(overview.referralCode)")
                    }
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
                group.leave()
            }
        }
        
        group.enter()
        service.getReferralStats { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    referralsCount = stats.totalReferrals
                    paidReferralsCount = stats.convertedReferrals
                    conversionRate = stats.conversionRate
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
                group.leave()
            }
        }
        
        group.enter()
        service.getReferralHistory { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let historyItems):
                    updateReferralHistory(with: historyItems)
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    referralHistoryItems = []
                }
                group.leave()
            }
        }
        
        group.enter()
        service.getReferralRewards { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let rewardsResponse):
                    rewardItems = rewardsResponse.rewards
                    rewardTotalConverted = rewardsResponse.totalConverted
                    if rewardsResponse.totalConverted > paidReferralsCount {
                        paidReferralsCount = rewardsResponse.totalConverted
                    }
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    rewardItems = []
                }
                group.leave()
            }
        }

        group.enter()
        let familyId = (UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        service.getFamilyReferralAOverview(familyId: familyId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let overview):
                    applyAOverview(overview)
                case .failure:
                    // A API may not be deployed yet — keep legacy stats.
                    break
                }
                group.leave()
            }
        }
        
        group.notify(queue: .main) {
            isLoading = false
            FamilyReferralInviteRouter.attachPendingIfNeeded()
        }
    }
    
    private func updateReferralHistory(with items: [ReferralHistoryItem]) {
        guard !items.isEmpty else {
            referralHistoryItems = []
            return
        }
        let sorted = items.sorted { $0.createdAt > $1.createdAt }
        referralHistoryItems = sorted.enumerated().map { index, item in
            let friendLabel = String(format: localizationManager.localized("referral_history_item_name"), index + 1)
            let displayDate = formattedDate(from: item.createdAt)
            let reward = rewardLabel(for: item)
            return ReferralHistory(id: item.id, name: friendLabel, date: displayDate, reward: reward, status: ReferralStatus.from(item.status))
        }
    }
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 89: Статические форматтеры для предотвращения рекурсии
    private static let isoFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()
    
    private static let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        // Используем статический locale вместо Locale.current (может читать из UserDefaults)
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    private func formattedDate(from isoString: String) -> String {
        if let date = Self.isoFormatter.date(from: isoString) {
            // ✅ Используем статический formatter вместо создания нового каждый раз
            return Self.dateFormatter.string(from: date)
        }
        return isoString
    }
    
    private func rewardLabel(for item: ReferralHistoryItem) -> String {
        if let reward = item.rewardAmount { return String(format: "%.0f₽", reward) }
        if let discount = item.discountApplied { return String(format: "%.0f₽", discount) }
        return localizationManager.localized("referral_status_pending")
    }
    
    private func openMessenger(type: MessengerType) {
        let message = referralText.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        let encodedLink = referralLink.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        
        var urlString: String?
        var fallbackToWeb: Bool = false
        
        switch type {
        case .whatsapp:
            // WhatsApp iOS app: whatsapp://send?text=...
            // Fallback to web: https://wa.me/?text=...
            if let whatsappURL = URL(string: "whatsapp://send?text=\(message)"),
               UIApplication.shared.canOpenURL(whatsappURL) {
                urlString = "whatsapp://send?text=\(message)"
            } else {
                // Fallback to WhatsApp Web
                urlString = "https://wa.me/?text=\(message)"
                fallbackToWeb = true
            }
        case .telegram:
            // Telegram iOS app: tg://msg?text=...
            // Fallback to web: https://t.me/share/url?url=...&text=...
            if let telegramURL = URL(string: "tg://msg?text=\(message)"),
               UIApplication.shared.canOpenURL(telegramURL) {
                urlString = "tg://msg?text=\(message)"
            } else {
                // Fallback to Telegram Web Share
                urlString = "https://t.me/share/url?url=\(encodedLink)&text=\(message)"
                fallbackToWeb = true
            }
        case .vk:
            // VK iOS app: vk://share?url=...
            // Fallback to web: https://vk.com/share.php?url=...
            if let vkURL = URL(string: "vk://share?url=\(encodedLink)"),
               UIApplication.shared.canOpenURL(vkURL) {
                urlString = "vk://share?url=\(encodedLink)"
            } else {
                // Fallback to VK Web Share
                urlString = "https://vk.com/share.php?url=\(encodedLink)&title=\(message)"
                fallbackToWeb = true
            }
        case .systemShare:
            showShareSheet = true
            return
        }
        
        if let urlString = urlString, let url = URL(string: urlString) {
            if fallbackToWeb || UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url, options: [:]) { success in
                    if !success {
                        // Если не удалось открыть, используем системный Share Sheet
                        DispatchQueue.main.async {
                            self.showShareSheet = true
                        }
                    }
                }
            } else {
                // Fallback to system share
                showShareSheet = true
            }
        } else {
            // Fallback to system share
            showShareSheet = true
        }
    }
    
    private func copyToClipboard(text: String, type: ClipboardType) {
        UIPasteboard.general.string = text
        HapticFeedback.selection()
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

struct ReferralHistory: Identifiable {
    let id: String
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
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .completed: return localizationManager.localized("referral_status_completed")
        case .pending: return localizationManager.localized("referral_status_pending")
        case .cancelled: return localizationManager.localized("referral_status_cancelled")
        }
    }
    
    static func from(_ remoteStatus: String) -> ReferralStatus {
        switch remoteStatus.lowercased() {
        case "completed", "converted":
            return .completed
        case "cancelled", "expired":
            return .cancelled
        default:
            return .pending
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

struct QRCodeView: View {
    let code: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @State private var qrImage: UIImage?
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text(localizationManager.localized("referral_qr_view_title"))
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .padding(.top, Spacing.m)
                
                if let qrImage = qrImage {
                    Image(uiImage: qrImage)
                        .resizable()
                        .interpolation(.none)
                        .scaledToFit()
                        .frame(width: 250, height: 250)
                        .background(Color.white)
                        .padding()
                } else {
                    VStack(spacing: Spacing.m) {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle())
                        
                        Text(localizationManager.localized("referral_qr_generating"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .frame(width: 250, height: 250)
                }
                
                if !code.isEmpty {
                    Text(code)
                        .font(.body.monospaced())
                        .foregroundColor(.textPrimary)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(CornerRadius.medium)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("referral_qr_done")) {
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            generateQRCode()
        }
    }
    
    private func generateQRCode() {
        guard !code.isEmpty else { return }
        
        let qrString = code.contains("http") ? code : "https://aladdin-ai.ru/invite/\(code)"
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        
        filter.message = Data(qrString.utf8)
        
        if let outputImage = filter.outputImage {
            let transform = CGAffineTransform(scaleX: 10, y: 10)
            let scaledImage = outputImage.transformed(by: transform)
            
            if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
                qrImage = UIImage(cgImage: cgImage)
            }
        }
    }
}

struct RewardsView: View {
    let rewardItems: [ReferralRewardItem]
    let totalConverted: Int
    @EnvironmentObject private var localizationManager: LocalizationManager

    private var qualified: Int { max(0, totalConverted) }

    private var rows: [(title: String, value: String, subtitle: String, unlocked: Bool)] {
        [
            (
                localizationManager.localized("referral_a_reward_friend_title"),
                localizationManager.localized("referral_a_reward_friend_value"),
                localizationManager.localized("referral_a_reward_friend_subtitle"),
                true
            ),
            (
                localizationManager.localized("referral_a_reward_bronze_title"),
                localizationManager.localized("referral_a_reward_bronze_value"),
                localizationManager.localized("referral_a_reward_bronze_subtitle"),
                qualified >= 1
            ),
            (
                localizationManager.localized("referral_a_reward_silver_title"),
                localizationManager.localized("referral_a_reward_silver_value"),
                localizationManager.localized("referral_a_reward_silver_subtitle"),
                qualified >= 3
            ),
            (
                localizationManager.localized("referral_a_reward_gold_title"),
                localizationManager.localized("referral_a_reward_gold_value"),
                localizationManager.localized("referral_a_reward_gold_subtitle"),
                qualified >= 5
            ),
            (
                localizationManager.localized("referral_a_reward_platinum_title"),
                localizationManager.localized("referral_a_reward_platinum_value"),
                localizationManager.localized("referral_a_reward_platinum_subtitle"),
                qualified >= 10
            ),
        ]
    }
    
    var body: some View {
        ScrollView(.vertical, showsIndicators: true) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("referral_a_rewards_title"))
                    .font(.h2)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                Text(String(format: localizationManager.localized("referral_a_rewards_view_subtitle"), qualified))
                    .font(.body)
                    .foregroundColor(.textSecondary)

                Text(localizationManager.localized("referral_a_rewards_caption"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)

                ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text(row.title)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            Text(row.subtitle)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        Text(row.value)
                            .font(.bodyBold)
                            .foregroundColor(row.unlocked ? .successGreen : .textSecondary)
                        Text(row.unlocked
                             ? localizationManager.localized("referral_unlocked")
                             : localizationManager.localized("referral_locked"))
                            .font(.caption2)
                            .foregroundColor(row.unlocked ? .successGreen : .textTertiary)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(row.unlocked ? Color.successGreen.opacity(0.08) : Color.backgroundMedium.opacity(0.25))
                    )
                }
            }
            .padding(Spacing.screenPadding)
        }
    }
}

struct ReferralScreen_Previews: PreviewProvider {
    static var previews: some View {
        ReferralScreen()
    }
}
