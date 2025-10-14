package family.aladdin.android.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import family.aladdin.android.ui.screens.*
import family.aladdin.android.viewmodels.*

/**
 * 🧭 App Nav Graph
 * Навигационный граф приложения
 * Jetpack Compose Navigation
 */

@Composable
fun AppNavGraph(
    navController: NavHostController = rememberNavController()
) {
    var hasCompletedOnboarding by remember { mutableStateOf(false) }
    
    NavHost(
        navController = navController,
        startDestination = if (hasCompletedOnboarding) Screen.Main.route else Screen.Onboarding.route
    ) {
        // Онбординг
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                navController = navController,
                onComplete = {
                    hasCompletedOnboarding = true
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Главный экран
        composable(Screen.Main.route) {
            MainScreen(navController = navController)
        }
        
        // Семья
        composable(Screen.Family.route) {
            FamilyScreen(navController = navController)
        }
        
        // VPN
        composable(Screen.VPN.route) {
            VPNScreen(navController = navController)
        }
        
        // Аналитика
        composable(Screen.Analytics.route) {
            AnalyticsScreen(navController = navController)
        }
        
        // AI Помощник
        composable(Screen.AIAssistant.route) {
            AIAssistantScreen(navController = navController)
        }
        
        // Родительский контроль
        composable(Screen.ParentalControl.route) {
            ParentalControlScreen(navController = navController)
        }
        
        // Детский интерфейс
        composable(Screen.ChildInterface.route) {
            ChildInterfaceScreen(navController = navController)
        }
        
        // Интерфейс для пожилых
        composable(Screen.ElderlyInterface.route) {
            ElderlyInterfaceScreen(navController = navController)
        }
        
        // Настройки
        composable(Screen.Settings.route) {
            SettingsScreen(navController = navController)
        }
        
        // Тарифы
        composable(Screen.Tariffs.route) {
            TariffsScreen(navController = navController)
        }
        
        // Профиль
        composable(Screen.Profile.route) {
            ProfileScreen(navController = navController)
        }
        
        // Уведомления
        composable(Screen.Notifications.route) {
            NotificationsScreen(navController = navController)
        }
        
        // Поддержка
        composable(Screen.Support.route) {
            SupportScreen(navController = navController)
        }
        
        // ═══════════════════════════════════════════════════════════
        // Дополнительные экраны (11 штук)
        // ═══════════════════════════════════════════════════════════
        
        // Вход - TODO: Create LoginScreen
        /*
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToRegistration = {
                    navController.navigate(Screen.Registration.route)
                },
                onNavigateToForgotPassword = {
                    navController.navigate(Screen.ForgotPassword.route)
                }
            )
        }
        */
        
        // Регистрация - TODO: Create RegistrationScreen
        /*
        composable(Screen.Registration.route) {
            RegistrationScreen(
                onRegistrationSuccess = {
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Registration.route) { inclusive = true }
                    }
                },
                onNavigateToLogin = {
                    navController.popBackStack()
                }
            )
        }
        */
        
        // Восстановление пароля - TODO: Create ForgotPasswordScreen
        /*
        composable(Screen.ForgotPassword.route) {
            ForgotPasswordScreen(
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        */
        
        // Политика конфиденциальности
        composable(Screen.PrivacyPolicy.route) {
            PrivacyPolicyScreen(navController = navController)
        }
        
        // Условия использования
        composable(Screen.TermsOfService.route) {
            TermsOfServiceScreen(navController = navController)
        }
        
        // Устройства
        composable(Screen.Devices.route) {
            DevicesScreen(navController = navController)
        }
        
        // Реферальная программа
        composable(Screen.Referral.route) {
            ReferralScreen(navController = navController)
        }
        
        // Детали устройства
        composable(Screen.DeviceDetail.route) { backStackEntry ->
            val deviceId = backStackEntry.arguments?.getString("deviceId") ?: ""
            DeviceDetailScreen(
                navController = navController,
                deviceId = deviceId
            )
        }
        
        // Семейный чат
        composable(Screen.FamilyChat.route) { backStackEntry ->
            val memberId = backStackEntry.arguments?.getString("memberId") ?: ""
            FamilyChatScreen(
                navController = navController,
                memberId = memberId
            )
        }
        
        // VPN Energy Stats
        composable(Screen.VPNEnergyStats.route) {
            VPNEnergyStatsScreen(navController = navController)
        }
        
        // QR Оплата
        composable(Screen.PaymentQR.route) {
            PaymentQRScreen(
                navController = navController,
                tariffTitle = "Семейный",
                tariffPrice = "590 ₽",
                tariffPeriod = "в месяц",
                tariffFeatures = listOf("До 5 устройств", "Полная защита"),
                onBackClick = {
                    navController.popBackStack()
                },
                onPaymentCompleted = {
                    navController.popBackStack()
                }
            )
        }
    }
}

/**
 * 📱 Screen Routes
 * Маршруты для всех 25 экранов
 */
sealed class Screen(val route: String) {
    // Основные экраны (14)
    object Onboarding : Screen("onboarding")
    object Main : Screen("main")
    object Family : Screen("family")
    object VPN : Screen("vpn")
    object Analytics : Screen("analytics")
    object AIAssistant : Screen("ai_assistant")
    object ParentalControl : Screen("parental_control")
    object ChildInterface : Screen("child_interface")
    object ElderlyInterface : Screen("elderly_interface")
    object Settings : Screen("settings")
    object Tariffs : Screen("tariffs")
    object Profile : Screen("profile")
    object Notifications : Screen("notifications")
    object Support : Screen("support")
    
    // Дополнительные экраны (11)
    object Login : Screen("login")
    object Registration : Screen("registration")
    object ForgotPassword : Screen("forgot_password")
    object PrivacyPolicy : Screen("privacy_policy")
    object TermsOfService : Screen("terms_of_service")
    object Devices : Screen("devices")
    object Referral : Screen("referral")
    object DeviceDetail : Screen("device_detail/{deviceId}") {
        fun createRoute(deviceId: String) = "device_detail/$deviceId"
    }
    object FamilyChat : Screen("family_chat/{memberId}") {
        fun createRoute(memberId: String) = "family_chat/$memberId"
    }
    object VPNEnergyStats : Screen("vpn_energy_stats")
    object PaymentQR : Screen("payment_qr")
}

