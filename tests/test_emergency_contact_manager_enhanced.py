#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для расширенного EmergencyContactManager
Покрытие всех методов включая асинхронные
"""

import asyncio
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.emergency_contact_manager import EmergencyContactManager
from security.ai_agents.emergency_models import EmergencyContact, EmergencyEvent


class TestEmergencyContactManagerEnhanced(unittest.TestCase):
    """Тесты для расширенного EmergencyContactManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.manager = EmergencyContactManager()
        self.test_contact_data = {
            'name': 'Тест Контакт',
            'phone': '+1234567890',
            'email': 'test@example.com',
            'relationship': 'family',
            'priority': 1,
            'is_available': True
        }

    def tearDown(self):
        """Очистка после каждого теста"""
        self.manager.clear_contacts()
        self.manager.clear_cache()

    # ============================================================================
    # ТЕСТЫ БАЗОВЫХ МЕТОДОВ
    # ============================================================================

    def test_init(self):
        """Тест инициализации менеджера"""
        self.assertIsInstance(self.manager.contacts, dict)
        self.assertIsInstance(self.manager.contact_groups, dict)
        self.assertEqual(len(self.manager.contacts), 0)
        self.assertEqual(len(self.manager.contact_groups), 0)

    def test_add_contact(self):
        """Тест добавления контакта"""
        contact = self.manager.add_contact(**self.test_contact_data)
        
        self.assertIsInstance(contact, EmergencyContact)
        self.assertEqual(contact.name, self.test_contact_data['name'])
        self.assertEqual(contact.phone, self.test_contact_data['phone'])
        self.assertEqual(contact.email, self.test_contact_data['email'])
        self.assertEqual(contact.relationship, self.test_contact_data['relationship'])
        self.assertEqual(contact.priority, self.test_contact_data['priority'])
        self.assertEqual(contact.is_available, self.test_contact_data['is_available'])
        
        # Проверяем, что контакт добавлен в менеджер
        self.assertIn(contact.contact_id, self.manager.contacts)
        self.assertEqual(len(self.manager.contacts), 1)

    def test_add_contact_validation_errors(self):
        """Тест валидации при добавлении контакта"""
        # Невалидный телефон
        with self.assertRaises(ValueError):
            self.manager.add_contact('Тест', 'невалидный_телефон')
        
        # Невалидный email
        with self.assertRaises(ValueError):
            self.manager.add_contact('Тест', '+1234567890', 'невалидный_email')

    def test_get_contact(self):
        """Тест получения контакта по ID"""
        contact = self.manager.add_contact(**self.test_contact_data)
        
        # Существующий контакт
        retrieved = self.manager.get_contact(contact.contact_id)
        self.assertEqual(retrieved, contact)
        
        # Несуществующий контакт
        not_found = self.manager.get_contact('несуществующий_id')
        self.assertIsNone(not_found)

    def test_update_contact(self):
        """Тест обновления контакта"""
        contact = self.manager.add_contact(**self.test_contact_data)
        
        # Успешное обновление
        result = self.manager.update_contact(contact.contact_id, name='Обновленное Имя')
        self.assertTrue(result)
        
        updated_contact = self.manager.get_contact(contact.contact_id)
        self.assertEqual(updated_contact.name, 'Обновленное Имя')
        
        # Обновление несуществующего контакта
        result = self.manager.update_contact('несуществующий_id', name='Новое Имя')
        self.assertFalse(result)

    def test_delete_contact(self):
        """Тест удаления контакта"""
        contact = self.manager.add_contact(**self.test_contact_data)
        
        # Успешное удаление
        result = self.manager.delete_contact(contact.contact_id)
        self.assertTrue(result)
        self.assertNotIn(contact.contact_id, self.manager.contacts)
        
        # Удаление несуществующего контакта
        result = self.manager.delete_contact('несуществующий_id')
        self.assertFalse(result)

    def test_get_contacts_by_priority(self):
        """Тест получения контактов по приоритету"""
        # Добавляем контакты с разными приоритетами
        contact1 = self.manager.add_contact('Контакт 1', '+1111111111', priority=1)
        contact2 = self.manager.add_contact('Контакт 2', '+2222222222', priority=2)
        contact3 = self.manager.add_contact('Контакт 3', '+3333333333', priority=1)
        
        # Тест фильтрации по приоритету 1
        priority_1_contacts = self.manager.get_contacts_by_priority(1)
        self.assertEqual(len(priority_1_contacts), 2)
        self.assertIn(contact1, priority_1_contacts)
        self.assertIn(contact3, priority_1_contacts)
        
        # Тест фильтрации по приоритету 2
        priority_2_contacts = self.manager.get_contacts_by_priority(2)
        self.assertEqual(len(priority_2_contacts), 1)
        self.assertIn(contact2, priority_2_contacts)

    def test_get_available_contacts(self):
        """Тест получения доступных контактов"""
        contact1 = self.manager.add_contact('Доступный', '+1111111111', is_available=True)
        contact2 = self.manager.add_contact('Недоступный', '+2222222222', is_available=False)
        
        available = self.manager.get_available_contacts()
        self.assertEqual(len(available), 1)
        self.assertIn(contact1, available)
        self.assertNotIn(contact2, available)

    def test_get_contacts_by_relationship(self):
        """Тест получения контактов по отношению"""
        contact1 = self.manager.add_contact('Семья', '+1111111111', relationship='family')
        contact2 = self.manager.add_contact('Друг', '+2222222222', relationship='friend')
        contact3 = self.manager.add_contact('Семья 2', '+3333333333', relationship='family')
        
        family_contacts = self.manager.get_contacts_by_relationship('family')
        self.assertEqual(len(family_contacts), 2)
        self.assertIn(contact1, family_contacts)
        self.assertIn(contact3, family_contacts)

    def test_create_contact_group(self):
        """Тест создания группы контактов"""
        contact1 = self.manager.add_contact('Контакт 1', '+1111111111')
        contact2 = self.manager.add_contact('Контакт 2', '+2222222222')
        
        result = self.manager.create_contact_group('test_group', [contact1.contact_id, contact2.contact_id])
        self.assertTrue(result)
        self.assertIn('test_group', self.manager.contact_groups)
        self.assertEqual(len(self.manager.contact_groups['test_group']), 2)

    def test_get_contact_group(self):
        """Тест получения контактов группы"""
        contact1 = self.manager.add_contact('Контакт 1', '+1111111111')
        contact2 = self.manager.add_contact('Контакт 2', '+2222222222')
        
        self.manager.create_contact_group('test_group', [contact1.contact_id, contact2.contact_id])
        
        group_contacts = self.manager.get_contact_group('test_group')
        self.assertEqual(len(group_contacts), 2)
        self.assertIn(contact1, group_contacts)
        self.assertIn(contact2, group_contacts)

    def test_get_contact_statistics(self):
        """Тест получения статистики контактов"""
        # Добавляем тестовые контакты
        self.manager.add_contact('Контакт 1', '+1111111111', priority=1, is_available=True)
        self.manager.add_contact('Контакт 2', '+2222222222', priority=2, is_available=False)
        self.manager.add_contact('Контакт 3', '+3333333333', priority=1, is_available=True)
        
        stats = self.manager.get_contact_statistics()
        
        self.assertEqual(stats['total_contacts'], 3)
        self.assertEqual(stats['available_contacts'], 2)
        self.assertEqual(stats['unavailable_contacts'], 1)
        self.assertEqual(stats['priority_statistics'][1], 2)
        self.assertEqual(stats['priority_statistics'][2], 1)

    # ============================================================================
    # ТЕСТЫ СПЕЦИАЛЬНЫХ МЕТОДОВ
    # ============================================================================

    def test_str(self):
        """Тест строкового представления"""
        self.manager.add_contact('Тест', '+1234567890')
        str_repr = str(self.manager)
        self.assertIn('EmergencyContactManager', str_repr)
        self.assertIn('contacts=1', str_repr)

    def test_repr(self):
        """Тест представления для отладки"""
        repr_str = repr(self.manager)
        self.assertIn('EmergencyContactManager', repr_str)
        self.assertIn('contacts={}', repr_str)

    def test_len(self):
        """Тест подсчета контактов"""
        self.assertEqual(len(self.manager), 0)
        
        self.manager.add_contact('Тест 1', '+1111111111')
        self.assertEqual(len(self.manager), 1)
        
        self.manager.add_contact('Тест 2', '+2222222222')
        self.assertEqual(len(self.manager), 2)

    def test_contains(self):
        """Тест проверки наличия контакта"""
        contact = self.manager.add_contact('Тест', '+1234567890')
        
        self.assertIn(contact.contact_id, self.manager)
        self.assertNotIn('несуществующий_id', self.manager)

    def test_clear_contacts(self):
        """Тест очистки контактов"""
        self.manager.add_contact('Тест 1', '+1111111111')
        self.manager.add_contact('Тест 2', '+2222222222')
        self.manager.create_contact_group('test_group', [])
        
        result = self.manager.clear_contacts()
        self.assertTrue(result)
        self.assertEqual(len(self.manager.contacts), 0)
        self.assertEqual(len(self.manager.contact_groups), 0)

    def test_search_contacts(self):
        """Тест поиска контактов"""
        contact1 = self.manager.add_contact('Иван Иванов', '+1111111111', 'ivan@example.com')
        contact2 = self.manager.add_contact('Петр Петров', '+2222222222', 'petr@example.com')
        
        # Поиск по имени
        results = self.manager.search_contacts('Иван')
        self.assertEqual(len(results), 1)
        self.assertIn(contact1, results)
        
        # Поиск по телефону
        results = self.manager.search_contacts('111')
        self.assertEqual(len(results), 1)
        self.assertIn(contact1, results)
        
        # Поиск по email
        results = self.manager.search_contacts('petr@')
        self.assertEqual(len(results), 1)
        self.assertIn(contact2, results)

    def test_validate_contact(self):
        """Тест валидации контакта"""
        contact = self.manager.add_contact('Тест', '+1234567890', 'test@example.com')
        
        # Валидный контакт
        self.assertTrue(self.manager.validate_contact(contact.contact_id))
        
        # Несуществующий контакт
        self.assertFalse(self.manager.validate_contact('несуществующий_id'))

    def test_export_import_contacts(self):
        """Тест экспорта и импорта контактов"""
        # Добавляем тестовые контакты
        contact1 = self.manager.add_contact('Контакт 1', '+1111111111', 'test1@example.com')
        contact2 = self.manager.add_contact('Контакт 2', '+2222222222', 'test2@example.com')
        self.manager.create_contact_group('test_group', [contact1.contact_id])
        
        # Экспорт
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            result = self.manager.export_contacts(export_file)
            self.assertTrue(result)
            
            # Проверяем содержимое файла
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(len(data['contacts']), 2)
            self.assertIn('test_group', data['groups'])
            
            # Создаем новый менеджер для импорта
            new_manager = EmergencyContactManager()
            result = new_manager.import_contacts(export_file)
            self.assertTrue(result)
            
            # Проверяем импортированные данные
            self.assertEqual(len(new_manager.contacts), 2)
            self.assertIn('test_group', new_manager.contact_groups)
            
        finally:
            os.unlink(export_file)

    def test_backup_contacts(self):
        """Тест создания резервной копии"""
        contact = self.manager.add_contact('Тест', '+1234567890')
        self.manager.create_contact_group('test_group', [contact.contact_id])
        
        backup = self.manager.backup_contacts()
        
        self.assertIn('timestamp', backup)
        self.assertIn('contacts', backup)
        self.assertIn('groups', backup)
        self.assertEqual(len(backup['contacts']), 1)
        self.assertIn('test_group', backup['groups'])

    # ============================================================================
    # ТЕСТЫ АСИНХРОННЫХ МЕТОДОВ
    # ============================================================================

    def test_add_contact_async(self):
        """Тест асинхронного добавления контакта"""
        async def run_test():
            contact = await self.manager.add_contact_async(**self.test_contact_data)
            
            self.assertIsInstance(contact, EmergencyContact)
            self.assertEqual(contact.name, self.test_contact_data['name'])
            self.assertIn(contact.contact_id, self.manager.contacts)
        
        asyncio.run(run_test())

    def test_add_contact_async_validation(self):
        """Тест валидации в асинхронном добавлении контакта"""
        async def run_test():
            with self.assertRaises(ValueError):
                await self.manager.add_contact_async('Тест', 'невалидный_телефон')
        
        asyncio.run(run_test())

    def test_get_contacts_async(self):
        """Тест асинхронного получения контактов"""
        async def run_test():
            # Добавляем тестовые контакты
            contact1 = self.manager.add_contact('Контакт 1', '+1111111111', priority=1, is_available=True)
            contact2 = self.manager.add_contact('Контакт 2', '+2222222222', priority=2, is_available=False)
            
            # Тест без фильтров
            all_contacts = await self.manager.get_contacts_async()
            self.assertEqual(len(all_contacts), 2)
            
            # Тест с фильтром по приоритету
            priority_1 = await self.manager.get_contacts_async(priority=1)
            self.assertEqual(len(priority_1), 1)
            self.assertIn(contact1, priority_1)
            
            # Тест с фильтром по доступности
            available = await self.manager.get_contacts_async(is_available=True)
            self.assertEqual(len(available), 1)
            self.assertIn(contact1, available)
        
        asyncio.run(run_test())

    def test_search_contacts_async(self):
        """Тест асинхронного поиска контактов"""
        async def run_test():
            contact = self.manager.add_contact('Иван Иванов', '+1234567890', 'ivan@example.com')
            
            # Поиск по имени
            results = await self.manager.search_contacts_async('Иван')
            self.assertEqual(len(results), 1)
            self.assertIn(contact, results)
            
            # Тест с коротким запросом
            with self.assertRaises(ValueError):
                await self.manager.search_contacts_async('И')
        
        asyncio.run(run_test())

    def test_export_contacts_async(self):
        """Тест асинхронного экспорта контактов"""
        async def run_test():
            self.manager.add_contact('Тест', '+1234567890', 'test@example.com')
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_file = f.name
            
            try:
                result = await self.manager.export_contacts_async(export_file)
                self.assertTrue(result)
                
                # Проверяем содержимое файла
                with open(export_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.assertEqual(len(data['contacts']), 1)
                self.assertIn('version', data)
                
            finally:
                os.unlink(export_file)
        
        asyncio.run(run_test())

    # ============================================================================
    # ТЕСТЫ КЭШИРОВАНИЯ
    # ============================================================================

    def test_cached_contact_retrieval(self):
        """Тест кэшированного получения контакта"""
        contact = self.manager.add_contact('Тест', '+1234567890')
        
        # Первый вызов - загружается в кэш
        result1 = self.manager.get_contact_by_id_cached(contact.contact_id)
        self.assertEqual(result1, contact)
        
        # Второй вызов - из кэша
        result2 = self.manager.get_contact_by_id_cached(contact.contact_id)
        self.assertEqual(result2, contact)
        
        # Проверяем статистику кэша
        cache_info = self.manager.get_contact_by_id_cached.cache_info()
        self.assertGreater(cache_info.hits, 0)

    def test_cached_priority_contacts(self):
        """Тест кэшированного получения контактов по приоритету"""
        contact1 = self.manager.add_contact('Контакт 1', '+1111111111', priority=1)
        contact2 = self.manager.add_contact('Контакт 2', '+2222222222', priority=1)
        
        # Первый вызов
        results1 = self.manager.get_contacts_by_priority_cached(1)
        self.assertEqual(len(results1), 2)
        
        # Второй вызов - из кэша
        results2 = self.manager.get_contacts_by_priority_cached(1)
        self.assertEqual(len(results2), 2)
        
        # Проверяем статистику кэша
        cache_info = self.manager.get_contacts_by_priority_cached.cache_info()
        self.assertGreater(cache_info.hits, 0)

    def test_clear_cache(self):
        """Тест очистки кэша"""
        self.manager.add_contact('Тест', '+1234567890')
        
        # Заполняем кэш
        self.manager.get_contact_by_id_cached('test_id')
        self.manager.get_contacts_by_priority_cached(1)
        
        # Очищаем кэш
        self.manager.clear_cache()
        
        # Проверяем, что кэш очищен
        cache_info1 = self.manager.get_contact_by_id_cached.cache_info()
        cache_info2 = self.manager.get_contacts_by_priority_cached.cache_info()
        
        self.assertEqual(cache_info1.hits, 0)
        self.assertEqual(cache_info2.hits, 0)

    # ============================================================================
    # ТЕСТЫ ЛОГИРОВАНИЯ
    # ============================================================================

    def test_log_contact_operation(self):
        """Тест логирования операций с контактами"""
        with patch.object(self.manager.logger, 'info') as mock_info:
            self.manager.log_contact_operation('add', 'test_id', True, 'Успешно добавлен')
            mock_info.assert_called_once()
            
            call_args = mock_info.call_args[0][0]
            self.assertIn('add', call_args)
            self.assertIn('test_id', call_args)
            self.assertIn('УСПЕХ', call_args)

    def test_log_performance_metric(self):
        """Тест логирования метрик производительности"""
        with patch.object(self.manager.logger, 'info') as mock_info:
            self.manager.log_performance_metric('search', 0.5, 100)
            mock_info.assert_called_once()
            
            call_args = mock_info.call_args[0][0]
            self.assertIn('PERF', call_args)
            self.assertIn('search', call_args)
            self.assertIn('0.500s', call_args)
            self.assertIn('100 записей', call_args)


if __name__ == '__main__':
    # Настройка логирования для тестов
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Запуск тестов
    unittest.main(verbosity=2)