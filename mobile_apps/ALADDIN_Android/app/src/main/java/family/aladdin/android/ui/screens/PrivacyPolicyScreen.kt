package family.aladdin.android.ui.screens

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.navigation.NavHostController
import family.aladdin.android.ui.components.navigation.ALADDINTopAppBar
import family.aladdin.android.ui.theme.ScreenPadding
import family.aladdin.android.ui.theme.backgroundGradient

/**
 * 📋 Privacy Policy Screen
 * Политика конфиденциальности
 * ОБЯЗАТЕЛЬНА для App Store/Google Play!
 */

@Composable
fun PrivacyPolicyScreen(navController: NavHostController) {
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            ALADDINTopAppBar(
                title = "Политика конфиденциальности",
                subtitle = "Как мы защищаем ваши данные",
                onBackClick = { navController.popBackStack() }
            )
            
            // WebView
            AndroidView(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(ScreenPadding),
                factory = { context ->
                    WebView(context).apply {
                        webViewClient = WebViewClient()
                        settings.javaScriptEnabled = true
                        loadUrl("https://aladdin.family/privacy")
                    }
                }
            )
        }
    }
}



