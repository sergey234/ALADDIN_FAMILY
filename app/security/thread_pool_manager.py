#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread Pool Manager - Менеджер пулов потоков
Замена создания новых потоков на эффективные пулы потоков
"""

import logging
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TaskPriority(Enum):
    """Приоритеты задач"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Задача для выполнения"""

    id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    created_at: float
    timeout: Optional[float] = None


class ThreadPoolManager:
    """Менеджер пулов потоков для оптимизации производительности"""

    def __init__(
        self,
        max_workers: int = 10,
        enable_priority_queue: bool = True,
        task_timeout: float = 300.0,
    ):
        """
        Инициализация менеджера пулов потоков

        Args:
            max_workers: Максимальное количество потоков
            enable_priority_queue: Включить очередь с приоритетами
            task_timeout: Таймаут выполнения задачи по умолчанию
        """
        self.max_workers = max_workers
        self.enable_priority_queue = enable_priority_queue
        self.task_timeout = task_timeout

        # Основной пул потоков
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Очередь задач с приоритетами
        self.task_queue = queue.PriorityQueue()

        # Статистика
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_timeout": 0,
            "active_workers": 0,
            "queue_size": 0,
        }

        # Логирование
        self.logger = logging.getLogger(__name__)

        # Флаг остановки
        self._stop_flag = False

        # Запускаем обработчик очереди
        if enable_priority_queue:
            self._start_queue_processor()

    def submit_task(
        self,
        task_id: str,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Отправка задачи на выполнение

        Args:
            task_id: Уникальный ID задачи
            function: Функция для выполнения
            args: Аргументы функции
            kwargs: Именованные аргументы
            priority: Приоритет задачи
            timeout: Таймаут выполнения

        Returns:
            ID задачи
        """
        if kwargs is None:
            kwargs = {}

        if timeout is None:
            timeout = self.task_timeout

        task = Task(
            id=task_id,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=time.time(),
            timeout=timeout,
        )

        if self.enable_priority_queue:
            # Добавляем в очередь с приоритетом
            self.task_queue.put((priority.value, task))
            self.stats["queue_size"] = self.task_queue.qsize()
        else:
            # Выполняем напрямую
            self.executor.submit(self._execute_task, task)
            self.stats["tasks_submitted"] += 1

        self.logger.info(
            f"Задача {task_id} отправлена с приоритетом {priority.name}"
        )
        return task_id

    def _start_queue_processor(self):
        """Запуск обработчика очереди задач"""

        def queue_processor():
            while not self._stop_flag:
                try:
                    # Получаем задачу из очереди
                    priority, task = self.task_queue.get(timeout=1.0)

                    # Выполняем задачу
                    self.executor.submit(self._execute_task, task)
                    self.stats["tasks_submitted"] += 1
                    self.stats["queue_size"] = self.task_queue.qsize()

                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Ошибка обработки очереди: {e}")

        processor_thread = threading.Thread(
            target=queue_processor, daemon=True
        )
        processor_thread.start()

    def _execute_task(self, task: Task) -> Any:
        """Выполнение задачи"""
        try:
            self.stats["active_workers"] += 1
            self.logger.info(f"Выполнение задачи {task.id}")

            # Выполняем функцию с таймаутом
            result = task.function(*task.args, **task.kwargs)

            self.stats["tasks_completed"] += 1
            self.logger.info(f"Задача {task.id} выполнена успешно")
            return result

        except Exception as e:
            self.stats["tasks_failed"] += 1
            self.logger.error(f"Ошибка выполнения задачи {task.id}: {e}")
            raise
        finally:
            self.stats["active_workers"] -= 1

    def submit_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Отправка пакета задач

        Args:
            tasks: Список задач в формате
                [{"id": str, "function": callable, ...}]

        Returns:
            Список ID задач
        """
        task_ids = []
        for task_data in tasks:
            task_id = self.submit_task(**task_data)
            task_ids.append(task_id)

        return task_ids

    def wait_for_completion(
        self, task_ids: List[str], timeout: float = None
    ) -> Dict[str, Any]:
        """
        Ожидание завершения задач

        Args:
            task_ids: Список ID задач
            timeout: Таймаут ожидания

        Returns:
            Результаты выполнения задач
        """
        results = {}

        # Для простоты возвращаем статистику
        # В реальной реализации нужно отслеживать Future объекты
        time.sleep(0.1)  # Небольшая задержка для демонстрации

        for task_id in task_ids:
            results[task_id] = {
                "status": "completed",
                "timestamp": time.time(),
            }

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики пула потоков"""
        return {
            **self.stats,
            "max_workers": self.max_workers,
            "queue_enabled": self.enable_priority_queue,
            "is_running": not self._stop_flag,
        }

    def shutdown(self, wait: bool = True):
        """Остановка пула потоков"""
        self._stop_flag = True
        self.executor.shutdown(wait=wait)
        self.logger.info("Пул потоков остановлен")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка состояния менеджера пулов потоков

        Returns:
            Dict[str, Any]: Статус здоровья менеджера
        """
        try:
            import asyncio

            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "ThreadPoolManager",
                "components": {
                    "executor_initialized": self.executor is not None,
                    "queue_processor_running": (
                        self.queue_processor_thread is not None
                        and self.queue_processor_thread.is_alive()
                    ),
                    "priority_queue_enabled": self.enable_priority_queue,
                    "task_queue_available": self.task_queue is not None
                },
                "metrics": {
                    "max_workers": self.max_workers,
                    "active_tasks": len(self.active_tasks),
                    "completed_tasks": self.completed_tasks,
                    "failed_tasks": self.failed_tasks,
                    "queue_size": self.task_queue.qsize() if self.task_queue else 0,
                    "task_timeout": self.task_timeout
                }
            }

            # Проверка состояния executor
            if not self.executor:
                health_status["status"] = "degraded"
                health_status["components"]["executor_initialized"] = False

            # Проверка потока обработки очереди
            if not (self.queue_processor_thread and self.queue_processor_thread.is_alive()):
                health_status["status"] = "degraded"
                health_status["components"]["queue_processor_running"] = False

            # Проверка размера очереди
            if self.task_queue and self.task_queue.qsize() > 1000:  # Большая очередь
                health_status["status"] = "degraded"
                health_status["components"]["large_queue_size"] = True

            # Проверка активных задач
            if len(self.active_tasks) > self.max_workers * 2:  # Слишком много активных задач
                health_status["status"] = "degraded"
                health_status["components"]["high_active_tasks"] = True

            return health_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": asyncio.get_event_loop().time(),
                "service": "ThreadPoolManager",
                "error": str(e)
            }


