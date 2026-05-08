import Foundation
import UniformTypeIdentifiers
import SwiftUI

// Master Logger for antivirus logging
private let logger = MasterLogger.shared

// Forward declaration для QuarantineManager
// Файл QuarantineManager.swift должен быть подключен к тому же target

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
        logger.business("Initializing AntivirusManager")
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
        logger.business("Starting offline antivirus scan for file: \(fileURL.lastPathComponent)")
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
    
    /// Максимальный размер файла для отправки на сервер (байты). Крупнее — только локальные эвристики.
    static let maxServerScanUploadBytes: Int64 = 25 * 1024 * 1024
    
    static var maxServerScanUploadMegabytes: Int {
        Int(maxServerScanUploadBytes / (1024 * 1024))
    }
    
    /// Полное сканирование: локальная база → метаданные → при возможности сервер.
    func performFullScan(fileURL: URL) async -> ScanResult {
        log("🛡️ Начато полное сканирование: \(fileURL.lastPathComponent)")
        
        isScanning = true
        scanProgress = 0.0
        
        let offline = await scanOffline(fileURL: fileURL)
        scanProgress = 0.15
        if offline.threatLevel == .suspicious {
            isScanning = false
            scanProgress = 1.0
            lastScanResult = offline
            threatsDetected = offline.detectedThreats
            if let firstThreat = offline.detectedThreats.first {
                emitSecurityThreatNotification(
                    threatName: firstThreat.name,
                    source: "antivirus_offline_scan",
                    filePath: fileURL.path
                )
            }
            log("⚠️ Офлайн-скан: обнаружена угроза")
            return offline
        }
        
        let quickResult = await quickMetadataCheck(fileURL: fileURL)
        scanProgress = 0.3
        
        guard let metadata = extractMetadata(from: fileURL) else {
            log("❌ Не удалось извлечь метаданные для полного скана")
            isScanning = false
            scanProgress = 1.0
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
        
        let sizeOk = metadata.size > 0 && metadata.size <= Self.maxServerScanUploadBytes
        let needsServerByMeta = (quickResult == .suspicious || quickResult == .checkingServer)
        let shouldTryServer = sizeOk && (needsServerByMeta || quickResult == .safe)
        
        if !shouldTryServer {
            isScanning = false
            scanProgress = 1.0
            let level: ThreatLevel
            if !sizeOk && (quickResult == .suspicious || quickResult == .checkingServer) {
                level = quickResult == .suspicious ? .suspicious : .checkingServer
            } else {
                level = quickResult == .clean ? .clean : .safe
            }
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: level,
                detectedThreats: [],
                scanTime: Date(),
                checksum: metadata.checksum
            )
            lastScanResult = result
            threatsDetected = []
            log("✅ Сканирование завершено без отправки на сервер (размер или политика)")
            return result
        }
        
        guard let fileData = try? Data(contentsOf: fileURL), !fileData.isEmpty else {
            log("❌ Не удалось прочитать файл для сканирования")
            isScanning = false
            scanProgress = 1.0
            let result = ScanResult(
                filePath: fileURL.path,
                threatLevel: .checkingServer,
                detectedThreats: [],
                scanTime: Date(),
                checksum: metadata.checksum
            )
            lastScanResult = result
            return result
        }
        
        scanProgress = 0.55
        
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
            if let firstThreat = serverResult.detectedThreats.first {
                emitSecurityThreatNotification(
                    threatName: firstThreat.name,
                    source: "antivirus_server_scan",
                    filePath: fileURL.path
                )
            }

            if !serverResult.detectedThreats.isEmpty {
                Task {
                    do {
                        let serverList = try await APIService.shared.getUserThreatsAsync()
                        await MainActor.run {
                            self.log("📡 Каталог угроз на сервере после скана: \(serverList.count) записей")
                        }
                    } catch {
                        await MainActor.run {
                            self.log("⚠️ Не удалось подтянуть GET /api/malware/threats: \(error.localizedDescription)")
                        }
                    }
                }
            }

            return result
        }
        
        scanProgress = 1.0
        isScanning = false
        
        let fallbackLevel: ThreatLevel = (quickResult == .safe) ? .safe : .checkingServer
        let result = ScanResult(
            filePath: fileURL.path,
            threatLevel: fallbackLevel,
            detectedThreats: [],
            scanTime: Date(),
            checksum: metadata.checksum
        )
        
        lastScanResult = result
        threatsDetected = []
        log("⚠️ Серверное сканирование недоступно или завершилось ошибкой")
        
        return result
    }

    private func emitSecurityThreatNotification(
        threatName: String,
        source: String,
        filePath: String
    ) {
        let correlationId = "malware-\(UUID().uuidString)"
        NotificationManager.shared.sendLocalNotification(
            title: "🛡️ Обнаружена угроза",
            body: "\(threatName) заблокирован(а)",
            category: .security,
            userInfo: [
                "type": "threat_detected",
                "priority": "high",
                "threat_type": threatName,
                "file_path": filePath,
                "source": source,
                "correlation_id": correlationId,
                "event_id": correlationId
            ]
        )
    }
    
    // MARK: - Server Upload
    
    /// Загрузка файла на сервер для глубокого сканирования
    private func uploadForDeepScan(fileData: Data, metadata: FileMetadata) async -> ServerScanResult? {
        logger.business("Uploading file for deep server scan: \(metadata.name) (\(fileData.count) bytes)")
        log("📤 Отправка файла на сервер для сканирования")
        
        do {
            let api = try await APIService.shared.uploadFileForScanAsync(
                fileData: fileData,
                fileName: metadata.name,
                fileSize: metadata.size,
                checksum: metadata.checksum
            )
            return Self.mapFileScanResponse(api)
        } catch {
            log("❌ Ошибка серверного скана: \(error.localizedDescription)")
            return nil
        }
    }

    private static func mapFileScanResponse(_ api: APIService.MalwareFileScanAPIResponse) -> ServerScanResult {
        let threats: [Threat] = (api.threatsFound ?? []).enumerated().map { index, dto in
            let tid: String
            if let id = dto.id, !id.isEmpty {
                tid = id
            } else {
                tid = "server_threat_\(index)"
            }
            return Threat(
                id: tid,
                name: dto.name ?? "Unknown threat",
                type: dto.type ?? "malware",
                severity: dto.severity ?? "medium",
                description: dto.description ?? "",
                confidence: dto.confidence ?? (api.confidence ?? 0.5)
            )
        }
        let isClean = api.clean ?? threats.isEmpty
        let level: ThreatLevel
        if threats.isEmpty && isClean {
            level = .clean
        } else if threats.isEmpty && !isClean {
            level = .suspicious
        } else {
            level = .dangerous
        }
        let recs = api.recommendations ?? []
        return ServerScanResult(threatLevel: level, detectedThreats: threats, recommendations: recs)
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
    
    /// Поместить угрозу в карантин
    func quarantineThreat(_ threat: Threat, fileURL: URL) async -> Bool {
        log("🚫 Карантин угрозы: \(threat.name)")
        
        do {
            let quarantinedFile = try await QuarantineManager.shared.quarantineFile(
                from: fileURL,
                threatName: threat.name,
                threatType: threat.type,
                severity: threat.severity,
                confidence: threat.confidence,
                stableThreatId: threat.id
            )
            
            await MainActor.run {
                threatsDetected.removeAll { $0.id == threat.id }
            }
            
            log("✅ Угроза \(threat.name) помещена в карантин: \(quarantinedFile.originalName)")
            return true
        } catch {
            log("❌ Ошибка помещения в карантин: \(error.localizedDescription)")
            return false
        }
    }
    
    /// Удаление угрозы
    func removeThreat(_ threat: Threat, fileURL: URL) async -> Bool {
        log("🗑️ Удаление угрозы: \(threat.name)")
        
        do {
            // Удаляем файл
            try FileManager.default.removeItem(at: fileURL)
            
            // Обновляем список обнаруженных угроз
            await MainActor.run {
                threatsDetected.removeAll { $0.id == threat.id }
            }
            
            log("✅ Угроза \(threat.name) удалена: \(fileURL.lastPathComponent)")
            return true
        } catch {
            log("❌ Ошибка удаления угрозы: \(error.localizedDescription)")
            return false
        }
    }
    
    // MARK: - Logging
    
    private func log(_ message: String) {
        logger.business("[Antivirus] \(message)")
    }
}

