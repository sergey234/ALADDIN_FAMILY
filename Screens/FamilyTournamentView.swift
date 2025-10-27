import SwiftUI

/// 🏆 Family Tournament View
/// Семейный турнир с рейтингом
/// Источник дизайна: /mobile/wireframes/family_tournament_component.html
struct FamilyTournamentView: View {
    
    @State private var participants = [
        ("Маша", 285, "👧"),
        ("Петя", 240, "👦"),
        ("Катя", 195, "👧")
    ]
    
    @State private var tournamentType = "📚 Отличники"
    @State private var questProgress: Double = 0.6
    @State private var daysLeft = 3
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Заголовок
                    Text("🏆 СЕМЕЙНЫЙ ТУРНИР")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    // Тип турнира
                    Text(tournamentType)
                        .font(.h3)
                        .foregroundColor(.primaryBlue)
                    
                    // Таймер
                    timerView
                    
                    // Рейтинг
                    leaderboardView
                    
                    // Семейный квест
                    questView
                    
                    Spacer()
                }
                .padding(.top, Spacing.xxl)
            }
        }
    }
    
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
                participantRow(rank: index + 1, name: participant.0, score: participant.1, avatar: participant.2)
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



