# ⚡ WEEK 2: VPN ЭНЕРГОСБЕРЕГАЮЩИЙ РЕЖИМ - ПЛАН РЕАЛИЗАЦИИ

**Дата начала:** 11 октября 2025  
**Дата завершения:** 15 октября 2025 (5 дней)  
**Приоритет:** 🔴 **ВЫСОКИЙ**

---

## 📋 **ЗАДАЧИ (10 шагов):**

### **ДЕНЬ 1 (11 октября) - Архитектура** 🏗️

#### ✅ **Задача 1: VPNEnergyMode enum** (2 часа)
**Файл:** `/security/vpn/client/vpn_client.py`

**Что делать:**
```python
class VPNEnergyMode(Enum):
    """Режимы энергопотребления VPN"""
    FULL = "full"           # 100% - полная защита
    NORMAL = "normal"       # 60% - обычный режим  
    ECO = "eco"             # 30% - экономный режим
    MINIMAL = "minimal"     # 10% - минимальный
    SLEEP = "sleep"         # 0% - сон (отключен)
```

**Добавить в `__init__`:**
```python
self.energy_mode = VPNEnergyMode.FULL
self.battery_level = 100
self.last_activity_time = time.time()
self.idle_timeout = 900  # 15 минут по умолчанию
self.auto_sleep_enabled = True
self.energy_settings = {
    'auto_mode': True,
    'idle_timeout': 900,
    'battery_threshold': 20,
    'home_network_disable': True
}
```

**Проверка:**
- [ ] Enum создан
- [ ] Все 5 режимов добавлены
- [ ] Переменные инициализированы
- [ ] Тесты пройдены

---

#### ✅ **Задача 2: Мониторинг батареи** (4 часа)
**Файл:** `/security/vpn/client/vpn_client.py`

**Что делать:**
```python
def _get_battery_level(self) -> int:
    """Получить уровень заряда батареи"""
    try:
        # iOS
        if platform.system() == 'Darwin':
            # Используем pyobjc для iOS
            import objc
            from Foundation import NSProcessInfo
            info = NSProcessInfo.processInfo()
            battery = info.thermalState()
            return battery
        
        # Android  
        elif platform.system() == 'Linux':
            # Используем Android Battery API
            import subprocess
            result = subprocess.run(
                ['termux-battery-status'],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            return data.get('percentage', 100)
        
        # Desktop (для тестирования)
        else:
            import psutil
            battery = psutil.sensors_battery()
            return battery.percent if battery else 100
            
    except Exception as e:
        logger.warning(f"Не удалось получить уровень батареи: {e}")
        return 100  # По умолчанию считаем полный заряд

def _get_network_type(self) -> str:
    """Определить тип сети (home/public)"""
    try:
        # Получаем SSID текущей сети
        if platform.system() == 'Darwin':
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'SSID' in line:
                    ssid = line.split(':')[1].strip()
                    # Проверяем, это домашняя сеть?
                    if ssid in self.config.get('home_networks', []):
                        return 'home'
        return 'public'
    except:
        return 'public'  # По умолчанию считаем публичной
```

**Проверка:**
- [ ] Батарея определяется на iOS
- [ ] Батарея определяется на Android
- [ ] Тип сети определяется
- [ ] Fallback для desktop работает

---

### **ДЕНЬ 2 (12 октября) - Логика** 🧠

#### ✅ **Задача 3: Автоотключение при бездействии** (3 часа)

