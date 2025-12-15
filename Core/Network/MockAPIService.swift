import Foundation

/**
 * 🧪 Mock API Service
 * Тестовые данные для разработки и тестирования без реального сервера
 * Используется только в DEBUG режиме
 */

class MockAPIService: APIService {
    
    // Singleton - используем другое имя, чтобы избежать конфликта с APIService.shared
    private static let _mockShared: MockAPIService = {
        let networkManager = NetworkManager()
        return MockAPIService(networkManager: networkManager)
    }()
    
    // Computed property для доступа к singleton
    static var mockShared: MockAPIService {
        return _mockShared
    }
    
    override init(networkManager: NetworkManager) {
        super.init(networkManager: networkManager)
    }
    
    // Для тестов - создание экземпляра напрямую
    #if DEBUG
    static func createForTesting(networkManager: NetworkManager = NetworkManager()) -> MockAPIService {
        return MockAPIService(networkManager: networkManager)
    }
    #endif
    
    // MARK: - Helper: Симуляция задержки сети
    
    private func simulateNetworkDelay(completion: @escaping () -> Void) {
        // Симулируем задержку сети (0.5-1.5 секунды)
        let delay = Double.random(in: 0.5...1.5)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            completion()
        }
    }
    
    // MARK: - Auth API
    
    override func login(email: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        simulateNetworkDelay {
            // Mock успешный вход
            let response = LoginResponse(
                token: "mock_token_\(UUID().uuidString)",
                userId: "user_mock_123",
                expiresAt: Date().addingTimeInterval(3600) // 1 час
            )
            
            // Сохраняем токен
            AppConfig.authToken = response.token
            
            completion(.success(response))
        }
    }
    
    override func logout(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        simulateNetworkDelay {
            // Очищаем токен
            AppConfig.authToken = nil
            
            let response = APIResponse<Bool>(
                success: true,
                data: true,
                message: "Logged out successfully",
                error: nil
            )
            completion(.success(response))
        }
    }
    
    // MARK: - User API
    
    override func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
        simulateNetworkDelay {
            let profile = UserProfile(
                id: "user_mock_123",
                name: "Test User",
                email: "test@aladdin.family",
                phone: "+7 (999) 123-45-67",
                registrationDate: "2025-01-01",
                subscriptionType: "family",
                subscriptionEndDate: ISO8601DateFormatter().string(from: Date().addingTimeInterval(30 * 24 * 60 * 60)), // 30 дней
                threatsBlocked: 47,
                familyMembers: 4,
                devices: 8
            )
            completion(.success(profile))
        }
    }
    
    override func deleteAccount(confirmationCode: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        simulateNetworkDelay {
            // Проверяем код подтверждения
            if confirmationCode.uppercased() == "УДАЛИТЬ" || confirmationCode.uppercased() == "DELETE" {
                // Очищаем токен
                AppConfig.authToken = nil
                
                let response = APIResponse<Bool>(
                    success: true,
                    data: true,
                    message: "Account deleted successfully",
                    error: nil
                )
                completion(.success(response))
            } else {
                // Ошибка подтверждения
                let error = NetworkError.badRequest("Invalid confirmation code. Please type 'УДАЛИТЬ' or 'DELETE'")
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Family API
    
    override func getFamilyMembers(completion: @escaping (Result<[FamilyMemberResponse], Error>) -> Void) {
        simulateNetworkDelay {
            let members = [
                FamilyMemberResponse(
                    id: "member_1",
                    name: "Родитель",
                    role: "parent",
                    avatar: "👨",
                    status: "protected",
                    threatsBlocked: 15,
                    lastActive: "2 минуты назад",
                    devices: 2
                ),
                FamilyMemberResponse(
                    id: "member_2",
                    name: "Ребенок",
                    role: "child",
                    avatar: "👶",
                    status: "protected",
                    threatsBlocked: 8,
                    lastActive: "5 минут назад",
                    devices: 1
                ),
                FamilyMemberResponse(
                    id: "member_3",
                    name: "Подросток",
                    role: "teenager",
                    avatar: "🧑",
                    status: "warning",
                    threatsBlocked: 3,
                    lastActive: "10 минут назад",
                    devices: 1
                ),
                FamilyMemberResponse(
                    id: "member_4",
                    name: "Пожилой",
                    role: "elderly",
                    avatar: "👴",
                    status: "protected",
                    threatsBlocked: 12,
                    lastActive: "1 час назад",
                    devices: 1
                )
            ]
            completion(.success(members))
        }
    }
    
    override func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
        simulateNetworkDelay {
            let stats = FamilyStatsResponse(
                totalMembers: 4,
                totalDevices: 8,
                totalThreats: 47,
                protectionLevel: 95,
                familyStatus: "active",
                familyStatusMessage: "Все члены семьи защищены"
            )
            completion(.success(stats))
        }
    }
    
    // MARK: - Subscription API
    
    override func getTariffs(completion: @escaping (Result<[TariffResponse], Error>) -> Void) {
        simulateNetworkDelay {
            let tariffs = [
                TariffResponse(
                    id: "free",
                    name: "Free",
                    price: 0,
                    period: "month",
                    features: [
                        "Базовая защита",
                        "VPN (ограниченный)",
                        "Родительский контроль (базовый)"
                    ],
                    isRecommended: false
                ),
                TariffResponse(
                    id: "personal",
                    name: "Personal",
                    price: 299,
                    period: "month",
                    features: [
                        "Полная защита",
                        "VPN без ограничений",
                        "Родительский контроль",
                        "AI помощник",
                        "Аналитика угроз"
                    ],
                    isRecommended: false
                ),
                TariffResponse(
                    id: "family",
                    name: "Family",
                    price: 499,
                    period: "month",
                    features: [
                        "Все функции Personal",
                        "До 10 членов семьи",
                        "Управление устройствами",
                        "Семейный чат",
                        "Приоритетная поддержка"
                    ],
                    isRecommended: true
                ),
                TariffResponse(
                    id: "premium",
                    name: "Premium",
                    price: 799,
                    period: "month",
                    features: [
                        "Все функции Family",
                        "Неограниченное количество устройств",
                        "Персональный менеджер",
                        "Расширенная аналитика",
                        "Ранний доступ к новым функциям"
                    ],
                    isRecommended: false
                )
            ]
            completion(.success(tariffs))
        }
    }
    
    override func activateSubscriptionCode(code: String, completion: @escaping (Result<ActivationCodeResponse, Error>) -> Void) {
        simulateNetworkDelay {
            let response = ActivationCodeResponse(
                status: "activated",
                message: "Подписка активирована",
                planName: "Family",
                expiresAt: ISO8601DateFormatter().string(from: Date().addingTimeInterval(30 * 24 * 60 * 60)),
                familyId: "mock_family_id"
            )
            completion(.success(response))
        }
    }
    
    override func createQRPayment(request: CreateQRPaymentRequest, completion: @escaping (Result<CreateQRPaymentResponse, Error>) -> Void) {
        simulateNetworkDelay {
            // Mock QR-код (в реальности это будет base64 изображение)
            let mockQRCode = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
            // Логируем период подписки для отладки
            if let periodMonths = request.periodMonths {
                print("📦 Mock API: Создание QR-платежа с периодом \(periodMonths) месяцев")
            }
            
            let response = CreateQRPaymentResponse(
                paymentId: "payment_mock_\(UUID().uuidString)",
                qrCode: mockQRCode,
                amount: request.amount,
                currency: request.currency,
                expiresAt: Date().addingTimeInterval(15 * 60), // 15 минут
                status: "pending"
            )
            completion(.success(response))
        }
    }
    
    override func checkQRPaymentStatus(paymentId: String, completion: @escaping (Result<CheckQRPaymentStatusResponse, Error>) -> Void) {
        simulateNetworkDelay {
            // Mock статус оплаты (в реальности проверяется на сервере)
            let response = CheckQRPaymentStatusResponse(
                paymentId: paymentId,
                status: "pending", // "pending", "completed", "failed", "expired"
                amount: 499.0,
                currency: "RUB",
                completedAt: nil
            )
            completion(.success(response))
        }
    }
    
    // MARK: - VPN API
    
    override func getVPNStatus(completion: @escaping (Result<NetworkProtectionStatusResponse, Error>) -> Void) {
        simulateNetworkDelay {
            let status = NetworkProtectionStatusResponse(
                isConnected: false,
                serverLocation: "Германия",
                ipAddress: "192.168.1.1",
                ping: 45,
                downloadSpeed: "45 Мбит/с",
                uploadSpeed: "12 Мбит/с",
                sessionTime: "0:00",
                threatsBlocked: 0
            )
            completion(.success(status))
        }
    }
    
    override func connectVPN(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        simulateNetworkDelay {
            let response = APIResponse<Bool>(
                success: true,
                data: true,
                message: "VPN connected successfully",
                error: nil
            )
            completion(.success(response))
        }
    }
    
    override func disconnectVPN(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        simulateNetworkDelay {
            let response = APIResponse<Bool>(
                success: true,
                data: true,
                message: "VPN disconnected successfully",
                error: nil
            )
            completion(.success(response))
        }
    }
    
    override func getVPNServers(completion: @escaping (Result<[NetworkProtectionServer], Error>) -> Void) {
        simulateNetworkDelay {
            let servers = [
                NetworkProtectionServer(
                    id: "server_1",
                    country: "Германия",
                    city: "Берлин",
                    flag: "🇩🇪",
                    ping: 45,
                    load: 30,
                    status: .optimal
                ),
                NetworkProtectionServer(
                    id: "server_2",
                    country: "США",
                    city: "Нью-Йорк",
                    flag: "🇺🇸",
                    ping: 120,
                    load: 50,
                    status: .optimal
                ),
                NetworkProtectionServer(
                    id: "server_3",
                    country: "Япония",
                    city: "Токио",
                    flag: "🇯🇵",
                    ping: 200,
                    load: 70,
                    status: .loaded
                ),
                NetworkProtectionServer(
                    id: "server_4",
                    country: "Россия",
                    city: "Москва",
                    flag: "🇷🇺",
                    ping: 15,
                    load: 20,
                    status: .optimal
                )
            ]
            completion(.success(servers))
        }
    }
    
    // MARK: - Analytics API
    
    override func getAnalytics(period: String, completion: @escaping (Result<AnalyticsResponse, Error>) -> Void) {
        simulateNetworkDelay {
            let analytics = AnalyticsResponse(
                period: period,
                threatsDetected: 47,
                threatsBlocked: 45,
                itemsScanned: 1250,
                protectionLevel: 95,
                topThreats: [
                    ThreatItem(
                        id: "threat_1",
                        name: "Фишинг",
                        count: 15,
                        icon: "🎣",
                        severity: "high"
                    ),
                    ThreatItem(
                        id: "threat_2",
                        name: "Вредоносное ПО",
                        count: 12,
                        icon: "🦠",
                        severity: "critical"
                    ),
                    ThreatItem(
                        id: "threat_3",
                        name: "Подозрительный сайт",
                        count: 10,
                        icon: "⚠️",
                        severity: "medium"
                    )
                ],
                threatsByType: [
                    ThreatByType(type: "web", count: 25, percentage: 53.2),
                    ThreatByType(type: "app", count: 12, percentage: 25.5),
                    ThreatByType(type: "network", count: 8, percentage: 17.0),
                    ThreatByType(type: "file", count: 2, percentage: 4.3)
                ]
            )
            completion(.success(analytics))
        }
    }
    
    override func getTopThreats(completion: @escaping (Result<[ThreatItem], Error>) -> Void) {
        simulateNetworkDelay {
            let threats = [
                ThreatItem(
                    id: "threat_1",
                    name: "Фишинг",
                    count: 15,
                    icon: "🎣",
                    severity: "high"
                ),
                ThreatItem(
                    id: "threat_2",
                    name: "Вредоносное ПО",
                    count: 12,
                    icon: "🦠",
                    severity: "critical"
                ),
                ThreatItem(
                    id: "threat_3",
                    name: "Подозрительный сайт",
                    count: 10,
                    icon: "⚠️",
                    severity: "medium"
                ),
                ThreatItem(
                    id: "threat_4",
                    name: "Рекламное ПО",
                    count: 8,
                    icon: "📢",
                    severity: "low"
                ),
                ThreatItem(
                    id: "threat_5",
                    name: "Трекеры",
                    count: 5,
                    icon: "👁️",
                    severity: "low"
                )
            ]
            completion(.success(threats))
        }
    }
    
    // MARK: - Notifications API
    
    override func getNotifications(completion: @escaping (Result<[NotificationResponse], Error>) -> Void) {
        simulateNetworkDelay {
            let notifications = [
                NotificationResponse(
                    id: "notif_1",
                    icon: "🛡️",
                    title: "Угроза заблокирована",
                    message: "Система защиты остановила подозрительную активность",
                    timestamp: Date().addingTimeInterval(-300), // 5 минут назад
                    isRead: false,
                    type: "threat",
                    priority: "high",
                    actionRequired: false,
                    actionUrl: nil,
                    metadata: ["category": "security"]
                ),
                NotificationResponse(
                    id: "notif_2",
                    icon: "✅",
                    title: "Подписка активирована",
                    message: "Подписка Family Pro успешно подключена",
                    timestamp: Date().addingTimeInterval(-3600), // 1 час назад
                    isRead: true,
                    type: "success",
                    priority: "medium",
                    actionRequired: false,
                    actionUrl: nil,
                    metadata: ["tariff": "family_pro"]
                ),
                NotificationResponse(
                    id: "notif_3",
                    icon: "🎁",
                    title: "Реферальная награда",
                    message: "Вы получили дополнительные дни защиты за приглашение друга",
                    timestamp: Date().addingTimeInterval(-7200), // 2 часа назад
                    isRead: true,
                    type: "info",
                    priority: "low",
                    actionRequired: false,
                    actionUrl: nil,
                    metadata: ["reward": "7_days"]
                )
            ]
            completion(.success(notifications))
        }
    }
    
    // MARK: - Family Registration (через NetworkManager extension)
    
    // Эти методы определены в NetworkManager extension
    // Для Mock API мы создаем расширение NetworkManager с mock реализацией
    
}

// MARK: - NetworkManager Extension для Mock API

extension NetworkManager {
    
    /**
     * Mock реализация createFamily для тестирования
     * Используется только когда включен Mock API
     */
    func createFamilyMock(request: CreateFamilyRequest, completion: @escaping (Result<CreateFamilyResponse, Error>) -> Void) {
        // Симулируем задержку сети
        let delay = Double.random(in: 0.5...1.5)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            let response = CreateFamilyResponse(
                success: true,
                family_id: "family_mock_\(UUID().uuidString)",
                recovery_code: "RECOVERY-\(Int.random(in: 1000...9999))",
                members: [
                    FamilyMemberResponse(
                        id: "member_\(UUID().uuidString)",
                        name: request.personal_letter,
                        role: request.role,
                        avatar: "👤",
                        status: "protected",
                        threatsBlocked: 0,
                        lastActive: "только что",
                        devices: 1
                    )
                ],
                your_member_id: "member_\(UUID().uuidString)"
            )
            completion(.success(response))
        }
    }
    
    /**
     * Mock реализация joinFamily для тестирования
     */
    func joinFamilyMock(request: JoinFamilyRequest, completion: @escaping (Result<JoinFamilyResponse, Error>) -> Void) {
        let delay = Double.random(in: 0.5...1.5)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            let response = JoinFamilyResponse(
                success: true,
                family_id: request.family_id,
                members: [
                    FamilyMemberResponse(
                        id: "member_1",
                        name: "Родитель",
                        role: "parent",
                        avatar: "👨",
                        status: "protected",
                        threatsBlocked: 15,
                        lastActive: "2 минуты назад",
                        devices: 2
                    ),
                    FamilyMemberResponse(
                        id: "member_\(UUID().uuidString)",
                        name: request.personal_letter,
                        role: request.role,
                        avatar: "👤",
                        status: "protected",
                        threatsBlocked: 0,
                        lastActive: "только что",
                        devices: 1
                    )
                ],
                your_member_id: "member_\(UUID().uuidString)"
            )
            completion(.success(response))
        }
    }
    
    /**
     * Mock реализация recoverFamily для тестирования
     * RecoverFamilyResponse определен в FamilyRegistrationViewModel.swift
     */
    func recoverFamilyMock(familyID: String, completion: @escaping (Result<RecoverFamilyResponse, Error>) -> Void) {
        let delay = Double.random(in: 0.5...1.5)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            // RecoverFamilyResponse определен в FamilyRegistrationViewModel.swift
            // Структура: success, message, familyId, members
            let response = RecoverFamilyResponse(
                success: true,
                message: "Семья успешно восстановлена",
                familyId: familyID,
                members: [
                    FamilyMemberResponse(
                        id: "member_1",
                        name: "Родитель",
                        role: "parent",
                        avatar: "👨",
                        status: "protected",
                        threatsBlocked: 15,
                        lastActive: "2 минуты назад",
                        devices: 2
                    )
                ]
            )
            completion(.success(response))
        }
    }
}