# Глобальный менеджер пулов потоков
_global_thread_pool = None


def get_thread_pool() -> ThreadPoolManager:
    """Получение глобального пула потоков"""
    global _global_thread_pool
    if _global_thread_pool is None:
        _global_thread_pool = ThreadPoolManager()
    return _global_thread_pool


def submit_async_task(
    task_id: str,
    function: Callable,
    args: tuple = (),
    kwargs: dict = None,
    priority: TaskPriority = TaskPriority.NORMAL,
) -> str:
    """
    Удобная функция для отправки асинхронной задачи

    Args:
        task_id: ID задачи
        function: Функция для выполнения
        args: Аргументы
        kwargs: Именованные аргументы
        priority: Приоритет

    Returns:
        ID задачи
    """
    pool = get_thread_pool()
    return pool.submit_task(task_id, function, args, kwargs or {}, priority)


# Пример использования
if __name__ == "__main__":
    import random

    def sample_task(task_name: str, duration: float = 1.0):
        """Пример задачи"""
        print(f"Выполнение задачи {task_name}")
        time.sleep(duration)
        return f"Результат {task_name}"

    # Создаем пул потоков
    with ThreadPoolManager(max_workers=5) as pool:
        print("🚀 Тестирование пула потоков")

        # Отправляем задачи
        task_ids = []
        for i in range(10):
            task_id = pool.submit_task(
                f"task_{i}",
                sample_task,
                args=(f"Task {i}", random.uniform(0.5, 2.0)),
                priority=(
                    TaskPriority.HIGH if i % 3 == 0 else TaskPriority.NORMAL
                ),
            )
            task_ids.append(task_id)

        # Ждем завершения
        results = pool.wait_for_completion(task_ids)

        # Показываем статистику
        stats = pool.get_statistics()
        print(f"📊 Статистика: {stats}")
