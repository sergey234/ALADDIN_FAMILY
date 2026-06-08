import SwiftUI

// MARK: - Variant

/// Storm mesh presets — см. `docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md` §3.
enum StormMeshVariant: String, CaseIterable, Identifiable {
    case hub
    case family
    case shield
    case grow
    case growWarm
    case warm
    case premium
    case ai
    case data
    case neutral
    case legal

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .hub: return "Hub"
        case .family: return "Family"
        case .shield: return "Shield"
        case .grow: return "Grow"
        case .growWarm: return "Grow Warm"
        case .warm: return "Warm"
        case .premium: return "Premium"
        case .ai: return "AI"
        case .data: return "Data"
        case .neutral: return "Neutral"
        case .legal: return "Legal"
        }
    }

    fileprivate var baseColor: Color {
        switch self {
        case .legal: return .stormBase
        case .growWarm: return .stormGrowWarmBase
        default: return .stormDeep
        }
    }

    /// Light Premium: scrim на stormDeep, не stormBase-чернота.
    fileprivate var scrimColor: Color {
        switch self {
        case .legal: return .stormBase
        default: return .stormDeep
        }
    }

    fileprivate var bottomScrimOpacity: CGFloat {
        switch self {
        case .legal: return 0
        default: return 0.28
        }
    }

    fileprivate var scrimStartY: CGFloat {
        switch self {
        case .legal: return 0.35
        default: return 0.68
        }
    }

    fileprivate var showsBlobs: Bool {
        self != .legal
    }

    fileprivate var showsAtmosphereLayer: Bool {
        switch self {
        case .hub, .premium, .family, .shield: return true
        default: return false
        }
    }
}

// MARK: - Blob model

private struct StormMeshBlobSpec {
    let color: Color
    let opacity: CGFloat
    let diameter: CGFloat
    let x: CGFloat
    let y: CGFloat
}

// MARK: - Background

/// Тёмный mesh-фон: 2–3 blur-blob + нижний scrim. Без анимации.
struct StormMeshBackground: View {
    let variant: StormMeshVariant

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            variant.baseColor

            if variant.showsAtmosphereLayer {
                atmosphereLayer
            }

            if variant.showsBlobs, !reduceMotion {
                blobLayer
            } else if variant.showsAtmosphereLayer, reduceMotion {
                reduceMotionLayer
            }

