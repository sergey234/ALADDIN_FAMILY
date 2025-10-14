import Foundation

class CacheManager {
    static let shared = CacheManager()
    
    private let memoryCache = NSCache<NSString, AnyObject>()
    private let fileManager = FileManager.default
    private let cacheDirectory: URL
    
    private init() {
        // Настройка кэш директории
        let paths = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)
        cacheDirectory = paths[0].appendingPathComponent("ALADDINCache")
        
        // Создаем директорию если не существует
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
        
        // Настройка memory cache
        memoryCache.countLimit = 100
        memoryCache.totalCostLimit = 50 * 1024 * 1024 // 50 MB
    }
    
    // MARK: - Memory Cache
    
    func cacheInMemory(_ object: AnyObject, forKey key: String) {
        memoryCache.setObject(object, forKey: key as NSString)
        print("✅ Cached in memory: \(key)")
    }
    
    func getFromMemory(forKey key: String) -> AnyObject? {
        return memoryCache.object(forKey: key as NSString)
    }
    
    func removeFromMemory(forKey key: String) {
        memoryCache.removeObject(forKey: key as NSString)
    }
    
    func clearMemoryCache() {
        memoryCache.removeAllObjects()
        print("✅ Memory cache cleared")
    }
    
    // MARK: - Disk Cache
    
    func cacheToDisk<T: Codable>(_ object: T, forKey key: String) {
        let fileURL = cacheDirectory.appendingPathComponent(key)
        
        do {
            let data = try JSONEncoder().encode(object)
            try data.write(to: fileURL)
            print("✅ Cached to disk: \(key)")
        } catch {
            print("❌ Disk cache error: \(error.localizedDescription)")
        }
    }
    
    func getFromDisk<T: Codable>(forKey key: String, as type: T.Type) -> T? {
        let fileURL = cacheDirectory.appendingPathComponent(key)
        
        guard fileManager.fileExists(atPath: fileURL.path) else {
            return nil
        }
        
        do {
            let data = try Data(contentsOf: fileURL)
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            print("❌ Disk read error: \(error.localizedDescription)")
            return nil
        }
    }
    
    func removeFromDisk(forKey key: String) {
        let fileURL = cacheDirectory.appendingPathComponent(key)
        try? fileManager.removeItem(at: fileURL)
    }
    
    func clearDiskCache() {
        try? fileManager.removeItem(at: cacheDirectory)
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
        print("✅ Disk cache cleared")
    }
    
    // MARK: - Hybrid Cache (Memory + Disk)
    
    func cache<T: Codable>(_ object: T, forKey key: String) {
        // Memory cache
        cacheInMemory(object as AnyObject, forKey: key)
        
        // Disk cache
        cacheToDisk(object, forKey: key)
    }
    
    func get<T: Codable>(forKey key: String, as type: T.Type) -> T? {
        // Try memory cache first
        if let cachedObject = getFromMemory(forKey: key) as? T {
            print("✅ Hit memory cache: \(key)")
            return cachedObject
        }
        
        // Try disk cache
        if let diskObject = getFromDisk(forKey: key, as: type) {
            print("✅ Hit disk cache: \(key)")
            // Cache to memory for faster access
            cacheInMemory(diskObject as AnyObject, forKey: key)
            return diskObject
        }
        
        print("❌ Cache miss: \(key)")
        return nil
    }
    
    // MARK: - Cache Management
    
    func getCacheSize() -> Int64 {
        var totalSize: Int64 = 0
        
        guard let enumerator = fileManager.enumerator(at: cacheDirectory, includingPropertiesForKeys: [.fileSizeKey]) else {
            return 0
        }
        
        for case let fileURL as URL in enumerator {
            if let fileSize = try? fileURL.resourceValues(forKeys: [.fileSizeKey]).fileSize {
                totalSize += Int64(fileSize)
            }
        }
        
        return totalSize
    }
    
    func clearAllCache() {
        clearMemoryCache()
        clearDiskCache()
        print("✅ All cache cleared")
    }
    
    func cleanupOldCache(olderThan days: Int) {
        let cutoffDate = Date().addingTimeInterval(-TimeInterval(days * 24 * 60 * 60))
        
        guard let enumerator = fileManager.enumerator(at: cacheDirectory, includingPropertiesForKeys: [.contentModificationDateKey]) else {
            return
        }
        
        for case let fileURL as URL in enumerator {
            if let modificationDate = try? fileURL.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate,
               modificationDate < cutoffDate {
                try? fileManager.removeItem(at: fileURL)
            }
        }
        
        print("✅ Old cache cleaned up")
    }
}