**Что делать:**
```python
async def monitor_energy(self):
    """Мониторинг энергопотребления и управление режимами"""
    logger.info("VPN Energy Monitor: Запущен")
    
    while self.is_running:
        try:
            # 1. Получаем текущее состояние
            battery = self._get_battery_level()
            idle_time = time.time() - self.last_activity_time
            network = self._get_network_type()
            
            # 2. Определяем нужный режим
            target_mode = self._calculate_target_mode(
                battery, idle_time, network
            )
            
            # 3. Переключаем режим если нужно
            if target_mode != self.energy_mode:
                await self._switch_energy_mode(target_mode)
            
            # 4. Логируем статистику
            self._log_energy_stats(battery, idle_time, network)
            
        except Exception as e:
            logger.error(f"Energy Monitor Error: {e}")
        
        # Проверяем каждые 60 секунд
        await asyncio.sleep(60)

def _calculate_target_mode(
    self, battery: int, idle_time: float, network: str
) -> VPNEnergyMode:
    """Вычислить целевой режим энергопотребления"""
    
    # Если авто-режим выключен - не меняем
    if not self.energy_settings['auto_mode']:
        return self.energy_mode
    
    # 1. КРИТИЧНЫЙ уровень батареи (<10%)
    if battery < 10:
        return VPNEnergyMode.SLEEP
    
    # 2. НИЗКИЙ уровень (<20%)
    if battery < self.energy_settings['battery_threshold']:
        return VPNEnergyMode.MINIMAL
    
    # 3. ДОЛГОЕ бездействие (30+ минут)
    if idle_time > 1800:  # 30 минут
        # В домашней сети можно отключить
        if network == 'home' and self.energy_settings['home_network_disable']:
            return VPNEnergyMode.SLEEP
        return VPNEnergyMode.ECO
    
    # 4. СРЕДНЕЕ бездействие (15+ минут)
    if idle_time > self.energy_settings['idle_timeout']:
        return VPNEnergyMode.ECO
    
    # 5. КОРОТКОЕ бездействие (5+ минут)
    if idle_time > 300:
        return VPNEnergyMode.NORMAL
    
    # 6. Активность - полный режим
    return VPNEnergyMode.FULL
```

**Проверка:**
- [ ] Мониторинг работает в фоне
- [ ] Idle time считается правильно
- [ ] Режимы переключаются корректно
- [ ] Логи выводятся

---

#### ✅ **Задача 4: Быстрое пробуждение** (2 часа)

**Что делать:**
```python
async def _switch_energy_mode(self, new_mode: VPNEnergyMode):
    """Переключение режима энергопотребления"""
    old_mode = self.energy_mode
    logger.info(f"VPN Energy: {old_mode.value} → {new_mode.value}")
    
    if new_mode == VPNEnergyMode.SLEEP:
        await self._enter_sleep_mode()
    elif new_mode == VPNEnergyMode.MINIMAL:
        await self._enter_minimal_mode()
    elif new_mode == VPNEnergyMode.ECO:
        await self._enter_eco_mode()
    elif new_mode == VPNEnergyMode.NORMAL:
        await self._enter_normal_mode()
    else:  # FULL
        await self._enter_full_mode()
    
    self.energy_mode = new_mode
    
    # Уведомляем пользователя
    await self._notify_energy_mode_change(old_mode, new_mode)

async def _enter_sleep_mode(self):
    """Перевод в режим сна"""
    logger.info("VPN → Режим сна: Отключение...")
    await self.disconnect()
    self.connection_suspended = True

async def _wake_up_from_sleep(self):
    """Быстрое пробуждение из режима сна"""
    logger.info("VPN: Пробуждение...")
    start_time = time.time()
    
    # 1. Восстанавливаем соединение с последним сервером
    if self.last_connected_server:
        success = await self.quick_connect(self.last_connected_server)
    else:
        success = await self.connect_to_best_server()
    
    wake_time = time.time() - start_time
    
    if success:
        logger.info(f"✅ VPN включен за {wake_time:.2f} сек")
        self.energy_mode = VPNEnergyMode.FULL
    else:
        logger.error("❌ Не удалось восстановить VPN")

async def on_user_activity(self):
    """Вызывается при активности пользователя"""
    self.last_activity_time = time.time()
    
    # Если VPN спал - быстро пробуждаем
    if self.energy_mode == VPNEnergyMode.SLEEP:
        await self._wake_up_from_sleep()
    
    # Если был в ECO/MINIMAL - переводим в NORMAL
    elif self.energy_mode in [VPNEnergyMode.ECO, VPNEnergyMode.MINIMAL]:
        await self._switch_energy_mode(VPNEnergyMode.NORMAL)
```

**Проверка:**
- [ ] Sleep mode корректно отключает VPN
- [ ] Wake up восстанавливает за <3 сек
- [ ] Последний сервер сохраняется
- [ ] Уведомления работают

