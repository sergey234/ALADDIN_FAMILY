# 🤖 ALADDIN Family Security - Android App

**Версия:** 1.0.0  
**Android:** 8.0+ (API 26+)  
**Язык:** Kotlin 1.9+  
**UI Framework:** Jetpack Compose  
**Архитектура:** MVVM

---

## 🎯 **ОПИСАНИЕ**

Мобильное приложение для комплексной защиты семьи в интернете с функциями VPN, родительского контроля, аналитики угроз и AI помощника.

---

## 📁 **СТРУКТУРА ПРОЕКТА**

```
ALADDIN_Android/
└── app/
    └── src/
        ├── main/
        │   ├── java/com/aladdin/familysecurity/
        │   │   ├── ALADDINApplication.kt      # Application class
        │   │   │
        │   │   ├── core/                      # Основная функциональность
        │   │   │   ├── network/
        │   │   │   │   ├── ApiClient.kt
        │   │   │   │   ├── Endpoints.kt
        │   │   │   │   └── NetworkError.kt
        │   │   │   ├── database/
        │   │   │   │   ├── AppDatabase.kt
        │   │   │   │   └── SecurePreferences.kt
        │   │   │   ├── vpn/
        │   │   │   │   ├── VPNManager.kt
        │   │   │   │   └── WireGuardService.kt
        │   │   │   └── utils/
        │   │   │       ├── Logger.kt
        │   │   │       └── Constants.kt
        │   │   │
        │   │   ├── features/                  # Экраны (14 штук)
        │   │   │   ├── auth/
        │   │   │   │   ├── ui/
        │   │   │   │   │   ├── LoginScreen.kt
        │   │   │   │   │   └── RegisterScreen.kt
        │   │   │   │   ├── viewmodel/
        │   │   │   │   │   └── AuthViewModel.kt
        │   │   │   │   └── model/
        │   │   │   │       └── User.kt
        │   │   │   │
        │   │   │   ├── main/                 # 1. Главный экран
        │   │   │   │   ├── ui/MainScreen.kt
        │   │   │   │   ├── viewmodel/MainViewModel.kt
        │   │   │   │   └── model/MainStatus.kt
        │   │   │   │
        │   │   │   ├── family/               # 2. Семья
        │   │   │   ├── protection/           # 3. VPN
        │   │   │   ├── analytics/            # 4. Аналитика
        │   │   │   ├── settings/             # 5. Настройки
        │   │   │   ├── parental/             # 6. Родительский контроль
        │   │   │   ├── ai/                   # 7. AI помощник
        │   │   │   ├── profile/              # 8. Профиль
        │   │   │   ├── devices/              # 9. Устройства
        │   │   │   ├── child/                # 10. Детский
        │   │   │   ├── elderly/              # 11. Пожилые
        │   │   │   ├── tariffs/              # 12. Тарифы
        │   │   │   ├── info/                 # 13. Информация
        │   │   │   └── notifications/        # 14. Уведомления
        │   │   │
        │   │   └── shared/                   # Переиспользуемые компоненты
        │   │       ├── components/
        │   │       │   ├── buttons/
        │   │       │   ├── cards/
        │   │       │   └── modals/
        │   │       ├── theme/
        │   │       │   ├── Colors.kt
        │   │       │   ├── Typography.kt
        │   │       │   └── Shapes.kt
        │   │       └── utils/
        │   │           └── Extensions.kt
        │   │
        │   ├── res/                          # Ресурсы Android
        │   │   ├── values/
        │   │   │   ├── strings.xml          # Переводы
        │   │   │   ├── colors.xml           # Цвета
        │   │   │   └── themes.xml           # Темы
        │   │   ├── drawable/                # Изображения
        │   │   └── mipmap/                  # Иконки
        │   │
        │   └── AndroidManifest.xml          # Манифест
        │
        └── test/                             # Тесты
            └── java/com/aladdin/familysecurity/
                ├── viewmodel/               # ViewModel тесты
                └── repository/              # Repository тесты
```

---

## 🎯 **АРХИТЕКТУРА MVVM**

### **Kotlin + Jetpack Compose:**

```kotlin
// Model
data class FamilyMember(
    val id: String,
    val name: String,
    val status: Status
)

// ViewModel
class FamilyViewModel : ViewModel() {
    private val _members = MutableStateFlow<List<FamilyMember>>(emptyList())
    val members: StateFlow<List<FamilyMember>> = _members.asStateFlow()
    
    fun loadMembers() {
        viewModelScope.launch {
            val data = repository.getMembers()
            _members.value = data
        }
    }
}

// View (Composable)
@Composable
fun FamilyScreen(viewModel: FamilyViewModel = hiltViewModel()) {
    val members by viewModel.members.collectAsState()
    
    LazyColumn {
        items(members) { member ->
            FamilyMemberCard(member)
        }
    }
}
```

