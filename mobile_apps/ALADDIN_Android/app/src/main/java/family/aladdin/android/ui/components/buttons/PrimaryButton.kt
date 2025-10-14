package family.aladdin.android.ui.components.buttons

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import family.aladdin.android.ui.theme.*

/**
 * 🔘 Primary Button
 * Основная кнопка ALADDIN (синяя с градиентом)
 * Источник: iOS PrimaryButton.swift
 */

@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(Size.ButtonHeight)
            .background(
                brush = Brush.horizontalGradient(
                    colors = if (enabled) {
                        listOf(PrimaryBlue, SecondaryBlue)
                    } else {
                        listOf(BackgroundMedium, BackgroundMedium)
                    }
                ),
                shape = RoundedCornerShape(CornerRadius.Large)
            ),
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent,
            contentColor = Color.White,
            disabledContainerColor = Color.Transparent,
            disabledContentColor = TextSecondary
        ),
        shape = RoundedCornerShape(CornerRadius.Large),
        contentPadding = PaddingValues(Spacing.M)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelLarge,
            color = if (enabled) Color.White else TextSecondary
        )
    }
}



