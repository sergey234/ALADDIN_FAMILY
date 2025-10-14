package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

data class FamilyMember(
    val name: String,
    val role: String,
    val avatar: String,
    val status: String,
    val threatsBlocked: Int
)

class FamilyViewModel : ViewModel() {
    private val _familyMembers = MutableStateFlow<List<FamilyMember>>(emptyList())
    val familyMembers: StateFlow<List<FamilyMember>> = _familyMembers
    
    init {
        loadFamilyMembers()
    }
    
    private fun loadFamilyMembers() {
        _familyMembers.value = listOf(
            FamilyMember("Сергей", "Родитель", "👨", "protected", 47),
            FamilyMember("Мария", "Родитель", "👩", "protected", 32),
            FamilyMember("Маша", "Ребёнок", "👧", "warning", 23),
            FamilyMember("Бабушка", "Пожилой", "👵", "offline", 12)
        )
    }
    
    fun addFamilyMember() {
        // Show add dialog
    }
}




