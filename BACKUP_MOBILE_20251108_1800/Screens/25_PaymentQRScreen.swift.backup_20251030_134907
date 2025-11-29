import SwiftUI

/**
 * 💳 Payment QR Screen
 * Экран оплаты через QR-код (СБП, SberPay, Universal)
 * Для российских пользователей вместо IAP
 */

struct PaymentQRScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем @StateObject с deferred инициализацией
    @StateObject private var viewModel: PaymentQRViewModel
    // ✅ УДАЛЕНО: Визуальные логи (только консоль)
    
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
            safeTariff = Tariff(
                id: "fallback_\(UUID().uuidString)",
                title: "Тариф",
                price: "0 ₽",
                period: "в месяц",
                features: ["Базовая защита"],
                product: nil,
                isPurchased: false
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
                viewModel.stopAutoCheck()
            }
        .alert("Оплата успешна!", isPresented: $viewModel.showSuccessAlert) {
            Button("Отлично!") {
                onPaymentCompleted()
                dismiss()
            }
        } message: {
            Text("Подписка \(tariff.title) активирована!\n\nСпасибо за покупку!")
        }
        .alert("Ошибка", isPresented: $viewModel.showErrorAlert) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let error = viewModel.errorMessage {
                Text(error)
            }
        }
    }
    
    // MARK: - Content Views
    
    private func paymentQRScreenContent(viewModel: PaymentQRViewModel) -> some View {
        ZStack {
            // Background
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Navigation Bar с кнопкой назад
                    ALADDINNavigationBar(
                        title: "ОПЛАТА",
                        subtitle: "QR-код оплаты",
                        showBackButton: true,
                        onBack: {
                            // ✅ ИСПРАВЛЕНИЕ: Всегда возвращаемся на страницу тарифов
                            // (Реализовано как в ChildInterfaceScreen и ElderlyInterfaceScreen)
                            print("🔙 Возврат из PaymentQRScreen")
                            print("🔙 Текущий экран: \(navigationManager.currentScreen)")
                            print("🔙 canGoBack: \(navigationManager.canGoBack)")
                            print("🔙 navigationStack.count: \(navigationManager.navigationStack.count)")
                            
                            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Всегда возвращаемся на страницу тарифов
                            // Используем goBack() если есть стек и предыдущий экран - тарифы,
                            // иначе - явно переходим на тарифы
                            if navigationManager.canGoBack, 
                               let previousScreen = navigationManager.previousScreen,
                               previousScreen == .tariffs {
                                // Предыдущий экран - тарифы, используем goBack()
                                print("🔙 Возврат через NavigationManager.goBack() на тарифы")
                                navigationManager.goBack()
                            } else {
                                // В любом другом случае - явно переходим на тарифы
                                print("🔙 Переход на .tariffs явно (как fallback)")
                                navigationManager.navigateTo(.tariffs)
                            }
                        }
                    )
                    
                    // Timer
                    if let expiresAt = viewModel.expiresAt {
                        timerView(expiresAt: expiresAt)
                    }
                    
                    // QR Tabs
                    qrTabsView(viewModel: viewModel)
                    
                    // Instructions (expandable)
                    expandableInstructionsView
                    
                    // Banks List (expandable)
                    expandableBanksView
                    
                    // Check Payment Button
                    checkPaymentButton(viewModel: viewModel)
                    
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
            
            Text("до окончания срока оплаты")
                .font(SwiftUI.Font.caption)
                .foregroundColor(.textSecondary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
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
                            Text(method.compactDisplayName)
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
                        Text("QR-КОД ОПЛАТЫ")
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.center)
                        
                        Text("Отсканируйте в приложении банка")
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
                                        Text("Загрузка QR-кода...")
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
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
            } else if viewModel.isLoading {
                // ✅ УЛУЧШЕНИЕ: Показываем состояние загрузки QR кода, выровнено по центру
                VStack(alignment: .center, spacing: Spacing.m) {
                    Text("QR-КОД ОПЛАТЫ")
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                    
                    VStack(spacing: Spacing.m) {
                        ProgressView()
                            .scaleEffect(1.5)
                            .tint(.secondaryGold)
                        Text("Создание платежа...")
                            .font(SwiftUI.Font.body)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(width: 280, height: 280)
                    .background(Color.surfaceDark)
                    .cornerRadius(CornerRadius.large)
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(Spacing.cardPadding)
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
            } else {
                // ✅ УЛУЧШЕНИЕ: Показываем ошибку с кнопкой "Обновить" если загрузка завершена, но QR нет, выровнено по центру
                VStack(alignment: .center, spacing: Spacing.m) {
                    Text("QR-КОД ОПЛАТЫ")
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
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
            }
        }
    }
    
    private var placeholder: some View {
        Rectangle()
            .fill(Color.surfaceDark)
            .frame(width: 280, height: 280)
            .cornerRadius(CornerRadius.large)
            .overlay(
                Text("QR-код недоступен")
                    .font(SwiftUI.Font.caption)
                    .foregroundColor(.textSecondary)
            )
    }
    
    private func qrCodeErrorView(onRetry: @escaping () -> Void) -> some View {
        VStack(spacing: Spacing.m) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 40))
                .foregroundColor(.dangerRed)
            Text("Не удалось загрузить QR-код")
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Text("Проверьте подключение к интернету")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
            Button("Обновить") {
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
                    Text("ИНСТРУКЦИЯ")
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
                                       title: "Откройте приложение банка",
                                       text: "На этом же телефоне откройте приложение вашего банка (Сбербанк, ВТБ, Тинькофф и т.д.)")
                        
                        instructionStep(number: 2,
                                       title: "Найдите сканер QR-кодов",
                                       text: "В приложении найдите раздел \"Оплата по QR\", \"Сканер QR\" или значок камеры. Обычно он находится в главном меню или в разделе \"Платежи\"")
                        
                        instructionStep(number: 3,
                                       title: "Отсканируйте QR-код",
                                       text: "В приложении банка нажмите \"Сканировать QR-код\". Затем переключитесь обратно в ALADDIN (проведите пальцем снизу вверх для переключения приложений). QR-код останется на экране ALADDIN - просто наведите камеру приложения банка на этот QR-код. Также можно сделать скриншот QR-кода!")
                        
                        instructionStep(number: 4,
                                       title: "Подтвердите оплату",
                                       text: "В приложении банка проверьте сумму и получателя, затем подтвердите платеж (обычно кнопка \"Оплатить\" или \"Подтвердить\")")
                        
                        instructionStep(number: 5,
                                       title: "Дождитесь активации",
                                       text: "После успешной оплаты приложение автоматически обнаружит платеж и активирует подписку. Обычно это занимает 10-30 секунд. Вы увидите сообщение об успешной оплате")
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.cardPadding)
                    
                    // Important note - без эмодзи, выровнено по левому краю
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text("Важно знать:")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        
                        Text("• Можно использовать 1 телефон для оплаты или оплачивать с семейного телефона родственника")
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text("• QR-код остается на экране ALADDIN")
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text("• Переключитесь между приложениями (свайп снизу вверх)")
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text("• В приложении банка откройте сканер и наведите камеру на QR-код в ALADDIN или вставьте скрин (фото QR) в приложение банка")
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text("• Оплата происходит через банковское приложение")
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
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
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
                    Text("БАНКИ")
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
                    
                    Text("Все эти банки поддерживают оплату по QR-коду через СБП:")
                        .font(.system(size: 14))
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, Spacing.cardPadding)
                        .padding(.top, Spacing.s)
                    
                    // Banks list - простой список, выровненный по левому краю
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        ForEach(supportedBanks, id: \.name) { bank in
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
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
    }
    
    private func bankCard(bank: BankInfo) -> some View {
        HStack(spacing: Spacing.s) {
            Text(bank.emoji)
                .font(.system(size: 24))
            Text(bank.name)
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
        let name: String
        let emoji: String
    }
    
    private let supportedBanks: [BankInfo] = [
        BankInfo(name: "Сбербанк", emoji: "🏛️"),
        BankInfo(name: "ВТБ", emoji: "🏦"),
        BankInfo(name: "Тинькофф", emoji: "💳"),
        BankInfo(name: "Альфа-Банк", emoji: "🏢"),
        BankInfo(name: "Райффайзен Банк", emoji: "🏪"),
        BankInfo(name: "Газпромбанк", emoji: "⛽"),
        BankInfo(name: "Открытие", emoji: "🚪"),
        BankInfo(name: "ЮMoney", emoji: "💸"),
        BankInfo(name: "Почта Банк", emoji: "📮"),
        BankInfo(name: "Росбанк", emoji: "🇷🇺"),
        BankInfo(name: "МКБ", emoji: "🏛️"),
        BankInfo(name: "МТС Банк", emoji: "📱"),
        BankInfo(name: "Россельхозбанк", emoji: "🌾"),
        BankInfo(name: "Хоум Кредит", emoji: "🏠"),
        BankInfo(name: "Совкомбанк", emoji: "🔷"),
        BankInfo(name: "Ак Барс", emoji: "⚪"),
        BankInfo(name: "Уралсиб", emoji: "⛰️"),
        BankInfo(name: "Ренессанс Кредит", emoji: "✨"),
        BankInfo(name: "ПСБ", emoji: "🏦"),
        BankInfo(name: "Другие банки СБП", emoji: "💼")
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
                    Text("Проверяем...")
                        .font(.system(size: 16, weight: .semibold))
                } else {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 16, weight: .semibold))
                    Text("Проверить статус оплаты")
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
            Text("ИНФОРМАЦИЯ О ПЛАТЕЖЕ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                infoRow(label: "Тариф", value: tariff.title)
                infoRow(label: "Сумма", value: tariff.price)
                infoRow(label: "Период", value: tariff.period)
                
                if let merchantInfo = viewModel.merchantInfo {
                    Divider()
                        .background(Color.textTertiary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    infoRow(label: "Получатель", value: merchantInfo.name)
                    infoRow(label: "Адрес", value: merchantInfo.address)
                    infoRow(label: "Телефон СБП", value: merchantInfo.phone ?? "Не указан")
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.cardPadding)
        .background(
            LinearGradient.cardGradient
                .appGlassmorphism()
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
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
            return "Истек срок"
        }
        
        let hours = Int(remaining) / 3600
        let minutes = (Int(remaining) % 3600) / 60
        
        return String(format: "%02d:%02d", hours, minutes)
    }
}


// MARK: - Merchant Info


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

