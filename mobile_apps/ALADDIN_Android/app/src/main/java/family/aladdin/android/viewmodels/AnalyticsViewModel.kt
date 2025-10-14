package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class AnalyticsViewModel : ViewModel() {
    private val _threatsDetected = MutableStateFlow(47)
    val threatsDetected: StateFlow<Int> = _threatsDetected
    
    private val _threatsBlocked = MutableStateFlow(45)
    val threatsBlocked: StateFlow<Int> = _threatsBlocked
    
    private val _protectionLevel = MutableStateFlow(96)
    val protectionLevel: StateFlow<Int> = _protectionLevel
    
    fun changePeriod(period: String) {
        // TODO: Update stats based on period
    }
}



