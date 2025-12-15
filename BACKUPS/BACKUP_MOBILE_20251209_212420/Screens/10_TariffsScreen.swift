import SwiftUI

/// 💳 Tariffs Screen
/// Экран тарифов - выбор подписки
/// Источник дизайна: /mobile/wireframes/09_tariffs_screen.html
struct TariffsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = TariffsViewModel()
    
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
        case free = "free"
        case personal = "personal"
        case family = "family"
        case premium = "premium"
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .free: return localizationManager.localized("tariffs_free")
            case .personal: return localizationManager.localized("tariffs_personal")
            case .family: return localizationManager.localized("tariffs_family")
            case .premium: return localizationManager.localized("tariffs_premium")
            }
        }
        
        var price: String {
            switch self {
            case .free: return "0 ₽"
            case .personal: return "290 ₽"
            case .family: return "490 ₽"
            case .premium: return "990 ₽"
            }
        }
        
        func period(localizationManager: LocalizationManager) -> String {
            switch self {
            case .free: return localizationManager.localized("tariffs_free_period")
            case .personal, .family, .premium: return localizationManager.localized("tariffs_period_month")
            }
        }
        
        func features(localizationManager: LocalizationManager) -> [String] {
            switch self {
            case .free: return [
                localizationManager.localized("tariffs_free_features_1"),
                localizationManager.localized("tariffs_free_features_2"),
                localizationManager.localized("tariffs_free_features_3"),
                localizationManager.localized("tariffs_free_features_4"),
                localizationManager.localized("tariffs_free_features_5"),
                localizationManager.localized("tariffs_free_features_6")
            ]
            case .personal: return [
                localizationManager.localized("tariffs_personal_features_1"),
                localizationManager.localized("tariffs_personal_features_2"),
                localizationManager.localized("tariffs_personal_features_3"),
                localizationManager.localized("tariffs_personal_features_4"),
                localizationManager.localized("tariffs_personal_features_5"),
                localizationManager.localized("tariffs_personal_features_6")
            ]
            case .family: return [
                localizationManager.localized("tariffs_family_features_1"),
                localizationManager.localized("tariffs_family_features_2"),
                localizationManager.localized("tariffs_family_features_3"),
                localizationManager.localized("tariffs_family_features_4"),
                localizationManager.localized("tariffs_family_features_5"),
                localizationManager.localized("tariffs_family_features_6")
            ]
            case .premium: return [
                localizationManager.localized("tariffs_premium_features_1"),
                localizationManager.localized("tariffs_premium_features_2"),
                localizationManager.localized("tariffs_premium_features_3"),
                localizationManager.localized("tariffs_premium_features_4"),
                localizationManager.localized("tariffs_premium_features_5"),
                localizationManager.localized("tariffs_premium_features_6"),
                localizationManager.localized("tariffs_premium_features_7")
            ]
            }
        }
        
        var color: Color {
            switch self {
            case .free: return .textSecondary
            case .personal: return .primaryBlue
            case .family: return .secondaryGold
            case .premium: return Color(hex: "#A855F7")
            }
        }
        
        var recommended: Bool {
            return self == .family
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
                        // ✅ Кнопка активации кода подписки (сверху)
                        activationCodeButton
                        
                        // Карточки тарифов
                        tariffCard(.free)
                        tariffCard(.personal)
                        tariffCard(.family)
                        tariffCard(.premium)
                        
                        // Флоу активации
                        activationFlowInfoCard
                            .padding(.top, Spacing.s)
                        
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
        .id("tariffs_lang_\(localizationManager.currentLanguage.rawValue)")
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
        if tariff == .free {
            return localizationManager.localized("tariffs_free_button")
        } else if selectedTariff == tariff {
            return localizationManager.localized("tariffs_selected")
        } else {
            // ✅ Оплата вынесена на лендинг, поэтому предлагаем переход на сайт
            return localizationManager.localized("tariffs_website_button")
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
                    return
                }
                
                let tariffId: String = {
                    switch tariff {
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
                
                if AppConfig.useAlternativePayments {
                    guard !tariffObj.id.isEmpty,
                          !tariffObj.title.isEmpty,
                          !tariffObj.price.isEmpty else {
                        viewModel.errorMessage = localizationManager.localized("tariffs_error_create_tariff")
                        return
                    }
                    
                    // ⚠️ Оплата по QR перенесена на лендинг: открываем сайт напрямую
                    // ✅ Получаем referralCode из UserDefaults (если есть)
                    let referralCode = UserDefaults.standard.string(forKey: "referral_code")
                    
                    URLHelper.openWebsite(
                        urlString: AppConfig.subscriptionWebsiteURL,
                        tariffId: tariffObj.id,
                        referralCode: referralCode
                    )
                } else {
                    guard !tariffObj.id.isEmpty,
                          !tariffObj.title.isEmpty else {
                        viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
                        return
                    }
                    
                    #if targetEnvironment(simulator)
                    viewModel.errorMessage = "In-App Purchase недоступен в симуляторе.\n\nStoreKit может вызвать краш при попытке покупки.\n\nДля тестирования оплаты используйте реальное устройство с настроенным тестовым Apple ID."
                    #else
                    let localTariffObj = tariffObj
                    
                    Task { @MainActor in
                        await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
                    }
                    #endif
                }
            }) {
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
                    Text("Активировать код подписки")
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Text("Введите код, полученный после оплаты")
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
