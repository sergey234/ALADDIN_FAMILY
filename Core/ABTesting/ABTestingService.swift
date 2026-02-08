import Foundation

/**
 * 🎯 A/B Testing Service
 * Фреймворк для A/B тестирования
 * Управляет экспериментами и вариантами для оптимизации UX
 */

class ABTestingService {
    static let shared = ABTestingService()

    // MARK: - Properties

    private let userDefaults = UserDefaults.standard
    private let experimentsKey = "ab_testing_experiments"

    // Активные эксперименты
    private var activeExperiments: [String: Experiment] = [:]

    // MARK: - Initialization

    private init() {
        loadActiveExperiments()
        setupDefaultExperiments()
    }

    // MARK: - Public Methods

    /// Получить вариант для эксперимента
    func getVariant(for experimentName: String) -> String {
        // Сначала проверяем сохраненный вариант
        if let savedVariant = getSavedVariant(for: experimentName) {
            return savedVariant
        }

        // Если не сохранен, присваиваем новый вариант
        let experiment = getExperiment(experimentName)
        let variant = assignVariant(for: experiment)

        // Сохраняем выбор
        saveVariant(variant, for: experimentName)

        // Отслеживаем в аналитике
        trackExperimentAssignment(experimentName, variant)

        return variant
    }

    /// Проверить активен ли эксперимент
    func isExperimentActive(_ experimentName: String) -> Bool {
        return activeExperiments[experimentName]?.isActive ?? false
    }

    /// Отследить конверсию в эксперименте
    func trackConversion(experimentName: String, goal: String, variant: String? = nil) {
        let experimentVariant = variant ?? getVariant(for: experimentName)

        // Отправляем в аналитику
        ProductionMonitoringService.shared.trackUserAction(
            action: "ab_test_conversion",
            parameters: [
                "experiment": experimentName,
                "variant": experimentVariant,
                "goal": goal
            ]
        )

        #if DEBUG
        print("🎯 A/B Conversion: \(experimentName) - \(experimentVariant) - Goal: \(goal)")
        #endif
    }

    /// Отследить взаимодействие с вариантом
    func trackInteraction(experimentName: String, interaction: String, variant: String? = nil) {
        let experimentVariant = variant ?? getVariant(for: experimentName)

        ProductionMonitoringService.shared.trackUserAction(
            action: "ab_test_interaction",
            parameters: [
                "experiment": experimentName,
                "variant": experimentVariant,
                "interaction": interaction
            ]
        )
    }

    /// Завершить эксперимент и выбрать победителя
    func completeExperiment(_ experimentName: String, winner: String) {
        guard var experiment = activeExperiments[experimentName] else { return }

        experiment.winner = winner
        experiment.endDate = Date()
        experiment.isActive = false

        activeExperiments[experimentName] = experiment
        saveActiveExperiments()

        #if DEBUG
        print("🏆 Experiment Completed: \(experimentName) - Winner: \(winner)")
        #endif
    }

    /// Получить статистику экспериментов
    func getExperimentStats() -> [String: ExperimentStats] {
        var stats: [String: ExperimentStats] = [:]

        for (name, experiment) in activeExperiments {
            let variants = experiment.variants
            var variantCounts: [String: Int] = [:]

            // В реальном приложении здесь был бы запрос к аналитике
            // Пока возвращаем моковые данные
            for variant in variants {
                variantCounts[variant] = Int.random(in: 100...500)
            }

            stats[name] = ExperimentStats(
                experimentName: name,
                variants: variantCounts,
                totalParticipants: variantCounts.values.reduce(0, +),
                startDate: experiment.startDate,
                isActive: experiment.isActive,
                winner: experiment.winner
            )
        }

        return stats
    }

    // MARK: - Private Methods

    private func setupDefaultExperiments() {
        // Настройка экспериментов по умолчанию
        let experiments: [Experiment] = [
            Experiment(
                name: "onboarding_flow",
                variants: ["original", "simplified", "guided"],
                weights: [0.5, 0.3, 0.2],
                isActive: true,
                startDate: Date(),
                description: "Тестирование разных потоков онбординга"
            ),

            Experiment(
                name: "notification_style",
                variants: ["minimal", "detailed", "emoji_rich"],
                weights: [0.4, 0.4, 0.2],
                isActive: true,
                startDate: Date(),
                description: "Стиль отображения уведомлений"
            ),

            Experiment(
                name: "dashboard_layout",
                variants: ["cards", "list", "compact"],
                weights: [0.5, 0.3, 0.2],
                isActive: true,
                startDate: Date(),
                description: "Макет главного экрана"
            ),

            Experiment(
                name: "scan_animation",
                variants: ["spinner", "progress_bar", "pulse"],
                weights: [0.3, 0.4, 0.3],
                isActive: true,
                startDate: Date(),
                description: "Анимация сканирования угроз"
            ),

            Experiment(
                name: "error_messaging",
                variants: ["technical", "user_friendly", "humorous"],
                weights: [0.2, 0.6, 0.2],
                isActive: true,
                startDate: Date(),
                description: "Стиль сообщений об ошибках"
            )
        ]

        for experiment in experiments {
            if activeExperiments[experiment.name] == nil {
                activeExperiments[experiment.name] = experiment
            }
        }

        saveActiveExperiments()
    }

    private func getExperiment(_ name: String) -> Experiment {
        return activeExperiments[name] ?? Experiment(
            name: name,
            variants: ["control", "variant"],
            weights: [0.5, 0.5],
            isActive: true,
            startDate: Date(),
            description: "Auto-generated experiment"
        )
    }

    private func assignVariant(for experiment: Experiment) -> String {
        let randomValue = Double.random(in: 0..<1)
        var cumulativeWeight = 0.0

        for (index, weight) in experiment.weights.enumerated() {
            cumulativeWeight += weight
            if randomValue <= cumulativeWeight {
                return experiment.variants[index]
            }
        }

        // Fallback на первый вариант
        return experiment.variants.first ?? "control"
    }

    private func getSavedVariant(for experimentName: String) -> String? {
        let key = "ab_test_\(experimentName)_variant"
        return userDefaults.string(forKey: key)
    }

    private func saveVariant(_ variant: String, for experimentName: String) {
        let key = "ab_test_\(experimentName)_variant"
        userDefaults.set(variant, forKey: key)
    }

    private func trackExperimentAssignment(_ experimentName: String, _ variant: String) {
        ProductionMonitoringService.shared.trackUserAction(
            action: "ab_test_assignment",
            parameters: [
                "experiment": experimentName,
                "variant": variant
            ]
        )

        #if DEBUG
        print("🎯 A/B Assignment: \(experimentName) → \(variant)")
        #endif
    }

    private func loadActiveExperiments() {
        if let data = userDefaults.data(forKey: experimentsKey),
           let experiments = try? JSONDecoder().decode([String: Experiment].self, from: data) {
            activeExperiments = experiments
        }
    }

    private func saveActiveExperiments() {
        if let data = try? JSONEncoder().encode(activeExperiments) {
            userDefaults.set(data, forKey: experimentsKey)
        }
    }
}

// MARK: - Supporting Types

struct Experiment: Codable {
    let name: String
    let variants: [String]
    let weights: [Double]
    var isActive: Bool
    let startDate: Date
    var endDate: Date?
    var winner: String?
    let description: String
}

struct ExperimentStats {
    let experimentName: String
    let variants: [String: Int]  // variant -> count
    let totalParticipants: Int
    let startDate: Date
    let isActive: Bool
    let winner: String?
}