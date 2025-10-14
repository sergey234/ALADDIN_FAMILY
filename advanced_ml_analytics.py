#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced ML Analytics для ALADDIN Enhanced Services
Машинное обучение для предсказания проблем и аналитики

Автор: ALADDIN Security Team
Версия: 3.0
Дата: 2025-01-06
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sqlite3
import asyncio

# ML библиотеки
try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available. Install scikit-learn for ML features.")

class MLPredictor:
    """ML предсказатель для системы ALADDIN"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.db_path = "ml_analytics.db"
        self.init_database()
        
    def init_database(self):
        """Инициализация базы данных для ML данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                service_name TEXT NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                response_time REAL NOT NULL,
                error_rate REAL NOT NULL,
                request_count INTEGER NOT NULL,
                anomaly_score REAL,
                predicted_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                service_name TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                prediction_value REAL NOT NULL,
                confidence REAL NOT NULL,
                actual_value REAL,
                accuracy REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def prepare_features(self, metrics_data: List[Dict]) -> np.ndarray:
        """Подготовка признаков для ML модели"""
        features = []
        
        for metric in metrics_data:
            feature_vector = [
                metric.get('cpu_usage', 0),
                metric.get('memory_usage', 0),
                metric.get('response_time', 0),
                metric.get('error_rate', 0),
                metric.get('request_count', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_anomaly_detection(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Обучение модели обнаружения аномалий"""
        if not ML_AVAILABLE:
            return {"error": "ML libraries not available"}
        
        try:
            # Подготавливаем данные
            X = self.prepare_features(metrics_data)
            
            if len(X) < 10:
                return {"error": "Not enough data for training"}
            
            # Обучаем модель Isolation Forest
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X)
            
            # Сохраняем модель
            self.models['anomaly_detection'] = model
            
            # Предсказываем аномалии
            predictions = model.predict(X)
            scores = model.decision_function(X)
            
            # Сохраняем результаты
            self._save_ml_metrics(metrics_data, scores, predictions)
            
            return {
                "status": "success",
                "model_type": "IsolationForest",
                "training_samples": len(X),
                "anomalies_detected": int(np.sum(predictions == -1)),
                "anomaly_rate": float(np.mean(predictions == -1))
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    def train_status_prediction(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Обучение модели предсказания статуса сервисов"""
        if not ML_AVAILABLE:
            return {"error": "ML libraries not available"}
        
        try:
            # Подготавливаем данные
            X = self.prepare_features(metrics_data)
            y = [1 if m.get('status') == 'running' else 0 for m in metrics_data]
            
            if len(X) < 10:
                return {"error": "Not enough data for training"}
            
            # Разделяем данные
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Нормализуем данные
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Обучаем модель
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Предсказываем
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Сохраняем модели
            self.models['status_prediction'] = model
            self.scalers['status_prediction'] = scaler
            
            return {
                "status": "success",
                "model_type": "RandomForestClassifier",
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "accuracy": float(accuracy)
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    def predict_anomalies(self, current_metrics: Dict) -> Dict[str, Any]:
        """Предсказание аномалий для текущих метрик"""
        if 'anomaly_detection' not in self.models:
            return {"error": "Model not trained"}
        
        try:
            # Подготавливаем данные
            X = self.prepare_features([current_metrics])
            
            # Предсказываем
            prediction = self.models['anomaly_detection'].predict(X)[0]
            score = self.models['anomaly_detection'].decision_function(X)[0]
            
            return {
                "is_anomaly": bool(prediction == -1),
                "anomaly_score": float(score),
                "confidence": float(abs(score)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def predict_status(self, current_metrics: Dict) -> Dict[str, Any]:
        """Предсказание статуса сервиса"""
        if 'status_prediction' not in self.models or 'status_prediction' not in self.scalers:
            return {"error": "Model not trained"}
        
        try:
            # Подготавливаем данные
            X = self.prepare_features([current_metrics])
            X_scaled = self.scalers['status_prediction'].transform(X)
            
            # Предсказываем
            prediction = self.models['status_prediction'].predict(X_scaled)[0]
            probabilities = self.models['status_prediction'].predict_proba(X_scaled)[0]
            
            return {
                "predicted_status": "running" if prediction == 1 else "stopped",
                "confidence": float(max(probabilities)),
                "probabilities": {
                    "running": float(probabilities[1]),
                    "stopped": float(probabilities[0])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def generate_insights(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Генерация аналитических инсайтов"""
        if not metrics_data:
            return {"error": "No data available"}
        
        try:
            df = pd.DataFrame(metrics_data)
            
            insights = {
                "performance_trends": {
                    "avg_cpu": float(df['cpu_usage'].mean()),
                    "avg_memory": float(df['memory_usage'].mean()),
                    "avg_response_time": float(df['response_time'].mean()),
                    "total_requests": int(df['request_count'].sum())
                },
                "stability_metrics": {
                    "cpu_variance": float(df['cpu_usage'].var()),
                    "memory_variance": float(df['memory_usage'].var()),
                    "response_time_variance": float(df['response_time'].var())
                },
                "recommendations": []
            }
            
            # Генерируем рекомендации
            if df['cpu_usage'].mean() > 80:
                insights["recommendations"].append("High CPU usage detected. Consider scaling up.")
            
            if df['memory_usage'].mean() > 90:
                insights["recommendations"].append("High memory usage detected. Check for memory leaks.")
            
            if df['response_time'].mean() > 1.0:
                insights["recommendations"].append("Slow response times detected. Optimize performance.")
            
            if df['error_rate'].mean() > 0.05:
                insights["recommendations"].append("High error rate detected. Check service health.")
            
            return insights
            
        except Exception as e:
            return {"error": f"Insights generation failed: {str(e)}"}
    
    def _save_ml_metrics(self, metrics_data: List[Dict], scores: np.ndarray, predictions: np.ndarray):
        """Сохранение ML метрик в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for i, metric in enumerate(metrics_data):
                cursor.execute('''
                    INSERT INTO ml_metrics 
                    (timestamp, service_name, cpu_usage, memory_usage, response_time, 
                     error_rate, request_count, anomaly_score, predicted_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(),
                    metric.get('service_name', 'unknown'),
                    metric.get('cpu_usage', 0),
                    metric.get('memory_usage', 0),
                    metric.get('response_time', 0),
                    metric.get('error_rate', 0),
                    metric.get('request_count', 0),
                    float(scores[i]) if i < len(scores) else 0,
                    'anomaly' if i < len(predictions) and predictions[i] == -1 else 'normal'
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving ML metrics: {e}")
    
    def get_ml_history(self, hours: int = 24) -> List[Dict]:
        """Получение истории ML данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ml_metrics 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            '''.format(hours))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error getting ML history: {e}")
            return []

class AdvancedAnalytics:
    """Продвинутая аналитика для ALADDIN системы"""
    
    def __init__(self):
        self.ml_predictor = MLPredictor()
        self.trends_data = {}
        
    async def analyze_system_health(self, services_data: Dict) -> Dict[str, Any]:
        """Анализ здоровья системы"""
        analysis = {
            "overall_health": "healthy",
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "ml_predictions": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Анализируем каждый сервис
        for service_name, service_data in services_data.items():
            # Проверяем критические проблемы
            if service_data.get('status') == 'stopped':
                analysis["critical_issues"].append(f"Service {service_name} is stopped")
                analysis["overall_health"] = "critical"
            
            if service_data.get('cpu_usage', 0) > 95:
                analysis["critical_issues"].append(f"Service {service_name} has critical CPU usage")
                analysis["overall_health"] = "critical"
            
            if service_data.get('memory_usage', 0) > 95:
                analysis["critical_issues"].append(f"Service {service_name} has critical memory usage")
                analysis["overall_health"] = "critical"
            
            # Проверяем предупреждения
            if service_data.get('cpu_usage', 0) > 80:
                analysis["warnings"].append(f"Service {service_name} has high CPU usage")
            
            if service_data.get('memory_usage', 0) > 80:
                analysis["warnings"].append(f"Service {service_name} has high memory usage")
            
            # ML предсказания
            if ML_AVAILABLE:
                anomaly_prediction = self.ml_predictor.predict_anomalies(service_data)
                status_prediction = self.ml_predictor.predict_status(service_data)
                
                analysis["ml_predictions"][service_name] = {
                    "anomaly": anomaly_prediction,
                    "status": status_prediction
                }
        
        # Генерируем рекомендации
        if analysis["critical_issues"]:
            analysis["recommendations"].append("Immediate action required for critical issues")
        
        if analysis["warnings"]:
            analysis["recommendations"].append("Monitor services with warnings closely")
        
        if not analysis["critical_issues"] and not analysis["warnings"]:
            analysis["recommendations"].append("System is running smoothly")
        
        return analysis
    
    async def generate_trend_analysis(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Генерация анализа трендов"""
        if not historical_data:
            return {"error": "No historical data available"}
        
        try:
            df = pd.DataFrame(historical_data)
            
            trends = {
                "cpu_trend": self._calculate_trend(df, 'cpu_usage'),
                "memory_trend": self._calculate_trend(df, 'memory_usage'),
                "response_time_trend": self._calculate_trend(df, 'response_time'),
                "error_rate_trend": self._calculate_trend(df, 'error_rate'),
                "forecast": self._generate_forecast(df),
                "seasonality": self._detect_seasonality(df),
                "timestamp": datetime.now().isoformat()
            }
            
            return trends
            
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Расчет тренда для колонки"""
        if column not in df.columns:
            return {"trend": "unknown", "slope": 0, "r_squared": 0}
        
        try:
            # Простой линейный тренд
            x = np.arange(len(df))
            y = df[column].values
            
            # Удаляем NaN значения
            mask = ~np.isnan(y)
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) < 2:
                return {"trend": "insufficient_data", "slope": 0, "r_squared": 0}
            
            # Линейная регрессия
            slope = np.polyfit(x_clean, y_clean, 1)[0]
            
            # R-squared
            y_pred = slope * x_clean + np.mean(y_clean)
            ss_res = np.sum((y_clean - y_pred) ** 2)
            ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Определяем тренд
            if abs(slope) < 0.01:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            return {
                "trend": trend,
                "slope": float(slope),
                "r_squared": float(r_squared),
                "confidence": "high" if r_squared > 0.7 else "medium" if r_squared > 0.4 else "low"
            }
            
        except Exception as e:
            return {"trend": "error", "slope": 0, "r_squared": 0, "error": str(e)}
    
    def _generate_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Генерация прогноза"""
        try:
            # Простой прогноз на основе тренда
            forecast = {}
            
            for column in ['cpu_usage', 'memory_usage', 'response_time']:
                if column in df.columns:
                    recent_data = df[column].tail(10).values
                    if len(recent_data) > 0:
                        # Простое среднее с трендом
                        trend = np.polyfit(range(len(recent_data)), recent_data, 1)[0]
                        forecast[column] = {
                            "next_hour": float(recent_data[-1] + trend),
                            "next_6_hours": float(recent_data[-1] + trend * 6),
                            "next_24_hours": float(recent_data[-1] + trend * 24)
                        }
            
            return forecast
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Обнаружение сезонности"""
        try:
            seasonality = {}
            
            for column in ['cpu_usage', 'memory_usage', 'response_time']:
                if column in df.columns and len(df) > 24:  # Нужно минимум 24 точки данных
                    data = df[column].values
                    
                    # Простая проверка на сезонность (сравнение с предыдущим периодом)
                    if len(data) >= 48:  # 48 часов данных
                        current_period = data[-24:]
                        previous_period = data[-48:-24]
                        
                        correlation = np.corrcoef(current_period, previous_period)[0, 1]
                        
                        seasonality[column] = {
                            "has_seasonality": abs(correlation) > 0.5,
                            "correlation": float(correlation),
                            "pattern": "daily" if abs(correlation) > 0.5 else "none"
                        }
            
            return seasonality
            
        except Exception as e:
            return {"error": str(e)}

# Глобальный экземпляр
advanced_analytics = AdvancedAnalytics()

if __name__ == "__main__":
    print("🤖 ALADDIN Advanced ML Analytics")
    print("=" * 50)
    
    if not ML_AVAILABLE:
        print("⚠️  ML libraries not available. Install scikit-learn for full functionality.")
    else:
        print("✅ ML libraries available. Full functionality enabled.")
    
    print("📊 Advanced analytics ready for ALADDIN Enhanced Services")