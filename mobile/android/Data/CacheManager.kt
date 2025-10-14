package com.aladdin.mobile.data

import android.content.Context
import android.util.LruCache
import com.google.gson.Gson
import java.io.File
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CacheManager @Inject constructor(
    private val context: Context
) {
    
    private val memoryCache: LruCache<String, Any>
    private val gson = Gson()
    private val cacheDirectory: File
    
    init {
        // Настройка memory cache (20% от доступной памяти)
        val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
        val cacheSize = maxMemory / 5
        
        memoryCache = LruCache(cacheSize)
        
        // Настройка кэш директории
        cacheDirectory = File(context.cacheDir, "ALADDINCache")
        if (!cacheDirectory.exists()) {
            cacheDirectory.mkdirs()
        }
        
        android.util.Log.i("CacheManager", "Initialized with cache size: ${cacheSize}KB")
    }
    
    // MARK: - Memory Cache
    
    fun cacheInMemory(key: String, value: Any) {
        memoryCache.put(key, value)
        android.util.Log.i("CacheManager", "Cached in memory: $key")
    }
    
    fun getFromMemory(key: String): Any? {
        return memoryCache.get(key)
    }
    
    fun removeFromMemory(key: String) {
        memoryCache.remove(key)
    }
    
    fun clearMemoryCache() {
        memoryCache.evictAll()
        android.util.Log.i("CacheManager", "Memory cache cleared")
    }
    
    // MARK: - Disk Cache
    
    fun <T> cacheToDisk(key: String, value: T) {
        val file = File(cacheDirectory, key)
        
        try {
            val json = gson.toJson(value)
            file.writeText(json)
            android.util.Log.i("CacheManager", "Cached to disk: $key")
        } catch (e: IOException) {
            android.util.Log.e("CacheManager", "Disk cache error", e)
        }
    }
    
    fun <T> getFromDisk(key: String, classOfT: Class<T>): T? {
        val file = File(cacheDirectory, key)
        
        if (!file.exists()) {
            return null
        }
        
        return try {
            val json = file.readText()
            gson.fromJson(json, classOfT)
        } catch (e: IOException) {
            android.util.Log.e("CacheManager", "Disk read error", e)
            null
        }
    }
    
    fun removeFromDisk(key: String) {
        val file = File(cacheDirectory, key)
        if (file.exists()) {
            file.delete()
        }
    }
    
    fun clearDiskCache() {
        cacheDirectory.deleteRecursively()
        cacheDirectory.mkdirs()
        android.util.Log.i("CacheManager", "Disk cache cleared")
    }
    
    // MARK: - Hybrid Cache (Memory + Disk)
    
    fun <T> cache(key: String, value: T) {
        // Memory cache
        cacheInMemory(key, value as Any)
        
        // Disk cache
        cacheToDisk(key, value)
    }
    
    fun <T> get(key: String, classOfT: Class<T>): T? {
        // Try memory cache first
        val memoryValue = getFromMemory(key)
        if (memoryValue != null && classOfT.isInstance(memoryValue)) {
            android.util.Log.i("CacheManager", "Hit memory cache: $key")
            return classOfT.cast(memoryValue)
        }
        
        // Try disk cache
        val diskValue = getFromDisk(key, classOfT)
        if (diskValue != null) {
            android.util.Log.i("CacheManager", "Hit disk cache: $key")
            // Cache to memory for faster access
            cacheInMemory(key, diskValue as Any)
            return diskValue
        }
        
        android.util.Log.i("CacheManager", "Cache miss: $key")
        return null
    }
    
    fun remove(key: String) {
        removeFromMemory(key)
        removeFromDisk(key)
    }
    
    // MARK: - Cache Management
    
    fun getCacheSize(): Long {
        return cacheDirectory.walkTopDown()
            .filter { it.isFile }
            .map { it.length() }
            .sum()
    }
    
    fun clearAllCache() {
        clearMemoryCache()
        clearDiskCache()
        android.util.Log.i("CacheManager", "All cache cleared")
    }
    
    fun cleanupOldCache(olderThanDays: Int) {
        val cutoffTime = System.currentTimeMillis() - (olderThanDays * 24 * 60 * 60 * 1000L)
        
        cacheDirectory.walkTopDown()
            .filter { it.isFile && it.lastModified() < cutoffTime }
            .forEach { it.delete() }
        
        android.util.Log.i("CacheManager", "Old cache cleaned up")
    }
    
    // MARK: - Cache Statistics
    
    fun getCacheStatistics(): CacheStatistics {
        val totalFiles = cacheDirectory.walkTopDown().filter { it.isFile }.count()
        val totalSize = getCacheSize()
        val memoryCacheSize = memoryCache.size()
        
        return CacheStatistics(
            totalFiles = totalFiles,
            totalSizeBytes = totalSize,
            totalSizeMB = totalSize / (1024 * 1024),
            memoryCacheEntries = memoryCacheSize
        )
    }
}

// MARK: - Data Models

data class CacheStatistics(
    val totalFiles: Int,
    val totalSizeBytes: Long,
    val totalSizeMB: Long,
    val memoryCacheEntries: Int
)

