import UIKit
import BackgroundTasks
import SwiftUI

/// VPN Background Tasks Manager
/// Оптимизация батареи через Background Tasks
class VPNBackgroundTasksManager: ObservableObject {
    
    static let shared = VPNBackgroundTasksManager()
    
    private let taskIdentifier = "family.aladdin.vpncheck"
    private var backgroundTaskScheduled = false
    
    private init() {
        registerTasks()
    }
    
    // MARK: - Task Registration
    
    func registerTasks() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: taskIdentifier,
            using: nil
        ) { task in
            self.handleVPNCheck(task: task as! BGAppRefreshTask)
        }
        
        print("✅ VPN Background Tasks зарегистрированы")
    }
    
    func scheduleNextCheck() {
        guard !backgroundTaskScheduled else {
            print("⚠️ Background task уже запланирован")
            return
        }
        
        let request = BGAppRefreshTaskRequest(identifier: taskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 минут
        
        do {
            try BGTaskScheduler.shared.submit(request)
            backgroundTaskScheduled = true
            print("✅ Background task запланирован на 15 минут")
        } catch {
            print("❌ Ошибка планирования Background Task: \(error)")
            backgroundTaskScheduled = false
        }
    }
    
    // MARK: - Task Handler
    
    private func handleVPNCheck(task: BGAppRefreshTask) {
        print("📱 Background Task начат")
        
        // Expiration handler
        task.expirationHandler = {
            print("⏰ Background Task истек")
            task.setTaskCompleted(success: false)
        }
        
        // Выполняем задачи
        Task {
            do {
                // 1. Отправляем статистику
                if VPNManager.shared.isConnected {
                    VPNManager.shared.sendStatsToServer()
                    print("✅ Статистика отправлена из Background Task")
                }
                
                // 2. Загружаем конфигурацию если нужно
                VPNManager.shared.loadConfigFromServer { result in
                    switch result {
                    case .success:
                        print("✅ Конфигурация загружена из Background Task")
                    case .failure(let error):
                        print("⚠️ Ошибка загрузки конфигурации: \(error)")
                    }
                }
                
                // 3. Проверяем статус VPN
                // В production здесь будет проверка состояния VPN
                
                await Task.sleep(nanoseconds: 100_000_000) // 0.1 сек
                
                task.setTaskCompleted(success: true)
                print("✅ Background Task завершен успешно")
                
                // Планируем следующую проверку
                self.backgroundTaskScheduled = false
                self.scheduleNextCheck()
                
            } catch {
                print("❌ Ошибка в Background Task: \(error)")
                task.setTaskCompleted(success: false)
            }
        }
    }
    
    // MARK: - Periodic Scheduling
    
    func startPeriodicScheduling() {
        // Отправляем статистику каждые 5 минут когда приложение активно
        let timer = Timer.scheduledTimer(withTimeInterval: 300.0, repeats: true) { _ in
            if VPNManager.shared.isConnected {
                VPNManager.shared.sendStatsToServer()
            }
        }
        
        RunLoop.current.add(timer, forMode: .common)
        print("✅ Периодическая отправка статистики запущена (каждые 5 минут)")
    }
    
    func cancelAllTasks() {
        BGTaskScheduler.shared.cancel(taskRequestWithIdentifier: taskIdentifier)
        backgroundTaskScheduled = false
        print("✅ Все Background Tasks отменены")
    }
}


