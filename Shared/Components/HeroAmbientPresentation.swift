import SwiftUI
import UIKit

#if canImport(Lottie)
import Lottie
#endif

// MARK: - Asset / behavior contract (для дизайна и каталога)
//
// Lottie JSON в бандле: `OnboardingHero_00` … `OnboardingHero_07`, `MainHero_ambient`
// Растровый fallback (2x/3x в Asset Catalog): те же имена как image set.
// Опционально iOS 17+: `MainHero_ambient.usdz` в каталоге / бандле — только если есть ресурс.
// USDZ не является единственным путём: при отсутствии файла или iOS < 17 показывается Lottie либо Image.

// MARK: - Slots & presentation

/// Слот героя: шаг 0 (язык), контент онбординга (0…6 = семь страниц после языка), главный экран.
enum HeroSlot: Equatable {
    case onboardingLanguage
    case onboardingContent(pageIndex: Int)
    case mainDashboard

    /// Индекс 0…7 для имени ассета (0 = язык, 1…7 = контент по сюжету; главный — отдельное имя).
    var onboardingAssetIndex: Int? {
        switch self {
        case .onboardingLanguage:
            return 0
        case .onboardingContent(let i):
            return min(max(i + 1, 1), 7)
        case .mainDashboard:
            return nil
        }
    }
}

/// Режим движения: один «дорогой» слой — при `.staticOnly` или `.reduced` не крутим Lottie в цикле и не делаем parallax.
enum HeroMotionTier: Equatable {
    case full
    case reduced
    case staticOnly
}

enum HeroPresentation: Equatable {
    case lottieOrRaster(baseName: String, allowsParallax: Bool)
    case mainHero

    static func presentation(for slot: HeroSlot) -> HeroPresentation {
        switch slot {
        case .onboardingLanguage:
            return .lottieOrRaster(baseName: "OnboardingHero_00", allowsParallax: false)
        case .onboardingContent(let idx):
            let storyIndex = min(max(idx + 1, 1), 7)
            let name = String(format: "OnboardingHero_%02d", storyIndex)
            // Parallax только на «ИИ-спутник» (слайд контента index 1 → story 2)
            let parallax = (storyIndex == 2)
            return .lottieOrRaster(baseName: name, allowsParallax: parallax)
        case .mainDashboard:
            return .mainHero
        }
    }

    var baseNameForFallback: String {
        switch self {
        case .lottieOrRaster(let baseName, _):
            return baseName
        case .mainHero:
            return "MainHero_ambient"
        }
    }

    var allowsParallax: Bool {
        switch self {
        case .lottieOrRaster(_, let flag):
            return flag
        case .mainHero:
            return false
        }
    }

