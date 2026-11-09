import Combine
import CoreLocation
import Foundation
import MapKit

/// S30 — Apple Maps address autocomplete for family places (no Google/Yandex key).
@MainActor
final class PlaceAddressSearchCompleter: NSObject, ObservableObject {
    @Published var query: String = "" {
        didSet { pushQueryToCompleter() }
    }
    @Published private(set) var results: [MKLocalSearchCompletion] = []
    @Published private(set) var isSearching = false
    @Published private(set) var appearsOffline = false

    private let completer = MKLocalSearchCompleter()
    private var lastPushedFragment: String = ""

    override init() {
        super.init()
        completer.delegate = self
        completer.resultTypes = [.address, .pointOfInterest]
    }

    func clearResults() {
        results = []
        isSearching = false
        appearsOffline = false
    }

    func reset() {
        query = ""
        clearResults()
        completer.queryFragment = ""
        lastPushedFragment = ""
    }

    /// Resolve a suggestion to a display address + coordinate for geofence save.
    func resolve(
        _ completion: MKLocalSearchCompletion
    ) async throws -> (address: String, coordinate: CLLocationCoordinate2D, title: String) {
        let request = MKLocalSearch.Request(completion: completion)
        let response = try await Self.startSearch(request)
        guard let item = response.mapItems.first else {
            throw PlaceAddressSearchError.noMapItem
        }
        let coordinate: CLLocationCoordinate2D
        if let location = item.placemark.location {
            coordinate = location.coordinate
        } else if CLLocationCoordinate2DIsValid(item.placemark.coordinate) {
            coordinate = item.placemark.coordinate
        } else {
            throw PlaceAddressSearchError.noCoordinate
        }

        let title = completion.title.trimmingCharacters(in: .whitespacesAndNewlines)
        let subtitle = completion.subtitle.trimmingCharacters(in: .whitespacesAndNewlines)
        let address: String
        if let line = Self.formattedAddress(from: item.placemark), !line.isEmpty {
            address = line
        } else if !subtitle.isEmpty {
            address = [title, subtitle].filter { !$0.isEmpty }.joined(separator: ", ")
        } else {
            address = title
        }
        guard !address.isEmpty else { throw PlaceAddressSearchError.noMapItem }
        return (address, coordinate, title.isEmpty ? address : title)
    }

    private func pushQueryToCompleter() {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)
        appearsOffline = false
        guard trimmed.count >= 2 else {
            results = []
            isSearching = false
            if lastPushedFragment != "" {
                completer.queryFragment = ""
                lastPushedFragment = ""
            }
            return
        }
        guard trimmed != lastPushedFragment else { return }
        lastPushedFragment = trimmed
        isSearching = true
        completer.queryFragment = trimmed
    }

    private static func formattedAddress(from placemark: CLPlacemark) -> String? {
        let streetLine: String? = {
            switch (placemark.thoroughfare, placemark.subThoroughfare) {
            case let (street?, num?): return "\(street), \(num)"
            case let (street?, nil): return street
            default: return nil
            }
        }()
        let parts = [
            streetLine ?? placemark.name,
            placemark.locality,
            placemark.administrativeArea,
            placemark.postalCode,
            placemark.country
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }

        var unique: [String] = []
        var seen = Set<String>()
        for part in parts where seen.insert(part).inserted {
            unique.append(part)
        }
        guard !unique.isEmpty else { return nil }
        return unique.joined(separator: ", ")
    }

    private static func startSearch(_ request: MKLocalSearch.Request) async throws -> MKLocalSearch.Response {
        try await withCheckedThrowingContinuation { cont in
            MKLocalSearch(request: request).start { response, error in
                if let error {
                    cont.resume(throwing: error)
                    return
                }
                guard let response else {
                    cont.resume(throwing: PlaceAddressSearchError.noMapItem)
                    return
                }
                cont.resume(returning: response)
            }
        }
    }
}

enum PlaceAddressSearchError: Error {
    case noMapItem
    case noCoordinate
}

extension PlaceAddressSearchCompleter: MKLocalSearchCompleterDelegate {
    nonisolated func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        let next = completer.results
        Task { @MainActor in
            self.results = next
            self.isSearching = false
            self.appearsOffline = false
        }
    }

    nonisolated func completer(_ completer: MKLocalSearchCompleter, didFailWithError error: Error) {
        let ns = error as NSError
        let offline = ns.domain == NSURLErrorDomain
            || ns.code == URLError.notConnectedToInternet.rawValue
            || ns.code == URLError.networkConnectionLost.rawValue
            || ns.code == CLError.network.rawValue
        Task { @MainActor in
            self.results = []
            self.isSearching = false
            self.appearsOffline = offline
        }
    }
}
