package family.aladdin.android.viewmodels

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 💬 Support View Model
 * Логика для экрана поддержки
 * Источник: iOS SupportViewModel.swift
 */

data class FAQItem(
    val id: String,
    val icon: String,
    val question: String,
    val answer: String,
    var isExpanded: Boolean = false
)

class SupportViewModel : ViewModel() {
    
    // MARK: - State
    
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery
    
    private val _faqItems = MutableStateFlow<List<FAQItem>>(emptyList())
    val faqItems: StateFlow<List<FAQItem>> = _faqItems
    
    // MARK: - Init
    
    init {
        loadFAQ()
    }
    
    // MARK: - Public Methods
    
    /**
     * Загрузить FAQ
     */
    fun loadFAQ() {
        _faqItems.value = listOf(
            FAQItem(
                id = "1",
                icon = "🛡️",
                question = "Как работает VPN?",
                answer = "VPN шифрует весь ваш интернет-трафик и скрывает IP адрес."
            ),
            FAQItem(
                id = "2",
                icon = "👶",
                question = "Как настроить родительский контроль?",
                answer = "Перейдите в раздел Семья → выберите ребёнка → настройте ограничения."
            ),
            FAQItem(
                id = "3",
                icon = "💳",
                question = "Как отменить подписку?",
                answer = "Настройки → Управление подпиской → Отменить подписку."
            ),
            FAQItem(
                id = "4",
                icon = "🔐",
                question = "Безопасны ли мои данные?",
                answer = "Да! Мы используем шифрование и не храним личные данные на серверах."
            )
        )
    }
    
    /**
     * Переключить раскрытие FAQ
     */
    fun toggleFAQ(itemId: String) {
        _faqItems.value = _faqItems.value.map {
            if (it.id == itemId) {
                it.copy(isExpanded = !it.isExpanded)
            } else {
                it
            }
        }
    }
    
    /**
     * Обновить поисковый запрос
     */
    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
        // В production: фильтрация FAQ по запросу
    }
    
    /**
     * Открыть чат с поддержкой
     */
    fun openChat() {
        println("Open support chat")
        // В production: открыть экран чата
    }
    
    /**
     * Отправить email
     */
    fun sendEmail() {
        println("Open email client: support@aladdin.family")
        // В production: открыть email клиент
    }
    
    /**
     * Позвонить в поддержку
     */
    fun call() {
        println("Initiate phone call: +7 (800) 555-35-35")
        // В production: инициировать звонок
    }
}




