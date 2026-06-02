import Foundation

/// Применяет ответ `GET /api/wellness/session/loop` к локальной сессии Hub → Companion.
@MainActor
enum WellnessLoopCoordinator {
  enum Outcome: Equatable {
    case proceed(suggestPhq: Bool)
    case crisisL3
    case guardBlocked(String)
  }

  /// Запускает loop на сервере и синхронизирует pillar / PHQ / кризис.
  static func runAndApply(
    message: String = "",
    requestedPillar: String? = nil
  ) async -> Outcome {
    guard WellnessSessionStore.hasAcceptedConsent else { return .proceed(suggestPhq: false) }
    do {
      let resp = try await WellnessAPIService.shared.fetchSessionLoop(
        message: message,
        requestedPillar: requestedPillar
      )
      return apply(resp)
    } catch {
      return .proceed(suggestPhq: false)
    }
  }

  static func apply(_ resp: WellnessSessionLoopResponse) -> Outcome {
    let loop = resp.loop
    if loop.phase == "crisis_l3" || loop.escalationLevel == "L3" {
      return .crisisL3
    }
    if !loop.guardOk {
      return .guardBlocked(loop.guardReason ?? "pillar_mismatch")
    }
    if let pillar = loop.primaryPillar, !pillar.isEmpty {
      WellnessSessionStore.setActivePillar(pillar)
    }
    return .proceed(suggestPhq: loop.suggestPhqLite)
  }
}
