package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 👴 Elderly Interface View Model
 * Логика для интерфейса пожилых
 * Источник: iOS ElderlyInterfaceViewModel.swift
 */

class ElderlyInterfaceViewModel : ViewModel() {
    
    // MARK: - State
    
    private val _elderlyName = MutableStateFlow("Бабушка")
    val elderlyName: StateFlow<String> = _elderlyName
    
    private val _isProtected = MutableStateFlow(true)
    val isProtected: StateFlow<Boolean> = _isProtected
    
    private val _threatsToday = MutableStateFlow(0)
    val threatsToday: StateFlow<Int> = _threatsToday
    
    private val _sosActivated = MutableStateFlow(false)
    val sosActivated: StateFlow<Boolean> = _sosActivated
    
    // MARK: - Public Methods
    
    /**
     * Позвонить родным (быстрый набор)
     */
    fun callFamily() {
        println("Quick dial family members")
        // В production: открыть список контактов для быстрого набора
        // Может быть интеграция с телефонной книгой
    }
    
    /**
     * Проверить безопасность
     */
    fun checkSecurity() {
        println("Show security status for elderly")
        // В production: показать упрощённый статус защиты
        // Крупный текст, простые индикаторы
    }
    
    /**
     * Открыть инструкции
     */
    fun openInstructions() {
        println("Show help and instructions for elderly")
        // В production: пошаговые инструкции с крупным текстом
        // Возможно с голосовым сопровождением
    }
    
    /**
     * Активировать SOS
     */
    fun triggerSOS() {
        _sosActivated.value = true
        println("!!! EMERGENCY SOS ACTIVATED !!!")
        
        // В production:
        // 1. Отправить уведомление родным
        // 2. Отправить геолокацию
        // 3. Возможно позвонить в скорую
        // 4. Записать аудио/видео
        
        // Сброс через 30 секунд если не подтверждено
    }
    
    /**
     * Отменить SOS
     */
    fun cancelSOS() {
        _sosActivated.value = false
        println("SOS cancelled")
    }
    
    /**
     * Обновить статус защиты
     */
    fun updateProtectionStatus(isProtected: Boolean, threatsCount: Int) {
        _isProtected.value = isProtected
        _threatsToday.value = threatsCount
    }
}



