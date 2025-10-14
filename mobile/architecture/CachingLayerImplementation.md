# 💾 Caching Layer - План Реализации

## 🎯 **ЧТО ЭТО ТАКОЕ?**
**Caching Layer** - это слой кэширования, который сохраняет часто используемые данные в памяти или на диске для быстрого доступа. Это как холодильник - продукты всегда под рукой, не нужно идти в магазин каждый раз.

## ⚠️ **ЗАЧЕМ НУЖНО?**
- **Ускорение загрузки** - данные доступны мгновенно
- **Экономия трафика** - меньше запросов к серверу
- **Улучшение UX** - пользователь не ждет
- **Снижение нагрузки** на сервер

## 📱 **РЕАЛИЗАЦИЯ ДЛЯ iOS (NSCache + Disk Cache)**

### Шаг 1: Создание Cache Manager
```swift
// mobile/ios/Cache/CacheManager.swift
import Foundation

class CacheManager {
    static let shared = CacheManager()
    
    // Память кэш
    private let memoryCache = NSCache<NSString, AnyObject>()
    
    // Диск кэш
    private let diskCacheURL: URL
    
    private init() {
        // Настройка памяти кэша
        memoryCache.countLimit = 100
        memoryCache.totalCostLimit = 50 * 1024 * 1024 // 50MB
        
        // Настройка диск кэша
        let cachesDirectory = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        diskCacheURL = cachesDirectory.appendingPathComponent("ALADDINCache")
        
        createCacheDirectoryIfNeeded()
    }
    
    // Сохранение в кэш
    func set<T: Codable>(_ object: T, forKey key: String, expiration: TimeInterval = 3600) {
        let cacheKey = NSString(string: key)
        
        // Сохраняем в память
        memoryCache.setObject(object as AnyObject, forKey: cacheKey)
        
        // Сохраняем на диск
        saveToDisk(object, key: key, expiration: expiration)
    }
    
    // Получение из кэша
    func get<T: Codable>(_ type: T.Type, forKey key: String) -> T? {
        let cacheKey = NSString(string: key)
        
        // Сначала проверяем память
        if let cachedObject = memoryCache.object(forKey: cacheKey) as? T {
            return cachedObject
        }
        
        // Затем проверяем диск
        if let diskObject = loadFromDisk(type, key: key) {
            // Восстанавливаем в память
            memoryCache.setObject(diskObject as AnyObject, forKey: cacheKey)
            return diskObject
        }
        
        return nil
    }
    
    // Очистка кэша
    func clearCache() {
        memoryCache.removeAllObjects()
        clearDiskCache()
    }
    
    // Проверка истечения
    private func isExpired(key: String) -> Bool {
        let fileURL = diskCacheURL.appendingPathComponent(key)
        
        guard let attributes = try? FileManager.default.attributesOfItem(atPath: fileURL.path),
              let modificationDate = attributes[.modificationDate] as? Date else {
            return true
        }
        
        return Date().timeIntervalSince(modificationDate) > 3600 // 1 час
    }
}
```

### Шаг 2: Создание Cacheable Protocol
```swift
// mobile/ios/Cache/Cacheable.swift
protocol Cacheable {
    var cacheKey: String { get }
    var cacheExpiration: TimeInterval { get }
}

extension SecurityEvent: Cacheable {
    var cacheKey: String {
        return "security_event_\(id)"
    }
    
    var cacheExpiration: TimeInterval {
        return 1800 // 30 минут
    }
}

extension FamilyMember: Cacheable {
    var cacheKey: String {
        return "family_member_\(id)"
    }
    
    var cacheExpiration: TimeInterval {
        return 3600 // 1 час
    }
}
```

### Шаг 3: Создание Cached Repository
```swift
// mobile/ios/Data/Repository/CachedRepository.swift
class CachedRepository {
    private let cacheManager = CacheManager.shared
    private let networkManager: NetworkManagerProtocol
    
    init(networkManager: NetworkManagerProtocol) {
        self.networkManager = networkManager
    }
    
    // Получение данных с кэшированием
    func getSecurityEvents(completion: @escaping (Result<[SecurityEvent], Error>) -> Void) {
        let cacheKey = "security_events"
        
        // Сначала проверяем кэш
        if let cachedEvents = cacheManager.get([SecurityEvent].self, forKey: cacheKey) {
            completion(.success(cachedEvents))
            return
        }
        
        // Если нет в кэше, загружаем с сервера
        networkManager.fetchSecurityEvents { [weak self] result in
            switch result {
            case .success(let events):
                // Сохраняем в кэш
                self?.cacheManager.set(events, forKey: cacheKey)
                completion(.success(events))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // Инвалидация кэша
    func invalidateCache(forKey key: String) {
        cacheManager.removeObject(forKey: key)
    }
}
```

## 🤖 **РЕАЛИЗАЦИЯ ДЛЯ ANDROID (LruCache + DiskLruCache)**

