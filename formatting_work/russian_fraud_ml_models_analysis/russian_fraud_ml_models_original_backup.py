#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Russian Fraud ML Models
Модели машинного обучения для детекции российского мошенничества
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RussianFraudMLModels:
    """
    Класс для создания и обучения ML моделей детекции российского мошенничества
    """

    def __init__(self, data_path: str = "data/demo_russian_fraud_data.json"):
        """
        Инициализация класса

        Args:
            data_path: Путь к файлу с данными о мошенничестве
        """
        self.data_path = data_path
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.feature_columns = []
        self.model_metrics = {}

        # Загрузка данных
        self.fraud_data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Загрузка данных о мошенничестве"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Загружены данные: {data['metadata']['total_records']} записей")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return {}

    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Подготовка данных для обучения

        Returns:
            Tuple[np.ndarray, np.ndarray]: X (признаки), y (целевые переменные)
        """
        # Создание датафрейма из данных
        records = []

        # Добавление отчетов ЦБ РФ
        for report in self.fraud_data.get('cbr_reports', []):
            records.append({
                'fraud_type': report['fraud_type'],
                'severity': report['severity'],
                'region': report['region'],
                'amount_lost': report['amount_lost'],
                'source': 'ЦБ РФ'
            })

        # Добавление новостных статей
        for article in self.fraud_data.get('news_articles', []):
            records.append({
                'fraud_type': article['fraud_type'],
                'severity': article['severity'],
                'region': article['region'],
                'amount_lost': self._estimate_amount_from_description(article['description']),
                'source': article['source']
            })

        df = pd.DataFrame(records)

        # Создание признаков
        df['severity_numeric'] = df['severity'].map({
            'низкая': 1,
            'средняя': 2,
            'высокая': 3,
            'критическая': 4
        })

        df['region_encoded'] = LabelEncoder().fit_transform(df['region'])
        df['source_encoded'] = LabelEncoder().fit_transform(df['source'])
        df['fraud_type_encoded'] = LabelEncoder().fit_transform(df['fraud_type'])

        # Нормализация суммы потерь
        df['amount_normalized'] = (
            (df['amount_lost'] - df['amount_lost'].min()) /
            (df['amount_lost'].max() - df['amount_lost'].min())
        )

        # Признаки для модели
        feature_columns = [
            'severity_numeric', 'region_encoded', 'source_encoded', 'amount_normalized'
        ]
        X = df[feature_columns].values
        y = df['fraud_type_encoded'].values

        self.feature_columns = feature_columns

        return X, y

    def _estimate_amount_from_description(self, description: str) -> int:
        """
        Оценка суммы потерь из описания

        Args:
            description: Описание случая мошенничества

        Returns:
            int: Оценочная сумма потерь
        """
        # Простая эвристика для оценки суммы
        description_lower = description.lower()

        if 'миллион' in description_lower or 'млн' in description_lower:
            return 1000000
        elif 'тысяч' in description_lower or 'тыс' in description_lower:
            return 100000
        elif 'сотен' in description_lower:
            return 500000
        else:
            return 50000  # Значение по умолчанию

    def create_fraud_classifier(self) -> Dict[str, Any]:
        """
        Создание классификатора типов мошенничества

        Returns:
            Dict[str, Any]: Метрики модели
        """
        try:
            logger.info("Создание классификатора типов мошенничества...")

            X, y = self._prepare_training_data()

            # Разделение на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Нормализация признаков
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            self.scalers['fraud_classifier'] = scaler

            # Обучение Random Forest
            rf_model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            )
            rf_model.fit(X_train_scaled, y_train)

            # Предсказания
            y_pred = rf_model.predict(X_test_scaled)

            # Метрики
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)

            metrics = {
                'model_name': 'Fraud Type Classifier',
                'algorithm': 'Random Forest',
                'accuracy': accuracy,
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'feature_importance': rf_model.feature_importances_.tolist(),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            self.models['fraud_classifier'] = rf_model
            self.model_metrics['fraud_classifier'] = metrics

            logger.info(f"Классификатор создан. Точность: {accuracy:.3f}")

            return metrics

        except Exception as e:
            logger.error(f"Ошибка создания классификатора: {e}")
            return {}

    def create_severity_predictor(self) -> Dict[str, Any]:
        """
        Создание предиктора серьезности мошенничества

        Returns:
            Dict[str, Any]: Метрики модели
        """
        try:
            logger.info("Создание предиктора серьезности мошенничества...")

            X, y = self._prepare_training_data()

            # Создание целевой переменной для серьезности
            records = []
            for report in self.fraud_data.get('cbr_reports', []):
                records.append({
                    'fraud_type_encoded': LabelEncoder().fit_transform([report['fraud_type']])[0],
                    'region_encoded': LabelEncoder().fit_transform([report['region']])[0],
                    'amount_normalized': report['amount_lost'] / 1000000,  # Нормализация
                    'severity': report['severity']
                })

            for article in self.fraud_data.get('news_articles', []):
                records.append({
                    'fraud_type_encoded': LabelEncoder().fit_transform([article['fraud_type']])[0],
                    'region_encoded': LabelEncoder().fit_transform([article['region']])[0],
                    'amount_normalized': self._estimate_amount_from_description(article['description']) / 1000000,
                    'severity': article['severity']
                })

            df = pd.DataFrame(records)
            X_severity = df[['fraud_type_encoded', 'region_encoded', 'amount_normalized']].values
            y_severity = df['severity'].map({
                'низкая': 1,
                'средняя': 2,
                'высокая': 3,
                'критическая': 4
            }).values

            # Разделение данных
            X_train, X_test, y_train, y_test = train_test_split(
                X_severity, y_severity, test_size=0.2, random_state=42, stratify=y_severity
            )

            # Обучение Gradient Boosting
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=6,
                learning_rate=0.1
            )
            gb_model.fit(X_train, y_train)

            # Предсказания
            y_pred = gb_model.predict(X_test)

            # Метрики
            accuracy = accuracy_score(y_test, y_pred)

            metrics = {
                'model_name': 'Severity Predictor',
                'algorithm': 'Gradient Boosting',
                'accuracy': accuracy,
                'feature_importance': gb_model.feature_importances_.tolist(),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            self.models['severity_predictor'] = gb_model
            self.model_metrics['severity_predictor'] = metrics

            logger.info(f"Предиктор серьезности создан. Точность: {accuracy:.3f}")

            return metrics

        except Exception as e:
            logger.error(f"Ошибка создания предиктора серьезности: {e}")
            return {}

    def create_region_analyzer(self) -> Dict[str, Any]:
        """
        Создание анализатора региональных трендов

        Returns:
            Dict[str, Any]: Метрики модели
        """
        try:
            logger.info("Создание анализатора региональных трендов...")

            # Создание данных для регионального анализа
            regional_data = []

            for region, count in self.fraud_data.get('fraud_patterns', {}).get('by_region', {}).items():
                regional_data.append({
                    'region': region,
                    'fraud_count': count,
                    'population_factor': self._get_population_factor(region),
                    'economic_factor': self._get_economic_factor(region),
                    'risk_score': min(count / 10, 10)  # Нормализация до 10
                })

            df = pd.DataFrame(regional_data)

            # Признаки
            X = df[['population_factor', 'economic_factor']].values
            y = df['risk_score'].values

            # Обучение модели регрессии
            from sklearn.linear_model import LinearRegression

            lr_model = LinearRegression()
            lr_model.fit(X, y)

            # Предсказания
            y_pred = lr_model.predict(X)

            # Метрики
            from sklearn.metrics import mean_squared_error, r2_score
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)

            metrics = {
                'model_name': 'Regional Risk Analyzer',
                'algorithm': 'Linear Regression',
                'mse': mse,
                'r2_score': r2,
                'coefficients': lr_model.coef_.tolist(),
                'training_samples': len(X)
            }

            self.models['region_analyzer'] = lr_model
            self.model_metrics['region_analyzer'] = metrics

            logger.info(f"Анализатор регионов создан. R²: {r2:.3f}")

            return metrics

        except Exception as e:
            logger.error(f"Ошибка создания анализатора регионов: {e}")
            return {}

    def _get_population_factor(self, region: str) -> float:
        """Получение фактора населения для региона"""
        population_factors = {
            'Москва': 1.0,
            'Санкт-Петербург': 0.7,
            'Екатеринбург': 0.4,
            'Казань': 0.3,
            'Новосибирск': 0.35,
            'Российская Федерация': 0.8
        }
        return population_factors.get(region, 0.2)

    def _get_economic_factor(self, region: str) -> float:
        """Получение экономического фактора для региона"""
        economic_factors = {
            'Москва': 1.0,
            'Санкт-Петербург': 0.8,
            'Екатеринбург': 0.6,
            'Казань': 0.5,
            'Новосибирск': 0.55,
            'Российская Федерация': 0.7
        }
        return economic_factors.get(region, 0.3)

    def save_models(self, models_dir: str = "data/ml_models"):
        """
        Сохранение обученных моделей

        Args:
            models_dir: Директория для сохранения моделей
        """
        try:
            os.makedirs(models_dir, exist_ok=True)

            for model_name, model in self.models.items():
                model_path = os.path.join(models_dir, f"{model_name}.joblib")
                joblib.dump(model, model_path)
                logger.info(f"Модель {model_name} сохранена: {model_path}")

            # Сохранение энкодеров и скейлеров
            scalers_path = os.path.join(models_dir, "scalers.joblib")
            joblib.dump(self.scalers, scalers_path)

            # Сохранение метрик
            metrics_path = os.path.join(models_dir, "model_metrics.json")
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_metrics, f, ensure_ascii=False, indent=2)

            logger.info(f"Все модели сохранены в {models_dir}")

        except Exception as e:
            logger.error(f"Ошибка сохранения моделей: {e}")

    def predict_fraud_type(self, severity: str, region: str, amount: float, source: str = "неизвестно") -> Dict[str, Any]:
        """
        Предсказание типа мошенничества

        Args:
            severity: Серьезность (низкая, средняя, высокая, критическая)
            region: Регион
            amount: Сумма потерь
            source: Источник информации

        Returns:
            Dict[str, Any]: Предсказание и уверенность
        """
        try:
            if 'fraud_classifier' not in self.models:
                return {"error": "Модель классификатора не обучена"}

            # Подготовка данных для предсказания
            severity_numeric = {
                'низкая': 1, 'средняя': 2, 'высокая': 3, 'критическая': 4
            }.get(severity, 2)
            region_encoded = 0  # Упрощенное кодирование
            source_encoded = 0
            amount_normalized = min(amount / 1000000, 1.0)  # Нормализация

            X_pred = np.array([[
                severity_numeric, region_encoded, source_encoded, amount_normalized
            ]])

            # Нормализация
            scaler = self.scalers.get('fraud_classifier')
            if scaler:
                X_pred = scaler.transform(X_pred)

            # Предсказание
            model = self.models['fraud_classifier']
            prediction = model.predict(X_pred)[0]
            probabilities = model.predict_proba(X_pred)[0]

            # Декодирование типа мошенничества
            fraud_types = [
                'банковское мошенничество', 'кибермошенничество', 'телефонное мошенничество',
                'интернет мошенничество', 'фишинг', 'карточное мошенничество', 'финансовая пирамида'
            ]

            predicted_type = (
                fraud_types[prediction] if prediction < len(fraud_types) else "неизвестный тип"
            )
            confidence = max(probabilities)

            return {
                'predicted_type': predicted_type,
                'confidence': confidence,
                'all_probabilities': dict(zip(fraud_types, probabilities))
            }

        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")
            return {"error": str(e)}

    def generate_model_report(self) -> Dict[str, Any]:
        """
        Генерация отчета по всем моделям

        Returns:
            Dict[str, Any]: Отчет по моделям
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(self.models),
            'models': self.model_metrics,
            'data_summary': {
                'total_records': self.fraud_data.get('metadata', {}).get('total_records', 0),
                'fraud_types': len(self.fraud_data.get('fraud_patterns', {}).get('by_type', {})),
                'regions': len(self.fraud_data.get('fraud_patterns', {}).get('by_region', {}))
            },
            'recommendations': [
                "Увеличить объем обучающих данных для повышения точности",
                "Добавить временные признаки для учета сезонности",
                "Интегрировать с реальными данными банков",
                "Реализовать онлайн-обучение моделей"
            ]
        }

        return report

