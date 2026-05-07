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
        
        var price: String {
            switch self {
            case .trial: return "0 ₽"
            case .free: return "0 ₽"
            case .personal: return "100 ₽"
            case .family: return "290 ₽"
            case .premium: return "490 ₽"
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
                localizationManager.localized("tariffs_trial_features_2"),
                localizationManager.localized("tariffs_trial_features_3"),
                localizationManager.localized("tariffs_trial_features_4"),
                localizationManager.localized("tariffs_trial_features_5")
            ]
            case .free: return [
                localizationManager.localized("tariffs_free_features_1"),
                localizationManager.localized("tariffs_free_features_2"),
                localizationManager.localized("tariffs_free_features_3"),
                localizationManager.localized("tariffs_free_features_4"),
                localizationManager.localized("tariffs_free_features_5"),
                localizationManager.localized("tariffs_free_features_6"),
                localizationManager.localized("tariffs_free_features_7"),
                localizationManager.localized("tariffs_free_features_8"),
                localizationManager.localized("tariffs_free_features_9"),
                localizationManager.localized("tariffs_free_features_10")
            ]
            case .personal: return [
                localizationManager.localized("tariffs_personal_features_1"),
                familyMemberLimitFeatureText(for: .personal, localizationManager: localizationManager),
                localizationManager.localized("tariffs_personal_features_3"),
                localizationManager.localized("tariffs_personal_features_4"),
                localizationManager.localized("tariffs_personal_features_5"),
                localizationManager.localized("tariffs_personal_features_6")
            ]
            case .family: return [
                localizationManager.localized("tariffs_family_features_1"),
                familyMemberLimitFeatureText(for: .family, localizationManager: localizationManager),
                localizationManager.localized("tariffs_family_features_3"),
                localizationManager.localized("tariffs_family_features_4"),
                localizationManager.localized("tariffs_family_features_5"),
                localizationManager.localized("tariffs_family_features_6")
            ]
            case .premium: return [
                localizationManager.localized("tariffs_premium_features_1"),
                familyMemberLimitFeatureText(for: .premium, localizationManager: localizationManager),
                localizationManager.localized("tariffs_premium_features_3"),
                localizationManager.localized("tariffs_premium_features_4"),
                localizationManager.localized("tariffs_premium_features_5"),
                localizationManager.localized("tariffs_premium_features_6"),
                localizationManager.localized("tariffs_premium_features_7"),
                localizationManager.localized("tariffs_premium_features_8")
            ]
            }
        }
        
        var color: Color {
            switch self {
            case .trial: return Color(hex: "#10B981")  // Зеленый для trial
            case .free: return .textSecondary
            case .personal: return .primaryBlue
            case .family: return .secondaryGold
            case .premium: return Color(hex: "#A855F7")
            }
        }
        
        var recommended: Bool {
            return self == .family
        }

        private func familyMemberLimitFeatureText(for level: SubscriptionLevel, localizationManager: LocalizationManager) -> String {
            let limit = SubscriptionManager.familyMemberLimitStatic(for: level)
            if localizationManager.currentLanguage == .russian {
                return "До \(limit) участников в семейном доступе"
            }
            return "Up to \(limit) family members in shared access"
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: localizationManager.localized("tariffs_title"),
                    subtitle: localizationManager.localized("tariffs_subtitle"),
                    showBackButton: navigationManager.canGoBack,
                    onBack: {
                        guard navigationManager.canGoBack else { return }
                        navigationManager.goBack(reason: "Tariffs.onBack")
                    }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // ✅ Кнопка активации кода подписки (сверху) - ТОЛЬКО для России
                        if AppConfig.isRussianRegion {
                            activationCodeButton
                        }
                        
                        // Карточки тарифов
                        tariffCard(.trial)
                        tariffCard(.free)
                        tariffCard(.personal)
                        tariffCard(.family)
                        tariffCard(.premium)
                        
                        // ✅ СКРЫТО: Флоу активации - убрано по требованию
                        // if AppConfig.isRussianRegion {
                        //     activationFlowInfoCard
                        //         .padding(.top, Spacing.s)
                        // }
                        
                        // Уровень защиты по тарифам
                        TariffFeaturesGallery()
                            .padding(.top, Spacing.s)
                        
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
            #if targetEnvironment(simulator)
            print("🔄 [TariffsScreen] Симулятор — без повторной проверки IAP (StoreManager не дергает StoreKit)")
            #else
            print("🔄 [TariffsScreen] Экран открыт, проверяем продукты...")
            let productsCount = await viewModel.getProductsCount()
            print("🔄 [TariffsScreen] Продуктов загружено: \(productsCount)")
            if productsCount == 0 {
                print("⚠️ [TariffsScreen] Продукты не загружены, начинаем загрузку...")
                await viewModel.loadProducts()
            } else {
                print("✅ [TariffsScreen] Продукты уже загружены")
            }
            #endif
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
                viewModel.isPurchaseSuccessful = false
                // Можно обновить UI
            }
        } message: {
            Text(localizationManager.localized("tariffs_subscription_activated"))
        }
    }
    
    // MARK: - Helpers
    
    private func getButtonText(for tariff: TariffType) -> String {
        if tariff == .trial || tariff == .free {
            return localizationManager.localized("tariffs_trial_button")
        } else if selectedTariff == tariff {
            return localizationManager.localized("tariffs_selected")
        } else {
            // ✅ ВАРИАНТ Б: Всегда показываем "Subscribe" / "Оформить подписку"
            // Логика проверки региона находится в обработчике кнопки (строки 313-345)
            // Для России → открывается сайт (QR оплата)
            // Для остальных стран → открывается IAP (App Store)
            return localizationManager.localized("tariffs_purchase_button")
        }
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
                        .font(.h2)
                        .foregroundColor(tariff.color)
                    
                    HStack(alignment: .firstTextBaseline, spacing: Spacing.xs) {
                        Text(tariff.price)
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(.white)
                        
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
            
            // Список функций
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
            
            // Кнопка выбора/оплаты
            Button(action: {
                HapticFeedback.impact(.medium)
                selectedTariff = tariff
                
                if tariff == .free {
                    Task { @MainActor in
                        await SubscriptionManager.shared.downgradeToFree()
                    }
                    return
                }
                
                // ✅ Trial не должен вести на лендинг QR-оплаты.
                // Trial выдаётся через наш backend (/api/auth/register-device-trial) и обновляет JWT/лимиты.
                if tariff == .trial {
                    Task { @MainActor in
                        await SubscriptionManager.shared.activateTrialIfNeeded()
                        // Подтянуть `/api/subscription/status` и разослать обновление — иначе главная может остаться на «Базовый», пока пользователь не перезапустит приложение.
                        await SubscriptionManager.shared.forceSync()
                        let level = SubscriptionManager.shared.getCurrentLevel().rawValue
                        NotificationCenter.default.post(
                            name: NSNotification.Name("SubscriptionUpdated"),
                            object: nil,
                            userInfo: ["level": level, "source": "tariffs_trial_selected"]
                        )
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
                    if let existingTariff = viewModel.tariffs.first(where: { $0.id == tariffId }),
                       !existingTariff.id.isEmpty,
                       !existingTariff.title.isEmpty {
                        return existingTariff
                    }
                    
                    let safeTitle = tariff.title(localizationManager: localizationManager).isEmpty
                        ? "Тариф \(tariffId)" : tariff.title(localizationManager: localizationManager)
                    let safePrice = tariff.price.isEmpty ? "0 ₽" : tariff.price
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
                
                // ✅ ОТЛАДКА: Проверяем регион
                let regionCode = Locale.current.regionCode ?? "nil"
                let useAltPayments = AppConfig.useAlternativePayments
                print("🔍 DEBUG Payment: regionCode = '\(regionCode)', useAlternativePayments = \(useAltPayments)")
                
                // 🔥 Trial → платный: в РФ оплата идёт через сайт/QR (как и без trial). Иначе `purchaseTariff` сразу return и логирует «upgrade failed».
                if let currentSubscription = SubscriptionManager.shared.currentSubscription,
                   currentSubscription.level == .trial {
                    print("🔥 TRIAL UPGRADE: User in trial wants to upgrade to \(tariffObj.id)")

                    if AppConfig.useAlternativePayments {
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

                    Task { @MainActor in
                        await viewModel.upgradeFromTrialToPaid(tariff: tariffObj)
                    }
                    return
                }

                if AppConfig.useAlternativePayments {
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
                } else {
                    // Не Россия → IAP (App Store)
                    print("🌍 Не российский регион: открываем IAP")
                    guard !tariffObj.id.isEmpty,
                          !tariffObj.title.isEmpty else {
                        viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
                        return
                    }
                    
                    #if targetEnvironment(simulator)
                    viewModel.errorMessage = localizationManager.localized("store_error_simulator_not_supported")
                    #else
                    let localTariffObj = tariffObj
                    
                    Task { @MainActor in
                        await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
                    }
                    #endif
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
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: Size.buttonHeight)
                        .background(
                            selectedTariff == tariff ?
                            LinearGradient(
                                colors: [Color.successGreen, Color(hex: "#16A34A")],
                                startPoint: .leading,
                                endPoint: .trailing
                            ) :
                            LinearGradient(
                                colors: [tariff.color, tariff.color.opacity(0.8)],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
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
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(
                            selectedTariff == tariff ?
                            tariff.color :
                            Color.white.opacity(0.1),
                            lineWidth: selectedTariff == tariff ? 2 : 1
                        )
                )
        )
        .cardShadow()
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
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
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
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.2), radius: 4, x: 0, y: 2)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("tariffs_activation_code"))
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Text(localizationManager.localized("activation_code_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.white.opacity(0.85))
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(hex: "#FAD961"),
                                Color(hex: "#F76B1C")
                            ],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(LinearGradient.aladdinGold, lineWidth: 2)
            )
            .shadow(color: Color(hex: "#F76B1C").opacity(0.45), radius: 16, x: 0, y: 8)
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
