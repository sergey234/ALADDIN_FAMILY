package family.aladdin.android.ui.components.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 🧭 ALADDIN Top Bar
 * Верхняя панель навигации
 * Источник: iOS ALADDINNavigationBar.swift
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ALADDINTopBar(
    title: String,
    subtitle: String? = null,
    onBackClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    Surface(
        color = Color.Transparent,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(
                                BackgroundDark.copy(alpha = 0.95f),
                                BackgroundDark.copy(alpha = 0.9f)
                            )
                        )
                    )
                    .padding(horizontal = Spacing.M, vertical = Spacing.S)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Левая кнопка
                    if (onBackClick != null) {
                        IconButton(
                            onClick = onBackClick,
                            modifier = Modifier
                                .size(Size.NavButtonSize)
                                .background(
                                    BackgroundMedium.copy(alpha = 0.5f),
                                    CircleShape
                                )
                        ) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Назад",
                                tint = TextPrimary
                            )
                        }
                    } else {
                        Spacer(modifier = Modifier.width(Size.NavButtonSize))
                    }
                    
                    // Заголовок
                    Column(
                        modifier = Modifier.weight(1f),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = title,
                            style = MaterialTheme.typography.displayMedium,
                            color = TextPrimary
                        )
                        subtitle?.let {
                            Text(
                                text = it,
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary
                            )
                        }
                    }
                    
                    // Правые кнопки
                    Row {
                        actions()
                    }
                }
            }
            
            // Разделитель
            Divider(
                thickness = 1.dp,
                color = PrimaryBlue.copy(alpha = 0.3f)
            )
        }
    }
}

@Composable
fun TopBarAction(
    icon: ImageVector,
    onClick: () -> Unit
) {
    IconButton(
        onClick = onClick,
        modifier = Modifier
            .size(Size.NavButtonSize)
            .background(
                BackgroundMedium.copy(alpha = 0.5f),
                CircleShape
            )
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = TextPrimary
        )
    }
}

// Alias для совместимости со старым кодом
@Composable
fun ALADDINTopAppBar(
    title: String,
    subtitle: String? = null,
    onBackClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    ALADDINTopBar(
        title = title,
        subtitle = subtitle,
        onBackClick = onBackClick,
        actions = actions
    )
}



