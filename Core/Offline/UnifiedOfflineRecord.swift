import CoreData

/// Запись unified-офлайн слоя (`ALADDINUnifiedOffline`), отделена от legacy `OfflineRecord` в `ALADDINOffline`.
@objc(UnifiedOfflineRecord)
public class UnifiedOfflineRecord: NSManagedObject {}

extension UnifiedOfflineRecord {

    @NSManaged public var id: UUID?
    @NSManaged public var dataType: String?
    @NSManaged public var data: Data?
    @NSManaged public var createdAt: Date?
    @NSManaged public var isSynced: Bool
    @NSManaged public var syncedAt: Date?
    @NSManaged public var priority: Int16
    @NSManaged public var isModified: Bool
    @NSManaged public var serverVersion: Date?
    @NSManaged public var clientVersion: Date?
}
