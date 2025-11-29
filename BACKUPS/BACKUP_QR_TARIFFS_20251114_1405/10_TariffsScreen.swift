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
    
    @State private var showComparisonModal: Bool = false
    @State private var showThreatsProtection: Bool = false
    @State private var expandedThreatCategory: ThreatProtectionCategory? = nil
#if DEBUG
    @State private var showNavigationLogs: Bool = false
#endif
    
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
                localizationManager.localized("tariffs_free_features_3")
            ]
            case .personal: return [
                localizationManager.localized("tariffs_personal_features_1"),
                localizationManager.localized("tariffs_personal_features_2"),
                localizationManager.localized("tariffs_personal_features_3"),
                localizationManager.localized("tariffs_personal_features_4")
            ]
            case .family: return [
                localizationManager.localized("tariffs_family_features_1"),
                localizationManager.localized("tariffs_family_features_2"),
                localizationManager.localized("tariffs_family_features_3"),
                localizationManager.localized("tariffs_family_features_4"),
                localizationManager.localized("tariffs_family_features_5")
            ]
            case .premium: return [
                localizationManager.localized("tariffs_premium_features_1"),
                localizationManager.localized("tariffs_premium_features_2"),
                localizationManager.localized("tariffs_premium_features_3"),
                localizationManager.localized("tariffs_premium_features_4"),
                localizationManager.localized("tariffs_premium_features_5")
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
                        // Карточки тарифов
                        tariffCard(.free)
                        tariffCard(.personal)
                        tariffCard(.family)
                        tariffCard(.premium)
                        
                        // AI Защита от угроз
                        aiProtectionCard
                            .padding(.top, Spacing.s)
                        
                        // Сравнение тарифов
                        comparisonButton
                        
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
        .sheet(isPresented: $showComparisonModal) {
            TariffComparisonModal(isPresented: $showComparisonModal)
                .environmentObject(localizationManager)
        }
#if DEBUG
        .overlay(alignment: .topTrailing) {
            VStack(alignment: .trailing, spacing: 8) {
                Button(action: {
                    withAnimation(.spring(response: 0.25, dampingFraction: 0.85)) {
                        showNavigationLogs.toggle()
                    }
                }) {
                    Text(showNavigationLogs ? "Скрыть логи" : "Показать логи")
                        .font(.caption2.weight(.semibold))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.black.opacity(0.45))
                        .foregroundColor(.white)
                        .clipShape(Capsule())
                }
                
                if showNavigationLogs {
                    let latestLogs = Array(navigationManager.debugLogs.suffix(200))
                    NavigationDebugOverlay(title: "Tariffs Navigation",
                                           logEntries: latestLogs)
                        .transition(.move(edge: .trailing).combined(with: .opacity))
                        .shadow(radius: 8)
                }
            }
            .padding(.trailing, 16)
            .padding(.top, 16)
        }
