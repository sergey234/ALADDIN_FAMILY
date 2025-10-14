package com.aladdin.mobile.data

import android.content.Context
import androidx.room.*
import androidx.sqlite.db.SupportSQLiteDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

// MARK: - Database

@Database(
    entities = [
        UserEntity::class,
        SecurityEventEntity::class,
        AnalyticsEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class ALADDINDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun securityEventDao(): SecurityEventDao
    abstract fun analyticsDao(): AnalyticsDao
    
    companion object {
        @Volatile
        private var INSTANCE: ALADDINDatabase? = null
        
        fun getDatabase(context: Context): ALADDINDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    ALADDINDatabase::class.java,
                    "aladdin_database"
                )
                    .fallbackToDestructiveMigration()
                    .addCallback(DatabaseCallback())
                    .build()
                
                INSTANCE = instance
                instance
            }
        }
    }
    
    private class DatabaseCallback : RoomDatabase.Callback() {
        override fun onCreate(db: SupportSQLiteDatabase) {
            super.onCreate(db)
            android.util.Log.i("ALADDINDatabase", "Database created")
        }
        
        override fun onOpen(db: SupportSQLiteDatabase) {
            super.onOpen(db)
            android.util.Log.i("ALADDINDatabase", "Database opened")
        }
    }
}

// MARK: - Entities

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "email") val email: String,
    @ColumnInfo(name = "last_sync") val lastSync: Long
)

@Entity(tableName = "security_events")
data class SecurityEventEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "type") val type: String,
    @ColumnInfo(name = "severity") val severity: String,
    @ColumnInfo(name = "timestamp") val timestamp: Long,
    @ColumnInfo(name = "synced") val synced: Boolean = false
)

@Entity(tableName = "analytics")
data class AnalyticsEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "metric") val metric: String,
    @ColumnInfo(name = "value") val value: String,
    @ColumnInfo(name = "timestamp") val timestamp: Long,
    @ColumnInfo(name = "synced") val synced: Boolean = false
)

// MARK: - DAOs

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<UserEntity>
    
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: String): UserEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)
    
    @Update
    suspend fun updateUser(user: UserEntity)
    
    @Delete
    suspend fun deleteUser(user: UserEntity)
    
    @Query("DELETE FROM users")
    suspend fun deleteAllUsers()
}

@Dao
interface SecurityEventDao {
    @Query("SELECT * FROM security_events ORDER BY timestamp DESC")
    suspend fun getAllEvents(): List<SecurityEventEntity>
    
    @Query("SELECT * FROM security_events WHERE synced = 0")
    suspend fun getUnsyncedEvents(): List<SecurityEventEntity>
    
    @Query("SELECT * FROM security_events WHERE id = :eventId")
    suspend fun getEventById(eventId: String): SecurityEventEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEvent(event: SecurityEventEntity)
    
    @Update
    suspend fun updateEvent(event: SecurityEventEntity)
    
    @Delete
    suspend fun deleteEvent(event: SecurityEventEntity)
    
    @Query("DELETE FROM security_events WHERE timestamp < :cutoffTime AND synced = 1")
    suspend fun deleteOldSyncedEvents(cutoffTime: Long)
    
    @Query("UPDATE security_events SET synced = 1 WHERE id IN (:eventIds)")
    suspend fun markEventsAsSynced(eventIds: List<String>)
}

@Dao
interface AnalyticsDao {
    @Query("SELECT * FROM analytics ORDER BY timestamp DESC")
    suspend fun getAllAnalytics(): List<AnalyticsEntity>
    
    @Query("SELECT * FROM analytics WHERE synced = 0")
    suspend fun getUnsyncedAnalytics(): List<AnalyticsEntity>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAnalytics(analytics: AnalyticsEntity)
    
    @Update
    suspend fun updateAnalytics(analytics: AnalyticsEntity)
    
    @Delete
    suspend fun deleteAnalytics(analytics: AnalyticsEntity)
    
    @Query("DELETE FROM analytics WHERE timestamp < :cutoffTime AND synced = 1")
    suspend fun deleteOldSyncedAnalytics(cutoffTime: Long)
    
    @Query("UPDATE analytics SET synced = 1 WHERE id IN (:analyticsIds)")
    suspend fun markAnalyticsAsSynced(analyticsIds: List<String>)
}

// MARK: - Offline Data Manager

