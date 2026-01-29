import Foundation
import SwiftUI
import CommonCrypto

/// Enterprise Quarantine Manager
/// Управление карантином зараженных файлов с enterprise функциями
class QuarantineManager: ObservableObject {

    static let shared = QuarantineManager()

    @Published var quarantinedFiles: [QuarantinedFile] = []
    @Published var quarantineSize: Int64 = 0
    @Published var isLoading = false

    private let quarantineDirectory: URL
    private let metadataFileName = "quarantine_metadata.json"
    private let fileManager = FileManager.default

    // MARK: - Models

    struct QuarantinedFile: Codable, Identifiable {
        let id: String
        let originalPath: String
        let originalName: String
        let quarantinePath: String
        let fileSize: Int64
        let threatName: String
        let threatType: String
        let severity: String
        let confidence: Double
        let quarantinedAt: Date
        let checksum: String?
        var status: String = "quarantined" // "quarantined", "restored", "removed"
    }

    // MARK: - Initialization

    private init() {
        // Создаем директорию карантина в Documents
        let documentsDirectory = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
        quarantineDirectory = documentsDirectory.appendingPathComponent("ALADDIN_Quarantine", isDirectory: true)

        createQuarantineDirectoryIfNeeded()
        loadQuarantineMetadata()
        updateQuarantineSize()

        print("[QuarantineManager] Инициализирован, карантин: \(quarantineDirectory.path)")
    }

    // MARK: - Public API

    /// Поместить файл в карантин
    func quarantineFile(
        from originalURL: URL,
        threatName: String,
        threatType: String,
        severity: String,
        confidence: Double
    ) async throws -> QuarantinedFile {

        print("[QuarantineManager] Карантин файла: \(originalURL.lastPathComponent)")

        let fileId = UUID().uuidString
        let quarantinedName = "\(fileId)_\(originalURL.lastPathComponent)"
        let quarantineURL = quarantineDirectory.appendingPathComponent(quarantinedName)

        // Получаем метаданные файла
        let attributes = try fileManager.attributesOfItem(atPath: originalURL.path)
        let fileSize = (attributes[.size] as? Int64) ?? 0

        // Вычисляем checksum
        let fileData = try Data(contentsOf: originalURL)
        let checksum = calculateMD5(data: fileData)

        // Копируем файл в карантин
        try fileManager.copyItem(at: originalURL, to: quarantineURL)

        // Создаем запись о карантине
        let quarantinedFile = QuarantinedFile(
            id: fileId,
            originalPath: originalURL.path,
            originalName: originalURL.lastPathComponent,
            quarantinePath: quarantineURL.path,
            fileSize: fileSize,
            threatName: threatName,
            threatType: threatType,
            severity: severity,
            confidence: confidence,
            quarantinedAt: Date(),
            checksum: checksum
        )

        // Добавляем в список и сохраняем
        await MainActor.run {
            quarantinedFiles.append(quarantinedFile)
        }

        saveQuarantineMetadata()
        updateQuarantineSize()

        // Отправляем на сервер
        try await syncWithServer(quarantinedFile, action: "quarantine")

        print("[QuarantineManager] ✅ Файл помещен в карантин: \(quarantinedName)")
        return quarantinedFile
    }

    /// Восстановить файл из карантина
    func restoreFile(from quarantinedFile: QuarantinedFile, to destinationURL: URL? = nil) async throws {

        print("[QuarantineManager] Восстановление файла: \(quarantinedFile.originalName)")

        let quarantineURL = URL(fileURLWithPath: quarantinedFile.quarantinePath)
        let restoreURL = destinationURL ?? URL(fileURLWithPath: quarantinedFile.originalPath)

        // Проверяем, существует ли оригинальный путь
        let restoreDirectory = restoreURL.deletingLastPathComponent()
        if !fileManager.fileExists(atPath: restoreDirectory.path) {
            try fileManager.createDirectory(at: restoreDirectory, withIntermediateDirectories: true)
        }

        // Копируем файл обратно
        try fileManager.copyItem(at: quarantineURL, to: restoreURL)

        // Обновляем статус
        await MainActor.run {
            if let index = quarantinedFiles.firstIndex(where: { $0.id == quarantinedFile.id }) {
                quarantinedFiles[index].status = "restored"
            }
        }

        saveQuarantineMetadata()

        // Отправляем на сервер
        try await syncWithServer(quarantinedFile, action: "restore")

        print("[QuarantineManager] ✅ Файл восстановлен: \(restoreURL.path)")
    }

    /// Полностью удалить файл из карантина
    func permanentlyRemoveFile(_ quarantinedFile: QuarantinedFile) async throws {

        print("[QuarantineManager] Удаление файла из карантина: \(quarantinedFile.originalName)")

        let quarantineURL = URL(fileURLWithPath: quarantinedFile.quarantinePath)

        // Удаляем файл из файловой системы
        try fileManager.removeItem(at: quarantineURL)

        // Обновляем статус
        await MainActor.run {
            if let index = quarantinedFiles.firstIndex(where: { $0.id == quarantinedFile.id }) {
                quarantinedFiles[index].status = "removed"
            }
        }

        saveQuarantineMetadata()
        updateQuarantineSize()

        // Отправляем на сервер
        try await syncWithServer(quarantinedFile, action: "remove")

        print("[QuarantineManager] ✅ Файл удален из карантина")
    }

