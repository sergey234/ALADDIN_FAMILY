import Foundation
import UIKit

class ErrorHandler {
    static let shared = ErrorHandler()
    
    private init() {}
    
    // MARK: - Error Handling
    
    func handle(_ error: Error, source: String = #file, line: Int = #line) {
        let errorInfo = ErrorInfo(
            error: error,
            source: source,
            line: line,
            timestamp: Date()
        )
        
        // Log error
        logError(errorInfo)
        
        // Send to analytics
        sendToAnalytics(errorInfo)
        
        // Show user-friendly message
        showUserMessage(for: error)
    }
    
    func handle(_ alamoError: ALADDINError, source: String = #file, line: Int = #line) {
        handle(alamoError as Error, source: source, line: line)
    }
    
    // MARK: - Logging
    
    private func logError(_ errorInfo: ErrorInfo) {
        print("❌ ERROR [\(errorInfo.timestamp)]")
        print("   Source: \(errorInfo.source):\(errorInfo.line)")
        print("   Error: \(errorInfo.error.localizedDescription)")
        
        // В production это было бы отправлено в систему логирования
    }
    
    // MARK: - Analytics
    
    private func sendToAnalytics(_ errorInfo: ErrorInfo) {
        // В реальном приложении здесь была бы отправка в Firebase/Crashlytics
        print("📊 Sending error to analytics...")
    }
    
    // MARK: - User Messages
    
    private func showUserMessage(for error: Error) {
        let message = getUserFriendlyMessage(for: error)
        
        DispatchQueue.main.async {
            if let topViewController = UIApplication.shared.keyWindow?.rootViewController {
                self.showAlert(title: "Ошибка", message: message, on: topViewController)
            }
        }
    }
    
    private func getUserFriendlyMessage(for error: Error) -> String {
        if let alamoError = error as? ALADDINError {
            switch alamoError {
            case .networkError(let networkError):
                return getMessageFor(networkError)
            case .securityError(let securityError):
                return getMessageFor(securityError)
            }
        }
        
        return "Произошла ошибка. Попробуйте позже."
    }
    
    private func getMessageFor(_ networkError: NetworkError) -> String {
        switch networkError {
        case .noConnection:
            return "Нет подключения к интернету"
        case .timeout:
            return "Превышено время ожидания"
        case .serverError(let code):
            return "Ошибка сервера (\(code))"
        case .invalidResponse:
            return "Некорректный ответ сервера"
        case .rateLimited:
            return "Слишком много запросов. Попробуйте позже."
        }
    }
    
    private func getMessageFor(_ securityError: SecurityError) -> String {
        switch securityError {
        case .certificatePinningFailed:
            return "Ошибка безопасности соединения"
        case .invalidCertificate:
            return "Недействительный сертификат"
        case .hostNotTrusted:
            return "Небезопасное соединение"
        }
    }
    
    // MARK: - Alert
    
    private func showAlert(title: String, message: String, on viewController: UIViewController) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        viewController.present(alert, animated: true)
    }
    
    // MARK: - Recovery
    
    func attemptRecovery(from error: Error, completion: @escaping (Bool) -> Void) {
        if let alamoError = error as? ALADDINError {
            switch alamoError {
            case .networkError(.noConnection):
                // Retry with exponential backoff
                retryWithBackoff(completion: completion)
                
            case .networkError(.timeout):
                // Retry immediately
                completion(true)
                
            case .securityError:
                // Cannot recover from security errors
                completion(false)
                
            default:
                completion(false)
            }
        } else {
            completion(false)
        }
    }
    
    private func retryWithBackoff(attempt: Int = 1, completion: @escaping (Bool) -> Void) {
        let delay = min(pow(2.0, Double(attempt)), 30.0) // Max 30 seconds
        
        DispatchQueue.global().asyncAfter(deadline: .now() + delay) {
            // Check if network is available
            completion(true)
        }
    }
}

// MARK: - Error Info

struct ErrorInfo {
    let error: Error
    let source: String
    let line: Int
    let timestamp: Date
}

// MARK: - Result Extension

extension Result {
    func handleError(handler: ErrorHandler = .shared) {
        if case .failure(let error) = self {
            handler.handle(error)
        }
    }
}

