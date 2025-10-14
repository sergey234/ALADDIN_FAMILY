#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для работы с местоположением в экстренных ситуациях
Применение Single Responsibility принципа
"""

import geopy.distance
from typing import List, Dict, Any, Tuple, Optional


class LocationDistanceCalculator:
    """Калькулятор расстояний между точками"""
    
    @staticmethod
    def calculate_distance(coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """
        Рассчитать расстояние между двумя точками в километрах
        
        Args:
            coord1: Первая точка (широта, долгота)
            coord2: Вторая точка (широта, долгота)
            
        Returns:
            float: Расстояние в километрах
        """
        try:
            return geopy.distance.geodesic(coord1, coord2).kilometers
        except Exception:
            return 0.0
    
    @staticmethod
    def is_location_in_radius(center: Tuple[float, float], 
                            point: Tuple[float, float], 
                            radius_km: float) -> bool:
        """
        Проверить, находится ли точка в радиусе от центра
        
        Args:
            center: Центральная точка
            point: Проверяемая точка
            radius_km: Радиус в километрах
            
        Returns:
            bool: True если точка в радиусе
        """
        distance = LocationDistanceCalculator.calculate_distance(center, point)
        return distance <= radius_km


class LocationServiceFinder:
    """Поиск ближайших служб к местоположению"""
    
    @staticmethod
    def find_nearest_services(location: Tuple[float, float], 
                            services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Найти ближайшие службы к местоположению
        
        Args:
            location: Координаты местоположения
            services: Список служб с координатами
            
        Returns:
            List[Dict]: Список служб, отсортированный по расстоянию
        """
        try:
            service_distances = []
            for service in services:
                service_coords = service.get('coordinates')
                if service_coords:
                    distance = LocationDistanceCalculator.calculate_distance(
                        location, service_coords
                    )
                    service_distances.append({
                        'service': service,
                        'distance': distance
                    })
            
            # Сортируем по расстоянию
            service_distances.sort(key=lambda x: x['distance'])
            return service_distances
            
        except Exception:
            return []
    
    @staticmethod
    def get_services_in_radius(location: Tuple[float, float], 
                             services: List[Dict[str, Any]], 
                             radius_km: float) -> List[Dict[str, Any]]:
        """
        Получить службы в радиусе от местоположения
        
        Args:
            location: Координаты местоположения
            services: Список служб
            radius_km: Радиус в километрах
            
        Returns:
            List[Dict]: Службы в радиусе
        """
        try:
            services_in_radius = []
            for service in services:
                service_coords = service.get('coordinates')
                if service_coords:
                    if LocationDistanceCalculator.is_location_in_radius(
                        location, service_coords, radius_km
                    ):
                        services_in_radius.append(service)
            
            return services_in_radius
        except Exception:
            return []


class LocationValidator:
    """Валидатор местоположений"""
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Проверить валидность координат
        
        Args:
            lat: Широта
            lon: Долгота
            
        Returns:
            bool: True если координаты валидны
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @staticmethod
    def validate_location_accuracy(accuracy: float) -> bool:
        """
        Проверить точность определения местоположения
        
        Args:
            accuracy: Точность в метрах
            
        Returns:
            bool: True если точность приемлема
        """
        return accuracy <= 100.0  # Точность в метрах
    
    @staticmethod
    def is_location_verified(location_data: Dict[str, Any]) -> bool:
        """
        Проверить, верифицировано ли местоположение
        
        Args:
            location_data: Данные местоположения
            
        Returns:
            bool: True если местоположение верифицировано
        """
        return location_data.get('is_verified', False)


class LocationClusterAnalyzer:
    """Анализатор кластеров местоположений"""
    
    @staticmethod
    def calculate_cluster_center(points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Рассчитать центр кластера
        
        Args:
            points: Список точек
            
        Returns:
            Tuple[float, float]: Центр кластера
        """
        try:
            if not points:
                return (0.0, 0.0)
            
            lat_sum = sum(point[0] for point in points)
            lon_sum = sum(point[1] for point in points)
            
            return (lat_sum / len(points), lon_sum / len(points))
        except Exception:
            return (0.0, 0.0)
    
    @staticmethod
    def calculate_cluster_radius(points: List[Tuple[float, float]], 
                               center: Tuple[float, float]) -> float:
        """
        Рассчитать радиус кластера
        
        Args:
            points: Список точек
            center: Центр кластера
            
        Returns:
            float: Радиус в километрах
        """
        try:
            max_distance = 0
            for point in points:
                distance = LocationDistanceCalculator.calculate_distance(center, point)
                max_distance = max(max_distance, distance)
            return round(max_distance, 2)
        except Exception:
            return 0.0