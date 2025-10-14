/**
 * VPN Activity Tracker
 * Отслеживает активность пользователя и уведомляет VPN клиент
 * для управления энергосберегающими режимами
 */

class VPNActivityTracker {
    constructor() {
        this.lastActivityTime = Date.now();
        this.activityLog = [];
        this.maxLogSize = 100;
        this.isInitialized = false;
        
        // Настройки
        this.settings = {
            logToConsole: true,
            sendToBackend: false,  // TODO: Включить когда будет API
            updateInterval: 30000   // 30 секунд
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        console.log('⚡ VPN Activity Tracker: Инициализация...');
        
        // Отслеживаем все типы активности
        const events = [
            'touchstart', 'touchmove', 'touchend',
            'mousedown', 'mousemove', 'mouseup',
            'scroll', 'keypress', 'click',
            'input', 'change'
        ];
        
        events.forEach(event => {
            document.addEventListener(event, (e) => this.recordActivity(event, e), 
                { passive: true, capture: true });
        });
        
        // Отслеживаем фокус/блюр окна
        window.addEventListener('focus', () => this.recordActivity('window_focus'));
        window.addEventListener('blur', () => this.recordActivity('window_blur'));
        
        // Отслеживаем видимость страницы
        document.addEventListener('visibilitychange', () => {
            this.recordActivity(document.hidden ? 'page_hidden' : 'page_visible');
        });
        
        // Периодически проверяем idle время
        setInterval(() => this.checkIdleStatus(), 60000); // каждую минуту
        
        // Периодически отправляем статус
        setInterval(() => this.sendStatusToVPN(), this.settings.updateInterval);
        
        this.isInitialized = true;
        console.log('✅ VPN Activity Tracker: Активирован');
    }
    
    recordActivity(type, event = null) {
        const now = Date.now();
        const timeSinceLastActivity = now - this.lastActivityTime;
        
        // Обновляем время последней активности
        this.lastActivityTime = now;
        
        // Добавляем в лог
        const logEntry = {
            type,
            timestamp: now,
            timeSinceLastActivity,
            page: window.location.pathname
        };
        
        this.activityLog.push(logEntry);
        
        // Ограничиваем размер лога
        if (this.activityLog.length > this.maxLogSize) {
            this.activityLog.shift();
        }
        
        // Если это первая активность после долгого бездействия
        if (timeSinceLastActivity > 300000) { // 5 минут
            this.onWakeUp(timeSinceLastActivity);
        }
        
        // Уведомляем VPN клиент о активности
        this.notifyVPNActivity();
    }
    
    onWakeUp(idleTime) {
        const idleMinutes = Math.floor(idleTime / 60000);
        console.log(`⚡ Пробуждение после ${idleMinutes} минут бездействия`);
        
        // Отправляем событие пробуждения
        this.sendEventToVPN('wake_up', {
            idle_time: idleTime,
            idle_minutes: idleMinutes
        });
        
        // Показываем уведомление пользователю
        if (idleMinutes > 15) {
            this.showNotification(
                `⚡ VPN возобновил полную защиту после ${idleMinutes} минут`,
                'info'
            );
        }
    }
    
    checkIdleStatus() {
        const idleTime = this.getIdleTime();
        const idleMinutes = Math.floor(idleTime / 60000);
        
        if (this.settings.logToConsole) {
            console.log(`⏱️ Idle time: ${idleMinutes} минут`);
        }
        
        // Уведомляем об изменении статуса
        if (idleMinutes === 5) {
            this.showNotification('⚡ VPN переключён в обычный режим', 'info');
        } else if (idleMinutes === 15) {
            this.showNotification('⚡ VPN переключён в экономный режим', 'info');
        } else if (idleMinutes === 30) {
            this.showNotification('💤 VPN отключен для экономии батареи', 'warning');
        }
        
        // Отправляем статус
        this.sendEventToVPN('idle_check', {
            idle_time: idleTime,
            idle_minutes: idleMinutes
        });
    }
    
    getIdleTime() {
        return Date.now() - this.lastActivityTime;
    }
    
    getIdleMinutes() {
        return Math.floor(this.getIdleTime() / 60000);
    }
    
    notifyVPNActivity() {
        // Отправляем в VPN клиент через API
        if (this.settings.sendToBackend) {
            this.sendEventToVPN('user_activity', {
                timestamp: Date.now(),
                page: window.location.pathname
            });
        }
        
        // Обновляем localStorage для других вкладок
        localStorage.setItem('vpn_last_activity', Date.now().toString());
    }
    
    sendEventToVPN(eventType, data) {
        // TODO: Реальная отправка через API
        const event = {
            event: eventType,
            data: data,
            timestamp: Date.now()
        };
        
        if (this.settings.logToConsole) {
            console.log('📤 Отправка в VPN:', event);
        }
        
        // Сохраняем в localStorage для симуляции
        const events = JSON.parse(localStorage.getItem('vpn_events') || '[]');
        events.push(event);
        if (events.length > 50) events.shift();
        localStorage.setItem('vpn_events', JSON.stringify(events));
    }
    
    sendStatusToVPN() {
        const status = this.getStatus();
        
        if (this.settings.sendToBackend) {
            this.sendEventToVPN('status_update', status);
        }
    }
    
    getStatus() {
        const idleTime = this.getIdleTime();
        const idleMinutes = this.getIdleMinutes();
        
        return {
            idle_time: idleTime,
            idle_minutes: idleMinutes,
            last_activity: this.lastActivityTime,
            activity_count: this.activityLog.length,
            current_page: window.location.pathname,
            is_visible: !document.hidden,
            has_focus: document.hasFocus()
        };
    }
    
    getStats() {
        const status = this.getStatus();
        const activityTypes = {};
        
        // Подсчитываем типы активности
        this.activityLog.forEach(log => {
            activityTypes[log.type] = (activityTypes[log.type] || 0) + 1;
        });
        
        return {
            ...status,
            activity_types: activityTypes,
            total_events: this.activityLog.length
        };
    }
    
    showNotification(message, type = 'info') {
        // Проверяем, не показываем ли мы уже такое же уведомление
        const lastNotification = localStorage.getItem('last_vpn_notification');
        if (lastNotification === message) return;
        
        localStorage.setItem('last_vpn_notification', message);
        
        const notification = document.createElement('div');
        notification.textContent = message;
        
        const colors = {
            'info': '#3B82F6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: ${colors[type] || colors.info};
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 500;
            z-index: 10001;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 280px;
            text-align: center;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
            localStorage.removeItem('last_vpn_notification');
        }, 3000);
    }
    
    // Публичные методы для отладки
    debug() {
        console.log('=== VPN Activity Tracker Debug ===');
        console.log('Status:', this.getStatus());
        console.log('Stats:', this.getStats());
        console.log('Recent Activity:', this.activityLog.slice(-10));
    }
}

// Глобальная инициализация
let vpnActivityTracker;

// Инициализируем при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        vpnActivityTracker = new VPNActivityTracker();
    });
} else {
    vpnActivityTracker = new VPNActivityTracker();
}

// Экспортируем для использования в других скриптах
window.VPNActivityTracker = VPNActivityTracker;
window.vpnActivityTracker = vpnActivityTracker;

console.log('📦 VPN Activity Tracker загружен');


