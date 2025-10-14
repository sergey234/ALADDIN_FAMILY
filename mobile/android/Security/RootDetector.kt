package com.aladdin.mobile.security

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import java.io.File
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RootDetector @Inject constructor(
    private val context: Context
) {
    
    // MARK: - Main Detection Method
    
    /**
     * Проверка на root
     */
    fun isRooted(): Boolean {
        return detectRoot()
    }
    
    /**
     * Детальная проверка с результатами
     */
    fun detectRoot(): RootDetectionResult {
        var detectionMethods: MutableMap<RootMethod, Boolean> = mutableMapOf()
        var riskLevel: RiskLevel = RiskLevel.LOW
        
        // 1. Проверка файлов root
        detectionMethods[RootMethod.ROOT_FILES] = checkRootFiles()
        
        // 2. Проверка приложений
        detectionMethods[RootMethod.ROOT_APPS] = checkRootApps()
        
        // 3. Проверка команд
        detectionMethods[RootMethod.ROOT_COMMANDS] = checkRootCommands()
        
        // 4. Проверка свойств системы
        detectionMethods[RootMethod.SYSTEM_PROPERTIES] = checkSystemProperties()
        
        // 5. Проверка библиотек
        detectionMethods[RootMethod.SUSPICIOUS_LIBRARIES] = checkSuspiciousLibraries()
        
        // 6. Проверка SELinux
        detectionMethods[RootMethod.SELINUX] = checkSELinuxStatus()
        
        // 7. Проверка отладки
        detectionMethods[RootMethod.DEBUGGING] = checkDebuggingStatus()
        
        // Определяем уровень риска
        val positiveDetections = detectionMethods.values.count { it }
        riskLevel = determineRiskLevel(positiveDetections)
        
        return RootDetectionResult(
            isRooted = positiveDetections > 0,
            riskLevel = riskLevel,
            detectionMethods = detectionMethods,
            timestamp = System.currentTimeMillis()
        )
    }
    
    // MARK: - Detection Methods
    
    // 1. Проверка файлов root
    private fun checkRootFiles(): Boolean {
        val rootPaths = listOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su",
            "/system/etc/init.d/99SuperSUDaemon",
            "/dev/com.koushikdutta.superuser.daemon/",
            "/system/etc/.has_su_daemon",
            "/system/etc/.installed_su_daemon",
            "/system/bin/.ext/.su",
            "/system/usr/we-need-root/su-backup",
            "/system/xbin/busybox",
            "/system/bin/busybox",
            "/data/local/busybox",
            "/system/sd/xbin/busybox",
            "/system/bin/.ext/busybox",
            "/data/local/xbin/busybox",
            "/system/xbin/daemonsu",
            "/system/etc/init.d/99SuperSUDaemon",
            "/system/bin/.ext/.su",
            "/system/usr/we-need-root/su-backup",
            "/system/xbin/busybox",
            "/system/bin/busybox",
            "/data/local/busybox",
            "/system/sd/xbin/busybox",
            "/system/bin/.ext/busybox",
            "/data/local/xbin/busybox"
        )
        
        for (path in rootPaths) {
            if (File(path).exists()) {
                android.util.Log.w("RootDetector", "Root detected: Found $path")
                return true
            }
        }
        
        return false
    }
    
    // 2. Проверка приложений
    private fun checkRootApps(): Boolean {
        val rootApps = listOf(
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.topjohnwu.magisk",
            "com.kingroot.kinguser",
            "com.kingo.root",
            "com.smedialink.oneclickroot",
            "com.zhiqupk.root.global",
            "com.alephzain.framaroot"
        )
        
        val packageManager = context.packageManager
        
        for (packageName in rootApps) {
            try {
                packageManager.getPackageInfo(packageName, 0)
                android.util.Log.w("RootDetector", "Root detected: Found app $packageName")
                return true
            } catch (e: PackageManager.NameNotFoundException) {
                // Ожидаемое поведение - приложение не найдено
                continue
            }
        }
        
        return false
    }
    
    // 3. Проверка команд
    private fun checkRootCommands(): Boolean {
        val rootCommands = listOf(
            "su",
            "which su",
            "busybox",
            "which busybox"
        )
        
        for (command in rootCommands) {
            if (executeCommand(command)) {
                android.util.Log.w("RootDetector", "Root detected: Command '$command' succeeded")
                return true
            }
        }
        
        return false
    }
    
    // 4. Проверка свойств системы
    private fun checkSystemProperties(): Boolean {
        val suspiciousProperties = mapOf(
            "ro.debuggable" to "1",
            "ro.secure" to "0",
            "service.adb.root" to "1"
        )
        
        for ((property, expectedValue) in suspiciousProperties) {
            val actualValue = getSystemProperty(property)
            if (actualValue == expectedValue) {
                android.util.Log.w("RootDetector", "Root detected: Property $property = $actualValue")
                return true
            }
        }
        
        return false
    }
    
    // 5. Проверка библиотек
    private fun checkSuspiciousLibraries(): Boolean {
        val suspiciousLibraries = listOf(
            "libsu.so",
            "libsuperuser.so",
            "libsupersu.so"
        )
        
        for (library in suspiciousLibraries) {
            if (isLibraryLoaded(library)) {
                android.util.Log.w("RootDetector", "Root detected: Library $library loaded")
                return true
            }
        }
        
        return false
    }
    
    // 6. Проверка SELinux
    private fun checkSELinuxStatus(): Boolean {
        val selinuxStatus = getSystemProperty("ro.build.selinux")
        if (selinuxStatus == "0" || selinuxStatus.isEmpty()) {
            android.util.Log.w("RootDetector", "Root detected: SELinux disabled")
            return true
        }
        
        return false
    }
    
    // 7. Проверка отладки
    private fun checkDebuggingStatus(): Boolean {
        val debugStatus = getSystemProperty("ro.debuggable")
        if (debugStatus == "1") {
            android.util.Log.w("RootDetector", "Root detected: Debug mode enabled")
            return true
        }
        
        return false
    }
    
    // MARK: - Helper Methods
    
    private fun executeCommand(command: String): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(command)
            val exitCode = process.waitFor()
            exitCode == 0
        } catch (e: IOException) {
            false
        } catch (e: InterruptedException) {
            false
        }
    }
    
    private fun getSystemProperty(property: String): String {
        return try {
            val process = Runtime.getRuntime().exec("getprop $property")
            val reader = process.inputStream.bufferedReader()
            val result = reader.readLine() ?: ""
            reader.close()
            result
        } catch (e: Exception) {
            ""
        }
    }
    
    private fun isLibraryLoaded(libraryName: String): Boolean {
        return try {
            System.loadLibrary(libraryName)
            true
        } catch (e: UnsatisfiedLinkError) {
            false
        }
    }
    
    private fun determineRiskLevel(positiveDetections: Int): RiskLevel {
        return when (positiveDetections) {
            0 -> RiskLevel.LOW
            1, 2 -> RiskLevel.MEDIUM
            3, 4 -> RiskLevel.HIGH
            else -> RiskLevel.CRITICAL
        }
    }
    
    // MARK: - Public Methods
    
    /**
     * Получить детальный отчет о проверке
     */
    fun getDetailedReport(): String {
        val result = detectRoot()
        
        var report = "🔍 Root Detection Report\n"
        report += "=====================\n"
        report += "Status: ${if (result.isRooted) "🚨 ROOTED" else "✅ CLEAN"}\n"
        report += "Risk Level: ${result.riskLevel.name}\n"
        report += "Timestamp: ${java.util.Date(result.timestamp)}\n\n"
        
        report += "Detection Methods:\n"
        for ((method, detected) in result.detectionMethods) {
            report += "- ${method.name}: ${if (detected) "🚨 DETECTED" else "✅ CLEAN"}\n"
        }
        
        return report
    }
}

// MARK: - Data Models

data class RootDetectionResult(
    val isRooted: Boolean,
    val riskLevel: RiskLevel,
    val detectionMethods: Map<RootMethod, Boolean>,
    val timestamp: Long
)

enum class RiskLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}

enum class RootMethod {
    ROOT_FILES,
    ROOT_APPS,
    ROOT_COMMANDS,
    SYSTEM_PROPERTIES,
    SUSPICIOUS_LIBRARIES,
    SELINUX,
    DEBUGGING
}

