import Foundation
import UIKit

@MainActor
final class ActivationCodeViewModel: ObservableObject {
    
    @Published var code: String = ""
    @Published var isLoading: Bool = false
    @Published var successMessage: String?
    @Published var errorMessage: String?
    @Published var activatedPlanName: String?
    @Published var activationExpiration: String?
    @Published var logs: [String] = []  // Логи для отображения на экране
    
    private let apiService: APIService
    
    init(apiService: APIService = APIService.shared) {
        self.apiService = apiService
    }
    
    func activateCode() {
        let trimmedCode = code.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        addLog("🔵 Начало активации кода")
        addLog("   Код: \(trimmedCode)")
        print("🔵 ActivationCodeViewModel.activateCode: Начало")
        print("   - Код: \(trimmedCode)")
        
        guard !trimmedCode.isEmpty else {
            addLog("❌ Ошибка: Код пустой")
            print("❌ Код пустой")
            errorMessage = "Введите код активации"
            successMessage = nil
            return
        }
        
        errorMessage = nil
        successMessage = nil
        isLoading = true
        logs = []  // Очищаем логи при новом запросе
        addLog("⏳ Начало проверки кода...")
        print("   - isLoading установлен в true")
        
        // Получаем deviceId и familyId
        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
        let familyId = UserDefaults.standard.string(forKey: "family_id") ?? "default"
        addLog("📱 deviceId: \(deviceId.prefix(8))...")
        addLog("👨‍👩‍👧 familyId: \(familyId)")
        print("   - deviceId: \(deviceId)")
        print("   - familyId: \(familyId)")
        
        // 1. Сначала проверить код
        addLog("🔍 Шаг 1: Отправка запроса на проверку кода...")
        addLog("   URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.activationVerify)")
        print("🔵 Шаг 1: Проверка кода активации...")
        apiService.verifyActivationCode(code: trimmedCode, familyId: familyId, deviceId: deviceId) { [weak self] verifyResult in
            guard let self = self else {
                self?.addLog("❌ Ошибка: self is nil")
                print("❌ self is nil в verifyActivationCode callback")
                return
            }
            
            DispatchQueue.main.async {
                self.addLog("📥 Получен ответ от сервера (проверка)")
            }
            print("🔵 Получен ответ verifyActivationCode")
            
            switch verifyResult {
            case .success(let verifyResponse):
                DispatchQueue.main.async {
                    self.addLog("✅ Код найден на сервере")
                    self.addLog("   Статус: \(verifyResponse.status)")
                    self.addLog("   Тариф: \(verifyResponse.tariffId)")
                    self.addLog("   Истекает: \(verifyResponse.expiresAt)")
                }
                print("✅ verifyActivationCode успешен")
                print("   - status: \(verifyResponse.status)")
                print("   - tariffId: \(verifyResponse.tariffId)")
                print("   - expiresAt: \(verifyResponse.expiresAt)")
                
                if verifyResponse.status == "redeemed" {
                    self.updateLocalSubscription(tariffId: verifyResponse.tariffId, expiresAt: verifyResponse.expiresAt)
                    DispatchQueue.main.async {
                        self.addLog("⚠️ Код уже был активирован ранее")
                        self.isLoading = false
                        self.errorMessage = "Этот код уже был активирован"
                    }
                    print("⚠️ Код уже активирован")
                    return
                }
                
                if verifyResponse.status == "active" {
                    self.updateLocalSubscription(tariffId: verifyResponse.tariffId, expiresAt: verifyResponse.expiresAt)
                }
                
                if verifyResponse.status == "expired" {
                    DispatchQueue.main.async {
                        self.addLog("⚠️ Срок действия кода истёк")
                        self.isLoading = false
                        self.errorMessage = "Срок действия кода истёк"
                    }
                    print("⚠️ Код истек")
                    return
                }
                
                // Код валидный, активируем
                DispatchQueue.main.async {
                    self.addLog("🔵 Шаг 2: Отправка запроса на активацию...")
                    self.addLog("   URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.activationActivate)")
                }
                print("🔵 Шаг 2: Активация кода...")
                self.apiService.activateCode(
                    code: trimmedCode,
                    familyId: familyId,
                    deviceId: deviceId
                ) { activateResult in
                    DispatchQueue.main.async {
                        self.addLog("📥 Получен ответ от сервера (активация)")
                    }
                    print("🔵 Получен ответ activateCode")
                    
                    DispatchQueue.main.async {
                        self.isLoading = false
                        print("   - isLoading установлен в false")
                        
                        switch activateResult {
                        case .success(let activateResponse):
                            self.addLog("✅ Активация успешна!")
                            self.addLog("   success: \(activateResponse.success)")
                            self.addLog("   tariffId: \(activateResponse.tariffId)")
                            self.addLog("   expiresAt: \(activateResponse.expiresAt)")
                            print("✅ activateCode успешен")
                            print("   - success: \(activateResponse.success)")
                            print("   - tariffId: \(activateResponse.tariffId)")
                            print("   - expiresAt: \(activateResponse.expiresAt)")
                            
                            if activateResponse.success {
                                self.successMessage = "Подписка успешно активирована"
                                self.activatedPlanName = activateResponse.tariffId
                                self.addLog("🎉 Подписка активирована!")
                                
                                self.updateLocalSubscription(tariffId: activateResponse.tariffId, expiresAt: activateResponse.expiresAt)
                                
                                let formatter = ISO8601DateFormatter()
                                if let date = formatter.date(from: activateResponse.expiresAt) {
                                    let displayFormatter = DateFormatter()
                                    displayFormatter.dateStyle = .medium
                                    displayFormatter.timeStyle = .none
                                    displayFormatter.locale = Locale(identifier: "ru_RU")
                                    self.activationExpiration = displayFormatter.string(from: date)
                                } else {
                                    self.activationExpiration = activateResponse.expiresAt
                                }
                                print("✅ Активация завершена успешно")
                            } else {
                                self.addLog("❌ Ошибка: success = false")
                                print("❌ activateResponse.success = false")
                                self.errorMessage = "Не удалось активировать код"
                            }
                        case .failure(let error):
                            self.addLog("❌ ОШИБКА АКТИВАЦИИ!")
                            self.addLog("   Сообщение: \(error.localizedDescription)")
                            if let nsError = error as NSError? {
                                self.addLog("   Domain: \(nsError.domain)")
                                self.addLog("   Code: \(nsError.code)")
                                if let description = nsError.userInfo[NSLocalizedDescriptionKey] as? String {
                                    self.addLog("   Описание: \(description)")
                                }
                                // Проверяем код ошибки
                                if nsError.code == -1009 {
                                    self.addLog("   ⚠️ Нет подключения к интернету!")
                                } else if nsError.code == -1001 {
                                    self.addLog("   ⚠️ Таймаут запроса!")
                                } else if nsError.code == 502 {
                                    self.addLog("   ⚠️ Ошибка 502: Сервер недоступен!")
                                } else if nsError.code == 404 {
                                    self.addLog("   ⚠️ Ошибка 404: Endpoint не найден!")
                                }
                            }
                            print("❌ activateCode ошибка: \(error)")
                            print("   - Тип ошибки: \(type(of: error))")
                            print("   - Описание: \(error.localizedDescription)")
                            if let nsError = error as NSError? {
                                print("   - Domain: \(nsError.domain)")
                                print("   - Code: \(nsError.code)")
                                print("   - UserInfo: \(nsError.userInfo)")
                            }
                            self.errorMessage = error.localizedDescription
                        }
                    }
                }
                
            case .failure(let error):
                DispatchQueue.main.async {
                    self.addLog("❌ ОШИБКА ПРОВЕРКИ КОДА!")
                    self.addLog("   Сообщение: \(error.localizedDescription)")
                    if let nsError = error as NSError? {
                        self.addLog("   Domain: \(nsError.domain)")
                        self.addLog("   Code: \(nsError.code)")
                        if let url = nsError.userInfo["NSErrorFailingURLKey"] as? URL {
                            self.addLog("   URL: \(url.absoluteString)")
                        }
                        if let description = nsError.userInfo[NSLocalizedDescriptionKey] as? String {
                            self.addLog("   Описание: \(description)")
                        }
                        // Проверяем код ошибки
                        if nsError.code == -1009 {
                            self.addLog("   ⚠️ Нет подключения к интернету!")
                        } else if nsError.code == -1001 {
                            self.addLog("   ⚠️ Таймаут запроса!")
                        } else if nsError.code == 502 {
                            self.addLog("   ⚠️ Ошибка 502: Сервер недоступен!")
                        } else if nsError.code == 404 {
                            self.addLog("   ⚠️ Ошибка 404: Endpoint не найден!")
                        }
                    }
                    self.isLoading = false
                    self.errorMessage = error.localizedDescription
                }
                print("❌ verifyActivationCode ошибка: \(error)")
                print("   - Тип ошибки: \(type(of: error))")
                print("   - Описание: \(error.localizedDescription)")
                if let nsError = error as NSError? {
                    print("   - Domain: \(nsError.domain)")
                    print("   - Code: \(nsError.code)")
                    print("   - UserInfo: \(nsError.userInfo)")
                }
            }
        }
    }
    
    private func addLog(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let logMessage = "[\(timestamp)] \(message)"
        logs.append(logMessage)
        print(logMessage)
        
        // Ограничиваем количество логов (последние 50)
        if logs.count > 50 {
            logs.removeFirst()
        }
    }
    
    func resetMessages() {
        successMessage = nil
        errorMessage = nil
    }

    private func updateLocalSubscription(tariffId: String, expiresAt: String) {
        if let tariffType = mapTariffType(from: tariffId) {
            TariffManager.shared.saveTariff(tariffType)
            NotificationCenter.default.post(
                name: Notification.Name("tariffPurchased"),
                object: nil,
                userInfo: ["tariff": tariffType]
            )
        }
        UserDefaults.standard.set(expiresAt, forKey: "subscription_expires_at_iso")
    }
    
    private func mapTariffType(from tariffId: String) -> TariffType? {
        let value = tariffId.lowercased()
        if value.contains("family") {
            return .family
        } else if value.contains("premium") {
            return .premium
        } else if value.contains("personal") || value.contains("individual") {
            return .personal
        } else if value.contains("free") || value.contains("basic") {
            return .free
        }
        return nil
    }
    
    func clearLogs() {
        logs = []
    }
}

