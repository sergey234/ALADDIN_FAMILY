import XCTest
@testable import ALADDIN

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
}
