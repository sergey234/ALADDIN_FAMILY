package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class VPNViewModel : ViewModel() {
    private val _isVPNEnabled = MutableStateFlow(true)
    val isVPNEnabled: StateFlow<Boolean> = _isVPNEnabled
    
    private val _currentIP = MutableStateFlow("192.168.1.147")
    val currentIP: StateFlow<String> = _currentIP
    
    fun toggleVPN() {
        _isVPNEnabled.value = !_isVPNEnabled.value
    }
}




