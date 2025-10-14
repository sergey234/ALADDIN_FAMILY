package family.aladdin.android.ui.components.inputs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import family.aladdin.android.ui.theme.*

/**
 * ✏️ ALADDIN TextField
 * Кастомное поле ввода
 * Источник: iOS ALADDINTextField.swift
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ALADDINTextField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    modifier: Modifier = Modifier,
    icon: String? = null,
    isSecure: Boolean = false,
    errorMessage: String? = null
) {
    var passwordVisible by remember { mutableStateOf(false) }
    
    Column(
        verticalArrangement = Arrangement.spacedBy(Spacing.XS)
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = modifier.fillMaxWidth(),
            placeholder = {
                Text(
                    text = placeholder,
                    color = TextSecondary
                )
            },
            leadingIcon = icon?.let {
                {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            },
            visualTransformation = if (isSecure && !passwordVisible)
                PasswordVisualTransformation()
            else
                VisualTransformation.None,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = TextPrimary,
                unfocusedTextColor = TextPrimary,
                focusedBorderColor = if (errorMessage != null) DangerRed else PrimaryBlue,
                unfocusedBorderColor = if (errorMessage != null) DangerRed else Color.White.copy(alpha = 0.1f),
                cursorColor = PrimaryBlue
            ),
            shape = RoundedCornerShape(CornerRadius.Medium),
            textStyle = MaterialTheme.typography.bodyLarge
        )
        
        // Сообщение об ошибке
        errorMessage?.let {
            Text(
                text = it,
                style = MaterialTheme.typography.bodySmall,
                color = DangerRed
            )
        }
    }
}



