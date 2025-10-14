package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 👶 Child Interface View Model
 * Логика для детского интерфейса
 * Источник: iOS ChildInterfaceViewModel.swift
 */

class ChildInterfaceViewModel : ViewModel() {
    
    // MARK: - State
    
    private val _childName = MutableStateFlow("Маша")
    val childName: StateFlow<String> = _childName
    
    private val _timeRemaining = MutableStateFlow("45 минут")
    val timeRemaining: StateFlow<String> = _timeRemaining
    
    private val _timeRemainingPercent = MutableStateFlow(0.25f)
    val timeRemainingPercent: StateFlow<Float> = _timeRemainingPercent
    
    private val _selectedActivity = MutableStateFlow<ActivityType?>(null)
    val selectedActivity: StateFlow<ActivityType?> = _selectedActivity
    
    enum class ActivityType {
        GAMES, EDUCATION, CREATIVITY, VIDEOS
    }
    
    // MARK: - Public Methods
    
    /**
     * Открыть игры
     */
    fun openGames() {
        _selectedActivity.value = ActivityType.GAMES
        println("Open games section for child")
        // В production: навигация к разделу игр
    }
    
    /**
     * Открыть обучение
     */
    fun openEducation() {
        _selectedActivity.value = ActivityType.EDUCATION
        println("Open education section for child")
        // В production: образовательные приложения
    }
    
    /**
     * Открыть творчество
     */
    fun openCreativity() {
        _selectedActivity.value = ActivityType.CREATIVITY
        println("Open creativity section for child")
        // В production: приложения для рисования, музыки
    }
    
    /**
     * Открыть видео
     */
    fun openVideos() {
        _selectedActivity.value = ActivityType.VIDEOS
        println("Open videos section for child")
        // В production: безопасные видео для детей
    }
    
    /**
     * Обновить оставшееся время
     */
    fun updateTimeRemaining(minutes: Int) {
        _timeRemaining.value = "$minutes минут"
        _timeRemainingPercent.value = minutes / 180f // 3 часа = 180 минут
    }
}




