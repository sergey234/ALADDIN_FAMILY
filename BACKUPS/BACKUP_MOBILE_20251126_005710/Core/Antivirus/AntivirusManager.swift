import Foundation
import UniformTypeIdentifiers
import SwiftUI

/// Antivirus Manager для ALADDIN
/// Быстрая проверка метаданных на клиенте, полное сканирование на сервере
class AntivirusManager: ObservableObject {
    
    static let shared = AntivirusManager()
    
    @Published var isScanning = false
    @Published var lastScanResult: ScanResult?
    @Published var threatsDetected: [Threat] = []
    @Published var scanProgress: Double = 0.0
    
    // MARK: - Models
    
    enum ThreatLevel: String, Codable {
        case clean = "clean"
        case safe = "safe"
        case suspicious = "suspicious"
        case dangerous = "dangerous"
        case checkingServer = "checking_server"
    }
    
    struct ScanResult: Codable {
        let filePath: String
        let threatLevel: ThreatLevel
        let detectedThreats: [Threat]
        let scanTime: Date
        let checksum: String?
    }
    
    struct Threat: Codable {
        let id: String
        let name: String
        let type: String // "virus", "malware", "adware", "spyware"
        let severity: String // "low", "medium", "high", "critical"
        let description: String
        let confidence: Double
    }
    
    struct FileMetadata {
        let path: String
        let name: String
        let size: Int64
        let modifiedDate: Date
        let fileExtension: String
        let checksum: String?
    }
    
    // MARK: - Scan Result Caching
    
    private var scanResultsCache: [String: ScanResult] = [:]
    private let cacheManager = CacheManager.shared
    
    private init() {
        log("AntivirusManager инициализирован")
    }
    
    // MARK: - Quick Metadata Check (Local)
    
    /// Быстрая проверка метаданных файла (локально, без сканирования содержимого)
    func quickMetadataCheck(fileURL: URL) async -> ThreatLevel {
        log("🔍 Быстрая проверка метаданных: \(fileURL.lastPathComponent)")
        
        guard let metadata = extractMetadata(from: fileURL) else {
            log("⚠️ Не удалось извлечь метаданные")
            return .checkingServer
        }
        
        // Проверка расширения
        if isDangerousExtension(metadata.fileExtension) {
            log("⚠️ Подозрительное расширение: \(metadata.fileExtension)")
            return .suspicious
        }
        
        // Проверка размера
        if metadata.size > 100 * 1024 * 1024 { // > 100MB
            log("⚠️ Файл слишком большой: \(metadata.size) bytes")
            return .checkingServer // Нужна проверка на сервере
        }
        
        // Файл выглядит безопасно
        log("✅ Метаданные файла выглядят безопасными")
        return .safe
    }
    
    /// Извлечение метаданных файла
    private func extractMetadata(from fileURL: URL) -> FileMetadata? {
        do {
            let fileAttributes = try FileManager.default.attributesOfItem(atPath: fileURL.path)
            let fileSize = (fileAttributes[.size] as? Int64) ?? 0
            let modifiedDate = (fileAttributes[.modificationDate] as? Date) ?? Date()
            
            let metadata = FileMetadata(
                path: fileURL.path,
                name: fileURL.lastPathComponent,
                size: fileSize,
                modifiedDate: modifiedDate,
                fileExtension: fileURL.pathExtension.lowercased(),
                checksum: nil // TODO: вычислить MD5/SHA256
            )
            
            return metadata
        } catch {
            log("❌ Ошибка извлечения метаданных: \(error.localizedDescription)")
            return nil
        }
    }
    
    /// Проверка опасных расширений
    private func isDangerousExtension(_ ext: String) -> Bool {
        let dangerousExtensions = [
            "exe", "bat", "cmd", "com", "pif", "scr", "vbs", "js",
            "jar", "app", "deb", "dmg", "pkg", "run",
            "sh", "bin", "py", "pl", "php", "rb"
        ]
        
        return dangerousExtensions.contains(ext)
    }
    
    // MARK: - Offline Scan
    
