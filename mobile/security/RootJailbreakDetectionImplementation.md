# 🔍 Root/Jailbreak Detection - План Реализации

## 🎯 **ЧТО ЭТО ТАКОЕ?**
**Root/Jailbreak Detection** - это проверка, не взломано ли устройство пользователя. Root (Android) и Jailbreak (iOS) дают полный доступ к системе, что может быть опасно для семейной безопасности.

## ⚠️ **ЗАЧЕМ НУЖНО?**
- **Защита от вредоносного ПО** с root-доступом
- **Предотвращение обхода** родительского контроля
- **Защита от модификации** приложения
- **Обеспечение целостности** системы безопасности

## 📱 **РЕАЛИЗАЦИЯ ДЛЯ iOS (Swift)**

### Шаг 1: Создание Jailbreak Detector
```swift
// mobile/ios/Security/JailbreakDetector.swift
import Foundation
import UIKit

class JailbreakDetector {
    
    // Проверка на jailbreak
    static func isJailbroken() -> Bool {
        return checkJailbreakSigns()
    }
    
    private static func checkJailbreakSigns() -> Bool {
        // 1. Проверка файлов Cydia
        let cydiaPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt"
        ]
        
        for path in cydiaPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }
        
        // 2. Проверка sandbox
        if canWriteToRestrictedDirectories() {
            return true
        }
        
        // 3. Проверка URL schemes
        if canOpenCydiaURL() {
            return true
        }
        
        // 4. Проверка системных вызовов
        if canForkProcess() {
            return true
        }
        
        return false
    }
    
    private static func canWriteToRestrictedDirectories() -> Bool {
        let restrictedPath = "/private/var/mobile/"
        do {
            try "test".write(toFile: restrictedPath + "jailbreak_test", 
                           atomically: true, encoding: .utf8)
            return true
        } catch {
            return false
        }
    }
    
    private static func canOpenCydiaURL() -> Bool {
        if let url = URL(string: "cydia://") {
            return UIApplication.shared.canOpenURL(url)
        }
        return false
    }
    
    private static func canForkProcess() -> Bool {
        let pid = fork()
        if pid >= 0 {
            if pid == 0 {
                exit(0)
            }
            return true
        }
        return false
    }
}
```

### Шаг 2: Интеграция в Security Manager
```swift
// mobile/ios/Security/ALADDINSecurityManager.swift
class ALADDINSecurityManager {
    
    func performSecurityChecks() -> SecurityStatus {
        var threats: [SecurityThreat] = []
        
        // Проверка jailbreak
        if JailbreakDetector.isJailbroken() {
            threats.append(SecurityThreat(
                type: .jailbreak,
                severity: .critical,
                message: "Устройство взломано (jailbreak). Безопасность может быть скомпрометирована."
            ))
        }
        
        return SecurityStatus(threats: threats)
    }
}
```

## 🤖 **РЕАЛИЗАЦИЯ ДЛЯ ANDROID (Kotlin)**

### Шаг 1: Создание Root Detector
```kotlin
// mobile/android/Security/RootDetector.kt
class RootDetector(private val context: Context) {
    
    fun isRooted(): Boolean {
        return checkRootSigns()
    }
    
    private fun checkRootSigns(): Boolean {
        // 1. Проверка файлов root
        val rootPaths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        )
        
        for (path in rootPaths) {
            if (File(path).exists()) {
                return true
            }
        }
        
        // 2. Проверка build tags
        if (isRootBuild()) {
            return true
        }
        
        // 3. Проверка su команды
        if (canExecuteSu()) {
            return true
        }
        
        // 4. Проверка busybox
        if (hasBusybox()) {
            return true
        }
        
        return false
    }
    
    private fun isRootBuild(): Boolean {
        val buildTags = android.os.Build.TAGS
        return buildTags != null && buildTags.contains("test-keys")
    }
    
    private fun canExecuteSu(): Boolean {
        return try {
            Runtime.getRuntime().exec("su").exitValue() == 0
        } catch (e: Exception) {
            false
        }
    }
    
    private fun hasBusybox(): Boolean {
        val busyboxPaths = arrayOf(
            "/system/bin/busybox",
            "/system/xbin/busybox",
            "/data/local/xbin/busybox"
        )
        
        return busyboxPaths.any { File(it).exists() }
    }
}
```

### Шаг 2: Интеграция в Security Manager
```kotlin
// mobile/android/Security/ALADDINSecurityManager.kt
class ALADDINSecurityManager(private val context: Context) {
    
    fun performSecurityChecks(): SecurityStatus {
        val threats = mutableListOf<SecurityThreat>()
        
        // Проверка root
        if (RootDetector(context).isRooted()) {
            threats.add(SecurityThreat(
                type = SecurityThreatType.ROOT,
                severity = SecurityThreatSeverity.CRITICAL,
                message = "Устройство имеет root-доступ. Безопасность может быть скомпрометирована."
            ))
        }
        
        return SecurityStatus(threats = threats)
    }
}
```

## 📋 **ПЛАН ВНЕДРЕНИЯ (1 неделя)**

### День 1-2: Разработка детекторов
- [ ] Создать JailbreakDetector для iOS
- [ ] Создать RootDetector для Android
- [ ] Написать unit тесты

### День 3-4: Интеграция
- [ ] Интегрировать в SecurityManager
- [ ] Добавить UI предупреждения
- [ ] Настроить логирование

### День 5-7: Тестирование
- [ ] Тестирование на jailbroken устройствах
- [ ] Тестирование на rooted устройствах
- [ ] Проверка ложных срабатываний

## 🎨 **UI ПРЕДУПРЕЖДЕНИЯ**

### iOS Alert
```swift
func showJailbreakWarning() {
    let alert = UIAlertController(
        title: "⚠️ Взломанное устройство",
        message: "Обнаружен jailbreak. Для обеспечения безопасности семьи рекомендуется использовать стандартное устройство.",
        preferredStyle: .alert
    )
    
    alert.addAction(UIAlertAction(title: "Понятно", style: .default))
    present(alert, animated: true)
}
```

### Android Alert
```kotlin
fun showRootWarning() {
    AlertDialog.Builder(context)
        .setTitle("⚠️ Root-доступ обнаружен")
        .setMessage("Устройство имеет root-доступ. Для обеспечения безопасности семьи рекомендуется использовать стандартное устройство.")
        .setPositiveButton("Понятно") { _, _ -> }
        .show()
}
```

## ⚠️ **ВАЖНЫЕ МОМЕНТЫ**

### ✅ **ПЛЮСЫ:**
- Защита от взломанных устройств
- Предотвращение обхода безопасности
- Информирование родителей о рисках

### ⚠️ **МИНУСЫ:**
- Возможны ложные срабатывания
- Сложность обхода для продвинутых пользователей
- Необходимость регулярного обновления методов

## 🔧 **ОБХОД ОБНАРУЖЕНИЯ**

### Защита от обхода
```swift
// Дополнительные проверки
private static func checkAdvancedJailbreak() -> Bool {
    // Проверка на подмену системных функций
    let originalFork = dlsym(RTLD_DEFAULT, "fork")
    let currentFork = dlsym(RTLD_DEFAULT, "fork")
    
    if originalFork != currentFork {
        return true
    }
    
    return false
}
```

## 📊 **МЕТРИКИ УСПЕХА**
- [ ] 95%+ точность обнаружения
- [ ] <1% ложных срабатываний
- [ ] Автоматическое обновление методов
- [ ] Интеграция с системой мониторинга

---

*Критически важно для защиты семейных данных от взломанных устройств!*

