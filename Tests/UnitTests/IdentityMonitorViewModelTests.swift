import XCTest
@testable import ALADDIN

@MainActor
final class IdentityMonitorViewModelTests: XCTestCase {

    private var viewModel: IdentityMonitorViewModel!

    override func setUpWithError() throws {
        try super.setUpWithError()
        viewModel = IdentityMonitorViewModel()
    }

    override func tearDownWithError() throws {
        AppConfig.authToken = nil
        var settings = ProtectionSettingsManager.shared.settings
        settings.setEnabled(.fraud, false)
        ProtectionSettingsManager.shared.settings = settings
        ProtectionSettingsManager.shared.saveSettings()
        viewModel = nil
        try super.tearDownWithError()
    }

    func testInitialFraudStateComesFromProtectionSettings() {
        var settings = ProtectionSettingsManager.shared.settings
        settings.setEnabled(.fraud, true)
        ProtectionSettingsManager.shared.settings = settings
        viewModel.syncFraudEnabledFromLocalSettings()
        XCTAssertTrue(viewModel.isFraudProtectionEnabled)
    }

    func testSetFraudProtectionWithoutAuthShowsError() async {
        AppConfig.authToken = nil
        await viewModel.setFraudProtectionEnabled(true)
        XCTAssertNotNil(viewModel.errorMessage)
    }

    func testCreditMonitorRequiresEnabledProtection() async {
        viewModel.syncFraudEnabledFromLocalSettings()
        let initialVerdict = viewModel.monitorVerdict
        await viewModel.runCreditMonitor()
        XCTAssertEqual(viewModel.monitorVerdict, initialVerdict)
    }
}
