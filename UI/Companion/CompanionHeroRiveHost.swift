import SwiftUI
import UIKit

/// P1-08 / HERO-3-08 — хост: bundled `.riv` + RiveRuntime (если подключён).
enum CompanionHeroRiveHost {
    private static let masterImageCache = NSCache<NSString, UIImage>()
    /// Placeholder `.riv` из репо ~15 KB; production export обычно &gt; 25 KB.
    static let productionRivMinBytes: Int = 25_000
    /// iOS контракт (см. `scripts/companion_07_verify_unicorn_riv.py`).
    static let stateMachineName = "HeroSM"
    private static let artboardNameCandidates: [String?] = ["Hero360", nil]
    private static let mouthInputCandidates = ["mouth_open", "mouthOpen", "MouthOpen"]

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

    static func hasRasterFallback(characterId: String) -> Bool {
        bundledMasterUIImage(characterId: characterId) != nil
    }

    /// PNG master 360×480 когда Rive runtime недоступен (симулятор iOS 15) или `.riv` ещё placeholder.
    static func shouldUseRasterMaster(characterId: String) -> Bool {
        guard hasRasterFallback(characterId: characterId) else { return false }
        if shouldAttemptRiveRuntime(characterId: characterId) { return false }
        return true
    }

    /// Пробуем Rive, если production `.riv` в бандле и среда без известных Metal-крашей.
    static func shouldAttemptRiveRuntime(characterId: String) -> Bool {
        guard isProductionRiv(characterId: characterId) else { return false }
        guard !isSimulatorIOS15MetalUnstable else { return false }
        return true
    }

    static func shouldUseRiveRuntime(characterId: String) -> Bool {
        shouldAttemptRiveRuntime(characterId: characterId)
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
    /// Загрузка bundled `.riv` из `Companion/` (не `webURL` / `file://`).
    static func makeRiveViewModel(characterId: String) -> RiveViewModel? {
        guard let url = bundledRivURL(characterId: characterId),
              let data = try? Data(contentsOf: url) else {
            return nil
        }
        guard let file = try? RiveFile(data: data, loadCdn: false) else {
            return nil
        }

        for artboardName in artboardNameCandidates {
            if let viewModel = attemptViewModel(file: file, artboardName: artboardName, stateMachineName: stateMachineName) {
                return viewModel
            }
        }
        for artboardName in artboardNameCandidates {
            if let viewModel = attemptViewModel(file: file, artboardName: artboardName, stateMachineName: nil) {
                return viewModel
            }
        }
        return nil
    }

    private static func attemptViewModel(
        file: RiveFile,
        artboardName: String?,
        stateMachineName: String?
    ) -> RiveViewModel? {
        let model = RiveModel(riveFile: file)
        do {
            if let artboardName {
                try model.setArtboard(artboardName)
            } else {
                try model.setArtboard(nil)
            }
            if let stateMachineName {
                try model.setStateMachine(stateMachineName)
            } else {
                try model.setStateMachine(nil)
            }
        } catch {
            return nil
        }

        return RiveViewModel(
            model,
            stateMachineName: stateMachineName,
            fit: .contain,
            alignment: .center,
            autoPlay: true,
            artboardName: artboardName
        )
    }

    /// Rive iOS SDK: `mouth_open` — Number; эмоция — trigger (`idle`, `happy`, …).
    static func applyRiveInputs(to viewModel: RiveViewModel, emotion: CompanionHeroEmotion, mouthOpen: CGFloat) {
        applyMouthOpen(to: viewModel, mouthOpen: mouthOpen)
        fireEmotionTrigger(on: viewModel, emotion: emotion)
    }

    private static func applyMouthOpen(to viewModel: RiveViewModel, mouthOpen: CGFloat) {
        let value = Float(mouthOpen)
        for name in mouthInputCandidates where viewModel.numberInput(named: name) != nil {
            viewModel.setInput(name, value: value)
            return
        }
    }

    private static func fireEmotionTrigger(on viewModel: RiveViewModel, emotion: CompanionHeroEmotion) {
        let trigger = CompanionHeroRiveMapping.riveStateName(for: emotion)
        guard viewModel.riveModel?.stateMachine?.getTrigger(trigger) != nil else { return }
        viewModel.triggerInput(trigger)
    }
    #endif
}

#if canImport(RiveRuntime)
import RiveRuntime

@MainActor
final class CompanionRiveViewModelHolder: ObservableObject {
    let viewModel: RiveViewModel?

