package family.aladdin.android.ui.components.modals

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.ui.theme.*

/**
 * 🔑 Recovery Options Modal
 * Модальное окно выбора способа восстановления доступа
 * Окно #6 - показывает 4 способа восстановления
 * 
 * РАЗМЕРЫ (проверено):
 * - Modal width: 340dp
 * - Modal height: 520dp (безопасно!)
 * - Each button: 72dp height
 * - Total content: ~500dp
 */

@Composable
fun RecoveryOptionsModal(
    onRecoveryComplete: () -> Unit,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    var showQRScanner by remember { mutableStateOf(false) }
    var showManualInput by remember { mutableStateOf(false) }
    var scannerMode by remember { mutableStateOf(QRScanMode.RECOVERY_QR) }
    
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            dismissOnBackPress = true,
            dismissOnClickOutside = false
        )
    ) {
        Card(
            modifier = Modifier
                .width(340.dp)
                .wrapContentHeight(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.Transparent
            )
        ) {
            Box(
                modifier = Modifier
                    .background(
                        Brush.linearGradient(
                            colors = listOf(
                                Color(0xFF0F172A),  // Космический тёмный
                                Color(0xFF1E3A8A),  // Глубокий синий
                                Color(0xFF3B82F6),  // Электрический синий
                                Color(0xFF1E40AF)   // Королевский синий
                            )
                        )
                    )
                    .padding(24.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(SpacingXL)
                ) {
                    // Header
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "🔑",
                            fontSize = 40.sp
                        )
                        
                        Text(
                            text = "ВОССТАНОВИТЬ ДОСТУП",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFFCD34D)  // Яркое золото!
                        )
                        
                        Text(
                            text = "Как вы хотите восстановить?",
                            fontSize = 14.sp,
                            color = TextSecondary
                        )
                    }
                    
                    // Recovery options (4 кнопки)
                    Column(verticalArrangement = Arrangement.spacedBy(SpacingM)) {
                        // Option 1: Through family member (BEST!)
                        RecoveryOptionButton(
                            icon = "👨‍👩‍👧‍👦",
                            title = "ЧЕРЕЗ ЧЛЕНА СЕМЬИ",
                            subtitle = "(если у кого-то есть доступ)",
                            color = Color(0xFF10B981),  // Зелёный
                            onClick = {
                                scannerMode = QRScanMode.RECOVERY_FROM_FAMILY
                                showQRScanner = true
                            }
                        )
                        
                        // Option 2: Scan saved QR #2
                        RecoveryOptionButton(
                            icon = "📷",
                            title = "СКАНИРОВАТЬ QR #2",
                            subtitle = "(сохранённый код восстановления)",
                            color = Color(0xFF60A5FA),  // Электрический синий из иконки!
                            onClick = {
                                scannerMode = QRScanMode.RECOVERY_QR
                                showQRScanner = true
                            }
                        )
                        
                        // Option 3: Enter code manually
                        RecoveryOptionButton(
                            icon = "🔤",
                            title = "ВВЕСТИ КОД ВРУЧНУЮ",
                            subtitle = "(FAM-A1B2-C3D4-E5F6)",
                            color = Color(0xFFFCD34D),  // Яркое золото из иконки!
                            onClick = {
                                showManualInput = true
                            }
                        )
                        
                        // Option 4: Contact support
                        RecoveryOptionButton(
                            icon = "📧",
                            title = "ОБРАТИТЬСЯ В ПОДДЕРЖКУ",
                            subtitle = "(если всё потеряно)",
                            color = Color(0xFFEF4444),  // Красный
                            onClick = {
                                val intent = Intent(Intent.ACTION_SENDTO).apply {
                                    data = Uri.parse("mailto:support@aladdin.family?subject=Восстановление доступа к семье")
                                }
                                context.startActivity(intent)
                            }
                        )
                    }
                    
                    // Back button
                    Text(
                        text = "НАЗАД",
                        fontSize = 14.sp,
                        color = TextSecondary,
                        modifier = Modifier.clickable(onClick = onDismiss)
                    )
                }
            }
        }
    }
    
    if (showQRScanner) {
        QRScannerModal(
            mode = scannerMode,
            onCodeScanned = { _ ->
                showQRScanner = false
                onRecoveryComplete()
            },
            onDismiss = { showQRScanner = false }
        )
    }
    
    if (showManualInput) {
        ManualCodeInputModal(
            onCodeEntered = { _ ->
                showManualInput = false
                onRecoveryComplete()
            },
            onDismiss = { showManualInput = false }
        )
    }
}

@Composable
fun RecoveryOptionButton(
    icon: String,
    title: String,
    subtitle: String,
    color: Color,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(72.dp)  // Фиксированная высота
            .background(
                color.copy(alpha = 0.15f),
                RoundedCornerShape(12.dp)
            )
            .border(
                width = 1.dp,
                color = color,
                shape = RoundedCornerShape(12.dp)
            )
            .clickable(onClick = onClick)
            .padding(horizontal = SpacingM),
        horizontalArrangement = Arrangement.spacedBy(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Icon
        Text(
            text = icon,
            fontSize = 32.sp
        )
        
        // Text
        Column(
            verticalArrangement = Arrangement.spacedBy(4.dp),
            modifier = Modifier.weight(1f)
        ) {
            Text(
                text = title,
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            
            Text(
                text = subtitle,
                fontSize = 12.sp,
                color = TextSecondary
            )
        }
        
        // Arrow
        Text(
            text = "›",
            fontSize = 24.sp,
            color = TextSecondary
        )
    }
}



