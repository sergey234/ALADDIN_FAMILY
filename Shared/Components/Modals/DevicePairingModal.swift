import SwiftUI
import CoreImage.CIFilterBuiltins
import UIKit

/**
 * 📱 Device Pairing Modal (Экран сопряжения устройства)
 * Открывается после успешного логического создания устройства на сервере.
 * Показывает 3 метода физической привязки:
 * 1. QR-код
 * 2. Deep Link (кнопка Поделиться)
 * 3. Короткий PIN-код (если камера сломана)
 */
struct DevicePairingModal: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    // Данные от сервера после создания устройства
    let deviceName: String
    let ownerName: String
    let qrToken: String
    let shortPin: String

    @State private var showShareSheet = false

    private var inviteLink: String {
        "aladdin://bind?token=\(qrToken)"
    }

    private var formattedPin: String {
        DevicePairingLinkParser.formattedPIN(shortPin.filter { $0.isNumber })
    }

    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: Spacing.l) {
                        VStack(spacing: Spacing.s) {
                            Text(localizationManager.localized("device_pairing_title"))
                                .font(.h2)
                                .foregroundColor(.textPrimary)

                            Text(localizationManager.localized("device_pairing_intro", deviceName, ownerName))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                        .padding(.top, Spacing.m)

                        VStack(spacing: Spacing.m) {
                            Text(localizationManager.localized("device_pairing_method1_title"))
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)

                            VStack(spacing: Spacing.s) {
                                Text(localizationManager.localized("device_pairing_method1_hint"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.center)

                                if let qrImage = generateQRCode(from: inviteLink) {
                                    Image(uiImage: qrImage)
                                        .interpolation(.none)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 180, height: 180)
                                        .padding(Spacing.m)
                                        .background(Color.white)
                                        .cornerRadius(CornerRadius.large)
                                        .shadow(color: Color.black.opacity(0.1), radius: 10)
                                }
                            }
                            .padding(Spacing.cardPadding)
                            .frame(maxWidth: .infinity)
                            .background(Color.backgroundMedium.opacity(0.4))
                            .cornerRadius(CornerRadius.medium)
                        }

                        VStack(spacing: Spacing.m) {
                            Text(localizationManager.localized("device_pairing_method2_title"))
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)

                            Button(action: {
                                let generator = UIImpactFeedbackGenerator(style: .medium)
                                generator.impactOccurred()
                                showShareSheet = true
                            }) {
                                HStack {
                                    Image(systemName: "square.and.arrow.up")
                                    Text(localizationManager.localized("device_pairing_method2_button"))
                                }
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.m)
                                .background(Color.secondaryBlue.opacity(0.8))
                                .cornerRadius(CornerRadius.medium)
                            }
                        }

                        VStack(spacing: Spacing.m) {
                            Text(localizationManager.localized("device_pairing_method3_title"))
                                .font(.h4)
                                .foregroundColor(.primaryBlue)
                                .frame(maxWidth: .infinity, alignment: .leading)

                            VStack(spacing: Spacing.s) {
                                Text(localizationManager.localized("device_pairing_method3_hint"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.center)

                                Text(formattedPin)
                                    .font(.system(size: 32, weight: .black, design: .monospaced))
                                    .foregroundColor(Color(red: 1.0, green: 0.84, blue: 0.0))
                                    .padding(.vertical, Spacing.s)

                                Text(localizationManager.localized("device_pairing_pin_digits_hint", formattedPin.replacingOccurrences(of: "-", with: "")))
                                    .font(.caption2)
                                    .foregroundColor(.textSecondary)
                                    .multilineTextAlignment(.center)

                                Button(action: {
                                    UIPasteboard.general.string = shortPin.filter { $0.isNumber }
                                    let gen = UINotificationFeedbackGenerator()
                                    gen.notificationOccurred(.success)
                                }) {
                                    HStack {
                                        Image(systemName: "doc.on.doc")
                                        Text(localizationManager.localized("device_pairing_copy_pin"))
                                    }
                                    .font(.bodyBold)
                                    .foregroundColor(.primaryBlue)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, Spacing.s)
                                    .background(Color.backgroundMedium.opacity(0.5))
                                    .cornerRadius(CornerRadius.medium)
                                }
                            }
                            .padding(Spacing.cardPadding)
                            .frame(maxWidth: .infinity)
                            .background(Color.backgroundMedium.opacity(0.4))
                            .cornerRadius(CornerRadius.medium)
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("device_pairing_done")) {
                        dismiss()
                    }
                    .font(.bodyBold)
                    .foregroundColor(.white)
                }
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheet(activityItems: [localizationManager.localized("device_pairing_share_message", inviteLink)])
            }
        }
    }

    // MARK: - QR Generator
    private func generateQRCode(from string: String) -> UIImage? {
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        filter.message = Data(string.utf8)

        if let outputImage = filter.outputImage {
            let transform = CGAffineTransform(scaleX: 10, y: 10)
            let scaledImage = outputImage.transformed(by: transform)
            if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
                return UIImage(cgImage: cgImage)
            }
        }
        return nil
    }
}
