import Foundation
import CoreData

class CoreDataStack {
    static let shared = CoreDataStack()
    
    private init() {}
    
    // MARK: - Core Data Stack
    
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "ALADDINDataModel")
        
        // Настройка хранилища
        let storeDescription = container.persistentStoreDescriptions.first
        storeDescription?.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
        storeDescription?.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
        
        container.loadPersistentStores { description, error in
            if let error = error {
                print("❌ Core Data error: \(error.localizedDescription)")
            } else {
                print("✅ Core Data loaded: \(description)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        
        return container
    }()
    
    var context: NSManagedObjectContext {
        return persistentContainer.viewContext
    }
    
    var backgroundContext: NSManagedObjectContext {
        return persistentContainer.newBackgroundContext()
    }
    
    // MARK: - Core Data Operations
    
    func saveContext() {
        let context = persistentContainer.viewContext
        if context.hasChanges {
            do {
                try context.save()
                print("✅ Context saved successfully")
            } catch {
                print("❌ Save error: \(error.localizedDescription)")
            }
        }
    }
    
    func performBackgroundTask(_ block: @escaping (NSManagedObjectContext) -> Void) {
        persistentContainer.performBackgroundTask(block)
    }
    
    // MARK: - Fetch Operations
    
    func fetch<T: NSManagedObject>(_ entityType: T.Type, predicate: NSPredicate? = nil, sortDescriptors: [NSSortDescriptor]? = nil) -> [T] {
        let fetchRequest = NSFetchRequest<T>(entityName: String(describing: entityType))
        fetchRequest.predicate = predicate
        fetchRequest.sortDescriptors = sortDescriptors
        
        do {
            return try context.fetch(fetchRequest)
        } catch {
            print("❌ Fetch error: \(error.localizedDescription)")
            return []
        }
    }
    
    func fetchFirst<T: NSManagedObject>(_ entityType: T.Type, predicate: NSPredicate? = nil) -> T? {
        let fetchRequest = NSFetchRequest<T>(entityName: String(describing: entityType))
        fetchRequest.predicate = predicate
        fetchRequest.fetchLimit = 1
        
        do {
            return try context.fetch(fetchRequest).first
        } catch {
            print("❌ Fetch error: \(error.localizedDescription)")
            return nil
        }
    }
    
    // MARK: - Delete Operations
    
    func delete(_ object: NSManagedObject) {
        context.delete(object)
        saveContext()
    }
    
    func deleteAll<T: NSManagedObject>(_ entityType: T.Type) {
        let fetchRequest = NSFetchRequest<NSFetchRequestResult>(entityName: String(describing: entityType))
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest)
        
        do {
            try context.execute(deleteRequest)
            saveContext()
            print("✅ All \(entityType) deleted")
        } catch {
            print("❌ Delete error: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Count Operations
    
    func count<T: NSManagedObject>(_ entityType: T.Type, predicate: NSPredicate? = nil) -> Int {
        let fetchRequest = NSFetchRequest<T>(entityName: String(describing: entityType))
        fetchRequest.predicate = predicate
        
        do {
            return try context.count(for: fetchRequest)
        } catch {
            print("❌ Count error: \(error.localizedDescription)")
            return 0
        }
    }
}

// MARK: - Offline Data Manager

class OfflineDataManager {
    static let shared = OfflineDataManager()
    private let coreDataStack = CoreDataStack.shared
    
    private init() {}
    
    // MARK: - Save Operations
    
    func saveUserData(_ userData: [String: Any]) {
        coreDataStack.performBackgroundTask { context in
            // Сохранение данных пользователя
            let userEntity = NSEntityDescription.insertNewObject(forEntityName: "User", into: context)
            userEntity.setValue(userData["id"], forKey: "id")
            userEntity.setValue(userData["name"], forKey: "name")
            userEntity.setValue(userData["email"], forKey: "email")
            userEntity.setValue(Date(), forKey: "lastSync")
            
            do {
                try context.save()
                print("✅ User data saved offline")
            } catch {
                print("❌ Error saving user data: \(error.localizedDescription)")
            }
        }
    }
    
    func saveSecurityEvent(_ event: [String: Any]) {
        coreDataStack.performBackgroundTask { context in
            let eventEntity = NSEntityDescription.insertNewObject(forEntityName: "SecurityEvent", into: context)
            eventEntity.setValue(event["id"], forKey: "id")
            eventEntity.setValue(event["type"], forKey: "type")
            eventEntity.setValue(event["severity"], forKey: "severity")
            eventEntity.setValue(Date(), forKey: "timestamp")
            eventEntity.setValue(false, forKey: "synced")
            
            do {
                try context.save()
                print("✅ Security event saved offline")
            } catch {
                print("❌ Error saving security event: \(error.localizedDescription)")
            }
        }
    }
    
    func saveAnalyticsData(_ analytics: [String: Any]) {
        coreDataStack.performBackgroundTask { context in
            let analyticsEntity = NSEntityDescription.insertNewObject(forEntityName: "Analytics", into: context)
            analyticsEntity.setValue(analytics["id"], forKey: "id")
            analyticsEntity.setValue(analytics["metric"], forKey: "metric")
            analyticsEntity.setValue(analytics["value"], forKey: "value")
            analyticsEntity.setValue(Date(), forKey: "timestamp")
            analyticsEntity.setValue(false, forKey: "synced")
            
            do {
                try context.save()
                print("✅ Analytics data saved offline")
            } catch {
                print("❌ Error saving analytics: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Fetch Operations
    
    func fetchPendingSyncData() -> [[String: Any]] {
        var pendingData: [[String: Any]] = []
        
        // Fetch unsync'd security events
        let eventsPredicate = NSPredicate(format: "synced == false")
        let events = coreDataStack.fetch(NSManagedObject.self, predicate: eventsPredicate)
        
        for event in events {
            if let dict = event.dictionaryWithValues(forKeys: ["id", "type", "severity", "timestamp"]) as? [String: Any] {
                pendingData.append(dict)
            }
        }
        
        return pendingData
    }
    
    // MARK: - Sync Operations
    
    func syncWithServer(completion: @escaping (Bool) -> Void) {
        let pendingData = fetchPendingSyncData()
        
        guard !pendingData.isEmpty else {
            print("✅ No data to sync")
            completion(true)
            return
        }
        
        print("🔄 Syncing \(pendingData.count) items...")
        
        // В реальном приложении здесь был бы запрос к серверу
        DispatchQueue.global().asyncAfter(deadline: .now() + 2.0) {
            // Simulate sync
            self.markDataAsSynced()
            print("✅ Sync completed")
            completion(true)
        }
    }
    
    private func markDataAsSynced() {
        coreDataStack.performBackgroundTask { context in
            let predicate = NSPredicate(format: "synced == false")
            let fetchRequest = NSFetchRequest<NSManagedObject>(entityName: "SecurityEvent")
            fetchRequest.predicate = predicate
            
            do {
                let events = try context.fetch(fetchRequest)
                for event in events {
                    event.setValue(true, forKey: "synced")
                }
                try context.save()
                print("✅ Data marked as synced")
            } catch {
                print("❌ Error marking as synced: \(error.localizedDescription)")
            }
        }
    }
    
    // MARK: - Clear Operations
    
    func clearOldData(olderThan days: Int) {
        let calendar = Calendar.current
        guard let cutoffDate = calendar.date(byAdding: .day, value: -days, to: Date()) else {
            return
        }
        
        coreDataStack.performBackgroundTask { context in
            let predicate = NSPredicate(format: "timestamp < %@ AND synced == true", cutoffDate as NSDate)
            let fetchRequest = NSFetchRequest<NSFetchRequestResult>(entityName: "SecurityEvent")
            fetchRequest.predicate = predicate
            
            let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest)
            
            do {
                try context.execute(deleteRequest)
                print("✅ Old data cleared")
            } catch {
                print("❌ Error clearing old data: \(error.localizedDescription)")
            }
        }
    }
}