---

### **ДЕНЬ 3 (13 октября) - Адаптация** 📊

#### ✅ **Задача 5: Адаптация под батарею** (3 часа)

**Что делать:**
```python
async def _enter_full_mode(self):
    """Полный режим (100% защита)"""
    self.encryption_strength = 'aes-256-gcm'
    self.monitoring_interval = 60  # каждую минуту
    self.keep_alive_interval = 30
    logger.info("🟢 VPN: Полный режим (AES-256)")

async def _enter_normal_mode(self):
    """Обычный режим (60% ресурсов)"""
    self.encryption_strength = 'aes-128-gcm'
    self.monitoring_interval = 120  # каждые 2 минуты
    self.keep_alive_interval = 60
    logger.info("🟡 VPN: Обычный режим (AES-128)")

async def _enter_eco_mode(self):
    """Экономный режим (30% ресурсов)"""
    self.encryption_strength = 'chacha20-poly1305'
    self.monitoring_interval = 300  # каждые 5 минут
    self.keep_alive_interval = 120
    logger.info("🟠 VPN: Экономный режим (ChaCha20)")

async def _enter_minimal_mode(self):
    """Минимальный режим (10% ресурсов)"""
    self.encryption_strength = 'chacha20'
    self.monitoring_interval = 600  # каждые 10 минут
    self.keep_alive_interval = 300
    # Отключаем некритичные функции
    self.dns_leak_protection = False
    self.ipv6_leak_protection = False
    logger.info("🔴 VPN: Минимальный режим (ChaCha20)")

def get_energy_stats(self) -> dict:
    """Получить статистику энергопотребления"""
    return {
        'current_mode': self.energy_mode.value,
        'battery_level': self._get_battery_level(),
        'idle_time': time.time() - self.last_activity_time,
        'active_time_today': self._get_active_time_today(),
        'sleep_time_today': self._get_sleep_time_today(),
        'battery_saved_percent': self._calculate_battery_saved(),
        'efficiency_score': self._calculate_efficiency()
    }
```

**Проверка:**
- [ ] Все 5 режимов реализованы
- [ ] Шифрование меняется
- [ ] Интервалы корректны
- [ ] Статистика считается

---

### **ДЕНЬ 4 (14 октября) - UI** 🎨

#### ✅ **Задача 6: UI настроек** (3 часа)
**Файл:** `/mobile/wireframes/05_settings_screen.html`

**Что делать:**
```html
<!-- VPN Энергосбережение -->
<div class="setting-card" onclick="openEnergySettings()" style="cursor: pointer;">
    <div class="setting-content">
        <div class="setting-icon">⚡</div>
        <div class="setting-info">
            <div class="setting-title">VPN Энергосбережение</div>
            <div class="setting-subtitle" id="energy-mode-text">Умное управление</div>
        </div>
        <div class="badge" id="energy-badge">~35% экономии</div>
        <div class="setting-arrow">→</div>
    </div>
</div>

<!-- Модальное окно настроек энергосбережения -->
<div class="modal-overlay" id="energy-modal" onclick="closeEnergyModal()">
    <div class="modal-content" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3>⚡ VPN Энергосбережение</h3>
            <button class="modal-close" onclick="closeEnergyModal()">×</button>
        </div>
        
        <div class="modal-body">
            <!-- Текущий режим -->
            <div class="energy-current">
                <div class="energy-mode-badge">🟢 Полный режим</div>
                <div class="energy-stats">
                    <div>🔋 Батарея: 67%</div>
                    <div>⏱️ VPN активен: 4ч 23мин</div>
                    <div>💰 Сэкономлено: ~35%</div>
                </div>
            </div>
            
            <!-- Автоматический режим -->
            <div class="setting-item">
                <div class="setting-label">
                    <div class="setting-title">🤖 Умное управление</div>
                    <div class="setting-desc">VPN автоматически адаптируется</div>
                </div>
                <div class="control-switch" id="auto-energy-switch" 
                     role="switch" aria-checked="true"
                     onclick="toggleAutoEnergy()"></div>
            </div>
            
            <!-- Автоотключение -->
            <div class="setting-item">
                <div class="setting-label">
                    <div class="setting-title">⏱️ Автоотключение</div>
                    <div class="setting-desc">Через 15 минут бездействия</div>
                </div>
                <select id="idle-timeout" onchange="updateIdleTimeout()">
                    <option value="300">5 минут</option>
                    <option value="900" selected>15 минут</option>
                    <option value="1800">30 минут</option>
                    <option value="0">Никогда</option>
                </select>
            </div>
            
            <!-- При низком заряде -->
            <div class="setting-item">
                <div class="setting-label">
                    <div class="setting-title">🔋 При низком заряде (<20%)</div>
                </div>
                <select id="battery-mode" onchange="updateBatteryMode()">
                    <option value="eco" selected>Экономный режим</option>
                    <option value="sleep">Отключить VPN</option>
                    <option value="nothing">Ничего не делать</option>
                </select>
            </div>
            
            <!-- В домашней сети -->
            <div class="setting-item">
                <div class="setting-label">
                    <div class="setting-title">🏠 В домашней сети</div>
                    <div class="setting-desc">Отключать VPN дома</div>
                </div>
                <div class="control-switch" id="home-disable-switch"
                     role="switch" aria-checked="true"
                     onclick="toggleHomeDisable()"></div>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn-primary" onclick="saveEnergySettings()">Сохранить</button>
        </div>
    </div>
</div>
```

