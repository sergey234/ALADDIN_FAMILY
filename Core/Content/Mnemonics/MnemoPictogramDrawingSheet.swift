import PencilKit
import SwiftUI
import UIKit

/// Mini canvas for co-created mnemo pictograms (B11-T03) → `MnemonicPictogramStore`.
struct MnemoPictogramDrawingSheet: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    let itemId: String
    var onSaved: (() -> Void)?

    @State private var drawing = PKDrawing()
    @State private var feedbackKey: String?

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 14) {
                Text(localizationManager.localized("child_mnemo_pictogram_draw_subtitle"))
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)

                MnemoPictogramCanvasRepresentable(drawing: $drawing)
                    .frame(height: 300)
                    .background(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .fill(Color.white)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(Color.purple.opacity(0.35), lineWidth: 1)
                    )
                    .accessibilityIdentifier("child_mnemo_pictogram_canvas")

                if let feedbackKey {
                    Text(localizationManager.localized(feedbackKey))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(feedbackKey.contains("empty") ? .orange : .green)
                }

                HStack(spacing: 10) {
                    Button(localizationManager.localized("child_mnemo_pictogram_draw_clear")) {
                        drawing = PKDrawing()
                        feedbackKey = nil
                    }
                    .buttonStyle(.bordered)

                    Button(localizationManager.localized("child_mnemo_pictogram_draw_save")) {
                        savePictogram()
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.purple)
                    .accessibilityIdentifier("child_mnemo_pictogram_draw_save")
                }
            }
            .padding(16)
            .navigationTitle(localizationManager.localized("child_mnemo_pictogram_draw_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("child_interface_back")) {
                        dismiss()
                    }
                }
            }
        }
        .accessibilityIdentifier("child_mnemo_pictogram_draw_sheet")
    }

    private func savePictogram() {
        guard !drawing.bounds.isEmpty else {
            feedbackKey = "child_mnemo_pictogram_draw_empty_error"
            return
        }
        let scale = UIScreen.main.scale
        let image = drawing.image(from: drawing.bounds.insetBy(dx: -8, dy: -8), scale: scale)
        do {
            _ = try MnemonicPictogramStore.shared.saveImage(
                image,
                itemId: itemId,
                childId: MnemonicPictogramStore.activeChildId()
            )
            feedbackKey = "child_mnemo_pictogram_draw_saved_ok"
            MasterLogger.shared.business("MNEMO-B11 pictogram saved itemId=\(itemId)")
            onSaved?()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                dismiss()
            }
        } catch {
            feedbackKey = "child_mnemo_pictogram_draw_save_error"
        }
    }
}

private struct MnemoPictogramCanvasRepresentable: UIViewRepresentable {
    @Binding var drawing: PKDrawing

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.delegate = context.coordinator
        canvas.drawingPolicy = .anyInput
        canvas.tool = PKInkingTool(.marker, color: .systemPurple, width: 8)
        canvas.backgroundColor = .white
        canvas.drawing = drawing
        return canvas
    }

    func updateUIView(_ uiView: PKCanvasView, context: Context) {
        if uiView.drawing != drawing {
            uiView.drawing = drawing
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(drawing: $drawing)
    }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        @Binding var drawing: PKDrawing

        init(drawing: Binding<PKDrawing>) {
            _drawing = drawing
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            drawing = canvasView.drawing
        }
    }
}
