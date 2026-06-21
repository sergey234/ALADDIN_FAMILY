import SwiftUI
import UIKit
import os.log

/// P1-08 / HERO-3-08 — хост: bundled `.riv` + RiveRuntime (если подключён).
enum CompanionHeroRiveHost {
    private static let masterImageCache = NSCache<NSString, UIImage>()
    private static let heroLog = OSLog(
        subsystem: Bundle.main.bundleIdentifier ?? "family.aladdin.ios",
        category: "CompanionHero"
    )
    /// Placeholder `.riv` из репо ~15 KB; production export обычно &gt; 25 KB.
    static let productionRivMinBytes: Int = 25_000
    /// iOS контракт (см. `scripts/companion_07_verify_unicorn_riv.py`).
    static let stateMachineName = "HeroSM"
    private static let mouthInputCandidates = ["mouth_open", "mouthOpen", "MouthOpen"]

    /// Production `.riv` artboard names differ per hero (runtime export vs editor `Hero360`).
    private static func artboardNameCandidates(for characterId: String) -> [String?] {
        switch rivBaseName(characterId: characterId) {
        case "unicorn":
            return ["unicorn_master_crop_360x480", "Hero360", nil]
        case "aladdin":
            return ["aladdin_master_crop_360x480", "Hero360", nil]
        case "genie":
            return ["genie_master_crop_360x480", "Hero360", nil]
        default:
            return ["Hero360", nil]
        }
    }

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

    #if DEBUG
    static func debugHeroPathLabel(characterId: String, usesRive: Bool) -> String {
        let riv = rivBaseName(characterId: characterId)
        if usesRive { return "b\(AppConfig.buildNumber) RIVE \(riv)" }
        if isSimulatorIOS15MetalUnstable { return "b\(AppConfig.buildNumber) PNG iOS15-sim" }
        if !isProductionRiv(characterId: characterId) { return "b\(AppConfig.buildNumber) PNG placeholder-riv" }
        return "b\(AppConfig.buildNumber) PNG fallback"
    }
    #endif

    /// Почему показываем PNG вместо Rive (Console: `CompanionHero`).
    static func pngFallbackReason(characterId: String) -> String {
        if isSimulatorIOS15MetalUnstable { return "ios15_simulator_rive_disabled" }
        if !isProductionRiv(characterId: characterId) { return "riv_placeholder_or_missing" }
        if !hasRasterFallback(characterId: characterId) { return "no_png_master" }
        return "rive_runtime_load_failed_or_not_visible"
    }

    private static func logRiveLoadFailure(characterId: String, reason: String, detail: String = "") {
        os_log(
            "[CompanionHero] rive_load_fail character=%{public}@ reason=%{public}@ detail=%{public}@",
            log: heroLog,
            type: .error,
            rivBaseName(characterId: characterId),
            reason,
            detail
        )
    }

