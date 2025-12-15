import Foundation

/**
 * Менеджер кэширования для ALADDIN
 * Обеспечивает эффективное кэширование данных с TTL и приоритетами
 * Поддерживает шифрование и изоляцию между пользователями/сессиями
 */
class CacheManager: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = CacheManager()
    
    // MARK: - Configuration
    
    /// Максимальный размер кэша в байтах
    private let maxCacheSize: Int
    
    /// Максимальное время жизни кэша по умолчанию (в секундах)
    private let defaultTTL: TimeInterval
    
    /// Интервал очистки устаревших записей (в секундах)
    private let cleanupInterval: TimeInterval
    
    // MARK: - Storage
    
    /// Основное хранилище кэша
    private var cache: [String: CacheEntry] = [:]
    
    /// Очередь для управления памятью (LRU)
    private var accessOrder: [String] = []
    
    /// Текущий размер кэша в байтах
    private var currentCacheSize: Int = 0
    
    /// Таймер для очистки устаревших записей
    private var cleanupTimer: Timer?
    
    // MARK: - Statistics
    
    /// Статистика кэша
    @Published var statistics = CacheStatistics()
    
    // MARK: - Initialization
    
    private init(
        maxCacheSize: Int = 50 * 1024 * 1024, // 50 MB
        defaultTTL: TimeInterval = 300, // 5 минут
        cleanupInterval: TimeInterval = 60 // 1 минута
    ) {
        self.maxCacheSize = maxCacheSize
        self.defaultTTL = defaultTTL
        self.cleanupInterval = cleanupInterval
        
        startCleanupTimer()
    }
    
    deinit {
        cleanupTimer?.invalidate()
    }
    
    // MARK: - Public Methods
    
    // MARK: - Cache Isolation
    
    private var userCachePrefix: String {
        // Используем user ID для изоляции между пользователями
        return "user_\(getCurrentUserId())_"
    }
    
    private var sessionCachePrefix: String {
        // Используем session ID для изоляции между сессиями
        return "session_\(getCurrentSessionId())_"
    }
    
    private func getCurrentUserId() -> String {
        // TODO: Получить текущий user ID из Keychain или UserDefaults
        if let userId: String = KeychainManager.shared.load(String.self, forKey: .userPreferences) {
            return userId
        }
        return "default"
    }
    
    private func getCurrentSessionId() -> String {
        // TODO: Получить текущий session ID или создать новый
        if let sessionId = UserDefaults.standard.string(forKey: "current_session_id") {
            return sessionId
        }
        let newSessionId = UUID().uuidString
        UserDefaults.standard.set(newSessionId, forKey: "current_session_id")
        return newSessionId
    }
    
    /// Изолированный ключ для кэша
    private func isolatedKey(_ key: String) -> String {
        return "\(userCachePrefix)\(sessionCachePrefix)\(key)"
    }
    
    /**
     * Сохраняет данные в кэш
     * - Parameter data: Данные для сохранения
     * - Parameter key: Ключ для доступа к данным
     * - Parameter ttl: Время жизни в секундах (по умолчанию - defaultTTL)
     * - Parameter priority: Приоритет кэширования
     * - Parameter encrypt: Шифровать ли данные (по умолчанию true)
     */
    func store<T: Codable>(
        _ data: T,
        forKey key: String,
        ttl: TimeInterval? = nil,
        priority: CachePriority = .normal,
        encrypt: Bool = true  // По умолчанию шифруем
    ) async {
        // Кодируем данные
        guard let encodedData = try? JSONEncoder().encode(data) else {
            print("❌ Cache: Не удалось закодировать данные для \(key)")
            return
        }
        
        // Шифруем данные если нужно
        let finalData: Data
        let isEncrypted: Bool
        if encrypt {
            // Вызываем encryptData на main actor
            let encryptedData = await MainActor.run {
                return SecurityManager.shared.encryptData(encodedData)
            }
            
            guard let encrypted = encryptedData else {
                print("❌ Cache: Не удалось зашифровать данные для \(key)")
                return
            }
            finalData = encrypted
            isEncrypted = true
        } else {
            finalData = encodedData
            isEncrypted = false
        }
        
        // Используем изолированный ключ
        let isolatedKey = self.isolatedKey(key)
        
        let entry = CacheEntry(
            data: finalData,  // Теперь это зашифрованные данные
            key: isolatedKey,
            ttl: ttl ?? defaultTTL,
            priority: priority,
            createdAt: Date(),
            lastAccessed: Date(),
            isEncrypted: isEncrypted
        )
        
        // Удаляем старую запись, если она существует
        remove(key: isolatedKey)
        
        // Добавляем новую запись
        cache[isolatedKey] = entry
        accessOrder.append(isolatedKey)
        currentCacheSize += entry.size
        
        // Обновляем статистику
        statistics.totalStores += 1
        statistics.currentSize = currentCacheSize
        statistics.entryCount = cache.count
        
        print("💾 Cache: Сохранено \(key) (изолированный ключ: \(isolatedKey), размер: \(entry.size) байт, TTL: \(entry.ttl)с, зашифровано: \(isEncrypted))")
        
        // Проверяем, не превышен ли лимит размера
        if currentCacheSize > maxCacheSize {
            evictLeastRecentlyUsed()
        }
    }
    
    /**
     * Получает данные из кэша
     * - Parameter key: Ключ для доступа к данным
     * - Returns: Данные или nil, если не найдены или устарели
     */
    func retrieve<T: Codable>(_ type: T.Type, forKey key: String) async -> T? {
        // Используем изолированный ключ
        let isolatedKey = self.isolatedKey(key)
        
        guard let entry = cache[isolatedKey] else {
            statistics.totalMisses += 1
            return nil
        }
        
        // Проверяем, не устарели ли данные
        if entry.isExpired {
            remove(key: isolatedKey)
            statistics.totalMisses += 1
            statistics.expiredEntries += 1
            return nil
        }
        
        // Дешифруем данные если нужно
        let decryptedData: Data
        if entry.isEncrypted {
            guard let encryptedData = entry.data as? Data else {
                print("❌ Cache: Неверный формат зашифрованных данных для \(key)")
                return nil
            }
            
            // Вызываем decryptData на main actor
            let decrypted = await MainActor.run {
                return SecurityManager.shared.decryptData(encryptedData)
            }
            
            guard let decrypted = decrypted else {
                print("❌ Cache: Не удалось расшифровать данные для \(key)")
                return nil
            }
            decryptedData = decrypted
        } else {
            guard let data = entry.data as? Data else {
                print("❌ Cache: Неверный формат данных для \(key)")
                return nil
            }
            decryptedData = data
        }
        
        // Декодируем данные
        guard let decoded = try? JSONDecoder().decode(type, from: decryptedData) else {
            print("❌ Cache: Не удалось декодировать данные для \(key)")
            return nil
        }
        
        // Обновляем время последнего доступа
        entry.lastAccessed = Date()
        updateAccessOrder(for: isolatedKey)
        
        // Обновляем статистику
        statistics.totalHits += 1
        statistics.currentSize = currentCacheSize
        statistics.entryCount = cache.count
        
        print("💾 Cache: Получено \(key) (возраст: \(String(format: "%.1f", entry.age))с, зашифровано: \(entry.isEncrypted))")
        
        return decoded
    }
    
    /**
     * Проверяет, существует ли ключ в кэше
     * - Parameter key: Ключ для проверки
     * - Returns: true, если ключ существует и не устарел
     */
    func exists(key: String) -> Bool {
        guard let entry = cache[key] else { return false }
        return !entry.isExpired
    }
    
    /**
     * Удаляет данные из кэша
     * - Parameter key: Ключ для удаления
     */
    func remove(key: String) {
        guard let entry = cache[key] else { return }
        
        cache.removeValue(forKey: key)
        accessOrder.removeAll { $0 == key }
        currentCacheSize -= entry.size
        
        statistics.currentSize = currentCacheSize
        statistics.entryCount = cache.count
        
        print("💾 Cache: Удалено \(key)")
    }
    
    /**
     * Очищает весь кэш
     */
    func clear() {
        cache.removeAll()
        accessOrder.removeAll()
        currentCacheSize = 0
        
        statistics = CacheStatistics()
        
        print("💾 Cache: Полная очистка кэша")
    }
    
    // MARK: - Cache Isolation Methods
    
    /// Очищает кэш для текущего пользователя
    func clearUserCache() {
        let userPrefix = userCachePrefix
        let keysToRemove = cache.keys.filter { $0.hasPrefix(userPrefix) }
        
        for key in keysToRemove {
            remove(key: key)
        }
        
        print("💾 Cache: Очищен кэш для пользователя (\(keysToRemove.count) записей)")
    }
    
    /// Очищает кэш для текущей сессии
    func clearSessionCache() {
        let sessionPrefix = sessionCachePrefix
        let keysToRemove = cache.keys.filter { $0.hasPrefix(sessionPrefix) }
        
        for key in keysToRemove {
            remove(key: key)
        }
        
        print("💾 Cache: Очищен кэш для сессии (\(keysToRemove.count) записей)")
    }
    
    // MARK: - Automatic Cleanup
    
    /// Очищает кэш при выходе из приложения
    func cleanupOnAppTermination() {
        print("💾 Cache: Очистка при выходе из приложения...")
        
        // Очищаем все не критичные данные
        let criticalKeys = cache.keys.filter { key in
            guard let entry = cache[key] else { return false }
            return entry.priority == .critical
        }
        
        // Сохраняем только критичные данные
        var criticalCache: [String: CacheEntry] = [:]
        for key in criticalKeys {
            if let entry = cache[key] {
                criticalCache[key] = entry
            }
        }
        
        // Очищаем весь кэш
        clear()
        
        // Восстанавливаем критичные данные
        for (key, entry) in criticalCache {
            cache[key] = entry
            accessOrder.append(key)
            currentCacheSize += entry.size
        }
        
        print("💾 Cache: Очистка при выходе из приложения завершена (сохранено \(criticalCache.count) критичных записей)")
    }
    
    /// Очищает кэш при смене пользователя
    func cleanupOnUserChange() {
        print("💾 Cache: Очистка при смене пользователя...")
        clearUserCache()
        print("💾 Cache: Очистка при смене пользователя завершена")
    }
    
    /// Очищает кэш при смене сессии
    func cleanupOnSessionChange() {
        print("💾 Cache: Очистка при смене сессии...")
        clearSessionCache()
        
        // Создаём новую сессию
        let newSessionId = UUID().uuidString
        UserDefaults.standard.set(newSessionId, forKey: "current_session_id")
        
        print("💾 Cache: Очистка при смене сессии завершена (новая сессия: \(newSessionId))")
    }
    
    /**
     * Очищает устаревшие записи
     */
    func cleanup() {
        let expiredKeys = cache.compactMap { key, entry in
            entry.isExpired ? key : nil
        }
        
        for key in expiredKeys {
            remove(key: key)
        }
        
        statistics.expiredEntries += expiredKeys.count
        
        if !expiredKeys.isEmpty {
            print("💾 Cache: Очищено \(expiredKeys.count) устаревших записей")
        }
    }
    
    /**
     * Получает информацию о кэше
     */
    func getCacheInfo() -> CacheInfo {
        return CacheInfo(
            entryCount: cache.count,
            totalSize: currentCacheSize,
            maxSize: maxCacheSize,
            hitRate: statistics.hitRate,
            oldestEntry: getOldestEntry(),
            newestEntry: getNewestEntry()
        )
    }
    
    // MARK: - Private Methods
    
    /**
     * Обновляет порядок доступа для LRU
     */
    private func updateAccessOrder(for key: String) {
        accessOrder.removeAll { $0 == key }
        accessOrder.append(key)
    }
    
    /**
     * Удаляет наименее используемые записи
     */
    private func evictLeastRecentlyUsed() {
        while currentCacheSize > maxCacheSize && !accessOrder.isEmpty {
            let keyToRemove = accessOrder.removeFirst()
            remove(key: keyToRemove)
        }
    }
    
    /**
     * Запускает таймер очистки
     */
    private func startCleanupTimer() {
        cleanupTimer = Timer.scheduledTimer(withTimeInterval: cleanupInterval, repeats: true) { [weak self] _ in
            self?.cleanup()
        }
    }
    
    /**
     * Получает самую старую запись
     */
    private func getOldestEntry() -> String? {
        return cache.min { $0.value.createdAt < $1.value.createdAt }?.key
    }
    
    /**
     * Получает самую новую запись
     */
    private func getNewestEntry() -> String? {
        return cache.max { $0.value.createdAt < $1.value.createdAt }?.key
    }
}

