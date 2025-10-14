# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Service Base
Расширенный базовый сервис для системы безопасности

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-01
"""

import asyncio
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .base import ComponentStatus, ServiceBase


class ServiceManager:
    """Менеджер сервисов для управления зависимостями"""

    def __init__(self):
        self.services = {}
        self.dependencies = {}
        self.startup_order = []
        self.shutdown_order = []

    def register_service(
        self,
        service_name: str,
        service_instance: ServiceBase,
        dependencies: Optional[List[str]] = None,
    ):
        """
        Регистрация сервиса

        Args:
            service_name: Название сервиса
            service_instance: Экземпляр сервиса
            dependencies: Список зависимостей
        """
        self.services[service_name] = service_instance
        self.dependencies[service_name] = dependencies or []
        self._update_startup_order()

    def _update_startup_order(self):
        """Обновление порядка запуска сервисов"""
        visited = set()
        temp_visited = set()
        self.startup_order = []

        def dfs(service_name):
            if service_name in temp_visited:
                raise ValueError(
                    f"Циклическая зависимость обнаружена: {service_name}")
            if service_name in visited:
                return

            temp_visited.add(service_name)

            for dep in self.dependencies.get(service_name, []):
                if dep in self.services:
                    dfs(dep)

            temp_visited.remove(service_name)
            visited.add(service_name)
            self.startup_order.append(service_name)

        for service_name in self.services:
            if service_name not in visited:
                dfs(service_name)

        self.shutdown_order = list(reversed(self.startup_order))

    def start_all_services(self) -> Dict[str, bool]:
        """
        Запуск всех сервисов в правильном порядке

        Returns:
            Dict[str, bool]: Результаты запуска сервисов
        """
        results = {}

        for service_name in self.startup_order:
            service = self.services[service_name]
            try:
                success = service.initialize() and service.start()
                results[service_name] = success
                if not success:
                    break  # Останавливаем при ошибке
            except Exception as e:
                results[service_name] = False
                service.log_activity(f"Ошибка запуска: {e}", "error")
                break

        return results

    def stop_all_services(self) -> Dict[str, bool]:
        """
        Остановка всех сервисов в правильном порядке

        Returns:
            Dict[str, bool]: Результаты остановки сервисов
        """
        results = {}

        for service_name in self.shutdown_order:
            service = self.services[service_name]
            try:
                success = service.stop()
                results[service_name] = success
            except Exception as e:
                results[service_name] = False
                service.log_activity(f"Ошибка остановки: {e}", "error")

        return results

    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Получение статуса всех сервисов

        Returns:
            Dict[str, Dict[str, Any]]: Статусы сервисов
        """
        return {name: service.get_status()
                for name, service in self.services.items()}


