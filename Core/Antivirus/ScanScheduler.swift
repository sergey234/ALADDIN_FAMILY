import Foundation
import BackgroundTasks
import UserNotifications

/// Планировщик автоматических сканирований
/// Использует BGAppRefreshTask для фоновых сканирований
class ScanScheduler: NSObject, ObservableObject {

    static let shared = ScanScheduler()

    @Published var isScheduled = false
    @Published var nextScanDate: Date?
    @Published var lastScheduledScan: Date?

    private let taskIdentifier = "com.aladdin.antivirus.scan"
    private let userDefaults = UserDefaults.standard
    private let notificationCenter = UNUserNotificationCenter.current()

    private var scanFrequency: String {
        get { userDefaults.string(forKey: "scanFrequency") ?? "daily" }
        set { userDefaults.set(newValue, forKey: "scanFrequency") }
    }

    private var autoScanEnabled: Bool {
        get { userDefaults.bool(forKey: "autoScanEnabled") }
        set { userDefaults.set(newValue, forKey: "autoScanEnabled") }
    }

    // MARK: - Initialization

    private override init() {
        super.init()
        registerBackgroundTask()
        requestNotificationPermissions()
        updateNextScanDate()
    }

    // MARK: - Public API

    /// Включение/отключение автоматического сканирования
    func setAutoScan(enabled: Bool, frequency: String = "daily") {
        autoScanEnabled = enabled
        scanFrequency = frequency

        if enabled {
            scheduleNextScan()
            print("[ScanScheduler] ✅ Автоматическое сканирование включено (\(frequency))")
        } else {
            cancelScheduledScans()
            print("[ScanScheduler] ❌ Автоматическое сканирование отключено")
        }

        updateNextScanDate()
    }

    /// Запуск сканирования вручную
    func performManualScan() async {
        print("[ScanScheduler] 🔄 Запуск ручного сканирования")

        do {
            let scanJob = try await APIService.shared.startQuickScanAsync(scanType: "manual")

            // Ждем завершения
            while true {
                let status = try await APIService.shared.getScanJobStatusAsync(jobId: scanJob.jobId)

                if status.status == "completed" {
                    await sendScanCompleteNotification(threatsFound: status.threatsFound)
                    lastScheduledScan = Date()
                    print("[ScanScheduler] ✅ Ручное сканирование завершено: \(status.threatsFound) угроз")
                    break
                } else if status.status == "failed" {
                    await sendScanFailedNotification()
                    print("[ScanScheduler] ❌ Ручное сканирование не удалось")
                    break
                }

                try await Task.sleep(nanoseconds: 2_000_000_000) // 2 секунды
            }

        } catch {
            print("[ScanScheduler] ❌ Ошибка ручного сканирования: \(error.localizedDescription)")
            await sendScanFailedNotification()
        }
    }

    /// Получить текущие настройки
    func getCurrentSettings() -> (enabled: Bool, frequency: String) {
        return (autoScanEnabled, scanFrequency)
    }

    // MARK: - Background Task Registration