    init(characterId: String) {
        viewModel = CompanionHeroRiveHost.makeRiveViewModel(characterId: characterId)
    }
}

struct CompanionHeroRiveRuntimeView: View {
    let characterId: String
    let emotion: CompanionHeroEmotion
    let lipSyncPhase: CGFloat
    let stageStyle: CompanionHeroLayout.StageStyle
    var stageContentMode: CompanionHeroLayout.HeroStageContentMode = .fit
    let stageSize: CGSize

    @StateObject private var holder: CompanionRiveViewModelHolder
    @Environment(\.scenePhase) private var scenePhase
    @State private var isVisible = false

    init(
        characterId: String,
        emotion: CompanionHeroEmotion,
        lipSyncPhase: CGFloat,
        stageStyle: CompanionHeroLayout.StageStyle = .hubThumbnail,
        stageContentMode: CompanionHeroLayout.HeroStageContentMode = .fit,
        stageSize: CGSize = CGSize(
            width: CompanionHeroLayout.hubThumbnailDiameterPt,
            height: CompanionHeroLayout.hubThumbnailDiameterPt
        )
    ) {
        self.characterId = characterId
        self.emotion = emotion
        self.lipSyncPhase = lipSyncPhase
        self.stageStyle = stageStyle
        self.stageContentMode = stageContentMode
        self.stageSize = stageSize
        _holder = StateObject(wrappedValue: CompanionRiveViewModelHolder(characterId: characterId))
    }

    var body: some View {
        Group {
            if let viewModel = holder.viewModel {
                if shouldRenderRive {
                    TimelineView(.animation(minimumInterval: 1 / 30)) { timeline in
                        let t = timeline.date.timeIntervalSinceReferenceDate
                        let lipActive = emotion == .speaking || lipSyncPhase > 0
                        let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
                        rivStage(viewModel: viewModel, mouthOpen: mouthOpen, frameIndex: Int(t * 30))
                    }
                } else {
                    fallbackHeroView
                }
            } else {
                fallbackHeroView
            }
        }
        .onAppear { isVisible = true }
        .onDisappear { isVisible = false }
        .onChange(of: scenePhase) { phase in
            isVisible = (phase == .active)
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
    private var fallbackHeroView: some View {
        if CompanionHeroRiveHost.hasRasterFallback(characterId: characterId) {
            CompanionHeroRasterView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
        } else {
            CompanionHeroAnimatedView(
                characterId: characterId,
                emotion: emotion,
                lipSyncPhase: lipSyncPhase,
                stageStyle: stageStyle,
                stageContentMode: stageContentMode,
                stageSize: stageSize
            )
        }
    }

    @ViewBuilder
    private func rivStage(viewModel: RiveViewModel, mouthOpen: CGFloat, frameIndex: Int) -> some View {
        let fillScale: CGFloat = {
            guard stageStyle == .conversationFullBody, stageContentMode == .fillBottom else { return 1 }
            return CompanionHeroLayout.stageFillScaleFactor(stageSize: stageSize)
        }()
        let scaled = ZStack {
            viewModel.view()
            CompanionHeroRiveInputsSync(
                viewModel: viewModel,
                emotion: emotion,
                mouthOpen: mouthOpen,
                frameIndex: frameIndex
            )
        }
        .frame(width: stageSize.width, height: stageSize.height)
        .scaleEffect(fillScale, anchor: .bottom)
        .frame(width: stageSize.width, height: stageSize.height, alignment: .bottom)
        .clipped()

        switch stageStyle {
        case .hubThumbnail:
            scaled.clipShape(Circle())
        case .conversationFullBody:
            scaled.clipShape(
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
