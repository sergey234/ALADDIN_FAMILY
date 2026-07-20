import SwiftUI

/// P1.4b — micro-steps checklist + Done → Unicorn XP (not for water habit).
struct CompanionBreakStepsSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    let plan: CompanionBreakStepsPlan
    @State private var doneFlags: [Bool]
    @State private var waterBlocked = false
    @State private var assignedNote: String?

    init(plan: CompanionBreakStepsPlan) {
        self.plan = plan
        _doneFlags = State(initialValue: Array(repeating: false, count: plan.steps.count))
    }

    private var canAssignToChild: Bool {
        let band = WellnessSessionStore.cachedAgeBand ?? CompanionUserContext.companionAgeBand
        return band == "parent" || band == "senior"
    }

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .neutral).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(plan.goal)
                            .font(.headline)
                        if waterBlocked {
                            Text(localizationManager.localized("companion_break_steps_water_blocked"))
                                .font(.caption)
                                .foregroundColor(.orange)
                        }
                        ForEach(Array(plan.steps.enumerated()), id: \.offset) { index, step in
                            Button {
                                toggleStep(index)
                            } label: {
                                HStack(alignment: .top, spacing: 10) {
                                    Image(systemName: doneFlags[safe: index] == true ? "checkmark.circle.fill" : "circle")
                                        .foregroundColor(doneFlags[safe: index] == true ? Color(hex: "34D399") : .white.opacity(0.6))
                                    Text(step)
                                        .font(.subheadline)
                                        .multilineTextAlignment(.leading)
                                        .foregroundColor(doneFlags[safe: index] == true ? .white.opacity(0.45) : .white)
                                    Spacer(minLength: 0)
                                }
                                .padding(10)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.white.opacity(0.08))
                                .cornerRadius(10)
                            }
                            .buttonStyle(.plain)
                            .accessibilityIdentifier("companion_break_step_\(index)")
                        }
                        if canAssignToChild {
                            Button {
                                let payload = [
                                    "goal": plan.goal,
                                    "steps": plan.steps.joined(separator: "\n")
                                ]
                                if let data = try? JSONSerialization.data(withJSONObject: payload),
                                   let raw = String(data: data, encoding: .utf8) {
                                    UserDefaults.standard.set(raw, forKey: "companion_break_steps_child_assignment")
                                    assignedNote = localizationManager.localized("companion_break_steps_assigned")
                                }
                            } label: {
                                Label(
                                    localizationManager.localized("companion_break_steps_assign_child"),
                                    systemImage: "person.crop.circle.badge.plus"
                                )
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                            }
                            .buttonStyle(.bordered)
                            if let assignedNote {
                                Text(assignedNote)
                                    .font(.caption)
                                    .foregroundColor(Color(hex: "34D399"))
                            }
                        }
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("companion_break_steps_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("wellness_guide_cancel")) { dismiss() }
                }
            }
            .onAppear {
                waterBlocked = CompanionBreakStepsService.isWaterHabitGoal(plan.goal)
            }
        }
        .accessibilityIdentifier("companion_break_steps_sheet")
    }

    private func toggleStep(_ index: Int) {
        guard doneFlags.indices.contains(index) else { return }
        if doneFlags[index] { return }
        if CompanionBreakStepsService.isWaterHabitGoal(plan.goal) {
            waterBlocked = true
            doneFlags[index] = true
            return
        }
        doneFlags[index] = true
        _ = CompanionBreakStepsService.markStepDone(planId: plan.id, index: index, goal: plan.goal)
        HapticFeedback.impact(.light)
    }
}

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