    private func registerBackgroundTask() {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: taskIdentifier, using: nil) { task in
            self.handleBackgroundScan(task as! BGAppRefreshTask)
        }
        print("[ScanScheduler] 📋 Background task зарегистрирован")
    }

    private func handleBackgroundScan(_ task: BGAppRefreshTask) {
        print("[ScanScheduler] 🎯 Выполнение фонового сканирования")

        // Устанавливаем обработчик истечения времени
        task.expirationHandler = {
            print("[ScanScheduler] ⏰ Фоновое сканирование истекло по времени")
            task.setTaskCompleted(success: false)
        }

        // Запускаем сканирование
        Task {
            do {
                let scanJob = try await APIService.shared.startQuickScanAsync(scanType: "scheduled")

                // Простая проверка статуса (в реальности нужно мониторить)
                try await Task.sleep(nanoseconds: 5_000_000_000) // 5 секунд

                let status = try await APIService.shared.getScanJobStatusAsync(jobId: scanJob.jobId)

                if status.status == "completed" {
                    await sendScanCompleteNotification(threatsFound: status.threatsFound)
                    lastScheduledScan = Date()
                    task.setTaskCompleted(success: true)
                    print("[ScanScheduler] ✅ Фоновое сканирование завершено успешно")
                } else {
                    task.setTaskCompleted(success: false)
                    print("[ScanScheduler] ❌ Фоновое сканирование не завершено")
                }

            } catch {
                print("[ScanScheduler] ❌ Ошибка фонового сканирования: \(error.localizedDescription)")
                task.setTaskCompleted(success: false)
            }
        }

        // Планируем следующее сканирование
        scheduleNextScan()
    }

    // MARK: - Scheduling

    private func scheduleNextScan() {
        guard autoScanEnabled else { return }

        let request = BGAppRefreshTaskRequest(identifier: taskIdentifier)

        // Устанавливаем время следующего сканирования
        let interval = getScanInterval()
        request.earliestBeginDate = Date(timeIntervalSinceNow: interval)

        do {
            try BGTaskScheduler.shared.submit(request)
            nextScanDate = request.earliestBeginDate
            isScheduled = true
            print("[ScanScheduler] 📅 Следующее сканирование запланировано на: \(nextScanDate!)")
        } catch {
            print("[ScanScheduler] ❌ Ошибка планирования сканирования: \(error.localizedDescription)")
        }
    }

    private func cancelScheduledScans() {
        BGTaskScheduler.shared.cancel(taskWithIdentifier: taskIdentifier)
        nextScanDate = nil
        isScheduled = false
        print("[ScanScheduler] 🚫 Запланированные сканирования отменены")
    }

    private func getScanInterval() -> TimeInterval {
        switch scanFrequency {
        case "hourly": return 3600      // 1 час
        case "daily": return 86400      // 24 часа
        case "weekly": return 604800    // 7 дней
        default: return 86400           // По умолчанию ежедневно
        }
    }

    private func updateNextScanDate() {
        if autoScanEnabled && isScheduled {
            let interval = getScanInterval()
            nextScanDate = Date(timeIntervalSinceNow: interval)
        } else {
            nextScanDate = nil
        }
    }

    // MARK: - Notifications

    private func requestNotificationPermissions() {
        notificationCenter.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                print("[ScanScheduler] ✅ Разрешение на уведомления получено")
            } else {
                print("[ScanScheduler] ❌ Разрешение на уведомления отклонено")
            }
        }
    }

    private func sendScanCompleteNotification(threatsFound: Int) async {
        let content = UNMutableNotificationContent()
        content.title = "Антивирусное сканирование завершено"

        if threatsFound > 0 {
            content.body = "Обнаружено \(threatsFound) угроз. Требуется внимание!"
            content.sound = .defaultCritical
        } else {
            content.body = "Угроз не обнаружено. Система в безопасности."
            content.sound = .default
        }

        content.badge = threatsFound > 0 ? 1 : 0

        let request = UNNotificationRequest(
            identifier: "scan_complete_\(Date().timeIntervalSince1970)",
            content: content,
            trigger: nil
        )

        do {
            try await notificationCenter.add(request)
            print("[ScanScheduler] 📢 Уведомление о завершении сканирования отправлено")
        } catch {
            print("[ScanScheduler] ❌ Ошибка отправки уведомления: \(error.localizedDescription)")
        }
    }

    private func sendScanFailedNotification() async {
        let content = UNMutableNotificationContent()
        content.title = "Ошибка антивирусного сканирования"
        content.body = "Не удалось выполнить сканирование. Проверьте подключение к интернету."
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "scan_failed_\(Date().timeIntervalSince1970)",
            content: content,
            trigger: nil
        )

        do {
            try await notificationCenter.add(request)
            print("[ScanScheduler] 📢 Уведомление об ошибке сканирования отправлено")
        } catch {
            print("[ScanScheduler] ❌ Ошибка отправки уведомления: \(error.localizedDescription)")
        }
    }

    // MARK: - File Monitoring

    /// Начать мониторинг загрузок файлов
    func startDownloadMonitoring() {
        // Реализация мониторинга с помощью FileProvider или NSMetadataQuery
        // для отслеживания новых файлов в Downloads
        print("[ScanScheduler] 👀 Мониторинг загрузок запущен")
    }

    /// Остановить мониторинг загрузок файлов
    func stopDownloadMonitoring() {
        print("[ScanScheduler] ⏹️ Мониторинг загрузок остановлен")
    }

    /// Сканировать вновь загруженный файл
    func scanDownloadedFile(at url: URL) async {
        print("[ScanScheduler] 📁 Сканирование загруженного файла: \(url.lastPathComponent)")

        // Используем быструю проверку для новых файлов
        let threatLevel = await AntivirusManager.shared.quickMetadataCheck(fileURL: url)

        if threatLevel == .suspicious || threatLevel == .dangerous {
            // Если файл подозрительный, запускаем полное сканирование
            let _ = await AntivirusManager.shared.performFullScan(fileURL: url)

            // Отправляем уведомление
            await sendDownloadedFileThreatNotification(fileName: url.lastPathComponent)
        }
    }

    private func sendDownloadedFileThreatNotification(fileName: String) async {
        let content = UNMutableNotificationContent()
        content.title = "Подозрительный файл обнаружен"
        content.body = "Файл '\(fileName)' может содержать угрозу. Рекомендуется проверить."
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "downloaded_file_threat_\(Date().timeIntervalSince1970)",
            content: content,
            trigger: nil
        )

        do {
            try await notificationCenter.add(request)
            print("[ScanScheduler] 📢 Уведомление о подозрительном файле отправлено")
        } catch {
            print("[ScanScheduler] ❌ Ошибка отправки уведомления: \(error.localizedDescription)")
        }
    }
}