def main():
    """Основная функция для демонстрации работы моделей"""
    print("🤖 СОЗДАНИЕ ML МОДЕЛЕЙ ДЛЯ ДЕТЕКЦИИ РОССИЙСКОГО МОШЕННИЧЕСТВА")
    print("=" * 70)

    try:
        # Создание экземпляра класса
        ml_models = RussianFraudMLModels()

        # Создание моделей
        print("📊 Создание классификатора типов мошенничества...")
        ml_models.create_fraud_classifier()
        
        print("📈 Создание предиктора серьезности...")
        ml_models.create_severity_predictor()
        
        print("🗺️ Создание анализатора регионов...")
        ml_models.create_region_analyzer()

        # Сохранение моделей
        print("💾 Сохранение моделей...")
        ml_models.save_models()

        # Тестирование предсказания
        print("🔍 Тестирование предсказания...")
        prediction = ml_models.predict_fraud_type(
            severity="высокая",
            region="Москва",
            amount=500000,
            source="банк"
        )

        print(f"Предсказанный тип мошенничества: {prediction.get('predicted_type', 'ошибка')}")
        print(f"Уверенность: {prediction.get('confidence', 0):.3f}")

        # Генерация отчета
        report = ml_models.generate_model_report()

        # Сохранение отчета
        report_path = "data/ml_models_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📋 Отчет сохранен: {report_path}")
        print("🎉 Модели машинного обучения созданы успешно!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
