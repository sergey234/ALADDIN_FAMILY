package com.aladdin.mobile

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.aladdin.mobile.databinding.ActivityMainBinding
import com.aladdin.mobile.ui.viewmodel.MainViewModel
import com.aladdin.mobile.utils.StormSkyTheme
import com.aladdin.mobile.utils.SecurityManager

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    private lateinit var securityManager: SecurityManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Инициализация ViewBinding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Инициализация ViewModel
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        // Инициализация SecurityManager
        securityManager = SecurityManager(this)
        
        // Настройка UI
        setupUI()
        
        // Настройка навигации
        setupNavigation()
        
        // Применение темы "Грозовое небо"
        applyStormSkyTheme()
        
        // Инициализация AI помощника
        initializeAIAssistant()
        
        // Проверка безопасности
        checkSecurityStatus()
    }
    
    override fun onResume() {
        super.onResume()
        // Обновление статуса безопасности при возвращении
        updateSecurityStatus()
    }
    
    override fun onPause() {
        super.onPause()
        // Сохранение состояния безопасности
        saveSecurityState()
    }
    
    private fun setupUI() {
        // Настройка основного интерфейса
        binding.apply {
            // Настройка заголовка
            setupHeader()
            
            // Настройка карточек функций
            setupFunctionCards()
            
            // Настройка AI помощника
            setupAIAssistant()
        }
    }
    
    private fun setupHeader() {
        binding.apply {
            logoText.text = "🌩️ ALADDIN"
            logoText.setTextColor(StormSkyTheme.accentColor)
            
            profileButton.setOnClickListener {
                onProfileButtonClicked()
            }
        }
    }
    
    private fun setupFunctionCards() {
        binding.apply {
            // Настройка карточки защиты
            protectionCard.setOnClickListener {
                onProtectionCardClicked()
            }
            
            // Настройка карточки семьи
            familyCard.setOnClickListener {
                onFamilyCardClicked()
            }
            
            // Настройка карточки аналитики
            analyticsCard.setOnClickListener {
                onAnalyticsCardClicked()
            }
            
            // Настройка карточки настроек
            settingsCard.setOnClickListener {
                onSettingsCardClicked()
            }
        }
    }
    
    private fun setupAIAssistant() {
        binding.apply {
            aiTitleText.text = "🤖 AI Помощник"
            aiMessageText.text = "Привет! Я помогу настроить защиту для вашей семьи. Чем могу помочь?"
            
            aiSendButton.setOnClickListener {
                onAISendButtonClicked()
            }
            
            // Настройка ввода текста
            aiInputText.setOnEditorActionListener { _, _, _ ->
                onAISendButtonClicked()
                true
            }
        }
    }
    
    private fun setupNavigation() {
        // Настройка Bottom Navigation
        val navController = findNavController(R.id.nav_host_fragment_activity_main)
        val appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.navigation_home,
                R.id.navigation_protection,
                R.id.navigation_family,
                R.id.navigation_analytics,
                R.id.navigation_ai
            )
        )
        
        setupActionBarWithNavController(navController, appBarConfiguration)
        binding.navView.setupWithNavController(navController)
    }
    
    private fun applyStormSkyTheme() {
        // Применение цветовой схемы "Грозовое небо с золотыми акцентами"
        StormSkyTheme.applyToActivity(this)
        
        // Настройка статус бара
        window.statusBarColor = StormSkyTheme.primaryBackground
        window.navigationBarColor = StormSkyTheme.primaryBackground
        
        // Настройка ActionBar
        supportActionBar?.setBackgroundDrawable(
            StormSkyTheme.createGradientDrawable(StormSkyTheme.primaryBackground)
        )
    }
    
    private fun initializeAIAssistant() {
        // Инициализация AI помощника
        viewModel.initializeAIAssistant()
        
        // Наблюдение за состоянием AI
        viewModel.aiStatus.observe(this) { status ->
            updateAIStatus(status)
        }
    }
    
    private fun checkSecurityStatus() {
        // Проверка статуса безопасности
        securityManager.checkSecurityStatus { isSecure ->
            runOnUiThread {
                updateSecurityIndicator(isSecure)
            }
        }
    }
    
    private fun updateSecurityStatus() {
        // Обновление статуса безопасности
        viewModel.updateSecurityStatus()
        
        // Наблюдение за изменениями статуса
        viewModel.securityStatus.observe(this) { status ->
            updateSecurityIndicator(status.isSecure)
        }
    }
    
    private fun saveSecurityState() {
        // Сохранение состояния безопасности
        securityManager.saveSecurityState()
    }
    
    // MARK: - Event Handlers
    
    private fun onProfileButtonClicked() {
        // Переход к профилю пользователя
        Toast.makeText(this, "👤 Профиль пользователя", Toast.LENGTH_SHORT).show()
        // TODO: Implement profile navigation
    }
    
    private fun onProtectionCardClicked() {
        // Переход к экрану защиты
        Toast.makeText(this, "🛡️ Экран защиты", Toast.LENGTH_SHORT).show()
        // TODO: Implement protection screen navigation
    }
    
    private fun onFamilyCardClicked() {
        // Переход к экрану семьи
        Toast.makeText(this, "👨‍👩‍👧‍👦 Экран семьи", Toast.LENGTH_SHORT).show()
        // TODO: Implement family screen navigation
    }
    
    private fun onAnalyticsCardClicked() {
        // Переход к экрану аналитики
        Toast.makeText(this, "📊 Экран аналитики", Toast.LENGTH_SHORT).show()
        // TODO: Implement analytics screen navigation
    }
    
    private fun onSettingsCardClicked() {
        // Переход к экрану настроек
        Toast.makeText(this, "⚙️ Экран настроек", Toast.LENGTH_SHORT).show()
        // TODO: Implement settings screen navigation
    }
    
    private fun onAISendButtonClicked() {
        val message = binding.aiInputText.text.toString().trim()
        if (message.isNotEmpty()) {
            sendMessageToAI(message)
            binding.aiInputText.text?.clear()
        }
    }
    
    // MARK: - AI Assistant
    
    private fun sendMessageToAI(message: String) {
        // Отправка сообщения AI помощнику
        showAILoadingIndicator()
        
        viewModel.sendMessageToAI(message) { response, error ->
            runOnUiThread {
                hideAILoadingIndicator()
                if (error != null) {
                    showAIError(error)
                } else {
                    updateAIMessage(response ?: "Ошибка получения ответа")
                }
            }
        }
    }
    
    private fun showAILoadingIndicator() {
        binding.aiMessageText.text = "🤖 AI помощник печатает..."
        binding.aiSendButton.isEnabled = false
    }
    
    private fun hideAILoadingIndicator() {
        binding.aiSendButton.isEnabled = true
    }
    
    private fun updateAIMessage(message: String) {
        binding.aiMessageText.text = message
    }
    
    private fun showAIError(error: Throwable) {
        binding.aiMessageText.text = "❌ Ошибка: ${error.message}"
    }
    
    private fun updateAIStatus(status: String) {
        // Обновление статуса AI помощника
        binding.aiStatusText.text = status
    }
    
    // MARK: - Security
    
    private fun updateSecurityIndicator(isSecure: Boolean) {
        // Обновление индикатора безопасности
        binding.securityIndicator.visibility = if (isSecure) View.VISIBLE else View.GONE
        binding.securityStatusText.text = if (isSecure) "🛡️ Защита активна" else "⚠️ Проверьте настройки"
    }
}

