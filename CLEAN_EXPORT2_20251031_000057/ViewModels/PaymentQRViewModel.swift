import Foundation
import Combine
import SwiftUI

// MARK: - Types
struct MerchantInfo: Codable {
    let id: String
    let name: String
    let address: String
    let phone: String?
}

// MARK: - API Error
enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, data: Data?)
    case decodingFailed(Error)
    case encodingFailed(Error)
    case unknown(Error)
    case networkError(String)
    case decodingError(String)
    case serverError(String)
    case unknownError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidResponse: return "Invalid Response"
        case .httpError(let statusCode, _): return "HTTP Error: \(statusCode)"
        case .decodingFailed(let error): return "Decoding Error: \(error.localizedDescription)"
        case .encodingFailed(let error): return "Encoding Error: \(error.localizedDescription)"
        case .unknown(let error): return "Unknown Error: \(error.localizedDescription)"
        case .networkError(let message): return "Network Error: \(message)"
        case .decodingError(let message): return "Decoding Error: \(message)"
        case .serverError(let message): return "Server Error: \(message)"
        case .unknownError: return "Unknown Error"
        }
    }
}

// MARK: - Payment Method
enum PaymentMethod: String, CaseIterable {
    case sbp = "sbp"
    case sberpay = "sberpay"
    case card = "card"
    case alpha = "alpha"
    case vtb = "vtb"
    
    var displayName: String {
        switch self {
        case .sbp: return "СБП"
        case .sberpay: return "СберPay"
        case .card: return "МИР"
        case .alpha: return "Альфа"
        case .vtb: return "ВТБ"
        }
    }
    
    // ✅ КОМПАКТНЫЕ НАЗВАНИЯ: Для табов без переносов
    var compactDisplayName: String {
        switch self {
        case .sbp: return "СБП"
        case .sberpay: return "СБЕР"
        case .card: return "МИР"
        case .alpha: return "АЛЬФА"
        case .vtb: return "ВТБ"
        }
    }
}

struct PaymentMethodInfo {
    let id: String
    let name: String
    let type: String
}

// MARK: - API Models (используем из APIModels.swift)
// CreateQRPaymentRequest, CreateQRPaymentResponse, CheckQRPaymentStatusResponse 
// определены в CoreModules/APIModels.swift

struct QRCodeData: Codable {
    let sbp: String?
    let sberpay: String?
    let universal: String?
}

struct MerchantInfoAPI: Codable {
    let name: String
    let id: String
    let phone: String?
    let status: String?  // "pending", "completed", "expired", "cancelled"
    let amount: Double?
    let message: String?
    let error: String?
}


/**
 * 💳 Payment QR View Model
 * Логика для экрана QR-оплаты
 */