    /// Мягкая эмоциональная вуаль поверх иллюстрации (не заменяет локализованный текст).
    @ViewBuilder
    func emotionWashOverlay() -> some View {
        switch self {
        case .lottieOrRaster(let base, _):
            washForOnboarding(baseName: base)
        case .mainHero:
            LinearGradient(
                colors: [
                    Color(red: 0.45, green: 0.35, blue: 0.12).opacity(0.12),
                    Color.clear,
                    Color.indigo.opacity(0.1)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }

    private func washForOnboarding(baseName: String) -> LinearGradient {
        // Привязка к имени ассета (палитра сюжета); при смене имён — обновить здесь.
        let colors: [Color]
        switch baseName {
        case "OnboardingHero_00":
            colors = [Color(red: 0.95, green: 0.75, blue: 0.2).opacity(0.18), Color.indigo.opacity(0.12)]
        case "OnboardingHero_01":
            colors = [Color.cyan.opacity(0.14), Color.blue.opacity(0.1)]
        case "OnboardingHero_02":
            colors = [Color.blue.opacity(0.12), Color(red: 0.95, green: 0.8, blue: 0.35).opacity(0.1)]
        case "OnboardingHero_03":
            colors = [Color.purple.opacity(0.12), Color.pink.opacity(0.08)]
        case "OnboardingHero_04":
            colors = [Color.blue.opacity(0.16), Color.cyan.opacity(0.06)]
        case "OnboardingHero_05":
            colors = [Color.yellow.opacity(0.14), Color.orange.opacity(0.06)]
        case "OnboardingHero_06":
            colors = [Color.gray.opacity(0.12), Color.purple.opacity(0.1)]
        case "OnboardingHero_07":
            colors = [Color(red: 0.95, green: 0.75, blue: 0.2).opacity(0.15), Color.indigo.opacity(0.08)]
        default:
            colors = [Color.clear]
        }
        return LinearGradient(colors: colors + [Color.clear], startPoint: .top, endPoint: .bottom)
    }
}

enum HeroMotionPolicy {
    static func tier(
        reduceMotion: Bool,
        lowPowerMode: Bool,
        scenePhase: ScenePhase
    ) -> HeroMotionTier {
        if reduceMotion { return .staticOnly }
        if lowPowerMode { return .reduced }
        if scenePhase != .active { return .reduced }
        return .full
    }
}

// MARK: - Lottie (UIViewRepresentable; модуль Lottie из CocoaPods при сборке с Pods)

#if canImport(Lottie)
private struct HeroLottieRepresentable: UIViewRepresentable {
    let name: String
    let loopMode: LottieLoopMode
    let isPlaying: Bool

    func makeUIView(context: Context) -> LottieAnimationView {
        let view = LottieAnimationView()
        view.animation = LottieAnimation.named(name, bundle: .main, subdirectory: nil)
        view.contentMode = .scaleAspectFit
        view.loopMode = loopMode
        view.backgroundBehavior = .pauseAndRestore
        if isPlaying {
            view.play()
        } else {
            view.currentProgress = 0
            view.pause()
        }
        return view
    }

    func updateUIView(_ uiView: LottieAnimationView, context: Context) {
        if isPlaying {
            if !uiView.isAnimationPlaying {
                uiView.play()
            }
        } else {
            uiView.pause()
        }
    }
}
#endif

// MARK: - Bundle helpers

private enum HeroBundleResource {
    static func hasLottie(named name: String) -> Bool {
        Bundle.main.url(forResource: name, withExtension: "json") != nil
            || Bundle.main.url(forResource: name, withExtension: "lottie") != nil
    }

    static func hasRaster(named name: String) -> Bool {
        UIImage(named: name) != nil
    }

    static func hasUSDZ(named name: String) -> Bool {
        Bundle.main.url(forResource: name, withExtension: "usdz") != nil
    }
}

// MARK: - USDZ (iOS 17+)
// Подключение `Model3D` / RealityKit — отдельным шагом после добавления `.usdz` в каталог
// и проверки на устройстве (один «дорогой» слой: не комбинировать с Lottie в одном кадре).

// MARK: - Public layer

/// Декоративный фоновый герой: не перехватывает нажатия; для VoiceOver — декоративный элемент.
struct HeroAmbientLayerView: View {
    let slot: HeroSlot

    @Environment(\.scenePhase) private var scenePhase
    @Environment(\.accessibilityReduceMotion) private var accessibilityReduceMotion

    @State private var lowPowerMode = ProcessInfo.processInfo.isLowPowerModeEnabled

    private var presentation: HeroPresentation {
        HeroPresentation.presentation(for: slot)
    }

    private var motionTier: HeroMotionTier {
        HeroMotionPolicy.tier(
            reduceMotion: accessibilityReduceMotion,
            lowPowerMode: lowPowerMode,
            scenePhase: scenePhase
        )
    }

    private var shouldLoopLottie: Bool {
        motionTier == .full
    }

    private var lottieShouldPlay: Bool {
        motionTier == .full
    }

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            ZStack {
                presentation.emotionWashOverlay()
                    .allowsHitTesting(false)

                heroCore()
                    .frame(width: w, height: h)
                    .allowsHitTesting(false)

                // Лёгкий parallax двух слоёв только в full и если разрешено презентацией
                if presentation.allowsParallax, motionTier == .full {
                    parallaxAccent(in: geo.size)
                }
            }
            .frame(width: w, height: h)
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .onReceive(NotificationCenter.default.publisher(for: Notification.Name.NSProcessInfoPowerStateDidChange)) { _ in
            lowPowerMode = ProcessInfo.processInfo.isLowPowerModeEnabled
        }
    }

    @ViewBuilder
    private func heroCore() -> some View {
        let base = presentation.baseNameForFallback
        rasterOrLottie(baseName: base)
    }

    @ViewBuilder
    private func rasterOrLottie(baseName: String) -> some View {
        #if canImport(Lottie)
        if HeroBundleResource.hasLottie(named: baseName) {
            HeroLottieRepresentable(
                name: baseName,
                loopMode: shouldLoopLottie ? .loop : .playOnce,
                isPlaying: lottieShouldPlay
            )
        } else if HeroBundleResource.hasRaster(named: baseName) {
            Image(baseName)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            heroPlaceholderGradient()
        }
        #else
        if HeroBundleResource.hasRaster(named: baseName) {
            Image(baseName)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            heroPlaceholderGradient()
        }
        #endif
    }

    private func heroPlaceholderGradient() -> some View {
        RadialGradient(
            colors: [Color.secondaryGold.opacity(0.15), Color.clear],
            center: .center,
            startRadius: 20,
            endRadius: 180
        )
    }

    private func parallaxAccent(in size: CGSize) -> some View {
        ZStack {
            Circle()
                .fill(Color.white.opacity(0.04))
                .frame(width: size.width * 0.5, height: size.width * 0.5)
                .offset(x: size.width * 0.08, y: -size.height * 0.06)
            Circle()
                .fill(Color.blue.opacity(0.05))
                .frame(width: size.width * 0.35, height: size.width * 0.35)
                .offset(x: -size.width * 0.1, y: size.height * 0.04)
        }
        .allowsHitTesting(false)
    }
}

/// Вспомогательный модификатор: затемнение низа под нижние кнопки / safe area.
struct HeroBottomReadableGradient: View {
    var body: some View {
        LinearGradient(
            colors: [Color.clear, Color.black.opacity(0.45)],
            startPoint: .center,
            endPoint: .bottom
        )
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}
