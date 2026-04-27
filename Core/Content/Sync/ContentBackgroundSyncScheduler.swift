import Foundation
import BackgroundTasks

final class ContentBackgroundSyncScheduler {
    static let shared = ContentBackgroundSyncScheduler()

    private let taskIdentifier = "family.aladdin.ios.content.refresh"
    private var isRegistered = false

    private init() {}

    func registerIfNeeded() {
        guard !isRegistered else { return }
        isRegistered = true

        BGTaskScheduler.shared.register(forTaskWithIdentifier: taskIdentifier, using: nil) { task in
            guard let refreshTask = task as? BGAppRefreshTask else {
                task.setTaskCompleted(success: false)
                return
            }
            self.handleAppRefresh(task: refreshTask)
        }
    }

    func scheduleNextRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: taskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 30 * 60)
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            // Ignore scheduling failures on unsupported targets/configurations.
        }
    }

    func triggerForegroundRefresh() {
        Task {
            await ContentManager.shared.autoRefreshIfNeeded(force: true)
        }
    }

    private func handleAppRefresh(task: BGAppRefreshTask) {
        scheduleNextRefresh()

        let operation = Task {
            await ContentManager.shared.autoRefreshIfNeeded(force: true)
            task.setTaskCompleted(success: true)
        }

        task.expirationHandler = {
            operation.cancel()
            task.setTaskCompleted(success: false)
        }
    }
}

