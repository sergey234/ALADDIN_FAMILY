package com.aladdin.mobile.network

import android.content.Context
import com.aladdin.mobile.security.CertificatePinningManager
import com.aladdin.mobile.security.CertificatePinningInterceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ALADDINNetworkManager @Inject constructor(
    private val context: Context,
    private val certificatePinningManager: CertificatePinningManager
) {
    
    private val okHttpClient: OkHttpClient
    private val retrofit: Retrofit
    
    init {
        // Создаем OkHttpClient с certificate pinning
        okHttpClient = createSecureClient()
        
        // Создаем Retrofit с безопасным клиентом
        retrofit = createRetrofit()
    }
    
    // Создание безопасного OkHttpClient
    private fun createSecureClient(): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        val pinningInterceptor = CertificatePinningInterceptor(certificatePinningManager)
        
        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor(pinningInterceptor)
            .certificatePinner(certificatePinningManager.createSecureClient().certificatePinner)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }
    
    // Создание Retrofit
    private fun createRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.aladdin.security/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    // MARK: - API Methods
    
    // Безопасный запрос с pinning
    suspend fun <T> secureRequest(
        endpoint: String,
        method: HttpMethod = HttpMethod.GET,
        parameters: Map<String, Any>? = null,
        headers: Map<String, String>? = null,
        responseType: Class<T>
    ): Result<T> {
        return try {
            val apiService = retrofit.create(ALADDINApiService::class.java)
            val response = when (method) {
                HttpMethod.GET -> apiService.get(endpoint, parameters, headers)
                HttpMethod.POST -> apiService.post(endpoint, parameters, headers)
                HttpMethod.PUT -> apiService.put(endpoint, parameters, headers)
                HttpMethod.DELETE -> apiService.delete(endpoint, parameters, headers)
            }
            
            if (response.isSuccessful) {
                Result.success(response.body() as T)
            } else {
                Result.failure(ALADDINException.NetworkException("Server error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(ALADDINException.NetworkException("Request failed: ${e.message}"))
        }
    }
    
    // Загрузка данных с проверкой сертификата
    suspend fun downloadData(url: String): Result<ByteArray> {
        return try {
            val request = okhttp3.Request.Builder()
                .url(url)
                .build()
            
            val response = okHttpClient.newCall(request).execute()
            
            if (response.isSuccessful) {
                val data = response.body?.bytes() ?: ByteArray(0)
                Result.success(data)
            } else {
                Result.failure(ALADDINException.NetworkException("Download failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(ALADDINException.NetworkException("Download error: ${e.message}"))
        }
    }
    
    // MARK: - Security Methods
    
    // Проверка статуса pinning
    fun getPinningStatus(): Map<String, Boolean> {
        return certificatePinningManager.getPinningStatus()
    }
    
    // Обновление сертификатов
    fun updateCertificates() {
        certificatePinningManager.updateCertificates()
    }
    
    // MARK: - Network Monitoring
    
    // Мониторинг сетевого соединения
    fun startNetworkMonitoring() {
        // В Android используется ConnectivityManager
        android.util.Log.i("NetworkManager", "Starting network monitoring...")
    }
}

// MARK: - API Service Interface
interface ALADDINApiService {
    @retrofit2.http.GET
    suspend fun get(
        @retrofit2.http.Url url: String,
        @retrofit2.http.QueryMap parameters: Map<String, Any>?,
        @retrofit2.http.HeaderMap headers: Map<String, String>?
    ): retrofit2.Response<Any>
    
    @retrofit2.http.POST
    suspend fun post(
        @retrofit2.http.Url url: String,
        @retrofit2.http.Body parameters: Map<String, Any>?,
        @retrofit2.http.HeaderMap headers: Map<String, String>?
    ): retrofit2.Response<Any>
    
    @retrofit2.http.PUT
    suspend fun put(
        @retrofit2.http.Url url: String,
        @retrofit2.http.Body parameters: Map<String, Any>?,
        @retrofit2.http.HeaderMap headers: Map<String, String>?
    ): retrofit2.Response<Any>
    
    @retrofit2.http.DELETE
    suspend fun delete(
        @retrofit2.http.Url url: String,
        @retrofit2.http.QueryMap parameters: Map<String, Any>?,
        @retrofit2.http.HeaderMap headers: Map<String, String>?
    ): retrofit2.Response<Any>
}

// MARK: - HTTP Methods
enum class HttpMethod {
    GET, POST, PUT, DELETE
}

// MARK: - Exception Types
sealed class ALADDINException(message: String) : Exception(message) {
    class NetworkException(message: String) : ALADDINException(message)
    class SecurityException(message: String) : ALADDINException(message)
    class CertificateException(message: String) : ALADDINException(message)
}

