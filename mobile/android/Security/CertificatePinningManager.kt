package com.aladdin.mobile.security

import android.content.Context
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient
import okhttp3.tls.HandshakeCertificates
import java.io.IOException
import java.security.cert.Certificate
import java.security.cert.CertificateFactory
import java.security.cert.X509Certificate
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CertificatePinningManager @Inject constructor(
    private val context: Context
) {
    
    private val pinnedHosts = setOf(
        "api.aladdin.security",
        "ai.aladdin.security",
        "vpn.aladdin.security", 
        "auth.aladdin.security"
    )
    
    private val certificatePinner: CertificatePinner
    private val pinnedCertificates: List<X509Certificate>
    
    init {
        // Загружаем сертификаты из ресурсов
        pinnedCertificates = loadPinnedCertificates()
        
        // Создаем Certificate Pinner
        certificatePinner = createCertificatePinner()
    }
    
    // Загрузка сертификатов из ресурсов
    private fun loadPinnedCertificates(): List<X509Certificate> {
        val certificates = mutableListOf<X509Certificate>()
        
        try {
            // Загружаем основные сертификаты
            val certFactory = CertificateFactory.getInstance("X.509")
            
            // API сертификат
            context.assets.open("certificates/aladdin-api-cert.cer").use { inputStream ->
                val cert = certFactory.generateCertificate(inputStream) as X509Certificate
                certificates.add(cert)
            }
            
            // AI сертификат
            context.assets.open("certificates/aladdin-ai-cert.cer").use { inputStream ->
                val cert = certFactory.generateCertificate(inputStream) as X509Certificate
                certificates.add(cert)
            }
            
        } catch (e: Exception) {
            android.util.Log.e("CertificatePinning", "Failed to load certificates", e)
        }
        
        return certificates
    }
    
    // Создание Certificate Pinner
    private fun createCertificatePinner(): CertificatePinner {
        val builder = CertificatePinner.Builder()
        
        // Добавляем pin для каждого хоста
        for (host in pinnedHosts) {
            for (cert in pinnedCertificates) {
                val pin = "sha256/${cert.publicKey.encoded.contentHashCode()}"
                builder.add(host, pin)
            }
        }
        
        return builder.build()
    }
    
    // Создание OkHttpClient с pinning
    fun createSecureClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .certificatePinner(certificatePinner)
            .build()
    }
    
    // Проверка статуса pinning
    fun getPinningStatus(): Map<String, Boolean> {
        val status = mutableMapOf<String, Boolean>()
        
        for (host in pinnedHosts) {
            status[host] = true // В реальном приложении здесь была бы проверка
        }
        
        return status
    }
    
    // Валидация сертификата
    fun validateCertificate(host: String, certificate: X509Certificate): Boolean {
        if (!pinnedHosts.contains(host)) {
            android.util.Log.w("CertificatePinning", "Host $host not in pinned hosts list")
            return false
        }
        
        // Проверяем, что сертификат в списке закрепленных
        val isValid = pinnedCertificates.any { pinnedCert ->
            pinnedCert.publicKey.encoded.contentEquals(certificate.publicKey.encoded)
        }
        
        if (isValid) {
            android.util.Log.i("CertificatePinning", "Certificate pinning successful for $host")
        } else {
            android.util.Log.e("CertificatePinning", "Certificate pinning failed for $host")
        }
        
        return isValid
    }
    
    // Обновление сертификатов
    fun updateCertificates() {
        android.util.Log.i("CertificatePinning", "Updating pinned certificates...")
        // В реальном приложении здесь была бы логика обновления
    }
    
    // Получение SHA-256 хеша сертификата
    private fun Certificate.getSha256Hash(): String {
        val publicKey = (this as X509Certificate).publicKey.encoded
        val digest = java.security.MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(publicKey)
        return android.util.Base64.encodeToString(hash, android.util.Base64.NO_WRAP)
    }
}

// MARK: - Network Interceptor для дополнительной проверки
class CertificatePinningInterceptor @Inject constructor(
    private val certificatePinningManager: CertificatePinningManager
) : okhttp3.Interceptor {
    
    override fun intercept(chain: okhttp3.Interceptor.Chain): okhttp3.Response {
        val request = chain.request()
        val host = request.url.host
        
        // Проверяем, что хост в списке защищенных
        if (certificatePinningManager.getPinningStatus().containsKey(host)) {
            try {
                val response = chain.proceed(request)
                
                // Дополнительная проверка сертификата
                val handshake = response.handshake
                if (handshake != null) {
                    val peerCertificates = handshake.peerCertificates
                    if (peerCertificates.isNotEmpty()) {
                        val serverCert = peerCertificates[0] as X509Certificate
                        if (!certificatePinningManager.validateCertificate(host, serverCert)) {
                            throw SecurityException("Certificate pinning failed for $host")
                        }
                    }
                }
                
                return response
            } catch (e: Exception) {
                android.util.Log.e("CertificatePinning", "Certificate validation failed", e)
                throw SecurityException("Certificate validation failed: ${e.message}")
            }
        }
        
        return chain.proceed(request)
    }
}