// MARK: - CacheEntry

/**
 * Запись в кэше
 */
private class CacheEntry {
    let data: Any  // Может быть Data (зашифрованные) или Any (незашифрованные)
    let key: String
    let ttl: TimeInterval
    let priority: CachePriority
    let createdAt: Date
    var lastAccessed: Date
    let isEncrypted: Bool  // Флаг шифрования
    
    init(
        data: Data,  // Теперь всегда Data (зашифрованные или незашифрованные)
        key: String,
        ttl: TimeInterval,
        priority: CachePriority,
        createdAt: Date,
        lastAccessed: Date,
        isEncrypted: Bool
    ) {
        self.data = data
        self.key = key
        self.ttl = ttl
        self.priority = priority
        self.createdAt = createdAt
        self.lastAccessed = lastAccessed
        self.isEncrypted = isEncrypted
    }
    
    /// Проверяет, устарели ли данные
    var isExpired: Bool {
        return Date().timeIntervalSince(createdAt) > ttl
    }
    
    /// Возраст записи в секундах
    var age: TimeInterval {
        return Date().timeIntervalSince(createdAt)
    }
    
    /// Размер записи в байтах (точный для Data)
    var size: Int {
        if let data = data as? Data {
            return data.count
        }
        // Fallback для других типов
        return key.count * 2 + 100 // Базовый размер + ключ
    }
}

