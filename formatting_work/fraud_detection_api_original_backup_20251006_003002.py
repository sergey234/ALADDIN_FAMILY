#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fraud Detection API - API сервер для интеграции с другими системами
"""

import asyncio
import logging
import os
import sys
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# Добавляем путь к модулям

from security.ai_agents.auto_learning_system import AutoLearningSystem  # noqa: E402
from security.ai_agents.enhanced_data_collector import EnhancedDataCollector  # noqa: E402
from security.ai_agents.russian_fraud_ml_models import RussianFraudMLModels  # noqa: E402

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание Flask приложения
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для интеграции

# Глобальные переменные
ml_models = None
data_collector = None
auto_learning = None

# HTML шаблон для веб-интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALADDIN AI Fraud Detection API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .api-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
        .get { background: #28a745; }
        .post { background: #007bff; }
        .endpoint-url { font-family: monospace; background: #e9ecef; padding: 5px; border-radius: 3px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.running { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.stopped { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .demo-section { background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .demo-form { margin: 10px 0; }
        .demo-form input, .demo-form select { margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        .demo-form button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .demo-form button:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; border: 1px solid #dee2e6; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #6c757d; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ALADDIN AI Fraud Detection API</h1>

        <div class="status {{ 'running' if api_status.is_running else 'stopped' }}">
            <strong>Статус API:</strong> {{ 'Запущен' if api_status.is_running else 'Остановлен' }}
            <br><strong>Время запуска:</strong> {{ api_status.start_time }}
            <br><strong>Версия:</strong> {{ api_status.version }}
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ api_status.total_requests }}</div>
                <div class="stat-label">Всего запросов</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ api_status.models_loaded }}</div>
                <div class="stat-label">Загружено моделей</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ api_status.uptime }}</div>
                <div class="stat-label">Время работы (мин)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ api_status.success_rate }}%</div>
                <div class="stat-label">Успешность</div>
            </div>
        </div>

        <div class="api-section">
            <h2>📊 API Endpoints</h2>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/status</span>
                <p>Получить статус API и системы</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/models/status</span>
                <p>Получить статус ML моделей</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-url">/api/predict/fraud-type</span>
                <p>Предсказать тип мошенничества</p>
                <p><strong>Параметры:</strong> severity, region, amount, source</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-url">/api/predict/severity</span>
                <p>Предсказать серьезность мошенничества</p>
                <p><strong>Параметры:</strong> fraud_type, region, amount</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="endpoint-url">/api/analyze/region-risk</span>
                <p>Анализ регионального риска</p>
                <p><strong>Параметры:</strong> region</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/data/collect</span>
                <p>Запустить сбор новых данных</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/models/retrain</span>
                <p>Переобучить ML модели</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/auto-learning/start</span>
                <p>Запустить автоматическое обучение 24/7</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="endpoint-url">/api/auto-learning/stop</span>
                <p>Остановить автоматическое обучение</p>
            </div>
        </div>

        <div class="demo-section">
            <h2>🧪 Демонстрация API</h2>

            <div class="demo-form">
                <h3>Предсказание типа мошенничества</h3>
                <select id="severity">
                    <option value="низкая">Низкая</option>
                    <option value="средняя">Средняя</option>
                    <option value="высокая">Высокая</option>
                    <option value="критическая">Критическая</option>
                </select>
                <select id="region">
                    <option value="Москва">Москва</option>
                    <option value="Санкт-Петербург">Санкт-Петербург</option>
                    <option value="Екатеринбург">Екатеринбург</option>
                    <option value="Казань">Казань</option>
                    <option value="Новосибирск">Новосибирск</option>
                </select>
                <input type="number" id="amount" placeholder="Сумма (руб)" value="500000">
                <input type="text" id="source" placeholder="Источник" value="банк">
                <button onclick="predictFraudType()">Предсказать тип</button>
            </div>

            <div id="prediction-result" class="result" style="display: none;"></div>

            <div class="demo-form">
                <h3>Анализ регионального риска</h3>
                <select id="region-risk">
                    <option value="Москва">Москва</option>
                    <option value="Санкт-Петербург">Санкт-Петербург</option>
                    <option value="Екатеринбург">Екатеринбург</option>
                    <option value="Казань">Казань</option>
                    <option value="Новосибирск">Новосибирск</option>
                </select>
                <button onclick="analyzeRegionRisk()">Анализировать риск</button>
            </div>

            <div id="risk-result" class="result" style="display: none;"></div>
        </div>
    </div>

    <script>
        function predictFraudType() {
            const data = {
                severity: document.getElementById('severity').value,
                region: document.getElementById('region').value,
                amount: parseInt(document.getElementById('amount').value),
                source: document.getElementById('source').value
            };

            fetch('/api/predict/fraud-type', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                const resultDiv = document.getElementById('prediction-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `
                    <h4>Результат предсказания:</h4>
                    <p><strong>Тип мошенничества:</strong> ${result.predicted_type || 'Ошибка'}</p>
                    <p><strong>Уверенность:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Все вероятности:</strong></p>
                    <ul>
                        ${Object.entries(result.all_probabilities || {}).map(([type, prob]) =>
                            `<li>${type}: ${(prob * 100).toFixed(1)}%</li>`
                        ).join('')}
                    </ul>
                `;
            })
            .catch(error => {
                document.getElementById('prediction-result').innerHTML = '<p style="color: red;">Ошибка: ' + error.message + '</p>';
            });
        }

        function analyzeRegionRisk() {
            const region = document.getElementById('region-risk').value;

            fetch(`/api/analyze/region-risk?region=${encodeURIComponent(region)}`)
            .then(response => response.json())
            .then(result => {
                const resultDiv = document.getElementById('risk-result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `
                    <h4>Анализ регионального риска:</h4>
                    <p><strong>Регион:</strong> ${region}</p>
                    <p><strong>Уровень риска:</strong> ${result.risk_level || 'Неопределен'}</p>
                    <p><strong>Оценка:</strong> ${result.risk_score || 'N/A'}/10</p>
                    <p><strong>Рекомендации:</strong> ${result.recommendations || 'Нет данных'}</p>
                `;
            })
            .catch(error => {
                document.getElementById('risk-result').innerHTML = '<p style="color: red;">Ошибка: ' + error.message + '</p>';
            });
        }
    </script>
</body>
</html>
"""

