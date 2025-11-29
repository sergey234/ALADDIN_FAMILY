    // MARK: - Published Properties
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showErrorAlert: Bool = false
    @Published var showSuccessAlert: Bool = false
    @Published var creationError: Bool = false
    
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

    private var autoCheckTimer: Timer?
    private let isoFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()

    private func localized(_ key: String) -> String {
        LocalizationManager().localized(key)
    }
    
    private func localized(_ key: String, _ arguments: CVarArg...) -> String {
        let manager = LocalizationManager()
        let format = manager.localized(key)
        return String(format: format, locale: manager.locale, arguments: arguments)
    }
    
    private func isoString(_ date: Date?) -> String {
