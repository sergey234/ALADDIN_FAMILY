import SwiftUI

/// P1-07 — каталог косметики за trust + выбор наряда.
struct CompanionCosmeticsSection: View {
    let characterId: String
    let trustScore: Int
    @Binding var equippedCosmeticId: String

    @State private var items: [CompanionCosmeticItem] = []
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var isSaving = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Наряды героя")
                    .font(.headline)
                Spacer()
                Text("Доверие: \(trustScore)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            if isLoading {
                ProgressView()
            } else if let errorText {
                Text(errorText).font(.caption).foregroundStyle(.orange)
            } else if items.isEmpty {
                Text("Пока нет нарядов для этого героя.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                    ForEach(items) { item in
                        cosmeticCard(item)
                    }
                }
            }
        }
        .task(id: characterId) { await load() }
    }

    @ViewBuilder
    private func cosmeticCard(_ item: CompanionCosmeticItem) -> some View {
        let selected = equippedCosmeticId == item.id
        Button {
            Task { await select(item) }
        } label: {
            VStack(spacing: 6) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(item.unlocked ? Color.purple.opacity(0.15) : Color.gray.opacity(0.12))
                        .frame(height: 72)
                    Text(CompanionCosmeticVisuals.emoji(for: item.id))
                        .font(.title)
                        .opacity(item.unlocked ? 1 : 0.35)
                }
                Text(item.title)
                    .font(.caption.weight(.semibold))
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                if item.unlocked {
                    Text(selected ? "Надето" : "Надеть")
                        .font(.caption2)
                        .foregroundStyle(selected ? .green : .purple)
                } else {
                    Text("Уровень \(item.trustLevel)")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(8)
            .overlay(
                RoundedRectangle(cornerRadius: 14)
                    .stroke(selected ? Color.purple : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
        .disabled(!item.unlocked || isSaving)
    }

    private func load() async {
        isLoading = true
        errorText = nil
        defer { isLoading = false }
        do {
            let resp = try await CompanionAPIService.shared.fetchCosmetics(characterId: characterId)
            items = resp.cosmetics
            if !equippedCosmeticId.isEmpty,
               !items.contains(where: { $0.id == equippedCosmeticId && $0.unlocked }) {
                equippedCosmeticId = ""
            }
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func select(_ item: CompanionCosmeticItem) async {
        guard item.unlocked else { return }
        let next = equippedCosmeticId == item.id ? "" : item.id
        isSaving = true
        defer { isSaving = false }
        do {
            _ = try await CompanionAPIService.shared.updateEquippedCosmetic(
                characterId: characterId,
                cosmeticId: next
            )
            equippedCosmeticId = next
            HapticFeedback.impact(.light)
        } catch {
            errorText = error.localizedDescription
        }
    }
}

enum CompanionCosmeticVisuals {
    static func emoji(for cosmeticId: String) -> String {
        switch cosmeticId {
        case "horn_glow_soft": return "✨"
        case "horn_glow_gold": return "🌟"
        case "mane_sparkle": return "💫"
        case "hoodie_star_patch": return "⭐"
        case "lamp_pin_gold": return "🪔"
        default: return "🎁"
        }
    }

    static func overlaySymbol(for cosmeticId: String) -> String? {
        switch cosmeticId {
        case "horn_glow_soft", "horn_glow_gold": return "sparkle"
        case "mane_sparkle": return "wand.and.stars"
        case "hoodie_star_patch": return "star.fill"
        case "lamp_pin_gold": return "lightbulb.fill"
        default: return nil
        }
    }

    static func ringColors(for cosmeticId: String) -> [Color] {
        switch cosmeticId {
        case "horn_glow_gold", "lamp_pin_gold":
            return [.yellow, .orange]
        case "horn_glow_soft":
            return [.purple.opacity(0.6), .pink.opacity(0.5)]
        case "mane_sparkle":
            return [.cyan, .purple]
        case "hoodie_star_patch":
            return [.blue, .indigo]
        default:
            return []
        }
    }
}
