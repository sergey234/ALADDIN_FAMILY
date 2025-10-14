package com.aladdin.mobile.performance

import android.app.ActivityManager
import android.content.Context
import android.os.BatteryManager
import android.os.Handler
import android.os.Looper
import android.util.Log
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PerformanceProfiler @Inject constructor(
    private val context: Context
) {
    
    private var isMonitoring = false
    private var monitoringHandler: Handler? = null
    private val metrics = mutableListOf<PerformanceMetric>()
    
    private val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    private val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
    
    // MARK: - Monitoring Control
    
    fun startMonitoring() {
        if (isMonitoring) return
        
        isMonitoring = true
        Log.i("PerformanceProfiler", "Performance monitoring started")
        
        monitoringHandler = Handler(Looper.getMainLooper())
        scheduleNextCollection()
    }
    
    fun stopMonitoring() {
        if (!isMonitoring) return
        
        isMonitoring = false
        monitoringHandler?.removeCallbacksAndMessages(null)
        monitoringHandler = null
        
        Log.i("PerformanceProfiler", "Performance monitoring stopped")
    }
    
    private fun scheduleNextCollection() {
        monitoringHandler?.postDelayed({
            if (isMonitoring) {
                collectMetrics()
                scheduleNextCollection()
            }
        }, 1000) // Every second
    }
    
    // MARK: - Metrics Collection
    
    private fun collectMetrics() {
        val metric = PerformanceMetric(
            cpuUsage = getCPUUsage(),
            memoryUsage = getMemoryUsage(),
            batteryLevel = getBatteryLevel(),
            networkActivity = getNetworkActivity(),
            timestamp = System.currentTimeMillis()
        )
        
        metrics.add(metric)
        
        // Keep only last 60 metrics (1 minute)
        if (metrics.size > 60) {
            metrics.removeAt(0)
        }
    }
    
    // MARK: - CPU Usage
    
    private var lastCpuTime = 0L
    private var lastAppTime = 0L
    
    private fun getCPUUsage(): Double {
        return try {
            val statFile = File("/proc/stat")
            val statContent = statFile.readText()
            val cpuLine = statContent.lines().first { it.startsWith("cpu ") }
            val cpuValues = cpuLine.split("\\s+".toRegex()).drop(1).map { it.toLong() }
            val totalCpuTime = cpuValues.sum()
            
            val processFile = File("/proc/${android.os.Process.myPid()}/stat")
            val processContent = processFile.readText()
            val processValues = processContent.split(" ")
            val utime = processValues[13].toLong()
            val stime = processValues[14].toLong()
            val totalAppTime = utime + stime
            
            val cpuDelta = totalCpuTime - lastCpuTime
            val appDelta = totalAppTime - lastAppTime
            
            lastCpuTime = totalCpuTime
            lastAppTime = totalAppTime
            
            if (cpuDelta > 0) {
                (appDelta.toDouble() / cpuDelta.toDouble()) * 100.0
            } else {
                0.0
            }
        } catch (e: Exception) {
            Log.e("PerformanceProfiler", "Error getting CPU usage", e)
            0.0
        }
    }
    
    // MARK: - Memory Usage
    
    private fun getMemoryUsage(): Long {
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        
        val runtime = Runtime.getRuntime()
        val usedMemory = runtime.totalMemory() - runtime.freeMemory()
        
        return usedMemory
    }
    
    // MARK: - Battery Level
    
    private fun getBatteryLevel(): Float {
        return try {
            val batteryLevel = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            batteryLevel / 100.0f
        } catch (e: Exception) {
            Log.e("PerformanceProfiler", "Error getting battery level", e)
            0.0f
        }
    }
    
    // MARK: - Network Activity
    
    private var lastNetworkBytes = 0L
    
    private fun getNetworkActivity(): Double {
        return try {
            val currentBytes = android.net.TrafficStats.getTotalRxBytes() + android.net.TrafficStats.getTotalTxBytes()
            val delta = currentBytes - lastNetworkBytes
            lastNetworkBytes = currentBytes
            
            // Convert to KB/s
            delta.toDouble() / 1024.0
        } catch (e: Exception) {
            Log.e("PerformanceProfiler", "Error getting network activity", e)
            0.0
        }
    }
    
    // MARK: - Reports
    
    fun getCurrentMetrics(): PerformanceMetric? {
        return metrics.lastOrNull()
    }
    
    fun getAverageMetrics(): PerformanceMetric? {
        if (metrics.isEmpty()) return null
        
        val avgCPU = metrics.map { it.cpuUsage }.average()
        val avgMemory = metrics.map { it.memoryUsage }.average().toLong()
        val avgBattery = metrics.map { it.batteryLevel }.average().toFloat()
        val avgNetwork = metrics.map { it.networkActivity }.average()
        
        return PerformanceMetric(
            cpuUsage = avgCPU,
            memoryUsage = avgMemory,
            batteryLevel = avgBattery,
            networkActivity = avgNetwork,
            timestamp = System.currentTimeMillis()
        )
    }
    
    fun getDetailedReport(): String {
        val current = getCurrentMetrics() ?: return "No metrics available"
        val average = getAverageMetrics() ?: return "No metrics available"
        
        return buildString {
            appendLine("📊 Performance Report")
            appendLine("====================")
            appendLine()
            
            appendLine("Current Metrics:")
            appendLine("- CPU Usage: ${"%.1f".format(current.cpuUsage)}%")
            appendLine("- Memory: ${formatBytes(current.memoryUsage)}")
            appendLine("- Battery: ${"%.0f".format(current.batteryLevel * 100)}%")
            appendLine("- Network: ${"%.1f".format(current.networkActivity)} KB/s")
            appendLine()
            
            appendLine("Average Metrics (Last Minute):")
            appendLine("- CPU Usage: ${"%.1f".format(average.cpuUsage)}%")
            appendLine("- Memory: ${formatBytes(average.memoryUsage)}")
            appendLine("- Battery: ${"%.0f".format(average.batteryLevel * 100)}%")
            appendLine("- Network: ${"%.1f".format(average.networkActivity)} KB/s")
        }
    }
    
    private fun formatBytes(bytes: Long): String {
        val kiloBytes = bytes / 1024
        val megaBytes = kiloBytes / 1024
        val gigaBytes = megaBytes / 1024
        
        return when {
            gigaBytes > 0 -> "${"%.2f".format(gigaBytes.toFloat())} GB"
            megaBytes > 0 -> "${"%.2f".format(megaBytes.toFloat())} MB"
            kiloBytes > 0 -> "${"%.2f".format(kiloBytes.toFloat())} KB"
            else -> "$bytes B"
        }
    }
    
    // MARK: - Performance Thresholds
    
    fun checkPerformanceThresholds(): PerformanceStatus {
        val current = getCurrentMetrics() ?: return PerformanceStatus.UNKNOWN
        
        return when {
            current.cpuUsage > 80.0 || current.memoryUsage > 500 * 1024 * 1024 -> {
                PerformanceStatus.CRITICAL
            }
            current.cpuUsage > 60.0 || current.memoryUsage > 300 * 1024 * 1024 -> {
                PerformanceStatus.WARNING
            }
            else -> {
                PerformanceStatus.GOOD
            }
        }
    }
}

// MARK: - Data Models

data class PerformanceMetric(
    val cpuUsage: Double,
    val memoryUsage: Long,
    val batteryLevel: Float,
    val networkActivity: Double,
    val timestamp: Long
)

enum class PerformanceStatus {
    GOOD, WARNING, CRITICAL, UNKNOWN
}

