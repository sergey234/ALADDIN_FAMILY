import SwiftUI

/// 🎉 Welcome Card for Family Creator
/// Информационная карточка для нового создателя семьи (Вариант 3)
struct WelcomeCardForCreator: View {
    let currentUser: FamilyMemberData
    let onShowInvitationGuide: () -> Void
    let onAddMember: () -> Void
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Заголовок
            HStack {
                Text("🎉")
                    .font(.system(size: 32))
                Text("Добро пожаловать!")
                    .font(.h2)
                    .foregroundColor(.secondaryGold)
            }
            .padding(.top, Spacing.m)
            
            Text("Вы создали новую семью")
                .font(.body)
                .foregroundColor(.white.opacity(0.9))
                .padding(.bottom, Spacing.s)
            
            // Карточка текущего пользователя
            FamilyMemberCard(
                name: currentUser.name,
                role: currentUser.role,
                avatar: currentUser.avatar,
                status: currentUser.status,
                threatsBlocked: currentUser.threatsBlocked,
                lastActive: currentUser.lastActive,
                action: {}
            )
            .frame(width: 120)
            .padding(.vertical, Spacing.s)
            
            // Подсказки
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("Теперь пригласите членов семьи:")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.8))
                    .padding(.bottom, Spacing.xxs)
                
                HStack(spacing: Spacing.xs) {
                    Text("•")
                        .foregroundColor(.secondaryGold)
                    Text("Введите код приглашения")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                
                HStack(spacing: Spacing.xs) {
                    Text("•")
                        .foregroundColor(.secondaryGold)
                    Text("Сканируйте QR-код")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
                
                HStack(spacing: Spacing.xs) {
                    Text("•")
                        .foregroundColor(.secondaryGold)
                    Text("Создайте новую семью")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            .padding(.vertical, Spacing.s)
            
            // Кнопка подсказки
            Button(action: onShowInvitationGuide) {
                HStack {
                    Text("➡️")
                    Text("Как пригласить участников")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.secondaryGold)
                .padding(.vertical, Spacing.s)
                .padding(.horizontal, Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
            }
            .padding(.bottom, Spacing.m)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.l)
        .background(Color.secondaryGold.opacity(0.1))
        .cornerRadius(CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 2)
        )
    }
}

