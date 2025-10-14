package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
fun FamilyTournamentScreen() {
    val participants = listOf(
        Triple("Маша", 285, "👧"),
        Triple("Петя", 240, "👦"),
        Triple("Катя", 195, "👧")
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
            Text("🏆 СЕМЕЙНЫЙ ТУРНИР", style = MaterialTheme.typography.displayLarge, color = TextPrimary)
            Text("📚 Отличники", style = MaterialTheme.typography.displaySmall, color = PrimaryBlue)
            
            Text("⏰ До завершения: 3 дня", style = MaterialTheme.typography.bodyMedium, color = TextSecondary, modifier = Modifier.padding(Spacing.M).background(BackgroundMedium.copy(alpha = 0.5f), RoundedCornerShape(CornerRadius.Medium)))
            
            // Рейтинг
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(Spacing.S)
            ) {
                participants.forEachIndexed { index, (name, score, avatar) ->
                    ParticipantRow(index + 1, name, score, avatar)
                }
            }
            
            // Семейный квест
            QuestCard()
        }
    }
}

@Composable
private fun ParticipantRow(rank: Int, name: String, score: Int, avatar: String) {
    val medal = if (rank == 1) "🥇" else if (rank == 2) "🥈" else "🥉"
    val prize = if (rank == 1) "+50 🦄" else if (rank == 2) "+30 🦄" else "+20 🦄"
    
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = if (rank == 1) androidx.compose.ui.graphics.Color(0xFFFFD700).copy(alpha = 0.1f) else BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Row(
            modifier = Modifier.padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(medal, style = MaterialTheme.typography.displaySmall)
            Text(avatar, style = MaterialTheme.typography.titleLarge)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(name, style = MaterialTheme.typography.titleMedium, color = TextPrimary)
                Text(prize, style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
            }
            
            Text("$score", style = MaterialTheme.typography.displayMedium, color = PrimaryBlue)
        }
    }
}

@Composable
private fun QuestCard() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(CornerRadius.Large),
        color = BackgroundMedium.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier.padding(Spacing.M),
            verticalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text("👨‍👩‍👧‍👦 СЕМЕЙНЫЙ КВЕСТ", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
            Text("Вместе заработайте 500 🦄 за неделю", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
            
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(20.dp)
                    .background(BackgroundMedium.copy(alpha = 0.5f), RoundedCornerShape(10.dp))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(0.6f)
                        .background(Brush.linearGradient(listOf(SuccessGreen, SuccessGreen.copy(alpha = 0.8f))), RoundedCornerShape(10.dp))
                )
            }
            
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("300 🦄 / 500 🦄", style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                Text("60%", style = MaterialTheme.typography.bodySmall.copy(fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold), color = SuccessGreen)
            }
            
            Text("🎁 Награда: каждому по +50 🦄", style = MaterialTheme.typography.bodySmall, color = SuccessGreen)
        }
    }
}