# API статус
api_status = {
    "is_running": False,
    "start_time": None,
    "version": "1.0.0",
    "total_requests": 0,
    "successful_requests": 0,
    "models_loaded": 0,
    "uptime": 0,
}


def initialize_api():
    """Инициализация API"""
    global ml_models, data_collector, auto_learning

    try:
        # Инициализация ML моделей
        ml_models = RussianFraudMLModels()
        api_status["models_loaded"] = (
            len(ml_models.models) if ml_models.models else 0
        )

        # Инициализация сборщика данных
        data_collector = EnhancedDataCollector()

        # Инициализация системы автоматического обучения
        auto_learning = AutoLearningSystem()

        api_status["is_running"] = True
        api_status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("✅ API инициализирован успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации API: {e}")
        api_status["is_running"] = False


@app.route("/")
def index():
    """Главная страница с веб-интерфейсом"""
    api_status["uptime"] = (
        int(
            (
                datetime.now()
                - datetime.strptime(
                    api_status["start_time"], "%Y-%m-%d %H:%M:%S"
                )
            ).total_seconds()
            / 60
        )
        if api_status["start_time"]
        else 0
    )

    return render_template_string(HTML_TEMPLATE, api_status=api_status)


@app.route("/api/status")
def get_status():
    """Получить статус API"""
    api_status["total_requests"] += 1
    api_status["successful_requests"] += 1

    return jsonify(
        {
            "status": "running" if api_status["is_running"] else "stopped",
            "version": api_status["version"],
            "start_time": api_status["start_time"],
            "uptime_minutes": api_status["uptime"],
            "total_requests": api_status["total_requests"],
            "success_rate": (
                round(
                    (
                        api_status["successful_requests"]
                        / api_status["total_requests"]
                    )
                    * 100,
                    2,
                )
                if api_status["total_requests"] > 0
                else 0
            ),
            "models_loaded": api_status["models_loaded"],
        }
    )


@app.route("/api/models/status")
def get_models_status():
    """Получить статус ML моделей"""
    api_status["total_requests"] += 1

    try:
        if ml_models and hasattr(ml_models, "model_metrics"):
            api_status["successful_requests"] += 1
            return jsonify(
                {
                    "status": "loaded",
                    "models": ml_models.model_metrics,
                    "total_models": (
                        len(ml_models.models) if ml_models.models else 0
                    ),
                }
            )
        else:
            return jsonify(
                {"status": "not_loaded", "error": "Модели не загружены"}
            )
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})


