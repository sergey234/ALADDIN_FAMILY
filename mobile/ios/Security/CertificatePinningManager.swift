import Foundation
import Security
import Network

class CertificatePinningManager {
    static let shared = CertificatePinningManager()
    
    private let pinnedCertificates: [Data]
    private let pinnedHosts: Set<String>
    
    private init() {
        // Загружаем сертификаты из bundle
        self.pinnedCertificates = loadPinnedCertificates()
        
        // Список защищенных хостов
        self.pinnedHosts = [
            "api.aladdin.security",
            "ai.aladdin.security", 
            "vpn.aladdin.security",
            "auth.aladdin.security"
        ]
    }
    
    // Загрузка сертификатов из bundle
    private func loadPinnedCertificates() -> [Data] {
        var certificates: [Data] = []
        
        // Загружаем основные сертификаты
        if let certPath = Bundle.main.path(forResource: "aladdin-api-cert", ofType: "cer"),
           let certData = NSData(contentsOfFile: certPath) {
            certificates.append(certData as Data)
        }
        
        if let certPath = Bundle.main.path(forResource: "aladdin-ai-cert", ofType: "cer"),
           let certData = NSData(contentsOfFile: certPath) {
            certificates.append(certData as Data)
        }
        
        return certificates
    }
    
    // Проверка сертификата
    func validateCertificate(_ serverTrust: SecTrust, host: String) -> Bool {
        // Проверяем, что хост в списке защищенных
        guard pinnedHosts.contains(host) else {
            print("⚠️ Host \(host) not in pinned hosts list")
            return false
        }
        
        // Получаем сертификат сервера
        guard let serverCertificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            print("❌ Failed to get server certificate")
            return false
        }
        
        // Получаем данные сертификата
        let serverCertData = SecCertificateCopyData(serverCertificate)
        let serverCertDataBytes = CFDataGetBytePtr(serverCertData)
        let serverCertDataLength = CFDataGetLength(serverCertData)
        let serverCertDataNSData = NSData(bytes: serverCertDataBytes, length: serverCertDataLength)
        
        // Сравниваем с закрепленными сертификатами
        for pinnedCert in pinnedCertificates {
            if serverCertDataNSData.isEqual(to: pinnedCert) {
                print("✅ Certificate pinning successful for \(host)")
                return true
            }
        }
        
        print("❌ Certificate pinning failed for \(host)")
        return false
    }
    
    // Создание Trust Evaluator для Alamofire
    func createTrustEvaluator() -> PinnedCertificatesTrustEvaluator {
        return PinnedCertificatesTrustEvaluator(certificates: pinnedCertificates)
    }
    
    // Проверка статуса pinning
    func getPinningStatus() -> [String: Bool] {
        var status: [String: Bool] = [:]
        
        for host in pinnedHosts {
            status[host] = true // В реальном приложении здесь была бы проверка
        }
        
        return status
    }
    
    // Обновление сертификатов
    func updateCertificates() {
        // В реальном приложении здесь была бы логика обновления
        print("🔄 Updating pinned certificates...")
    }
}

// MARK: - Certificate Validation Delegate
extension CertificatePinningManager: URLSessionDelegate {
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        let host = challenge.protectionSpace.host
        
        if validateCertificate(serverTrust, host: host) {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

