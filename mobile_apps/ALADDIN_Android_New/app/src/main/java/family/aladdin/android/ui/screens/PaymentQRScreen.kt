package family.aladdin.android.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*
import family.aladdin.android.viewmodels.PaymentQRViewModel

/**
 * 💳 Payment QR Screen
 * Экран оплаты через QR-код (СБП, SberPay, Universal)
 * Для российских пользователей вместо IAP
 */

enum class PaymentMethodType {
    SBP, SBERPAY, UNIVERSAL;
    
    val icon: String
        get() = when (this) {
            SBP -> "💳"
            SBERPAY -> "🏦"
            UNIVERSAL -> "📱"
        }
    
    val shortTitle: String
        get() = when (this) {
            SBP -> "СБП"
            SBERPAY -> "СберPay"
            UNIVERSAL -> "Универсальный"
        }
    
    val fullTitle: String
        get() = when (this) {
            SBP -> "Система Быстрых Платежей"
            SBERPAY -> "SberPay QR-код"
            UNIVERSAL -> "Универсальный QR-код"
        }
    
    val instructions: String
        get() = when (this) {
            SBP -> """
                Отсканируйте в приложении любого банка:
                • Сбербанк Онлайн
                • ВТБ Онлайн
                • Тинькофф
                • Альфа-Мобайл
                • Райффайзен Онлайн
                • Газпромбанк
                • Россельхозбанк
                • ВТБ24
                • ЮниКредит
                • Русский Стандарт
                • МКБ Онлайн
                • Открытие
                и другие
            """.trimIndent()
            SBERPAY -> "Отсканируйте в приложении\nСберБанк Онлайн"
            UNIVERSAL -> """
                Универсальный способ для всех банков.
                Откройте приложение вашего банка,
                найдите раздел переводов и используйте
                данные из QR-кода.
            """.trimIndent()
        }
}

@Composable
fun PaymentQRScreen(
    navController: androidx.navigation.NavHostController,
    tariffTitle: String,
    tariffPrice: String,
    tariffPeriod: String,
    tariffFeatures: List<String>, // TODO: Use tariffFeatures for display
    onBackClick: () -> Unit,
    onPaymentCompleted: () -> Unit,
    viewModel: PaymentQRViewModel = viewModel()
) {
    var selectedMethod by remember { mutableStateOf(PaymentMethodType.SBP) }
    
    // Create payment on first launch
    LaunchedEffect(Unit) {
        viewModel.createPayment(tariffTitle, tariffPrice)
    }
    
    // Show success dialog
    if (viewModel.showSuccessDialog) {
        AlertDialog(
            onDismissRequest = { },
            title = { Text("Оплата успешна!") },
            text = { Text("Подписка $tariffTitle активирована!\n\nСпасибо за покупку!") },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.showSuccessDialog = false
                    onPaymentCompleted()
                    onBackClick()
                }) {
                    Text("Отлично!")
                }
            }
        )
    }
    
    // Show error dialog
    if (viewModel.showErrorDialog && viewModel.errorMessage != null) {
        AlertDialog(
            onDismissRequest = { viewModel.showErrorDialog = false },
            title = { Text("Ошибка") },
            text = { Text(viewModel.errorMessage ?: "") },
            confirmButton = {
                TextButton(onClick = { viewModel.showErrorDialog = false }) {
                    Text("OK")
                }
            }
        )
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "ОПЛАТА ПОДПИСКИ",
                subtitle = tariffTitle,
                onBackClick = { navController.popBackStack() }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = ScreenPadding),
                verticalArrangement = Arrangement.spacedBy(SpacingL)
            ) {
                Spacer(modifier = Modifier.height(SpacingM))
                
                // Timer
                viewModel.expiresAt?.let { expiresAt ->
                    TimerCard(expiresAt = expiresAt)
                }
                
                // QR Tabs
                QRTabsCard(
                    selectedMethod = selectedMethod,
                    onMethodSelected = { selectedMethod = it },
                    qrImageSBP = viewModel.qrCodeImageSBP,
                    qrImageSberPay = viewModel.qrCodeImageSberPay,
                    qrImageUniversal = viewModel.qrCodeImageUniversal
                )
                
                // Instructions
                InstructionsCard()
                
                // Check Payment Button
                PrimaryButton(
                    text = "Проверить оплату",
                    onClick = { viewModel.checkPaymentStatus() },
                    enabled = !viewModel.isLoading
                )
                
                // Payment Info
                PaymentInfoCard(
                    tariffTitle = tariffTitle,
                    tariffPrice = tariffPrice,
                    tariffPeriod = tariffPeriod,
                    merchantInfo = viewModel.merchantInfo
                )
                
                Spacer(modifier = Modifier.height(SpacingXXL))
            }
        }
        
        // Loading Overlay
        if (viewModel.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.5f)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = SecondaryGold)
            }
        }
    }
}

