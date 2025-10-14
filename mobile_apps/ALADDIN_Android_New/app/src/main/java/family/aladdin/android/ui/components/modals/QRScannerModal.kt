package family.aladdin.android.ui.components.modals

import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import family.aladdin.android.ui.components.buttons.SecondaryButton
import family.aladdin.android.ui.theme.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * 📷 QR Scanner Modal
 * Модальное окно для сканирования QR-кодов
 * 
 * РАЗМЕРЫ (проверено):
 * - Modal width: 340dp
 * - Modal height: 520dp
 * - Camera preview: 280dp × 280dp
 * - Scan frame: 180dp × 180dp (центрирован)
 * 
 * Используется для:
 * - Присоединения к семье (QR #1)
 * - Восстановления через члена семьи (QR #1)
 * - Восстановления через сохранённый QR #2
 */

@Composable
fun QRScannerModal(
    mode: QRScanMode,
    onCodeScanned: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var showManualInput by remember { mutableStateOf(false) }
    
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
                            text = mode.icon,
                            fontSize = 40.sp
                        )
                        
                        Text(
                            text = mode.title,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = mode.titleColor,
                            textAlign = TextAlign.Center
                        )
                        
                    if (mode.instructions.isNotEmpty()) {
                        Text(
                            text = mode.instructions,
                            fontSize = 13.sp,
                            color = TextSecondary,
                            textAlign = TextAlign.Center
                        )
                    }
                }
                
                // Info card: What to scan?
                Column(
                    modifier = Modifier
                        .padding(horizontal = SpacingM)
                        .background(
                            Color(0xFFFCD34D).copy(alpha = 0.15f),
                            RoundedCornerShape(8.dp)
                        )
                        .border(1.dp, Color(0xFFFCD34D), RoundedCornerShape(8.dp))
                        .padding(SpacingM),
                    verticalArrangement = Arrangement.spacedBy(SpacingS)
                ) {
                    Text(
                        text = "💡 Что сканировать?",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFFFCD34D)
                    )
                    
                    Column(
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = "QR #1: Для присоединения к семье",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color.White
                        )
                        Text(
                            text = "(Попросите члена семьи: Настройки → Добавить члена)",
                            fontSize = 11.sp,
                            color = TextSecondary
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            text = "QR #2: Для восстановления доступа",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color.White
                        )
                        Text(
                            text = "(Ваш сохранённый код из iCloud/Email/Скриншота)",
                            fontSize = 11.sp,
                            color = TextSecondary
                        )
                    }
                }
                
                // Camera preview with scan frame
                    Box(
                        modifier = Modifier
                            .size(280.dp)
                            .background(Color.Black, RoundedCornerShape(16.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        // Camera preview
                        CameraPreview(onQRCodeDetected = onCodeScanned)
                        
                        // Scan frame overlay
                        Box(
                            modifier = Modifier
                                .size(180.dp)
                                .border(
                                    width = 3.dp,
                                    color = Color(0xFFFCD34D),  // Золотая рамка из иконки!
                                    shape = RoundedCornerShape(12.dp)
                                )
                        )
                    }
                    
                    Text(
                        text = "Наведите на QR-код",
                        fontSize = 14.sp,
                        color = TextSecondary
                    )
                    
                    // Divider
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(modifier = Modifier.weight(1f).height(1.dp).background(TextTertiary))
                        Text("или", fontSize = 12.sp, color = TextSecondary)
                        Box(modifier = Modifier.weight(1f).height(1.dp).background(TextTertiary))
                    }
                    
                    // Manual input button
                    SecondaryButton(
                        text = "🔤 ВВЕСТИ КОД ВРУЧНУЮ",
                        onClick = { showManualInput = true }
                    )
                    
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
    
    if (showManualInput) {
        ManualCodeInputModal(
            onCodeEntered = onCodeScanned,
            onDismiss = { showManualInput = false }
        )
    }
}

// MARK: - QR Scan Mode

enum class QRScanMode(
    val icon: String,
    val title: String,
    val instructions: String,
    val titleColor: Color
) {
    JOIN_FAMILY(
        icon = "📷",
        title = "ПРИСОЕДИНИТЬСЯ К СЕМЬЕ",
        instructions = "Попросите члена семьи показать QR-код:\nНастройки → Семья → \"Добавить члена\"",
        titleColor = Color(0xFFFCD34D)
    ),
    RECOVERY_FROM_FAMILY(
        icon = "👨‍👩‍👧‍👦",
        title = "ВОССТАНОВЛЕНИЕ ЧЕРЕЗ СЕМЬЮ",
        instructions = "Попросите члена семьи:\n1. Открыть ALADDIN\n2. Настройки → Семья\n3. \"Добавить члена семьи\"\n4. Показать вам QR-код",
        titleColor = Color(0xFF10B981)
    ),
    RECOVERY_QR(
        icon = "🔑",
        title = "СКАНИРОВАТЬ КОД ВОССТАНОВЛЕНИЯ",
        instructions = "Отсканируйте сохранённый QR-код\n(скриншот, печать, email)",
        titleColor = Color(0xFF60A5FA)
    )
}