@app.route("/api/predict/fraud-type", methods=["POST"])
def predict_fraud_type():
    """Предсказать тип мошенничества"""
    api_status["total_requests"] += 1

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400

        # Валидация данных
        required_fields = ["severity", "region", "amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Отсутствует поле: {field}"}), 400

        # Предсказание
        if ml_models:
            prediction = ml_models.predict_fraud_type(
                severity=data["severity"],
                region=data["region"],
                amount=data["amount"],
                source=data.get("source", "неизвестно"),
            )

            api_status["successful_requests"] += 1
            return jsonify(prediction)
        else:
            return jsonify({"error": "ML модели не загружены"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict/severity", methods=["POST"])
def predict_severity():
    """Предсказать серьезность мошенничества"""
    api_status["total_requests"] += 1

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Отсутствуют данные"}), 400

        # Простая логика для демонстрации
        fraud_type = data.get("fraud_type", "неизвестно")
        amount = data.get("amount", 0)
        region = data.get("region", "неизвестно")

        # Определение серьезности
        severity_map = {
            "фишинг": 2,
            "банковское мошенничество": 4,
            "кибермошенничество": 3,
            "телефонное мошенничество": 1,
        }

        base_severity = severity_map.get(fraud_type, 2)

        if amount > 1000000:
            base_severity = min(base_severity + 1, 4)
        elif amount < 50000:
            base_severity = max(base_severity - 1, 1)

        if region == "Москва":
            base_severity = min(base_severity + 1, 4)

        severity_names = {
            1: "низкая",
            2: "средняя",
            3: "высокая",
            4: "критическая",
        }

        api_status["successful_requests"] += 1
        return jsonify(
            {
                "predicted_severity": severity_names[base_severity],
                "severity_level": base_severity,
                "confidence": base_severity / 4,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/region-risk")
def analyze_region_risk():
    """Анализ регионального риска"""
    api_status["total_requests"] += 1

    try:
        region = request.args.get("region", "Москва")

        # Простая логика для демонстрации
        risk_factors = {
            "Москва": {"score": 6.5, "level": "средний"},
            "Санкт-Петербург": {"score": 5.2, "level": "средний"},
            "Екатеринбург": {"score": 3.9, "level": "низкий"},
            "Казань": {"score": 3.2, "level": "низкий"},
            "Новосибирск": {"score": 3.6, "level": "низкий"},
        }

        risk_data = risk_factors.get(
            region, {"score": 5.0, "level": "неопределен"}
        )

        api_status["successful_requests"] += 1
        return jsonify(
            {
                "region": region,
                "risk_score": risk_data["score"],
                "risk_level": risk_data["level"],
                "recommendations": [
                    "Усилить мониторинг подозрительных транзакций",
                    "Провести обучение сотрудников по кибербезопасности",
                    "Внедрить системы раннего предупреждения",
                ],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/collect")
def collect_data():
    """Запустить сбор новых данных"""
    api_status["total_requests"] += 1

    try:
        if data_collector:
            # Запуск сбора данных в отдельном потоке
            def collect_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    data_collector.collect_comprehensive_data()
                )

            thread = threading.Thread(target=collect_async)
            thread.start()

            api_status["successful_requests"] += 1
            return jsonify(
                {
                    "status": "started",
                    "message": "Сбор данных запущен в фоновом режиме",
                }
            )
        else:
            return jsonify({"error": "Сборщик данных не инициализирован"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models/retrain")
def retrain_models():
    """Переобучить ML модели"""
    api_status["total_requests"] += 1

    try:
        if ml_models:
            # Переобучение моделей
            ml_models.create_region_analyzer()
            ml_models.create_fraud_classifier()
            ml_models.create_severity_predictor()
            ml_models.save_models()

            api_status["successful_requests"] += 1
            return jsonify(
                {"status": "completed", "message": "Модели переобучены"}
            )
        else:
            return jsonify({"error": "ML модели не инициализированы"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auto-learning/start")
def start_auto_learning():
    """Запустить автоматическое обучение 24/7"""
    api_status["total_requests"] += 1

    try:
        if auto_learning:
            auto_learning.start_auto_learning()

            api_status["successful_requests"] += 1
            return jsonify(
                {
                    "status": "started",
                    "message": "Автоматическое обучение запущено",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "error": "Система автоматического обучения не инициализирована"
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auto-learning/stop")
def stop_auto_learning():
    """Остановить автоматическое обучение"""
    api_status["total_requests"] += 1

    try:
        if auto_learning:
            auto_learning.stop_auto_learning()

            api_status["successful_requests"] += 1
            return jsonify(
                {
                    "status": "stopped",
                    "message": "Автоматическое обучение остановлено",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "error": "Система автоматического обучения не инициализирована"
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    return jsonify({"error": "Endpoint не найден"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500


def main():
    """Основная функция для запуска API сервера"""
    print("🚀 ЗАПУСК FRAUD DETECTION API СЕРВЕРА")
    print("=" * 50)

    # Инициализация API
    initialize_api()

    if api_status["is_running"]:
        print("✅ API инициализирован успешно")
        print("🌐 Веб-интерфейс: http://localhost:5000")
        print("📊 API документация: http://localhost:5000/api/status")
        print(
            "🤖 Автоматическое обучение: http://localhost:5000/api/auto-learning/start"
        )
        print("\n⏰ Сервер запущен. Нажмите Ctrl+C для остановки")

        # Запуск Flask сервера
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    else:
        print("❌ Ошибка инициализации API")


if __name__ == "__main__":
    main()
