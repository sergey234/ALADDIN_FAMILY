import SwiftUI

/// Зеркало `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` (275 строк) для отслеживания в DEBUG.
/// Генерация: `python3 scripts/generate_plan_item_275_mirror.py`
struct PlanItem275CatalogWorkbenchCard: View {
    private static let struckOpenIdsKey = "plan_item_275_struck_open_ids_v1"

    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showOpenSheet = false
    @State private var showDoneSheet = false
    @State private var struckOpenIds: Set<String> = []

    private var loc: LocalizationManager { localizationManager }

    private var openLines: [PlanItem275CatalogLine] { PlanItem275CatalogMirror.openLines }
    private var doneLines: [PlanItem275CatalogLine] { PlanItem275CatalogMirror.doneOnlyLines }
    private var validOpenIds: Set<String> { Set(openLines.map(\.id)) }
    private var notStruckOpen: Int { openLines.filter { !struckOpenIds.contains($0.id) }.count }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "list.bullet.rectangle")
                    .foregroundColor(.orange)
                Text(loc.localized("plan_275_panel_title"))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
            }

            Text(loc.localized("plan_275_panel_subtitle"))
                .font(.caption)
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            Text(String(format: loc.localized("plan_275_panel_updated_fmt"), PlanItem275CatalogMirror.generatedAtUTC))
                .font(.caption2)
                .foregroundColor(.secondary)

            HStack(spacing: 8) {
                countChip(title: "DONE", value: PlanItem275CatalogMirror.doneCount, color: .green)
                countChip(title: "PART", value: PlanItem275CatalogMirror.partialCount, color: .orange)
                countChip(title: "TODO", value: PlanItem275CatalogMirror.todoCount, color: .red)
            }

            Text(String(format: loc.localized("plan_275_local_tick_fmt"), notStruckOpen, openLines.count))
                .font(.subheadline)
                .foregroundColor(.textPrimary)

            Text(loc.localized("plan_275_strike_hint"))
                .font(.caption2)
                .foregroundColor(.secondary)

            Text(loc.localized("plan_275_regenerate_hint"))
                .font(.caption2)
                .foregroundColor(.secondary)

            // Первые открытые (короткий inline)
            Text(loc.localized("plan_275_open_inline_header"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)
                .padding(.top, 4)

            ForEach(Array(openLines.prefix(6))) { line in
                openRow(line)
            }

            HStack(spacing: 12) {
                Button {
                    showOpenSheet = true
                } label: {
                    Text(String(format: loc.localized("plan_275_open_sheet_button_fmt"), openLines.count))
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.orange)

                Button {
                    showDoneSheet = true
                } label: {
                    Text(String(format: loc.localized("plan_275_done_sheet_button_fmt"), doneLines.count))
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
            .padding(.top, 4)
        }
        .padding(Spacing.m)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.orange.opacity(0.25), lineWidth: 1)
        )
        .onAppear(perform: reconcileStruck)
        .sheet(isPresented: $showOpenSheet) {
            Plan275CatalogListSheet(titleKey: "plan_275_sheet_open_title", lines: openLines)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDoneSheet) {
            Plan275CatalogListSheet(titleKey: "plan_275_sheet_done_title", lines: doneLines)
                .environmentObject(localizationManager)
        }
    }

    private func countChip(title: String, value: Int, color: Color) -> some View {
        VStack(spacing: 2) {
            Text("\(value)")
                .font(.title3.weight(.bold))
                .foregroundColor(color)
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 6)
        .background(Color.secondary.opacity(0.06))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private func openRow(_ line: PlanItem275CatalogLine) -> some View {
        let struck = struckOpenIds.contains(line.id)
        return HStack(alignment: .top, spacing: 10) {
            Button {
                toggleStruck(line.id)
            } label: {
                Image(systemName: struck ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(struck ? .green : .secondary)
            }
            .buttonStyle(.plain)
            VStack(alignment: .leading, spacing: 2) {
                Text("\(line.itemId) · \(line.wave)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(line.planTitle)
                    .font(.subheadline)
                    .strikethrough(struck, color: .secondary)
                    .foregroundColor(.textPrimary)
            }
        }
    }

    private func reconcileStruck() {
        var s = Self.loadStruck()
        s = s.intersection(validOpenIds)
        struckOpenIds = s
        Self.saveStruck(s)
    }

    private func toggleStruck(_ id: String) {
        if struckOpenIds.contains(id) {
            struckOpenIds.remove(id)
        } else {
            struckOpenIds.insert(id)
        }
        Self.saveStruck(struckOpenIds)
    }

    private static func loadStruck() -> Set<String> {
        guard let d = UserDefaults.standard.data(forKey: struckOpenIdsKey),
              let a = try? JSONDecoder().decode([String].self, from: d) else { return [] }
        return Set(a)
    }

    private static func saveStruck(_ s: Set<String>) {
        if let d = try? JSONEncoder().encode(Array(s).sorted()) {
            UserDefaults.standard.set(d, forKey: struckOpenIdsKey)
        }
    }

}

// MARK: - Full list sheet

private struct Plan275CatalogListSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    let titleKey: String
    let lines: [PlanItem275CatalogLine]

    var body: some View {
        NavigationView {
            List(lines) { line in
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(line.status.rawValue)
                            .font(.caption2.weight(.semibold))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(rowStatusBackground(line.status))
                            .clipShape(Capsule())
                        Text(line.wave)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                        Spacer()
                        Text(line.itemId)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    Text(line.planTitle)
                        .font(.body)
                    Text(line.categoryId)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 4)
            }
            .listStyle(.plain)
            .navigationTitle(localizationManager.localized(titleKey))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_close")) { dismiss() }
                }
            }
        }
    }

    private func rowStatusBackground(_ s: PlanItem275Status) -> Color {
        switch s {
        case .done: return Color.green.opacity(0.2)
        case .partial: return Color.orange.opacity(0.2)
        case .todo: return Color.red.opacity(0.15)
        }
    }
}
