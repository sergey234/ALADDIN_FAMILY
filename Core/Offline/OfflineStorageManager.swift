import Foundation
import CoreData

// MARK: - Shared offline types (используются UnifiedOfflineStore + менеджеры)

enum DataPriority: Int, Codable, Comparable {
    case critical = 0
    case important = 1
    case normal = 2

    static func < (lhs: DataPriority, rhs: DataPriority) -> Bool {
        lhs.rawValue < rhs.rawValue
    }
}

/**
 * Менеджер офлайн хранения для ALADDIN
 * Обеспечивает локальное хранение данных с Core Data
 */
class OfflineStorageManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = OfflineStorageManager()
    
    // MARK: - Unified Store (новый главный слой)
    /// Теперь используем UnifiedOfflineStore вместо дублирования Core Data
    let unifiedStore = UnifiedOfflineStore.shared
    
    // MARK: - Legacy Core Data Stack
    // Удалён из рабочих путей: операции идут через UnifiedOfflineStore.
    
    // MARK: - Published Properties
    
    /// Количество сохраненных записей
    @Published var savedRecordsCount: Int = 0
    
    /// Статус синхронизации
    @Published var syncStatus: SyncStatus = .idle
    
    // MARK: - Initialization
    
    private init() {
        // no-op
    }
    
    // MARK: - Public Methods (Delegated to UnifiedOfflineStore — 100% "из коробки")

    /**
     * Сохраняет данные через UnifiedOfflineStore (основной путь)
     */
    func save<T: Codable>(
        _ data: T,
        type: OfflineDataType,
        priority: DataPriority = .normal
    ) async -> Result<Void, NetworkError> {
        let result = await unifiedStore.save(data, type: type, priority: priority)

        switch result {
        case .success:
            await MainActor.run {
                self.savedRecordsCount += 1
                self.syncStatus = .completed
            }
            print("💾 OfflineStorageManager: Delegated save of \(type) to UnifiedOfflineStore")
            return .success(())
        case .failure(let error):
            print("❌ OfflineStorageManager: Unified save failed for \(type): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    /**
     * Получает данные через UnifiedOfflineStore (реактивно и с merge)
     */
    func retrieve<T: Codable>(
        _ type: T.Type,
        dataType: OfflineDataType
    ) async -> Result<[T], NetworkError> {
        let result = await unifiedStore.fetch(type: dataType) as Result<[T], Error>

        switch result {
        case .success(let data):
            await MainActor.run {
                self.savedRecordsCount = data.count
            }
            print("💾 OfflineStorageManager: Delegated retrieve of \(data.count) \(dataType) records via UnifiedOfflineStore")
            return .success(data)
        case .failure(let error):
            print("❌ OfflineStorageManager: Unified fetch failed for \(dataType): \(error)")
            return .failure(.fileSystemError(error))
        }
    }
    
    /**
     * Удаляет данные из офлайн хранилища
     * - Parameter type: Тип данных
     * - Returns: Результат удаления
     */
    func delete(
        dataType: OfflineDataType
    ) async -> Result<Void, NetworkError> {
        let result = await unifiedStore.delete(type: dataType)
        switch result {
        case .success:
            let stats = unifiedStore.statistics()
            await MainActor.run {
                self.savedRecordsCount = stats.totalRecords
            }
            return .success(())
        case .failure(let error):
            return .failure(.fileSystemError(error))
        }
    }
    
    // MARK: - Conflict Resolution
    
    /// Обнаруживает конфликты при синхронизации
    func detectConflicts() async -> [SyncConflict] {
        await unifiedStore.detectConflicts()
    }
    
    /// Автоматически разрешает конфликты
    func autoResolveConflicts(_ conflicts: [SyncConflict]) async {
        print("🔄 OfflineStorage: Автоматическое разрешение \(conflicts.count) конфликтов...")
        let strategy = conflicts.first?.resolutionStrategy ?? .serverWins
        await unifiedStore.resolveConflicts(strategy: strategy)
        print("✅ OfflineStorage: Конфликты разрешены")
    }
    
    /**
     * Синхронизация делегирована в UnifiedOfflineStore (центральный reactive слой)
     */
    func sync(
        dataType: OfflineDataType,
        onlyChanged: Bool = true
    ) async -> Result<Void, NetworkError> {
        await MainActor.run {
            self.syncStatus = .syncing
        }

        // Delegate to unified store
        await unifiedStore.syncAll()

        // Resolve any conflicts
        await unifiedStore.resolveConflicts(strategy: .serverWins)

        await MainActor.run {
            self.syncStatus = .completed
            self.savedRecordsCount = 0 // reset after sync
        }

        print("✅ OfflineStorageManager: Delegated full sync + conflict resolution for \(dataType) to UnifiedOfflineStore")
        return .success(())
    }
    
    /**
     * Получает статистику офлайн хранилища
     */
    func getStorageStatistics() -> OfflineStorageStatistics {
        unifiedStore.statistics()
    }
    
    /**
     * Очищает все данные из офлайн хранилища
     */
    func clearAll() async -> Result<Void, NetworkError> {
        let result = await unifiedStore.clearAll()
        switch result {
        case .success:
            await MainActor.run {
                self.savedRecordsCount = 0
                self.syncStatus = .idle
            }
            return .success(())
        case .failure(let error):
            return .failure(.fileSystemError(error))
        }
    }
}

// MARK: - OfflineDataType

/**
 * Типы данных для офлайн хранения
 */
enum OfflineDataType: String, CaseIterable, Codable {
    case networkProtectionStatus = "network_protection_status"
    case familyMembers = "family_members"
    case analytics = "analytics"
    case notifications = "notifications"
    case subscription = "subscription"
    case deviceInfo = "device_info"
    case userProfile = "user_profile"
    case settings = "settings"
    case familyChatMessage = "family_chat_message"
    case aiInteraction = "ai_interaction"
    case userSettings = "user_settings"
    case gamificationProgress = "gamification_progress"
    case mediaUpload = "media_upload"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .networkProtectionStatus:
            return "Статус защиты сети"
        case .familyMembers:
            return "Члены семьи"
        case .analytics:
            return "Аналитика"
        case .notifications:
            return "Уведомления"
        case .subscription:
            return "Подписка"
        case .deviceInfo:
            return "Информация об устройстве"
        case .userProfile:
            return "Профиль пользователя"
        case .settings:
            return "Настройки"
        case .familyChatMessage:
            return "Семейный чат"
        case .aiInteraction:
            return "AI"
        case .userSettings:
            return "Настройки пользователя"
        case .gamificationProgress:
            return "Геймификация"
        case .mediaUpload:
            return "Медиа"
        case .other:
            return "Прочее"
        }
    }
}

