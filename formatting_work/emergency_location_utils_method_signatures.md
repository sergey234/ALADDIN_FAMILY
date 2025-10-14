# Сигнатуры методов emergency_location_utils.py

## LocationDistanceCalculator

### 1. calculate_distance
```python
@staticmethod
def calculate_distance(
    coord1: Tuple[float, float], 
    coord2: Tuple[float, float]
) -> float
```
- **Аргументы**: 2 (coord1, coord2)
- **Возвращает**: float
- **Тип**: staticmethod

### 2. is_location_in_radius
```python
@staticmethod
def is_location_in_radius(
    center: Tuple[float, float],
    point: Tuple[float, float],
    radius_km: float
) -> bool
```
- **Аргументы**: 3 (center, point, radius_km)
- **Возвращает**: bool
- **Тип**: staticmethod

## LocationServiceFinder

### 3. find_nearest_services
```python
@staticmethod
def find_nearest_services(
    location: Tuple[float, float], 
    services: List[Dict[str, Any]]
) -> List[Dict[str, Any]]
```
- **Аргументы**: 2 (location, services)
- **Возвращает**: List[Dict[str, Any]]
- **Тип**: staticmethod

### 4. get_services_in_radius
```python
@staticmethod
def get_services_in_radius(
    location: Tuple[float, float],
    services: List[Dict[str, Any]],
    radius_km: float
) -> List[Dict[str, Any]]
```
- **Аргументы**: 3 (location, services, radius_km)
- **Возвращает**: List[Dict[str, Any]]
- **Тип**: staticmethod

## LocationValidator

### 5. validate_coordinates
```python
@staticmethod
def validate_coordinates(lat: float, lon: float) -> bool
```
- **Аргументы**: 2 (lat, lon)
- **Возвращает**: bool
- **Тип**: staticmethod

### 6. validate_location_accuracy
```python
@staticmethod
def validate_location_accuracy(accuracy: float) -> bool
```
- **Аргументы**: 1 (accuracy)
- **Возвращает**: bool
- **Тип**: staticmethod

### 7. is_location_verified
```python
@staticmethod
def is_location_verified(location_data: Dict[str, Any]) -> bool
```
- **Аргументы**: 1 (location_data)
- **Возвращает**: bool
- **Тип**: staticmethod

## LocationClusterAnalyzer

### 8. calculate_cluster_center
```python
@staticmethod
def calculate_cluster_center(
    points: List[Tuple[float, float]]
) -> Tuple[float, float]
```
- **Аргументы**: 1 (points)
- **Возвращает**: Tuple[float, float]
- **Тип**: staticmethod

### 9. calculate_cluster_radius
```python
@staticmethod
def calculate_cluster_radius(
    points: List[Tuple[float, float]], 
    center: Tuple[float, float]
) -> float
```
- **Аргументы**: 2 (points, center)
- **Возвращает**: float
- **Тип**: staticmethod

## Общая статистика

- **Всего методов**: 9
- **Статических методов**: 9 (100%)
- **Методов класса**: 0 (0%)
- **Свойств**: 0 (0%)
- **Приватных методов**: 0 (0%)
- **Защищенных методов**: 0 (0%)

## Типы возвращаемых значений

- **float**: 3 метода
- **bool**: 4 метода  
- **List[Dict[str, Any]]**: 2 метода
- **Tuple[float, float]**: 1 метод