### Шаг 1: Создание Cache Manager
```kotlin
// mobile/android/Cache/CacheManager.kt
class CacheManager @Inject constructor(
    private val context: Context
) {
    // Память кэш
    private val memoryCache = LruCache<String, Any>(100)
    
    // Диск кэш
    private val diskCache: DiskLruCache
    
    init {
        val cacheDir = File(context.cacheDir, "aladdin_cache")
        diskCache = DiskLruCache.open(cacheDir, 1, 1, 50 * 1024 * 1024) // 50MB
    }
    
    // Сохранение в кэш
    fun <T> set(key: String, value: T, expiration: Long = 3600000) {
        // Сохраняем в память
        memoryCache.put(key, value)
        
        // Сохраняем на диск
        saveToDisk(key, value, expiration)
    }
    
    // Получение из кэша
    @Suppress("UNCHECKED_CAST")
    fun <T> get(key: String, type: Class<T>): T? {
        // Сначала проверяем память
        val memoryValue = memoryCache.get(key)
        if (memoryValue != null) {
            return memoryValue as T
        }
        
        // Затем проверяем диск
        val diskValue = loadFromDisk(key, type)
        if (diskValue != null) {
            // Восстанавливаем в память
            memoryCache.put(key, diskValue)
            return diskValue as T
        }
        
        return null
    }
    
    // Очистка кэша
    fun clearCache() {
        memoryCache.evictAll()
        diskCache.delete()
    }
    
    // Проверка истечения
    private fun isExpired(key: String): Boolean {
        val snapshot = diskCache.get(key)
        return snapshot?.getLength(0)?.let { length ->
            val lastModified = snapshot.getLastModified(0)
            System.currentTimeMillis() - lastModified > 3600000 // 1 час
        } ?: true
    }
}
```

### Шаг 2: Создание Cacheable Interface
```kotlin
// mobile/android/Cache/Cacheable.kt
interface Cacheable {
    val cacheKey: String
    val cacheExpiration: Long
}

data class SecurityEvent(
    val id: String,
    val timestamp: Date,
    val type: String,
    val severity: String,
    val description: String
) : Cacheable {
    override val cacheKey: String
        get() = "security_event_$id"
    
    override val cacheExpiration: Long
        get() = 1800000 // 30 минут
}

data class FamilyMember(
    val id: String,
    val name: String,
    val age: Int,
    val role: String,
    val isActive: Boolean,
    val lastSeen: Date
) : Cacheable {
    override val cacheKey: String
        get() = "family_member_$id"
    
    override val cacheExpiration: Long
        get() = 3600000 // 1 час
}
```

### Шаг 3: Создание Cached Repository
```kotlin
// mobile/android/Data/Repository/CachedRepository.kt
class CachedRepository @Inject constructor(
    private val cacheManager: CacheManager,
    private val networkManager: NetworkManager
) {
    
    // Получение данных с кэшированием
    suspend fun getSecurityEvents(): Result<List<SecurityEvent>> {
        val cacheKey = "security_events"
        
        // Сначала проверяем кэш
        val cachedEvents = cacheManager.get(cacheKey, List::class.java)
        if (cachedEvents != null) {
            return Result.success(cachedEvents as List<SecurityEvent>)
        }
        
        // Если нет в кэше, загружаем с сервера
        return try {
            val events = networkManager.fetchSecurityEvents()
            // Сохраняем в кэш
            cacheManager.set(cacheKey, events)
            Result.success(events)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Инвалидация кэша
    fun invalidateCache(key: String) {
        cacheManager.remove(key)
    }
}
```

## 📋 **ПЛАН ВНЕДРЕНИЯ (1 неделя)**

### День 1-2: Создание Cache Manager
- [ ] Реализовать CacheManager для iOS
- [ ] Реализовать CacheManager для Android
- [ ] Написать unit тесты

### День 3-4: Интеграция с Repository
- [ ] Создать CachedRepository для iOS
- [ ] Создать CachedRepository для Android
- [ ] Интегрировать с существующими API

### День 5-7: Оптимизация и тестирование
- [ ] Настроить размеры кэша
- [ ] Реализовать стратегии инвалидации
- [ ] Тестирование производительности

## 🎨 **UI ИНДИКАТОРЫ КЭША**

### Индикатор загрузки из кэша
```swift
// iOS
class CacheIndicatorView: UIView {
    @IBOutlet weak var cacheLabel: UILabel!
    @IBOutlet weak var cacheIcon: UIImageView!
    
    func showCacheStatus(_ isFromCache: Bool) {
        cacheIcon.image = isFromCache ? UIImage(systemName: "externaldrive.fill") : UIImage(systemName: "wifi")
        cacheLabel.text = isFromCache ? "Из кэша" : "С сервера"
    }
}
```

```kotlin
// Android
class CacheIndicatorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {
    
    private val cacheIcon: ImageView = ImageView(context)
    private val cacheLabel: TextView = TextView(context)
    
    fun showCacheStatus(isFromCache: Boolean) {
        cacheIcon.setImageResource(if (isFromCache) R.drawable.ic_cache else R.drawable.ic_wifi)
        cacheLabel.text = if (isFromCache) "Из кэша" else "С сервера"
    }
}
```

## ⚠️ **ВАЖНЫЕ МОМЕНТЫ**

### ✅ **ПЛЮСЫ:**
- Значительное ускорение загрузки
- Экономия трафика и батареи
- Улучшение пользовательского опыта
- Снижение нагрузки на сервер

### ⚠️ **МИНУСЫ:**
- Увеличение потребления памяти
- Сложность управления кэшем
- Потенциальные проблемы с актуальностью данных
- Необходимость стратегий инвалидации

## 📊 **МЕТРИКИ УСПЕХА**
- [ ] 90%+ запросов обслуживаются из кэша
- [ ] <100ms время загрузки из кэша
- [ ] 50%+ экономия трафика
- [ ] <10MB дополнительного потребления памяти

---

*Критически важно для производительности семейного приложения!*

