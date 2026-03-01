//
//  FamilyTournamentView.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  🏆 Family Tournament - Premium Feature
//  Interactive family challenges and competitions
//

import SwiftUI

struct FamilyTournamentView: View {

    // MARK: - Environment

    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - State

    @State private var selectedTournament: TournamentType = .daily
    @State private var currentScore = 1247
    @State private var familyRank = 3
    @State private var isJoined = true

    // MARK: - Types

    enum TournamentType: String, CaseIterable {
        case daily = "daily"
        case weekly = "weekly"
        case monthly = "monthly"

        var title: String {
            switch self {
            case .daily: return "Daily Challenge"
            case .weekly: return "Weekly Tournament"
            case .monthly: return "Monthly Championship"
            }
        }

        var duration: String {
            switch self {
            case .daily: return "24h"
            case .weekly: return "7 days"
            case .monthly: return "30 days"
            }
        }

        var reward: String {
            switch self {
            case .daily: return "50 🦄"
            case .weekly: return "500 🦄"
            case .monthly: return "2000 🦄"
            }
        }
    }

    // MARK: - Body

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("🏆 Family Tournament")
                        .font(.h3)
                        .foregroundColor(.primary)

                    Text("Challenge your family to fun competitions!")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }

                Spacer()

                // Current score
                VStack(alignment: .trailing, spacing: Spacing.xs) {
                    Text("\(currentScore)")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.orange)

                    Text("Points")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }

            // Tournament selector
            HStack(spacing: Spacing.s) {
                ForEach(TournamentType.allCases, id: \.self) { type in
                    TournamentTypeButton(
                        type: type,
                        isSelected: selectedTournament == type,
                        action: { selectedTournament = type }
                    )
                }
            }

            // Current tournament info
            VStack(spacing: Spacing.m) {
                TournamentCard(tournament: selectedTournament)

                // Join/Leave button
                Button(action: {
                    isJoined.toggle()
                    HapticFeedback.selection()
                }) {
                    Text(isJoined ? "Leave Tournament" : "Join Tournament")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.m)
                        .background(isJoined ? Color.red.opacity(0.8) : Color.green)
                        .cornerRadius(12)
                        .shadow(color: (isJoined ? Color.red : Color.green).opacity(0.3), radius: 5)
                }
            }

            // Family leaderboard
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("Family Leaderboard")
                    .font(.h4)
                    .foregroundColor(.primary)

                FamilyLeaderboardView()
            }
        }
        .padding(Spacing.m)
        .background(Color.cardBackground)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.1), radius: 8)
    }
}

// MARK: - Subviews

struct TournamentTypeButton: View {
    let type: FamilyTournamentView.TournamentType
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Text(type.title)
                    .font(.caption)
                    .fontWeight(isSelected ? .bold : .regular)
                    .foregroundColor(isSelected ? .white : .primary)

                Text(type.duration)
                    .font(.caption2)
                    .foregroundColor(isSelected ? .white.opacity(0.8) : .textSecondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, Spacing.s)
            .padding(.horizontal, Spacing.xs)
            .background(isSelected ? Color.orange : Color.gray.opacity(0.2))
            .cornerRadius(8)
        }
    }
}

struct TournamentCard: View {
    let tournament: FamilyTournamentView.TournamentType

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(tournament.title)
                        .font(.h4)
                        .foregroundColor(.primary)

                    Text("Complete challenges to earn points!")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }

                Spacer()

                VStack(alignment: .trailing, spacing: Spacing.xs) {
                    Text("Reward")
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    Text(tournament.reward)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.orange)
                }
            }

            // Progress bar
            VStack(alignment: .leading, spacing: Spacing.xs) {
                HStack {
                    Text("Progress")
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    Spacer()

                    Text("3/5 challenges")
                        .font(.caption)
                        .foregroundColor(.orange)
                }

                GeometryReader { geometry in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.gray.opacity(0.2))
                            .frame(height: 6)

                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.orange)
                            .frame(width: geometry.size.width * 0.6, height: 6)
                    }
                }
                .frame(height: 6)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.5))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.orange.opacity(0.3), lineWidth: 1)
        )
    }
}

struct FamilyLeaderboardView: View {
    let familyMembers = [
        ("Mom", 1450, true),
        ("Dad", 1320, false),
        ("Alex", 1280, false),
        ("Emma", 1150, false)
    ]

    var body: some View {
        VStack(spacing: Spacing.xs) {
            ForEach(0..<familyMembers.count, id: \.self) { index in
                let member = familyMembers[index]

                HStack(spacing: Spacing.m) {
                    // Rank
                    ZStack {
                        Circle()
                            .fill(index == 0 ? Color.yellow : Color.gray.opacity(0.2))
                            .frame(width: 24, height: 24)

                        Text("\(index + 1)")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(index == 0 ? .white : .primary)
                    }

                    // Crown for winner
                    if index == 0 {
                        Text("👑")
                            .font(.title3)
                    }

                    // Name
                    Text(member.0)
                        .font(.body)
                        .foregroundColor(.primary)
                        .frame(maxWidth: .infinity, alignment: .leading)

                    // Score
                    Text("\(member.1)")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.orange)
                }
                .padding(.vertical, Spacing.xs)
            }
        }
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyTournamentView_Previews: PreviewProvider {
    static var previews: some View {
        FamilyTournamentView()
            .environmentObject(LocalizationManager())
            .padding()
            .background(Color.backgroundPrimary)
            .previewDisplayName("Family Tournament")
    }
}
#endif