---

## 📋 **14 ЭКРАНОВ**

| № | Feature | HTML Источник | Package |
|---|---------|---------------|---------|
| 1 | Main | 01_main_screen.html | features.main |
| 2 | Family | 03_family_screen.html | features.family |
| 3 | Protection | 02_protection_screen.html | features.protection |
| 4 | Analytics | 04_analytics_screen.html | features.analytics |
| 5 | Settings | 05_settings_screen.html | features.settings |
| 6 | Parental | 14_parental_control_screen.html | features.parental |
| 7 | AI | 08_ai_assistant.html | features.ai |
| 8 | Profile | 11_profile_screen.html | features.profile |
| 9 | Devices | 12_devices_screen.html | features.devices |
| 10 | Child | 06_child_interface.html | features.child |
| 11 | Elderly | 07_elderly_interface.html | features.elderly |
| 12 | Tariffs | 09_tariffs_screen.html | features.tariffs |
| 13 | Info | 10_info_screen.html | features.info |
| 14 | Notifications | 08_notifications_screen.html | features.notifications |

---

## 🔧 **ТРЕБОВАНИЯ**

### **Минимальные версии:**
- Android 8.0+ (API 26+)
- Android Studio Hedgehog+
- Kotlin 1.9+

### **Зависимости (build.gradle.kts):**
```kotlin
dependencies {
    // Jetpack Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    // Database
    implementation("androidx.room:room-runtime:2.6.0")
    
    // DI
    implementation("com.google.dagger:hilt-android:2.48")
    
    // VPN
    implementation("com.wireguard.android:tunnel:1.0.0")
    
    // Images
    implementation("io.coil-kt:coil-compose:2.5.0")
    
    // Maps
    implementation("com.google.maps.android:maps-compose:4.3.0")
}
```

---

## 🚀 **КАК НАЧАТЬ РАЗРАБОТКУ**

### **Шаг 1: Открыть проект**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_Android
# Открыть в Android Studio
```

### **Шаг 2: Выбрать Feature**
Например, MainScreen:
```
features/main/
├── ui/MainScreen.kt           ← Compose UI
├── viewmodel/MainViewModel.kt ← ViewModel + StateFlow
└── model/MainStatus.kt        ← Data class
```

### **Шаг 3: Использовать HTML как ТЗ**
```
1. Открыть: mobile/wireframes/01_main_screen.html
2. Скопировать дизайн в Jetpack Compose
3. Реализовать логику из JavaScript
```

### **Шаг 4: Запуск**
```bash
./gradlew assembleDebug  # Сборка
./gradlew installDebug   # Установка на эмулятор
```

---

## 📐 **ДИЗАЙН-СИСТЕМА**

### **Цвета (Material 3):**
```kotlin
// shared/theme/Colors.kt
object ALADDINColors {
    val PrimaryBlue = Color(0xFF2E5BFF)
    val SecondaryGold = Color(0xFFFCD34D)
    val SuccessGreen = Color(0xFF10B981)
    val DangerRed = Color(0xFFEF4444)
    val WarningOrange = Color(0xFFF59E0B)
    
    val BackgroundDark = Color(0xFF0F172A)
    val SurfaceDark = Color(0xFF1E293B)
    val TextPrimary = Color.White
    val TextSecondary = Color(0xFF94A3B8)
}
```

### **Типография:**
```kotlin
// shared/theme/Typography.kt
val ALADDINTypography = Typography(
    displayLarge = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold),
    displayMedium = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold),
    headlineMedium = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.SemiBold),
    bodyLarge = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Normal),
    bodyMedium = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Normal),
    bodySmall = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Normal)
)
```

---

## 🔗 **API**

**Base URL:** `https://api.aladdin.family/v1/`

**Retrofit interface:**
```kotlin
interface ALADDINApi {
    @GET("family/status")
    suspend fun getFamilyStatus(): Response<FamilyStatus>
    
    @GET("family/members")
    suspend fun getFamilyMembers(): Response<List<FamilyMember>>
    
    @POST("vpn/connect")
    suspend fun connectVPN(@Body request: VPNRequest): Response<VPNStatus>
}
```

---

## ✅ **ЧЕКЛИСТ**

- [ ] Структура проекта создана ✅
- [ ] build.gradle.kts настроен
- [ ] AndroidManifest.xml настроен
- [ ] Hilt DI настроен
- [ ] Navigation настроен
- [ ] Theme (Material 3) создана
- [ ] API client создан
- [ ] Начало разработки экранов

---

**Создано:** 11 октября 2025  
**Автор:** ALADDIN Security Team  
**Статус:** ✅ Готово к разработке



