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
 * 📜 Terms of Service Screen
 * Условия использования
 * ОБЯЗАТЕЛЬНЫ для App Store/Google Play!
 */

@Composable
fun TermsOfServiceScreen(navController: NavHostController) {
    
    Box(modifier = Modifier.fillMaxSize().backgroundGradient()) {
        Column(modifier = Modifier.fillMaxSize()) {
            
            ALADDINTopAppBar(
                title = "Условия использования",
                subtitle = "Правила пользования сервисом",
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
                        loadUrl("https://aladdin.family/terms")
                    }
                }
            )
        }
    }
}



