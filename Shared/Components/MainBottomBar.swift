import SwiftUI

/// Нижняя полоса главной: пять входов, золотой кружок у выбранного.
/// На главной кружка нет. Глубже пяти корней полоса скрыта.
struct MainBottomBar: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    private static let iconSize: CGFloat = 24
    private static let circleSize: CGFloat = 36

    var body: some View {
        HStack(spacing: 0) {
            ForEach(Self.items) { item in
                tabButton(item)
            }
        }
        .padding(.horizontal, 6)
        .padding(.vertical, 8)
        .background(
            Capsule()
                .fill(Color.black.opacity(0.55))
        )
        .padding(.horizontal, 16)
        .padding(.bottom, 6)
    }

    static func shows(on screen: NavigationManager.ALADDINScreen) -> Bool {
        // Новые линейные кнопки: только классическая главная и только стиль «Классика».
        screen == .main && AliveIconDiscStyle.current == .legacy
    }

    private func tabButton(_ item: Item) -> some View {
        let selected = navigationManager.currentScreen == item.screen
        return Button {
            HapticFeedback.impact(.light)
            navigationManager.openBottomTab(item.screen)
        } label: {
            VStack(spacing: 4) {
                ZStack {
                    if selected {
                        Circle()
                            .fill(Color.secondaryGold)
                            .frame(width: Self.circleSize, height: Self.circleSize)
                    }
                    item.icon
                        .frame(width: Self.iconSize, height: Self.iconSize)
                        .foregroundColor(.white)
                }
                .frame(height: Self.circleSize)
                Text(localizationManager.localized(item.titleKey))
                    .font(.system(size: 11, weight: .regular))
                    .foregroundColor(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier(item.identifier)
        .accessibilityLabel(localizationManager.localized(item.titleKey))
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private struct Item: Identifiable {
        let screen: NavigationManager.ALADDINScreen
        let titleKey: String
        let identifier: String
        let icon: AnyView

        var id: NavigationManager.ALADDINScreen { screen }
    }

    private static let items: [Item] = [
        Item(
            screen: .childRewards,
            titleKey: "main_tab_game",
            identifier: "main_tab_game",
            icon: AnyView(UnicornLineIcon())
        ),
        Item(
            screen: .childInterface,
            titleKey: "main_tab_aladdin_kids",
            identifier: "main_tab_aladdin_kids",
            icon: AnyView(ChildLineIcon())
        ),
        Item(
            screen: .notifications,
            titleKey: "main_tab_notifications",
            identifier: "main_tab_notifications",
            icon: AnyView(lineSymbol("bell"))
        ),
        Item(
            screen: .profile,
            titleKey: "main_tab_profile",
            identifier: "main_tab_profile",
            icon: AnyView(lineSymbol("person"))
        ),
        Item(
            screen: .devices,
            titleKey: "main_tab_devices",
            identifier: "main_tab_devices",
            icon: AnyView(lineSymbol("iphone"))
        )
    ]

    private static func lineSymbol(_ name: String) -> some View {
        Image(systemName: name)
            .font(.system(size: iconSize, weight: .regular))
    }
}

/// Единорог одной линией, того же веса, что системные значки полосы.
private struct UnicornLineIcon: View {
    var body: some View {
        UnicornLineShape()
            .stroke(
                Color.white,
                style: StrokeStyle(lineWidth: 1.6, lineCap: .round, lineJoin: .round)
            )
    }
}

/// Ребёнок одной линией. Системный значок ребёнка на части iOS пустой, поэтому рисуем сами.
private struct ChildLineIcon: View {
    var body: some View {
        ChildLineShape()
            .stroke(
                Color.white,
                style: StrokeStyle(lineWidth: 1.6, lineCap: .round, lineJoin: .round)
            )
    }
}

private struct ChildLineShape: Shape {
    func path(in rect: CGRect) -> Path {
        func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
            CGPoint(x: rect.minX + rect.width * x, y: rect.minY + rect.height * y)
        }
        var path = Path()
        path.addEllipse(in: CGRect(x: rect.minX + rect.width * 0.34, y: rect.minY + rect.height * 0.08, width: rect.width * 0.32, height: rect.height * 0.28))
        path.move(to: p(0.50, 0.38))
        path.addLine(to: p(0.50, 0.68))
        path.move(to: p(0.28, 0.50))
        path.addLine(to: p(0.72, 0.50))
        path.move(to: p(0.50, 0.68))
        path.addLine(to: p(0.32, 0.92))
        path.move(to: p(0.50, 0.68))
        path.addLine(to: p(0.68, 0.92))
        return path
    }
}

private struct UnicornLineShape: Shape {
    func path(in rect: CGRect) -> Path {
        let w = rect.width
        let h = rect.height
        func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
            CGPoint(x: rect.minX + w * x, y: rect.minY + h * y)
        }
        var path = Path()
        path.move(to: p(0.28, 0.62))
        path.addQuadCurve(to: p(0.62, 0.58), control: p(0.42, 0.78))
        path.addQuadCurve(to: p(0.70, 0.42), control: p(0.78, 0.52))
        path.addQuadCurve(to: p(0.48, 0.36), control: p(0.62, 0.28))
        path.move(to: p(0.52, 0.38))
        path.addLine(to: p(0.62, 0.12))
        path.addLine(to: p(0.66, 0.40))
        path.move(to: p(0.40, 0.40))
        path.addLine(to: p(0.34, 0.22))
        path.addLine(to: p(0.48, 0.38))
        path.move(to: p(0.22, 0.70))
        path.addQuadCurve(to: p(0.18, 0.88), control: p(0.10, 0.78))
        path.move(to: p(0.55, 0.72))
        path.addQuadCurve(to: p(0.78, 0.86), control: p(0.70, 0.70))
        return path
    }
}
