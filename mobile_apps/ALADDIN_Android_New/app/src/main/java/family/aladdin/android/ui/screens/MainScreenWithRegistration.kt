package family.aladdin.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import family.aladdin.android.ui.components.modals.*
import family.aladdin.android.viewmodels.FamilyRegistrationViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 📱 Main Screen with Progressive Registration
 * Обёртка для MainScreen с прогрессивной регистрацией
 * 
 * Показывает модальные окна регистрации поверх MainScreen:
 * - Окно #0: Consent Modal (согласие с Privacy Policy)
 * - Окно #1: Выбор роли (через 0.5 сек после consent)
 * - Окно #2: Выбор возраста (через 1 сек после роли)
 * - Окно #3: Выбор буквы (через 1 сек после возраста)
 * - Окно #4: Семья создана! (через 2 сек после буквы)
 * - Notification: Подсказка (через 5 сек после создания)
 */
@Composable
fun MainScreenWithRegistration(
    navController: NavHostController = rememberNavController()
) {
    val context = LocalContext.current
    val registrationVM: FamilyRegistrationViewModel = viewModel { 
        FamilyRegistrationViewModel(
            apiService = family.aladdin.android.network.SimpleApiService(),
            context = context
        )
    }
    var showTip by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    
    // Собираем StateFlow в State
    val showConsentModal by registrationVM.showConsentModal.collectAsState()
    val showRoleModal by registrationVM.showRoleModal.collectAsState()
    val showAgeGroupModal by registrationVM.showAgeGroupModal.collectAsState()
    val showLetterModal by registrationVM.showLetterModal.collectAsState()
    val showFamilyCreatedModal by registrationVM.showFamilyCreatedModal.collectAsState()
    val showSuccessModal by registrationVM.showSuccessModal.collectAsState()
    val selectedLetter by registrationVM.selectedLetter.collectAsState()
    val familyID by registrationVM.familyID.collectAsState()
    val recoveryCode by registrationVM.recoveryCode.collectAsState()
    val familyMembers by registrationVM.familyMembers.collectAsState()
    // TODO: Use familyMembers for displaying family list
    
    Box(modifier = Modifier.fillMaxSize()) {
        // Main Screen (основной экран)
        MainScreen(navController = navController)
        
        // МОДАЛКА #0: Consent (Согласие с Privacy Policy)
        if (showConsentModal) {
            ConsentModal(
                onDismiss = { /* Модальное окно нельзя закрыть */ },
                onAccept = {
                    registrationVM.acceptConsent()
                },
                onReadMore = {
                    // TODO: Открыть PrivacyPolicyScreen
                    // navController.navigate("privacy_policy")
                }
            )
        }
        
        // МОДАЛКА #1: Выбор роли
        if (showRoleModal) {
            RoleSelectionModal(
                onDismiss = { /* Модальное окно нельзя закрыть на первой регистрации */ },
                onRoleSelected = { role ->
                    registrationVM.onRoleSelected(role)
                }
            )
        }
        
        // МОДАЛКА #2: Выбор возраста
        if (showAgeGroupModal) {
            AgeGroupSelectionModal(
                onDismiss = { /* Модальное окно нельзя закрыть */ },
                onAgeGroupSelected = { ageGroup ->
                    registrationVM.onAgeGroupSelected(ageGroup)
                }
            )
        }
        
        // МОДАЛКА #3: Выбор буквы
        if (showLetterModal) {
            LetterSelectionModal(
                onDismiss = { /* Модальное окно нельзя закрыть */ },
                selectedLetter = selectedLetter,
                onLetterSelected = { letter ->
                    registrationVM.onLetterSelected(letter)
                }
            )
        }
        
        // МОДАЛКА #4: Семья создана!
        if (showFamilyCreatedModal) {
            familyID?.let { familyIDValue ->
                recoveryCode?.let { recoveryCodeValue ->
                    FamilyCreatedModal(
                        onDismiss = { /* Модальное окно нельзя закрыть */ },
                        familyID = familyIDValue,
                        recoveryCode = recoveryCodeValue,
                        onContinue = {
                            registrationVM.dismissFamilyCreatedModal()
                            
                            // Показать подсказку через 5 секунд
                            scope.launch {
                                delay(5000)
                                showTip = true
                                
                                // Auto-dismiss через 10 секунд
                                delay(10000)
                                showTip = false
                            }
                        }
                    )
                }
            }
        }
        
        // МОДАЛКА #5: Успешное присоединение/восстановление
        if (showSuccessModal) {
            androidx.compose.material3.AlertDialog(
                onDismissRequest = { /* Модальное окно нельзя закрыть */ },
                title = { Text("Семья создана!") },
                text = { Text("Добро пожаловать в семью!") },
                confirmButton = {
                    TextButton(onClick = {
                        registrationVM.dismissSuccessModal()
                    }) {
                        Text("Продолжить")
                    }
                }
            )
        }
        
        // TIP NOTIFICATION (Подсказка)
        if (showTip) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .align(Alignment.TopCenter)
                    .padding(top = 60.dp)
            ) {
                TipNotification(
                    message = "Хотите добавить членов семьи?\n→ Настройки → Семья → \"Добавить члена семьи\"",
                    onDismiss = { showTip = false }
                )
            }
        }
    }
    
    // Автоматический старт регистрации при первом запуске
    LaunchedEffect(Unit) {
        registrationVM.startRegistration()
    }
}

/**
 * Tip Notification Component
 * Подсказка для пользователя
 */
@Composable
fun TipNotification(
    message: String,
    onDismiss: () -> Unit
) {
    androidx.compose.material3.Card(
        modifier = Modifier
            .fillMaxWidth(0.9f)
            .padding(16.dp),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(16.dp),
        colors = androidx.compose.material3.CardDefaults.cardColors(
            containerColor = androidx.compose.ui.graphics.Color(0xFF3B82F6)
        ),
        elevation = androidx.compose.material3.CardDefaults.cardElevation(
            defaultElevation = 8.dp
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            androidx.compose.material3.Text(
                text = message,
                color = androidx.compose.ui.graphics.Color.White,
                fontSize = 14.sp,
                modifier = Modifier.weight(1f)
            )
            
            androidx.compose.material3.IconButton(
                onClick = onDismiss
            ) {
                androidx.compose.material3.Text(
                    text = "✕",
                    color = androidx.compose.ui.graphics.Color.White,
                    fontSize = 18.sp
                )
            }
        }
    }
}



