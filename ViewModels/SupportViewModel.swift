import SwiftUI

// Master Logger for support logging
private let logger = MasterLogger.shared

/// 💬 Support View Model
/// Логика для экрана поддержки
class SupportViewModel: ObservableObject {
    
    @Published var searchQuery: String = ""
    @Published var faqItems: [FAQItem] = []
    
    struct FAQItem: Identifiable {
        let id = UUID()
        let icon: String
        let question: String
        let answer: String
        var isExpanded: Bool = false
    }
    
    init() {
        loadFAQ()
    }
    
    func loadFAQ() {
        faqItems = [
            FAQItem(icon: "🛡️", question: "Как работает защита сети?", answer: "Защита сети шифрует весь ваш интернет-трафик и скрывает IP адрес."),
            FAQItem(icon: "👶", question: "Как настроить родительский контроль?", answer: "Перейдите в раздел Семья → выберите ребёнка → настройте ограничения."),
            FAQItem(icon: "💳", question: "Как отменить подписку?", answer: "Настройки → Управление подпиской → Отменить подписку."),
            FAQItem(icon: "🔐", question: "Безопасны ли мои данные?", answer: "Да! Мы используем шифрование и не храним личные данные на серверах.")
        ]
    }
    
    func toggleFAQ(_ item: FAQItem) {
        logger.business("User toggled FAQ: \(item.question)")
        if let index = faqItems.firstIndex(where: { $0.id == item.id }) {
            faqItems[index].isExpanded.toggle()
        }
    }
    
    func openChat() {
        logger.business("User opened support chat")
        print("Open support chat")
    }
    
    func sendEmail() {
        logger.business("User initiated support email")
        print("Open email client")
    }
    
    func call() {
        logger.business("User initiated support call")
        print("Initiate phone call")
    }
}