**JavaScript:**
```javascript
function openEnergySettings() {
    document.getElementById('energy-modal').style.display = 'flex';
    loadCurrentEnergySettings();
}

function loadCurrentEnergySettings() {
    // Загружаем текущие настройки из localStorage
    const settings = JSON.parse(localStorage.getItem('vpn_energy_settings') || '{}');
    
    document.getElementById('auto-energy-switch').classList.toggle('active', 
        settings.auto_mode !== false);
    document.getElementById('idle-timeout').value = settings.idle_timeout || 900;
    document.getElementById('battery-mode').value = settings.battery_mode || 'eco';
    document.getElementById('home-disable-switch').classList.toggle('active',
        settings.home_disable !== false);
}

function saveEnergySettings() {
    const settings = {
        auto_mode: document.getElementById('auto-energy-switch').classList.contains('active'),
        idle_timeout: parseInt(document.getElementById('idle-timeout').value),
        battery_mode: document.getElementById('battery-mode').value,
        home_disable: document.getElementById('home-disable-switch').classList.contains('active')
    };
    
    localStorage.setItem('vpn_energy_settings', JSON.stringify(settings));
    
    // Отправляем настройки в VPN клиент
    sendToVPNClient('update_energy_settings', settings);
    
    showNotification('✅ Настройки энергосбережения сохранены', 'success');
    closeEnergyModal();
}
```

**Проверка:**
- [ ] Модальное окно открывается
- [ ] Все настройки работают
- [ ] Сохранение в localStorage
- [ ] UI responsive

---

#### ✅ **Задача 7: Activity tracking** (2 часа)
**Файл:** `/mobile/wireframes/02_protection_screen.html`

**Что делать:**
```javascript
// Глобальный трекер активности
class ActivityTracker {
    constructor() {
        this.lastActivityTime = Date.now();
        this.activityLog = [];
        this.init();
    }
    
    init() {
        // Отслеживаем все типы активности
        const events = [
            'touchstart', 'touchmove', 'touchend',
            'mousedown', 'mousemove', 'mouseup',
            'scroll', 'keypress', 'click'
        ];
        
        events.forEach(event => {
            document.addEventListener(event, () => this.recordActivity(event), 
                { passive: true });
        });
        
        // Отслеживаем фокус/блюр
        window.addEventListener('focus', () => this.recordActivity('focus'));
        window.addEventListener('blur', () => this.recordActivity('blur'));
        
        // Проверяем idle каждую минуту
        setInterval(() => this.checkIdle(), 60000);
    }
    
    recordActivity(type) {
        this.lastActivityTime = Date.now();
        this.activityLog.push({ type, time: Date.now() });
        
        // Отправляем в VPN клиент
        this.notifyVPNActivity();
    }
    
    getIdleTime() {
        return (Date.now() - this.lastActivityTime) / 1000; // секунды
    }
    
    checkIdle() {
        const idleTime = this.getIdleTime();
        
        if (idleTime > 900) {  // 15 минут
            showEnergyNotification('VPN перешел в экономный режим');
        } else if (idleTime > 1800) {  // 30 минут
            showEnergyNotification('VPN отключен для экономии батареи');
        }
    }
    
    notifyVPNActivity() {
        // Отправляем событие в VPN клиент через API
        if (window.VPNClient) {
            window.VPNClient.onUserActivity();
        }
    }
}

// Инициализируем трекер при загрузке
const activityTracker = new ActivityTracker();
```

