import SwiftUI
import UIKit

/// Pure height math for the Messages-style composer (testable, no View).
enum AladdinComposerMetrics {
    static let minLines = 1
    static let maxLines = 5
    static let fontSize: CGFloat = 16
    static let verticalPadding: CGFloat = 20

    static var lineHeight: CGFloat {
        UIFont.systemFont(ofSize: fontSize).lineHeight
    }

    static func lineCount(for text: String, width: CGFloat) -> Int {
        let trimmedWidth = max(width, 80)
        if text.isEmpty { return minLines }
        let font = UIFont.systemFont(ofSize: fontSize)
        let bounds = (text as NSString).boundingRect(
            with: CGSize(width: trimmedWidth, height: .greatestFiniteMagnitude),
            options: [.usesLineFragmentOrigin, .usesFontLeading],
            attributes: [.font: font],
            context: nil
        )
        let measured = Int(ceil(bounds.height / max(font.lineHeight, 1)))
        let newlineLines = text.split(separator: "\n", omittingEmptySubsequences: false).count
        return min(maxLines, max(minLines, max(measured, newlineLines)))
    }

    static func height(for text: String, width: CGFloat) -> CGFloat {
        CGFloat(lineCount(for: text, width: width)) * lineHeight + verticalPadding
    }
}

/// Shared composer: grows 1→5 lines, then scrolls inside the field.
struct AladdinComposerBar<Leading: View, ExtraTrailing: View>: View {
    @Binding var text: String
    var placeholder: String
    var doneTitle: String
    var accessibilityLabel: String
    var isSending: Bool = false
    var isDisabled: Bool = false
    var sendEnabled: Bool
    var focused: FocusState<Bool>.Binding
    var fieldAccessibilityIdentifier: String = "aladdin_composer_input"
    var sendAccessibilityIdentifier: String = "aladdin_composer_send"
    var onSend: () -> Void
    @ViewBuilder var leading: () -> Leading
    @ViewBuilder var extraTrailing: () -> ExtraTrailing

    @State private var fieldWidth: CGFloat = 220

    var body: some View {
        HStack(alignment: .bottom, spacing: 10) {
            leading()
            composerField
            sendButton
            extraTrailing()
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: 16)
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.top, 8)
        .padding(.bottom, 8)
        .modifier(AladdinKeyboardDoneToolbarModifier(title: doneTitle) {
            focused.wrappedValue = false
        })
    }

    private var composerField: some View {
        ZStack(alignment: .topLeading) {
            if text.isEmpty {
                Text(placeholder)
                    .foregroundColor(Color(UIColor.secondaryLabel))
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .allowsHitTesting(false)
            }
            TextEditor(text: $text)
                .font(.system(size: AladdinComposerMetrics.fontSize))
                .foregroundColor(Color(UIColor.label))
                .modifier(AladdinHideTextEditorBackground())
                .padding(.horizontal, 10)
                .padding(.vertical, 8)
                // Fixed height by line count → scroll inside the field past 5 lines.
                .frame(height: AladdinComposerMetrics.height(for: text, width: fieldWidth))
                .background(Color.clear)
                .focused(focused)
                .disabled(isDisabled || isSending)
                .accessibilityLabel(accessibilityLabel)
                .accessibilityIdentifier(fieldAccessibilityIdentifier)
                .background(
                    GeometryReader { geo in
                        Color.clear.preference(key: AladdinComposerWidthKey.self, value: geo.size.width)
                    }
                )
        }
        .onPreferenceChange(AladdinComposerWidthKey.self) { fieldWidth = $0 }
        .background(Color(UIColor.secondarySystemGroupedBackground))
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color(UIColor.separator), lineWidth: 1)
        )
        .cornerRadius(14)
    }

    private var sendButton: some View {
        Button(action: onSend) {
            if isSending {
                ProgressView()
                    .tint(.backgroundDark)
                    .scaleEffect(0.85)
                    .frame(width: 42, height: 42)
            } else {
                Image(systemName: "paperplane.fill")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(.backgroundDark)
                    .frame(width: 42, height: 42)
                    .background(sendEnabled ? Color.secondaryGold : Color.surfaceDark.opacity(0.5))
                    .cornerRadius(12)
            }
        }
        .disabled(!sendEnabled || isSending || isDisabled)
        .accessibilityIdentifier(sendAccessibilityIdentifier)
    }
}

private struct AladdinComposerWidthKey: PreferenceKey {
    static var defaultValue: CGFloat = 220
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

struct AladdinHideTextEditorBackground: ViewModifier {
    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.scrollContentBackground(.hidden)
        } else {
            content.background(AladdinTextEditorUIKitClearer())
        }
    }
}

/// Walks up from an embedded UIView to clear `UITextView.backgroundColor` (iOS 15.2).
private struct AladdinTextEditorUIKitClearer: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let probe = UIView(frame: .zero)
        probe.isUserInteractionEnabled = false
        probe.backgroundColor = .clear
        DispatchQueue.main.async {
            var node: UIView? = probe.superview
            while let current = node {
                if let textView = current as? UITextView {
                    textView.backgroundColor = .clear
                    textView.isOpaque = false
                    break
                }
                for sub in current.subviews where sub is UITextView {
                    (sub as? UITextView)?.backgroundColor = .clear
                    (sub as? UITextView)?.isOpaque = false
                }
                node = current.superview
            }
        }
        return probe
    }

    func updateUIView(_ uiView: UIView, context: Context) {}
}

struct AladdinKeyboardDoneToolbarModifier: ViewModifier {
    let title: String
    let action: () -> Void

    func body(content: Content) -> some View {
        content.toolbar(content: keyboardToolbar)
    }

    @ToolbarContentBuilder
    private func keyboardToolbar() -> some ToolbarContent {
        ToolbarItemGroup(placement: .keyboard) {
            Spacer()
            Button(action: action) {
                Text(title)
            }
        }
    }
}

struct AladdinChatKeyboardDismissModifier: ViewModifier {
    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.scrollDismissesKeyboard(.interactively)
        } else {
            content
        }
    }
}

extension View {
    func aladdinChatKeyboardDismiss() -> some View {
        modifier(AladdinChatKeyboardDismissModifier())
    }

    func aladdinKeyboardDoneToolbar(title: String, action: @escaping () -> Void) -> some View {
        modifier(AladdinKeyboardDoneToolbarModifier(title: title, action: action))
    }

    /// Scroll chat to the caret/last bubble when the keyboard begins showing (plan C).
    func aladdinScrollOnKeyboardShow(perform: @escaping () -> Void) -> some View {
        onReceive(NotificationCenter.default.publisher(for: UIResponder.keyboardWillShowNotification)) { _ in
            DispatchQueue.main.async(execute: perform)
        }
    }
}

struct AladdinNotificationDeniedBanner: View {
    let message: String
    let buttonTitle: String
    var onOpenSettings: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(message)
                .font(.caption)
                .foregroundColor(.orange)
            Button(buttonTitle, action: onOpenSettings)
                .font(.caption.weight(.semibold))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityIdentifier("aladdin_notification_denied_banner")
    }

    static func openSystemSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }
}
