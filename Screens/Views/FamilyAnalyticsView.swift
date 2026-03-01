//
//  FamilyAnalyticsView.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  📊 Family Analytics - Premium Feature
//  Advanced family protection statistics and insights
//

import SwiftUI

struct FamilyAnalyticsView: View {

    // MARK: - Environment

    @EnvironmentObject private var localizationManager: LocalizationManager

    // MARK: - State

    @State private var selectedPeriod: AnalyticsPeriod = .week
    @State private var showDetailedView = false

    // MARK: - Types

    enum AnalyticsPeriod: String, CaseIterable {
        case day = "day"
        case week = "week"
        case month = "month"

        var title: String {
            switch self {
            case .day: return "Today"
            case .week: return "This Week"
            case .month: return "This Month"
            }
        }
    }

    // MARK: - Body

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            // Header
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Text("📊 Family Analytics")
                        .font(.h3)
                        .foregroundColor(.primary)

                    Spacer()

                    Button(action: { showDetailedView.toggle() }) {
                        Image(systemName: showDetailedView ? "chart.bar.fill" : "chart.bar")
                            .font(.title2)
                            .foregroundColor(.blue)
                    }
                }

                Text("Advanced protection insights for your family")
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }

            // Period selector
            HStack(spacing: Spacing.s) {
                ForEach(AnalyticsPeriod.allCases, id: \.self) { period in
                    PeriodButton(
                        period: period,
                        isSelected: selectedPeriod == period,
                        action: { selectedPeriod = period }
                    )
                }
            }

            // Analytics cards
            if showDetailedView {
                DetailedAnalyticsView()
            } else {
                SummaryAnalyticsView()
            }
        }
        .padding(Spacing.m)
        .background(Color.cardBackground)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.1), radius: 8)
    }
}

// MARK: - Subviews

struct PeriodButton: View {
    let period: FamilyAnalyticsView.AnalyticsPeriod
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(period.title)
                .font(.caption)
                .fontWeight(isSelected ? .bold : .regular)
                .foregroundColor(isSelected ? .white : .primary)
                .padding(.vertical, Spacing.xs)
                .padding(.horizontal, Spacing.m)
                .background(isSelected ? Color.blue : Color.gray.opacity(0.2))
                .cornerRadius(16)
        }
    }
}

struct SummaryAnalyticsView: View {
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Protection score
            AnalyticsCard(
                icon: "🛡️",
                title: "Family Protection Score",
                value: "94%",
                subtitle: "+2% from last week",
                color: .green
            )

            // Threats blocked
            AnalyticsCard(
                icon: "🚫",
                title: "Threats Blocked",
                value: "127",
                subtitle: "23 attempts prevented",
                color: .orange
            )

            // Screen time managed
            AnalyticsCard(
                icon: "⏱️",
                title: "Screen Time Managed",
                value: "42h",
                subtitle: "15% reduction achieved",
                color: .blue
            )

            // Family activity
            AnalyticsCard(
                icon: "📱",
                title: "Family Activity",
                value: "89%",
                subtitle: "Active family engagement",
                color: .purple
            )
        }
    }
}

struct DetailedAnalyticsView: View {
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Charts would go here
            Text("Detailed Analytics Coming Soon")
                .font(.body)
                .foregroundColor(.textSecondary)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(.vertical, Spacing.xl)

            // Preview of detailed metrics
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("Advanced Metrics:")
                    .font(.h4)
                    .foregroundColor(.primary)

                DetailMetricRow(label: "Risk Assessment Trends", value: "📈 Improving")
                DetailMetricRow(label: "Device Usage Patterns", value: "📊 Analyzed")
                DetailMetricRow(label: "Content Filtering Efficiency", value: "🎯 96%")
                DetailMetricRow(label: "Emergency Response Time", value: "⚡ <30s")
            }
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.5))
            .cornerRadius(12)
        }
    }
}

struct AnalyticsCard: View {
    let icon: String
    let title: String
    let value: String
    let subtitle: String
    let color: Color

    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.title)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.primary)

                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(color)

                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }

            Spacer()
        }
        .padding(Spacing.m)
        .background(color.opacity(0.1))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(color.opacity(0.3), lineWidth: 1)
        )
    }
}

struct DetailMetricRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.body)
                .foregroundColor(.primary)

            Spacer()

            Text(value)
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.blue)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyAnalyticsView_Previews: PreviewProvider {
    static var previews: some View {
        FamilyAnalyticsView()
            .environmentObject(LocalizationManager())
            .padding()
            .background(Color.backgroundPrimary)
            .previewDisplayName("Family Analytics")
    }
}
#endif