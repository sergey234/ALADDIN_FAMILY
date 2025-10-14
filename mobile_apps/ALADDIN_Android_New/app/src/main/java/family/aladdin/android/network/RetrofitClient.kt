package family.aladdin.android.network

import family.aladdin.android.config.AppConfig
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * 🌐 Retrofit Client
 * HTTP клиент для подключения к Python backend
 * Использует Retrofit 2 + OkHttp
 */

object RetrofitClient {
    
    private const val TIMEOUT_SECONDS = 30L
    
    /**
     * OkHttp клиент с настройками
     */
    private val okHttpClient: OkHttpClient by lazy {
        val builder = OkHttpClient.Builder()
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        
        // Логирование (только в DEBUG режиме)
        if (AppConfig.isDebugMode) {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            builder.addInterceptor(loggingInterceptor)
        }
        
        // Interceptor для добавления заголовков
        val headerInterceptor = Interceptor { chain ->
            val original = chain.request()
            val requestBuilder = original.newBuilder()
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
            
            // Добавляем токен авторизации если есть
            AppConfig.authToken?.let { token ->
                requestBuilder.header("Authorization", "Bearer $token")
            }
            
            val request = requestBuilder.build()
            chain.proceed(request)
        }
        
        builder.addInterceptor(headerInterceptor)
        builder.build()
    }
    
    /**
     * Retrofit instance
     */
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(AppConfig.apiBaseURL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    /**
     * API Service
     */
    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}



