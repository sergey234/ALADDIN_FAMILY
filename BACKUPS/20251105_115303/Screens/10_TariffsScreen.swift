import SwiftUI

/// 💳 Tariffs Screen
/// Экран тарифов - выбор подписки
/// Источник дизайна: /mobile/wireframes/09_tariffs_screen.html
struct TariffsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
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
    @State private var expandedThreatCategory: ThreatCategory? = nil
    // ✅ УДАЛЕНО: Визуальные логи (только консоль)
    
    // ✅ УДАЛЕНО: showPaymentQRScreen и selectedTariffForPayment - больше не нужны
    // Используем только NavigationManager.selectedTariffForPayment
    
    // MARK: - Helper Methods
    
    // ✅ Логи только в консоль (без визуального отображения)
    private func addLog(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let logMessage = "[\(timestamp)] \(message)"
        print(logMessage)
    }
    
    enum TariffType: String {
        case free = "free"
        case personal = "personal"
        case family = "family"
        case premium = "premium"
        
        var title: String {
            switch self {
            case .free: return "БАЗОВЫЙ"
            case .personal: return "ЛИЧНЫЙ"
            case .family: return "СЕМЕЙНЫЙ"
            case .premium: return "ПРЕМИУМ"
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
        
        var period: String {
            switch self {
            case .free: return "Бесплатно"
            case .personal, .family, .premium: return "в месяц"
            }
        }
        
        var features: [String] {
            switch self {
            case .free: return ["VPN базовый", "1 устройство", "Реклама"]
            case .personal: return ["VPN Pro", "3 устройства", "Без рекламы", "AI помощник"]
            case .family: return [
                "VPN Ultra", "10 устройств",
                "Родительский контроль", "AI + Аналитика",
                "Приоритетная поддержка"
            ]
            case .premium: return [
                "VPN Max", "Неограниченно",
                "Всё из Семейного", "Консьерж-сервис",
                "Премиум поддержка 24/7"
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
                    title: "ТАРИФЫ",
                    subtitle: "Выберите подходящий план",
                    showBackButton: true,
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
        // ✅ УДАЛЕНО: Визуальные логи с экрана (оставляем только в консоли)
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН .sheet модификатор
        // Sheet создавал PaymentQRScreen дважды (через sheet И через NavigationManager)
        // Это вызывало краш! Теперь используем ТОЛЬКО NavigationManager
        .alert("Ошибка оплаты", isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
        .alert("Покупка успешна!", isPresented: Binding(
            get: { viewModel.isPurchaseSuccessful },
            set: { if !$0 { viewModel.isPurchaseSuccessful = false } }
        )) {
            Button("Отлично!") {
                viewModel.isPurchaseSuccessful = false
                // Можно обновить UI
            }
        } message: {
            Text("Подписка успешно активирована!")
        }
        .sheet(isPresented: $showComparisonModal) {
            TariffComparisonModal(isPresented: $showComparisonModal)
        }
    }
    
    // MARK: - Helpers
    
    private func getButtonText(for tariff: TariffType) -> String {
        if tariff == .free {
            return "БЕСПЛАТНО"
        } else if selectedTariff == tariff {
            return "✓ ВЫБРАН"
        } else {
            // ✅ ВСЕГДА используем QR оплату (IAP в России недоступен)
            return "ОПЛАТИТЬ ЧЕРЕЗ QR"
        }
    }
    
    // MARK: - Tariff Card
    
    private func tariffCard(_ tariff: TariffType) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Бейдж "Рекомендуем"
            if tariff.recommended {
                HStack {
                    Spacer()
                    Text("⭐ РЕКОМЕНДУЕМ")
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
                    Text(tariff.title)
                        .font(.h2)
                        .foregroundColor(tariff.color)
                    
                    HStack(alignment: .firstTextBaseline, spacing: Spacing.xs) {
                        Text(tariff.price)
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(.white)
                        
                        Text(tariff.period)
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
                ForEach(tariff.features, id: \.self) { feature in
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
                    // 🚨 КРИТИЧЕСКИЙ ЛОГ: Должен появиться ПЕРВЫМ - ПРЯМО в консоль
                    print("==========================================")
                    print("🚨🚨🚨 КНОПКА НАЖАТА! НАЧАЛО ДЕЙСТВИЯ! 🚨🚨🚨")
                    print("==========================================")
                    print("🔍 Thread в button action: \(Thread.isMainThread ? "Main" : "Background")")
                    print("🔍 Время: \(Date())")
                    
                    // ✅ Логирование (только в консоль)
                    addLog("🚨🚨🚨 КНОПКА НАЖАТА! НАЧАЛО ДЕЙСТВИЯ!")
                    addLog("Thread: \(Thread.isMainThread ? "Main" : "Background")")
                    
                    print("✅ addLog() вызван успешно")
                
                // 🔍 Логирование начала процесса
                addLog("========== НАЧАЛО ВЫБОРА ТАРИФА ==========")
                addLog("Выбран тариф: \(tariff.title)")
                addLog("Регион: \(Locale.current.regionCode ?? "unknown")")
                addLog("useAlternativePayments: \(AppConfig.useAlternativePayments)")
                
                print("🔍 ========== НАЧАЛО ВЫБОРА ТАРИФА ==========")
                
                print("🔍 Выбран тариф: \(tariff.title)")
                print("🔍 TariffType: \(tariff)")
                print("🔍 Регион: \(Locale.current.regionCode ?? "unknown")")
                print("🔍 Locale: \(Locale.current.identifier)")
                print("🔍 AppConfig.useAlternativePayments: \(AppConfig.useAlternativePayments)")
                print("🔍 viewModel.tariffs.count: \(viewModel.tariffs.count)")
                print("🔍 viewModel.isLoading: \(viewModel.isLoading)")
                
                // Безопасная обработка выбора тарифа
                HapticFeedback.impact(.medium)
                selectedTariff = tariff
                
                // Если тариф бесплатный
                if tariff == .free {
                    addLog("✅ Активирован бесплатный тариф")
                    print("✅ Активирован бесплатный тариф")
                    return
                }
                
                // Создаем Tariff объект для передачи в PaymentQRScreen или IAP
                let tariffId: String = {
                    switch tariff {
                    case .free: return "free"
                    case .personal: return "personal"
                    case .family: return "family"
                    case .premium: return "premium"
                    }
                }()
                
                print("🔍 DEBUG: Создание tariffObj для tariffId: \(tariffId)")
                
                // Безопасно создаём тариф с полной проверкой
                let tariffObj: Tariff = {
                    // Сначала пытаемся найти существующий тариф из StoreKit
                    if !viewModel.tariffs.isEmpty,
                       let existingTariff = viewModel.tariffs.first(where: { $0.id == tariffId }) {
                        print("✅ Используем тариф из StoreKit: \(existingTariff.id)")
                        
                        // Проверяем валидность тарифа из StoreKit
                        if !existingTariff.id.isEmpty && !existingTariff.title.isEmpty {
                            return existingTariff
                        } else {
                            print("⚠️ Тариф из StoreKit невалиден, создаём новый")
                            // Продолжаем создание нового тарифа
                        }
                    }
                    
                    // Создаём новый тариф для QR-оплаты (или если StoreKit тариф невалиден)
                    print("ℹ️ Создан новый тариф для оплаты: \(tariffId)")
                    
                    // Проверяем обязательные поля перед созданием
                    let safeTitle = tariff.title.isEmpty ? "Тариф \(tariffId)" : tariff.title
                    let safePrice = tariff.price.isEmpty ? "0 ₽" : tariff.price
                    let safePeriod = tariff.period.isEmpty ? "в месяц" : tariff.period
                    let safeFeatures = tariff.features.isEmpty ? ["Базовая защита"] : tariff.features
                    
                    print("🔍 DEBUG: Создаём Tariff с параметрами:")
                    print("   - id: \(tariffId)")
                    print("   - title: \(safeTitle)")
                    print("   - price: \(safePrice)")
                    print("   - period: \(safePeriod)")
                    print("   - features: \(safeFeatures.count) шт.")
                    
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
                
                // Проверяем регион и запускаем оплату
                if AppConfig.useAlternativePayments {
                    // 🇷🇺 Россия → QR оплата
                    print("🚨 ========== ВЫБОР ТАРИФА ДЛЯ QR ОПЛАТЫ ==========")
                    print("🔍 Thread: \(Thread.isMainThread ? "Main" : "Background")")
                    print("🇷🇺 Регион: Россия → Открываем QR-оплату для тарифа: \(tariff.title)")
                    print("🔍 DEBUG: tariffObj проверка:")
                    print("   - id: '\(tariffObj.id)'")
                    print("   - title: '\(tariffObj.title)'")
                    print("   - price: '\(tariffObj.price)'")
                    print("   - period: '\(tariffObj.period)'")
                    print("   - features.count: \(tariffObj.features.count)")
                    
                    // КРИТИЧЕСКАЯ ПРОВЕРКА: убедимся, что tariffObj валиден
                    guard !tariffObj.id.isEmpty, !tariffObj.title.isEmpty, !tariffObj.price.isEmpty else {
                        print("❌ КРИТИЧЕСКАЯ ОШИБКА: tariffObj создан неправильно!")
                        print("   id.isEmpty: \(tariffObj.id.isEmpty)")
                        print("   title.isEmpty: \(tariffObj.title.isEmpty)")
                        print("   price.isEmpty: \(tariffObj.price.isEmpty)")
                        viewModel.errorMessage = "Ошибка создания тарифа. Попробуйте ещё раз."
                        return
                    }
                    
                    print("✅ tariffObj валиден, открываем PaymentQRScreen")
                    print("🔍 Проверяем AppConfig перед открытием...")
                    print("   - AppConfig.apiBaseURL: \(AppConfig.apiBaseURL)")
                    print("   - AppConfig.apiBaseURL.isEmpty: \(AppConfig.apiBaseURL.isEmpty)")
                    
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убрали ЛОКАЛЬНЫЙ selectedTariffForPayment
                    // Используем ТОЛЬКО NavigationManager.selectedTariffForPayment
                    // Это предотвращает двойное создание PaymentQRScreen (sheet + NavigationManager)
                    addLog("🔍 ШАГ 1: Передаем тариф в NavigationManager...")
                    print("🔍 Передаем тариф в NavigationManager...")
                    
                    // Устанавливаем тариф в NavigationManager ПЕРЕД вызовом navigateTo
                    addLog("🔍 ШАГ 2: Устанавливаем navigationManager.selectedTariffForPayment...")
                    navigationManager.selectedTariffForPayment = tariffObj
                    
                    // Дополнительная проверка после установки
                    guard navigationManager.selectedTariffForPayment != nil else {
                        addLog("❌ КРИТИЧЕСКАЯ ОШИБКА: selectedTariffForPayment остался nil!")
                        print("❌ КРИТИЧЕСКАЯ ОШИБКА: navigationManager.selectedTariffForPayment остался nil!")
                        viewModel.errorMessage = "Не удалось выбрать тариф. Попробуйте ещё раз."
                        return
                    }
                    
                    addLog("✅ ШАГ 3: selectedTariffForPayment установлен: \(navigationManager.selectedTariffForPayment!.id)")
                    print("✅ NavigationManager.selectedTariffForPayment установлен: \(navigationManager.selectedTariffForPayment!.id)")
                    
                    addLog("🔍 ШАГ 4: Открываем PaymentQRScreen через NavigationManager...")
                    print("🔍 Открываем PaymentQRScreen через NavigationManager.navigateTo...")
                    
                    // ✅ Открываем PaymentQRScreen ТОЛЬКО через NavigationManager
                    // Убрали sheet - он конфликтовал и создавал PaymentQRScreen дважды!
                    addLog("🔍 ШАГ 5: ВЫЗОВ navigationManager.navigateTo(.paymentQR)...")
                    navigationManager.navigateTo(.paymentQR)
                    
                    addLog("✅ ШАГ 6: NavigationManager.navigateTo(.paymentQR) ВЫПОЛНЕН!")
                    addLog("========== ВЫБОР ТАРИФА ЗАВЕРШЕН ==========")
                    print("✅ NavigationManager.navigateTo(.paymentQR) вызван")
                    print("🚨 ========== ВЫБОР ТАРИФА ЗАВЕРШЕН ==========")
                } else {
                    // ⚠️ ЭТОТ КОД НЕ ДОЛЖЕН ВЫПОЛНЯТЬСЯ - используется только QR!
                    // Если мы здесь, значит что-то не так с конфигурацией
                    addLog("⚠️ ВНИМАНИЕ: Должна быть QR оплата, но регион = \(Locale.current.regionCode ?? "unknown")")
                    print("⚠️ ВНИМАНИЕ: Код IAP не должен выполняться - используется только QR оплата!")
                    print("🌍 Регион: \(Locale.current.regionCode ?? "unknown") → ОШИБКА: должен быть QR!")
                    
                    // КРИТИЧЕСКАЯ ПРОВЕРКА перед IAP
                    addLog("🔍 Проверяем tariffObj перед IAP...")
                    addLog("   - id: '\(tariffObj.id)'")
                    addLog("   - title: '\(tariffObj.title)'")
                    
                    guard !tariffObj.id.isEmpty, !tariffObj.title.isEmpty else {
                        addLog("❌ ОШИБКА: tariffObj невалиден для IAP!")
                        viewModel.errorMessage = "Ошибка создания тарифа для покупки."
                        return
                    }
                    
                    addLog("✅ tariffObj валиден, запускаем IAP...")
                    
                    // ✅ КРИТИЧЕСКАЯ ЗАЩИТА: В симуляторе StoreKit НЕ РАБОТАЕТ И КРАШИТ - БЛОКИРУЕМ ВСЕГДА!
                    addLog("🔍 Проверяем доступность StoreKit...")
                    
                    #if targetEnvironment(simulator)
                    addLog("❌ СТОП: Симулятор обнаружен!")
                    print("❌ КРИТИЧЕСКОЕ: Симулятор - StoreKit вызывает краш при вызове purchase()")
                    print("❌ Блокируем все вызовы StoreKit в симуляторе")
                    viewModel.errorMessage = "In-App Purchase недоступен в симуляторе.\n\nStoreKit может вызвать краш при попытке покупки.\n\nДля тестирования оплаты используйте реальное устройство с настроенным тестовым Apple ID."
                    // ✅ ВАЖНО: ВОЗВРАЩАЕМСЯ СРАЗУ - НЕ ДОПУСКАЕМ ВЫЗОВ StoreKit
                    #else
                    // ✅ ОТЛОЖЕННЫЙ ВЫЗОВ: Используем Task для безопасного асинхронного выполнения
                    // ПРИМЕЧАНИЕ: Этот код выполняется ТОЛЬКО на реальном устройстве (не в симуляторе)
                    addLog("🔍 Планируем IAP покупку на реальном устройстве...")
                    print("🔍 DEBUG: Планируем IAP покупку через Task...")
                    
                    // Сохраняем tariffObj локально для использования в Task
                    let localTariffObj = tariffObj
                    
                    addLog("🔍 Создаем Task для IAP...")
                    
                    Task { @MainActor in
                        addLog("🔍 Запуск IAP покупки в Task...")
                        print("🔍 DEBUG: Запуск IAP покупки...")
                        
                        // ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА внутри Task
                        addLog("   - tariffObj.id: '\(localTariffObj.id)'")
                        addLog("   - tariffObj.title: '\(localTariffObj.title)'")
                        addLog("   - viewModel.tariffs.count: \(viewModel.tariffs.count)")
                        
                        addLog("   - Вызываем purchaseSelectedTariff...")
                        await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
                        addLog("✅ IAP покупка завершена")
                        print("🔍 DEBUG: IAP покупка завершена")
                    }
                    addLog("✅ IAP покупка запланирована")
                    #endif
                }
                
                addLog("========== КОНЕЦ ВЫБОРА ТАРИФА ==========")
                print("🔍 ========== КОНЕЦ ВЫБОРА ТАРИФА ==========")
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
        VStack(spacing: 0) {
            // Header - always visible
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    showThreatsProtection.toggle()
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.m) {
                    Text("🛡️")
                        .font(.system(size: 32))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text("AI ЗАЩИТА ОТ 100+ КИБЕРУГРОЗ")
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text("Комплексная защита для всей вашей семьи")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.leading)
                    }
                    
                    Spacer()
                    
                    Image(systemName: showThreatsProtection ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            // Content - expandable
            if showThreatsProtection {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    // Categories list
                    ForEach(ThreatCategory.allCases, id: \.self) { category in
                        threatCategoryRow(category: category)
                    }
                    .padding(.horizontal, Spacing.m)
                    .padding(.bottom, Spacing.m)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Threat Category Row
    
    private func threatCategoryRow(category: ThreatCategory) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.2, dampingFraction: 0.8)) {
                    // Toggle expansion
                    if expandedThreatCategory == category {
                        expandedThreatCategory = nil
                    } else {
                        expandedThreatCategory = category
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.s) {
                    Text(category.emoji)
                        .font(.system(size: 20))
                    
                    Text(category.rawValue)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    Text("(\(category.count))")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Image(systemName: expandedThreatCategory == category ? "chevron.up" : "chevron.down")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(.vertical, Spacing.s)
            }
            
            // Expanded threats list
            if expandedThreatCategory == category {
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    ForEach(Array(category.threats.enumerated()), id: \.offset) { index, threat in
                        HStack(spacing: Spacing.xs) {
                            Circle()
                                .fill(Color.secondaryGold.opacity(0.3))
                                .frame(width: 4, height: 4)
                            
                            Text(threat)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(.leading, Spacing.l)
                .padding(.top, Spacing.xs)
                .padding(.bottom, Spacing.s)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(.vertical, Spacing.xs)
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
                
                Text("Сравнить все тарифы")
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
    
    // MARK: - Threat Category Enum
    
    enum ThreatCategory: String, CaseIterable {
        case cyberThreats = "КИБЕРУГРОЗЫ"
        case fraud = "МОШЕННИЧЕСТВО"
        case childThreats = "ДЕТСКИЕ УГРОЗЫ"
        case dataLeaks = "УТЕЧКИ ДАННЫХ"
        case deepfakes = "ПОДДЕЛКИ"
        case internetThreats = "ИНТЕРНЕТ-УГРОЗЫ"
        case mobileThreats = "МОБИЛЬНЫЕ УГРОЗЫ"
        case familyThreats = "СЕМЕЙНЫЕ УГРОЗЫ"
        case iotThreats = "УМНЫЙ ДОМ"
        
        var emoji: String {
            switch self {
            case .cyberThreats: return "🛡️"
            case .fraud: return "💰"
            case .childThreats: return "👶"
            case .dataLeaks: return "🔒"
            case .deepfakes: return "🎭"
            case .internetThreats: return "🌐"
            case .mobileThreats: return "📱"
            case .familyThreats: return "🏠"
            case .iotThreats: return "🏡"
            }
        }
        
        var count: Int {
            switch self {
            case .cyberThreats: return 10
            case .fraud: return 12
            case .childThreats: return 17
            case .dataLeaks: return 12
            case .deepfakes: return 8
            case .internetThreats: return 6
            case .mobileThreats: return 10
            case .familyThreats: return 15
            case .iotThreats: return 10
            }
        }
        
        var threats: [String] {
            switch self {
            case .cyberThreats:
                return ["Вирусы и трояны", "Ransomware", "Шпионское ПО", "Ботнеты", "DDoS атаки", "Фишинговые сайты", "Поддельные приложения", "Вредоносные ссылки", "Криптовалютные майнеры", "Руткиты"]
            case .fraud:
                return ["Телефонное мошенничество", "Финансовое мошенничество", "Медицинские аферы", "Социальная инженерия", "Поддельные банки", "Фишинговые письма", "Мошенничество с картами", "Инвестиционные пирамиды", "Лотерейные мошенничества", "Романтические аферы", "Vishing (голосовой фишинг)", "Smishing (SMS фишинг)"]
            case .childThreats:
                return ["Неподходящий контент", "Кибербуллинг", "Опасные знакомства", "Игровая зависимость", "Случайные покупки", "Взрослые сайты", "Насилие в играх", "Наркотики и алкоголь", "Азартные игры", "Экстремистский контент", "Self-harm content", "Inappropriate advertisements", "Online predators", "Grooming атаки", "Catfishing", "Toxic gaming communities", "Online gambling addiction"]
            case .dataLeaks:
                return ["Кража паролей", "Компрометация аккаунтов", "Утечки персональных данных", "Нарушение приватности", "Слежка за семьей", "Утечки в темной сети", "Утечки метаданных", "Keyloggers", "Session hijacking", "Tracking cookies", "Location tracking", "EXIF data leaks"]
            case .deepfakes:
                return ["Deepfake видео", "Поддельные голоса", "Спуфинг номеров", "Поддельные сайты", "Фейковые новости", "Поддельные документы", "Fake dating profiles", "Email spoofing"]
            case .internetThreats:
                return ["Опасные сайты", "Вредоносная реклама", "Подозрительные загрузки", "Небезопасные Wi-Fi", "DNS-спуфинг", "Man-in-the-middle атаки"]
            case .mobileThreats:
                return ["Вредоносные приложения", "SMS-мошенничество", "Поддельные уведомления", "Кража данных с телефона", "Геолокационные угрозы", "Bluetooth-атаки", "SIM swapping", "Fake mobile banking apps", "Mobile ransomware", "Screen recorders"]
            case .familyThreats:
                return ["Домашнее насилие в сети", "Семейные конфликты", "Изоляция от семьи", "Эмоциональные проблемы", "Психологическое давление", "Cyberstalking", "Digital harassment", "Online disputes", "Family member impersonation", "Digital isolation", "Online depression triggers", "Online manipulation", "Gaslighting в сети", "Family privacy violations", "Unauthorized family member access"]
            case .iotThreats:
                return ["Взлом умных устройств", "Вторжение в умный дом", "Скомпрометированные камеры", "Подслушивание через умную колонку", "Взлом домашней сети", "Утечка данных умных устройств", "Манипуляция голосовыми командами", "Слабые пароли устройств", "Использование паролей по умолчанию", "Кража умного устройства"]
            }
        }
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
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    Text("📊 СРАВНЕНИЕ ТАРИФОВ")
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
                    Button("Готово") {
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
            comparisonRow(title: "Цена", values: ["0₽", "290₽", "490₽", "990₽"])
            comparisonRow(title: "Устройства", values: ["1", "4", "6", "10"])
            comparisonRow(title: "Защита", values: ["20+%", "50+%", "80+%", "100%"], highlightIndex: 3)
            comparisonRow(title: "VPN", values: ["50МБ/дн", "∞", "∞", "∞"])
            
            // Разделитель
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Функции - вторая часть
            Group {
                comparisonRow(title: "Защита детей", values: ["✅", "✅", "✅", "✅"])
                comparisonRow(title: "Защита пожилых", values: ["❌", "❌", "✅", "✅"])
                comparisonRow(title: "AI анализ", values: ["❌", "✅", "✅", "✅"])
                comparisonRow(title: "Голосовое управление", values: ["❌", "❌", "✅", "✅"])
                comparisonRow(title: "Геймификация", values: ["❌", "❌", "✅", "✅"])
            }
            
            Group {
                comparisonRow(title: "Анонимность", values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: "AES-256", values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: "Deepfake защита", values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: "Мониторинг утечек", values: ["❌", "❌", "❌", "✅"])
                comparisonRow(title: "Месяц бесплатно", values: ["⭐", "✅", "✅", "✅"])
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
            Text("Критерий")
                .font(.bodyBold)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text("FREE")
                .font(.captionBold)
                .foregroundColor(TariffColumn.free.color)
                .frame(maxWidth: .infinity)
            
            Text("BASIC")
                .font(.captionBold)
                .foregroundColor(TariffColumn.basic.color)
                .frame(maxWidth: .infinity)
            
            Text("FAMILY")
                .font(.captionBold)
                .foregroundColor(TariffColumn.family.color)
                .frame(maxWidth: .infinity)
            
            Text("PREMIUM")
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
            Text("💡 РЕКОМЕНДАЦИИ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            recommendationCard(
                title: "🆓 FREEMIUM",
                subtitle: "Начните с бесплатного",
                text: "Попробуйте систему бесплатно, защитите 1 устройство от базовых угроз"
            )
            
            recommendationCard(
                title: "💎 BASIC",
                subtitle: "Для одного пользователя",
                text: "Идеально для индивидуальной защиты на 4 устройствах с AI-анализом"
            )
            
            recommendationCard(
                title: "👨‍👩‍👧‍👦 FAMILY ⭐ ПОПУЛЯРНЫЙ",
                subtitle: "Для всей семьи",
                text: "Лучший баланс цены и функций - защитите всю семью на 6 устройствах",
                highlight: true
            )
            
            recommendationCard(
                title: "⭐ PREMIUM",
                subtitle: "Максимальная защита",
                text: "Военное шифрование, анонимность, защита от deepfake и всех угроз"
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