#endif
    }
    
    // MARK: - Helpers
    
    private func getButtonText(for tariff: TariffType) -> String {
        if tariff == .free {
            return localizationManager.localized("tariffs_free_button")
        } else if selectedTariff == tariff {
            return localizationManager.localized("tariffs_selected")
        } else {
            // ✅ ВСЕГДА используем QR оплату (IAP в России недоступен)
            return localizationManager.localized("tariffs_pay_qr")
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
                    
                    navigationManager.selectedTariffForPayment = tariffObj
                    
                    guard navigationManager.selectedTariffForPayment != nil else {
                        viewModel.errorMessage = localizationManager.localized("tariffs_error_select_tariff")
                        return
                    }
                    
                    navigationManager.navigateTo(.paymentQR)
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
    
    // MARK: - AI Protection Card
    
    private var aiProtectionCard: some View {
        ThreatProtectionCard(
            icon: "🤖",
            title: localizationManager.localized("tariffs_ai_protection"),
            subtitle: localizationManager.localized("tariffs_ai_protection_desc"),
            isExpanded: $showThreatsProtection,
            expandedCategory: $expandedThreatCategory
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Comparison Button
    
    private var comparisonButton: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            showComparisonModal = true
        }) {
            HStack(spacing: Spacing.m) {
                Text("📊")
                    .font(.system(size: 24))
                
                Text(localizationManager.localized("tariffs_compare_all"))
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
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

// MARK: - Tariff Comparison Modal

struct TariffComparisonModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    Text(localizationManager.localized("tariffs_comparison_title"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .padding(.top, Spacing.m)
                    
                    // Краткая таблица
                    comparisonTable
                    
                    // Рекомендации
                    recommendations
                    
                    Spacer()
                        .frame(height: Spacing.xl)
                }
                .padding(Spacing.cardPadding)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("tariffs_comparison_done")) {
                        isPresented = false
                    }
                }
            }
        }
    }
    
    // MARK: - Comparison Table
    
    private var comparisonTable: some View {
        VStack(spacing: Spacing.s) {
            // Заголовок таблицы
            tableHeader
            
            // Строки таблицы - первая часть
            comparisonRow(title: localizationManager.localized("tariffs_comparison_price"), values: ["0₽", "290₽", "490₽", "990₽"])
            comparisonRow(title: localizationManager.localized("tariffs_comparison_devices"), values: ["1", "4", "6", "10"])
            comparisonRow(title: localizationManager.localized("tariffs_comparison_protection"), values: ["20+%", "50+%", "80+%", "100%"], highlightIndex: 3)
            comparisonRow(title: localizationManager.localized("tariffs_comparison_vpn"), values: [
                localizationManager.localized("tariffs_comparison_vpn_limited"),
                localizationManager.localized("tariffs_comparison_vpn_unlimited"),
                localizationManager.localized("tariffs_comparison_vpn_unlimited"),
                localizationManager.localized("tariffs_comparison_vpn_unlimited")
            ])
            
            // Разделитель
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Функции - вторая часть
            Group {
                comparisonRow(title: localizationManager.localized("tariffs_comparison_child_protection"), values: ["✅", "✅", "✅", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_elderly_protection"), values: ["❌", "❌", "✅", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_ai_analysis"), values: ["❌", "✅", "✅", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_voice_control"), values: ["❌", "❌", "✅", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_gamification"), values: ["❌", "❌", "✅", "✅"])
            }
            
            Group {
                comparisonRow(title: localizationManager.localized("tariffs_comparison_anonymity"), values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_aes256"), values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_deepfake"), values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_leak_monitoring"), values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: localizationManager.localized("tariffs_comparison_free_month"), values: ["⭐", "✅", "✅", "✅"])
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
    }
    
    private var tableHeader: some View {
        HStack(spacing: Spacing.xs) {
            Text(localizationManager.localized("tariffs_comparison_criterion"))
                .font(.bodyBold)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(localizationManager.localized("tariffs_comparison_column_free"))
                .font(.captionBold)
                .foregroundColor(TariffColumn.free.color)
                .frame(maxWidth: .infinity)
            
            Text(localizationManager.localized("tariffs_comparison_column_basic"))
                .font(.captionBold)
                .foregroundColor(TariffColumn.basic.color)
                .frame(maxWidth: .infinity)
            
            Text(localizationManager.localized("tariffs_comparison_column_family"))
                .font(.captionBold)
                .foregroundColor(TariffColumn.family.color)
                .frame(maxWidth: .infinity)
            
            Text(localizationManager.localized("tariffs_comparison_column_premium"))
                .font(.captionBold)
                .foregroundColor(TariffColumn.premium.color)
                .frame(maxWidth: .infinity)
        }
        .padding(Spacing.s)
        .background(Color.primaryBlue.opacity(0.1))
    }
    
    private func comparisonRow(title: String, values: [String], highlightIndex: Int? = nil) -> some View {
        HStack(spacing: Spacing.xs) {
            Text(title)
                .font(.body)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(values[0])
                .font(.caption)
                .foregroundColor(highlightIndex == 0 ? .successGreen : .textPrimary)
                .frame(maxWidth: .infinity)
            
            Text(values[1])
                .font(.caption)
                .foregroundColor(highlightIndex == 1 ? .successGreen : .textPrimary)
                .frame(maxWidth: .infinity)
            
            Text(values[2])
                .font(.caption)
                .foregroundColor(highlightIndex == 2 ? .successGreen : .textPrimary)
                .frame(maxWidth: .infinity)
            
            Text(values[3])
                .font(.caption)
                .foregroundColor(highlightIndex == 3 ? .successGreen : .textPrimary)
                .frame(maxWidth: .infinity)
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Recommendations
    
    private var recommendations: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("tariffs_recommendations"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            recommendationCard(
                title: localizationManager.localized("tariffs_recommendation_freemium"),
                subtitle: localizationManager.localized("tariffs_recommendation_freemium_subtitle"),
                text: localizationManager.localized("tariffs_recommendation_freemium_text")
            )
            
            recommendationCard(
                title: localizationManager.localized("tariffs_recommendation_basic"),
                subtitle: localizationManager.localized("tariffs_recommendation_basic_subtitle"),
                text: localizationManager.localized("tariffs_recommendation_basic_text")
            )
            
            recommendationCard(
                title: localizationManager.localized("tariffs_recommendation_family"),
                subtitle: localizationManager.localized("tariffs_recommendation_family_subtitle"),
                text: localizationManager.localized("tariffs_recommendation_family_text"),
                highlight: true
            )
            
            recommendationCard(
                title: localizationManager.localized("tariffs_recommendation_premium"),
                subtitle: localizationManager.localized("tariffs_recommendation_premium_subtitle"),
                text: localizationManager.localized("tariffs_recommendation_premium_text")
            )
        }
    }
    
    private func recommendationCard(title: String, subtitle: String, text: String, highlight: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                if highlight {
                    Text("⭐")
                        .font(.caption)
                }
            }
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            Text(text)
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(highlight ? Color.secondaryGold.opacity(0.2) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(highlight ? Color.secondaryGold : Color.clear, lineWidth: 2)
                )
        )
    }
    
    enum TariffColumn: CaseIterable {
        case free, basic, family, premium
        
        var shortName: String {
            switch self {
            case .free: return "FREE"
            case .basic: return "BASIC"
            case .family: return "FAMILY"
            case .premium: return "PREMIUM"
            }
        }
        
        var color: Color {
            switch self {
            case .free: return .textSecondary
            case .basic: return .primaryBlue
            case .family: return .secondaryGold
            case .premium: return Color(hex: "#A855F7")
            }
        }
    }
}

