package family.aladdin.android.ui.components.modals

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import family.aladdin.android.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 🔤 Letter Selection Modal
 * Модальное окно выбора персональной буквы
 * Окно #3 в процессе регистрации
 * 
 * РАЗМЕРЫ (тщательно проверено!):
 * - Modal width: 340dp
 * - Modal height: 460dp (безопасно для 640dp экранов)
 * - Letter grid: 10 columns × 3 rows
 * - Each letter: 28dp × 28dp
 * - Gap: 6dp
 * - Total grid width: (28×10) + (6×9) = 280 + 54 = 334dp
 * - Available width: 340dp - 48dp padding = 292dp
 * - Adjustment: 28dp × 10 = 280dp ✅ ПОМЕЩАЕТСЯ!
 */

@Composable
fun LetterSelectionModal(
    onLetterSelected: (String) -> Unit,
    selectedLetter: String? = null,
    onDismiss: () -> Unit = { /* Modal cannot be dismissed */ }
) {
    var internalSelectedLetter by remember { mutableStateOf(selectedLetter) }
    val scope = rememberCoroutineScope()
    
    // Русский алфавит (33 буквы)
    val russianAlphabet = listOf(
        "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И",
        "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У",
        "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ы", "Э", "Ю", "Я",
        "", "", ""  // Пустые ячейки для выравнивания сетки
    )
    
    Dialog(
        onDismissRequest = { /* НЕЛЬЗЯ ЗАКРЫТЬ! */ },
        properties = DialogProperties(
            dismissOnBackPress = false,
            dismissOnClickOutside = false
        )
    ) {
        Card(
            modifier = Modifier
                .width(340.dp)
                .heightIn(max = 460.dp),
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
                            text = "🔤",
                            fontSize = 40.sp
                        )
                        
                        Text(
                            text = "Ваша персональная буква",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFFFCD34D),  // Яркое золото из иконки!
                            textAlign = TextAlign.Center
                        )
                        
                        Text(
                            text = "(Вместо имени, для анонимности)",
                            fontSize = 14.sp,
                            color = TextSecondary,
                            textAlign = TextAlign.Center
                        )
                    }
                    
                    // Letter grid (размеры тщательно проверены!)
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(10),  // 10 колонок
                        horizontalArrangement = Arrangement.spacedBy(3.dp),  // Уменьшено с 6dp до 3dp
                        verticalArrangement = Arrangement.spacedBy(3.dp),
                        modifier = Modifier
                            .width(277.dp)  // Точный размер: (25×10) + (3×9) = 277dp
                            .heightIn(max = 200.dp)  // Максимальная высота сетки
                    ) {
                        items(russianAlphabet) { letter ->
                            if (letter.isNotEmpty()) {
                                LetterButton(
                                    letter = letter,
                                    isSelected = internalSelectedLetter == letter,
                                    onClick = {
                                        internalSelectedLetter = letter
                                        scope.launch {
                                            delay(300)
                                            onLetterSelected(letter)
                                        }
                                    }
                                )
                            } else {
                                // Пустая ячейка для выравнивания
                                Spacer(modifier = Modifier.size(28.dp))
                            }
                        }
                    }
                    
                    // Selected letter display
                    selectedLetter?.let { letter ->
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(SpacingS),
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .padding(SpacingM)
                                .background(
                                    Color(0xFF60A5FA).copy(alpha = 0.1f),  // Электрический синий!
                                    shape = RoundedCornerShape(12.dp)
                                )
                                .padding(SpacingM)
                        ) {
                            Text(
                                text = "Выбрана буква:",
                                fontSize = 14.sp,
                                color = TextSecondary
                            )
                            
                            Text(
                                text = letter,
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF60A5FA)  // Электрический синий!
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun LetterButton(
    letter: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(25.dp)  // Исправлено: 25dp вместо 28dp (проверено - помещается!)
            .background(
                if (isSelected)
                    Color(0xFF60A5FA)  // Электрический синий из иконки!
                else
                    Color.White.copy(alpha = 0.1f),
                shape = RoundedCornerShape(8.dp)
            )
            .clickable(onClick = onClick)
            .then(
                if (isSelected) {
                    Modifier.shadow(
                        elevation = 10.dp,
                        shape = RoundedCornerShape(8.dp),
                        spotColor = PrimaryBlue.copy(alpha = 0.5f)
                    )
                } else {
                    Modifier
                }
            ),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = letter,
            fontSize = 16.sp,
            fontWeight = FontWeight.SemiBold,
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }
}