@MainActor
class PaymentQRViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showErrorAlert: Bool = false
    @Published var showSuccessAlert: Bool = false
    
    @Published var paymentId: String?
    @Published var qrCodeDataSBP: String?
    @Published var qrCodeDataSberPay: String?
    @Published var qrCodeDataUniversal: String?
    @Published var qrCodeImageSBP: String?
    @Published var qrCodeImageSberPay: String?
    @Published var qrCodeImageUniversal: String?
    @Published var qrCodeImageCard: String?
    @Published var qrCodeImageApplePay: String?
    @Published var expiresAt: Date?
    @Published var merchantInfo: MerchantInfo?
    
    @Published var selectedMethod: PaymentMethod = .sbp
    
    // MARK: - Private Properties
    
    let tariff: Tariff
    private var cancellables = Set<AnyCancellable>()
    private var autoCheckTimer: Timer?
    
    // ✅ ИСПРАВЛЕНИЕ #6: NetworkManager создается один раз и переиспользуется
    private lazy var networkManager: NetworkManager = {
        print("🔍 PaymentQRViewModel: Создание NetworkManager (lazy)")
        return NetworkManager()
    }()
    
    // ✅ ИСПРАВЛЕНИЕ #6: APIService создается один раз
    private lazy var apiService: APIService = {
        print("🔍 PaymentQRViewModel: Создание APIService (lazy)")
        return APIService(networkManager: networkManager)
    }()
    
    // MARK: - Computed Properties
    
    var currentQRImage: String? {
        switch selectedMethod {
        case .sbp:
            return qrCodeImageSBP
        case .sberpay:
            return qrCodeImageSberPay
        case .card:
            return qrCodeImageCard
        case .alpha, .vtb:
            // Для Альфа и ВТБ используем универсальный QR
            return qrCodeImageUniversal
        }
    }
    
    // MARK: - Init
    
    init(tariff: Tariff) {
        print("🚨 ========== PaymentQRViewModel.init НАЧАЛО ==========")
        print("🔍 Thread: \(Thread.isMainThread ? "Main" : "Background")")
        print("🔍 Stack trace start:")
        Thread.callStackSymbols.prefix(5).forEach { print("   \($0)") }
        
        print("🔍 PaymentQRViewModel.init: Начало инициализации")
        print("   - tariff.id: '\(tariff.id)' (isEmpty: \(tariff.id.isEmpty))")
        print("   - tariff.title: '\(tariff.title)' (isEmpty: \(tariff.title.isEmpty))")
        print("   - tariff.price: '\(tariff.price)' (isEmpty: \(tariff.price.isEmpty))")
        print("   - tariff.period: '\(tariff.period)'")
        print("   - tariff.features.count: \(tariff.features.count)")
        
        // КРИТИЧЕСКАЯ ЗАЩИТА: Используем безопасные значения вместо fatalError
        // Согласно "Pro iOS Testing" - не используем fatalError в production коде
        // ✅ ИСПРАВЛЕНИЕ #9: Улучшенная безопасность создания тарифа
        if tariff.id.isEmpty || tariff.title.isEmpty || tariff.price.isEmpty {
            print("⚠️ PaymentQRViewModel.init: Получен невалидный тариф, используем безопасные значения")
            
            // ✅ Безопасное создание features массива
            let safeFeatures: [String] = {
                if tariff.features.isEmpty {
                    return ["Базовая защита"]
                } else {
                    // Копируем массив для безопасности
                    return Array(tariff.features)
                }
            }()
            
            self.tariff = Tariff(
                id: tariff.id.isEmpty ? "fallback_\(UUID().uuidString)" : tariff.id,
                title: tariff.title.isEmpty ? "Тариф" : tariff.title,
                price: tariff.price.isEmpty ? "0 ₽" : tariff.price,
                period: tariff.period.isEmpty ? "в месяц" : tariff.period,
                features: safeFeatures,
                product: nil,
                isPurchased: false
            )
            print("⚠️ Использован fallback тариф с id: \(self.tariff.id)")
        } else {
            // ✅ ИСПРАВЛЕНИЕ #9: Копируем тариф для безопасности
            print("✅ Тариф валиден, создаем безопасную копию")
            self.tariff = Tariff(
                id: tariff.id,
                title: tariff.title,
                price: tariff.price,
                period: tariff.period,
                features: Array(tariff.features),  // Копия массива
                product: tariff.product,
                isPurchased: tariff.isPurchased
            )
        }
        
        print("🔍 Проверяем AppConfig перед созданием NetworkManager...")
        print("   - AppConfig.apiBaseURL: \(AppConfig.apiBaseURL)")
        print("   - AppConfig.apiBaseURL.isEmpty: \(AppConfig.apiBaseURL.isEmpty)")
        
        print("✅ PaymentQRViewModel.init: Инициализация завершена успешно")
        print("   - id: \(self.tariff.id)")
        print("   - title: \(self.tariff.title)")
        print("   - price: \(self.tariff.price)")
        print("🚨 ========== PaymentQRViewModel.init КОНЕЦ ==========")
    }
    
    // MARK: - Create Payment
    
    /**
     * Создание платежа и получение QR-кодов
     */
    func createPayment() {
        print("🚨 ========== PaymentQRViewModel.createPayment НАЧАЛО ==========")
        print("🔍 Thread: \(Thread.isMainThread ? "Main" : "Background")")
        print("🔍 Timestamp: \(Date())")
        
        isLoading = true
        errorMessage = nil
        
        // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Шаг 1 - Парсинг суммы
        print("📊 ШАГ 1: Парсинг суммы из тарифа")
        print("   - tariff.price (исходная строка): '\(tariff.price)'")
        
        // Парсим сумму из строки (например, "590 ₽" → 590)
        let amountString = tariff.price.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
        print("   - amountString после парсинга: '\(amountString)'")
        
        guard let amount = Double(amountString) else {
            print("❌ ОШИБКА ШАГ 1: Не удалось преобразовать '\(amountString)' в Double")
            self.errorMessage = "Ошибка определения суммы платежа"
            self.showErrorAlert = true
            self.isLoading = false
            return
        }
        print("✅ ШАГ 1 завершен: amount = \(amount)")
        
        // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Шаг 2 - Создание запроса
        print("📊 ШАГ 2: Создание запроса CreateQRPaymentRequest")
        print("   - amount: \(amount)")
        print("   - currency: RUB")
        print("   - description: '\(tariff.title)'")
        print("   - tariffId: '\(tariff.id)'")
        
        // Создаем запрос
        let request = CreateQRPaymentRequest(
            amount: amount,
            currency: "RUB",
            description: tariff.title,
            tariffId: tariff.id
        )
        print("✅ ШАГ 2 завершен: CreateQRPaymentRequest создан")
        
        // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Шаг 3 - Проверка конфигурации
        print("📊 ШАГ 3: Проверка конфигурации API")
        print("   - AppConfig.apiBaseURL: '\(AppConfig.apiBaseURL)'")
        print("   - AppConfig.apiBaseURL.isEmpty: \(AppConfig.apiBaseURL.isEmpty)")
        print("   - AppConfig.isAPIURLValid(): \(AppConfig.isAPIURLValid())")
        
        // Отправляем запрос на backend
        // ✅ ИСПРАВЛЕНИЕ #6: Используем lazy properties вместо создания новых экземпляров
        print("🔍 PaymentQRViewModel.createPayment: Использование существующих NetworkManager и APIService")
        
        // ✅ Проверяем валидность API URL перед использованием
        guard AppConfig.isAPIURLValid() else {
            print("❌ ОШИБКА ШАГ 3: API URL невалиден!")
            print("   - apiBaseURL: '\(AppConfig.apiBaseURL)'")
            Task { @MainActor in
                self.isLoading = false
                self.errorMessage = "Конфигурация API неверна. Обратитесь к разработчикам."
                self.showErrorAlert = true
            }
            return
        }
        
        print("✅ ШАГ 3 завершен: API URL валиден")
        print("✅ NetworkManager и APIService готовы к использованию (lazy)")
        
        // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Шаг 4 - Отправка запроса
        print("📊 ШАГ 4: Отправка запроса на создание платежа")
        print("   - Endpoint: POST \(AppConfig.apiBaseURL)/payments/qr/create")
        print("   - Request body:")
        print("     * amount: \(request.amount)")
        print("     * currency: \(request.currency)")
        print("     * description: '\(request.description)'")
        print("     * tariffId: '\(request.tariffId ?? "nil")'")
        print("   - Отправляем запрос...")
        
        apiService.createQRPayment(request: request) { [weak self] result in
            guard let self = self else {
                print("❌ PaymentQRViewModel.createPayment: self is nil в completion handler")
                return
            }
            
            Task { @MainActor [weak self] in
                guard let self = self else {
                    print("❌ PaymentQRViewModel.createPayment: self is nil в Task")
                    return
                }
                
                self.isLoading = false
                
                switch result {
                case .success(let response):
                    // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Шаг 5 - Обработка успешного ответа
                    print("✅ ШАГ 4 завершен: Получен успешный ответ от сервера")
                    print("📊 ШАГ 5: Обработка ответа от сервера")
                    print("   - payment_id: '\(response.paymentId)'")
                    print("   - payment_id.isEmpty: \(response.paymentId.isEmpty)")
                    print("   - qrCode (первые 50 символов): '\(String(response.qrCode.prefix(50)))...'")
                    print("   - qrCode длина: \(response.qrCode.count) символов")
                    print("   - qrCode.isEmpty: \(response.qrCode.isEmpty)")
                    print("   - expiresAt: \(response.expiresAt)")
                    print("   - status: '\(response.status)'")
                    print("   - amount: \(response.amount)")
                    print("   - currency: '\(response.currency)'")
                    
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверяем что qrCode валидный URL
                    guard !response.qrCode.isEmpty else {
                        print("❌ ОШИБКА ШАГ 5: qrCode пустой в ответе от сервера!")
                        self.errorMessage = "Не удалось получить QR-код. Сервер вернул пустой ответ. Попробуйте еще раз или обратитесь в поддержку."
                        self.showErrorAlert = true
                        return
                    }
                    print("✅ ШАГ 5.1: qrCode не пустой - продолжаем валидацию")
                    
                    // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Проверка формата QR кода
                    print("🔍 Проверка формата QR кода:")
                    let isURL = URL(string: response.qrCode) != nil
                    let isBase64 = response.qrCode.hasPrefix("data:image/") || response.qrCode.hasPrefix("iVBORw0KGgo") // PNG base64
                    print("   - isURL (валидный URL): \(isURL)")
                    print("   - isBase64 (base64 изображение): \(isBase64)")
                    
                    if !isURL && !isBase64 {
                        print("⚠️ QR код не является URL или base64 изображением, но попробуем загрузить")
                        print("   - Первые 100 символов: '\(String(response.qrCode.prefix(100)))'")
                    } else {
                        print("✅ Формат QR кода валиден (\(isURL ? "URL" : "base64"))")
                    }
                    
                    // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Сохранение данных
                    print("📊 ШАГ 6: Сохранение данных платежа")
                    
                    // Сохраняем данные платежа
                    self.paymentId = response.paymentId
                    self.qrCodeImageSBP = response.qrCode
                    self.qrCodeImageSberPay = response.qrCode
                    self.qrCodeImageUniversal = response.qrCode
                    self.expiresAt = response.expiresAt
                    
                    print("✅ ШАГ 6 завершен: Данные сохранены")
                    print("   - paymentId сохранен: '\(self.paymentId ?? "nil")'")
                    print("   - qrCodeImageSBP сохранен: \(self.qrCodeImageSBP != nil && !(self.qrCodeImageSBP?.isEmpty ?? true))")
                    print("   - qrCodeImageSberPay сохранен: \(self.qrCodeImageSberPay != nil && !(self.qrCodeImageSberPay?.isEmpty ?? true))")
                    print("   - qrCodeImageUniversal сохранен: \(self.qrCodeImageUniversal != nil && !(self.qrCodeImageUniversal?.isEmpty ?? true))")
                    print("   - expiresAt сохранен: \(self.expiresAt != nil ? "\(self.expiresAt!)" : "nil")")
                    
                    // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Проверка доступности currentQRImage
                    print("📊 ШАГ 7: Проверка доступности currentQRImage")
                    print("   - selectedMethod: \(self.selectedMethod.rawValue)")
                    print("   - currentQRImage != nil: \(self.currentQRImage != nil)")
                    if let currentQR = self.currentQRImage {
                        print("   - currentQRImage.isEmpty: \(currentQR.isEmpty)")
                        print("   - currentQRImage (первые 50 символов): '\(String(currentQR.prefix(50)))...'")
                    }
                    print("✅ ========== QR-коды успешно сохранены и доступны ==========")
                    
                case .failure(let error):
                    // ✅ ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Обработка ошибки
                    print("❌ ОШИБКА ШАГ 4: Запрос не выполнен")
                    print("❌ ========== Ошибка создания платежа ==========")
                    print("   - Error type: \(type(of: error))")
                    print("   - Error description: \(error.localizedDescription)")
                    print("   - Error localizedDescription: '\(error.localizedDescription)'")
                    if let nsError = error as NSError? {
                        print("   - NSError domain: '\(nsError.domain)'")
                        print("   - NSError code: \(nsError.code)")
                        print("   - NSError userInfo: \(nsError.userInfo)")
                    }
                    
                    // Более подробное сообщение об ошибке
                    let detailedErrorMessage: String
                    if let apiError = error as? APIError {
                        switch apiError {
                        case .networkError(let msg):
                            detailedErrorMessage = "Проблема с подключением к интернету. Проверьте соединение и попробуйте снова.\n\n\(msg)"
                        case .serverError(let msg):
                            detailedErrorMessage = "Ошибка сервера. Попробуйте позже или обратитесь в поддержку.\n\n\(msg)"
                        case .invalidURL:
                            detailedErrorMessage = "Ошибка конфигурации. Обратитесь к разработчикам."
                        default:
                            detailedErrorMessage = "Ошибка: \(error.localizedDescription)\n\nПопробуйте еще раз или обратитесь в поддержку."
                        }
                    } else {
                        detailedErrorMessage = "Ошибка создания платежа: \(error.localizedDescription)\n\nПопробуйте еще раз или обратитесь в поддержку."
                    }
                    
                    self.errorMessage = detailedErrorMessage
                    self.showErrorAlert = true
                    print("❌ ========== Конец ошибки ==========")
                }
            }
        }
    }
    
    // MARK: - Check Payment Status
    
    /**
     * Проверка статуса оплаты
     */
    func checkPaymentStatus() {
        print("🔍 ========== checkPaymentStatus НАЧАЛО ==========")
        print("   - paymentId: \(paymentId ?? "nil")")
        print("   - isLoading: \(isLoading)")
        print("   - currentQRImage: \(currentQRImage != nil ? "есть" : "nil")")
        print("   - API URL: \(AppConfig.apiBaseURL)")
        
        // ✅ ИСПРАВЛЕНИЕ: Более подробная проверка и понятное сообщение
        guard let paymentId = paymentId else {
            print("❌ checkPaymentStatus: paymentId == nil, платеж еще не создан")
            print("   - QR код может еще загружаться, подождите...")
            errorMessage = "QR-код еще загружается. Пожалуйста, подождите несколько секунд и попробуйте снова."
            showErrorAlert = true
            print("🔍 ========== checkPaymentStatus КОНЕЦ (paymentId == nil) ==========")
            return
        }
        
        // Дополнительная проверка
        guard !paymentId.isEmpty else {
            print("❌ checkPaymentStatus: paymentId пустой")
            errorMessage = "Платеж не был создан. Попробуйте перезагрузить страницу."
            showErrorAlert = true
            print("🔍 ========== checkPaymentStatus КОНЕЦ (paymentId пустой) ==========")
            return
        }
        
        print("✅ checkPaymentStatus: Начинаем проверку статуса для paymentId: \(paymentId)")
        
        isLoading = true
        errorMessage = nil
        
        print("🔍 Отправляем запрос на: /api/payments/qr/status/\(paymentId)")
        
        apiService.checkQRPaymentStatus(paymentId: paymentId) { [weak self] result in
            guard let self = self else {
                print("❌ checkPaymentStatus: self is nil в completion handler")
                return
            }
            
            Task { @MainActor [weak self] in
                guard let self = self else {
                    print("❌ checkPaymentStatus: self is nil в Task")
                    return
                }
                
                self.isLoading = false
                
                switch result {
                case .success(let response):
                    print("✅ ========== Ответ от сервера получен ==========")
                    print("   - paymentId: \(response.paymentId)")
                    print("   - status: \(response.status)")
                    print("   - amount: \(response.amount)")
                    print("   - currency: \(response.currency)")
                    if let completedAt = response.completedAt {
                        print("   - completedAt: \(completedAt)")
                    }
                    
                    if response.status == "completed" {
                        // Платеж завершен!
                        print("✅✅✅ ПЛАТЕЖ ЗАВЕРШЕН! ✅✅✅")
                        self.showSuccessAlert = true
                        self.stopAutoCheck()
                        
                        // Отправляем Firebase Analytics событие
                        print("✅ Purchase completed: \(self.tariff.title) - \(response.amount) \(response.currency) via qr_code")
                        print("🔍 ========== checkPaymentStatus КОНЕЦ (completed) ==========")
                    } else if response.status == "expired" {
                        print("⚠️ Платеж истек")
                        self.errorMessage = "Срок действия платежа истек. Пожалуйста, создайте новый платеж."
                        self.showErrorAlert = true
                        self.stopAutoCheck()
                        print("🔍 ========== checkPaymentStatus КОНЕЦ (expired) ==========")
                    } else if response.status == "cancelled" {
                        print("⚠️ Платеж отменен")
                        self.errorMessage = "Платеж был отменен. Вы можете создать новый платеж."
                        self.showErrorAlert = true
                        print("🔍 ========== checkPaymentStatus КОНЕЦ (cancelled) ==========")
                    } else {
                        // Платеж еще в ожидании (pending)
                        print("⏳ Платеж ожидает оплаты (status: \(response.status))")
                        print("   - Сообщение пользователю не показываем, так как это нормально")
                        print("🔍 ========== checkPaymentStatus КОНЕЦ (pending) ==========")
                    }
                    
                case .failure(let error):
                    print("❌ ========== Ошибка проверки статуса ==========")
                    print("   - Error type: \(type(of: error))")
                    print("   - Error description: \(error.localizedDescription)")
                    
                    // Более подробное сообщение об ошибке
                    let detailedErrorMessage: String
                    if let apiError = error as? APIError {
                        switch apiError {
                        case .networkError(let msg):
                            detailedErrorMessage = "Проблема с подключением к интернету.\n\n\(msg)\n\nПроверьте соединение и попробуйте снова."
                        case .serverError(let msg):
                            detailedErrorMessage = "Ошибка сервера.\n\n\(msg)\n\nПопробуйте позже."
                        case .httpError(let statusCode, _):
                            if statusCode == 404 {
                                detailedErrorMessage = "Платеж не найден. Возможно, истек срок действия.\n\nПопробуйте создать новый платеж."
                            } else {
                                detailedErrorMessage = "Ошибка сервера (код \(statusCode)). Попробуйте позже."
                            }
                        case .invalidURL:
                            detailedErrorMessage = "Ошибка конфигурации. Обратитесь к разработчикам."
                        default:
                            detailedErrorMessage = "Ошибка проверки статуса: \(error.localizedDescription)\n\nПопробуйте еще раз."
                        }
                    } else {
                        detailedErrorMessage = "Ошибка проверки статуса: \(error.localizedDescription)\n\nПопробуйте еще раз."
                    }
                    
                    self.errorMessage = detailedErrorMessage
                    self.showErrorAlert = true
                    print("❌ ========== Конец ошибки ==========")
                    print("🔍 ========== checkPaymentStatus КОНЕЦ (error) ==========")
                }
            }
        }
    }
    
    // MARK: - Auto Check
    
    /**
     * Запуск автоматической проверки каждые 30 секунд
     */
    func startAutoCheck() {
        autoCheckTimer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            self?.checkPaymentStatus()
        }
    }
    
    /**
     * Остановка автоматической проверки
     */
    func stopAutoCheck() {
        autoCheckTimer?.invalidate()
        autoCheckTimer = nil
    }
    
    // MARK: - Helpers
    
    /**
     * Получение ID семьи (анонимного)
     */
    private func getFamilyId() -> String {
        // В реальном приложении это будет ID из UserDefaults или KeyChain
        // Пока возвращаем UUID устройства
        return UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
    }
}
