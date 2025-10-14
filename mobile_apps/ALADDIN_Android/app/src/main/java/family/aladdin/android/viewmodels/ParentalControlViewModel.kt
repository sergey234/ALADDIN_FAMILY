package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow

class ParentalControlViewModel : ViewModel() {
    val isContentFilterEnabled = MutableStateFlow(true)
    val screenTimeLimit = MutableStateFlow(3f)
    
    fun toggleContentFilter() {
        isContentFilterEnabled.value = !isContentFilterEnabled.value
    }
    
    fun updateScreenTimeLimit(value: Float) {
        screenTimeLimit.value = value
    }
}



