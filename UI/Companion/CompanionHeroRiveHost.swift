import SwiftUI
import UIKit

/// P1-08 / HERO-3-08 — хост: bundled `.riv` + RiveRuntime (если подключён).
enum CompanionHeroRiveHost {
    private static let masterImageCache = NSCache<NSString, UIImage>()
    /// Placeholder `.riv` из репо ~15 KB; production export обычно &gt; 25 KB.
    static let productionRivMinBytes: Int = 25_000

    /// Симулятор iOS 15.x: известные падения Rive/Metal (`currentDrawable`, sampler binding). QA Rive — на device.
    static var isSimulatorIOS15MetalUnstable: Bool {
        #if targetEnvironment(simulator)
        if #available(iOS 16.0, *) { return false }
        return true
        #else
        return false
        #endif
    }

    /// Production `.riv` (не placeholder) в бандле.
    static func isProductionRiv(characterId: String) -> Bool {
        guard let url = bundledRivURL(characterId: characterId) else { return false }
        let size = (try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
        return size >= productionRivMinBytes
    }

    /// PNG master 360×480 пока `.riv` ещё placeholder (HERO-3-07).
    static func shouldUseRasterMaster(characterId: String) -> Bool {
        guard !isProductionRiv(characterId: characterId) else { return false }
        return bundledMasterUIImage(characterId: characterId) != nil
    }

    /// Можно ли включать RiveViewModel (production `.riv` + среда без Metal-крашей).
    static func shouldUseRiveRuntime(characterId: String) -> Bool {
        guard isProductionRiv(characterId: characterId) else { return false }
        guard !isSimulatorIOS15MetalUnstable else { return false }
        return true
    }

    static func rivBaseName(characterId: String) -> String {
        switch characterId {
        case "aladdin": return "aladdin"
        case "genie": return "genie"
        default: return "unicorn"
        }
    }

    static func hasBundledRiv(characterId: String) -> Bool {
        bundledRivURL(characterId: characterId) != nil
    }

    /// `Resources/Companion/*.riv` копируется в бандл как подпапка `Companion/`.
    static func bundledRivURL(characterId: String) -> URL? {
        let name = rivBaseName(characterId: characterId)
        return Bundle.main.url(forResource: name, withExtension: "riv", subdirectory: "Companion")
            ?? Bundle.main.url(forResource: name, withExtension: "riv")
    }

    static func bundledMasterUIImage(characterId: String) -> UIImage? {
        let name = "\(rivBaseName(characterId: characterId))_master"
        let cacheKey = NSString(string: name)
        if let cached = masterImageCache.object(forKey: cacheKey) {
            return cached
        }
        guard let url = Bundle.main.url(forResource: name, withExtension: "png", subdirectory: "Companion")
            ?? Bundle.main.url(forResource: name, withExtension: "png") else {
            return nil
        }
        guard let image = UIImage(contentsOfFile: url.path) else {
            return nil
        }
        masterImageCache.setObject(image, forKey: cacheKey)
        return image
    }

    #if canImport(RiveRuntime)
    static func makeRiveViewModel(characterId: String) -> RiveViewModel {
        let name = rivBaseName(characterId: characterId)
        if let url = bundledRivURL(characterId: characterId) {
            return RiveViewModel(
                webURL: url.absoluteString,
                stateMachineName: nil,
                fit: .contain,
                alignment: .center,
                autoPlay: true
            )
        }
        return RiveViewModel(
            fileName: name,
            extension: ".riv",
            in: .main,
            alignment: .center,
            autoPlay: true
        )
    }

    /// Rive iOS SDK: `mouth_open` — Number; эмоция — trigger (`idle`, `happy`, …).
    static func applyRiveInputs(to viewModel: RiveViewModel, emotion: CompanionHeroEmotion, mouthOpen: CGFloat) {
        viewModel.setInput("mouth_open", value: Float(mouthOpen))
        viewModel.triggerInput(CompanionHeroRiveMapping.riveStateName(for: emotion))
    }
    #endif
}

#if canImport(RiveRuntime)
import RiveRuntime

struct CompanionHeroRiveRuntimeView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    let lipSyncPhase: CGFloat
    let stageStyle: CompanionHeroLayout.StageStyle
    let stageSize: CGSize

    @StateObject private var viewModel: RiveViewModel
    @Environment(\.scenePhase) private var scenePhase
    @State private var isVisible = false

    init(
        characterId: String,
        emotion: CompanionHeroEmotion,
        lipSyncPhase: CGFloat,
        stageStyle: CompanionHeroLayout.StageStyle = .hubThumbnail,
        stageSize: CGSize = CGSize(
            width: CompanionHeroLayout.hubThumbnailDiameterPt,
            height: CompanionHeroLayout.hubThumbnailDiameterPt
        )
    ) {
        self.characterId = characterId
        self.emotion = emotion
        self.lipSyncPhase = lipSyncPhase
        self.stageStyle = stageStyle
        self.stageSize = stageSize
        _viewModel = StateObject(
            wrappedValue: CompanionHeroRiveHost.makeRiveViewModel(characterId: characterId)
        )
    }

    var body: some View {
        Group {
            if shouldRenderRive {
                TimelineView(.animation(minimumInterval: 1 / 30)) { timeline in
                    let t = timeline.date.timeIntervalSinceReferenceDate
                    let lipActive = emotion == .speaking || lipSyncPhase > 0
                    let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
                    rivStage(mouthOpen: mouthOpen, frameIndex: Int(t * 30))
                }
            } else {
                // Если `CAMetalLayer.currentDrawable == nil` (view не в окне/в фоне/нулевой размер),
                // Rive внутри может упасть. Безопаснее пропустить кадр, чем падать.
                Color.clear
                    .frame(width: stageSize.width, height: stageSize.height)
            }
        }
        .onAppear { isVisible = true }
        .onDisappear { isVisible = false }
        .onChange(of: scenePhase) { phase in
            if phase == .active {
                isVisible = true
            } else {
                isVisible = false
            }
        }
    }

    private var shouldRenderRive: Bool {
        guard isVisible else { return false }
        guard scenePhase == .active else { return false }
        guard stageSize.width > 1, stageSize.height > 1 else { return false }
        guard !CompanionHeroRiveHost.isSimulatorIOS15MetalUnstable else { return false }
        return true
    }

    @ViewBuilder
    private func rivStage(mouthOpen: CGFloat, frameIndex: Int) -> some View {
        let content = ZStack {
            viewModel.view()
            CompanionHeroRiveInputsSync(
                viewModel: viewModel,
                emotion: emotion,
                mouthOpen: mouthOpen,
                frameIndex: frameIndex
            )
        }
        .frame(width: stageSize.width, height: stageSize.height)
        switch stageStyle {
        case .hubThumbnail:
            content.clipShape(Circle())
        case .conversationFullBody:
            content.clipShape(
                RoundedRectangle(cornerRadius: CompanionHeroLayout.stageCornerRadius, style: .continuous)
            )
        }
    }
}

/// Проброс `emotion` + `mouth_open` на каждый кадр TimelineView (30 fps).
private struct CompanionHeroRiveInputsSync: View {
    let viewModel: RiveViewModel
    let emotion: CompanionHeroEmotion
    let mouthOpen: CGFloat
    let frameIndex: Int

    var body: some View {
        Color.clear
            .frame(width: 0, height: 0)
            .task(id: "\(emotion.rawValue)-\(frameIndex)") { sync() }
    }

    private func sync() {
        CompanionHeroRiveHost.applyRiveInputs(
            to: viewModel,
            emotion: emotion,
            mouthOpen: mouthOpen
        )
    }
}
#endif
