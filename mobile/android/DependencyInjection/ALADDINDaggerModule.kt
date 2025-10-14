package com.aladdin.mobile.di

import android.content.Context
import com.aladdin.mobile.network.ALADDINNetworkManager
import com.aladdin.mobile.security.*
import com.aladdin.mobile.vpn.ALADDINVPNClient
import com.aladdin.mobile.vpn.VPNManager
import com.aladdin.mobile.support.SupportAPIClient
import com.aladdin.mobile.support.SupportAPIManager
import com.aladdin.mobile.viewmodels.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object ALADDINDaggerModule {
    
    // MARK: - Networking
    
    @Provides
    @Singleton
    fun provideNetworkManager(
        @ApplicationContext context: Context,
        certificatePinningManager: CertificatePinningManager
    ): ALADDINNetworkManager {
        return ALADDINNetworkManager(context, certificatePinningManager)
    }
    
    @Provides
    @Singleton
    fun provideCertificatePinningManager(
        @ApplicationContext context: Context
    ): CertificatePinningManager {
        return CertificatePinningManager(context)
    }
    
    // MARK: - Security
    
    @Provides
    @Singleton
    fun provideSecurityManager(
        @ApplicationContext context: Context,
        rootDetector: RootDetector,
        raspManager: RASPManager,
        antiTamperingManager: AntiTamperingManager
    ): ALADDINSecurityManager {
        return ALADDINSecurityManager(
            context,
            rootDetector,
            raspManager,
            antiTamperingManager
        )
    }
    
    @Provides
    @Singleton
    fun provideRootDetector(
        @ApplicationContext context: Context
    ): RootDetector {
        return RootDetector(context)
    }
    
    @Provides
    @Singleton
    fun provideRASPManager(
        @ApplicationContext context: Context
    ): RASPManager {
        return RASPManager(context)
    }
    
    @Provides
    @Singleton
    fun provideAntiTamperingManager(
        @ApplicationContext context: Context
    ): AntiTamperingManager {
        return AntiTamperingManager(context)
    }
    
    // MARK: - AI & Support
    
    @Provides
    @Singleton
    fun provideSupportAPIClient(
        networkManager: ALADDINNetworkManager
    ): SupportAPIClient {
        return SupportAPIClient(networkManager)
    }
    
    @Provides
    @Singleton
    fun provideSupportAPIManager(
        supportAPIClient: SupportAPIClient
    ): SupportAPIManager {
        return SupportAPIManager(supportAPIClient)
    }
    
    // MARK: - VPN
    
    @Provides
    @Singleton
    fun provideVPNClient(
        @ApplicationContext context: Context,
        networkManager: ALADDINNetworkManager
    ): ALADDINVPNClient {
        return ALADDINVPNClient(context, networkManager)
    }
    
    @Provides
    @Singleton
    fun provideVPNManager(
        vpnClient: ALADDINVPNClient
    ): VPNManager {
        return VPNManager(vpnClient)
    }
    
    // MARK: - ViewModels
    
    @Provides
    fun provideMainViewModel(
        networkManager: ALADDINNetworkManager,
        securityManager: ALADDINSecurityManager
    ): MainViewModel {
        return MainViewModel(networkManager, securityManager)
    }
    
    @Provides
    fun provideProtectionViewModel(
        vpnManager: VPNManager,
        securityManager: ALADDINSecurityManager
    ): ProtectionViewModel {
        return ProtectionViewModel(vpnManager, securityManager)
    }
    
    @Provides
    fun provideFamilyViewModel(
        networkManager: ALADDINNetworkManager
    ): FamilyViewModel {
        return FamilyViewModel(networkManager)
    }
    
    @Provides
    fun provideAnalyticsViewModel(
        networkManager: ALADDINNetworkManager
    ): AnalyticsViewModel {
        return AnalyticsViewModel(networkManager)
    }
    
    @Provides
    fun provideSettingsViewModel(
        networkManager: ALADDINNetworkManager,
        securityManager: ALADDINSecurityManager
    ): SettingsViewModel {
        return SettingsViewModel(networkManager, securityManager)
    }
    
    @Provides
    fun provideSupportViewModel(
        supportAPIManager: SupportAPIManager
    ): SupportViewModel {
        return SupportViewModel(supportAPIManager)
    }
}

// MARK: - Security Manager

class ALADDINSecurityManager(
    private val context: Context,
    private val rootDetector: RootDetector,
    private val raspManager: RASPManager,
    private val antiTamperingManager: AntiTamperingManager
) {
    
    fun performSecurityChecks(): Boolean {
        // Проверка Root
        if (rootDetector.isRooted()) {
            android.util.Log.w("SecurityManager", "Device is rooted")
            return false
        }
        
        // Проверка целостности
        if (antiTamperingManager.validateAppIntegrity().isTampered) {
            android.util.Log.w("SecurityManager", "App integrity compromised")
            return false
        }
        
        // Запуск RASP мониторинга
        raspManager.startMonitoring()
        
        return true
    }
    
    fun getSecurityStatus(): SecurityStatus {
        val rootResult = rootDetector.detectRoot()
        val tamperingResult = antiTamperingManager.validateAppIntegrity()
        val raspStatus = raspManager.getMonitoringStatus()
        
        val overallStatus = when {
            rootResult.isRooted || tamperingResult.isTampered -> SecurityLevel.CRITICAL
            raspStatus.threatCount > 5 -> SecurityLevel.HIGH
            raspStatus.threatCount > 2 -> SecurityLevel.MEDIUM
            else -> SecurityLevel.LOW
        }
        
        return SecurityStatus(
            isRooted = rootResult.isRooted,
            isTampered = tamperingResult.isTampered,
            raspThreatCount = raspStatus.threatCount,
            overallStatus = overallStatus
        )
    }
}

// MARK: - Data Models

data class SecurityStatus(
    val isRooted: Boolean,
    val isTampered: Boolean,
    val raspThreatCount: Int,
    val overallStatus: SecurityLevel
)

enum class SecurityLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}

// MARK: - Application Class

@dagger.hilt.android.HiltAndroidApp
class ALADDINApplication : android.app.Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // Инициализация Dagger Hilt
        android.util.Log.i("ALADDINApp", "Dagger Hilt initialized")
        
        // Запуск безопасности
        initializeSecurity()
    }
    
    private fun initializeSecurity() {
        // Security Manager будет внедрен через Dagger
        android.util.Log.i("ALADDINApp", "Security initialized")
    }
}

