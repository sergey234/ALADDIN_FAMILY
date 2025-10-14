package family.aladdin.android.ui.components.modals

import android.graphics.Bitmap
import android.graphics.Color as AndroidColor
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
// import com.google.zxing.BarcodeFormat
// import com.google.zxing.qrcode.QRCodeWriter
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.theme.*

/**
 * ✅ Family Created Modal
 * Модальное окно "Семья создана!" с QR-кодом
 * Окно #4 в процессе регистрации
 * 
 * РАЗМЕРЫ (тщательно проверено!):
 * - Modal width: 340dp
 * - Modal height: 600dp (с прокруткой если нужно!)
 * - QR code: 180dp × 180dp
 * - Padding: 24dp (сверху/снизу/слева/справа)
 * - Content height: ~580dp
 * - Scrollable: да (на всякий случай)
 * 
 * Безопасно для экранов от 640dp высотой ✅
 */

@Composable
fun FamilyCreatedModal(
    familyID: String,
    recoveryCode: String,
    onContinue: () -> Unit,
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ }
) {
    var selectedSaveMethods by remember { mutableStateOf(setOf<SaveMethod>()) }
    var showEmailInput by remember { mutableStateOf(false) }
    var email by remember { mutableStateOf("") }
    // TODO: Use email for sending family details
    
    Dialog(
        onDismissRequest = { /* НЕЛЬЗЯ ЗАКРЫТЬ БЕЗ СОХРАНЕНИЯ! */ },
        properties = DialogProperties(
            dismissOnBackPress = false,
            dismissOnClickOutside = false
        )
    ) {
        Card(
            modifier = Modifier
                .width(340.dp)
                .heightIn(max = 600.dp),
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
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(SpacingL)
                ) {
                    // Header
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "✅",
                            fontSize = 60.sp
                        )
                        
                        Text(
                            text = "СЕМЬЯ СОЗДАНА!",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = SuccessGreen
                        )
                    }
                    
                    // Recovery code section
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "🔑 Ваш код восстановления:",
                            fontSize = 14.sp,
                            color = TextSecondary
                        )
                        
                        // QR Code placeholder (180×180dp - безопасный размер)
                        Box(
                            modifier = Modifier
                                .size(180.dp)
                                .background(Color.White, RoundedCornerShape(12.dp))
                                .padding(12.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "QR\nCODE\nPLACEHOLDER",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.Black,
                                textAlign = TextAlign.Center
                            )
                        }
                        
                        // Recovery code text
                        Text(
                            text = recoveryCode,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace,
                            color = Color(0xFFFCD34D),  // Яркое золото из иконки!
                            letterSpacing = 2.sp,
                            textAlign = TextAlign.Center,
                            modifier = Modifier
                                .padding(SpacingM)
                                .background(
                                    Color.Black.copy(alpha = 0.3f),
                                    RoundedCornerShape(8.dp)
                                )
                                .padding(SpacingM)
                        )
                    }
                    
                    // Warning box
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                WarningOrange.copy(alpha = 0.15f),
                                RoundedCornerShape(12.dp)
                            )
                            .border(
                                width = 3.dp,
                                color = WarningOrange,
                                shape = RoundedCornerShape(12.dp)
                            )
                            .padding(SpacingM),
                        horizontalArrangement = Arrangement.spacedBy(SpacingM),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "⚠️",
                            fontSize = 24.sp
                        )
                        
                        Text(
                            text = "ВАЖНО: Сохраните этот код!",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = WarningOrange
                        )
                    }
                    
                    // Save methods
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(SpacingM)
                    ) {
                        Text(
                            text = "СПОСОБЫ СОХРАНЕНИЯ:",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        
                        SaveMethod.values().forEach { method ->
                            SaveMethodCheckbox(
                                method = method,
                                isSelected = selectedSaveMethods.contains(method),
                                onClick = {
                                    selectedSaveMethods = if (selectedSaveMethods.contains(method)) {
                                        selectedSaveMethods - method
                                    } else {
                                        selectedSaveMethods + method
                                    }
                                    
                                    if (method == SaveMethod.EMAIL) {
                                        showEmailInput = selectedSaveMethods.contains(method)
                                    }
                                }
                            )
                        }
                    }
                    
                    // Continue button
                    PrimaryButton(
                        text = "СОХРАНИЛ, ПРОДОЛЖИТЬ ✅",
                        onClick = {
                            if (selectedSaveMethods.isNotEmpty()) {
                                onContinue()
                            }
                        },
                        enabled = selectedSaveMethods.isNotEmpty()
                    )
                    
                    if (selectedSaveMethods.isEmpty()) {
                        Text(
                            text = "⚠️ Выберите хотя бы 1 способ сохранения",
                            fontSize = 12.sp,
                            color = DangerRed,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
        }
    }
}

enum class SaveMethod(val label: String) {
    CLIPBOARD("📋 Скопировать в буфер"),
    SCREENSHOT("📸 Сделать скриншот"),
    CLOUD("💾 Сохранить в облако"),
    EMAIL("📧 Отправить на email")
}

@Composable
fun SaveMethodCheckbox(
    method: SaveMethod,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (isSelected)
                    SuccessGreen.copy(alpha = 0.15f)
                else
                    Color.White.copy(alpha = 0.05f),
                RoundedCornerShape(8.dp)
            )
            .border(
                width = if (isSelected) 1.dp else 0.dp,
                color = if (isSelected) SuccessGreen else Color.Transparent,
                shape = RoundedCornerShape(8.dp)
            )
            .clickable(onClick = onClick)
            .padding(SpacingM),
        horizontalArrangement = Arrangement.spacedBy(SpacingM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = isSelected,
            onCheckedChange = { onClick() },
            colors = CheckboxDefaults.colors(
                checkedColor = SuccessGreen,
                uncheckedColor = TextSecondary
            )
        )
        
        Text(
            text = method.label,
            fontSize = 14.sp,
            color = TextPrimary
        )
    }
}

// QR Code generation removed - using placeholder instead

