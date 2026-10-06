import SwiftUI

/// fsl-03 — одна «карта дома»: телефоны семьи + умные устройства (не хаб роутера).
/// fsl-04 — пауза 1 час через уже существующий block API.
struct HomeMapSection: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    let familyDevices: [Device]
    let onPauseFamilyDevice: (Device) -> Void
    let onResumeFamilyDevice: (Device) -> Void

    @StateObject private var iotModule = IoTSecurityModule()
    @State private var isLoadingIoT = false
    @State private var iotError: String?
    @State private var pausingIoTId: String?
    @State private var pauseBusyFamilyId: String?

    private var homeId: String { IoTHomeIdResolver.current }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("home_map_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                    Text(localizationManager.localized("home_map_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 8)
                Button {
                    navigationManager.navigateToDeviceHub(tab: .iot)
                } label: {
                    Text(localizationManager.localized("home_map_open_hub"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("home_map_open_hub")
            }

            Text(localizationManager.localized("home_map_pause_honest"))
                .font(.caption2)
                .foregroundColor(.white.opacity(0.65))
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityIdentifier("home_map_pause_honest")

            phonesBlock
            iotBlock
        }
        .padding(Spacing.cardPadding)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("home_map_section")
        .task { await refreshIoT() }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyDevicesDidChange"))) { _ in
            Task { await refreshIoT() }
        }
    }

    private var phonesBlock: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("home_map_phones_title"),
                systemImage: "iphone"
            )
            .font(.subheadline.weight(.semibold))
            .foregroundColor(.textPrimary)

            if familyDevices.isEmpty {
                Text(localizationManager.localized("home_map_phones_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                ForEach(familyDevices.prefix(6)) { device in
                    homePhoneRow(device)
                }
                if familyDevices.count > 6 {
                    Text(
                        String(
                            format: localizationManager.localized("home_map_more_phones"),
                            familyDevices.count - 6
                        )
                    )
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
                }
            }

            Button {
                navigationManager.navigateTo(.family)
            } label: {
                Text(localizationManager.localized("home_map_screen_time_link"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondaryGold)
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("home_map_screen_time_link")
        }
    }

    private func homePhoneRow(_ device: Device) -> some View {
        let paused = DevicePauseScheduler.isPaused(device.id) || device.status == .blocked
        let remaining = DevicePauseScheduler.remainingMinutes(deviceId: device.id)

        return HStack(spacing: Spacing.s) {
            Image(systemName: device.type.icon)
                .foregroundColor(.secondaryGold)
                .frame(width: 28)

            NavigationLink(destination: DeviceDetailScreen(device: device)) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(device.name)
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                        .lineLimit(1)
                    Text(device.owner)
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                        .lineLimit(1)
                }
            }
            .buttonStyle(.plain)

            Spacer(minLength: 4)

            if paused, let remaining {
                Text(
                    String(
                        format: localizationManager.localized("home_map_pause_remaining"),
                        remaining
                    )
                )
                .font(.caption2)
                .foregroundColor(.warningOrange)
            }

            if pauseBusyFamilyId == device.id {
                ProgressView().tint(.white)
            } else if paused {
                Button {
                    pauseBusyFamilyId = device.id
                    onResumeFamilyDevice(device)
                    pauseBusyFamilyId = nil
                } label: {
                    Text(localizationManager.localized("home_map_resume"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("home_map_resume_phone_\(device.id)")
            } else {
                Button {
                    pauseBusyFamilyId = device.id
                    onPauseFamilyDevice(device)
                    pauseBusyFamilyId = nil
                } label: {
                    Text(localizationManager.localized("home_map_pause_1h"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.warningOrange)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("home_map_pause_phone_\(device.id)")
            }
        }
        .padding(.vertical, Spacing.xs)
        .accessibilityIdentifier("home_map_phone_\(device.id)")
    }

    private var iotBlock: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Label(
                    localizationManager.localized("home_map_iot_title"),
                    systemImage: "house.fill"
                )
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)
                Spacer()
                if isLoadingIoT {
                    ProgressView().tint(.white).scaleEffect(0.8)
                }
            }

            if let iotError {
                Text(iotError)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
            } else if iotModule.iotDevices.isEmpty {
                Text(localizationManager.localized("home_map_iot_empty"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                ForEach(iotModule.iotDevices.prefix(8)) { device in
                    iotRow(device)
                }
            }
        }
    }

    private func iotRow(_ device: IoTDevice) -> some View {
        let paused = DevicePauseScheduler.isPaused(device.id) || device.status == .blocked
        let remaining = DevicePauseScheduler.remainingMinutes(deviceId: device.id)

        return HStack(spacing: Spacing.s) {
            Image(systemName: iotIcon(for: device.type))
                .foregroundColor(.secondaryGold)
                .frame(width: 28)

            VStack(alignment: .leading, spacing: 2) {
                Text(device.name)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.textPrimary)
                    .lineLimit(1)
                Text(device.type.displayName)
                    .font(.caption2)
                    .foregroundColor(.textSecondary)
            }

            Spacer(minLength: 4)

            if paused, let remaining {
                Text(
                    String(
                        format: localizationManager.localized("home_map_pause_remaining"),
                        remaining
                    )
                )
                .font(.caption2)
                .foregroundColor(.warningOrange)
            }

            if pausingIoTId == device.id {
                ProgressView().tint(.white)
            } else if paused {
                Button {
                    Task { await resumeIoT(device) }
                } label: {
                    Text(localizationManager.localized("home_map_resume"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.secondaryGold)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("home_map_resume_iot_\(device.id)")
            } else {
                Button {
                    Task { await pauseIoT(device) }
                } label: {
                    Text(localizationManager.localized("home_map_pause_1h"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.warningOrange)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("home_map_pause_iot_\(device.id)")
            }
        }
        .padding(.vertical, Spacing.xs)
        .accessibilityIdentifier("home_map_iot_\(device.id)")
    }

    private func refreshIoT() async {
        isLoadingIoT = true
        iotError = nil
        defer { isLoadingIoT = false }
        do {
            try await iotModule.loadStatus(homeId: homeId)
        } catch {
            iotError = localizationManager.localized("home_map_iot_load_failed")
        }
    }

    private func pauseIoT(_ device: IoTDevice) async {
        pausingIoTId = device.id
        defer { pausingIoTId = nil }
        do {
            try await iotModule.blockDevice(device.id)
            DevicePauseScheduler.schedulePause(deviceId: device.id, kind: .iot)
            HapticFeedback.notification(.success)
            await refreshIoT()
        } catch {
            iotError = error.localizedDescription
            HapticFeedback.notification(.error)
        }
    }

    private func resumeIoT(_ device: IoTDevice) async {
        pausingIoTId = device.id
        defer { pausingIoTId = nil }
        do {
            try await iotModule.unblockDevice(device.id)
            DevicePauseScheduler.cancel(deviceId: device.id)
            HapticFeedback.notification(.success)
            await refreshIoT()
        } catch {
            iotError = error.localizedDescription
            HapticFeedback.notification(.error)
        }
    }

    private func iotIcon(for type: IoTDeviceType) -> String {
        switch type {
        case .camera, .smartCamera: return "camera.fill"
        case .smartOutlet: return "powerplug.fill"
        case .light, .smartLight: return "lightbulb.fill"
        case .speaker, .smartSpeaker: return "speaker.wave.2.fill"
        case .door, .smartLock: return "lock.fill"
        case .thermostat, .smartThermostat: return "thermometer"
        default: return "wifi.router.fill"
        }
    }
}
