package family.aladdin.android

import android.app.Application
import family.aladdin.android.analytics.AnalyticsManager

class ALADDINApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // Initialize Analytics
        AnalyticsManager.initialize(this)
        
        // Log app launch
        AnalyticsManager.logEvent("app_open", mapOf(
            "timestamp" to System.currentTimeMillis(),
            "version" to "1.0"
        ))
    }
}


