import SwiftUI

/// 🏆 Family Tournament View
/// Семейный турнир с рейтингом
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct FamilyTournamentView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    
    @State private var participants: [(name: String, points: Int, avatar: String)] = []
    
    @State private var tournamentTypes = ["📚 Отличники", "🛡️ Защитники", "🧹 Помощники"]
    
    // Сохраняем состояние турнира в AppStorage
    @AppStorage("tournament_selected_index") private var selectedTournamentIndex: Int = 0
    @AppStorage("tournament_quest_progress") private var questProgress: Double = 0.6
    @AppStorage("tournament_days_left") private var daysLeft: Int = 3
    
    private var tournamentType: String {
        tournamentTypes[selectedTournamentIndex]
    }
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header с кнопкой "← Назад"
                header
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Переключатель типов турнира
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: Spacing.m) {
                                ForEach(Array(tournamentTypes.enumerated()), id: \.offset) { index, type in
                                    Button(action: {
                                        withAnimation(.easeInOut(duration: 0.3)) {
                                            selectedTournamentIndex = index
                                        }
                                    }) {
                                        Text(type)
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundColor(selectedTournamentIndex == index ? .white : .textSecondary)
                                            .padding(.horizontal, 16)
                                            .padding(.vertical, 8)
                                            .background(
                                                RoundedRectangle(cornerRadius: CornerRadius.large)
                                                    .fill(selectedTournamentIndex == index ? Color.primaryBlue : Color.clear)
                                            )
                                            .overlay(
                                                RoundedRectangle(cornerRadius: CornerRadius.large)
                                                    .stroke(Color.primaryBlue, lineWidth: selectedTournamentIndex == index ? 0 : 1)
                                            )
                                    }
                                }
                            }
                            .padding(.horizontal, Spacing.screenPadding)
                        }
                        .padding(.vertical, Spacing.s)
                        
                        // Таймер
                        timerView
                        
                        // Рейтинг
                        if participants.isEmpty {
                            EmptyStateView(
                                icon: "🏆",
                                title: "Турнир ещё не начался",
                                description: "Участники турнира появятся здесь после начала семейного соревнования",
                                actionTitle: nil,
                                action: nil
                            )
                            .padding()
                        } else {
                            leaderboardView
                        }
                        
                        // Семейный квест
                        questView
                        
                        Spacer()
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .onAppear {
            loadParticipants()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadParticipants() // Синхронизируем при изменении family_members_list
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Data Loading
    
    private func loadParticipants() {
        // Загружаем участников из family_members_list
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            participants = []
            print("⚠️ Нет данных о членах семьи для турнира")
            return
        }
        
        // Фильтруем только детей и подростков
        let childrenMembers = decoded.filter { member in
            member.role == .child || member.role == .teenager
        }
        
        // Преобразуем в формат турнира: (name, points, avatar)
        participants = childrenMembers.map { member in
            // Загружаем баллы турнира из UserDefaults для каждого участника
            let pointsKey = "tournament_points_\(member.name)"
            let points = UserDefaults.standard.integer(forKey: pointsKey)
            
            return (
                name: member.name,
                points: points > 0 ? points : 0, // Если баллов нет - 0
                avatar: member.avatar
            )
        }
        
        // Сортируем по баллам (от большего к меньшему)
        participants.sort { $0.points > $1.points }
        
        print("✅ Загружено участников турнира: \(participants.count)")
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack {
            Button(action: {
                HapticFeedback.impact(.light)
                navigationManager.goBack()
            }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.textPrimary)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
            }
            
            Text("🏆 Турнир семьи")
                .font(.h2)
                .foregroundColor(.warningOrange)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Timer View
    
    private var timerView: some View {
        Text("⏰ До завершения: \(daysLeft) дня")
            .font(.body)
            .foregroundColor(.textSecondary)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
    }
    
    private var leaderboardView: some View {
        VStack(spacing: Spacing.s) {
            ForEach(Array(participants.enumerated()), id: \.offset) { index, participant in
                participantRow(
                    rank: index + 1,
                    name: participant.name,
                    score: participant.points,
                    avatar: participant.avatar
                )
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func participantRow(rank: Int, name: String, score: Int, avatar: String) -> some View {
        let medal = rank == 1 ? "🥇" : (rank == 2 ? "🥈" : "🥉")
        let prize = rank == 1 ? "+50 🦄" : (rank == 2 ? "+30 🦄" : "+20 🦄")
        
        return HStack(spacing: Spacing.m) {
            Text(medal)
                .font(.system(size: 32))
            
            Text(avatar)
                .font(.system(size: 28))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Text(prize)
                    .font(.caption)
                    .foregroundColor(.successGreen)
            }
            
            Spacer()
            
            Text("\(score)")
                .font(.h2)
                .foregroundColor(.primaryBlue)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(rank == 1 ? Color(hex: "FFD700").opacity(0.1) : Color.backgroundMedium.opacity(0.5))
        )
    }
    
    private var questView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("👨‍👩‍👧‍👦 СЕМЕЙНЫЙ КВЕСТ")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Text("Вместе заработайте 500 🦄 за неделю")
                .font(.body)
                .foregroundColor(.textSecondary)
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 20)
                    
                    RoundedRectangle(cornerRadius: 10)
                        .fill(LinearGradient(colors: [.successGreen, .successGreen.opacity(0.8)], startPoint: .leading, endPoint: .trailing))
                        .frame(width: geometry.size.width * questProgress, height: 20)
                }
            }
            .frame(height: 20)
            
            HStack {
                Text("300 🦄 / 500 🦄")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Spacer()
                Text("60%")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.successGreen)
            }
            
            Text("🎁 Награда: каждому по +50 🦄")
                .font(.caption)
                .foregroundColor(.successGreen)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
}

#if DEBUG
struct FamilyTournamentView_Previews: PreviewProvider {
    static var previews: some View {
        FamilyTournamentView()
    }
}
#endif



