package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MainViewModel : ViewModel() {
    private val _isVPNEnabled = MutableStateFlow(true)
    val isVPNEnabled: StateFlow<Boolean> = _isVPNEnabled
    
    private val _threatsBlocked = MutableStateFlow(47)
    val threatsBlocked: StateFlow<Int> = _threatsBlocked
    
    fun toggleVPN() {
        _isVPNEnabled.value = !_isVPNEnabled.value
    }
    
    fun refreshStats() {
        // Load data from API
    }
}




