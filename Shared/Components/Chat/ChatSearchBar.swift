import SwiftUI

/**
 * 🔍 Chat Search Bar
 * Поисковая строка для чата
 */

struct ChatSearchBar: View {
    @Binding var searchText: String
    @Binding var isSearching: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onClear: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.s) {
            // Иконка поиска
            Image(systemName: "magnifyingglass")
                .foregroundColor(.textSecondary)
            
            // Поле поиска
            TextField(
                localizationManager.localized("family_chat_search_placeholder"),
                text: $searchText
            )
            .textFieldStyle(PlainTextFieldStyle())
            .foregroundColor(.textPrimary)
            
            // Кнопка очистки
            if !searchText.isEmpty {
                Button(action: {
                    searchText = ""
                    onClear()
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.textSecondary)
                }
            }
            
            // Кнопка закрытия поиска
            Button(action: {
                isSearching = false
                searchText = ""
                onClear()
            }) {
                Text(localizationManager.localized("family_chat_search_clear"))
                    .font(.body)
                    .foregroundColor(.secondaryGold)
            }
        }
        .padding(Spacing.m)
        .background(Color.surfaceDark.opacity(0.5))
        .cornerRadius(CornerRadius.medium)
    }
}
