import SwiftUI
import CoreLocation

/// 🚗 Roadside Assistance View
/// Экран для вызова помощи на дороге
/// ✅ ЗАДАЧА 26: UI для Roadside Assistance
struct RoadsideAssistanceView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var vehicleInfo: String = ""
    @State private var currentLocation: CLLocationCoordinate2D?
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var activeRequest: RoadsideRequest? = nil
    @State private var requestHistory: [RoadsideRequest] = []
    
    private let apiService = APIService.shared
    private let locationManager = CLLocationManager()
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Кнопка вызова помощи
                        if activeRequest == nil {
                            callHelpSection
                        } else {
                            activeRequestSection
                        }
                        
                        // История обращений
                        if !requestHistory.isEmpty {
                            historySection
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle(localizationManager.localized("roadside_assistance_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("close")) {
                        dismiss()
                    }
                }
            }
        }
        .onAppear {
            requestLocation()
            loadHistory()
        }
    }
    
    private var callHelpSection: some View {
        VStack(spacing: 16) {
            Text(localizationManager.localized("roadside_call_dialog_title"))
                .font(.title2)
                .foregroundColor(.textPrimary)
            
            // Информация о ТС
            VStack(alignment: .leading, spacing: 8) {
                Text(localizationManager.localized("roadside_vehicle_info"))
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                
                TextField(localizationManager.localized("roadside_vehicle_info_placeholder"), text: $vehicleInfo)
                    .textFieldStyle(.roundedBorder)
            }
            
            // Кнопка вызова
            Button(action: callHelp) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text(localizationManager.localized("roadside_call_help"))
                        .font(.headline)
                        .foregroundColor(.white)
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.red)
            .cornerRadius(10)
            .disabled(isLoading || vehicleInfo.isEmpty)
            
            if let error = errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
            }
        }
        .padding()
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(12)
    }
    
    private var activeRequestSection: some View {
        VStack(spacing: 16) {
            if let request = activeRequest {
                Text(localizationManager.localized("roadside_status_\(request.status)"))
                    .font(.title2)
                    .foregroundColor(.textPrimary)
                
                if let eta = request.eta {
                    Text(String(format: localizationManager.localized("roadside_eta"), eta))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                
                if let provider = request.provider {
                    Text(String(format: localizationManager.localized("roadside_provider"), provider))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                
                Button(action: cancelRequest) {
                    Text(localizationManager.localized("roadside_cancel_request"))
                        .font(.headline)
                        .foregroundColor(.white)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.orange)
                .cornerRadius(10)
            }
        }
        .padding()
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(12)
    }
    
    private var historySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("roadside_history"))
                .font(.title3)
                .foregroundColor(.textPrimary)
            
            ForEach(requestHistory) { request in
                HistoryRow(request: request)
            }
        }
        .padding()
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(12)
    }
    
    private func requestLocation() {
        locationManager.requestWhenInUseAuthorization()
        if let location = locationManager.location {
            currentLocation = location.coordinate
        }
    }
    
    private func callHelp() {
        guard let location = currentLocation else {
            errorMessage = localizationManager.localized("roadside_location_error")
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        apiService.callRoadsideAssistance(
            location: location,
            vehicleInfo: vehicleInfo
        ) { result in
            isLoading = false
            switch result {
            case .success(let request):
                activeRequest = request
            case .failure(let error):
                errorMessage = error.localizedDescription
            }
        }
    }
    
    private func cancelRequest() {
        guard let requestId = activeRequest?.id else { return }
        
        apiService.cancelRoadsideAssistance(requestId: requestId) { result in
            switch result {
            case .success:
                activeRequest = nil
            case .failure(let error):
                errorMessage = error.localizedDescription
            }
        }
    }
    
    private func loadHistory() {
        apiService.getRoadsideAssistanceHistory { result in
            switch result {
            case .success(let history):
                requestHistory = history
            case .failure:
                break
            }
        }
    }
}

private struct HistoryRow: View {
    let request: RoadsideRequest
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("roadside_status_\(request.status)"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                if let createdAt = request.createdAt {
                    Text(createdAt)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(8)
    }
}
