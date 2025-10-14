package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 🔔 Notifications View Model
 * Логика для экрана уведомлений
 * Источник: iOS NotificationsViewModel.swift
 */

data class AppNotificationItem(
    val id: String,
    val icon: String,
    val title: String,
    val message: String,
    val time: String,
    val isRead: Boolean,
    val type: NotificationType
)

enum class NotificationType {
    THREAT, SUCCESS, INFO, WARNING
}

class NotificationsViewModel : ViewModel() {
    
    // MARK: - State
    
    private val _notifications = MutableStateFlow<List<AppNotificationItem>>(emptyList())
    val notifications: StateFlow<List<AppNotificationItem>> = _notifications
    
    private val _unreadCount = MutableStateFlow(0)
    val unreadCount: StateFlow<Int> = _unreadCount
    
    // MARK: - Init
    
    init {
        loadNotifications()
    }
    
    // MARK: - Public Methods
    
    /**
     * Загрузить уведомления
     */
    fun loadNotifications() {
        _notifications.value = listOf(
            AppNotificationItem(
                id = "1",
                icon = "🛡️",
                title = "Угроза заблокирована",
                message = "Заблокирован вредоносный сайт",
                time = "5 мин назад",
                isRead = false,
                type = NotificationType.THREAT
            ),
            AppNotificationItem(
                id = "2",
                icon = "✅",
                title = "VPN подключён",
                message = "Ваше соединение защищено",
                time = "1 час назад",
                isRead = true,
                type = NotificationType.SUCCESS
            ),
            AppNotificationItem(
                id = "3",
                icon = "⚠️",
                title = "Подозрительная активность",
                message = "Обнаружена попытка доступа",
                time = "2 часа назад",
                isRead = true,
                type = NotificationType.WARNING
            ),
            AppNotificationItem(
                id = "4",
                icon = "ℹ️",
                title = "Обновление доступно",
                message = "Доступна новая версия ALADDIN",
                time = "Вчера",
                isRead = true,
                type = NotificationType.INFO
            )
        )
        updateUnreadCount()
    }
    
    /**
     * Отметить уведомление как прочитанное
     */
    fun markAsRead(notificationId: String) {
        _notifications.value = _notifications.value.map {
            if (it.id == notificationId) {
                it.copy(isRead = true)
            } else {
                it
            }
        }
        updateUnreadCount()
    }
    
    /**
     * Отметить все как прочитанные
     */
    fun markAllAsRead() {
        _notifications.value = _notifications.value.map { it.copy(isRead = true) }
        updateUnreadCount()
    }
    
    /**
     * Удалить уведомление
     */
    fun deleteNotification(notificationId: String) {
        _notifications.value = _notifications.value.filter { it.id != notificationId }
        updateUnreadCount()
    }
    
    /**
     * Очистить все уведомления
     */
    fun clearAll() {
        _notifications.value = emptyList()
        _unreadCount.value = 0
    }
    
    // MARK: - Private Methods
    
    private fun updateUnreadCount() {
        _unreadCount.value = _notifications.value.count { !it.isRead }
    }
}



