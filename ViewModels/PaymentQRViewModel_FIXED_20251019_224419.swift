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
    case universal = "universal"
    case card = "card"
    case applePay = "applePay"
    
    var displayName: String {
        switch self {
        case .sbp: return "СБП"
        case .sberpay: return "СберPay"
        case .universal: return "Универсальный"
        case .card: return "Банковская карта"
        case .applePay: return "Apple Pay"
        }
    }
}

struct PaymentMethodInfo {
    let id: String
    let name: String
    let type: String
}

// MARK: - API Models
struct CreateQRPaymentRequest: Codable {
    let family_id: String
    let tariff: String
    let amount: Double
    let payment_method: String
}

struct CreateQRPaymentResponse: Codable {
    enum CodingKeys: String, CodingKey {
        case payment_id, qr_codes, expires_at, merchant_info
    }
    let payment_id: String
    let qr_codes: QRCodeData?
    let expires_at: String?
    let merchant_info: MerchantInfo?
}

struct QRCodeData: Codable {
    let sbp: String?
    let sberpay: String?
    let universal: String?
}

struct CheckQRPaymentStatusResponse: Codable {
    let payment_id: String
    let status: String
    let amount: Double?
    let currency: String?
    let merchant_info: MerchantInfoAPI?
    let expires_at: String?
    let error: String?
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
        case .card:
            return qrCodeImageCard
        case .applePay:
            return qrCodeImageApplePay
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
        APIService(networkManager: NetworkManager()).createQRPayment(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
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
                            id: merchantData.id,
                            name: merchantData.name,
                            address: "",
                            phone: merchantData.phone
                        )
                    }
                    
                    print("✅ QR-коды получены: payment_id=\(response.payment_id)")
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    self?.showErrorAlert = true
                    print("❌ Ошибка создания платежа: \(error)")
                }
            }
        }
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
        
        APIService(networkManager: NetworkManager()).checkQRPaymentStatus(paymentId: paymentId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    print("ℹ️ Статус платежа: \(response.status)")
                    
                    if response.status == "completed" {
                        // Платеж завершен!
                        self?.showSuccessAlert = true
                        self?.stopAutoCheck()
                        
                        // Отправляем Firebase Analytics событие
                        print("✅ Purchase completed: \(self?.tariff.title ?? "Unknown") - \(response.amount ?? 0.0) \(response.currency ?? "RUB") via qr_code")
                    } else if response.status == "expired" {
                        self?.errorMessage = "Срок действия платежа истек"
                        self?.showErrorAlert = true
                        self?.stopAutoCheck()
                    } else {
                        // Платеж еще в ожидании
                        print("⏳ Платеж ожидает оплаты")
                    }
                    
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    self?.showErrorAlert = true
                    print("❌ Ошибка проверки статуса: \(error)")
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
