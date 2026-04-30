import CoreData

/// Программная модель для `ALADDINUnifiedOffline` (в репозитории нет отдельного `.xcdatamodeld`).
enum UnifiedOfflineManagedObjectModelFactory {

    static func makeModel() -> NSManagedObjectModel {
        let model = NSManagedObjectModel()

        let entity = NSEntityDescription()
        entity.name = "UnifiedOfflineRecord"
        entity.managedObjectClassName = NSStringFromClass(UnifiedOfflineRecord.self)

        func attr(
            _ name: String,
            _ type: NSAttributeType,
            optional: Bool = true,
            usesScalar: Bool = false,
            defaultValue: Any? = nil
        ) -> NSAttributeDescription {
            let a = NSAttributeDescription()
            a.name = name
            a.attributeType = type
            a.isOptional = optional
            a.isTransient = false
            switch type {
            case .booleanAttributeType:
                a.defaultValue = defaultValue ?? false
            case .integer16AttributeType:
                a.defaultValue = defaultValue ?? Int16(2)
            default:
                break
            }
            return a
        }

        let idAttr = attr("id", .UUIDAttributeType, optional: true)
        let dataTypeAttr = attr("dataType", .stringAttributeType, optional: true)
        let dataAttr = attr("data", .binaryDataAttributeType, optional: true)
        let createdAttr = attr("createdAt", .dateAttributeType, optional: true)
        let isSyncedAttr = attr("isSynced", .booleanAttributeType, optional: false, usesScalar: true, defaultValue: false)
        let syncedAtAttr = attr("syncedAt", .dateAttributeType, optional: true)
        let priorityAttr = attr("priority", .integer16AttributeType, optional: false, usesScalar: true, defaultValue: Int16(2))
        let isModifiedAttr = attr("isModified", .booleanAttributeType, optional: false, usesScalar: true, defaultValue: false)
        let serverVersionAttr = attr("serverVersion", .dateAttributeType, optional: true)
        let clientVersionAttr = attr("clientVersion", .dateAttributeType, optional: true)

        entity.properties = [
            idAttr, dataTypeAttr, dataAttr, createdAttr, isSyncedAttr, syncedAtAttr,
            priorityAttr, isModifiedAttr, serverVersionAttr, clientVersionAttr
        ]

        model.entities = [entity]
        return model
    }
}
