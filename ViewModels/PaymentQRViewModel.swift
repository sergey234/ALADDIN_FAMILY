import Foundation
import Combine

/**
 * 💳 Payment QR View Model
 * Логика для экрана QR-оплаты
 */

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
    @Published var expiresAt: Date?
    @Published var merchantInfo: MerchantInfo?
    
    @Published var selectedMethod: PaymentMethod = .sbp
    
    // MARK: - Private Properties
    
    private let tariff: Tariff
    private var cancellables = Set<AnyCancellable>()
    private var autoCheckTimer: Timer?
    
    // MARK: - Computed Properties
    
    var currentQRImage: String? {
        switch selectedMethod {
        case .sbp:
            return qrCodeImageSBP
        case .sberpay:
            return qrCodeImageSberPay
        case .universal:
            return qrCodeImageUniversal
        }
    }
    
    // MARK: - Init
    
    init(tariff: Tariff) {
        self.tariff = tariff
    }
    
    // MARK: - Create Payment
    
    /**
     * Создание платежа и получение QR-кодов
     */
    func createPayment() {
        isLoading = true
        errorMessage = nil
        
        // Парсим сумму из строки (например, "590 ₽" → 590)
        let amountString = tariff.price.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
        guard let amount = Double(amountString) else {
            self.errorMessage = "Ошибка определения суммы платежа"
            self.showErrorAlert = true
            self.isLoading = false
            return
        }
        
        // Создаем запрос
        let request = CreateQRPaymentRequest(
            family_id: getFamilyId(),
            tariff: tariff.title,
            amount: amount,
            payment_method: "sbp"
        )
        
        // Отправляем запрос на backend
        APIService.shared.createQRPayment(request: request)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                
                if case .failure(let error) = completion {
                    self?.errorMessage = error.errorDescription
                    self?.showErrorAlert = true
                    print("❌ Ошибка создания платежа: \(error)")
                }
            } receiveValue: { [weak self] response in
                // Сохраняем данные платежа
                self?.paymentId = response.payment_id
                self?.qrCodeImageSBP = response.qr_codes?.sbp
                self?.qrCodeImageSberPay = response.qr_codes?.sberpay
                self?.qrCodeImageUniversal = response.qr_codes?.universal
                
                if let expiresAtString = response.expires_at {
                    self?.expiresAt = ISO8601DateFormatter().date(from: expiresAtString)
                }
                
                if let merchantData = response.merchant_info {
                    self?.merchantInfo = MerchantInfo(
                        name: merchantData.name,
                        card: merchantData.card,
                        phone: merchantData.phone
                    )
                }
                
                print("✅ QR-коды получены: payment_id=\(response.payment_id)")
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Check Payment Status
    
    /**
     * Проверка статуса оплаты
     */
    func checkPaymentStatus() {
        guard let paymentId = paymentId else {
            errorMessage = "ID платежа не найден"
            showErrorAlert = true
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        APIService.shared.checkQRPaymentStatus(paymentId: paymentId)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                
                if case .failure(let error) = completion {
                    self?.errorMessage = error.errorDescription
                    self?.showErrorAlert = true
                    print("❌ Ошибка проверки статуса: \(error)")
                }
            } receiveValue: { [weak self] response in
                print("ℹ️ Статус платежа: \(response.status)")
                
                if response.status == "completed" {
                    // Платеж завершен!
                    self?.showSuccessAlert = true
                    self?.stopAutoCheck()
                    
                    // Отправляем Firebase Analytics событие
                    AnalyticsManager.shared.logPurchase(
                        tariff: self?.tariff.title ?? "Unknown",
                        amount: response.amount ?? 0.0,
                        currency: "RUB",
                        paymentMethod: "qr_code"
                    )
                } else if response.status == "expired" {
                    self?.errorMessage = "Срок действия платежа истек"
                    self?.showErrorAlert = true
                    self?.stopAutoCheck()
                } else {
                    // Платеж еще в ожидании
                    print("⏳ Платеж ожидает оплаты")
                }
            }
            .store(in: &cancellables)
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

// MARK: - API Models

struct CreateQRPaymentRequest: Codable {
    let family_id: String
    let tariff: String
    let amount: Double
    let payment_method: String
}

struct CreateQRPaymentResponse: Codable {
    let success: Bool
    let payment_id: String
    let qr_codes: QRCodes?
    let merchant_info: MerchantInfoAPI?
    let expires_at: String?
    let error: String?
}

struct QRCodes: Codable {
    let sbp: String?
    let sberpay: String?
    let universal: String?
}

struct MerchantInfoAPI: Codable {
    let name: String
    let card: String
    let phone: String
}

struct CheckQRPaymentStatusResponse: Codable {
    let success: Bool
    let payment_id: String
    let status: String  // "pending", "completed", "expired", "cancelled"
    let amount: Double?
    let message: String?
    let error: String?
}

// MARK: - API Service Extension

extension APIService {
    
    /**
     * Создание QR-платежа
     */
    func createQRPayment(request: CreateQRPaymentRequest) -> AnyPublisher<CreateQRPaymentResponse, APIError> {
        guard let url = URL(string: AppConfig.baseURL + "/payments/qr/create") else {
            return Fail(error: APIError.invalidURL).eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.addValue("Bearer \(AppConfig.apiKey)", forHTTPHeaderField: "Authorization")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: APIError.encodingFailed(error)).eraseToAnyPublisher()
        }
        
        return NetworkManager.shared.session.dataTaskPublisher(for: urlRequest)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw APIError.httpError(statusCode: httpResponse.statusCode, data: data)
                }
                return data
            }
            .decode(type: CreateQRPaymentResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else if error is DecodingError {
                    return APIError.decodingFailed(error)
                } else {
                    return APIError.unknown(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    /**
     * Проверка статуса QR-платежа
     */
    func checkQRPaymentStatus(paymentId: String) -> AnyPublisher<CheckQRPaymentStatusResponse, APIError> {
        guard let url = URL(string: AppConfig.baseURL + "/payments/qr/status/\(paymentId)") else {
            return Fail(error: APIError.invalidURL).eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.addValue("Bearer \(AppConfig.apiKey)", forHTTPHeaderField: "Authorization")
        
        return NetworkManager.shared.session.dataTaskPublisher(for: urlRequest)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw APIError.httpError(statusCode: httpResponse.statusCode, data: data)
                }
                return data
            }
            .decode(type: CheckQRPaymentStatusResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else if error is DecodingError {
                    return APIError.decodingFailed(error)
                } else {
                    return APIError.unknown(error)
                }
            }
            .eraseToAnyPublisher()
    }
}



