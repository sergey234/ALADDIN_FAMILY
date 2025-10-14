package com.aladdin.mobile.security

import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import java.io.File
import java.security.MessageDigest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AntiTamperingManager @Inject constructor(
    private val context: Context
) {
    
    private val expectedChecksums: Map<String, String>
    private val criticalClasses: List<String>
    
    init {
        expectedChecksums = loadExpectedChecksums()
        criticalClasses = listOf(
            "com.aladdin.mobile.security.CertificatePinningManager",
            "com.aladdin.mobile.security.RootDetector",
            "com.aladdin.mobile.security.RASPManager",
            "com.aladdin.mobile.network.ALADDINNetworkManager"
        )
    }
    
    // MARK: - Main Validation Methods
    
    /**
     * Проверка целостности приложения
     */
    fun validateAppIntegrity(): TamperingDetectionResult {
        var detectionMethods: MutableMap<TamperingCheck, Boolean> = mutableMapOf()
        var riskLevel: TamperingRiskLevel = TamperingRiskLevel.LOW
        
        // 1. Проверка подписи приложения
        detectionMethods[TamperingCheck.APP_SIGNATURE] = validateAppSignature()
        
        // 2. Проверка целостности критических классов
        detectionMethods[TamperingCheck.CRITICAL_CLASSES] = validateCriticalClasses()
        
        // 3. Проверка целостности ресурсов
        detectionMethods[TamperingCheck.RESOURCES] = validateResources()
        
        // 4. Проверка целостности APK
        detectionMethods[TamperingCheck.APK_INTEGRITY] = validateApkIntegrity()
        
        // 5. Проверка контрольных сумм
        detectionMethods[TamperingCheck.CHECKSUMS] = validateChecksums()
        
        // 6. Проверка установщика
        detectionMethods[TamperingCheck.INSTALLER] = validateInstaller()
        
        // 7. Проверка манифеста
        detectionMethods[TamperingCheck.MANIFEST] = validateManifest()
        
        // Определяем уровень риска
        val violations = detectionMethods.values.count { !it }
        riskLevel = determineTamperingRiskLevel(violations)
        
        val isTampered = violations > 0
        
        return TamperingDetectionResult(
            isTampered = isTampered,
            riskLevel = riskLevel,
            detectionMethods = detectionMethods,
            timestamp = System.currentTimeMillis()
        )
    }
    
    // MARK: - Validation Methods
    
    // 1. Проверка подписи приложения
    private fun validateAppSignature(): Boolean {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(
                context.packageName,
                PackageManager.GET_SIGNATURES
            )
            
            val signatures = packageInfo.signatures
            if (signatures.isNotEmpty()) {
                val signature = signatures[0]
                val md = MessageDigest.getInstance("SHA-256")
                md.update(signature.toByteArray())
                val hash = md.digest()
                val hashString = hash.joinToString("") { "%02x".format(it) }
                
                val expectedSignature = expectedChecksums["app_signature"]
                val isValid = expectedSignature == null || hashString == expectedSignature
                
                if (isValid) {
                    Log.i("AntiTampering", "App signature valid")
                } else {
                    Log.w("AntiTampering", "App signature invalid")
                }
                
                isValid
            } else {
                Log.w("AntiTampering", "No signatures found")
                false
            }
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error validating app signature", e)
            false
        }
    }
    
    // 2. Проверка целостности критических классов
    private fun validateCriticalClasses(): Boolean {
        var allValid = true
        
        for (className in criticalClasses) {
            try {
                val clazz = Class.forName(className)
                val checksum = calculateClassChecksum(clazz)
                
                val expectedChecksum = expectedChecksums[className]
                if (expectedChecksum != null && checksum != expectedChecksum) {
                    Log.w("AntiTampering", "Class $className modified")
                    allValid = false
                } else {
                    Log.i("AntiTampering", "Class $className intact")
                }
            } catch (e: ClassNotFoundException) {
                Log.w("AntiTampering", "Class $className not found")
                allValid = false
            }
        }
        
        return allValid
    }
    
    // 3. Проверка целостности ресурсов
    private fun validateResources(): Boolean {
        val criticalResources = listOf(
            "AndroidManifest.xml",
            "classes.dex",
            "resources.arsc"
        )
        
        var allValid = true
        
        for (resource in criticalResources) {
            val checksum = calculateResourceChecksum(resource)
            val expectedChecksum = expectedChecksums[resource]
            
            if (expectedChecksum != null && checksum != expectedChecksum) {
                Log.w("AntiTampering", "Resource $resource modified")
                allValid = false
            } else {
                Log.i("AntiTampering", "Resource $resource intact")
            }
        }
        
        return allValid
    }
    
    // 4. Проверка целостности APK
    private fun validateApkIntegrity(): Boolean {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(
                context.packageName,
                0
            )
            
            val apkPath = packageInfo.applicationInfo.sourceDir
            val apkFile = File(apkPath)
            
            if (!apkFile.exists()) {
                Log.w("AntiTampering", "APK file not found")
                return false
            }
            
            val checksum = calculateFileChecksum(apkFile)
            val expectedChecksum = expectedChecksums["apk"]
            
            val isValid = expectedChecksum == null || checksum == expectedChecksum
            
            if (isValid) {
                Log.i("AntiTampering", "APK integrity valid")
            } else {
                Log.w("AntiTampering", "APK integrity invalid")
            }
            
            isValid
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error validating APK integrity", e)
            false
        }
    }
    
    // 5. Проверка контрольных сумм
    private fun validateChecksums(): Boolean {
        var allValid = true
        
        for ((file, expectedChecksum) in expectedChecksums) {
            // Проверяем существование файла и его контрольную сумму
            val actualChecksum = when {
                file.startsWith("com.aladdin") -> calculateClassChecksum(Class.forName(file))
                file.endsWith(".xml") || file.endsWith(".dex") -> calculateResourceChecksum(file)
                else -> continue
            }
            
            if (actualChecksum != expectedChecksum) {
                Log.w("AntiTampering", "Checksum mismatch for $file")
                allValid = false
            } else {
                Log.i("AntiTampering", "Checksum valid for $file")
            }
        }
        
        return allValid
    }
    
    // 6. Проверка установщика
    private fun validateInstaller(): Boolean {
        val installerPackageName = context.packageManager.getInstallerPackageName(context.packageName)
        
        val validInstallers = listOf(
            "com.android.vending", // Google Play
            "com.google.android.feedback", // Google Play (альтернативный)
            null // Разрешаем установку через ADB в debug режиме
        )
        
        val isValid = validInstallers.contains(installerPackageName)
        
        if (isValid) {
            Log.i("AntiTampering", "Installer valid: $installerPackageName")
        } else {
            Log.w("AntiTampering", "Installer invalid: $installerPackageName")
        }
        
        return isValid
    }
    
    // 7. Проверка манифеста
    private fun validateManifest(): Boolean {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(
                context.packageName,
                PackageManager.GET_PERMISSIONS
            )
            
            // Проверяем критические разрешения
            val criticalPermissions = listOf(
                android.Manifest.permission.INTERNET,
                android.Manifest.permission.ACCESS_NETWORK_STATE
            )
            
            val requestedPermissions = packageInfo.requestedPermissions?.toList() ?: emptyList()
            
            var allValid = true
            for (permission in criticalPermissions) {
                if (!requestedPermissions.contains(permission)) {
                    Log.w("AntiTampering", "Missing permission: $permission")
                    allValid = false
                }
            }
            
            if (allValid) {
                Log.i("AntiTampering", "Manifest valid")
            }
            
            allValid
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error validating manifest", e)
            false
        }
    }
    
    // MARK: - Helper Methods
    
    private fun loadExpectedChecksums(): Map<String, String> {
        // В реальном приложении эти значения были бы зашифрованы и обфусцированы
        return mapOf(
            "app_signature" to "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
            "apk" to "def456ghi789jkl012mno345pqr678stu901vwx234yz567abc",
            "AndroidManifest.xml" to "ghi789jkl012mno345pqr678stu901",
            "classes.dex" to "jkl012mno345pqr678stu901vwx234",
            "resources.arsc" to "mno345pqr678stu901vwx234yz567"
        )
    }
    
    private fun calculateClassChecksum(clazz: Class<*>): String {
        return try {
            val classLoader = clazz.classLoader
            val className = clazz.name.replace(".", "/") + ".class"
            val inputStream = classLoader?.getResourceAsStream(className)
            
            val md = MessageDigest.getInstance("SHA-256")
            val buffer = ByteArray(8192)
            var bytesRead: Int
            
            while (inputStream?.read(buffer).also { bytesRead = it ?: -1 } != -1) {
                md.update(buffer, 0, bytesRead)
            }
            
            inputStream?.close()
            
            val hash = md.digest()
            hash.joinToString("") { "%02x".format(it) }
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error calculating class checksum", e)
            ""
        }
    }
    
    private fun calculateResourceChecksum(resourceName: String): String {
        return try {
            val assetManager = context.assets
            val inputStream = assetManager.open(resourceName)
            
            val md = MessageDigest.getInstance("SHA-256")
            val buffer = ByteArray(8192)
            var bytesRead: Int
            
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                md.update(buffer, 0, bytesRead)
            }
            
            inputStream.close()
            
            val hash = md.digest()
            hash.joinToString("") { "%02x".format(it) }
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error calculating resource checksum", e)
            ""
        }
    }
    
    private fun calculateFileChecksum(file: File): String {
        return try {
            val md = MessageDigest.getInstance("SHA-256")
            val inputStream = file.inputStream()
            val buffer = ByteArray(8192)
            var bytesRead: Int
            
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                md.update(buffer, 0, bytesRead)
            }
            
            inputStream.close()
            
            val hash = md.digest()
            hash.joinToString("") { "%02x".format(it) }
        } catch (e: Exception) {
            Log.e("AntiTampering", "Error calculating file checksum", e)
            ""
        }
    }
    
    private fun determineTamperingRiskLevel(violations: Int): TamperingRiskLevel {
        return when (violations) {
            0 -> TamperingRiskLevel.LOW
            1, 2 -> TamperingRiskLevel.MEDIUM
            3, 4 -> TamperingRiskLevel.HIGH
            else -> TamperingRiskLevel.CRITICAL
        }
    }
    
    // MARK: - Public Methods
    
    /**
     * Получить детальный отчет
     */
    fun getDetailedReport(): String {
        val result = validateAppIntegrity()
        
        var report = "🔒 Anti-Tampering Report\n"
        report += "========================\n"
        report += "Status: ${if (result.isTampered) "🚨 TAMPERED" else "✅ INTACT"}\n"
        report += "Risk Level: ${result.riskLevel.name}\n"
        report += "Timestamp: ${java.util.Date(result.timestamp)}\n\n"
        
        report += "Validation Checks:\n"
        for ((check, isValid) in result.detectionMethods) {
            report += "- ${check.name}: ${if (isValid) "✅ VALID" else "🚨 INVALID"}\n"
        }
        
        return report
    }
    
    /**
     * Быстрая проверка целостности
     */
    fun quickIntegrityCheck(): Boolean {
        val result = validateAppIntegrity()
        return !result.isTampered
    }
}

// MARK: - Data Models

data class TamperingDetectionResult(
    val isTampered: Boolean,
    val riskLevel: TamperingRiskLevel,
    val detectionMethods: Map<TamperingCheck, Boolean>,
    val timestamp: Long
)

enum class TamperingRiskLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}

enum class TamperingCheck {
    APP_SIGNATURE,
    CRITICAL_CLASSES,
    RESOURCES,
    APK_INTEGRITY,
    CHECKSUMS,
    INSTALLER,
    MANIFEST
}

