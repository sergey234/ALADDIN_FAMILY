#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Elasticsearch Simulator
Симулятор Elasticsearch для поиска по логам

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-08
"""

import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from core.base import ComponentStatus
from core.security_base import SecurityBase


class LogLevel(Enum):
    """Уровни логов"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Запись лога"""
    timestamp: datetime
    level: LogLevel
    component: str
    message: str
    metadata: Dict[str, Any]
    log_id: str = ""


class ElasticsearchSimulator(SecurityBase):
    """Симулятор Elasticsearch для поиска по логам"""
    
    def __init__(self):
        super().__init__("ElasticsearchSimulator")
        self.service_name = "ElasticsearchSimulator"
        self.status = ComponentStatus.RUNNING
        
        # Хранилище логов
        self.logs: List[LogEntry] = []
        self.indices: Dict[str, List[LogEntry]] = {}
        
        # Статистика
        self.stats = {
            'total_logs': 0,
            'indexed_logs': 0,
            'search_queries': 0,
            'last_indexed': None
        }
        
        # Инициализация
        self._create_indices()
        self._load_sample_logs()
        
        self.logger.info("ElasticsearchSimulator инициализирован")
    
    def _create_indices(self):
        """Создание индексов"""
        self.indices = {
            'security_logs': [],
            'system_logs': [],
            'error_logs': [],
            'performance_logs': [],
            'family_logs': []
        }
        self.logger.info(f"Создано {len(self.indices)} индексов")
    
    def _load_sample_logs(self):
        """Загрузка примеров логов"""
        sample_logs = [
            LogEntry(
                timestamp=datetime.now() - timedelta(minutes=5),
                level=LogLevel.INFO,
                component="SecurityMonitoringManager",
                message="Система мониторинга безопасности активна",
                metadata={"status": "active", "uptime": "2h 15m"},
                log_id="log_001"
            ),
            LogEntry(
                timestamp=datetime.now() - timedelta(minutes=4),
                level=LogLevel.WARNING,
                component="PerformanceOptimizer",
                message="Высокая нагрузка на CPU: 85%",
                metadata={"cpu_usage": 85.2, "threshold": 80},
                log_id="log_002"
            ),
            LogEntry(
                timestamp=datetime.now() - timedelta(minutes=3),
                level=LogLevel.ERROR,
                component="DatabaseManager",
                message="Ошибка подключения к базе данных",
                metadata={"error_code": "DB_CONN_001", "retry_count": 3},
                log_id="log_003"
            ),
            LogEntry(
                timestamp=datetime.now() - timedelta(minutes=2),
                level=LogLevel.INFO,
                component="AuthenticationManager",
                message="Пользователь успешно авторизован",
                metadata={"user_id": "user_123", "ip": "192.168.1.100"},
                log_id="log_004"
            ),
            LogEntry(
                timestamp=datetime.now() - timedelta(minutes=1),
                level=LogLevel.CRITICAL,
                component="ThreatDetectionAgent",
                message="Обнаружена критическая угроза безопасности",
                metadata={"threat_type": "malware", "severity": "critical"},
                log_id="log_005"
            ),
            LogEntry(
                timestamp=datetime.now() - timedelta(seconds=30),
                level=LogLevel.INFO,
                component="FamilySecurityManager",
                message="Родительский контроль активирован для ребенка",
                metadata={"child_id": "child_001", "age": 12},
                log_id="log_006"
            )
        ]
        
        for log in sample_logs:
            self.index_log(log)
        
        self.logger.info(f"Загружено {len(sample_logs)} примеров логов")
    
    def index_log(self, log_entry: LogEntry) -> bool:
        """Индексация лога"""
        try:
            # Генерация ID если не задан
            if not log_entry.log_id:
                log_entry.log_id = f"log_{int(time.time() * 1000)}"
            
            # Добавление в общее хранилище
            self.logs.append(log_entry)
            self.stats['total_logs'] += 1
            
            # Добавление в соответствующие индексы
            self._add_to_indices(log_entry)
            
            self.stats['indexed_logs'] += 1
            self.stats['last_indexed'] = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка индексации лога: {e}")
            return False
    
    def _add_to_indices(self, log_entry: LogEntry):
        """Добавление лога в соответствующие индексы"""
        # Все логи идут в system_logs
        self.indices['system_logs'].append(log_entry)
        
        # По уровню
        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.indices['error_logs'].append(log_entry)
        
        # По компоненту
        if 'security' in log_entry.component.lower() or 'threat' in log_entry.component.lower():
            self.indices['security_logs'].append(log_entry)
        
        if 'performance' in log_entry.component.lower() or 'cpu' in log_entry.message.lower():
            self.indices['performance_logs'].append(log_entry)
        
        if 'family' in log_entry.component.lower() or 'child' in log_entry.message.lower():
            self.indices['family_logs'].append(log_entry)
    
    def search(self, query: str, index: str = "system_logs", 
              level: Optional[LogLevel] = None, 
              component: Optional[str] = None,
              time_range: Optional[tuple] = None,
              use_regex: bool = False,
              case_sensitive: bool = False,
              limit: int = 100) -> Dict[str, Any]:
        """Поиск по логам с поддержкой регулярных выражений"""
        try:
            self.stats['search_queries'] += 1
            
            # Получение логов из индекса
            logs = self.indices.get(index, self.logs)
            
            # Фильтрация по уровню
            if level:
                logs = [log for log in logs if log.level == level]
            
            # Фильтрация по компоненту
            if component:
                logs = [log for log in logs if component.lower() in log.component.lower()]
            
            # Фильтрация по времени
            if time_range:
                start_time, end_time = time_range
                logs = [log for log in logs if start_time <= log.timestamp <= end_time]
            
            # Поиск по тексту с поддержкой регулярных выражений
            if query:
                filtered_logs = []
                
                # Подготовка паттерна поиска
                if use_regex:
                    try:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        pattern = re.compile(query, flags)
                    except re.error as e:
                        self.logger.warning(f"Некорректное регулярное выражение: {e}")
                        return {
                            'hits': 0,
                            'total': len(self.logs),
                            'logs': [],
                            'error': f"Некорректное регулярное выражение: {e}",
                            'query': query
                        }
                else:
                    # Обычный поиск
                    query_lower = query.lower() if not case_sensitive else query
                
                for log in logs:
                    match_found = False
                    
                    if use_regex:
                        # Поиск с регулярными выражениями
                        if pattern.search(log.message):
                            match_found = True
                        elif pattern.search(log.component):
                            match_found = True
                        else:
                            # Поиск в метаданных
                            for value in log.metadata.values():
                                if pattern.search(str(value)):
                                    match_found = True
                                    break
                    else:
                        # Обычный поиск
                        search_text = log.message if case_sensitive else log.message.lower()
                        component_text = log.component if case_sensitive else log.component.lower()
                        
                        if query_lower in search_text:
                            match_found = True
                        elif query_lower in component_text:
                            match_found = True
                        else:
                            # Поиск в метаданных
                            for value in log.metadata.values():
                                value_text = str(value) if case_sensitive else str(value).lower()
                                if query_lower in value_text:
                                    match_found = True
                                    break
                    
                    if match_found:
                        filtered_logs.append(log)
                
                logs = filtered_logs
            
            # Ограничение количества результатов
            logs = logs[:limit]
            
            # Подсчет релевантности (простая реализация)
            for log in logs:
                relevance_score = self._calculate_relevance(log, query)
                log.metadata['relevance_score'] = relevance_score
            
            # Сортировка по релевантности и времени
            logs.sort(key=lambda x: (x.metadata.get('relevance_score', 0), x.timestamp), reverse=True)
            
            return {
                'hits': len(logs),
                'total': len(self.logs),
                'logs': [self._log_to_dict(log) for log in logs],
                'query': query,
                'index': index,
                'took': 0.001  # Симуляция времени выполнения
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска: {e}")
            return {
                'hits': 0,
                'total': 0,
                'logs': [],
                'error': str(e)
            }
    
    def _calculate_relevance(self, log: LogEntry, query: str) -> float:
        """Расчет релевантности лога к запросу"""
        if not query:
            return 0.0
        
        query_lower = query.lower()
        score = 0.0
        
        # Поиск в сообщении (высокий вес)
        if query_lower in log.message.lower():
            score += 2.0
        
        # Поиск в компоненте (средний вес)
        if query_lower in log.component.lower():
            score += 1.0
        
        # Поиск в метаданных (низкий вес)
        for value in log.metadata.values():
            if query_lower in str(value).lower():
                score += 0.5
                break
        
        return min(score, 3.0)  # Максимальный балл 3.0
    
    def _log_to_dict(self, log: LogEntry) -> Dict[str, Any]:
        """Преобразование лога в словарь"""
        return {
            'log_id': log.log_id,
            'timestamp': log.timestamp.isoformat(),
            'level': log.level.value,
            'component': log.component,
            'message': log.message,
            'metadata': log.metadata
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        level_counts = {}
        component_counts = {}
        
        for log in self.logs:
            # Подсчет по уровням
            level = log.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
            
            # Подсчет по компонентам
            component = log.component
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            'total_logs': self.stats['total_logs'],
            'indexed_logs': self.stats['indexed_logs'],
            'search_queries': self.stats['search_queries'],
            'last_indexed': self.stats['last_indexed'].isoformat() if self.stats['last_indexed'] else None,
            'indices': {name: len(logs) for name, logs in self.indices.items()},
            'level_distribution': level_counts,
            'component_distribution': component_counts,
            'status': self.status.value
        }
    
    def create_index(self, index_name: str) -> bool:
        """Создание нового индекса"""
        try:
            if index_name not in self.indices:
                self.indices[index_name] = []
                self.logger.info(f"Создан индекс: {index_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка создания индекса {index_name}: {e}")
            return False
    
    def delete_index(self, index_name: str) -> bool:
        """Удаление индекса"""
        try:
            if index_name in self.indices:
                del self.indices[index_name]
                self.logger.info(f"Удален индекс: {index_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления индекса {index_name}: {e}")
            return False
    
    def bulk_index(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Массовая индексация логов"""
        try:
            success_count = 0
            error_count = 0
            
            for log in logs:
                if self.index_log(log):
                    success_count += 1
                else:
                    error_count += 1
            
            return {
                'success_count': success_count,
                'error_count': error_count,
                'total': len(logs)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка массовой индексации: {e}")
            return {
                'success_count': 0,
                'error_count': len(logs),
                'total': len(logs),
                'error': str(e)
            }


# Пример использования
if __name__ == "__main__":
    print("🔍 Запуск Elasticsearch Simulator...")
    
    # Создание симулятора
    es = ElasticsearchSimulator()
    
    # Тестирование поиска
    print("\n📊 Статистика:")
    stats = es.get_statistics()
    print(f"  Всего логов: {stats['total_logs']}")
    print(f"  Индексов: {len(stats['indices'])}")
    print(f"  Поисковых запросов: {stats['search_queries']}")
    
    print("\n🔍 Тестирование поиска:")
    
    # Поиск по тексту
    results = es.search("безопасность", limit=5)
    print(f"  Поиск 'безопасность': {results['hits']} результатов")
    
    # Поиск по уровню
    results = es.search("", level=LogLevel.ERROR, limit=5)
    print(f"  Поиск ошибок: {results['hits']} результатов")
    
    # Поиск по компоненту
    results = es.search("", component="Security", limit=5)
    print(f"  Поиск по Security: {results['hits']} результатов")
    
    print("\n✅ Elasticsearch Simulator готов к работе!")