// MARK: - SyncStatus

/**
 * Статус синхронизации
 */
enum SyncStatus {
    case idle
    case syncing
    case completed
    case failed
    
    var displayName: String {
        switch self {
        case .idle:
            return "Ожидание"
        case .syncing:
            return "Синхронизация"
        case .completed:
            return "Завершено"
        case .failed:
            return "Ошибка"
        }
    }
}

// MARK: - OfflineStorageStatistics

/**
 * Статистика офлайн хранилища
 */
struct OfflineStorageStatistics {
    let totalRecords: Int
    let syncedRecords: Int
    let unsyncedRecords: Int
    let syncPercentage: Double
    
    var isFullySynced: Bool {
        return syncPercentage >= 1.0
    }
    
    var description: String {
        return """
        Offline Storage Statistics:
        - Всего записей: \(totalRecords)
        - Синхронизировано: \(syncedRecords)
        - Не синхронизировано: \(unsyncedRecords)
        - Процент синхронизации: \(String(format: "%.1f", syncPercentage * 100))%
        - Статус: \(isFullySynced ? "✅ Полностью синхронизировано" : "⚠️ Требуется синхронизация")
        """
    }
}

// MARK: - Conflict Resolution Models

/// Конфликт при синхронизации
struct SyncConflict: Codable {
    let recordId: UUID
    let dataType: OfflineDataType
    let clientVersion: Date
    let serverVersion: Date
    let resolutionStrategy: ConflictResolutionStrategy
}

/// Стратегия разрешения конфликта
enum ConflictResolutionStrategy: String, Codable {
    case serverWins = "server_wins"  // Использовать версию с сервера
    case clientWins = "client_wins"  // Использовать локальную версию
    case merge = "merge"             // Объединить изменения
    case manual = "manual"           // Требуется ручное разрешение
}

// MARK: - OfflineRecord (Core Data Entity)

/**
 * Сущность Core Data для офлайн записей
 */
@objc(OfflineRecord)
public class OfflineRecord: NSManagedObject {
    
}

extension OfflineRecord {
    
    @NSManaged public var id: UUID?
    @NSManaged public var dataType: String?
    @NSManaged public var data: Data?
    @NSManaged public var createdAt: Date?
    @NSManaged public var isSynced: Bool
    @NSManaged public var syncedAt: Date?
}

// MARK: - OfflineStorageManager Extensions

extension OfflineStorageManager {
    
    /**
     * Создает OfflineStorageManager для тестирования
     */
    static func test() -> OfflineStorageManager {
        return OfflineStorageManager()
    }
    
    /**
     * Создает OfflineStorageManager для продакшена
     */
    static func production() -> OfflineStorageManager {
        return OfflineStorageManager()
    }
}