@Singleton
class OfflineDataManager @Inject constructor(
    private val database: ALADDINDatabase
) {
    
    // MARK: - Save Operations
    
    suspend fun saveUserData(userData: Map<String, Any>) {
        try {
            val user = UserEntity(
                id = userData["id"] as? String ?: "",
                name = userData["name"] as? String ?: "",
                email = userData["email"] as? String ?: "",
                lastSync = System.currentTimeMillis()
            )
            
            database.userDao().insertUser(user)
            android.util.Log.i("OfflineDataManager", "User data saved offline")
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error saving user data", e)
        }
    }
    
    suspend fun saveSecurityEvent(event: Map<String, Any>) {
        try {
            val securityEvent = SecurityEventEntity(
                id = event["id"] as? String ?: java.util.UUID.randomUUID().toString(),
                type = event["type"] as? String ?: "",
                severity = event["severity"] as? String ?: "",
                timestamp = System.currentTimeMillis(),
                synced = false
            )
            
            database.securityEventDao().insertEvent(securityEvent)
            android.util.Log.i("OfflineDataManager", "Security event saved offline")
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error saving security event", e)
        }
    }
    
    suspend fun saveAnalyticsData(analytics: Map<String, Any>) {
        try {
            val analyticsEntity = AnalyticsEntity(
                id = analytics["id"] as? String ?: java.util.UUID.randomUUID().toString(),
                metric = analytics["metric"] as? String ?: "",
                value = analytics["value"] as? String ?: "",
                timestamp = System.currentTimeMillis(),
                synced = false
            )
            
            database.analyticsDao().insertAnalytics(analyticsEntity)
            android.util.Log.i("OfflineDataManager", "Analytics data saved offline")
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error saving analytics", e)
        }
    }
    
    // MARK: - Fetch Operations
    
    suspend fun fetchPendingSyncData(): List<Map<String, Any>> {
        val pendingData = mutableListOf<Map<String, Any>>()
        
        try {
            // Fetch unsynced security events
            val events = database.securityEventDao().getUnsyncedEvents()
            for (event in events) {
                pendingData.add(
                    mapOf(
                        "id" to event.id,
                        "type" to event.type,
                        "severity" to event.severity,
                        "timestamp" to event.timestamp
                    )
                )
            }
            
            // Fetch unsynced analytics
            val analytics = database.analyticsDao().getUnsyncedAnalytics()
            for (analytic in analytics) {
                pendingData.add(
                    mapOf(
                        "id" to analytic.id,
                        "metric" to analytic.metric,
                        "value" to analytic.value,
                        "timestamp" to analytic.timestamp
                    )
                )
            }
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error fetching pending data", e)
        }
        
        return pendingData
    }
    
    // MARK: - Sync Operations
    
    suspend fun syncWithServer(): Boolean {
        return try {
            val pendingData = fetchPendingSyncData()
            
            if (pendingData.isEmpty()) {
                android.util.Log.i("OfflineDataManager", "No data to sync")
                return true
            }
            
            android.util.Log.i("OfflineDataManager", "Syncing ${pendingData.size} items...")
            
            // В реальном приложении здесь был бы запрос к серверу
            kotlinx.coroutines.delay(2000) // Simulate network request
            
            // Mark data as synced
            markDataAsSynced()
            
            android.util.Log.i("OfflineDataManager", "Sync completed")
            true
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Sync error", e)
            false
        }
    }
    
    private suspend fun markDataAsSynced() {
        try {
            val events = database.securityEventDao().getUnsyncedEvents()
            val eventIds = events.map { it.id }
            database.securityEventDao().markEventsAsSynced(eventIds)
            
            val analytics = database.analyticsDao().getUnsyncedAnalytics()
            val analyticsIds = analytics.map { it.id }
            database.analyticsDao().markAnalyticsAsSynced(analyticsIds)
            
            android.util.Log.i("OfflineDataManager", "Data marked as synced")
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error marking as synced", e)
        }
    }
    
    // MARK: - Clear Operations
    
    suspend fun clearOldData(olderThanDays: Int) {
        try {
            val cutoffTime = System.currentTimeMillis() - (olderThanDays * 24 * 60 * 60 * 1000L)
            
            database.securityEventDao().deleteOldSyncedEvents(cutoffTime)
            database.analyticsDao().deleteOldSyncedAnalytics(cutoffTime)
            
            android.util.Log.i("OfflineDataManager", "Old data cleared")
        } catch (e: Exception) {
            android.util.Log.e("OfflineDataManager", "Error clearing old data", e)
        }
    }
}

