package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 👋 Onboarding View Model
 * Логика для экрана онбординга
 * Источник: iOS OnboardingViewModel.swift
 */

class OnboardingViewModel : ViewModel() {
    
    // MARK: - State
    
    private val _currentPage = MutableStateFlow(0)
    val currentPage: StateFlow<Int> = _currentPage
    
    private val _isCompleted = MutableStateFlow(false)
    val isCompleted: StateFlow<Boolean> = _isCompleted
    
    val totalPages: Int = 4
    
    // MARK: - Public Methods
    
    /**
     * Перейти на следующую страницу
     */
    fun nextPage() {
        if (_currentPage.value < totalPages - 1) {
            _currentPage.value += 1
        } else {
            completeOnboarding()
        }
    }
    
    /**
     * Перейти на предыдущую страницу
     */
    fun previousPage() {
        if (_currentPage.value > 0) {
            _currentPage.value -= 1
        }
    }
    
    /**
     * Пропустить онбординг
     */
    fun skipOnboarding() {
        completeOnboarding()
    }
    
    /**
     * Перейти на конкретную страницу
     */
    fun goToPage(page: Int) {
        if (page in 0 until totalPages) {
            _currentPage.value = page
        }
    }
    
    // MARK: - Private Methods
    
    /**
     * Завершить онбординг
     */
    private fun completeOnboarding() {
        _isCompleted.value = true
        
        // В production: сохранить в SharedPreferences
        // SharedPreferences.edit().putBoolean("hasCompletedOnboarding", true).apply()
        
        println("Onboarding completed, navigating to main screen")
    }
    
    /**
     * Сбросить онбординг (для тестирования)
     */
    fun resetOnboarding() {
        _currentPage.value = 0
        _isCompleted.value = false
    }
}