    /// Офлайн сканирование файла (использует локальную базу сигнатур)
    func scanOffline(fileURL: URL) async -> ScanResult {
        log("🛡️ Офлайн сканирование: \(fileURL.lastPathComponent)")
        
        // Используем локальную базу сигнатур
        let localThreatLevel = LocalThreatDatabase.shared.scanFile(fileURL: fileURL)
        
        if localThreatLevel == .suspicious {
            let threat = Threat(
                id: UUID().uuidString,
                name: "Обнаружено локальной базой сигнатур",
                type: "malware",
                severity: "medium",
                description: "Файл соответствует сигнатуре из локальной базы угроз",
                confidence: 0.8
            )
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: .suspicious,
                detectedThreats: [threat],
                scanTime: Date(),
                checksum: nil
            )
            
            // Кэшируем результат
            cacheScanResult(result)
            
            log("⚠️ Офлайн сканирование: Обнаружена угроза")
            return result
        }
        
        // Если локальная база не нашла угроз, возвращаем safe
        let result = ScanResult(
            filePath: fileURL.path,
            threatLevel: .safe,
            detectedThreats: [],
            scanTime: Date(),
            checksum: nil
        )
        
        cacheScanResult(result)
        log("✅ Офлайн сканирование: Файл безопасен")
        return result
    }
    
    // MARK: - Scan Result Caching
    
    /// Кэширует результат сканирования
    private func cacheScanResult(_ result: ScanResult) {
        // Используем путь файла как ключ
        let cacheKey = "scan_\(result.filePath)"
        
        // Сохраняем в CacheManager (асинхронно)
        Task {
            await cacheManager.store(result, forKey: cacheKey, ttl: 3600, priority: .normal)
        }
        
        // Сохраняем в локальный кэш
        scanResultsCache[cacheKey] = result
        
        log("💾 Результат сканирования закэширован: \(cacheKey)")
    }
    
    /// Получает результат сканирования из кэша
    func getCachedScanResult(fileURL: URL) async -> ScanResult? {
        let cacheKey = "scan_\(fileURL.path)"
        
        // Проверяем локальный кэш
        if let cached = scanResultsCache[cacheKey] {
            log("💾 Результат найден в локальном кэше")
            return cached
        }
        
        // Проверяем CacheManager (асинхронно)
        if let cached: ScanResult = await cacheManager.retrieve(ScanResult.self, forKey: cacheKey) {
            log("💾 Результат найден в CacheManager")
            scanResultsCache[cacheKey] = cached
            return cached
        }
        
        return nil
    }
    
    /// Проверяет, изменился ли файл (по checksum)
    private func hasFileChanged(fileURL: URL, cachedResult: ScanResult) -> Bool {
        // TODO: Вычислить checksum файла и сравнить с cachedResult.checksum
        // Если checksum отличается, файл изменился
        // Пока всегда считаем, что файл мог измениться
        return true
    }
    
    // MARK: - Full Server Scan
    
    /// Полное сканирование файла на сервере
    func performFullScan(fileURL: URL) async -> ScanResult {
        log("🛡️ Начато полное сканирование: \(fileURL.lastPathComponent)")
        
        isScanning = true
        scanProgress = 0.0
        
        // Начало сканирования (может использоваться для логирования времени)
        let _ = Date()
        
        // 1. Быстрая локальная проверка
        let quickResult = await quickMetadataCheck(fileURL: fileURL)
        
        if quickResult == .clean || quickResult == .safe {
            scanProgress = 1.0
            isScanning = false
            
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: quickResult,
                detectedThreats: [],
                scanTime: Date(),
                checksum: nil
            )
            
            lastScanResult = result
            log("✅ Сканирование завершено: файл безопасен")
            
            return result
        }
        
        scanProgress = 0.3
        
        // 2. Отправка на сервер для глубокого сканирования
        guard let metadata = extractMetadata(from: fileURL),
              let fileData = try? Data(contentsOf: fileURL) else {
            log("❌ Не удалось загрузить файл для сканирования")
            isScanning = false
            
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: .checkingServer,
                detectedThreats: [],
                scanTime: Date(),
                checksum: nil
            )
            
            lastScanResult = result
            return result
        }
        
        scanProgress = 0.6
        
        // Отправка на сервер
        if let serverResult = await uploadForDeepScan(fileData: fileData, metadata: metadata) {
            scanProgress = 1.0
            isScanning = false
            
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: serverResult.threatLevel,
                detectedThreats: serverResult.detectedThreats,
                scanTime: Date(),
                checksum: metadata.checksum
            )
            
            lastScanResult = result
            threatsDetected = serverResult.detectedThreats
            
            log("✅ Серверное сканирование завершено: \(serverResult.detectedThreats.count) угроз обнаружено")
            
            return result
        }
        
        // Ошибка подключения к серверу
        scanProgress = 1.0
        isScanning = false
        
        let result = ScanResult(
            filePath: fileURL.path,
            threatLevel: .checkingServer,
            detectedThreats: [],
            scanTime: Date(),
            checksum: metadata.checksum
        )
        
        lastScanResult = result
        log("⚠️ Не удалось подключиться к серверу для сканирования")
        
        return result
    }
    
    // MARK: - Server Upload
    
    /// Загрузка файла на сервер для глубокого сканирования
    private func uploadForDeepScan(fileData: Data, metadata: FileMetadata) async -> ServerScanResult? {
        log("📤 Отправка файла на сервер для сканирования")
        
        // TODO: Интеграция с APIService
        // Временная заглушка
        return nil
    }
    
    struct ServerScanResult {
        let threatLevel: ThreatLevel
        let detectedThreats: [Threat]
        let recommendations: [String]
    }
    
    // MARK: - Batch Scan
    
    /// Сканирование нескольких файлов
    /// Сканирует несколько файлов параллельно (оптимизация производительности)
    func scanFiles(_ fileURLs: [URL]) async -> [ScanResult] {
        log("🛡️ Параллельное сканирование \(fileURLs.count) файлов")
        
        return await withTaskGroup(of: ScanResult.self) { group in
            for fileURL in fileURLs {
                group.addTask { [weak self] in
                    guard let self = self else {
                        return ScanResult(
                            filePath: fileURL.path,
                            threatLevel: .checkingServer,
                            detectedThreats: [],
                            scanTime: Date(),
                            checksum: nil
                        )
                    }
                    
                    // Сначала проверяем кэш
                    if let cached = await self.getCachedScanResult(fileURL: fileURL),
                       !self.hasFileChanged(fileURL: fileURL, cachedResult: cached) {
                        return cached
                    }
                    
                    // Если нет в кэше или файл изменился, сканируем
                    return await self.performFullScan(fileURL: fileURL)
                }
            }
            
            var results: [ScanResult] = []
            for await result in group {
                results.append(result)
            }
            
            log("✅ Параллельное сканирование завершено: \(results.count) файлов")
            return results
        }
    }
    
    /// Старый метод (оставлен для обратной совместимости)
    func scanFilesOld(_ fileURLs: [URL]) async -> [ScanResult] {
        log("🛡️ Начато сканирование \(fileURLs.count) файлов")
        
        var results: [ScanResult] = []
        
        for (index, fileURL) in fileURLs.enumerated() {
            let result = await performFullScan(fileURL: fileURL)
            results.append(result)
            
            scanProgress = Double(index + 1) / Double(fileURLs.count)
        }
        
        isScanning = false
        log("✅ Пакетное сканирование завершено: \(results.count) файлов проверено")
        
        return results
    }
    
    // MARK: - Threat Management
    
    /// Очистка обнаруженных угроз
    func quarantineThreat(_ threat: Threat) async -> Bool {
        log("🚫 Карантин угрозы: \(threat.name)")
        
        // TODO: Реализовать карантин
        return true
    }
    
    /// Удаление угрозы
    func removeThreat(_ threat: Threat) async -> Bool {
        log("🗑️ Удаление угрозы: \(threat.name)")
        
        // TODO: Реализовать удаление
        return true
    }
    
    // MARK: - Logging
    
    private func log(_ message: String) {
        print("[AntivirusManager] \(message)")
    }
}

