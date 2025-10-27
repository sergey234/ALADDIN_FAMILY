//
//  RoleSelectionModal.swift
//  ALADDIN
//
//  Created by AI Assistant on 2024
//  Модальное окно выбора роли пользователя
//

import SwiftUI

struct RoleSelectionModal: View {
    @Binding var isPresented: Bool
    @State private var selectedRole: FamilyRole = .parent
    let onRoleSelected: (FamilyRole) -> Void
    
    // Используем FamilyRole из ViewModels
    // Дополнительные свойства для FamilyRole
    private func icon(for role: FamilyRole) -> String {
        switch role {
        case .parent: return "person.2.fill"
        case .child: return "person.fill"
        case .grandparent: return "person.badge.shield.checkmark.fill"
        }
    }
    
    private func description(for role: FamilyRole) -> String {
        switch role {
        case .parent: return "Полный доступ к настройкам и контролю"
        case .child: return "Ограниченный доступ под контролем родителей"
        case .grandparent: return "Расширенные права для опеки"
        }
    }
    
    var body: some View {
        VStack(spacing: 20) {
            // Заголовок
            VStack(spacing: 12) {
                Text("Выберите роль")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.primary)
                
                Text("Это поможет настроить интерфейс под ваши потребности")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            
            // Список ролей
            VStack(spacing: 12) {
                ForEach(FamilyRole.allCases, id: \.self) { role in
                    RoleSelectionCard(
                        role: role,
                        isSelected: selectedRole == role,
                        onTap: {
                            selectedRole = role
                        }
                    )
                }
            }
            
            // Кнопки
            HStack(spacing: 16) {
                Button("Отмена") {
                    isPresented = false
                }
                .buttonStyle(.bordered)
                
                Button("Продолжить") {
                    onRoleSelected(selectedRole)
                    isPresented = false
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(20)
        .background(Color.black.opacity(0.1))
        .cornerRadius(16)
        .shadow(radius: 20)
    }
}

struct RoleSelectionCard: View {
    let role: FamilyRole
    let isSelected: Bool
    let onTap: () -> Void
    
    private func icon(for role: FamilyRole) -> String {
        switch role {
        case .parent: return "person.2.fill"
        case .child: return "person.fill"
        case .grandparent: return "person.badge.shield.checkmark.fill"
        }
    }
    
    private func description(for role: FamilyRole) -> String {
        switch role {
        case .parent: return "Полный доступ к настройкам и контролю"
        case .child: return "Ограниченный доступ под контролем родителей"
        case .grandparent: return "Расширенные права для опеки"
        }
    }
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                Image(systemName: icon(for: role))
                    .font(.title2)
                    .foregroundColor(isSelected ? .blue : .secondary)
                    .frame(width: 30)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(role.rawValue)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text(description(for: role))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                        .font(.title3)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct RoleSelectionModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            RoleSelectionModal(
                isPresented: $isPresented,
                onRoleSelected: { role in
                    print("Selected role: \(role.rawValue)")
                }
            )
        }
    }
}
