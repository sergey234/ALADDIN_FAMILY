import SwiftUI

// MARK: - Navigation (deployment target iOS 15.2)

/// `NavigationStack` is iOS 16+; use stack-style `NavigationView` on older OS.
struct WellnessNavigationStack<Content: View>: View {
    @ViewBuilder private let root: () -> Content

    init(@ViewBuilder root: @escaping () -> Content) {
        self.root = root
    }

    var body: some View {
        if #available(iOS 16.0, *) {
            NavigationStack(root: root)
        } else {
            NavigationView(content: root)
                .navigationViewStyle(StackNavigationViewStyle())
        }
    }
}

// MARK: - Sheet detents

struct WellnessSheetDetentsModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.presentationDetents([.medium, .large])
        } else {
            content
        }
    }
}

extension View {
    func wellnessSheetDetents() -> some View {
        modifier(WellnessSheetDetentsModifier())
    }
}

// MARK: - Multiline text (TextField `axis:` is iOS 16+)

struct WellnessMultilineField: View {
    let title: String
    @Binding var text: String
    var lineLimit: ClosedRange<Int> = 3...6
    var minHeight: CGFloat = 88

    var body: some View {
        if #available(iOS 16.0, *) {
            TextField(title, text: $text, axis: .vertical)
                .lineLimit(lineLimit)
        } else {
            ZStack(alignment: .topLeading) {
                if text.isEmpty {
                    Text(title)
                        .foregroundStyle(Color(UIColor.placeholderText))
                        .padding(.horizontal, 5)
                        .padding(.vertical, 8)
                        .allowsHitTesting(false)
                }
                TextEditor(text: $text)
                    .frame(minHeight: minHeight)
            }
        }
    }
}
