import Foundation

/// 🛡️ Local Threat Database
/// Локальная база сигнатур для офлайн сканирования
class LocalThreatDatabase {
    static let shared = LocalThreatDatabase()
    
    private var threatSignatures: [ThreatSignature] = []
    private let databaseFile = "threat_database.json"
    private var lastUpdateDate: Date?
    
    private init() {
        loadDatabase()
    }
    
    // MARK: - Database Management
    
    /// Загружает базу сигнатур из Bundle
    private func loadDatabase() {
        // Сначала пытаемся загрузить из Bundle
        if let url = Bundle.main.url(forResource: "threat_database", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let signatures = try? JSONDecoder().decode([ThreatSignature].self, from: data) {
            threatSignatures = signatures
            print("✅ LocalThreatDatabase: Загружено \(signatures.count) сигнатур из Bundle")
            return
        }
        
        // Если нет в Bundle, используем встроенную базу
        loadBuiltInDatabase()
    }
    
    /// Загружает встроенную базу сигнатур (базовая защита)
    private func loadBuiltInDatabase() {
        threatSignatures = [
            // Опасные расширения
            ThreatSignature(
                id: "dangerous_extensions",
                name: "Опасные расширения файлов",
                type: "extension",
                dangerousExtensions: [
                    "exe", "bat", "cmd", "com", "pif", "scr", "vbs", "js",
                    "jar", "app", "deb", "dmg", "pkg", "run",
                    "sh", "bin", "py", "pl", "php", "rb"
                ],
                dangerousNames: [],
                severity: "high"
            ),
            // Подозрительные имена файлов
            ThreatSignature(
                id: "suspicious_names",
                name: "Подозрительные имена файлов",
                type: "filename",
                dangerousExtensions: [],
                dangerousNames: [
                    "virus", "trojan", "malware", "spyware",
                    "keygen", "crack", "hack", "exploit"
                ],
                severity: "medium"
            )
        ]
        
        print("✅ LocalThreatDatabase: Загружена встроенная база (\(threatSignatures.count) сигнатур)")
    }
    
    /// Обновляет базу сигнатур с сервера
    func updateDatabase() async {
        print("🔄 LocalThreatDatabase: Обновление базы сигнатур...")
        
        // TODO: Реализовать загрузку обновлений с сервера
        // Пример:
        /*
        do {
            let response = try await APIService.shared.getThreatDatabase()
            threatSignatures = response.signatures
            lastUpdateDate = Date()
            
            // Сохраняем обновлённую базу
            saveDatabase()
            
            print("✅ LocalThreatDatabase: База обновлена (\(threatSignatures.count) сигнатур)")
        } catch {
            print("❌ LocalThreatDatabase: Ошибка обновления базы: \(error.localizedDescription)")
        }
        */
        
        print("⚠️ LocalThreatDatabase: Обновление базы требует реализации API")
    }
    
    /// Сохраняет базу сигнатур на диск
    private func saveDatabase() {
        guard let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        
        let fileURL = documentsURL.appendingPathComponent(databaseFile)
        
        do {
            let data = try JSONEncoder().encode(threatSignatures)
            try data.write(to: fileURL)
            print("✅ LocalThreatDatabase: База сохранена на диск")
        } catch {
            print("❌ LocalThreatDatabase: Ошибка сохранения базы: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Threat Detection
    
    /// Проверяет файл на наличие угроз в локальной базе
    func scanFile(fileURL: URL) -> AntivirusManager.ThreatLevel {
        let fileName = fileURL.lastPathComponent.lowercased()
        let fileExtension = fileURL.pathExtension.lowercased()
        
        // Проверка по расширению
        for signature in threatSignatures {
            if signature.dangerousExtensions.contains(fileExtension) {
                print("⚠️ LocalThreatDatabase: Обнаружена угроза по расширению '\(fileExtension)' - \(signature.name)")
                return .suspicious
            }
        }
        
        // Проверка по имени файла
        for signature in threatSignatures {
            for dangerousName in signature.dangerousNames {
                if fileName.contains(dangerousName.lowercased()) {
                    print("⚠️ LocalThreatDatabase: Обнаружена угроза по имени '\(dangerousName)' - \(signature.name)")
                    return .suspicious
                }
            }
        }
        
        return .safe
    }
    
    /// Получает количество сигнатур в базе
    func getSignatureCount() -> Int {
        return threatSignatures.count
    }
    
    /// Получает дату последнего обновления
    func getLastUpdateDate() -> Date? {
        return lastUpdateDate
    }
}

// MARK: - Threat Signature Model

struct ThreatSignature: Codable {
    let id: String
    let name: String
    let type: String  // "extension", "filename", "hash", "pattern"
    let dangerousExtensions: [String]
    let dangerousNames: [String]
    let severity: String  // "low", "medium", "high", "critical"
}

