import SwiftUI

/// Панель отслеживания исполнения основного плана: зеркало `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`
/// (сводка, **полный список открытых задач** на экране, локальные галочки; выполненные — в листе).
struct ImplementationPlanWorkbenchCard: View {
    private static let struckPendingUserDefaultsKey = "implementation_plan_struck_pending_ids_v1"

    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showCompletedChecklist = false
    @State private var showPendingChecklist = false
    @State private var keyFilesExpanded = false
    @State private var struckPendingIds: Set<String> = []

    private var loc: LocalizationManager { localizationManager }

    private var completedCount: Int { ImplementationPlanDashboardMirror.completedItems.count }
    private var pendingCount: Int { ImplementationPlanDashboardMirror.pendingItems.count }
    private var validPendingIds: Set<String> {
        Set(ImplementationPlanDashboardMirror.pendingItems.map(\.id))
    }

    private var notStruckOpenCount: Int {
        pendingCount - struckPendingIds.count
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(loc.localized("main_exec_plan_panel_title"))
                .font(.headline)
                .fontWeight(.bold)
                .foregroundColor(.white)

            Text(loc.localized("main_exec_plan_panel_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
                .fixedSize(horizontal: false, vertical: true)

            Text(String(format: loc.localized("main_exec_plan_panel_updated_fmt"), ImplementationPlanDashboardMirror.generatedAtUTC))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.65))

            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text("\(ImplementationPlanProgressValues.doneTasks)")
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                Text("/ \(ImplementationPlanProgressValues.totalTasks)")
                    .font(.title2.weight(.medium))
                    .foregroundColor(.white.opacity(0.9))
            }
            .accessibilityElement(children: .combine)

            Text(String(format: loc.localized("main_exec_plan_panel_done_big_fmt"), completedCount))
                .font(.title3.weight(.semibold))
                .foregroundColor(Color.green.opacity(0.95))

            Text(String(format: loc.localized("main_exec_plan_panel_pending_big_fmt"), pendingCount))
                .font(.title2.weight(.semibold))
                .foregroundColor(Color.orange.opacity(0.95))

            Text(String(format: loc.localized("main_exec_plan_local_tick_progress_fmt"), notStruckOpenCount, pendingCount))
                .font(.subheadline.weight(.medium))
                .foregroundColor(.white.opacity(0.9))

            Text(loc.localized("main_exec_plan_chat_snapshot_hint"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.7))
                .fixedSize(horizontal: false, vertical: true)

            Text("Post-plan final item: stabilize ALADDINUnitTests + run ChildRosterReconcilePolicyTests (after closing all plan tasks).")
                .font(.caption2.weight(.semibold))
                .foregroundColor(Color.yellow.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)

            Divider()
                .background(Color.white.opacity(0.35))

            Text(loc.localized("main_exec_plan_all_open_inline_header"))
                .font(.title3.weight(.bold))
                .foregroundColor(.white)

