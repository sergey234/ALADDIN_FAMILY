package family.aladdin.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.inputs.ALADDINTextField
import family.aladdin.android.ui.components.navigation.ALADDINTopBar
import family.aladdin.android.ui.theme.*

@Composable
fun SupportScreen(navController: NavHostController) {
    var searchQuery by remember { mutableStateOf("") }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.linearGradient(listOf(GradientStart, GradientMiddle, GradientEnd)))
    ) {
        Column {
            ALADDINTopBar(
                title = "ПОДДЕРЖКА",
                subtitle = "Мы всегда рядом",
                onBackClick = { navController.popBackStack() }
            )
            
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .padding(top = Spacing.M),
                verticalArrangement = Arrangement.spacedBy(Spacing.L)
            ) {
                // Поиск
                ALADDINTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = "Поиск по вопросам...",
                    icon = "🔍",
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding)
                )
                
                // Способы связи
                Column(
                    modifier = Modifier.padding(horizontal = Spacing.ScreenPadding),
                    verticalArrangement = Arrangement.spacedBy(Spacing.S)
                ) {
                    Text("СВЯЗАТЬСЯ С НАМИ", style = MaterialTheme.typography.displaySmall, color = TextPrimary)
                    
                    ContactButton("💬", "Чат с поддержкой", "Ответим за 5 минут")
                    ContactButton("📧", "Email", "support@aladdin.family")
                    ContactButton("📱", "Телефон", "+7 (800) 555-35-35")
                }
                
                Spacer(modifier = Modifier.height(Spacing.XXL))
            }
        }
    }
}

@Composable
private fun ContactButton(icon: String, title: String, subtitle: String) {
    Surface(
        onClick = {},
        shape = RoundedCornerShape(CornerRadius.Medium),
        color = BackgroundMedium.copy(alpha = 0.3f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.M),
            horizontalArrangement = Arrangement.spacedBy(Spacing.M)
        ) {
            Text(icon, style = MaterialTheme.typography.displayMedium)
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.bodyMedium, color = TextPrimary)
                Text(subtitle, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
            }
            
            Text("›", style = MaterialTheme.typography.displaySmall, color = TextSecondary)
        }
    }
}



