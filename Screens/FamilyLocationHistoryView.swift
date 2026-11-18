import MapKit
import SwiftUI

/// GET `/api/family/location-history` — one member's points within the plan window.
struct FamilyLocationHistoryResponse: Decodable, Equatable {
    struct Point: Decodable, Equatable {
        let lat: Double
        let lon: Double
        let speed: Double?
        let at: String
    }

    let memberId: String
    let retentionHours: Int
    let points: [Point]

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case retentionHours = "retention_hours"
        case points
    }
}

/// L360 stage 4: where a family member has been (24 h / 7 days / 30 days by plan; server is the authority).
struct FamilyLocationHistoryView: View {
    let memberId: String
    let memberName: String
    let onOpenTariffs: () -> Void

    @ObservedObject private var localizationManager = LocalizationManager.shared
    @State private var state: LoadState = .loading

    private enum LoadState: Equatable {
        case loading
        case loaded(FamilyLocationHistoryResponse)
        case failed
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(memberName)
                    .font(.headline)
                    .foregroundColor(.textPrimary)
                content
                Text(localizationManager.localized("family_location_history_privacy_note"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
        }
        .background(Color.backgroundDark.ignoresSafeArea())
        .navigationTitle(localizationManager.localized("family_location_history_title"))
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
    }

    @ViewBuilder
    private var content: some View {
        switch state {
        case .loading:
            ProgressView()
                .frame(maxWidth: .infinity, minHeight: 220)
        case .failed:
            VStack(spacing: Spacing.s) {
                Text(localizationManager.localized("family_location_history_error"))
                    .font(.subheadline)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                Button(localizationManager.localized("family_location_history_retry")) {
                    Task { await load() }
                }
                .foregroundColor(.secondaryGold)
            }
            .frame(maxWidth: .infinity, minHeight: 220)
        case .loaded(let history):
            Text(localizationManager.localized(Self.windowKey(hours: history.retentionHours)))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.secondaryGold)
            if history.points.isEmpty {
                Text(localizationManager.localized("family_location_history_empty"))
                    .font(.subheadline)
                    .foregroundColor(.textPrimary)
                    .frame(maxWidth: .infinity, minHeight: 160)
                    .multilineTextAlignment(.center)
            } else {
                FamilyLocationHistoryMap(coordinates: history.points.map {
                    CLLocationCoordinate2D(latitude: $0.lat, longitude: $0.lon)
                })
                .frame(height: 320)
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                .accessibilityIdentifier("family_location_history_map")
                Text(String(format: localizationManager.localized("family_location_history_points_fmt"), history.points.count))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            if history.retentionHours < TariffEntitlements.locationHistoryHours(.premium) {
                Button(action: onOpenTariffs) {
                    HStack {
                        Text(localizationManager.localized("family_location_history_upsell"))
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        Spacer(minLength: Spacing.s)
                        Text(localizationManager.localized("family_location_history_upsell_cta"))
                            .font(.caption.weight(.bold))
                            .foregroundColor(.secondaryGold)
                    }
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.28))
                    )
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("family_location_history_upsell")
            }
        }
    }

    static func windowKey(hours: Int) -> String {
        if hours >= TariffEntitlements.locationHistoryHours(.premium) { return "family_location_history_window_30d" }
        if hours >= TariffEntitlements.locationHistoryHours(.family) { return "family_location_history_window_7d" }
        return "family_location_history_window_24h"
    }

    @MainActor
    private func load() async {
        state = .loading
        let result: Result<FamilyLocationHistoryResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getFamilyLocationHistory(memberId: memberId) { continuation.resume(returning: $0) }
        }
        switch result {
        case .success(let history):
            state = .loaded(history)
        case .failure(let error):
            if let networkError = error as? NetworkError, case .notFound = networkError {
                state = .loaded(FamilyLocationHistoryResponse(
                    memberId: memberId,
                    retentionHours: TariffEntitlements.locationHistoryHours(.free),
                    points: []
                ))
            } else {
                state = .failed
            }
        }
    }
}

private struct FamilyLocationHistoryMap: UIViewRepresentable {
    let coordinates: [CLLocationCoordinate2D]

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView()
        map.delegate = context.coordinator
        map.isRotateEnabled = false
        map.pointOfInterestFilter = .excludingAll
        return map
    }

    func updateUIView(_ map: MKMapView, context: Context) {
        map.removeOverlays(map.overlays)
        map.removeAnnotations(map.annotations)
        guard let first = coordinates.first, let last = coordinates.last else { return }
        let line = MKPolyline(coordinates: coordinates, count: coordinates.count)
        map.addOverlay(line)
        let start = MKPointAnnotation()
        start.coordinate = first
        let end = MKPointAnnotation()
        end.coordinate = last
        map.addAnnotations(coordinates.count > 1 ? [start, end] : [end])
        let padding = UIEdgeInsets(top: 32, left: 32, bottom: 32, right: 32)
        if coordinates.count > 1 {
            map.setVisibleMapRect(line.boundingMapRect, edgePadding: padding, animated: false)
        } else {
            map.setRegion(MKCoordinateRegion(center: last, latitudinalMeters: 800, longitudinalMeters: 800), animated: false)
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator: NSObject, MKMapViewDelegate {
        func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
            guard let line = overlay as? MKPolyline else { return MKOverlayRenderer(overlay: overlay) }
            let renderer = MKPolylineRenderer(polyline: line)
            renderer.strokeColor = UIColor(Color.secondaryGold)
            renderer.lineWidth = 4
            return renderer
        }
    }
}
