#if !APP_STORE_BUILD
import SwiftUI

/**
 * 💳 Payment QR Screen
 * Экран оплаты через QR-код (СБП, SberPay, Universal)
 * Для российских пользователей вместо IAP
 * ⚠️ С текущего релиза основная оплата перенесена на лендинг; экран оставлен как резерв
 */

struct PaymentQRScreen: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel: PaymentQRViewModel
#if DEBUG
    @State private var showNavigationLogs: Bool = false
#endif
    let tariff: Tariff
    let onPaymentCompleted: () -> Void
    
    // MARK: - Helper Methods
    
    // ✅ Логи только в консоль (без визуального отображения)
    private func addLog(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let logMessage = "[\(timestamp)] \(message)"
        print(logMessage)
    }
    
    // MARK: - Init
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ViewModel создается через StateObject(wrappedValue:)
    // Это правильный способ для SwiftUI - StateObject управляет lifecycle автоматически
    init(tariff: Tariff, onPaymentCompleted: @escaping () -> Void) {
        // 🚨 САМЫЙ ПЕРВЫЙ ЛОГ - должен появиться ПЕРВЫМ!
        // Примечание: addLog() нельзя вызвать здесь, т.к. это init
        // Логи будут добавлены в onAppear
        print("🚨🚨🚨 PaymentQRScreen.init НАЧАЛОСЬ! 🚨🚨🚨")
        
        print("🚨 ========== PaymentQRScreen.init НАЧАЛО ==========")
        print("🔍 Thread: \(Thread.isMainThread ? "Main" : "Background")")
        print("🔍 Stack trace:")
        Thread.callStackSymbols.prefix(10).forEach { print("   \($0)") }
        
        print("🔍 PaymentQRScreen.init: Начало инициализации")
        print("   - id: '\(tariff.id)'")
        print("   - title: '\(tariff.title)'")
        print("   - price: '\(tariff.price)'")
        print("   - period: '\(tariff.period)'")
        print("   - features.count: \(tariff.features.count)")
        
        self.onPaymentCompleted = onPaymentCompleted
        
        // ✅ ИСПРАВЛЕНИЕ #4: Создаем ViewModel безопасно с проверкой
        // ObservedObject не требует специального управления lifecycle, но нужна защита
        print("🔍 Перед созданием PaymentQRViewModel...")
        print("   - AppConfig.apiBaseURL существует: \(!AppConfig.apiBaseURL.isEmpty)")
        print("   - AppConfig.isAPIURLValid(): \(AppConfig.isAPIURLValid())")
        
        // ✅ ИСПРАВЛЕНИЕ: Проверяем тариф перед созданием ViewModel, НО не используем fatalError
        // fatalError крашит приложение - используем безопасный fallback
        let safeTariff: Tariff
        if tariff.id.isEmpty {
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: Tariff.id пустой! Создаем fallback тариф")
            // Создаем безопасный fallback тариф
            // Создаем безопасный fallback тариф (используем ключи локализации позже)
            let localizationManager = LocalizationManager.shared
            safeTariff = Tariff(
                id: "fallback_\(UUID().uuidString)",
                title: localizationManager.localized("payment_qr_fallback_tariff"),
                price: "0 ₽",
                period: localizationManager.localized("payment_qr_fallback_period"),
                features: [localizationManager.localized("payment_qr_fallback_feature")],
                product: nil,
                isPurchased: false,
                periodMonths: 1,
                originalPrice: nil,
                discountPercent: nil,
                monthlyPrice: "0 ₽",
                savings: nil
            )
            print("⚠️ PaymentQRScreen: Использован fallback тариф")
        } else {
            safeTariff = tariff
        }
        
        // Устанавливаем безопасный тариф один раз
        self.tariff = safeTariff
        
        print("🔍 Создание PaymentQRViewModel через StateObject(wrappedValue:) в PaymentQRScreen.init")
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем StateObject(wrappedValue:) - правильный способ для SwiftUI
        // StateObject управляет lifecycle автоматически и безопасен для использования в init
        self._viewModel = StateObject(wrappedValue: PaymentQRViewModel(tariff: safeTariff))
        
        print("✅ PaymentQRViewModel создан через StateObject")
        
        print("✅ PaymentQRScreen.init: Инициализация завершена")
        print("🚨 ========== PaymentQRScreen.init КОНЕЦ ==========")
    }
    
    // MARK: - Body
    
    var body: some View {
        // ✅ ViewModel создан в init через ObservedObject
        // ObservedObject безопасно создается в init и управляется SwiftUI
        paymentQRScreenContent(viewModel: viewModel)
            .navigationBarHidden(true)
            // ✅ УДАЛЕНО: Визуальные логи с экрана (оставляем только в консоли)
            .onAppear {
                addLog("✅ PaymentQRScreen.onAppear: Экран появился")
                addLog("ViewModel тариф ID: \(viewModel.tariff.id)")
                
                print("🔍 PaymentQRScreen.onAppear: Экран появился")
                print("   - ViewModel уже создан: \(viewModel.tariff.id)")
                
                // Начинаем создание платежа
                addLog("🔍 Начинаем создание платежа...")
                print("🔍 PaymentQRScreen.onAppear: Начинаем создание платежа")
                viewModel.createPayment()
                viewModel.startAutoCheck()
                
                addLog("✅ Платеж инициирован успешно")
                print("✅ PaymentQRScreen.onAppear: Платеж инициирован")
            }
            .onDisappear {
                print("🔍 PaymentQRScreen.onDisappear: Останавливаем авто-проверку")
                DispatchQueue.main.async {
                    viewModel.resetState()
                }
            }
            .onChange(of: viewModel.errorMessage) { newValue in
#if DEBUG
                if let message = newValue {
                    navigationManager.recordDebugLog("❗️ PaymentQR error alert: \(message)")
                }
#endif
            }
            .onChange(of: viewModel.showSuccessAlert) { isShown in
#if DEBUG
                if isShown {
                    navigationManager.recordDebugLog("✅ PaymentQR success alert отображён")
                }
#endif
            }
        .alert(localizationManager.localized("payment_qr_success_title"), isPresented: $viewModel.showSuccessAlert) {
            Button(localizationManager.localized("payment_qr_success_button")) {
                onPaymentCompleted()
            }
        } message: {
            Text(String(format: localizationManager.localized("payment_qr_success_message"), tariff.title))
        }
        .alert(localizationManager.localized("payment_qr_error_title"), isPresented: $viewModel.showErrorAlert) {
            Button(localizationManager.localized("payment_qr_error_ok")) {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
#if DEBUG
        .overlay(alignment: .topTrailing) {
            if AppConfig.showDebugOverlays && !AppConfig.screenshotMode {
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
                        NavigationDebugOverlay(title: "PaymentQR Navigation",
                                               logEntries: latestLogs)
                            .transition(.move(edge: .trailing).combined(with: .opacity))
                            .shadow(radius: 8)
                    }
                }
                .padding(.trailing, 16)
                .padding(.top, 16)
            }
        }
#endif
    }
    
    // MARK: - Content Views
    
    private func paymentQRScreenContent(viewModel: PaymentQRViewModel) -> some View {
        ZStack {
            // Фон — Storm Mesh premium light (Batch 4)
            StormMeshBackground(variant: .premium)
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Navigation Bar с кнопкой назад
                    ALADDINNavigationBar(
                        title: localizationManager.localized("payment_qr_title"),
                        subtitle: localizationManager.localized("payment_qr_subtitle"),
                        showBackButton: true,
                        showProfileButton: false,
                        showListButton: false,
                        onBack: {
                            navigationManager.beginManualPaymentQRClose()
                            viewModel.prepareForManualClose()
                            navigationManager.goBack(reason: "PaymentQR.onBack")
                        }
                    )
                    
                    // Timer
                    if let expiresAt = viewModel.expiresAt, !AppConfig.screenshotMode {
                        timerView(expiresAt: expiresAt)
                    }
                    
                    // QR Tabs
                    if AppConfig.screenshotMode {
                        demoQRView
                    } else {
                        qrTabsView(viewModel: viewModel)
                    }
                    
                    // Instructions (expandable)
                    if !AppConfig.screenshotMode {
                        expandableInstructionsView
                    }
                    
                    // Banks List (expandable)
                    if !AppConfig.screenshotMode {
                        expandableBanksView
                    }
                    
                    // Check Payment Button
                    if !AppConfig.screenshotMode {
                        checkPaymentButton(viewModel: viewModel)
                    }
                    
                    // Payment Info
                    paymentInfoView(viewModel: viewModel)
                    
                    Spacer()
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            
            // Loading Overlay
            if viewModel.isLoading {
                Color.black.opacity(0.5)
                    .ignoresSafeArea()
                ProgressView()
                    .scaleEffect(1.5)
                    .tint(.secondaryGold)
            }
        }
    }
    
    // MARK: - Timer View
    
    private func timerView(expiresAt: Date) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text("⏰")
                .font(.system(size: 32))
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(timeRemaining(until: expiresAt))
                .font(.h3)
                .foregroundColor(.secondaryGold)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(localizationManager.localized("payment_qr_timer_until"))
                .font(SwiftUI.Font.caption)
                .foregroundColor(.textSecondary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    // MARK: - QR Tabs
    
    private func qrTabsView(viewModel: PaymentQRViewModel) -> some View {
        VStack(spacing: Spacing.m) {
            // ✅ ВЕРНУТО: Табы банков для выбора метода оплаты
            HStack(spacing: Spacing.xs) {
                ForEach(PaymentMethod.allCases, id: \.self) { method in
                    Button(action: {
                        viewModel.selectedMethod = method
                        HapticFeedback.selection()
                    }) {
                        VStack(spacing: Spacing.xxs) {
                            Text("💳")
                                .font(.system(size: 20))
                            Text(method.localizedShortName(localizationManager))
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(viewModel.selectedMethod == method ? .secondaryGold : .textSecondary)
                                .lineLimit(1)
                                .minimumScaleFactor(0.8)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.xs)
                        .padding(.horizontal, 4)
                        .background(
                            viewModel.selectedMethod == method ?
                            Color.primaryBlue.opacity(0.3) :
                            Color.clear
                        )
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
            .padding(.horizontal, Spacing.m)
            
            // QR Code Display - показываем сразу если есть
            // ✅ УЛУЧШЕНИЕ: Добавлена обработка всех состояний UI
            if let qrImage = viewModel.currentQRImage, !qrImage.isEmpty {
                VStack(alignment: .center, spacing: Spacing.m) {
                    // ✅ УЛУЧШЕНИЕ: Заголовок без эмодзи, выровненный по центру
                    VStack(alignment: .center, spacing: Spacing.xs) {
                        Text(localizationManager.localized("payment_qr_qr_code_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.center)
                        
                        Text(localizationManager.localized("payment_qr_scan_instruction"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.bottom, Spacing.s)
                    
                    // ✅ УЛУЧШЕНИЕ: QR код с поддержкой URL и base64, выровнен по центру
                    Group {
                        if let url = URL(string: qrImage) {
                            // Это URL - загружаем через AsyncImage
                            AsyncImage(url: url) { phase in
                                switch phase {
                                case .success(let image):
                                    image
                                        .resizable()
                                        .interpolation(.none)
                                        .scaledToFit()
                                        .frame(width: 280, height: 280)
                                        .background(Color.white)
                                        .cornerRadius(CornerRadius.large)
                                        .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
                                case .failure(_):
                                    qrCodeErrorView(onRetry: {
                                        print("❌ Ошибка загрузки QR-кода, URL: \(qrImage)")
                                        viewModel.createPayment()
                                    })
                                case .empty:
                                    VStack(spacing: Spacing.m) {
                                        ProgressView()
                                            .scaleEffect(1.5)
                                            .tint(.secondaryGold)
                                        Text(localizationManager.localized("payment_qr_loading"))
                                            .font(SwiftUI.Font.caption)
                                            .foregroundColor(.textSecondary)
                                    }
                                    .frame(width: 280, height: 280)
                                @unknown default:
                                    placeholder
                                }
                            }
                        } else if qrImage.hasPrefix("data:image/") || qrImage.hasPrefix("iVBORw0KGgo") {
                            // Это base64 изображение - декодируем напрямую
                            if let data = Data(base64Encoded: qrImage.components(separatedBy: ",").last ?? qrImage),
                               let uiImage = UIImage(data: data) {
                                Image(uiImage: uiImage)
                                    .resizable()
                                    .interpolation(.none)
                                    .scaledToFit()
                                    .frame(width: 280, height: 280)
                                    .background(Color.white)
                                    .cornerRadius(CornerRadius.large)
                                    .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
                            } else {
                                qrCodeErrorView(onRetry: {
                                    print("❌ Ошибка декодирования base64 QR-кода")
                                    viewModel.createPayment()
                                })
                            }
                        } else {
                            // Неизвестный формат
                            qrCodeErrorView(onRetry: {
                                print("❌ Неизвестный формат QR-кода: \(String(qrImage.prefix(50)))...")
                                viewModel.createPayment()
                            })
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.top, Spacing.s)
                    
                    // Текст убран - он уже есть в заголовке выше
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(Spacing.cardPadding)
                .stormGlassCard(cornerRadius: CornerRadius.large)
            } else if viewModel.isLoading {
                // ✅ УЛУЧШЕНИЕ: Показываем состояние загрузки QR кода, выровнено по центру
                VStack(alignment: .center, spacing: Spacing.m) {
                    Text(localizationManager.localized("payment_qr_qr_code_title"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                    
                    VStack(spacing: Spacing.m) {
                        ProgressView()
                            .scaleEffect(1.5)
                            .tint(.secondaryGold)
                        Text(localizationManager.localized("payment_qr_creating"))
                            .font(SwiftUI.Font.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                        Text(localizationManager.localized("payment_qr_loading_steps"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, Spacing.m)
                    }
                    .frame(width: 280, height: 280)
                    .background(Color.surfaceDark)
                    .cornerRadius(CornerRadius.large)
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(Spacing.cardPadding)
                .stormGlassCard(cornerRadius: CornerRadius.large)
            } else {
                // ✅ УЛУЧШЕНИЕ: Показываем ошибку с кнопкой "Обновить" если загрузка завершена, но QR нет, выровнено по центру
                VStack(alignment: .center, spacing: Spacing.m) {
                    Text(localizationManager.localized("payment_qr_qr_code_title"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                    
                    qrCodeErrorView(onRetry: {
                        print("🔄 Пользователь нажал 'Обновить' - повторяем создание платежа")
                        viewModel.createPayment()
                    })
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(Spacing.cardPadding)
                .stormGlassCard(cornerRadius: CornerRadius.large)
            }
        }
    }
    
    private var placeholder: some View {
        Rectangle()
            .fill(Color.surfaceDark)
            .frame(width: 280, height: 280)
            .cornerRadius(CornerRadius.large)
            .overlay(
                Text(localizationManager.localized("payment_qr_unavailable"))
                    .font(SwiftUI.Font.caption)
                    .foregroundColor(.textSecondary)
            )
    }
    
    private func qrCodeErrorView(onRetry: @escaping () -> Void) -> some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 40))
                .foregroundColor(.dangerRed)
            Text(localizationManager.localized("payment_qr_error_load"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Text(localizationManager.localized("payment_qr_error_connection"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
            Button(localizationManager.localized("payment_qr_button_refresh")) {
                onRetry()
            }
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.xs)
            .background(Color.primaryBlue)
            .foregroundColor(.white)
            .cornerRadius(CornerRadius.medium)
        }
        .frame(width: 280, height: 280)
        .background(Color.surfaceDark)
        .cornerRadius(CornerRadius.large)
    }
    
    // MARK: - Expandable Instructions
    
    @State private var isInstructionsExpanded: Bool = false
    
    private var expandableInstructionsView: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header (always visible) - выровнен по левому краю
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isInstructionsExpanded.toggle()
                }
                HapticFeedback.selection()
            }) {
                HStack(alignment: .center, spacing: Spacing.xs) {
                    Text(localizationManager.localized("payment_qr_instructions_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .lineLimit(1)
                    Image(systemName: isInstructionsExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.cardPadding)
            }
            
            // Content (expandable)
            if isInstructionsExpanded {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Divider()
                        .background(Color.textTertiary)
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                        instructionStep(number: 1, 
                                       title: localizationManager.localized("payment_qr_instruction_step1_title"),
                                       text: localizationManager.localized("payment_qr_instruction_step1_text"))
                        
                        instructionStep(number: 2,
                                       title: localizationManager.localized("payment_qr_instruction_step2_title"),
                                       text: localizationManager.localized("payment_qr_instruction_step2_text"))
                        
                        instructionStep(number: 3,
                                       title: localizationManager.localized("payment_qr_instruction_step3_title"),
                                       text: localizationManager.localized("payment_qr_instruction_step3_text"))
                        
                        instructionStep(number: 4,
                                       title: localizationManager.localized("payment_qr_instruction_step4_title"),
                                       text: localizationManager.localized("payment_qr_instruction_step4_text"))
                        
                        instructionStep(number: 5,
                                       title: localizationManager.localized("payment_qr_instruction_step5_title"),
                                       text: localizationManager.localized("payment_qr_instruction_step5_text"))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.cardPadding)
                    
                    // Important note - без эмодзи, выровнено по левому краю
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("payment_qr_important"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        
                        Text(localizationManager.localized("payment_qr_important_note1"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text(localizationManager.localized("payment_qr_important_note2"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text(localizationManager.localized("payment_qr_important_note3"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text(localizationManager.localized("payment_qr_important_note4"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text(localizationManager.localized("payment_qr_important_note5"))
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .font(.system(size: 13))
                    .foregroundColor(.textSecondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(Spacing.m)
                    .background(Color.primaryBlue.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    .padding(.horizontal, Spacing.cardPadding)
                    .padding(.bottom, Spacing.cardPadding)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    private func instructionStep(number: Int, title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("\(number)")
                    .font(.h3)
                    .foregroundColor(.secondaryGold)
                    .frame(width: 36, height: 36)
                    .background(Color.surfaceDark)
                    .cornerRadius(CornerRadius.small)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    Text(text)
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, Spacing.xs)
    }
    
    // MARK: - Expandable Banks List
    
    @State private var isBanksExpanded: Bool = false
    
    private var expandableBanksView: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header (always visible) - выровнен по левому краю
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isBanksExpanded.toggle()
                }
                HapticFeedback.selection()
            }) {
                HStack(alignment: .center, spacing: Spacing.xs) {
                    Text(localizationManager.localized("payment_qr_banks_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .fontWeight(.bold)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .lineLimit(1)
                    Image(systemName: isBanksExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.cardPadding)
            }
            
            // Content (expandable)
            if isBanksExpanded {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    Text(localizationManager.localized("payment_qr_banks_description"))
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, Spacing.cardPadding)
                        .padding(.top, Spacing.s)
                    
                    // Banks list - простой список, выровненный по левому краю
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        ForEach(supportedBanks, id: \.titleKey) { bank in
                            bankCard(bank: bank)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.cardPadding)
                    .padding(.bottom, Spacing.cardPadding)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    private func bankCard(bank: BankInfo) -> some View {
        HStack(spacing: Spacing.s) {
            Text(bank.emoji)
                .font(.system(size: 24))
            Text(localizationManager.localized(bank.titleKey))
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, Spacing.m)
        .padding(.horizontal, Spacing.m)
        .background(Color.surfaceDark.opacity(0.5))
        .cornerRadius(CornerRadius.medium)
    }
    
    struct BankInfo {
        let titleKey: String
        let emoji: String
    }
    
    private let supportedBanks: [BankInfo] = [
        BankInfo(titleKey: "payment_qr_bank_sber", emoji: "🏛️"),
        BankInfo(titleKey: "payment_qr_bank_vtb", emoji: "🏦"),
        BankInfo(titleKey: "payment_qr_bank_tinkoff", emoji: "💳"),
        BankInfo(titleKey: "payment_qr_bank_alfa", emoji: "🏢"),
        BankInfo(titleKey: "payment_qr_bank_raiffeisen", emoji: "🏪"),
        BankInfo(titleKey: "payment_qr_bank_gazprom", emoji: "⛽"),
        BankInfo(titleKey: "payment_qr_bank_otkritie", emoji: "🚪"),
        BankInfo(titleKey: "payment_qr_bank_yoomoney", emoji: "💸"),
        BankInfo(titleKey: "payment_qr_bank_pochta", emoji: "📮"),
        BankInfo(titleKey: "payment_qr_bank_rosbank", emoji: "🇷🇺"),
        BankInfo(titleKey: "payment_qr_bank_mkb", emoji: "🏛️"),
        BankInfo(titleKey: "payment_qr_bank_mts", emoji: "📱"),
        BankInfo(titleKey: "payment_qr_bank_rosselkhoz", emoji: "🌾"),
        BankInfo(titleKey: "payment_qr_bank_homecredit", emoji: "🏠"),
        BankInfo(titleKey: "payment_qr_bank_sovcom", emoji: "🔷"),
        BankInfo(titleKey: "payment_qr_bank_akbars", emoji: "⚪"),
        BankInfo(titleKey: "payment_qr_bank_uralsib", emoji: "⛰️"),
        BankInfo(titleKey: "payment_qr_bank_rencredit", emoji: "✨"),
        BankInfo(titleKey: "payment_qr_bank_psb", emoji: "🏦"),
        BankInfo(titleKey: "payment_qr_bank_other", emoji: "💼")
    ]
    
    // MARK: - Check Payment Button
    
    private func checkPaymentButton(viewModel: PaymentQRViewModel) -> some View {
        Button(action: {
            print("🔍 ========== Пользователь нажал 'Проверить статус оплаты' ==========")
            print("   - paymentId: \(viewModel.paymentId ?? "nil")")
            print("   - isLoading: \(viewModel.isLoading)")
            print("   - currentQRImage: \(viewModel.currentQRImage != nil ? "есть" : "nil")")
            
            // ✅ Добавляем haptic feedback для лучшего UX
            HapticFeedback.impact(.medium)
            
            viewModel.checkPaymentStatus()
        }) {
            HStack {
                if viewModel.isLoading {
                    ProgressView()
                        .scaleEffect(0.8)
                        .tint(.white)
                    Text(localizationManager.localized("payment_qr_checking"))
                        .font(.system(size: 16, weight: .semibold))
                } else {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 16, weight: .semibold))
                    Text(localizationManager.localized("payment_qr_check_button"))
                        .font(.system(size: 16, weight: .semibold))
                }
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 48)
            .background(
                viewModel.paymentId != nil && !viewModel.isLoading ?
                Color.primaryBlue :
                Color.gray.opacity(0.5)
            )
            .cornerRadius(8)
        }
        .disabled(viewModel.isLoading || viewModel.paymentId == nil)
        .opacity((viewModel.paymentId != nil && !viewModel.isLoading) ? 1.0 : 0.6)
    }
    
    // MARK: - Payment Info
    
    private func paymentInfoView(viewModel: PaymentQRViewModel) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("payment_qr_info_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                infoRow(label: localizationManager.localized("payment_qr_info_tariff"), value: tariff.title)
                
                // Период подписки
                if tariff.periodMonths > 1 {
                    let periodText = tariff.periodMonths == 1 
                        ? localizationManager.localized("tariffs_period_month")
                        : "\(tariff.periodMonths) месяцев"
                    infoRow(label: "Период подписки", value: periodText)
                    
                    // Скидка (если есть)
                    if let discount = tariff.discountPercent, discount > 0 {
                        infoRow(label: "Скидка", value: "-\(discount)%")
                    }
                    
                    // Экономия (если есть)
                    if let savings = tariff.savings, !savings.isEmpty {
                        infoRow(label: "Экономия", value: savings)
                    }
                }
                
                infoRow(label: localizationManager.localized("payment_qr_info_amount"), value: tariff.price)
                infoRow(label: localizationManager.localized("payment_qr_info_period"), value: tariff.period)
                
                if let merchantInfo = viewModel.merchantInfo {
                    Divider()
                        .background(Color.textTertiary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    infoRow(label: localizationManager.localized("payment_qr_info_recipient"), value: merchantInfo.name)
                    infoRow(label: localizationManager.localized("payment_qr_info_address"), value: merchantInfo.address)
                    infoRow(label: localizationManager.localized("payment_qr_info_phone"), value: merchantInfo.phone ?? localizationManager.localized("payment_qr_info_phone_not_set"))
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large)
    }
    
    private func infoRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(SwiftUI.Font.body)
                .foregroundColor(.textSecondary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
    }
    
    // MARK: - Helpers
    
    private func timeRemaining(until date: Date) -> String {
        let now = Date()
        let remaining = date.timeIntervalSince(now)
        
        if remaining <= 0 {
            return localizationManager.localized("payment_qr_expired")
        }
        
        let hours = Int(remaining) / 3600
        let minutes = (Int(remaining) % 3600) / 60
        
        return String(format: "%02d:%02d", hours, minutes)
    }
    
    // MARK: - Demo QR for Screenshot Mode
    private var demoQRView: some View {
        VStack(spacing: Spacing.m) {
            if let image = generateQRCode(from: "https://aladdin.family/pay/demo") {
                Image(uiImage: image)
                    .interpolation(.none)
                    .resizable()
                    .scaledToFit()
                    .frame(width: 220, height: 220)
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: .black.opacity(0.15), radius: 8, x: 0, y: 4)
            }
            Text(localizationManager.localized("payment_qr_subtitle"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
    }
    
    private func generateQRCode(from string: String) -> UIImage? {
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        filter.message = Data(string.utf8)
        if let outputImage = filter.outputImage {
            let transform = CGAffineTransform(scaleX: 10, y: 10)
            let scaledImage = outputImage.transformed(by: transform)
            if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
                return UIImage(cgImage: cgImage)
            }
        }
        return nil
    }
}


// MARK: - Merchant Info


#if DEBUG
struct NavigationDebugOverlay: View {
    let title: String
    let logEntries: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .fontWeight(.semibold)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Divider().blendMode(.overlay)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(Array(logEntries.suffix(24).enumerated()), id: \.offset) { _, entry in
                        Text(entry)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white.opacity(0.92))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 1)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 200)
        }
        .padding(12)
        .background(Color.black.opacity(0.7))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.white.opacity(0.2))
        )
    }
}
#endif

// MARK: - Preview
struct PaymentQRScreen_Previews: PreviewProvider {
    static var previews: some View {
        let testTariff = Tariff(
                id: "test",
                title: "Семейный",
                price: "590 ₽",
                period: "в месяц",
                features: ["До 5 устройств", "Полная защита"],
                product: nil,
                isPurchased: false
        )
        return PaymentQRScreen(
            tariff: testTariff,
            onPaymentCompleted: {}
        )
    }
}

#endif