**Проверка:**
- [ ] Все события отслеживаются
- [ ] Idle time считается правильно
- [ ] Уведомления показываются
- [ ] API коммуникация работает

---

### **ДЕНЬ 5 (15 октября) - Финализация** ✅

#### ✅ **Задача 8: Статистика для пользователя** (3 часа)
**Файл:** Создать `/mobile/wireframes/18_vpn_energy_stats.html`

**Что делать:**
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <title>VPN Энергостатистика</title>
    <!-- ... стили ... -->
</head>
<body>
    <div class="phone">
        <div class="screen">
            <div class="header">
                <button class="back-btn" onclick="window.history.back()">←</button>
                <div class="title">⚡ VPN и Батарея</div>
            </div>
            
            <!-- Сегодня -->
            <div class="stats-section">
                <h3>📊 Сегодня</h3>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-value" id="active-time">4ч 23м</div>
                        <div class="stat-label">VPN активен</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">💤</div>
                        <div class="stat-value" id="sleep-time">2ч 15м</div>
                        <div class="stat-label">В режиме сна</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔋</div>
                        <div class="stat-value" id="battery-saved">~35%</div>
                        <div class="stat-label">Сэкономлено</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📱</div>
                        <div class="stat-value" id="battery-current">67%</div>
                        <div class="stat-label">Заряд сейчас</div>
                    </div>
                </div>
            </div>
            
            <!-- График режимов -->
            <div class="chart-section">
                <h3>📈 Режимы работы</h3>
                <canvas id="energy-chart"></canvas>
            </div>
            
            <!-- На этой неделе -->
            <div class="stats-section">
                <h3>📅 На этой неделе</h3>
                <div class="weekly-stats">
                    <div class="stat-row">
                        <span>⚡ Средняя активность VPN</span>
                        <strong>5ч 12м/день</strong>
                    </div>
                    <div class="stat-row">
                        <span>💰 Сэкономлено батареи</span>
                        <strong>~2 дня автономности</strong>
                    </div>
                    <div class="stat-row">
                        <span>🎯 Эффективность</span>
                        <strong>92%</strong>
                    </div>
                </div>
            </div>
            
            <!-- Рекомендации -->
            <div class="recommendations">
                <h3>💡 Рекомендации</h3>
                <div class="tip-card">
                    <div class="tip-icon">✅</div>
                    <div class="tip-text">
                        VPN автоматически отключается когда не нужен
                    </div>
                </div>
                <div class="tip-card">
                    <div class="tip-icon">⚡</div>
                    <div class="tip-text">
                        Экономит 30-40% батареи в день
                    </div>
                </div>
                <div class="tip-card">
                    <div class="tip-icon">🚀</div>
                    <div class="tip-text">
                        Включается за 2 секунды при необходимости
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Загружаем статистику
        async function loadEnergyStats() {
            const stats = await fetchFromAPI('/vpn/energy/stats');
            updateUI(stats);
            renderChart(stats.timeline);
        }
        
        loadEnergyStats();
    </script>
</body>
</html>
```

**Проверка:**
- [ ] Статистика загружается
- [ ] График отображается
- [ ] Все цифры корректны
- [ ] Адаптивная верстка

---

#### ✅ **Задача 9: Тестирование** (4 часа)

**Что тестировать:**
```python
# tests/test_vpn_energy.py

import pytest
import asyncio
from security.vpn.client.vpn_client import ALADDINVPNClient, VPNEnergyMode

