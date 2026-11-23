import SwiftUI

/// 💳 Tariffs Screen
/// Экран тарифов - выбор подписки
/// Источник дизайна: /mobile/wireframes/09_tariffs_screen.html
struct TariffsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = TariffsViewModel()
    
    // Состояние для показа Privacy Policy и Terms
    @State private var showPrivacyPolicy = false
    @State private var showTermsOfService = false
    /// Paid subscribe → choose month or year (with prices) before StoreKit / website.
    @State private var billingChooserTariff: TariffType? = nil
    /// W-pre-C: confirm before ending trial via Базовый.
    @State private var showDowngradeFromTrialConfirm = false
    @State private var showcaseVariant = TariffShowcaseExperiment.variant()
    @State private var showGatesDetail = false
    @State private var gatesFocus: TariffType = .family
    
    // Сохраняем выбранный тариф в AppStorage
    @AppStorage("selected_tariff_type") private var selectedTariffRaw: String = "family"
    var selectedTariff: TariffType {
        get {
            TariffType(rawValue: selectedTariffRaw) ?? .family
        }
        nonmutating set {
            selectedTariffRaw = newValue.rawValue
        }
    }
    
    enum TariffType: String {
        case trial = "trial"
        case free = "free"
        case personal = "personal"
        case family = "family"
        case premium = "premium"
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .trial: return localizationManager.localized("tariffs_trial")
            case .free: return localizationManager.localized("tariffs_free")
            case .personal: return localizationManager.localized("tariffs_personal")
            case .family: return localizationManager.localized("tariffs_family")
            case .premium: return localizationManager.localized("tariffs_premium")
            }
        }
        
        func period(localizationManager: LocalizationManager) -> String {
            switch self {
            case .trial: return localizationManager.localized("tariffs_trial_period")
            case .free: return localizationManager.localized("tariffs_free_period")
            case .personal, .family, .premium: return localizationManager.localized("tariffs_period_month")
            }
        }
        
        func features(localizationManager: LocalizationManager) -> [String] {
            switch self {
            case .trial: return [
                localizationManager.localized("tariffs_trial_features_1"),
                familyMemberLimitFeatureText(for: .trial, localizationManager: localizationManager),
                localizationManager.localized("tariffs_trial_features_3"),
                localizationManager.localized("tariffs_trial_features_4"),
                localizationManager.localized("tariffs_trial_features_5")
            ]
            case .free: return freeIncludedFeatures(localizationManager: localizationManager) + [
                localizationManager.localized("tariffs_antifake_free")
            ]
            case .personal:
                let quota = TariffEntitlements.antifakeMonthlyHeavyQuota(.personal)
                    ?? TariffEntitlements.personalMonthlyHeavyChecksDefault
                let hours = TariffEntitlements.locationHistoryHours(.personal)
                return [
                    localizationManager.localized("tariffs_card_personal_1"),
                    String(format: localizationManager.localized("tariffs_card_personal_quota"), quota),
                    String(format: localizationManager.localized("tariffs_card_history_hours"), hours)
                ]
            case .family: return [
                localizationManager.localized("tariffs_card_family_map"),
                localizationManager.localized("tariffs_card_family_child"),
                localizationManager.localized("tariffs_card_family_check"),
                localizationManager.localized("tariffs_family_scam_alert")
            ]
            case .premium:
                let members = TariffEntitlements.familyMemberLimit(.premium)
                let days = TariffEntitlements.locationHistoryHours(.premium) / 24
                return [
                    String(format: localizationManager.localized("tariffs_card_premium_members"), members),
                    localizationManager.localized("tariffs_card_premium_unlimited"),
                    String(format: localizationManager.localized("tariffs_card_premium_history"), days),
                    localizationManager.localized("tariffs_card_premium_trips")
                ]
            }
        }
        
        /// Accent for picker cards — same Shyam canon as main family card (`TariffAccentPalette`).
        var color: Color {
            let level: SubscriptionLevel
            switch self {
            case .trial: level = .trial
            case .free: level = .free
            case .personal: level = .personal
            case .family: level = .family
            case .premium: level = .premium
            }
            return TariffAccentPalette.color(for: level)
        }
        
        var recommended: Bool {
            return self == .family
        }

        /// Что реально открыто на Free (п.1–7). П.8 — явное «нет Antifake».
        static func freeIncludedFeatures(localizationManager: LocalizationManager) -> [String] {
            (1...7).map { localizationManager.localized("tariffs_free_features_\($0)") }
        }

        /// Явно не входит — Antifake Check и большая семья (живая карта есть на всех тарифах).
        static func freeExcludedFeatures(localizationManager: LocalizationManager) -> [String] {
            [8, 10].map { localizationManager.localized("tariffs_free_features_\($0)") }
        }

        private func freeIncludedFeatures(localizationManager: LocalizationManager) -> [String] {
            Self.freeIncludedFeatures(localizationManager: localizationManager)
        }

        private func familyMemberLimitFeatureText(for level: SubscriptionLevel, localizationManager: LocalizationManager) -> String {
            String(
                format: localizationManager.localized("tariffs_member_limit_format"),
                SubscriptionManager.familyMemberLimitStatic(for: level)
            )
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh premium light (Batch 1b, режим C)
            StormMeshBackground(variant: .premium)
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: localizationManager.localized("tariffs_title"),
                    subtitle: nil,
                    showBackButton: navigationManager.canGoBack,
                    onBack: {
                        navigationManager.goBackToPreviousScreen(reason: "Tariffs.onBack")
                    }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        planStatusBlock
                            .padding(.horizontal, Spacing.screenPadding)

                        // External activation is unavailable in the App Store binary.
                        if AppStoreBuildPolicy.allowsAlternativePayments && AppConfig.isRussianRegion {
                            if navigationManager.showSiteRenewHint {
                                siteRenewHintCard
                            }
                            activationCodeButton
                        }
                        
                        if SubscriptionManager.shared.getCurrentLevel() == .personal {
                            personalToFamilyUpgradeCard
                        }

                        // Trial A: no «Пробный» card — trial starts after onboarding via activateTrialIfNeeded.
                        // Card order is the `tariff_showcase_v1` A/B; comparison table below.
                        ForEach(paidCardOrder, id: \.self) { tariff in
                            tariffCard(tariff)
                        }

                        freePlanRow
                            .padding(.horizontal, Spacing.screenPadding)

                        honestGatesComparisonTable
                            .padding(.horizontal, Spacing.screenPadding)

                        Button {
                            HapticFeedback.impact(.light)
                            Task { @MainActor in
                                await viewModel.restorePurchases()
                            }
                        } label: {
                            HStack(spacing: Spacing.s) {
                                if viewModel.isLoading {
                                    ProgressView()
                                } else {
                                    Image(systemName: "arrow.clockwise.circle")
                                }
                                Text(localizationManager.localized("tariffs_restore_purchases"))
                            }
                            .font(.body.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(.primaryBlue)
                        .disabled(viewModel.isLoading)
                        .accessibilityIdentifier("restore_purchases_button")
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        // ✅ СКРЫТО: Флоу активации - убрано по требованию
                        // if AppConfig.isRussianRegion {
                        //     activationFlowInfoCard
                        //         .padding(.top, Spacing.s)
                        // }
                        
                        // Проценты по тарифам спрятаны с экрана. Файл TariffFeaturesGallery не удалён.
                        
                        // Spacer
                    Spacer()
                        .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .onDisappear {
            // После тарифов — синк без 1.2s троттлинга `syncSubscriptionOnMainScreenAppear`, иначе быстрый возврат на главную не подтягивает лимиты/цвет.
            Task { await SubscriptionManager.shared.syncSubscriptionAfterTariffsDismiss() }
        }
        .id("tariffs_lang_\(localizationManager.currentLanguage.rawValue)")
        // ✅ КРИТИЧНО: Загружаем продукты при открытии экрана тарифов
        .task {
            AnalyticsManager.shared.trackEvent("paywall_shown", parameters: [
                "source": "tariffs_screen",
                "variant": showcaseVariant,
                "tier": SubscriptionManager.shared.getCurrentLevel().rawValue
            ])
            AntifakeMonthlyQuota.refreshServerPersonalLimit()
            print("🔄 [TariffsScreen] Экран открыт, проверяем продукты...")
            let productsCount = await viewModel.getProductsCount()
            print("🔄 [TariffsScreen] Продуктов загружено: \(productsCount)")
            if productsCount == 0 {
                print("⚠️ [TariffsScreen] Продукты не загружены, начинаем загрузку...")
                await viewModel.loadProducts()
            } else {
                print("✅ [TariffsScreen] Продукты уже загружены")
            }
        }
        // ✅ УДАЛЕНО: Визуальные логи с экрана (оставляем только в консоли)
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН .sheet модификатор
        // Sheet создавал PaymentQRScreen дважды (через sheet И через NavigationManager)
        // Это вызывало краш! Теперь используем ТОЛЬКО NavigationManager
        .alert(localizationManager.localized("tariffs_payment_error"), isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button(localizationManager.localized("tariffs_ok")) {
                HapticFeedback.selection()
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
        .alert(localizationManager.localized("tariffs_purchase_success"), isPresented: Binding(
            get: { viewModel.isPurchaseSuccessful },
            set: { if !$0 { viewModel.isPurchaseSuccessful = false } }
        )) {
            Button(localizationManager.localized("tariffs_excellent")) {
                HapticFeedback.notification(.success)
                viewModel.isPurchaseSuccessful = false
            }
        } message: {
            Text(localizationManager.localized("tariffs_subscription_activated"))
        }
        .alert(
            localizationManager.localized("tariffs_downgrade_trial_confirm_title"),
            isPresented: $showDowngradeFromTrialConfirm
        ) {
            Button(localizationManager.localized("tariffs_downgrade_trial_confirm_cancel"), role: .cancel) {
                HapticFeedback.selection()
            }
            Button(localizationManager.localized("tariffs_downgrade_trial_confirm_continue"), role: .destructive) {
                HapticFeedback.notification(.warning)
                Task { @MainActor in
                    await SubscriptionManager.shared.downgradeToFree()
                }
            }
        } message: {
            Text(localizationManager.localized("tariffs_downgrade_trial_confirm_body"))
        }
        .sheet(isPresented: Binding(
            get: { billingChooserTariff != nil },
            set: { if !$0 { billingChooserTariff = nil } }
        )) {
            if let tariff = billingChooserTariff {
                billingPeriodChooserSheet(for: tariff)
                    .environmentObject(localizationManager)
            }
        }
    }

    /// Personal subscribers: upgrade inside the subscription group (App Store prorates level 1 → 2).
    private var personalToFamilyUpgradeCard: some View {
        let title: String = {
            if let delta = viewModel.personalToFamilyUpgradeDelta() {
                return String(format: localizationManager.localized("tariffs_upgrade_personal_to_family_cta"), delta)
            }
            return localizationManager.localized("tariffs_upgrade_personal_to_family_cta_plain")
        }()
        return VStack(alignment: .leading, spacing: Spacing.s) {
            PrimaryButton(title) {
                HapticFeedback.impact(.medium)
                AnalyticsManager.shared.trackEvent("paywall_upgrade_tap", parameters: [
                    "source": "personal_upsell",
                    "plan": TariffType.family.rawValue
                ])
                billingChooserTariff = .family
            }
            Text(localizationManager.localized("tariffs_upgrade_personal_to_family_note"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityIdentifier("tariffs_personal_to_family_upgrade")
    }

    /// Free / Personal / Family / Premium from TariffEntitlements. Four columns stay for a wide screen.
    /// On a narrow width the same rows show for one plan at a time.
    private var honestGatesComparisonTable: some View {
        let rows = gateRows
        let levels = gateLevels
        return VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("tariffs_levels_title"))
                .font(AladdinFamilyType.title3())
                .foregroundColor(.textPrimary)
            Text(String(
                format: localizationManager.localized("tariffs_levels_devices_fmt"),
                TariffEntitlements.familyMemberLimit(.free),
                TariffEntitlements.familyMemberLimit(.personal),
                TariffEntitlements.familyMemberLimit(.family),
                TariffEntitlements.familyMemberLimit(.premium)
            ))
            .font(AladdinFamilyType.caption())
            .foregroundColor(.textSecondary)
            .fixedSize(horizontal: false, vertical: true)
            Text(String(
                format: localizationManager.localized("tariffs_free_simple"),
                TariffEntitlements.familyMemberLimit(.free),
                TariffEntitlements.locationHistoryHours(.free)
            ))
            .font(AladdinFamilyType.caption())
            .foregroundColor(.textPrimary)
            Text(String(
                format: localizationManager.localized("tariffs_personal_simple"),
                TariffEntitlements.antifakeMonthlyHeavyQuota(.personal) ?? TariffEntitlements.personalMonthlyHeavyChecksDefault,
                TariffEntitlements.locationHistoryHours(.personal)
            ))
            .font(AladdinFamilyType.caption())
            .foregroundColor(.textPrimary)
            Text(String(
                format: localizationManager.localized("tariffs_family_simple"),
                TariffEntitlements.familyMemberLimit(.family),
                TariffEntitlements.locationHistoryHours(.family) / 24
            ))
            .font(AladdinFamilyType.caption())
            .foregroundColor(.textPrimary)
            Text(String(
                format: localizationManager.localized("tariffs_premium_simple"),
                TariffEntitlements.familyMemberLimit(.premium),
                TariffEntitlements.locationHistoryHours(.premium) / 24
            ))
            .font(AladdinFamilyType.caption())
            .foregroundColor(.textPrimary)

            Button {
                HapticFeedback.selection()
                showGatesDetail.toggle()
            } label: {
                HStack {
                    Text(localizationManager.localized("tariffs_compare_toggle"))
                        .font(AladdinFamilyType.body(weight: .semibold))
                    Spacer()
                    Image(systemName: showGatesDetail ? "chevron.up" : "chevron.down")
                }
                .foregroundColor(Color.secondaryGold)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("tariffs_compare_toggle")

            if showGatesDetail {
                tariffGatesFit(rows: rows, levels: levels)
            }
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .accessibilityIdentifier("tariffs_gates_table")
    }

    private var gateLevels: [SubscriptionLevel] {
        [.free, .personal, .family, .premium]
    }

    private var gateRows: [(feature: String, values: [String])] {
        let levels = gateLevels
        func mark(_ on: Bool) -> String { on ? "✓" : "—" }
        func history(_ level: SubscriptionLevel) -> String {
            let hours = TariffEntitlements.locationHistoryHours(level)
            if hours <= 48 {
                return String(format: localizationManager.localized("tariffs_history_hours"), hours)
            }
            return String(format: localizationManager.localized("tariffs_history_days"), hours / 24)
        }
        func heavy(_ level: SubscriptionLevel) -> String {
            guard TariffEntitlements.canUseAntifake(level) else { return "—" }
            if let quota = TariffEntitlements.antifakeMonthlyHeavyQuota(level) {
                return String(format: localizationManager.localized("tariffs_heavy_quota"), quota)
            }
            return localizationManager.localized("tariffs_heavy_unlimited")
        }
        func places(_ level: SubscriptionLevel) -> String {
            switch level {
            case .family, .premium, .trial: return "✓"
            case .free, .personal: return "—"
            }
        }
        return [
            (localizationManager.localized("tariffs_gates_members"), levels.map { String(TariffEntitlements.familyMemberLimit($0)) }),
            (localizationManager.localized("tariffs_gates_map_live"), levels.map { mark(TariffEntitlements.hasLiveMap($0)) }),
            (localizationManager.localized("tariffs_gates_map_last"), levels.map { _ in "✓" }),
            (localizationManager.localized("tariffs_gates_history_places"), levels.map(history)),
            (localizationManager.localized("tariffs_gates_child_basic"), levels.map { _ in "✓" }),
            (localizationManager.localized("tariffs_gates_sos"), levels.map { _ in "✓" }),
            (localizationManager.localized("tariffs_gates_check"), levels.map { mark(TariffEntitlements.canUseAntifake($0)) }),
            (localizationManager.localized("tariffs_family_scam_alert"), levels.map { mark(TariffEntitlements.ownerTierSharesFamilyPerks($0.rawValue)) }),
            (localizationManager.localized("tariffs_gates_adblock"), levels.map { _ in "✓" }),
            (localizationManager.localized("tariffs_gates_heavy"), levels.map(heavy)),
            (localizationManager.localized("tariffs_gates_trips"), levels.map { mark(TariffEntitlements.hasDrivingInsights($0)) }),
            (localizationManager.localized("tariffs_gates_share"), levels.map { mark(TariffEntitlements.ownerTierSharesFamilyPerks($0.rawValue)) }),
            (localizationManager.localized("tariffs_gates_places_more"), levels.map(places))
        ]
    }

    private func columnTitle(_ level: SubscriptionLevel) -> String {
        switch level {
        case .free: return localizationManager.localized("tariffs_free")
        case .personal: return localizationManager.localized("tariffs_personal")
        case .family: return localizationManager.localized("tariffs_family")
        case .premium: return localizationManager.localized("tariffs_premium")
        case .trial: return localizationManager.localized("tariffs_trial")
        }
    }

    @ViewBuilder
    private func tariffGatesFit(rows: [(feature: String, values: [String])], levels: [SubscriptionLevel]) -> some View {
        if #available(iOS 16.0, *) {
            ViewThatFits(in: .horizontal) {
                wideGates(rows: rows, levels: levels)
                    .frame(minWidth: 640)
                narrowGates(rows: rows, levels: levels)
            }
        } else {
            narrowGates(rows: rows, levels: levels)
        }
    }

    private func wideGates(rows: [(feature: String, values: [String])], levels: [SubscriptionLevel]) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.s) {
                Text("")
                    .frame(maxWidth: .infinity, alignment: .leading)
                ForEach(levels, id: \.self) { level in
                    Text(columnTitle(level))
                        .font(AladdinFamilyType.caption2(weight: .bold))
                        .foregroundColor(.textSecondary)
                        .frame(width: 72)
                }
            }
            ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                HStack(alignment: .top, spacing: Spacing.s) {
                    Text(row.feature)
                        .font(AladdinFamilyType.caption())
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    ForEach(Array(row.values.enumerated()), id: \.offset) { _, value in
                        Text(value)
                            .font(AladdinFamilyType.caption(weight: .bold))
                            .foregroundColor(value == "—" ? .textSecondary : .secondaryGold)
                            .frame(width: 72)
                            .multilineTextAlignment(.center)
                    }
                }
            }
        }
        .accessibilityIdentifier("tariffs_gates_wide")
    }

    private func narrowGates(rows: [(feature: String, values: [String])], levels: [SubscriptionLevel]) -> some View {
        let index = levels.firstIndex(of: level(for: gatesFocus)) ?? 0
        let choices: [TariffType] = [.free, .personal, .family, .premium]
        return VStack(alignment: .leading, spacing: Spacing.m) {
            VStack(spacing: Spacing.s) {
                HStack(spacing: Spacing.s) {
                    tariffChoiceChip(choices[0])
                    tariffChoiceChip(choices[1])
                }
                HStack(spacing: Spacing.s) {
                    tariffChoiceChip(choices[2])
                    tariffChoiceChip(choices[3])
                }
            }
            .accessibilityIdentifier("tariffs_gates_chips")
            ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                VStack(alignment: .leading, spacing: 4) {
                    Text(row.feature)
                        .font(AladdinFamilyType.body())
                        .foregroundColor(.textPrimary)
                    Text(row.values[index])
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(row.values[index] == "—" ? .textSecondary : .secondaryGold)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .accessibilityIdentifier("tariffs_gates_narrow")
    }

    private func tariffChoiceChip(_ tariff: TariffType) -> some View {
        let selected = gatesFocus == tariff
        return Button {
            gatesFocus = tariff
            HapticFeedback.selection()
        } label: {
            Text(tariff.title(localizationManager: localizationManager))
                .font(AladdinFamilyType.body(weight: .semibold))
                .foregroundColor(selected ? Color.backgroundDark : Color.secondaryGold)
                .lineLimit(1)
                .frame(maxWidth: .infinity)
                .frame(minHeight: 44)
                .background(
                    Capsule()
                        .fill(selected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.55))
                )
                .overlay(
                    Capsule()
                        .stroke(Color.secondaryGold, lineWidth: selected ? 0 : 1.5)
                )
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("tariffs_gate_chip_\(tariff.rawValue)")
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private func level(for tariff: TariffType) -> SubscriptionLevel {
        switch tariff {
        case .trial: return .trial
        case .free: return .free
        case .personal: return .personal
        case .family: return .family
        case .premium: return .premium
        }
    }

    private var paidCardOrder: [TariffType] {
        let paid = TariffShowcaseExperiment.order(for: showcaseVariant).filter {
            $0 == .personal || $0 == .family || $0 == .premium
        }
        return paid.isEmpty ? [.personal, .family, .premium] : paid
    }

    private var planStatusBlock: some View {
        let manager = SubscriptionManager.shared
        let level = manager.getCurrentLevel()
        let trialOn = level == .trial || manager.trialStatus?.isActive == true
        return VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(planStatusText(level: level, manager: manager))
                .font(AladdinFamilyType.body(weight: .semibold))
                .foregroundColor(.textPrimary)
                .fixedSize(horizontal: false, vertical: true)
            if trialOn {
                Text(localizationManager.localized("tariffs_trial_auto_note"))
                    .font(AladdinFamilyType.caption())
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityIdentifier("tariffs_plan_status")
    }

    private func planStatusText(level: SubscriptionLevel, manager: SubscriptionManager) -> String {
        func dated(_ key: String, _ date: Date?) -> String {
            guard let date else {
                return localizationManager.localized(key + "_nodate")
            }
            return String(format: localizationManager.localized(key), planDate(date))
        }
        switch level {
        case .trial:
            let end = manager.trialStatus?.endDate ?? manager.currentSubscription?.trialInfo?.endDate
            return dated("tariffs_status_trial", end)
        case .free:
            return localizationManager.localized("tariffs_status_free")
        case .personal:
            return dated("tariffs_status_personal", manager.currentSubscription?.expiresAt)
        case .family:
            return dated("tariffs_status_family", manager.currentSubscription?.expiresAt)
        case .premium:
            return dated("tariffs_status_premium", manager.currentSubscription?.expiresAt)
        }
    }

    private func planDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = localizationManager.currentLanguage == .english
            ? Locale(identifier: "en_US")
            : Locale(identifier: "ru_RU")
        formatter.setLocalizedDateFormatFromTemplate("d MMMM")
        return formatter.string(from: date)
    }

    private var freePlanRow: some View {
        Text(String(
            format: localizationManager.localized("tariffs_free_row"),
            TariffEntitlements.familyMemberLimit(.free)
        ))
        .font(AladdinFamilyType.body())
        .foregroundColor(.textPrimary)
        .fixedSize(horizontal: false, vertical: true)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .accessibilityIdentifier("tariffs_free_row")
    }

    private func cardSubtitle(_ tariff: TariffType) -> String? {
        switch tariff {
        case .personal:
            return localizationManager.localized("tariffs_card_personal_subtitle")
        case .family:
            return String(
                format: localizationManager.localized("tariffs_card_family_subtitle"),
                TariffEntitlements.familyMemberLimit(.family)
            )
        case .premium:
            return localizationManager.localized("tariffs_card_premium_subtitle")
        case .free, .trial:
            return nil
        }
    }

    private func billingPeriodChooserSheet(for tariff: TariffType) -> some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("tariffs_billing_chooser_title"))
                    .font(.system(.title3, design: .serif).weight(.bold))
                    .foregroundColor(.textPrimary)
                Text(String(
                    format: localizationManager.localized("tariffs_billing_chooser_body"),
                    tariff.title(localizationManager: localizationManager)
                ))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)

                billingPeriodRow(for: tariff, period: .monthly)
                billingPeriodRow(for: tariff, period: .yearly)

                Text(localizationManager.localized("tariffs_billing_autorenew_note"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                HapticFeedback.selection()
                billingChooserTariff = nil
            })
        }
    }

    private func billingPeriodRow(for tariff: TariffType, period: StoreManager.BillingPeriod) -> some View {
        let price = viewModel.displayedPrice(
            for: tariff,
            period: period,
            localizationManager: localizationManager
        )
        let badge = viewModel.discountBadge(for: tariff, period: period)
        let titleKey = period == .yearly ? "tariffs_period_year" : "tariffs_period_month"
        return Button {
            HapticFeedback.impact(.medium)
            billingChooserTariff = nil
            startPaidPurchase(tariff: tariff, period: period)
        } label: {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: Spacing.s) {
                        Text(localizationManager.localized(titleKey))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        if let badge {
                            Text(badge)
                                .font(.caption2.weight(.bold))
                                .foregroundColor(.backgroundDark)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.secondaryGold)
                                .clipShape(Capsule())
                        }
                    }
                    Text(price)
                        .font(.title3.weight(.bold))
                        .foregroundColor(.secondaryGold)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("tariffs_billing_\(period.rawValue)")
    }

    private func startPaidPurchase(tariff: TariffType, period: StoreManager.BillingPeriod) {
        guard let productID = StoreManager.ProductID.productID(tier: tariff.rawValue, period: period) else {
            viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
            return
        }
        let price = viewModel.displayedPrice(
            for: tariff,
            period: period,
            localizationManager: localizationManager
        )
        let periodLabel = localizationManager.localized(
            period == .yearly ? "tariffs_period_year" : "tariffs_period_month"
        )
        let websiteTariffId = period == .yearly ? "\(tariff.rawValue)_yearly" : tariff.rawValue
        let tariffObj = Tariff(
            id: productID.rawValue,
            title: tariff.title(localizationManager: localizationManager),
            price: price,
            period: periodLabel,
            features: tariff.features(localizationManager: localizationManager),
            product: nil,
            isPurchased: false
        )

        #if !APP_STORE_BUILD
        if AppConfig.useAlternativePayments {
            let referralCode = UserDefaults.standard.string(forKey: "referral_code")
            URLHelper.openWebsite(
                urlString: AppConfig.subscriptionWebsiteURL,
                tariffId: websiteTariffId,
                referralCode: referralCode
            )
            return
        }
        #endif

        Task { @MainActor in
            await viewModel.purchaseSelectedTariff(tariff: tariffObj)
        }
    }
    
    // MARK: - Helpers
    
    private func getButtonText(for tariff: TariffType) -> String {
        if tariff == .trial || tariff == .free {
            return localizationManager.localized("tariffs_trial_button")
        }
        switch tariff {
        case .personal:
            return localizationManager.localized("tariffs_choose_personal")
        case .family:
            return localizationManager.localized("tariffs_choose_family")
        case .premium:
            return localizationManager.localized("tariffs_choose_premium")
        case .trial, .free:
            return localizationManager.localized("tariffs_trial_button")
        }
    }
    
    // MARK: - Free plan bullets (on-screen)

    private var freePlanFeaturesBlock: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("tariffs_free_no_charge_note"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.textSecondary)

            Text(localizationManager.localized("tariffs_free_included_title"))
                .font(.subheadline.weight(.bold))
                .foregroundColor(.textPrimary)

            ForEach(TariffType.freeIncludedFeatures(localizationManager: localizationManager), id: \.self) { feature in
                HStack(alignment: .top, spacing: Spacing.s) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 18))
                        .foregroundColor(TariffType.free.color)
                    Text(feature)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            Text(localizationManager.localized("tariffs_free_excluded_title"))
                .font(.subheadline.weight(.bold))
                .foregroundColor(.textPrimary)
                .padding(.top, Spacing.xs)

            ForEach(TariffType.freeExcludedFeatures(localizationManager: localizationManager), id: \.self) { feature in
                HStack(alignment: .top, spacing: Spacing.s) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 18))
                        .foregroundColor(.textSecondary)
                    Text(feature)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .accessibilityIdentifier("tariffs_free_features_block")
    }

    // MARK: - Tariff Card
    
    private func tariffCard(_ tariff: TariffType) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Бейдж "Рекомендуем"
            if tariff.recommended {
                HStack {
                    Spacer()
                    Text(localizationManager.localized("tariffs_recommended"))
                        .font(.captionBold)
                        .foregroundColor(.backgroundDark)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.xs)
                        .background(
                            Capsule()
                                .fill(tariff.color)
                        )
                }
            }
            
            // Заголовок тарифа
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(tariff.title(localizationManager: localizationManager))
                        .font(AladdinFamilyType.title3())
                        .foregroundColor(tariff.color)
                    if let subtitle = cardSubtitle(tariff) {
                        Text(subtitle)
                            .font(AladdinFamilyType.caption())
                            .foregroundColor(.textSecondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    
                    HStack(alignment: .firstTextBaseline, spacing: Spacing.xs) {
                        Text(viewModel.displayedPrice(for: tariff, localizationManager: localizationManager))
                            .font(AladdinFamilyType.title2(weight: .bold))
                            .foregroundColor(.white)
                            .accessibilityIdentifier("tariff_price_\(tariff.rawValue)")
                        
                        Text(tariff.period(localizationManager: localizationManager))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
            }
            
            // Разделитель
            Rectangle()
                .fill(tariff.color.opacity(0.3))
                .frame(height: 1)

            if tariff == .free {
                freePlanFeaturesBlock
            } else {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    ForEach(tariff.features(localizationManager: localizationManager), id: \.self) { feature in
                        HStack(spacing: Spacing.s) {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 18))
                                .foregroundColor(tariff.color)

                            Text(feature)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
            }
            
            // Кнопка выбора/оплаты
            Button(action: {
                HapticFeedback.impact(.medium)
                selectedTariff = tariff
                
                if tariff == .free {
                    // W-pre-C: во время trial — confirm, не silent downgrade.
                    if SubscriptionManager.shared.trialStatus?.isActive == true
                        || SubscriptionManager.shared.getCurrentLevel() == .trial {
                        showDowngradeFromTrialConfirm = true
                    } else {
                        Task { @MainActor in
                            await SubscriptionManager.shared.downgradeToFree()
                        }
                    }
                    return
                }

                // Paid: сначала месяц или год с ценами — потом StoreKit / сайт.
                if tariff == .personal || tariff == .family || tariff == .premium {
                    billingChooserTariff = tariff
                    return
                }
                
                // ✅ Trial не должен вести на лендинг QR-оплаты.
                // Trial выдаётся через наш backend (/api/auth/register-device-trial) и обновляет JWT/лимиты.
                if tariff == .trial {
                    Task { @MainActor in
                        // trial-ux-a: уже активный trial → не registration (пустой локальный кэш после RESET не повод).
                        let wasAlreadyActive = SubscriptionManager.shared.trialStatus?.isActive == true
                        let alreadyActiveUntil = SubscriptionManager.shared.trialStatus?.endDate

                        await SubscriptionManager.shared.activateTrialIfNeeded()
                        // Подтянуть `/api/subscription/status` и разослать обновление — иначе главная может остаться на «Базовый», пока пользователь не перезапустит приложение.
                        await SubscriptionManager.shared.forceSync()
                        SubscriptionManager.shared.bumpSubscriptionDisplayEpoch()
                        let level = SubscriptionManager.shared.getCurrentLevel().rawValue
                        let trialNowActive = SubscriptionManager.shared.trialStatus?.isActive == true
                            || SubscriptionManager.shared.getCurrentLevel() == .trial

                        // Honest UX: cooldown / server fail → toast, не притворяемся что trial включился.
                        if !wasAlreadyActive && !trialNowActive {
                            let cooldown = SubscriptionManager.shared.remainingTrialActivationCooldownSeconds()
                            if cooldown > 0 {
                                let minutes = max(1, (cooldown + 59) / 60)
                                ToastManager.shared.showWarning(
                                    localizationManager.localized("tariffs_trial_cooldown_minutes", minutes)
                                )
                            } else {
                                ToastManager.shared.showError(
                                    localizationManager.localized("tariffs_trial_activate_failed")
                                )
                            }
                            return
                        }

                        NotificationCenter.default.post(
                            name: NSNotification.Name("SubscriptionUpdated"),
                            object: nil,
                            userInfo: ["level": level, "source": "tariffs_trial_selected"]
                        )
                        NotificationCenter.default.post(
                            name: NSNotification.Name("tariffPurchased"),
                            object: nil,
                            userInfo: ["tariff": "trial"]
                        )

                        if wasAlreadyActive {
                            let dateText: String = {
                                guard let until = alreadyActiveUntil ?? SubscriptionManager.shared.trialStatus?.endDate else {
                                    return "—"
                                }
                                let formatter = DateFormatter()
                                formatter.locale = localizationManager.currentLanguage == .english
                                    ? Locale(identifier: "en_US")
                                    : Locale(identifier: "ru_RU")
                                formatter.dateStyle = .medium
                                formatter.timeStyle = .none
                                return formatter.string(from: until)
                            }()
                            ToastManager.shared.showInfo(
                                localizationManager.localized("tariffs_trial_already_active_until", dateText)
                            )
                            return
                        }

                        ToastManager.shared.showSuccess(
                            localizationManager.localized(
                                "tariffs_trial_activated_slots",
                                TariffEntitlements.familyMemberLimit(.trial)
                            )
                        )

                        // Registration только после свеже выданного trial, если на сервере реально нет семьи.
                        if FamilyLocalStore.needsServerFamilyCreation() {
                            FamilyLocalStore.prepareCreateFamilyFlow()
                            navigationManager.navigateTo(.mainWithRegistration)
                        }
                    }
                    return
                }
                
                let tariffId: String = {
                    switch tariff {
                    case .trial: return "trial"
                    case .free: return "free"
                    case .personal: return "personal"
                    case .family: return "family"
                    case .premium: return "premium"
                    }
                }()
                
                let tariffObj: Tariff = {
                    // Предпочитаем живой StoreKit-тариф (id = Product ID + displayPrice).
                    if let existingTariff = viewModel.tariffs.first(where: {
                        switch tariff {
                        case .personal: return $0.id == StoreManager.ProductID.individual.rawValue
                        case .family: return $0.id == StoreManager.ProductID.family.rawValue
                        case .premium: return $0.id == StoreManager.ProductID.premium.rawValue
                        default: return $0.id == tariffId
                        }
                    }),
                       !existingTariff.id.isEmpty,
                       !existingTariff.title.isEmpty {
                        return existingTariff
                    }
                    
                    let safeTitle = tariff.title(localizationManager: localizationManager).isEmpty
                        ? "Тариф \(tariffId)" : tariff.title(localizationManager: localizationManager)
                    let safePrice = viewModel.displayedPrice(for: tariff, localizationManager: localizationManager)
                    let safePeriod = tariff.period(localizationManager: localizationManager).isEmpty
                        ? localizationManager.localized("tariffs_period_month") : tariff.period(localizationManager: localizationManager)
                    let safeFeatures = tariff.features(localizationManager: localizationManager).isEmpty
                        ? [localizationManager.localized("tariffs_free_features_1")] : tariff.features(localizationManager: localizationManager)
                    
                    return Tariff(
                        id: tariffId,
                        title: safeTitle,
                        price: safePrice,
                        period: safePeriod,
                        features: safeFeatures,
                        product: nil,
                        isPurchased: false
                    )
                }()
                
                #if !APP_STORE_BUILD
                let useAltPayments = AppConfig.useAlternativePayments
                #if DEBUG
                let regionCode = Locale.current.regionCode ?? "nil"
                print("🔍 DEBUG Payment: regionCode = '\(regionCode)', useAlternativePayments = \(useAltPayments)")
                #endif
                #endif
                
                // 🔥 Trial → платный: в РФ оплата идёт через сайт/QR (как и без trial). Иначе `purchaseTariff` сразу return и логирует «upgrade failed».
                if let currentSubscription = SubscriptionManager.shared.currentSubscription,
                   currentSubscription.level == .trial {
                    print("🔥 TRIAL UPGRADE: User in trial wants to upgrade to \(tariffObj.id)")

                    #if !APP_STORE_BUILD
                    if useAltPayments {
                        print("🇷🇺 TRIAL UPGRADE (RU): открываем сайт для QR оплаты (тот же поток, что и для не-trial)")
                        guard !tariffObj.id.isEmpty,
                              !tariffObj.title.isEmpty,
                              !tariffObj.price.isEmpty else {
                            viewModel.errorMessage = localizationManager.localized("tariffs_error_create_tariff")
                            return
                        }
                        let referralCode = UserDefaults.standard.string(forKey: "referral_code")
                        print("🌐 Открываем сайт: \(AppConfig.subscriptionWebsiteURL) с тарифом: \(tariffObj.id)")
                        URLHelper.openWebsite(
                            urlString: AppConfig.subscriptionWebsiteURL,
                            tariffId: tariffObj.id,
                            referralCode: referralCode
                        )
                        return
                    }
                    #endif

                    Task { @MainActor in
                        await viewModel.upgradeFromTrialToPaid(tariff: tariffObj)
                    }
                    return
                }

                #if !APP_STORE_BUILD
                if useAltPayments {
                    // Россия → QR оплата на сайте
                    print("🇷🇺 Российский регион: открываем сайт для QR оплаты")
                    guard !tariffObj.id.isEmpty,
                          !tariffObj.title.isEmpty,
                          !tariffObj.price.isEmpty else {
                        viewModel.errorMessage = localizationManager.localized("tariffs_error_create_tariff")
                        return
                    }
                    
                    // ⚠️ Оплата по QR перенесена на лендинг: открываем сайт напрямую
                    // ✅ Получаем referralCode из UserDefaults (если есть)
                    let referralCode = UserDefaults.standard.string(forKey: "referral_code")
                    
                    print("🌐 Открываем сайт: \(AppConfig.subscriptionWebsiteURL) с тарифом: \(tariffObj.id)")
                    URLHelper.openWebsite(
                        urlString: AppConfig.subscriptionWebsiteURL,
                        tariffId: tariffObj.id,
                        referralCode: referralCode
                    )
                    return
                }
                #endif

                #if DEBUG
                print("🍎 App Store purchase: opening StoreKit")
                #endif
                guard !tariffObj.id.isEmpty,
                      !tariffObj.title.isEmpty else {
                    viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
                    return
                }

                // Симулятор: покупка через StoreKit Configuration (.storekit в Scheme).
                let localTariffObj = tariffObj

                Task { @MainActor in
                    await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
                }
            }) {
                VStack(spacing: Spacing.xs) {
                    // ✅ Ссылки на Privacy Policy и Terms of Use (требование Apple)
                    if tariff != .trial && tariff != .free {
                        VStack(spacing: Spacing.xxs) {
                            Text(localizationManager.localized("tariffs_subscribe_agreement_text"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                            
                            HStack(spacing: Spacing.xxs) {
                                Button(action: {
                                    HapticFeedback.selection()
                                    showTermsOfService = true
                                }) {
                                    Text(localizationManager.localized("terms_of_service"))
                                        .font(.caption)
                                        .foregroundColor(.blue)
                                        .underline()
                                }
                                
                                Text(localizationManager.localized("tariffs_subscribe_agreement_and"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Button(action: {
                                    HapticFeedback.selection()
                                    showPrivacyPolicy = true
                                }) {
                                    Text(localizationManager.localized("privacy_policy"))
                                        .font(.caption)
                                        .foregroundColor(.blue)
                                        .underline()
                                }
                            }
                        }
                        .padding(.bottom, Spacing.xs)
                    }
                    
                    // Кнопка Subscribe
                    Text(getButtonText(for: tariff))
                        .font(.buttonText)
                        .foregroundColor(Color.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .frame(height: Size.buttonHeight)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.large)
                }
            }
            .sheet(isPresented: $showPrivacyPolicy) {
                PrivacyPolicyScreen()
            }
            .sheet(isPresented: $showTermsOfService) {
                TermsOfServiceScreen()
            }
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(
                    selectedTariff == tariff ? tariff.color : Color.clear,
                    lineWidth: selectedTariff == tariff ? 2 : 0
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Activation Flow Info
    
    private var activationFlowInfoCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🔐 " + localizationManager.localized("activation_code_instruction_title"))
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Text(localizationManager.localized("tariffs_website_info"))
                .font(.footnote)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(.horizontal, Spacing.screenPadding)
    }

    // MARK: - Site renew hint (push 7/3 → Tariffs)

    private var siteRenewHintCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("site_sub_renew_hint_title"))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                Spacer()
                Button {
                    navigationManager.showSiteRenewHint = false
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.textSecondary)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(localizationManager.localized("common_close"))
            }
            Text(localizationManager.localized("site_sub_renew_hint_body"))
                .font(.subheadline)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityIdentifier("site_sub_renew_hint_card")
    }

    // MARK: - Activation Code Button
    
    @ViewBuilder
    private var activationCodeButton: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            navigationManager.navigateTo(.activationCode)
        }) {
            HStack(spacing: Spacing.m) {
                Image(systemName: "key.fill")
                    .font(.system(size: 18))
                    .foregroundColor(Color.backgroundDark)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("tariffs_activation_code"))
                        .font(.body)
                        .foregroundColor(Color.backgroundDark)
                    
                    Text(localizationManager.localized("activation_code_subtitle"))
                        .font(.caption)
                        .foregroundColor(Color.backgroundDark.opacity(0.75))
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(Color.backgroundDark.opacity(0.75))
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.secondaryGold)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, 20) // Используем фиксированное значение вместо Spacing.screenPadding для безопасности
    }
    
}

// MARK: - Preview

#if DEBUG
struct TariffsScreen_Previews: PreviewProvider {
    static var previews: some View {
        TariffsScreen()
    }
}
#endif