    /// Очистить старые файлы из карантина (старше 30 дней)
    func cleanupOldQuarantineFiles(daysOld: Int = 30) async {

        print("[QuarantineManager] Очистка старых файлов карантина (старше \(daysOld) дней)")

        let cutoffDate = Date().addingTimeInterval(-Double(daysOld * 24 * 60 * 60))
        var removedCount = 0

        await MainActor.run {
            quarantinedFiles = quarantinedFiles.filter { quarantinedFile in
                if quarantinedFile.quarantinedAt < cutoffDate && quarantinedFile.status == "quarantined" {
                    do {
                        let quarantineURL = URL(fileURLWithPath: quarantinedFile.quarantinePath)
                        try fileManager.removeItem(at: quarantineURL)
                        print("[QuarantineManager] 🗑️ Удален старый файл: \(quarantinedFile.originalName)")
                        return false // Удаляем из списка
                    } catch {
                        print("[QuarantineManager] ❌ Ошибка удаления старого файла: \(error.localizedDescription)")
                        return true // Оставляем в списке
                    }
                }
                return true // Оставляем в списке
            }
        }

        // Обновляем счетчик после фильтрации
        removedCount = quarantinedFiles.filter { $0.quarantinedAt < cutoffDate && $0.status != "quarantined" }.count

        if removedCount > 0 {
            saveQuarantineMetadata()
            updateQuarantineSize()
            print("[QuarantineManager] ✅ Очищено \(removedCount) старых файлов")
        }
    }

    /// Получить статистику карантина
    func getQuarantineStats() -> QuarantineStats {
        let totalFiles = quarantinedFiles.count
        let activeFiles = quarantinedFiles.filter { $0.status == "quarantined" }.count
        let restoredFiles = quarantinedFiles.filter { $0.status == "restored" }.count
        let removedFiles = quarantinedFiles.filter { $0.status == "removed" }.count

        let threatsByType = Dictionary(grouping: quarantinedFiles) { $0.threatType }
            .mapValues { $0.count }

        let threatsBySeverity = Dictionary(grouping: quarantinedFiles) { $0.severity }
            .mapValues { $0.count }

        return QuarantineStats(
            totalFiles: totalFiles,
            activeFiles: activeFiles,
            restoredFiles: restoredFiles,
            removedFiles: removedFiles,
            quarantineSize: quarantineSize,
            threatsByType: threatsByType,
            threatsBySeverity: threatsBySeverity,
            oldestFile: quarantinedFiles.min(by: { $0.quarantinedAt < $1.quarantinedAt })?.quarantinedAt
        )
    }

    /// Синхронизировать карантин с сервером
    func syncQuarantineWithServer() async {
        print("[QuarantineManager] Синхронизация карантина с сервером")

        do {
            // Получаем список угроз с сервера
            let serverThreats = try await APIService.shared.getUserThreatsAsync(status: "quarantined")

            // Синхронизируем локальный карантин с сервером
            for serverThreat in serverThreats {
                let existsLocally = quarantinedFiles.contains { $0.id == serverThreat.id }

                if !existsLocally && serverThreat.quarantinePath != nil {
                    // Сервер имеет файл в карантине, которого нет локально
                    // TODO: Скачать файл из серверного карантина если нужно
                    print("[QuarantineManager] Найден файл в серверном карантине: \(serverThreat.fileName)")
                }
            }

            print("[QuarantineManager] ✅ Синхронизация завершена")

        } catch {
            print("[QuarantineManager] ❌ Ошибка синхронизации: \(error.localizedDescription)")
        }
    }

    // MARK: - Private Methods

    private func createQuarantineDirectoryIfNeeded() {
        if !fileManager.fileExists(atPath: quarantineDirectory.path) {
            do {
                try fileManager.createDirectory(at: quarantineDirectory, withIntermediateDirectories: true)
                print("[QuarantineManager] ✅ Создана директория карантина")
            } catch {
                print("[QuarantineManager] ❌ Ошибка создания директории карантина: \(error.localizedDescription)")
            }
        }
    }

    private func loadQuarantineMetadata() {
        let metadataURL = quarantineDirectory.appendingPathComponent(metadataFileName)

        guard fileManager.fileExists(atPath: metadataURL.path) else {
            print("[QuarantineManager] Метаданные карантина не найдены, начинаем с пустого списка")
            return
        }

        do {
            let data = try Data(contentsOf: metadataURL)
            quarantinedFiles = try JSONDecoder().decode([QuarantinedFile].self, from: data)
            print("[QuarantineManager] ✅ Загружены метаданные карантина: \(quarantinedFiles.count) файлов")
        } catch {
            print("[QuarantineManager] ❌ Ошибка загрузки метаданных карантина: \(error.localizedDescription)")
        }
    }

    private func saveQuarantineMetadata() {
        let metadataURL = quarantineDirectory.appendingPathComponent(metadataFileName)

        do {
            let data = try JSONEncoder().encode(quarantinedFiles)
            try data.write(to: metadataURL)
            print("[QuarantineManager] 💾 Метаданные карантина сохранены")
        } catch {
            print("[QuarantineManager] ❌ Ошибка сохранения метаданных карантина: \(error.localizedDescription)")
        }
    }

    private func updateQuarantineSize() {
        quarantineSize = quarantinedFiles
            .filter { $0.status == "quarantined" }
            .reduce(0) { $0 + $1.fileSize }
    }

    private func calculateMD5(data: Data) -> String {
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))
        data.withUnsafeBytes { bytes in
            CC_MD5(bytes.baseAddress, CC_LONG(data.count), &digest)
        }
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    private func syncWithServer(_ quarantinedFile: QuarantinedFile, action: String) async throws {
        // Синхронизируем действие с сервером
        _ = try await APIService.shared.quarantineFileAsync(
            threatId: quarantinedFile.id,
            action: action
        )
    }
}

// MARK: - Supporting Types

struct QuarantineStats {
    let totalFiles: Int
    let activeFiles: Int
    let restoredFiles: Int
    let removedFiles: Int
    let quarantineSize: Int64
    let threatsByType: [String: Int]
    let threatsBySeverity: [String: Int]
    let oldestFile: Date?
}
