#if DEBUG
private struct PaymentQRDiagnosticsView: View {
    @ObservedObject var viewModel: PaymentQRViewModel
    private static let formatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Diagnostics")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.white.opacity(0.95))
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Divider().blendMode(.overlay)
            
            VStack(alignment: .leading, spacing: 4) {
                infoRow("creationError", value: boolString(viewModel.creationError))
                infoRow("isLoading", value: boolString(viewModel.isLoading))
                infoRow("autoCheck", value: viewModel.isAutoCheckRunning ? "running" : "stopped")
                infoRow("paymentId", value: viewModel.paymentId ?? "nil")
                infoRow("last create", value: format(viewModel.lastCreatePaymentAt))
                infoRow("last retry", value: format(viewModel.lastRetryAt))
                infoRow("last auto start", value: format(viewModel.lastAutoCheckStartedAt))
                infoRow("last auto stop", value: format(viewModel.lastAutoCheckStoppedAt))
                infoRow("last check", value: format(viewModel.lastCheckPaymentStatusAt))
                infoRow("last success", value: format(viewModel.lastSuccessStatusAt))
                infoRow("last error", value: format(viewModel.lastErrorAt))
            }
        }
        .padding(12)
        .background(Color.black.opacity(0.72))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.white.opacity(0.2))
        )
    }
    
    private func boolString(_ value: Bool) -> String {
        value ? "true" : "false"
    }
    
    @ViewBuilder
    private func infoRow(_ title: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 6) {
            Text(title + ":")
                .font(.system(size: 11, weight: .semibold, design: .monospaced))
                .foregroundColor(.white.opacity(0.8))
            Text(value)
                .font(.system(size: 11, weight: .regular, design: .monospaced))
                .foregroundColor(.white.opacity(0.9))
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
    
    private func format(_ date: Date?) -> String {
        guard let date else { return "—" }
        return Self.formatter.string(from: date)
    }
}

struct NavigationDebugOverlay: View {
    let title: String
    let logEntries: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption)
                .fontWeight(.semibold)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Divider().blendMode(.overlay)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(Array(logEntries.suffix(24).enumerated()), id: \.offset) { _, entry in
                        Text(entry)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white.opacity(0.92))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 1)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 200)
        }
        .padding(12)
        .background(Color.black.opacity(0.7))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.white.opacity(0.2))
        )
    }
}
#endif

// MARK: - Preview