// MARK: - Camera Preview

@Composable
fun CameraPreview(
    onQRCodeDetected: (String) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    
    AndroidView(
        factory = { ctx ->
            val previewView = PreviewView(ctx)
            val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
            
            cameraProviderFuture.addListener({
                val cameraProvider = cameraProviderFuture.get()
                
                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                
                val imageAnalysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()
                    .also {
                        it.setAnalyzer(cameraExecutor, QRCodeAnalyzer { qrCode ->
                            onQRCodeDetected(qrCode)
                        })
                    }
                
                val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                
                try {
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        cameraSelector,
                        preview,
                        imageAnalysis
                    )
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }, ContextCompat.getMainExecutor(ctx))
            
            previewView
        },
        modifier = Modifier.fillMaxSize()
    )
}

// MARK: - QR Code Analyzer

class QRCodeAnalyzer(
    private val onQRCodeDetected: (String) -> Unit
) : ImageAnalysis.Analyzer {
    
    private val scanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build()
    )
    
    @androidx.camera.core.ExperimentalGetImage
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
            
            scanner.process(image)
                .addOnSuccessListener { barcodes ->
                    for (barcode in barcodes) {
                        barcode.rawValue?.let { qrCode ->
                            onQRCodeDetected(qrCode)
                        }
                    }
                }
                .addOnCompleteListener {
                    imageProxy.close()
                }
        } else {
            imageProxy.close()
        }
    }
}

// MARK: - Manual Code Input Modal

@Composable
fun ManualCodeInputModal(
    onCodeEntered: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var codePart1 by remember { mutableStateOf("FAM") }
    var codePart2 by remember { mutableStateOf("") }
    var codePart3 by remember { mutableStateOf("") }
    var codePart4 by remember { mutableStateOf("") }
    
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .width(340.dp)
                .wrapContentHeight(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent)
        ) {
            Box(
                modifier = Modifier
                    .background(
                        Brush.linearGradient(
                            colors = listOf(
                                Color(0xFF0F172A),
                                Color(0xFF1E3A8A),
                                Color(0xFF3B82F6),
                                Color(0xFF1E40AF)
                            )
                        )
                    )
                    .padding(24.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(SpacingXL)
                ) {
                    Text(
                        text = "🔤",
                        fontSize = 40.sp
                    )
                    
                    Text(
                        text = "ВВЕДИТЕ КОД ВОССТАНОВЛЕНИЯ",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFCD34D),  // Яркое золото!
                        textAlign = TextAlign.Center
                    )
                    
                    // Code input segments
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        CodeSegmentField(value = codePart1, onValueChange = {}, enabled = false, width = 50.dp)
                        Text("-", color = TextSecondary)
                        CodeSegmentField(value = codePart2, onValueChange = { codePart2 = it }, width = 60.dp)
                        Text("-", color = TextSecondary)
                        CodeSegmentField(value = codePart3, onValueChange = { codePart3 = it }, width = 60.dp)
                        Text("-", color = TextSecondary)
                        CodeSegmentField(value = codePart4, onValueChange = { codePart4 = it }, width = 60.dp)
                    }
                    
                    // Submit button
                    androidx.compose.material3.Button(
                        onClick = {
                            val fullCode = "$codePart1-$codePart2-$codePart3-$codePart4"
                            onCodeEntered(fullCode)
                        },
                        enabled = codePart2.length >= 4 && codePart3.length >= 4 && codePart4.length >= 4,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("ВОССТАНОВИТЬ")
                    }
                    
                    // Hint
                    Column(
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = "💡 Код можно найти:",
                            fontSize = 12.sp,
                            color = TextSecondary
                        )
                        Text("• В письме на email", fontSize = 12.sp, color = TextTertiary)
                        Text("• В скриншоте", fontSize = 12.sp, color = TextTertiary)
                        Text("• В облачном хранилище", fontSize = 12.sp, color = TextTertiary)
                        Text("• Попросить у других членов семьи", fontSize = 12.sp, color = TextTertiary)
                    }
                    
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
}

@Composable
fun CodeSegmentField(
    value: String,
    onValueChange: (String) -> Unit,
    enabled: Boolean = true,
    width: Dp = 70.dp
) {
    androidx.compose.material3.OutlinedTextField(
        value = value,
        onValueChange = { if (it.length <= 4) onValueChange(it.uppercase()) },
        enabled = enabled,
        singleLine = true,
        textStyle = androidx.compose.ui.text.TextStyle(
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
            color = Color.White,
            textAlign = TextAlign.Center
        ),
        modifier = Modifier
            .width(width)
            .height(56.dp),
        colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(
            focusedBorderColor = Color(0xFF60A5FA),  // Электрический синий!
            unfocusedBorderColor = Color.White.copy(alpha = 0.2f),
            disabledBorderColor = Color.White.copy(alpha = 0.1f),
            focusedContainerColor = Color(0xFF60A5FA).copy(alpha = 0.1f),
            unfocusedContainerColor = Color.White.copy(alpha = 0.05f),
            disabledContainerColor = Color.White.copy(alpha = 0.05f)
        )
    )
}