@Composable
private fun TimerCard(expiresAt: Long) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadiusLarge),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(SpacingM),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(SpacingXS)
        ) {
            Text("⏰", style = MaterialTheme.typography.displayMedium)
            
            val timeRemaining = remember(expiresAt) {
                val now = System.currentTimeMillis()
                val remaining = (expiresAt - now) / 1000
                if (remaining <= 0) {
                    "Истек срок"
                } else {
                    val hours = remaining / 3600
                    val minutes = (remaining % 3600) / 60
                    String.format("%02d:%02d", hours, minutes)
                }
            }
            
            Text(
                text = timeRemaining,
                style = MaterialTheme.typography.headlineMedium,
                color = SecondaryGold
            )
            
            Text(
                text = "до окончания срока оплаты",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }
    }
}

@Composable
private fun QRTabsCard(
    selectedMethod: PaymentMethodType,
    onMethodSelected: (PaymentMethodType) -> Unit,
    qrImageSBP: String?,
    qrImageSberPay: String?,
    qrImageUniversal: String?
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadiusLarge),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(CardPadding),
            verticalArrangement = Arrangement.spacedBy(SpacingM)
        ) {
            // Tab Selector
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(SpacingS)
            ) {
                PaymentMethodType.values().forEach { method ->
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onMethodSelected(method) }
                            .background(
                                if (selectedMethod == method) PrimaryBlue.copy(alpha = 0.3f) else Color.Transparent,
                                RoundedCornerShape(CornerRadiusMedium)
                            )
                            .padding(vertical = SpacingS),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingXXS)
                    ) {
                        Text(method.icon, style = MaterialTheme.typography.headlineMedium)
                        Text(
                            text = method.shortTitle,
                            style = MaterialTheme.typography.labelMedium,
                            color = if (selectedMethod == method) SecondaryGold else TextSecondary
                        )
                    }
                }
            }
            
            // QR Code Display
            val currentQRImage = when (selectedMethod) {
                PaymentMethodType.SBP -> qrImageSBP
                PaymentMethodType.SBERPAY -> qrImageSberPay
                PaymentMethodType.UNIVERSAL -> qrImageUniversal
            }
            
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(SpacingM)
            ) {
                Text(
                    text = selectedMethod.fullTitle,
                    style = MaterialTheme.typography.headlineSmall,
                    color = TextPrimary
                )
                
                // QR Code Image
                Box(
                    modifier = Modifier
                        .size(280.dp)
                        .background(Color.White, RoundedCornerShape(CornerRadiusLarge)),
                    contentAlignment = Alignment.Center
                ) {
                    if (currentQRImage != null) {
                        // TODO: Decode base64 and display image
                        Text("QR-код", color = Color.Black)
                    } else {
                        CircularProgressIndicator()
                    }
                }
                
                Text(
                    text = selectedMethod.instructions,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun InstructionsCard() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadiusLarge),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(CardPadding),
            verticalArrangement = Arrangement.spacedBy(SpacingM)
        ) {
            Text(
                text = "КАК ОПЛАТИТЬ",
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary
            )
            
            listOf(
                "Откройте приложение вашего банка",
                "Найдите раздел \"Оплата по QR\"",
                "Отсканируйте QR-код выше",
                "Подтвердите оплату",
                "Дождитесь активации подписки"
            ).forEachIndexed { index, text ->
                InstructionStep(number = index + 1, text = text)
            }
        }
    }
}

@Composable
private fun InstructionStep(number: Int, text: String) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Surface(
            modifier = Modifier.size(32.dp),
            shape = RoundedCornerShape(CornerRadiusSmall),
            color = SurfaceDark
        ) {
            Box(contentAlignment = Alignment.Center) {
                Text(
                    text = number.toString(),
                    style = MaterialTheme.typography.headlineSmall,
                    color = SecondaryGold
                )
            }
        }
        
        Text(
            text = text,
            style = MaterialTheme.typography.bodyLarge,
            color = TextPrimary
        )
    }
}

@Composable
private fun PaymentInfoCard(
    tariffTitle: String,
    tariffPrice: String,
    tariffPeriod: String,
    merchantInfo: family.aladdin.android.models.MerchantInfo?
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadiusLarge),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(CardPadding),
            verticalArrangement = Arrangement.spacedBy(SpacingM)
        ) {
            Text(
                text = "ИНФОРМАЦИЯ О ПЛАТЕЖЕ",
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary
            )
            
            Column(verticalArrangement = Arrangement.spacedBy(SpacingS)) {
                InfoRow(label = "Тариф", value = tariffTitle)
                InfoRow(label = "Сумма", value = tariffPrice)
                InfoRow(label = "Период", value = tariffPeriod)
                
                merchantInfo?.let { info ->
                    Divider(color = TextTertiary, thickness = 1.dp)
                    InfoRow(label = "Получатель", value = info.name)
                    InfoRow(label = "Карта", value = info.card)
                    InfoRow(label = "Телефон СБП", value = info.phone)
                }
            }
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyLarge,
            color = TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = TextPrimary
        )
    }
}