@pytest.mark.asyncio
async def test_energy_mode_switching():
    """Тест переключения режимов"""
    client = ALADDINVPNClient()
    
    # Тест 1: FULL → NORMAL
    client.last_activity_time = time.time() - 400  # 6+ минут назад
    await client.monitor_energy_once()
    assert client.energy_mode == VPNEnergyMode.NORMAL
    
    # Тест 2: NORMAL → ECO
    client.last_activity_time = time.time() - 1000  # 16+ минут назад
    await client.monitor_energy_once()
    assert client.energy_mode == VPNEnergyMode.ECO
    
    # Тест 3: ECO → SLEEP
    client.last_activity_time = time.time() - 2000  # 33+ минут назад
    client.battery_level = 100
    await client.monitor_energy_once()
    assert client.energy_mode == VPNEnergyMode.SLEEP

@pytest.mark.asyncio
async def test_battery_adaptation():
    """Тест адаптации под батарею"""
    client = ALADDINVPNClient()
    
    # Тест: Низкая батарея → MINIMAL
    client.battery_level = 15
    mode = client._calculate_target_mode(15, 0, 'public')
    assert mode == VPNEnergyMode.MINIMAL
    
    # Тест: Критичная батарея → SLEEP
    client.battery_level = 5
    mode = client._calculate_target_mode(5, 0, 'public')
    assert mode == VPNEnergyMode.SLEEP

@pytest.mark.asyncio
async def test_quick_wake_up():
    """Тест быстрого пробуждения"""
    client = ALADDINVPNClient()
    
    # Переводим в режим сна
    await client._enter_sleep_mode()
    assert client.energy_mode == VPNEnergyMode.SLEEP
    
    # Пробуждаем
    start = time.time()
    await client._wake_up_from_sleep()
    wake_time = time.time() - start
    
    assert client.energy_mode == VPNEnergyMode.FULL
    assert wake_time < 3.0  # Меньше 3 секунд
```

**Проверка:**
- [ ] Все тесты проходят
- [ ] Покрытие >80%
- [ ] Нет regression
- [ ] Performance OK

---

#### ✅ **Задача 10: Документация** (2 часа)

**Что написать:**
1. **User Guide** (для пользователей)
2. **API Documentation** (для разработчиков)
3. **Help-тексты** в приложении

**Файл:** `/docs/VPN_ENERGY_SAVING_GUIDE.md`

**Проверка:**
- [ ] User Guide готов
- [ ] API документирован
- [ ] Help-тексты добавлены
- [ ] Примеры работают

---

## 🎯 **КРИТЕРИИ ГОТОВНОСТИ:**

### **Must Have (обязательно):**
- ✅ Все 5 режимов работают
- ✅ Автоотключение при бездействии
- ✅ Адаптация под батарею
- ✅ Быстрое пробуждение (<3 сек)
- ✅ UI настроек
- ✅ Тесты проходят

### **Should Have (желательно):**
- ✅ Статистика для пользователя
- ✅ Activity tracking
- ✅ Уведомления
- ✅ Графики

### **Nice to Have (опционально):**
- ⏳ Machine Learning для оптимизации
- ⏳ Предиктивное пробуждение
- ⏳ Интеграция с Apple Watch
- ⏳ A/B тестирование

---

## 📊 **ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:**

**После Week 2:**
- ✅ VPN экономит 30-40% батареи
- ✅ Пользователи видят статистику
- ✅ Настройки гибкие
- ✅ Все работает стабильно
- ✅ **ПЕРВЫЙ VPN С УМНЫМ ЭНЕРГОСБЕРЕЖЕНИЕМ!** 🏆

---

## 📝 **ЕЖЕДНЕВНЫЕ CHECKPOINTS:**

**Конец каждого дня:**
1. ✅ Запустить тесты
2. ✅ Проверить на реальном устройстве
3. ✅ Обновить TODO лист
4. ✅ Задокументировать изменения
5. ✅ Commit + Push

---

**ГОТОВЫ НАЧИНАТЬ В ПОНЕДЕЛЬНИК!** 🚀  
**Week 1: 100% ✅**  
**Week 2: LET'S GO! ⚡**