            if variant.bottomScrimOpacity > 0 {
                LinearGradient(
                    colors: [.clear, variant.scrimColor.opacity(variant.bottomScrimOpacity)],
                    startPoint: UnitPoint(x: 0.5, y: variant.scrimStartY),
                    endPoint: .bottom
                )
            }
        }
        .ignoresSafeArea()
        .accessibilityHidden(true)
    }

    @ViewBuilder
    private var atmosphereLayer: some View {
        switch variant {
        case .hub:
            stormWash(
                indigo: 0.32,
                gold: 0.14,
                violet: 0.10,
                goldTrailing: true
            )
        case .premium:
            stormWash(
                indigo: 0.24,
                gold: 0.20,
                violet: 0.12,
                goldTrailing: true
            )
        case .family:
            stormWash(
                indigo: 0.26,
                gold: 0.16,
                violet: 0.18,
                goldTrailing: false
            )
        case .shield:
            stormWash(
                indigo: 0.30,
                gold: 0.08,
                violet: 0.08,
                goldTrailing: false,
                lightning: 0.10
            )
        default:
            EmptyView()
        }
    }

    private func stormWash(
        indigo: CGFloat,
        gold: CGFloat,
        violet: CGFloat,
        goldTrailing: Bool,
        lightning: CGFloat = 0
    ) -> some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color.stormIndigo.opacity(indigo),
                    Color.stormDeep.opacity(0.55),
                    Color.stormDeep
                ],
                startPoint: .topLeading,
                endPoint: UnitPoint(x: 0.45, y: 0.55)
            )
            if goldTrailing {
                LinearGradient(
                    colors: [Color.goldPrimary.opacity(gold), Color.clear],
                    startPoint: .topTrailing,
                    endPoint: UnitPoint(x: 0.55, y: 0.35)
                )
            } else {
                LinearGradient(
                    colors: [Color.goldPrimary.opacity(gold), Color.clear],
                    startPoint: .top,
                    endPoint: UnitPoint(x: 0.5, y: 0.4)
                )
            }
            if lightning > 0 {
                LinearGradient(
                    colors: [Color.stormLightning.opacity(lightning), Color.clear],
                    startPoint: UnitPoint(x: 0.7, y: 0.05),
                    endPoint: UnitPoint(x: 0.5, y: 0.35)
                )
            }
            LinearGradient(
                colors: [Color.clear, Color.stormViolet.opacity(violet)],
                startPoint: UnitPoint(x: 0.5, y: 0.55),
                endPoint: .bottom
            )
        }
        .allowsHitTesting(false)
    }

    private var reduceMotionLayer: some View {
        LinearGradient(
            colors: [
                Color.stormIndigo.opacity(0.26),
                Color.stormDeep,
                Color.stormViolet.opacity(0.12)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .overlay(alignment: .topTrailing) {
            Color.goldPrimary.opacity(variant == .premium ? 0.20 : 0.14)
                .frame(width: 220, height: 180)
                .offset(x: 40, y: -20)
        }
        .allowsHitTesting(false)
    }

    @ViewBuilder
    private var blobLayer: some View {
        GeometryReader { proxy in
            let w = proxy.size.width
            let h = proxy.size.height
            ZStack {
                ForEach(Array(blobs.enumerated()), id: \.offset) { _, blob in
                    Circle()
                        .fill(blob.color.opacity(blob.opacity))
                        .frame(width: blob.diameter, height: blob.diameter)
                        .blur(radius: 80)
                        .position(
                            x: w * blob.x,
                            y: h * blob.y
                        )
                }
            }
        }
        .allowsHitTesting(false)
    }

    private var blobs: [StormMeshBlobSpec] {
        switch variant {
        // Main / Support — «Золотой просвет» v1.2: видимая гроза (indigo/lightning), не stormCloud на stormDeep.
        case .hub:
            return [
                .init(color: .stormIndigo, opacity: 0.38, diameter: 360, x: 0.22, y: 0.14),
                .init(color: .stormLightning, opacity: 0.20, diameter: 240, x: 0.58, y: 0.12),
                .init(color: .goldPrimary, opacity: 0.28, diameter: 280, x: 0.86, y: 0.11),
                .init(color: .stormViolet, opacity: 0.14, diameter: 300, x: 0.48, y: 0.78)
            ]
        case .family:
            return [
                .init(color: .stormViolet, opacity: 0.26, diameter: 300, x: 0.50, y: 0.40),
                .init(color: .goldPrimary, opacity: 0.20, diameter: 220, x: 0.82, y: 0.10),
                .init(color: .stormIndigo, opacity: 0.22, diameter: 280, x: 0.18, y: 0.14)
            ]
        case .shield:
            return [
                .init(color: .stormIndigo, opacity: 0.32, diameter: 300, x: 0.22, y: 0.14),
                .init(color: .stormLightning, opacity: 0.22, diameter: 240, x: 0.72, y: 0.18),
                .init(color: .stormCloud, opacity: 0.14, diameter: 260, x: 0.78, y: 0.35)
            ]
        case .grow:
            return [
                .init(color: .stormViolet, opacity: 0.24, diameter: 280, x: 0.35, y: 0.28),
                .init(color: .stormTeal, opacity: 0.22, diameter: 260, x: 0.72, y: 0.50),
                .init(color: .goldPrimary, opacity: 0.14, diameter: 200, x: 0.85, y: 0.11)
            ]
        case .growWarm:
            return [
                .init(color: .stormTeal, opacity: 0.28, diameter: 300, x: 0.40, y: 0.38),
                .init(color: .goldPrimary, opacity: 0.14, diameter: 200, x: 0.78, y: 0.12),
                .init(color: .stormViolet, opacity: 0.14, diameter: 240, x: 0.80, y: 0.25)
            ]
        case .warm:
            return [
                .init(color: .goldWarm, opacity: 0.22, diameter: 260, x: 0.65, y: 0.16),
                .init(color: .goldPrimary, opacity: 0.12, diameter: 180, x: 0.30, y: 0.10),
                .init(color: .stormViolet, opacity: 0.12, diameter: 220, x: 0.25, y: 0.68)
            ]
        case .premium:
            return [
                .init(color: .goldPrimary, opacity: 0.30, diameter: 300, x: 0.74, y: 0.12),
                .init(color: .stormIndigo, opacity: 0.22, diameter: 260, x: 0.24, y: 0.14),
                .init(color: .stormLightning, opacity: 0.14, diameter: 200, x: 0.55, y: 0.22),
                .init(color: .stormViolet, opacity: 0.12, diameter: 280, x: 0.48, y: 0.72)
            ]
        case .ai:
            return [
                .init(color: .stormLightning, opacity: 0.26, diameter: 280, x: 0.55, y: 0.18),
                .init(color: .goldPrimary, opacity: 0.16, diameter: 200, x: 0.20, y: 0.10),
                .init(color: .stormIndigo, opacity: 0.18, diameter: 240, x: 0.75, y: 0.30)
            ]
        case .data:
            return [
                .init(color: .stormIndigo, opacity: 0.24, diameter: 260, x: 0.25, y: 0.22),
                .init(color: .stormLightning, opacity: 0.18, diameter: 220, x: 0.75, y: 0.38),
                .init(color: .goldPrimary, opacity: 0.12, diameter: 180, x: 0.50, y: 0.75)
            ]
        case .neutral:
            return [
                .init(color: .stormIndigo, opacity: 0.14, diameter: 280, x: 0.30, y: 0.20),
                .init(color: .goldPrimary, opacity: 0.08, diameter: 200, x: 0.80, y: 0.12)
            ]
        case .legal:
            return []
        }
    }
}

// MARK: - Preview grid

#if DEBUG
struct StormMeshBackground_Previews: PreviewProvider {
    static var previews: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(StormMeshVariant.allCases) { variant in
                    ZStack {
                        StormMeshBackground(variant: variant)
                        VStack {
                            Text(variant.displayName)
                                .font(.caption.bold())
                                .foregroundColor(.white)
                            Spacer()
                        }
                        .padding(8)
                    }
                    .frame(height: 200)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.15), lineWidth: 1)
                    )
                }
            }
            .padding()
        }
        .background(Color.black)
        .previewDisplayName("Storm Mesh — all variants")
    }
}
#endif

