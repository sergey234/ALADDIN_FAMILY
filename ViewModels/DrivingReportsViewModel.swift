import Foundation
import Combine
import CoreLocation

/**
 * 🚗 Driving Reports ViewModel
 * Управление данными для DrivingReportsModal
 */

@MainActor
class DrivingReportsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var stats: DrivingStats?
    @Published var reports: [DrivingReport] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private let locationManager = LocationManager.shared
    private var cancellables = Set<AnyCancellable>()
    private var trackSampleTask: Task<Void, Never>?
    
    // MARK: - Initialization
    
    init(apiService: APIService? = nil, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }

    private func startTrackSampling(tripId: String) {
        stopTrackSampling()
        trackSampleTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 30_000_000_000)
                guard !Task.isCancelled else { break }
                guard DrivingTripTrackStore.activeTripId == tripId else { break }
                guard let self else { break }
                if let loc = try? await self.locationManager.getCurrentLocation() {
                    DrivingTripTrackStore.append(tripId: tripId, coordinate: loc.coordinate)
                }
            }
        }
    }

    private func stopTrackSampling() {
        trackSampleTask?.cancel()
        trackSampleTask = nil
    }
    
    // MARK: - Public Methods
    
    /// Legacy hook from AnalyticsViewModel — больше не источник правды (агент без trip list).
    /// Оставляем no-op, чтобы старые call sites не затирали ledger/API данными.
    func applyFrom(components: ComponentsAnalytics?, period: String) {
        _ = components
        _ = period
    }
    
    /// Life360-паттерн: поездки выбранного члена за период = remote (если есть) ∪ local ledger.
    /// Статистику считаем **только** из реальных поездок. `/stats` mock на сервере не вызываем.
    func loadReports(userId: String?, period: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let normalizedPeriod: String = {
            switch period {
            case "today", "week", "month", "year": return period
            default: return "week"
            }
        }()

        let local = FamilyDrivingTripLedger.reports(memberId: userId, period: normalizedPeriod)

        var remote: [DrivingReport] = []
        do {
            // API period: today → week window on server (фильтр today уже на клиенте).
            let apiPeriod = (normalizedPeriod == "today") ? "week" : normalizedPeriod
            remote = try await withCheckedThrowingContinuation { continuation in
                apiService.getDrivingReports(userId: userId, period: apiPeriod) { result in
                    continuation.resume(with: result)
                }
            }
            if normalizedPeriod == "today" {
                let start = FamilyDrivingTripLedger.periodStart("today")
                remote = remote.filter { $0.startTime >= start }
            }
            if let uid = userId?.trimmingCharacters(in: .whitespacesAndNewlines), !uid.isEmpty, uid != "current" {
                remote = remote.filter { $0.userId == uid }
            }
        } catch {
            let networkError = NetworkError.from(error)
            if case .unauthorized = networkError {
                // Local ledger всё равно показываем — родитель видит свои поездки offline.
                print("⚠️ DrivingReportsViewModel: unauthorized — local ledger only")
            } else {
                print("⚠️ DrivingReportsViewModel: remote load failed: \(networkError.localizedDescription)")
            }
        }

        let merged = FamilyDrivingTripLedger.merge(remote: remote, local: local)
            .map { DrivingTripTrackStore.mergeInto($0) }
        reports = merged
        stats = FamilyDrivingTripLedger.stats(from: merged, period: normalizedPeriod)
        errorMessage = nil
    }
    
    func exportReport(reportId: String, format: String) async throws -> Data {
        return try await withCheckedThrowingContinuation { continuation in
            apiService.exportDrivingReport(reportId: reportId, format: format) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Начать поездку с получением координат
    func startTrip(userId: String?) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // ✅ ИНТЕГРАЦИЯ: Получаем текущее местоположение при начале поездки
            let startLocation = try await locationManager.getCurrentLocation()
            print("📍 DrivingReportsViewModel: Начало поездки для пользователя \(userId ?? "current"): \(startLocation.coordinate.latitude), \(startLocation.coordinate.longitude)")
            
            // ✅ ИНТЕГРАЦИЯ: Отправляем координаты начала поездки на сервер
            try await withCheckedThrowingContinuation { continuation in
                apiService.startDrivingTrip(userId: userId, startLatitude: startLocation.coordinate.latitude, startLongitude: startLocation.coordinate.longitude) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }

            let tripId = "local_\(Int(Date().timeIntervalSince1970))"
            let device = FamilyDrivingTripLedger.currentDeviceMember()
            let mid = (userId?.isEmpty == false) ? userId! : device.id
            DrivingTripTrackStore.begin(tripId: tripId, start: startLocation.coordinate)
            FamilyDrivingTripLedger.beginMeta(
                tripId: tripId,
                memberId: mid,
                memberName: device.name
            )
            startTrackSampling(tripId: tripId)
            
            // Обновляем отчеты
            await loadReports(userId: userId, period: "week")
        } catch {
            // Если ошибка получения местоположения - все равно начинаем поездку
            if error is LocationManagerError {
                print("⚠️ DrivingReportsViewModel: Ошибка получения местоположения, но начинаем поездку: \(error.localizedDescription)")
                // Продолжаем без координат
                await loadReports(userId: userId, period: "week")
            } else {
                let networkError = NetworkError.from(error)
                // ✅ ИСПРАВЛЕНИЕ 1: Обрабатываем ошибку авторизации отдельно
                if case .unauthorized = networkError {
                    errorMessage = "Требуется авторизация. Войдите в аккаунт для начала поездки."
                } else if networkError.isCritical || !networkError.isRetryable {
                    let errorKey = "driving_reports_error_start_failed"
                    let errorFormat = localizationManager.localized(errorKey)
                    errorMessage = String(format: errorFormat, networkError.localizedDescription)
                }
            }
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Завершить поездку с получением координат
    func endTrip(userId: String?, tripId: String?) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // ✅ ИНТЕГРАЦИЯ: Получаем текущее местоположение при завершении поездки
            let endLocation = try await locationManager.getCurrentLocation()
            print("📍 DrivingReportsViewModel: Завершение поездки \(tripId ?? "current"): \(endLocation.coordinate.latitude), \(endLocation.coordinate.longitude)")
            
            // ✅ ИНТЕГРАЦИЯ: Отправляем координаты конца поездки на сервер
            let resolvedTripId = tripId
                ?? DrivingTripTrackStore.activeTripId
                ?? "current"
            try await withCheckedThrowingContinuation { continuation in
                apiService.endDrivingTrip(tripId: resolvedTripId, endLatitude: endLocation.coordinate.latitude, endLongitude: endLocation.coordinate.longitude) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            stopTrackSampling()
            let finishId = DrivingTripTrackStore.activeTripId ?? resolvedTripId
            _ = FamilyDrivingTripLedger.finalizeActiveTrip(
                tripId: finishId,
                end: endLocation.coordinate,
                memberId: userId
            )
            
            // Обновляем отчеты
            await loadReports(userId: userId, period: "week")
        } catch {
            // Если ошибка получения местоположения - все равно завершаем поездку
            if error is LocationManagerError {
                print("⚠️ DrivingReportsViewModel: Ошибка получения местоположения, но завершаем поездку: \(error.localizedDescription)")
                stopTrackSampling()
                if let active = DrivingTripTrackStore.activeTripId {
                    _ = FamilyDrivingTripLedger.finalizeActiveTrip(tripId: active, end: nil, memberId: userId)
                }
                // Продолжаем без координат
                await loadReports(userId: userId, period: "week")
            } else {
                let networkError = NetworkError.from(error)
                // ✅ ИСПРАВЛЕНИЕ 1: Обрабатываем ошибку авторизации отдельно
                if case .unauthorized = networkError {
                    errorMessage = "Требуется авторизация. Войдите в аккаунт для завершения поездки."
                } else if networkError.isCritical || !networkError.isRetryable {
                    let errorKey = "driving_reports_error_end_failed"
                    let errorFormat = localizationManager.localized(errorKey)
                    errorMessage = String(format: errorFormat, networkError.localizedDescription)
                }
            }
        }
    }
}

