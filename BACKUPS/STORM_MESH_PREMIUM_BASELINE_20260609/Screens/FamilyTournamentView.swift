import SwiftUI
import UIKit

/// 🏆 Family Tournament View
/// Семейный турнир с рейтингом
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct FamilyTournamentView: View {
    
    // MARK: - Properties
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var participants: [(name: String, points: Int, avatar: String)] = []
    
    // Сохраняем состояние турнира в AppStorage
    @AppStorage("tournament_selected_index") private var selectedTournamentIndex: Int = 0
    @AppStorage("tournament_quest_progress") private var questProgress: Double = 0.6
    @AppStorage("tournament_days_left") private var daysLeft: Int = 3
    
    // ✅ ГЕЙМИФИКАЦИЯ: Турниры с сервера
    @State private var activeTournaments: [TournamentResponse] = []
    @State private var currentTournament: TournamentResponse? = nil
    @State private var leaderboard: [LeaderboardEntry] = []
    @State private var isLoadingTournaments: Bool = false
    @State private var isLoadingLeaderboard: Bool = false
    @State private var tournamentError: String? = nil
    @State private var isJoined: Bool = false
    
    private let apiService = APIService.shared
    
    // Получаем userId для API вызовов
    private var userId: String {
        UserDefaults.standard.string(forKey: "user_id") ?? "guest"
    }
    
    private var tournamentTypes: [String] {
        [
            localizationManager.localized("family_tournament_type_excellent"),
            localizationManager.localized("family_tournament_type_protector"),
            localizationManager.localized("family_tournament_type_helpers")
        ]
    }
    
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
                        if isLoadingLeaderboard {
                            HStack {
                                ProgressView()
                                Text(localizationManager.localized("loading_leaderboard"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            .padding()
                        } else if let error = tournamentError {
                            Text(error)
                                .font(.caption)
                                .foregroundColor(.dangerRed)
                                .padding()
                        } else if participants.isEmpty {
                            VStack(spacing: Spacing.m) {
                                EmptyStateView(
                                    icon: "🏆",
                                    title: localizationManager.localized("family_tournament_empty_title"),
                                    description: localizationManager.localized("family_tournament_empty_desc"),
                                    actionTitle: isJoined ? nil : localizationManager.localized("join_tournament"),
                                    action: isJoined ? nil : {
                                        joinTournament()
                                    }
                                )
                            }
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
            loadTournamentsFromServer()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadParticipants() // Синхронизируем при изменении family_members_list
        }
        .refreshable {
            await refreshTournamentData()
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Data Loading
    
    private func loadParticipants() {
        // Загружаем участников из family_members_list (локальный fallback)
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
    
    // MARK: - ✅ ГЕЙМИФИКАЦИЯ: API методы для синхронизации турниров
    
    /// Загрузить активные турниры с сервера
    private func loadTournamentsFromServer() {
        isLoadingTournaments = true
        tournamentError = nil
        
        apiService.getGamificationTournaments(status: "active") { [self] result in
            isLoadingTournaments = false
            switch result {
            case .success(let response):
                activeTournaments = response.tournaments
                // Выбираем первый активный турнир, если есть
                if let firstTournament = response.tournaments.first {
                    currentTournament = firstTournament
                    loadLeaderboardForTournament(tournamentId: firstTournament.id)
                    checkIfJoined(tournamentId: firstTournament.id)
                }
            case .failure(let error):
                tournamentError = error.localizedDescription
                // Используем локальные данные при ошибке
            }
        }
    }
    
    /// Загрузить таблицу лидеров для турнира
    private func loadLeaderboardForTournament(tournamentId: String) {
        isLoadingLeaderboard = true
        
        apiService.getGamificationTournamentLeaderboard(tournamentId: tournamentId, limit: 50) { [self] result in
            isLoadingLeaderboard = false
            switch result {
            case .success(let response):
                leaderboard = response.leaderboard
                // Обновляем локальных участников данными с сервера
                updateParticipantsFromLeaderboard(response.leaderboard)
            case .failure(let error):
                tournamentError = error.localizedDescription
            }
        }
    }
    
    /// Обновить участников из таблицы лидеров сервера
    private func updateParticipantsFromLeaderboard(_ serverLeaderboard: [LeaderboardEntry]) {
        // Конвертируем LeaderboardEntry в формат участников
        participants = serverLeaderboard.map { entry in
            (
                name: entry.username ?? entry.userId,
                points: entry.score,
                avatar: entry.avatar ?? "👤"
            )
        }
        
        // Если участников с сервера нет, используем локальных
        if participants.isEmpty {
            loadParticipants()
        }
    }
    
    /// Проверить, присоединен ли пользователь к турниру
    private func checkIfJoined(tournamentId: String) {
        // Загружаем историю турниров пользователя
        apiService.getGamificationTournamentsHistory(userId: userId, limit: 10) { [self] result in
            switch result {
            case .success(let response):
                // Проверяем, есть ли текущий турнир в истории
                isJoined = response.tournaments.contains { $0.id == tournamentId }
            case .failure:
                isJoined = false
            }
        }
    }
    
    /// Присоединиться к турниру
    private func joinTournament() {
        guard let tournament = currentTournament else { return }
        
        apiService.joinGamificationTournament(
            userId: userId,
            tournamentId: tournament.id,
            deviceId: UIDevice.current.identifierForVendor?.uuidString
        ) { [self] result in
            switch result {
            case .success:
                isJoined = true
                HapticFeedback.notification(.success)
                // Обновляем данные турнира
                loadLeaderboardForTournament(tournamentId: tournament.id)
            case .failure(let error):
                tournamentError = error.localizedDescription
                HapticFeedback.notification(.error)
            }
        }
    }
    
    /// Обновить все данные турнира (для pull-to-refresh)
    @MainActor
    private func refreshTournamentData() async {
        loadTournamentsFromServer()
        if let tournamentId = currentTournament?.id {
            loadLeaderboardForTournament(tournamentId: tournamentId)
        }
        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 секунды
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
            
            Text(localizationManager.localized("family_tournament_title"))
                .font(.h2)
                .foregroundColor(.warningOrange)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    // MARK: - Timer View
    
    private var timerView: some View {
        VStack(spacing: Spacing.xs) {
            if let tournament = currentTournament {
                // Показываем информацию о турнире с сервера
                Text(tournament.name)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                if let description = tournament.description {
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                // Вычисляем дни до окончания
                if let endDate = ISO8601DateFormatter().date(from: tournament.endDate) {
                    let days = Calendar.current.dateComponents([.day], from: Date(), to: endDate).day ?? 0
                    Text(String(format: localizationManager.localized("family_tournament_timer"), max(0, days)))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                } else {
                    Text(String(format: localizationManager.localized("family_tournament_timer"), daysLeft))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                
                // Кнопка присоединения, если не присоединен
                if !isJoined {
                    Button(action: {
                        joinTournament()
                    }) {
                        Text(localizationManager.localized("join_tournament"))
                            .font(.body)
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.l)
                            .padding(.vertical, Spacing.s)
                            .background(Color.primaryBlue)
                            .cornerRadius(CornerRadius.medium)
                    }
                    .padding(.top, Spacing.xs)
                }
            } else {
                // Fallback на локальные данные
                Text(String(format: localizationManager.localized("family_tournament_timer"), daysLeft))
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
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
        let medal = rank == 1 ? localizationManager.localized("family_tournament_medal_1") : (rank == 2 ? localizationManager.localized("family_tournament_medal_2") : localizationManager.localized("family_tournament_medal_3"))
        let prize = rank == 1 ? localizationManager.localized("family_tournament_prize_1") : (rank == 2 ? localizationManager.localized("family_tournament_prize_2") : localizationManager.localized("family_tournament_prize_3"))
        
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
            Text(localizationManager.localized("family_tournament_family_quest"))
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Text(localizationManager.localized("family_tournament_family_quest_desc"))
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
                Text(localizationManager.localized("family_tournament_family_quest_progress"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Spacer()
                Text(String(format: "%.0f%%", questProgress * 100))
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.successGreen)
            }
            
            Text(localizationManager.localized("family_tournament_family_quest_reward"))
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
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
#endif