// MARK: - Batch 8 ASO hub light slides (export via Xcode Preview)

#if DEBUG
enum ASOHubLightSlide: Int, CaseIterable, Identifiable {
    case familyProtection = 1
    case parentalControl
    case childLearning
    case aiParents
    case devicesPanel
    case tryFree

    var id: Int { rawValue }

    var title: String {
        switch self {
        case .familyProtection: return "Защита семьи 24/7"
        case .parentalControl: return "Умный родконтроль"
        case .childLearning: return "Обучение без страха"
        case .aiParents: return "AI для родителей"
        case .devicesPanel: return "Все устройства — одна панель"
        case .tryFree: return "Попробуйте бесплатно"
        }
    }

    var subtitle: String {
        switch self {
        case .familyProtection: return "Main · Storm hub v1.2"
        case .parentalControl: return "Parental · grow mesh"
        case .childLearning: return "Child · growWarm"
        case .aiParents: return "AI Assistant · ai mesh"
        case .devicesPanel: return "Devices · shield mesh"
        case .tryFree: return "Tariffs · premium mesh"
        }
    }

    var meshVariant: StormMeshVariant {
        switch self {
        case .familyProtection: return .hub
        case .parentalControl: return .grow
        case .childLearning: return .growWarm
        case .aiParents: return .ai
        case .devicesPanel: return .shield
        case .tryFree: return .premium
        }
    }

    var heroEmoji: String {
        switch self {
        case .familyProtection: return "🛡️"
        case .parentalControl: return "👨‍👩‍👧"
        case .childLearning: return "✨"
        case .aiParents: return "🤖"
        case .devicesPanel: return "📱"
        case .tryFree: return "⭐"
        }
    }
}

struct ASOHubLightSlideView: View {
    let slide: ASOHubLightSlide

    var body: some View {
        ZStack {
            StormMeshBackground(variant: slide.meshVariant)

            VStack(spacing: 20) {
                Spacer()
                Text(slide.heroEmoji)
                    .font(.system(size: 72))
                Text(slide.title)
                    .font(.title.bold())
                    .multilineTextAlignment(.center)
                    .foregroundColor(.white)
                    .padding(.horizontal, 24)
                Text(slide.subtitle)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
                Spacer()
                Text("ALADDIN · hub light premium")
                    .font(.caption2.bold())
                    .foregroundColor(Color.secondaryGold)
                    .padding(.bottom, 32)
            }
        }
        .frame(width: 393, height: 852)
    }
}

struct ASOHubLightSlides_Previews: PreviewProvider {
    static var previews: some View {
        TabView {
            ForEach(ASOHubLightSlide.allCases) { slide in
                ASOHubLightSlideView(slide: slide)
                    .previewDisplayName("ASO \(slide.rawValue)")
            }
        }
        .tabViewStyle(.page)
        .previewDisplayName("Batch 8 — ASO 6 slides hub light")
    }
}
#endif
