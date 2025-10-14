#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML модели для анализа экстренных ситуаций
Применение Single Responsibility принципа
"""

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from typing import List, Tuple, Dict, Any


class EmergencyAnomalyDetector:
    """Детектор аномалий для экстренных ситуаций"""
    
    def __init__(self, contamination: float = 0.1):
        """
        Инициализация детектора аномалий
        
        Args:
            contamination: Доля аномалий в данных
        """
        self.contamination = contamination
        self.detector = IsolationForest(
            contamination=contamination, 
            random_state=42
        )
        self.is_trained = False
    
    def train(self, data: List[Dict[str, Any]]) -> bool:
        """
        Обучить детектор аномалий
        
        Args:
            data: Данные для обучения
            
        Returns:
            bool: True если обучение успешно
        """
        try:
            if not data:
                return False
            
            # Извлекаем признаки
            features = self._extract_features(data)
            if len(features) == 0:
                return False
            
            # Обучаем модель
            self.detector.fit(features)
            self.is_trained = True
            return True
            
        except Exception:
            return False
    
    def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[bool]:
        """
        Обнаружить аномалии в данных
        
        Args:
            data: Данные для анализа
            
        Returns:
            List[bool]: Список аномалий (True = аномалия)
        """
        try:
            if not self.is_trained or not data:
                return [False] * len(data)
            
            features = self._extract_features(data)
            if len(features) == 0:
                return [False] * len(data)
            
            predictions = self.detector.predict(features)
            return predictions == -1
            
        except Exception:
            return [False] * len(data)
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """
        Извлечь признаки из данных
        
        Args:
            data: Исходные данные
            
        Returns:
            np.ndarray: Матрица признаков
        """
        try:
            features = []
            for item in data:
                feature_vector = [
                    item.get('severity_score', 0),
                    item.get('time_score', 0),
                    item.get('location_score', 0),
                    item.get('type_score', 0)
                ]
                features.append(feature_vector)
            
            return np.array(features)
        except Exception:
            return np.array([])


class EmergencyClusterAnalyzer:
    """Анализатор кластеров для экстренных ситуаций"""
    
    def __init__(self, eps: float = 0.5, min_samples: int = 2):
        """
        Инициализация анализатора кластеров
        
        Args:
            eps: Максимальное расстояние между точками
            min_samples: Минимальное количество точек в кластере
        """
        self.eps = eps
        self.min_samples = min_samples
        self.clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, data: List[Dict[str, Any]]) -> bool:
        """
        Обучить анализатор кластеров
        
        Args:
            data: Данные для обучения
            
        Returns:
            bool: True если обучение успешно
        """
        try:
            if not data:
                return False
            
            # Извлекаем признаки
            features = self._extract_features(data)
            if len(features) == 0:
                return False
            
            # Масштабируем признаки
            features_scaled = self.scaler.fit_transform(features)
            
            # Обучаем модель
            self.clusterer.fit(features_scaled)
            self.is_trained = True
            return True
            
        except Exception:
            return False
    
    def analyze_clusters(self, data: List[Dict[str, Any]]) -> List[int]:
        """
        Проанализировать кластеры в данных
        
        Args:
            data: Данные для анализа
            
        Returns:
            List[int]: Метки кластеров
        """
        try:
            if not self.is_trained or not data:
                return [-1] * len(data)
            
            features = self._extract_features(data)
            if len(features) == 0:
                return [-1] * len(data)
            
            features_scaled = self.scaler.transform(features)
            return self.clusterer.fit_predict(features_scaled)
            
        except Exception:
            return [-1] * len(data)
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """
        Извлечь признаки из данных
        
        Args:
            data: Исходные данные
            
        Returns:
            np.ndarray: Матрица признаков
        """
        try:
            features = []
            for item in data:
                feature_vector = [
                    item.get('latitude', 0),
                    item.get('longitude', 0),
                    item.get('timestamp', 0),
                    item.get('severity', 0)
                ]
                features.append(feature_vector)
            
            return np.array(features)
        except Exception:
            return np.array([])


class EmergencyPatternRecognizer:
    """Распознаватель паттернов в экстренных ситуациях"""
    
    def __init__(self):
        self.patterns = {}
        self.is_trained = False
    
    def train(self, data: List[Dict[str, Any]]) -> bool:
        """
        Обучить распознаватель паттернов
        
        Args:
            data: Данные для обучения
            
        Returns:
            bool: True если обучение успешно
        """
        try:
            if not data:
                return False
            
            # Анализируем паттерны
            self.patterns = self._analyze_patterns(data)
            self.is_trained = True
            return True
            
        except Exception:
            return False
    
    def recognize_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Распознать паттерны в данных
        
        Args:
            data: Данные для анализа
            
        Returns:
            Dict[str, Any]: Распознанные паттерны
        """
        try:
            if not self.is_trained or not data:
                return {}
            
            patterns = {}
            
            # Анализируем временные паттерны
            patterns['temporal'] = self._analyze_temporal_patterns(data)
            
            # Анализируем пространственные паттерны
            patterns['spatial'] = self._analyze_spatial_patterns(data)
            
            # Анализируем типовые паттерны
            patterns['type'] = self._analyze_type_patterns(data)
            
            return patterns
            
        except Exception:
            return {}
    
    def _analyze_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ паттернов в данных"""
        try:
            patterns = {
                'temporal': self._analyze_temporal_patterns(data),
                'spatial': self._analyze_spatial_patterns(data),
                'type': self._analyze_type_patterns(data)
            }
            return patterns
        except Exception:
            return {}
    
    def _analyze_temporal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ временных паттернов"""
        try:
            timestamps = [item.get('timestamp', 0) for item in data]
            if not timestamps:
                return {}
            
            # Анализируем распределение по часам
            hours = [ts % 24 for ts in timestamps]
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Находим пиковые часы
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'peak_hours': peak_hours,
                'total_events': len(timestamps),
                'time_span': max(timestamps) - min(timestamps) if timestamps else 0
            }
        except Exception:
            return {}
    
    def _analyze_spatial_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ пространственных паттернов"""
        try:
            locations = [(item.get('latitude', 0), item.get('longitude', 0)) 
                        for item in data if item.get('latitude') and item.get('longitude')]
            
            if not locations:
                return {}
            
            # Вычисляем центр масс
            center_lat = sum(loc[0] for loc in locations) / len(locations)
            center_lon = sum(loc[1] for loc in locations) / len(locations)
            
            # Вычисляем радиус рассеивания
            distances = [np.sqrt((loc[0] - center_lat)**2 + (loc[1] - center_lon)**2) 
                        for loc in locations]
            max_distance = max(distances) if distances else 0
            
            return {
                'center': (center_lat, center_lon),
                'max_distance': max_distance,
                'total_locations': len(locations)
            }
        except Exception:
            return {}
    
    def _analyze_type_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ типовых паттернов"""
        try:
            types = [item.get('type', 'unknown') for item in data]
            type_counts = {}
            for event_type in types:
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            # Находим наиболее частые типы
            common_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'type_distribution': type_counts,
                'most_common': common_types[:3],
                'total_types': len(type_counts)
            }
        except Exception:
            return {}