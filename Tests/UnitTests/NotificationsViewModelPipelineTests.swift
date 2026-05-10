import XCTest
@testable import ALADDIN

@MainActor
final class NotificationsViewModelPipelineTests: XCTestCase {

    private struct FailingNotificationsService: NotificationsService {
        func fetchNotifications(includeRead: Bool, limit: Int) async throws -> NotificationsEnvelope {
            throw NotificationsAPIError.invalidResponse
        }

        func markNotificationAsRead(_ notificationId: String) async throws -> Int {
            0
        }
    }

    override func setUpWithError() throws {
        NotificationManager.shared.clearPersistedSecurityEvents()
    }

    override func tearDownWithError() throws {
        NotificationManager.shared.clearPersistedSecurityEvents()
    }

    func testCorrelationResolutionPrefersExplicitCorrelationId() {
        let response = NotificationResponse(
            id: "n1",
            icon: "🔔",
            title: "Threat",
            message: "Detected",
            timestamp: Date(),
            isRead: false,
            type: "threat_detected",
            priority: "high",
            actionRequired: nil,
            actionUrl: nil,
            metadata: ["event_id": "event-1"],
            correlationId: "corr-1",
            eventId: "event-2"
        )

        let mapped = NotificationsViewModel.AppNotification(from: response)
        XCTAssertEqual(mapped.correlationId, "corr-1")
    }

    func testLoadNotificationsFallsBackToPersistedSecurityEventsOnError() async throws {
        let manager = NotificationManager.shared
        manager.sendLocalNotification(
            title: "Persisted threat",
            body: "Detected while offline",
            category: .security,
            userInfo: [
                "type": "threat_detected",
                "correlation_id": "persisted-corr-1"
            ],
            delay: 0.1
        )

        try await Task.sleep(nanoseconds: 250_000_000)

        let viewModel = NotificationsViewModel(service: FailingNotificationsService())
        await viewModel.loadNotifications(includeRead: true)

        XCTAssertFalse(viewModel.notifications.isEmpty, "Fallback should load persisted security events")
        XCTAssertEqual(viewModel.notifications.first?.correlationId, "persisted-corr-1")
        XCTAssertNotNil(viewModel.errorMessage, "Original API error should still be visible")
    }

    func testNotificationKindMapsKnownServerTypes() {
        XCTAssertEqual(NotificationsViewModel.NotificationKind(from: "threat_detected"), .threat)
        XCTAssertEqual(NotificationsViewModel.NotificationKind(from: "security_alert"), .threat)
        XCTAssertEqual(NotificationsViewModel.NotificationKind(from: "bypass_attempt"), .bypassAttempt)
        XCTAssertEqual(NotificationsViewModel.NotificationKind(from: "payment_success"), .success)
        XCTAssertEqual(NotificationsViewModel.NotificationKind(from: "unknown_server_type_xyz"), .info)
    }

    func testMergeRemoteWithPersistedSkipsPersistedWhenCorrelationMatchesRemote() {
        let base = Date()
        let remote = NotificationsViewModel.AppNotification(
            id: "remote-1",
            icon: "🔔",
            title: "Server",
            message: "m",
            timestamp: base,
            isRead: false,
            kind: .bypassAttempt,
            metadata: ["correlation_id": "corr-dup"]
        )
        let persisted = NotificationsViewModel.AppNotification(
            id: "local-1",
            icon: "🔔",
            title: "Offline",
            message: "m",
            timestamp: base.addingTimeInterval(-60),
            isRead: false,
            kind: .bypassAttempt,
            metadata: ["correlation_id": "corr-dup"]
        )
        let merged = NotificationsViewModel.mergeRemoteNotificationsWithPersistedLocal(
            remote: [remote],
            persisted: [persisted]
        )
        XCTAssertEqual(merged.count, 1)
        XCTAssertEqual(merged.first?.id, "remote-1")
    }

    func testMergeRemoteWithPersistedAppendsOnlyMissingCorrelationIds() {
        let base = Date()
        let remote = NotificationsViewModel.AppNotification(
            id: "r-a",
            icon: "🔔",
            title: "A",
            message: "",
            timestamp: base,
            isRead: true,
            kind: .info,
            metadata: ["correlation_id": "corr-a"]
        )
        let persistedOnly = NotificationsViewModel.AppNotification(
            id: "p-b",
            icon: "🔔",
            title: "B",
            message: "",
            timestamp: base.addingTimeInterval(-120),
            isRead: false,
            kind: .threat,
            metadata: ["correlation_id": "corr-b"]
        )
        let merged = NotificationsViewModel.mergeRemoteNotificationsWithPersistedLocal(
            remote: [remote],
            persisted: [persistedOnly]
        )
        XCTAssertEqual(merged.count, 2)
        let ids = Set(merged.map(\.id))
        XCTAssertEqual(ids, ["r-a", "p-b"])
    }
}
