import SwiftUI
import UIKit

/// 👤 Family Member Card
/// Карточка члена семьи для экрана Family
/// Источник дизайна: HTML .member-card на 02_family_screen.html
struct FamilyMemberCard: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    let name: String
    let role: FamilyRole
    let avatar: String
    let status: ProtectionStatus
    let threatsBlocked: Int
    let lastActive: String
    let action: () -> Void
    var onDelete: (() -> Void)? = nil  // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #4: Функция удаления
    var showDeleteButton: Bool = false  // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #4: Показывать ли кнопку удаления
    var isDeleteDisabled: Bool = false
    // Маркер источника: "server" / "local" (микрометка)
    var originBadge: String? = nil
    
    // MARK: - Localized Role Label
    
    private var localizedRoleLabel: String {
        switch role {
        case .parent: return localizationManager.localized("family_role_parent_label")
        case .child: return localizationManager.localized("family_role_child_label")
        case .teenager: return localizationManager.localized("family_role_teen_label")
        case .elderly: return localizationManager.localized("family_role_elderly_label")
        }
    }
    
    // MARK: - Family Role
    
    enum FamilyRole: String, Codable, Equatable {
        case parent      // Родитель
        case child       // Ребёнок
        case teenager    // Подросток
        case elderly     // Пожилой
        
        var label: String {
            switch self {
            case .parent: return "Родитель"
            case .child: return "Ребёнок"
            case .teenager: return "Подросток"
            case .elderly: return "Пожилой"
            }
        }
        
        var icon: String {
            switch self {
            case .parent: return "👨‍💼"
            case .child: return "👶"
            case .teenager: return "🧒"
            case .elderly: return "👴"
            }
        }
    }
    
    // MARK: - Protection Status
    
    enum ProtectionStatus: String, Codable, Equatable {
        case protected   // 🟢 Защищён
        case warning     // ⚠️ Предупреждение
        case danger      // 🔴 Опасность
        case offline     // ⚫ Оффлайн
        
        var label: String {
            switch self {
            case .protected: return "Защищён"
            case .warning: return "Внимание"
            case .danger: return "Угроза"
            case .offline: return "Оффлайн"
            }
        }
        
        var color: Color {
            switch self {
            case .protected: return .green
            case .warning: return .orange
            case .danger: return .red
            case .offline: return .gray
            }
        }
        
        var indicator: String {
            switch self {
            case .protected: return "🟢"
            case .warning: return "⚠️"
            case .danger: return "🔴"
            case .offline: return "⚫"
            }
        }
    }
    
    // MARK: - Init
    
    init(
        name: String,
        role: FamilyRole,
        avatar: String,
        status: ProtectionStatus,
        threatsBlocked: Int,
        lastActive: String = "",
        action: @escaping () -> Void,
        onDelete: (() -> Void)? = nil,
        showDeleteButton: Bool = false,
        isDeleteDisabled: Bool = false,
        originBadge: String? = nil
    ) {
        self.name = name
        self.role = role
        self.avatar = avatar
        self.status = status
        self.threatsBlocked = threatsBlocked
        self.lastActive = lastActive
        self.action = action
        self.onDelete = onDelete
        self.showDeleteButton = showDeleteButton
        self.isDeleteDisabled = isDeleteDisabled
        self.originBadge = originBadge
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            Button(action: {
                // Haptic feedback
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
                
                // Вызываем action() closure
                print("✅ [FamilyMemberCard] Основная кнопка карточки нажата для: \(name)")
                action()
            }) {
            VStack(spacing: 4) {
                // Верхняя часть: Аватар и имя
                HStack(spacing: 4) {
                    Text(avatar)
                        .font(.system(size: 16))
                    
                    Text(name)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                        .lineLimit(1)
                    
                    Spacer()
                    
                    // Микрометка источника
                    if let origin = originBadge, !origin.isEmpty {
                        // Нормализуем подпись: "local" → "pending"
                        let originText = origin.lowercased() == "local" ? "pending" : origin
                        Text(originText)
                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(originText.lowercased() == "server" ? Color.green.opacity(0.8) : Color.gray.opacity(0.8))
                            .clipShape(Capsule())
                    }
                    
                    // ✅ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ #4: Кнопка удаления (видимая и заметная)
                    if showDeleteButton, let onDelete = onDelete {
                        Button(action: {
                            guard !isDeleteDisabled else { return }
                            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Останавливаем распространение события
                            // чтобы не вызывался action() основной карточки
                            print("🗑️ [FamilyMemberCard] Кнопка удаления нажата для: \(name)")
                            
                            // Haptic feedback
                            let generator = UINotificationFeedbackGenerator()
                            generator.notificationOccurred(.warning)
                            
                            // Вызываем функцию удаления
                            onDelete()
                        }) {
                            Image(systemName: "trash.fill")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 28, height: 28)
                                .background(Color.red)
                                .clipShape(Circle())
                                .shadow(color: .red.opacity(0.3), radius: 4, x: 0, y: 2)
                                .opacity(isDeleteDisabled ? 0.45 : 1.0)
                        }
                        .buttonStyle(PlainButtonStyle())
                        .disabled(isDeleteDisabled)
                        .zIndex(10)  // Поверх других элементов
                        .onTapGesture {
                            // ✅ Дополнительная защита: предотвращаем всплытие события
                            print("🗑️ [FamilyMemberCard] onTapGesture для кнопки удаления")
                        }
                    }
                }
                
                // Роль
                Text(localizedRoleLabel)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                    .lineLimit(1)
                
                Spacer()
                
                // Статус
                Text(status.indicator)
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Кнопка удаления ВНЕ основной кнопки для предотвращения конфликтов
            if showDeleteButton, let onDelete = onDelete {
                VStack {
                    HStack {
                        Spacer()
                        Button(action: {
                            guard !isDeleteDisabled else { return }
                            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Останавливаем распространение события
                            print("🗑️ [FamilyMemberCard] Кнопка удаления нажата для: \(name)")
                            
                            // Haptic feedback
                            let generator = UINotificationFeedbackGenerator()
                            generator.notificationOccurred(.warning)
                            
                            // Вызываем функцию удаления
                            onDelete()
                        }) {
                            Image(systemName: "trash.fill")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 28, height: 28)
                                .background(Color.red)
                                .clipShape(Circle())
                                .shadow(color: .red.opacity(0.3), radius: 4, x: 0, y: 2)
                                .opacity(isDeleteDisabled ? 0.45 : 1.0)
                        }
                        .buttonStyle(PlainButtonStyle())
                        .disabled(isDeleteDisabled)
                        .padding(.top, 8)
                        .padding(.trailing, 8)
                    }
                    Spacer()
                }
                .zIndex(1000)  // ✅ Очень высокий приоритет - поверх всего
                .allowsHitTesting(true)
            }
        }
        .buttonStyle(PlainButtonStyle())
        .contentShape(Rectangle())  // Явная область для нажатий
        .allowsHitTesting(true)  // ✅ Явное разрешение нажатий
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyMemberCard_Previews: PreviewProvider {
    static var previews: some View {
    VStack(spacing: 16) {
        // Родитель - защищён
        FamilyMemberCard(
            name: "Сергей",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 47
        ) {
            print("Открыть профиль Сергея")
        }
        
        // Ребёнок - предупреждение
        FamilyMemberCard(
            name: "Маша",
            role: .child,
            avatar: "👧",
            status: .warning,
            threatsBlocked: 23,
            lastActive: "5 мин назад"
        ) {
            print("Открыть профиль Маши")
        }
        
        // Пожилой - оффлайн
        FamilyMemberCard(
            name: "Бабушка",
            role: .elderly,
            avatar: "👵",
            status: .offline,
            threatsBlocked: 12,
            lastActive: "2 часа назад"
        ) {
            print("Открыть профиль Бабушки")
        }
    }
    .padding()
    .background(
        LinearGradient(
            colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )
    }
}
#endif