            Text(loc.localized("main_exec_plan_inline_strike_hint"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: 12) {
                ForEach(Array(ImplementationPlanDashboardMirror.pendingItems.enumerated()), id: \.element.id) { pair in
                    let index = pair.offset + 1
                    let line = pair.element
                    let struck = struckPendingIds.contains(line.id)
                    HStack(alignment: .top, spacing: 10) {
                        Button {
                            toggleStruck(line.id)
                        } label: {
                            Image(systemName: struck ? "checkmark.circle.fill" : "circle")
                                .font(.title2)
                                .foregroundColor(struck ? Color.green.opacity(0.95) : .white.opacity(0.9))
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel(struck ? loc.localized("main_exec_plan_a11y_mark_undone") : loc.localized("main_exec_plan_a11y_mark_done"))

                        VStack(alignment: .leading, spacing: 4) {
                            Text("\(index).  \(line.context)")
                                .font(.caption.weight(.semibold))
                                .foregroundColor(.white.opacity(struck ? 0.45 : 0.78))
                            Text(line.title)
                                .font(.body.weight(.medium))
                                .foregroundColor(.white)
                                .opacity(struck ? 0.5 : 1)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(.vertical, 4)
                }
            }

            Divider()
                .background(Color.white.opacity(0.35))

            DisclosureGroup(isExpanded: $keyFilesExpanded) {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(Array(ImplementationPlanDashboardMirror.keyWorkingFilePaths.enumerated()), id: \.offset) { _, path in
                        Text(path)
                            .font(.caption.monospaced())
                            .foregroundColor(.white.opacity(0.88))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(.top, 6)
            } label: {
                VStack(alignment: .leading, spacing: 2) {
                    Text(loc.localized("main_exec_plan_key_files_header"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.white)
                    Text(loc.localized("main_exec_plan_key_files_caption"))
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.65))
                }
            }
            .tint(.white.opacity(0.9))

            Divider()
                .background(Color.white.opacity(0.35))

            Text(loc.localized("main_exec_plan_panel_tracks_phases_caption"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.white.opacity(0.85))

            Text(String(
                format: loc.localized("settings_exec_plan_track_a_fmt"),
                ImplementationPlanProgressValues.trackADone,
                ImplementationPlanProgressValues.trackATotal,
                ImplementationPlanProgressValues.trackAProgressPercent
            ))
            .font(.title3)
            .foregroundColor(.white)
            .fixedSize(horizontal: false, vertical: true)

            Text(String(
                format: loc.localized("settings_exec_plan_track_b_fmt"),
                ImplementationPlanProgressValues.trackBDone,
                ImplementationPlanProgressValues.trackBTotal,
                ImplementationPlanProgressValues.trackBProgressPercent
            ))
            .font(.title3)
            .foregroundColor(.white)
            .fixedSize(horizontal: false, vertical: true)

            ForEach(0..<10, id: \.self) { index in
                let stats = phaseStats(index)
                Text(String(format: loc.localized("settings_exec_plan_phase_row_fmt"), index, stats.done, stats.total, stats.pending))
                    .font(.title3)
                    .foregroundColor(stats.pending > 0 ? Color.white : Color.white.opacity(0.55))
                    .fixedSize(horizontal: false, vertical: true)
            }

            VStack(spacing: 10) {
                Button {
                    showCompletedChecklist = true
                } label: {
                    Text(String(format: loc.localized("main_exec_plan_open_done_button_fmt"), completedCount))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.green.opacity(0.88)))
                }
                .buttonStyle(.plain)
                .accessibilityHint(loc.localized("main_exec_plan_open_done_accessibility_hint"))

                Button {
                    showPendingChecklist = true
                } label: {
                    Text(String(format: loc.localized("main_exec_plan_open_fullscreen_button_fmt"), pendingCount))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(RoundedRectangle(cornerRadius: 10).fill(Color.white.opacity(0.92)))
                }
                .buttonStyle(.plain)
                .accessibilityHint(loc.localized("main_exec_plan_open_all_accessibility_hint"))
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.12))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.white.opacity(0.22), lineWidth: 1)
                )
        )
        .accessibilityElement(children: .contain)
        .accessibilityLabel(loc.localized("main_exec_plan_panel_accessibility"))
        .onAppear(perform: reconcileStruckPendingFromStorage)
        .sheet(isPresented: $showCompletedChecklist) {
            ImplementationPlanDashboardChecklistSheet(
                items: ImplementationPlanDashboardMirror.completedItems,
                navigationTitle: loc.localized("main_exec_plan_sheet_title_done")
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPendingChecklist) {
            ImplementationPlanDashboardChecklistSheet(
                items: ImplementationPlanDashboardMirror.pendingItems,
                navigationTitle: loc.localized("main_exec_plan_sheet_title")
            )
            .environmentObject(localizationManager)
        }
    }

    private func reconcileStruckPendingFromStorage() {
        var loaded = Self.loadStruckIdsFromDefaults()
        loaded = loaded.intersection(validPendingIds)
        struckPendingIds = loaded
        Self.saveStruckIdsToDefaults(loaded)
    }

    private func toggleStruck(_ id: String) {
        if struckPendingIds.contains(id) {
            struckPendingIds.remove(id)
        } else {
            struckPendingIds.insert(id)
        }
        Self.saveStruckIdsToDefaults(struckPendingIds)
    }

    private static func loadStruckIdsFromDefaults() -> Set<String> {
        guard let data = UserDefaults.standard.data(forKey: struckPendingUserDefaultsKey),
              let arr = try? JSONDecoder().decode([String].self, from: data) else {
            return []
        }
        return Set(arr)
    }

    private static func saveStruckIdsToDefaults(_ ids: Set<String>) {
        let arr = Array(ids).sorted()
        if let data = try? JSONEncoder().encode(arr) {
            UserDefaults.standard.set(data, forKey: struckPendingUserDefaultsKey)
        }
    }

    private func phaseStats(_ phase: Int) -> (done: Int, total: Int, pending: Int) {
        switch phase {
        case 0: return (ImplementationPlanProgressValues.phase0Done, ImplementationPlanProgressValues.phase0Total, ImplementationPlanProgressValues.phase0Pending)
        case 1: return (ImplementationPlanProgressValues.phase1Done, ImplementationPlanProgressValues.phase1Total, ImplementationPlanProgressValues.phase1Pending)
        case 2: return (ImplementationPlanProgressValues.phase2Done, ImplementationPlanProgressValues.phase2Total, ImplementationPlanProgressValues.phase2Pending)
        case 3: return (ImplementationPlanProgressValues.phase3Done, ImplementationPlanProgressValues.phase3Total, ImplementationPlanProgressValues.phase3Pending)
        case 4: return (ImplementationPlanProgressValues.phase4Done, ImplementationPlanProgressValues.phase4Total, ImplementationPlanProgressValues.phase4Pending)
        case 5: return (ImplementationPlanProgressValues.phase5Done, ImplementationPlanProgressValues.phase5Total, ImplementationPlanProgressValues.phase5Pending)
        case 6: return (ImplementationPlanProgressValues.phase6Done, ImplementationPlanProgressValues.phase6Total, ImplementationPlanProgressValues.phase6Pending)
        case 7: return (ImplementationPlanProgressValues.phase7Done, ImplementationPlanProgressValues.phase7Total, ImplementationPlanProgressValues.phase7Pending)
        case 8: return (ImplementationPlanProgressValues.phase8Done, ImplementationPlanProgressValues.phase8Total, ImplementationPlanProgressValues.phase8Pending)
        case 9: return (ImplementationPlanProgressValues.phase9Done, ImplementationPlanProgressValues.phase9Total, ImplementationPlanProgressValues.phase9Pending)
        default:
            return (0, 0, 0)
        }
    }
}

private struct ImplementationPlanDashboardChecklistSheet: View {
    let items: [ImplementationPlanDashboardChecklistLine]
    let navigationTitle: String

    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            List(items) { line in
                VStack(alignment: .leading, spacing: 4) {
                    Text(line.context)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(line.title)
                        .font(.body)
                }
                .padding(.vertical, 4)
            }
            .listStyle(.plain)
            .navigationTitle(navigationTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_close")) {
                        dismiss()
                    }
                }
            }
        }
    }
}
