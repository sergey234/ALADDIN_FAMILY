import SwiftUI

/// P1.6 — shared family checklist (AnyList-lite).
struct FamilyListScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var items: [FamilyListItem] = []
    @State private var draftText = ""
    @State private var isSyncing = false
    @State private var syncNote: String?

    var body: some View {
        ZStack {
            StormMeshBackground(variant: .neutral).ignoresSafeArea()
            VStack(spacing: 0) {
                header
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizationManager.localized("family_list_subtitle"))
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.85))

                        HStack(spacing: 8) {
                            TextField(
                                localizationManager.localized("family_list_placeholder"),
                                text: $draftText
                            )
                            .textFieldStyle(.roundedBorder)
                            Button {
                                addItem()
                            } label: {
                                Image(systemName: "plus.circle.fill")
                                    .font(.title2)
                            }
                            .disabled(draftText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                            .accessibilityIdentifier("family_list_add")
                        }

                        if items.isEmpty {
                            Text(localizationManager.localized("family_list_empty"))
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.6))
                                .padding(.vertical, 20)
                        } else {
                            ForEach(items) { item in
                                row(item)
                            }
                        }

                        if let syncNote {
                            Text(syncNote)
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.7))
                        }
                    }
                    .padding()
                }
            }
        }
        .foregroundColor(.white)
        .navigationBarHidden(true)
        .onAppear {
            items = FamilyListStore.loadLocal()
            mergeVoiceDraft()
            Task { await refreshFromServer() }
        }
        .accessibilityIdentifier("family_list_screen")
    }

    private var header: some View {
        HStack {
            Button {
                navigationManager.goBackToPreviousScreen(reason: "family_list_back")
            } label: {
                Image(systemName: "chevron.left")
                    .font(.body.weight(.semibold))
            }
            Text(localizationManager.localized("family_list_title"))
                .font(.headline.bold())
            Spacer()
            if isSyncing {
                ProgressView()
            } else {
                Button {
                    Task { await pushToServer() }
                } label: {
                    Image(systemName: "arrow.triangle.2.circlepath")
                }
                .accessibilityLabel(localizationManager.localized("family_list_sync"))
            }
        }
        .padding()
    }

    private func row(_ item: FamilyListItem) -> some View {
        HStack(spacing: 10) {
            Button {
                toggle(item)
            } label: {
                Image(systemName: item.checked ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(item.checked ? Color(hex: "34D399") : .white.opacity(0.6))
            }
            .buttonStyle(.plain)
            Text(item.text)
                .font(.subheadline)
                .foregroundColor(item.checked ? .white.opacity(0.45) : .white)
            Spacer()
            Button(role: .destructive) {
                items.removeAll { $0.id == item.id }
                persistAndPush()
            } label: {
                Image(systemName: "trash")
                    .font(.caption)
            }
            .buttonStyle(.plain)
        }
        .padding(10)
        .background(Color.white.opacity(0.08))
        .cornerRadius(10)
    }

    private func addItem() {
        let text = draftText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        items.insert(FamilyListItem(text: text), at: 0)
        draftText = ""
        persistAndPush()
    }

    private func toggle(_ item: FamilyListItem) {
        guard let idx = items.firstIndex(where: { $0.id == item.id }) else { return }
        items[idx].checked.toggle()
        if items[idx].checked {
            let checkedCount = items.filter(\.checked).count
            _ = FamilyListStore.rewardIfNeeded(for: items[idx], checkedCount: checkedCount)
            HapticFeedback.impact(.light)
        }
        persistAndPush()
    }

    private func mergeVoiceDraft() {
        let lines = FamilyListStore.consumeVoiceDraft()
        guard !lines.isEmpty else { return }
        let existing = Set(items.map { $0.text.lowercased() })
        for line in lines where !existing.contains(line.lowercased()) {
            items.insert(FamilyListItem(text: line), at: 0)
        }
        FamilyListStore.saveLocal(items)
    }

    private func persistAndPush() {
        FamilyListStore.saveLocal(items)
        Task { await pushToServer() }
    }

    private func refreshFromServer() async {
        isSyncing = true
        defer { isSyncing = false }
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            APIService.shared.getFamilySharedList { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let remote):
                        if !remote.isEmpty || items.isEmpty {
                            items = remote
                            FamilyListStore.saveLocal(items)
                        }
                        syncNote = nil
                    case .failure:
                        syncNote = localizationManager.localized("family_list_offline")
                    }
                    cont.resume()
                }
            }
        }
    }

    private func pushToServer() async {
        isSyncing = true
        defer { isSyncing = false }
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            APIService.shared.setFamilySharedList(items: items) { result in
                DispatchQueue.main.async {
                    if case .failure = result {
                        syncNote = localizationManager.localized("family_list_offline")
                    } else {
                        syncNote = localizationManager.localized("family_list_synced")
                    }
                    cont.resume()
                }
            }
        }
    }
}
