package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow

class SettingsViewModel : ViewModel() {
    val isVPNEnabled = MutableStateFlow(true)
    val isNotificationsEnabled = MutableStateFlow(true)
    val isBiometricEnabled = MutableStateFlow(true)
    val protectionLevel = MutableStateFlow(75f)
    
    fun toggleVPN() { isVPNEnabled.value = !isVPNEnabled.value }
    fun toggleNotifications() { isNotificationsEnabled.value = !isNotificationsEnabled.value }
    fun toggleBiometric() { isBiometricEnabled.value = !isBiometricEnabled.value }
    fun updateProtectionLevel(value: Float) { protectionLevel.value = value }
}



