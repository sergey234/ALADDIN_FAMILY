/**
 * Navigation History Manager
 * Отслеживает откуда пришёл пользователь для правильной навигации "Назад"
 */

class NavigationHistory {
    constructor() {
        this.history = this.loadHistory();
        this.init();
    }
    
    init() {
        // Сохраняем текущую страницу при загрузке
        window.addEventListener('DOMContentLoaded', () => {
            this.addToHistory(window.location.pathname);
        });
        
        // Переопределяем навигацию
        this.setupBackButtons();
    }
    
    loadHistory() {
        try {
            return JSON.parse(sessionStorage.getItem('nav_history') || '[]');
        } catch {
            return [];
        }
    }
    
    saveHistory() {
        try {
            sessionStorage.setItem('nav_history', JSON.stringify(this.history));
        } catch (e) {
            console.warn('Не удалось сохранить историю навигации:', e);
        }
    }
    
    addToHistory(page) {
        // Добавляем страницу в историю
        this.history.push({
            page,
            timestamp: Date.now()
        });
        
        // Ограничиваем размер истории
        if (this.history.length > 20) {
            this.history.shift();
        }
        
        this.saveHistory();
    }
    
    getPreviousPage() {
        // Получаем предыдущую страницу (не текущую)
        if (this.history.length < 2) {
            return '01_main_screen.html'; // По умолчанию на главную
        }
        
        // Предпоследняя страница
        return this.history[this.history.length - 2].page;
    }
    
    goBack() {
        const previousPage = this.getPreviousPage();
        
        // Удаляем текущую страницу из истории
        this.history.pop();
        this.saveHistory();
        
        // Переходим
        window.location.href = previousPage;
    }
    
    setupBackButtons() {
        // Находим все кнопки "Назад"
        document.addEventListener('DOMContentLoaded', () => {
            const backButtons = document.querySelectorAll('.back-btn, [data-back-btn]');
            
            backButtons.forEach(btn => {
                // Если у кнопки уже есть onclick - пропускаем
                if (btn.getAttribute('onclick')) {
                    return;
                }
                
                // Добавляем умную навигацию
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.goBack();
                });
            });
        });
    }
    
    navigateTo(page) {
        this.addToHistory(page);
        window.location.href = page;
    }
}

// Глобальная инициализация
const navHistory = new NavigationHistory();

// Экспортируем для использования
window.NavigationHistory = NavigationHistory;
window.navHistory = navHistory;

console.log('🗺️ Navigation History Manager загружен');


