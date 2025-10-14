package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import family.aladdin.android.models.FamilyRole
import family.aladdin.android.models.AgeGroup
import family.aladdin.android.models.FamilyMember
import family.aladdin.android.models.CreateFamilyRequest
import family.aladdin.android.models.CreateFamilyResponse
import family.aladdin.android.models.JoinFamilyRequest
import family.aladdin.android.models.JoinFamilyResponse
import family.aladdin.android.models.RecoverFamilyResponse
import family.aladdin.android.models.FamilyMemberDetail
import family.aladdin.android.network.ApiService
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * 🏠 Family Registration ViewModel
 * Управление процессом прогрессивной регистрации
 * 
 * Отвечает за:
 * - Создание новой семьи
 * - Присоединение к существующей семье
 * - Восстановление доступа
 * - Интеграция с family_registration.py backend
 */

class FamilyRegistrationViewModel(
    private val apiService: ApiService,
    private val context: android.content.Context
) : ViewModel() {
    
    // MARK: - State
    
    private val _currentStep = MutableStateFlow(RegistrationStep.IDLE)
    val currentStep: StateFlow<RegistrationStep> = _currentStep.asStateFlow()
    
    private val _showConsentModal = MutableStateFlow(false)
    val showConsentModal: StateFlow<Boolean> = _showConsentModal.asStateFlow()
    
    private val _showRoleModal = MutableStateFlow(false)
    val showRoleModal: StateFlow<Boolean> = _showRoleModal.asStateFlow()
    
    private val _showAgeGroupModal = MutableStateFlow(false)
    val showAgeGroupModal: StateFlow<Boolean> = _showAgeGroupModal.asStateFlow()
    
    private val _showLetterModal = MutableStateFlow(false)
    val showLetterModal: StateFlow<Boolean> = _showLetterModal.asStateFlow()
    
    private val _showFamilyCreatedModal = MutableStateFlow(false)
    val showFamilyCreatedModal: StateFlow<Boolean> = _showFamilyCreatedModal.asStateFlow()
    
    private val _showSuccessModal = MutableStateFlow(false)
    val showSuccessModal: StateFlow<Boolean> = _showSuccessModal.asStateFlow()
    
    private val _consentAccepted = MutableStateFlow(false)
    val consentAccepted: StateFlow<Boolean> = _consentAccepted.asStateFlow()
    
    private val _selectedRole = MutableStateFlow<FamilyRole?>(null)
    val selectedRole: StateFlow<FamilyRole?> = _selectedRole.asStateFlow()
    
    private val _selectedAgeGroup = MutableStateFlow<AgeGroup?>(null)
    val selectedAgeGroup: StateFlow<AgeGroup?> = _selectedAgeGroup.asStateFlow()
    
    private val _selectedLetter = MutableStateFlow<String?>(null)
    val selectedLetter: StateFlow<String?> = _selectedLetter.asStateFlow()
    
    private val _familyID = MutableStateFlow<String?>(null)
    val familyID: StateFlow<String?> = _familyID.asStateFlow()
    
    private val _recoveryCode = MutableStateFlow<String?>(null)
    val recoveryCode: StateFlow<String?> = _recoveryCode.asStateFlow()
    
    private val _familyMembers = MutableStateFlow<List<FamilyMember>>(emptyList())
    val familyMembers: StateFlow<List<FamilyMember>> = _familyMembers.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    // MARK: - Registration Steps
    
    enum class RegistrationStep {
        IDLE,
        SHOWING_CONSENT,
        SELECTING_ROLE,
        SELECTING_AGE_GROUP,
        SELECTING_LETTER,
        CREATING_FAMILY,
        SHOWING_RECOVERY_CODE,
        COMPLETED
    }
    
    // MARK: - Public Methods
    
    /**
     * Начать регистрацию (показать Consent)
     */
    fun startRegistration() {
        viewModelScope.launch {
            // Проверяем, было ли согласие дано ранее
            val sharedPrefs = context.getSharedPreferences("aladdin_prefs", android.content.Context.MODE_PRIVATE)
            
            if (sharedPrefs.getBoolean("consent_accepted", false)) {
                // Согласие уже дано - пропускаем
                _consentAccepted.value = true
                showRoleSelection()
            } else {
                // Показываем Consent Modal
                _currentStep.value = RegistrationStep.SHOWING_CONSENT
                _showConsentModal.value = true
            }
        }
    }
    
    /**
     * Согласие принято
     */
    fun acceptConsent() {
        viewModelScope.launch {
            _consentAccepted.value = true
            
            // Сохраняем в SharedPreferences
            val sharedPrefs = context.getSharedPreferences("aladdin_prefs", android.content.Context.MODE_PRIVATE)
            sharedPrefs.edit().apply {
                putBoolean("consent_accepted", true)
                putLong("consent_date", System.currentTimeMillis())
                putString("consent_version", "2.0")
                apply()
            }
            
            _showConsentModal.value = false
            
            // Переходим к выбору роли
            showRoleSelection()
        }
    }
    
    /**
     * Показать выбор роли
     */
    fun showRoleSelection() {
        _currentStep.value = RegistrationStep.SELECTING_ROLE
        _showRoleModal.value = true
    }
    
    /**
     * Выбрана роль
     */
    fun onRoleSelected(role: FamilyRole) {
        viewModelScope.launch {
            _selectedRole.value = role
            _showRoleModal.value = false
            
            delay(500)
            
            _currentStep.value = RegistrationStep.SELECTING_AGE_GROUP
            _showAgeGroupModal.value = true
        }
    }
    
    fun onAgeGroupSelected(ageGroup: AgeGroup) {
        viewModelScope.launch {
            _selectedAgeGroup.value = ageGroup
            _showAgeGroupModal.value = false
            
            delay(500)
            
            _currentStep.value = RegistrationStep.SELECTING_LETTER
            _showLetterModal.value = true
        }
    }
    
    fun onLetterSelected(letter: String) {
        viewModelScope.launch {
            _selectedLetter.value = letter
            _showLetterModal.value = false
            
            delay(500)
            
            createFamily()
        }
    }
    
    // MARK: - Create Family
    
    private fun createFamily() {
        val role = _selectedRole.value ?: return
        val ageGroup = _selectedAgeGroup.value ?: return
        val letter = _selectedLetter.value ?: return
        
        viewModelScope.launch {
            _currentStep.value = RegistrationStep.CREATING_FAMILY
            _isLoading.value = true
            
            try {
                val request = CreateFamilyRequest(
                    role = role.value,
                    age_group = ageGroup.value,
                    personal_letter = letter,
                    device_type = getDeviceType()
                )
                
                val response = apiService.createFamily(request)
                
                _familyID.value = response.family_id
                _recoveryCode.value = response.recovery_code
                
                _currentStep.value = RegistrationStep.SHOWING_RECOVERY_CODE
                
                delay(500)
                
                _showFamilyCreatedModal.value = true
                
            } catch (e: Exception) {
                _errorMessage.value = e.message
                android.util.Log.e("FamilyRegistration", "Error creating family", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    // MARK: - Join Family
    
    fun joinFamily(familyCode: String) {
        val role = _selectedRole.value ?: return
        val ageGroup = _selectedAgeGroup.value ?: return
        val letter = _selectedLetter.value ?: return
        
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                val request = JoinFamilyRequest(
                    family_id = extractFamilyID(familyCode),
                    role = role.value,
                    age_group = ageGroup.value,
                    personal_letter = letter,
                    device_type = getDeviceType()
                )
                
                val response = apiService.joinFamily(request)
                
                _familyID.value = response.family_id
                _familyMembers.value = response.members.map { member ->
                    FamilyMember(
                        id = member.member_id,
                        letter = member.personal_letter,
                        role = FamilyRole.values().find { it.value == member.role } ?: FamilyRole.OTHER,
                        ageGroup = AgeGroup.values().find { it.value == member.age_group } ?: AgeGroup.ADULT_24_55,
                        isYou = member.member_id == response.your_member_id
                    )
                }
                
                _currentStep.value = RegistrationStep.COMPLETED
                _showSuccessModal.value = true
                
            } catch (e: Exception) {
                _errorMessage.value = e.message
                android.util.Log.e("FamilyRegistration", "Error joining family", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    // MARK: - Recover Access
    
    fun recoverAccess(recoveryCode: String) {
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                val familyId = extractFamilyID(recoveryCode)
                val response = apiService.recoverFamily(familyId)
                
                _familyID.value = response.family_id
                _familyMembers.value = response.members.map { member ->
                    FamilyMember(
                        id = member.member_id,
                        letter = member.personal_letter,
                        role = FamilyRole.values().find { it.value == member.role } ?: FamilyRole.OTHER,
                        ageGroup = AgeGroup.values().find { it.value == member.age_group } ?: AgeGroup.ADULT_24_55,
                        isYou = false
                    )
                }
                
                _currentStep.value = RegistrationStep.COMPLETED
                _showSuccessModal.value = true
                
            } catch (e: Exception) {
                _errorMessage.value = e.message
                android.util.Log.e("FamilyRegistration", "Error recovering family", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private fun extractFamilyID(code: String): String {
        // Convert FAM-A1B2-C3D4-E5F6 → FAM_A1B2C3D4E5F6
        return code.replace("-", "").replace("FAM", "FAM_")
    }
    
    private fun getDeviceType(): String {
        return "smartphone"  // TODO: Detect tablet
    }
    
    /**
     * Закрыть модалку "Семья создана"
     */
    fun dismissFamilyCreatedModal() {
        _showFamilyCreatedModal.value = false
    }
    
    /**
     * Закрыть модалку "Успешная регистрация"
     */
    fun dismissSuccessModal() {
        _showSuccessModal.value = false
    }
}

// MARK: - API Service Extension

suspend fun ApiService.createFamily(request: CreateFamilyRequest): CreateFamilyResponse {
    // TODO: Implement actual API call using request
    return CreateFamilyResponse(
        success = true,
        family_id = "FAM_A1B2C3D4E5F6",
        recovery_code = "FAM-A1B2-C3D4-E5F6",
        qr_code_data = "{}",
        short_code = "AB12",
        member_id = "MEM_X1Y2Z3W4"
    )
}

suspend fun ApiService.joinFamily(request: JoinFamilyRequest): JoinFamilyResponse {
    // TODO: Implement actual API call
    return JoinFamilyResponse(
        success = true,
        family_id = request.family_id,
        your_member_id = "MEM_NEW123",
        role = request.role,
        personal_letter = request.personal_letter,
        members = emptyList()
    )
}

suspend fun ApiService.recoverFamily(familyId: String): RecoverFamilyResponse {
    // TODO: Implement actual API call
    return RecoverFamilyResponse(
        success = true,
        family_id = familyId,
        members = emptyList(),
        family_status = emptyMap()
    )
}

