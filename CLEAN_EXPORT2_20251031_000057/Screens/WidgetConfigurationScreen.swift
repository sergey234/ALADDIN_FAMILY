import SwiftUI

/**
 * ⚙️ Widget Configuration Screen
 * Экран настройки виджетов
 * Показывает доступные виджеты и инструкции по добавлению
 */

struct WidgetConfigurationScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @State private var showingInstructions = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана настройки виджетов")
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: "Widget Settings",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Навигационная панель настроек виджетов")
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        
                        // Header
                        VStack(spacing: Spacing.s) {
                            Image(systemName: "square.grid.2x2")
                                .font(.system(size: 48))
                                .foregroundColor(.blue)
                                .accessibilityLabel("Иконка виджетов")
                            
                            Text("Widget Configuration")
                                .font(.title2)
                                .fontWeight(.bold)
                                .accessibilityAddTraits(.isHeader)
                                .accessibilityLabel("Настройка виджетов")
                            
                            Text("Configure your home screen widgets")
                                .font(.body)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                                .accessibilityLabel("Настройте виджеты для главного экрана")
                        }
                        .padding(.top, Spacing.l)
                        .accessibilityElement(children: .contain)
                        .accessibilityLabel("Заголовок настроек виджетов")
                        
                        // Instructions Card
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text("How to Add Widgets")
                                .font(.headline)
                                .fontWeight(.semibold)
                                .accessibilityAddTraits(.isHeader)
                                .accessibilityLabel("Как добавить виджеты")
                            
                            VStack(alignment: .leading, spacing: Spacing.s) {
                                InstructionStep(
                                    number: "1",
                                    text: "Long press on your home screen"
                                )
                                
                                InstructionStep(
                                    number: "2", 
                                    text: "Tap the '+' button in the top corner"
                                )
                                
                                InstructionStep(
                                    number: "3",
                                    text: "Search for 'ALADDIN' and select a widget"
                                )
                                
                                InstructionStep(
                                    number: "4",
                                    text: "Choose size and position, then tap 'Add Widget'"
                                )
                            }
                            .accessibilityElement(children: .contain)
                            .accessibilityLabel("Пошаговые инструкции по добавлению виджетов")
                        }
                        .padding(Spacing.m)
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(CornerRadius.medium)
                        .cardShadow()
                        .padding(.horizontal, Spacing.screenPadding)
                        .accessibilityElement(children: .contain)
                        .accessibilityLabel("Карточка с инструкциями по добавлению виджетов")
                        
                        // Available Widgets
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text("Available Widgets")
                                .font(.headline)
                                .fontWeight(.semibold)
                                .accessibilityAddTraits(.isHeader)
                                .accessibilityLabel("Доступные виджеты")
                            
                            LazyVGrid(columns: [
                                GridItem(.flexible()),
                                GridItem(.flexible())
                            ], spacing: Spacing.m) {
                                
                                WidgetCard(
                                    title: "Family Status",
                                    description: "See family members online",
                                    icon: "person.3.fill",
                                    color: .blue
                                )
                                
                                WidgetCard(
                                    title: "Security Alerts",
                                    description: "Recent security events",
                                    icon: "shield.fill",
                                    color: .red
                                )
                                
                                WidgetCard(
                                    title: "Quick Actions",
                                    description: "Fast access to features",
                                    icon: "bolt.fill",
                                    color: .orange
                                )
                                
                                WidgetCard(
                                    title: "Statistics",
                                    description: "Usage and activity stats",
                                    icon: "chart.bar.fill",
                                    color: .green
                                )
                            }
                            .accessibilityElement(children: .contain)
                            .accessibilityLabel("Список доступных виджетов")
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .accessibilityElement(children: .contain)
                        .accessibilityLabel("Секция доступных виджетов")
                        
                        Spacer(minLength: 100)
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое экрана настройки виджетов")
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 WidgetConfigurationScreen загружен!")
        }
    }
}

// MARK: - Supporting Views

struct InstructionStep: View {
    let number: String
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: Spacing.s) {
            Text(number)
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 24, height: 24)
                .background(Color.blue)
                .clipShape(Circle())
                .accessibilityLabel("Шаг \(number)")
            
            Text(text)
                .font(.body)
                .foregroundColor(.primary)
                .accessibilityLabel(text)
            
            Spacer()
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Шаг \(number): \(text)")
    }
}

struct WidgetCard: View {
    let title: String
    let description: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
                .accessibilityLabel("Иконка: \(icon)")
            
            Text(title)
                .font(.headline)
                .fontWeight(.semibold)
                .accessibilityLabel(title)
            
            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.leading)
                .accessibilityLabel(description)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.tertiarySystemBackground))
        .cornerRadius(CornerRadius.medium)
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(description)")
    }
}

#if DEBUG
struct WidgetConfigurationScreen_Previews: PreviewProvider {
    static var previews: some View {
        WidgetConfigurationScreen()
    }
}
#endif