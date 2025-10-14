package family.aladdin.android.models

/**
 * 🏠 Family Registration Models
 * Модели для анонимной семейной регистрации
 */

// MARK: - Enums

enum class FamilyRole(val value: String) {
    PARENT("parent"),
    CHILD("child"),
    ELDERLY("elderly"),
    OTHER("other")
}

enum class AgeGroup(val value: String, val display: String, val description: String) {
    CHILD_1_6("1-6", "1-6 лет", "Дошкольник"),
    CHILD_7_12("7-12", "7-12 лет", "Школьник"),
    TEEN_13_17("13-17", "13-17 лет", "Подросток"),
    YOUNG_ADULT_18_23("18-23", "18-23 года", "Молодой взрослый"),
    ADULT_24_55("24-55", "24-55 лет", "Взрослый"),
    ELDERLY_55_PLUS("55+", "55+ лет", "Пожилой")
}

// MARK: - Data Classes

data class FamilyMember(
    val id: String,
    val letter: String,
    val role: FamilyRole,
    val ageGroup: AgeGroup,
    val isYou: Boolean = false
)

data class CreateFamilyRequest(
    val role: String,
    val age_group: String,
    val personal_letter: String,
    val device_type: String
)

data class CreateFamilyResponse(
    val success: Boolean,
    val family_id: String,
    val recovery_code: String,
    val qr_code_data: String,
    val short_code: String,
    val member_id: String
)

data class JoinFamilyRequest(
    val family_id: String,
    val role: String,
    val age_group: String,
    val personal_letter: String,
    val device_type: String
)

data class JoinFamilyResponse(
    val success: Boolean,
    val family_id: String,
    val your_member_id: String,
    val role: String,
    val personal_letter: String,
    val members: List<FamilyMemberDetail>
)

data class FamilyMemberDetail(
    val member_id: String,
    val role: String,
    val age_group: String,
    val personal_letter: String,
    val device_type: String,
    val registration_time: String,
    val last_active: String,
    val is_active: Boolean
)

data class RecoverFamilyResponse(
    val success: Boolean,
    val family_id: String,
    val members: List<FamilyMemberDetail>,
    val family_status: Map<String, Any>
)



