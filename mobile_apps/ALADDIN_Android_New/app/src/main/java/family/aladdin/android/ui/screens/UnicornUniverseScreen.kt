package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

@Composable
fun UnicornUniverseScreen() {
    val unicornBalance = 245
    // TODO: Use unicornBalance for rewards system
    val gardenCount = 25
    
    val unicornSpecies = listOf(
        Triple("🦄", "Базовый", "Обычный единорог"),
        Triple("⭐", "Звёздный", "Сияет в ночи"),
        Triple("🌈", "Радужный", "Все цвета"),
        Triple("💎", "Алмазный", "Редкий и ценный")
    )
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column(
            modifier = Modifier
                .verticalScroll(rememberScrollState())
                .padding(Spacing.L),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Spacing.L)
        ) {
            Text("🌳 ЕДИНОРОГ-ВСЕЛЕННАЯ", style = MaterialTheme.typography.displayLarge, color = TextPrimary)
            
            // Сад
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(CornerRadius.Large),
                color = SuccessGreen.copy(alpha = 0.1f)
            ) {
                Column(
                    modifier = Modifier.padding(Spacing.M),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("🌳 МОЙ САД", style = MaterialTheme.typography.displayMedium, color = TextPrimary)
                    Text("$gardenCount единорогов", style = MaterialTheme.typography.displaySmall, color = SuccessGreen)
                    
                    // Сад (упрощённый)
                    Column {
                        (0 until 5).forEach { row ->
                            Row {
                                (0 until 5).forEach { col ->
                                    if (row * 5 + col < gardenCount) {
                                        Text("🦄", style = MaterialTheme.typography.titleLarge)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Коллекция
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(Spacing.M)
            ) {
                Text("📚 КОЛЛЕКЦИЯ", style = MaterialTheme.typography.displayMedium, color = TextPrimary)
                
                Column(verticalArrangement = Arrangement.spacedBy(Spacing.S)) {
                    unicornSpecies.forEach { (icon, name, desc) ->
                        SpeciesCard(icon, name, desc)
                    }
                }
            }
        }
    }
}

@Composable
private fun SpeciesCard(icon: String, name: String, desc: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text(icon, style = MaterialTheme.typography.displayLarge)
            
            Column {
                Text(name, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(desc, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
        }
    }
}