class AsyncServiceBase(ServiceBase):
    """Асинхронный базовый сервис"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.tasks: List[asyncio.Task] = []
        self.running = False
        self.background_tasks: Dict[str, Callable] = {}

    async def async_initialize(self) -> bool:
        """
        Асинхронная инициализация сервиса

        Returns:
            bool: True если инициализация прошла успешно
        """
        try:
            self.log_activity(f"Асинхронная инициализация сервиса {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Здесь будет асинхронная логика инициализации
            await asyncio.sleep(0.1)  # Имитация асинхронной работы

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Сервис {self.name} успешно инициализирован асинхронно")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка асинхронной инициализации сервиса {self.name}: {e}",
                "error")
            return False

    async def async_start(self) -> bool:
        """
        Асинхронный запуск сервиса

        Returns:
            bool: True если запуск прошел успешно
        """
        try:
            self.log_activity(f"Асинхронный запуск сервиса {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.running = True

            # Запуск фоновых задач
            await self._start_background_tasks()

            self.log_activity(f"Сервис {self.name} успешно запущен асинхронно")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка асинхронного запуска сервиса {self.name}: {e}",
                "error")
            return False

    async def async_stop(self) -> bool:
        """
        Асинхронная остановка сервиса

        Returns:
            bool: True если остановка прошла успешно
        """
        try:
            self.log_activity(f"Асинхронная остановка сервиса {self.name}")
            self.running = False

            # Остановка фоновых задач
            await self._stop_background_tasks()

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Сервис {self.name} успешно остановлен асинхронно")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка асинхронной остановки сервиса {self.name}: {e}",
                "error")
            return False

    async def _start_background_tasks(self):
        """Запуск фоновых задач"""
        for task_name, task_func in self.background_tasks.items():
            task = asyncio.create_task(task_func())
            self.tasks.append(task)
            self.log_activity(f"Запущена фоновая задача: {task_name}")

    async def _stop_background_tasks(self):
        """Остановка фоновых задач"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self.tasks.clear()

    def add_background_task(self, task_name: str, task_func: Callable):
        """
        Добавление фоновой задачи

        Args:
            task_name: Название задачи
            task_func: Функция задачи
        """
        self.background_tasks[task_name] = task_func
        self.log_activity(f"Добавлена фоновая задача: {task_name}")

    def initialize(self) -> bool:
        """Синхронная инициализация (для совместимости)"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            return self.loop.run_until_complete(self.async_initialize())
        except Exception as e:
            self.log_activity(f"Ошибка инициализации: {e}", "error")
            return False

    def start(self) -> bool:
        """Синхронный запуск (для совместимости)"""
        try:
            if self.loop:
                return self.loop.run_until_complete(self.async_start())
            return False
        except Exception as e:
            self.log_activity(f"Ошибка запуска: {e}", "error")
            return False

    def stop(self) -> bool:
        """Синхронная остановка (для совместимости)"""
        try:
            if self.loop:
                result = self.loop.run_until_complete(self.async_stop())
                self.loop.close()
                return result
            return False
        except Exception as e:
            self.log_activity(f"Ошибка остановки: {e}", "error")
            return False


class ThreadedServiceBase(ServiceBase):
    """Потоковый базовый сервис"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        self.max_workers = config.get("max_workers", 5) if config else 5

    def start_worker_thread(self, worker_func: Callable, *args, **kwargs):
        """
        Запуск рабочего потока

        Args:
            worker_func: Функция рабочего потока
            *args: Аргументы функции
            **kwargs: Ключевые аргументы функции
        """
        if len(self.worker_threads) < self.max_workers:
            thread = threading.Thread(
                target=worker_func,
                args=args,
                kwargs=kwargs,
                daemon=True)
            thread.start()
            self.worker_threads.append(thread)
            self.log_activity(f"Запущен рабочий поток: {thread.name}")
        else:
            self.log_activity("Достигнут лимит рабочих потоков", "warning")

    def stop_worker_threads(self):
        """Остановка всех рабочих потоков"""
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
        self.worker_threads.clear()
        self.log_activity("Все рабочие потоки остановлены")

    def initialize(self) -> bool:
        """Инициализация потокового сервиса"""
        try:
            self.log_activity(f"Инициализация потокового сервиса {self.name}")
            self.status = ComponentStatus.INITIALIZING

            # Инициализация потоков
            self._initialize_threads()

            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.log_activity(
                f"Потоковый сервис {self.name} успешно инициализирован")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка инициализации потокового сервиса {self.name}: {e}",
                "error")
            return False

    def _initialize_threads(self):
        """Инициализация потоков"""
        # Здесь будет логика инициализации потоков

    def start(self) -> bool:
        """Запуск потокового сервиса"""
        try:
            self.log_activity(f"Запуск потокового сервиса {self.name}")
            self.status = ComponentStatus.RUNNING
            self.start_time = datetime.now()
            self.running = True

            # Запуск основного потока
            self.thread = threading.Thread(target=self._main_loop, daemon=True)
            self.thread.start()

            self.log_activity(f"Потоковый сервис {self.name} успешно запущен")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.log_activity(
                f"Ошибка запуска потокового сервиса {self.name}: {e}", "error")
            return False

    def stop(self) -> bool:
        """Остановка потокового сервиса"""
        try:
            self.log_activity(f"Остановка потокового сервиса {self.name}")
            self.running = False

            # Остановка рабочих потоков
            self.stop_worker_threads()

            # Ожидание основного потока
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=10.0)

            self.status = ComponentStatus.STOPPED
            self.log_activity(
                f"Потоковый сервис {self.name} успешно остановлен")
            return True
        except Exception as e:
            self.log_activity(
                f"Ошибка остановки потокового сервиса {self.name}: {e}",
                "error")
            return False

    def _main_loop(self):
        """Основной цикл сервиса"""
        while self.running:
            try:
                # Здесь будет основная логика сервиса
                asyncio.sleep(1)
            except Exception as e:
                self.log_activity(f"Ошибка в основном цикле: {e}", "error")
                break
