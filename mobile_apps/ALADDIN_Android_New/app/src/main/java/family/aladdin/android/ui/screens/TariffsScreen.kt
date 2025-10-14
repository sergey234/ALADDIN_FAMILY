package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.buttons.PrimaryButton
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*

enum class TariffType(val title: String, val price: String, val period: String) {
    FREE("БАЗОВЫЙ", "0 ₽", "Бесплатно"),
    PERSONAL("ЛИЧНЫЙ", "290 ₽", "в месяц"),
    FAMILY("СЕМЕЙНЫЙ", "590 ₽", "в месяц"),
    PREMIUM("ПРЕМИУМ", "990 ₽", "в месяц")
}

@Composable
fun TariffsScreen(navController: NavHostController) {
    var selectedTariff by remember { mutableStateOf(TariffType.FAMILY) }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "ТАРИФЫ",
                subtitle = "Выберите подходящий план",
                onBackClick = { navController.popBackStack() }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                TariffCard(TariffType.FREE, selectedTariff) { selectedTariff = it }
                TariffCard(TariffType.PERSONAL, selectedTariff) { selectedTariff = it }
                TariffCard(TariffType.FAMILY, selectedTariff, recommended = true) { selectedTariff = it }
                TariffCard(TariffType.PREMIUM, selectedTariff) { selectedTariff = it }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun TariffCard(
    tariff: TariffType,
    selected: TariffType,
    recommended: Boolean = false,
    onSelect: (TariffType) -> Unit
) {
    val isSelected = tariff == selected
    val color = when (tariff) {
        TariffType.FREE -> TextSecondary
        TariffType.PERSONAL -> PrimaryBlue
        TariffType.FAMILY -> SecondaryGold
        TariffType.PREMIUM -> Color(0xFFA855F7)
    }
    
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.ScreenPadding),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(modifier = Modifier.padding(Spacing.CardPadding)) {
            if (recommended) {
                Text("⭐ РЕКОМЕНДУЕМ", style = MaterialTheme.typography.bodyMedium, color = color)
            }
            
            Text(tariff.title, style = MaterialTheme.typography.displayMedium, color = color)
            
            Row(verticalAlignment = Alignment.Bottom) {
                Text(tariff.price, style = MaterialTheme.typography.displayLarge.copy(fontSize = 36.sp), color = Color.White)
                Spacer(modifier = Modifier.width(Spacing.XS))
                Text(tariff.period, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            
            Spacer(modifier = Modifier.height(Spacing.M))
            
            Button(
                onClick = { onSelect(tariff) },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isSelected) SuccessGreen else color
                )
            ) {
                Text(if (isSelected) "✓ АКТИВЕН" else "ВЫБРАТЬ")
            }
        }
    }
}