// MARK: - CachePriority

/**
 * Приоритеты кэширования
 */
enum CachePriority: Int, CaseIterable {
    case low = 0
    case normal = 1
    case high = 2
    case critical = 3
    
    var ttlMultiplier: Double {
        switch self {
        case .low:
            return 0.5
        case .normal:
            return 1.0
        case .high:
            return 2.0
        case .critical:
            return 4.0
        }
    }
}

// MARK: - CacheStatistics

/**
 * Статистика кэша
 */
struct CacheStatistics {
    var totalHits: Int = 0
    var totalMisses: Int = 0
    var totalStores: Int = 0
    var expiredEntries: Int = 0
    var currentSize: Int = 0
    var entryCount: Int = 0
    
    var hitRate: Double {
        let totalRequests = totalHits + totalMisses
        return totalRequests > 0 ? Double(totalHits) / Double(totalRequests) : 0
    }
    
    var missRate: Double {
        return 1 - hitRate
    }
    
    var averageEntrySize: Int {
        return entryCount > 0 ? currentSize / entryCount : 0
    }
}

// MARK: - CacheInfo

/**
 * Информация о кэше
 */
struct CacheInfo {
    let entryCount: Int
    let totalSize: Int
    let maxSize: Int
    let hitRate: Double
    let oldestEntry: String?
    let newestEntry: String?
    
    var sizeUsagePercentage: Double {
        return maxSize > 0 ? Double(totalSize) / Double(maxSize) : 0
    }
    
    var isNearCapacity: Bool {
        return sizeUsagePercentage > 0.8
    }
}

// MARK: - CacheManager Extensions

extension CacheManager {
    
    /**
     * Создает CacheManager для API запросов
     */
    static func api() -> CacheManager {
        return CacheManager(
            maxCacheSize: 100 * 1024 * 1024, // 100 MB
            defaultTTL: 600, // 10 минут
            cleanupInterval: 120 // 2 минуты
        )
    }
    
    /**
     * Создает CacheManager для изображений
     */
    static func images() -> CacheManager {
        return CacheManager(
            maxCacheSize: 200 * 1024 * 1024, // 200 MB
            defaultTTL: 3600, // 1 час
            cleanupInterval: 300 // 5 минут
        )
    }
    
    /**
     * Создает CacheManager для пользовательских данных
     */
    static func userData() -> CacheManager {
        return CacheManager(
            maxCacheSize: 25 * 1024 * 1024, // 25 MB
            defaultTTL: 1800, // 30 минут
            cleanupInterval: 300 // 5 минут
        )
    }
}

