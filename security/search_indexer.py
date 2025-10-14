# -*- coding: utf-8 -*-
"""
Search Indexer - Система индексации для быстрого поиска функций
Создает и поддерживает индексы для SFM функций
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import threading

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchIndex:
    """Индекс для быстрого поиска"""
    
    def __init__(self, name: str, index_type: str = "text"):
        """Инициализация индекса"""
        self.name = name
        self.index_type = index_type
        self.data: Dict[str, Set[str]] = defaultdict(set)
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self._lock = threading.Lock()
        
    def add_item(self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Добавление элемента в индекс"""
        with self._lock:
            self.data[key].add(value)
            if metadata:
                self.metadata[value] = metadata
            self.updated_at = datetime.now()
    
    def remove_item(self, key: str, value: str) -> None:
        """Удаление элемента из индекса"""
        with self._lock:
            if key in self.data:
                self.data[key].discard(value)
                if not self.data[key]:
                    del self.data[key]
                self.updated_at = datetime.now()
    
    def search(self, query: str, exact_match: bool = False) -> Set[str]:
        """Поиск в индексе"""
        with self._lock:
            results = set()
            query_lower = query.lower()
            
            for key, values in self.data.items():
                if exact_match:
                    if query_lower == key.lower():
                        results.update(values)
                else:
                    if query_lower in key.lower():
                        results.update(values)
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики индекса"""
        with self._lock:
            return {
                'name': self.name,
                'type': self.index_type,
                'total_keys': len(self.data),
                'total_values': sum(len(values) for values in self.data.values()),
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }

class SearchIndexer:
    """Основной класс для индексации поиска"""
    
    def __init__(self, registry_path: str = "data/sfm/function_registry.json"):
        """Инициализация индексера"""
        self.registry_path = registry_path
        self.indexes: Dict[str, SearchIndex] = {}
        self.index_stats = {
            'total_indexes': 0,
            'total_items': 0,
            'last_rebuild': None,
            'rebuild_time': 0.0
        }
        self._lock = threading.Lock()
        
    def create_index(self, name: str, index_type: str = "text") -> SearchIndex:
        """Создание нового индекса"""
        with self._lock:
            if name in self.indexes:
                logger.warning(f"Index {name} already exists, replacing...")
            
            index = SearchIndex(name, index_type)
            self.indexes[name] = index
            self.index_stats['total_indexes'] += 1
            
            logger.info(f"Created index: {name}")
            return index
    
    def get_index(self, name: str) -> Optional[SearchIndex]:
        """Получение индекса по имени"""
        return self.indexes.get(name)
    
    def add_to_index(self, index_name: str, key: str, value: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Добавление элемента в индекс"""
        index = self.get_index(index_name)
        if index is None:
            logger.error(f"Index {index_name} not found")
            return False
        
        index.add_item(key, value, metadata)
        self.index_stats['total_items'] += 1
        return True
    
    def search_in_index(self, index_name: str, query: str, 
                       exact_match: bool = False) -> Set[str]:
        """Поиск в индексе"""
        index = self.get_index(index_name)
        if index is None:
            logger.error(f"Index {index_name} not found")
            return set()
        
        return index.search(query, exact_match)
    
    def rebuild_indexes_from_registry(self) -> bool:
        """Перестроение всех индексов из registry"""
        try:
            start_time = time.time()
            
            # Загрузка registry
            if not os.path.exists(self.registry_path):
                logger.error(f"Registry file not found: {self.registry_path}")
                return False
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            functions = registry_data.get('functions', {})
            
            # Очистка существующих индексов
            for index in self.indexes.values():
                index.data.clear()
                index.metadata.clear()
            
            # Создание индексов
            self._create_name_index(functions)
            self._create_category_index(functions)
            self._create_status_index(functions)
            self._create_type_index(functions)
            self._create_description_index(functions)
            self._create_keywords_index(functions)
            
            # Обновление статистики
            self.index_stats['last_rebuild'] = datetime.now().isoformat()
            self.index_stats['rebuild_time'] = time.time() - start_time
            
            logger.info(f"Rebuilt {len(self.indexes)} indexes in {self.index_stats['rebuild_time']:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebuild indexes: {e}")
            return False
    
    def _create_name_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по именам функций"""
        name_index = self.create_index("function_names", "text")
        
        for func_id, func_data in functions.items():
            name = func_data.get('name', '')
            if name:
                # Добавление полного имени
                name_index.add_item(name, func_id)
                
                # Добавление отдельных слов
                words = re.findall(r'\w+', name.lower())
                for word in words:
                    if len(word) > 2:  # Игнорируем короткие слова
                        name_index.add_item(word, func_id)
    
    def _create_category_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по категориям"""
        category_index = self.create_index("function_categories", "category")
        
        for func_id, func_data in functions.items():
            category = func_data.get('category', 'UNKNOWN')
            category_index.add_item(category, func_id)
    
    def _create_status_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по статусам"""
        status_index = self.create_index("function_statuses", "status")
        
        for func_id, func_data in functions.items():
            status = func_data.get('status', 'UNKNOWN')
            status_index.add_item(status, func_id)
    
    def _create_type_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по типам функций"""
        type_index = self.create_index("function_types", "type")
        
        for func_id, func_data in functions.items():
            func_type = func_data.get('function_type', 'unknown')
            type_index.add_item(func_type, func_id)
    
    def _create_description_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по описаниям"""
        desc_index = self.create_index("function_descriptions", "text")
        
        for func_id, func_data in functions.items():
            description = func_data.get('description', '')
            if description:
                # Добавление отдельных слов из описания
                words = re.findall(r'\w+', description.lower())
                for word in words:
                    if len(word) > 3:  # Игнорируем короткие слова
                        desc_index.add_item(word, func_id)
    
    def _create_keywords_index(self, functions: Dict[str, Any]) -> None:
        """Создание индекса по ключевым словам"""
        keywords_index = self.create_index("function_keywords", "text")
        
        # Ключевые слова для поиска
        security_keywords = [
            'security', 'encrypt', 'decrypt', 'auth', 'password', 'hash',
            'monitor', 'detect', 'threat', 'malware', 'firewall', 'vpn',
            'compliance', 'audit', 'log', 'alert', 'incident', 'response'
        ]
        
        for func_id, func_data in functions.items():
            name = func_data.get('name', '').lower()
            description = func_data.get('description', '').lower()
            func_type = func_data.get('function_type', '').lower()
            
            text_content = f"{name} {description} {func_type}"
            
            for keyword in security_keywords:
                if keyword in text_content:
                    keywords_index.add_item(keyword, func_id)
    
    def advanced_search(self, query: str, search_fields: List[str] = None, 
                       exact_match: bool = False) -> Dict[str, Set[str]]:
        """Расширенный поиск по нескольким полям"""
        if search_fields is None:
            search_fields = ['function_names', 'function_descriptions', 'function_keywords']
        
        results = {}
        
        for field in search_fields:
            field_results = self.search_in_index(field, query, exact_match)
            if field_results:
                results[field] = field_results
        
        return results
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Получение предложений для автодополнения"""
        suggestions = set()
        
        # Поиск в именах функций
        name_results = self.search_in_index("function_names", partial_query)
        for func_id in name_results:
            # Получение полного имени функции
            # Здесь нужно будет добавить логику получения имени по ID
            suggestions.add(partial_query)  # Заглушка
        
        return list(suggestions)[:limit]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Получение статистики всех индексов"""
        with self._lock:
            stats = {
                'indexer_stats': self.index_stats,
                'indexes': {}
            }
            
            for name, index in self.indexes.items():
                stats['indexes'][name] = index.get_stats()
            
            return stats
    
    def optimize_indexes(self) -> bool:
        """Оптимизация индексов"""
        try:
            # Удаление пустых индексов
            empty_indexes = []
            for name, index in self.indexes.items():
                if not index.data:
                    empty_indexes.append(name)
            
            for name in empty_indexes:
                del self.indexes[name]
                self.index_stats['total_indexes'] -= 1
            
            logger.info(f"Optimized indexes, removed {len(empty_indexes)} empty indexes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize indexes: {e}")
            return False

# Глобальный индексер
_search_indexer = SearchIndexer()

def get_search_indexer() -> SearchIndexer:
    """Получение глобального индексера"""
    return _search_indexer

def rebuild_search_indexes() -> bool:
    """Перестроение индексов поиска"""
    return _search_indexer.rebuild_indexes_from_registry()

def search_functions(query: str, search_fields: List[str] = None) -> Dict[str, Set[str]]:
    """Поиск функций"""
    return _search_indexer.advanced_search(query, search_fields)

def get_search_suggestions(partial_query: str, limit: int = 10) -> List[str]:
    """Получение предложений поиска"""
    return _search_indexer.get_search_suggestions(partial_query, limit)

def get_search_stats() -> Dict[str, Any]:
    """Получение статистики поиска"""
    return _search_indexer.get_index_stats()

# Функции для интеграции с SFM
def initialize_search_indexer() -> bool:
    """Инициализация системы поиска"""
    try:
        # Перестроение индексов
        success = rebuild_search_indexes()
        if success:
            logger.info("Search indexer initialized successfully")
        return success
        
    except Exception as e:
        logger.error(f"Failed to initialize search indexer: {e}")
        return False

def get_search_functions() -> List[str]:
    """Получение списка функций поиска"""
    return [
        'get_search_indexer',
        'rebuild_search_indexes',
        'search_functions',
        'get_search_suggestions',
        'get_search_stats',
        'initialize_search_indexer',
        'get_search_functions'
    ]

if __name__ == "__main__":
    # Тестирование
    def test_search_indexer():
        print("🧪 Тестирование Search Indexer")
        
        # Инициализация
        success = initialize_search_indexer()
        print(f"✅ Инициализация: {'Успешно' if success else 'Ошибка'}")
        
        # Поиск
        results = search_functions("security")
        print(f"🔍 Результаты поиска 'security': {len(results)} полей")
        
        # Статистика
        stats = get_search_stats()
        print(f"📊 Статистика: {stats['indexer_stats']}")
        
        print("✅ Тестирование завершено")
    
    test_search_indexer()
