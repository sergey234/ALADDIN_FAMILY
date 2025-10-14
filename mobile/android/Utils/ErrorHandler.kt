package com.aladdin.mobile.utils

import android.content.Context
import android.util.Log
import androidx.appcompat.app.AlertDialog
import com.aladdin.mobile.network.ALADDINException
import kotlinx.coroutines.delay
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.min
import kotlin.math.pow

@Singleton
class ErrorHandler @Inject constructor(
    private val context: Context
) {
    
    // MARK: - Error Handling
    
    fun handle(error: Throwable, source: String = "", line: Int = 0) {
        val errorInfo = ErrorInfo(
            error = error,
            source = source,
            line = line,
            timestamp = System.currentTimeMillis()
        )
        
        // Log error
        logError(errorInfo)
        
        // Send to analytics
        sendToAnalytics(errorInfo)
        
        // Show user-friendly message
        showUserMessage(error)
    }
    
    fun handle(exception: ALADDINException, source: String = "", line: Int = 0) {
        handle(exception as Throwable, source, line)
    }
    
    // MARK: - Logging
    
    private fun logError(errorInfo: ErrorInfo) {
        Log.e(
            "ErrorHandler",
            "ERROR [${java.util.Date(errorInfo.timestamp)}]\n" +
                    "Source: ${errorInfo.source}:${errorInfo.line}\n" +
                    "Error: ${errorInfo.error.message}",
            errorInfo.error
        )
        
        // В production это было бы отправлено в систему логирования
    }
    
    // MARK: - Analytics
    
    private fun sendToAnalytics(errorInfo: ErrorInfo) {
        // В реальном приложении здесь была бы отправка в Firebase/Crashlytics
        Log.i("ErrorHandler", "Sending error to analytics...")
    }
    
    // MARK: - User Messages
    
    private fun showUserMessage(error: Throwable) {
        val message = getUserFriendlyMessage(error)
        
        // В реальном приложении здесь был бы показ диалога
        Log.i("ErrorHandler", "User message: $message")
    }
    
    fun showAlertDialog(title: String, message: String) {
        AlertDialog.Builder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("OK", null)
            .show()
    }
    
    private fun getUserFriendlyMessage(error: Throwable): String {
        return when (error) {
            is ALADDINException.NetworkException -> {
                when {
                    error.message?.contains("No internet", ignoreCase = true) == true -> 
                        "Нет подключения к интернету"
                    error.message?.contains("timeout", ignoreCase = true) == true -> 
                        "Превышено время ожидания"
                    error.message?.contains("Server error", ignoreCase = true) == true -> 
                        "Ошибка сервера"
                    else -> "Ошибка сети. Попробуйте позже."
                }
            }
            is ALADDINException.SecurityException -> {
                "Ошибка безопасности соединения"
            }
            is ALADDINException.CertificateException -> {
                "Недействительный сертификат"
            }
            else -> "Произошла ошибка. Попробуйте позже."
        }
    }
    
    // MARK: - Recovery
    
    suspend fun attemptRecovery(error: Throwable): Boolean {
        return when (error) {
            is ALADDINException.NetworkException -> {
                when {
                    error.message?.contains("No internet", ignoreCase = true) == true -> {
                        // Retry with exponential backoff
                        retryWithBackoff()
                    }
                    error.message?.contains("timeout", ignoreCase = true) == true -> {
                        // Retry immediately
                        true
                    }
                    else -> false
                }
            }
            is ALADDINException.SecurityException,
            is ALADDINException.CertificateException -> {
                // Cannot recover from security errors
                false
            }
            else -> false
        }
    }
    
    private suspend fun retryWithBackoff(attempt: Int = 1, maxAttempts: Int = 5): Boolean {
        if (attempt > maxAttempts) {
            return false
        }
        
        val delayMs = min(2.0.pow(attempt.toDouble()), 30.0) * 1000 // Max 30 seconds
        delay(delayMs.toLong())
        
        // Check if network is available
        return isNetworkAvailable()
    }
    
    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) 
            as android.net.ConnectivityManager
        val activeNetwork = connectivityManager.activeNetworkInfo
        return activeNetwork?.isConnected == true
    }
    
    // MARK: - Error Types Classification
    
    fun classifyError(error: Throwable): ErrorSeverity {
        return when (error) {
            is ALADDINException.SecurityException,
            is ALADDINException.CertificateException -> ErrorSeverity.CRITICAL
            
            is ALADDINException.NetworkException -> {
                if (error.message?.contains("Server error", ignoreCase = true) == true) {
                    ErrorSeverity.HIGH
                } else {
                    ErrorSeverity.MEDIUM
                }
            }
            
            else -> ErrorSeverity.LOW
        }
    }
}

// MARK: - Data Models

data class ErrorInfo(
    val error: Throwable,
    val source: String,
    val line: Int,
    val timestamp: Long
)

enum class ErrorSeverity {
    LOW, MEDIUM, HIGH, CRITICAL
}

// MARK: - Result Extension

fun <T> Result<T>.handleError(handler: ErrorHandler): Result<T> {
    if (this.isFailure) {
        handler.handle(this.exceptionOrNull()!!)
    }
    return this
}