    /// Release-safe: Console.app filter `CompanionHero`.
    static func logHeroPath(characterId: String, renderPath: String, vmStatus: String) {
        let rivName = rivBaseName(characterId: characterId)
        let bytes: Int = {
            guard let url = bundledRivURL(characterId: characterId) else { return 0 }
            return (try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
        }()
        os_log(
            "[CompanionHero] path=%{public}@ character=%{public}@ rivBytes=%d vm=%{public}@",
            log: heroLog,
            type: .info,
            renderPath,
            rivName,
            bytes,
            vmStatus
        )
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
        guard let url = bundledRivURL(characterId: characterId) else {
            logRiveLoadFailure(characterId: characterId, reason: "missing_bundle_url")
            return nil
        }
        guard let data = try? Data(contentsOf: url) else {
            logRiveLoadFailure(characterId: characterId, reason: "read_data_failed", detail: url.lastPathComponent)
            return nil
        }
        guard let file = try? RiveFile(data: data, loadCdn: false) else {
            logRiveLoadFailure(
                characterId: characterId,
                reason: "rive_file_decode_failed",
                detail: "\(data.count)b fmt=\(riveFormatLabel(data))"
            )
            return nil
        }

        let candidates = artboardNameCandidates(for: characterId)
        for artboardName in candidates {
            if let viewModel = attemptViewModel(
                file: file,
                artboardName: artboardName,
                stateMachineName: stateMachineName
            ) {
                os_log(
                    "[CompanionHero] rive_load_ok character=%{public}@ artboard=%{public}@ sm=%{public}@",
                    log: heroLog,
                    type: .info,
                    rivBaseName(characterId: characterId),
                    artboardName ?? "(default)",
                    stateMachineName
                )
                return viewModel
            }
        }
        for artboardName in candidates {
            if let viewModel = attemptViewModel(
                file: file,
                artboardName: artboardName,
                stateMachineName: nil
            ) {
                os_log(
                    "[CompanionHero] rive_load_ok character=%{public}@ artboard=%{public}@ sm=(none)",
                    log: heroLog,
                    type: .info,
                    rivBaseName(characterId: characterId),
                    artboardName ?? "(default)"
                )
                return viewModel
            }
        }
        logRiveLoadFailure(
            characterId: characterId,
            reason: "no_artboard_or_state_machine",
            detail: candidates.compactMap { $0 ?? "default" }.joined(separator: ",")
        )
        return nil
    }

    private static func riveFormatLabel(_ data: Data) -> String {
        guard data.count >= 6, data.starts(with: [0x52, 0x49, 0x56, 0x45]) else { return "not_rive" }
        return "v\(data[4]).\(data[5])"
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

    static func applyRiveMouthOnly(to viewModel: RiveViewModel, mouthOpen: CGFloat) {
        applyMouthOpen(to: viewModel, mouthOpen: mouthOpen)
    }

    static func applyRiveEmotionTrigger(to viewModel: RiveViewModel, emotion: CompanionHeroEmotion) {
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
    private static var cache: [String: RiveViewModel] = [:]
    let viewModel: RiveViewModel?

    init(characterId: String) {
        if let cached = Self.cache[characterId] {
            viewModel = cached
            return
        }
        let created = CompanionHeroRiveHost.makeRiveViewModel(characterId: characterId)
        if let created {
            Self.cache[characterId] = created
        }
        viewModel = created
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
    @State private var didLogPath = false

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
                    TimelineView(.animation(minimumInterval: 1 / 20)) { timeline in
                        let t = timeline.date.timeIntervalSinceReferenceDate
                        let lipActive = emotion == .speaking || lipSyncPhase > 0
                        let mouthOpen = CompanionHeroLipSync.proceduralMouthOpen(isActive: lipActive, time: t)
                        rivStage(viewModel: viewModel, mouthOpen: mouthOpen)
                    }
                } else {
                    fallbackHeroView
                }
            } else {
                fallbackHeroView
                    .onAppear { logRenderPathOnce(path: "PNG", vmStatus: "nil") }
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
    private func rivStage(viewModel: RiveViewModel, mouthOpen: CGFloat) -> some View {
        let fillScale: CGFloat = {
            guard stageStyle == .conversationFullBody, stageContentMode == .fillBottom else { return 1 }
            return CompanionHeroLayout.stageFillScaleFactor(stageSize: stageSize)
        }()
        let scaled = ZStack(alignment: .topLeading) {
            viewModel.view()
            CompanionHeroRiveInputsSync(
                viewModel: viewModel,
                emotion: emotion,
                mouthOpen: mouthOpen,
                characterId: characterId
            )
            #if DEBUG
            Text(CompanionHeroRiveHost.debugHeroPathLabel(characterId: characterId, usesRive: true))
                .font(.caption2.monospaced())
                .padding(4)
                .background(.black.opacity(0.55))
                .foregroundStyle(.green)
                .clipShape(RoundedRectangle(cornerRadius: 4))
                .padding(6)
            #endif
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

    private func logRenderPathOnce(path: String, vmStatus: String) {
        guard !didLogPath else { return }
        didLogPath = true
        CompanionHeroRiveHost.logHeroPath(characterId: characterId, renderPath: path, vmStatus: vmStatus)
    }
}

/// Lip-sync на mouth_open; эмоция — trigger только при смене emotion.
private struct CompanionHeroRiveInputsSync: View {
    let viewModel: RiveViewModel
    let emotion: CompanionHeroEmotion
    let mouthOpen: CGFloat
    let characterId: String

    @State private var didLogPath = false

    private var mouthQuantized: Int { Int(mouthOpen * 16) }

    var body: some View {
        Color.clear
            .frame(width: 0, height: 0)
            .onAppear {
                if !didLogPath {
                    didLogPath = true
                    CompanionHeroRiveHost.logHeroPath(
                        characterId: characterId,
                        renderPath: "RIVE",
                        vmStatus: "ok"
                    )
                }
                CompanionHeroRiveHost.applyRiveEmotionTrigger(to: viewModel, emotion: emotion)
                CompanionHeroRiveHost.applyRiveMouthOnly(to: viewModel, mouthOpen: mouthOpen)
            }
            .onChange(of: emotion) { newEmotion in
                CompanionHeroRiveHost.applyRiveEmotionTrigger(to: viewModel, emotion: newEmotion)
            }
            .onChange(of: mouthQuantized) { _ in
                CompanionHeroRiveHost.applyRiveMouthOnly(to: viewModel, mouthOpen: mouthOpen)
            }
    }
}
#endif
