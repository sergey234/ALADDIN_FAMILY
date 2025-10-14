"""
Асинхронная обработка для ALADDIN VPN
Обеспечивает высокую производительность через асинхронные операции
"""

import logging as std_logging
import queue
import threading
import time
import weakref
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import asyncio

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)


class TaskPriority(Enum):
    """Приоритеты задач"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Статусы задач"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncTask:
    """Асинхронная задача"""

    task_id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3

    def __lt__(self, other):
        """Сравнение для сортировки по приоритету"""
        if not isinstance(other, AsyncTask):
            return NotImplemented
        return self.priority.value < other.priority.value


class ALADDINAsyncProcessor:
    """Асинхронный процессор для ALADDIN VPN"""

    def __init__(self, max_workers: int = 10, max_tasks: int = 1000, task_timeout: int = 300):

        self.max_workers = max_workers
        self.max_tasks = max_tasks
        self.task_timeout = task_timeout

        # Очереди задач по приоритетам
        self.task_queues = {
            TaskPriority.CRITICAL: asyncio.PriorityQueue(),
            TaskPriority.HIGH: asyncio.PriorityQueue(),
            TaskPriority.NORMAL: asyncio.PriorityQueue(),
            TaskPriority.LOW: asyncio.PriorityQueue(),
        }

        # Активные задачи
        self.active_tasks: Dict[str, AsyncTask] = {}
        self.completed_tasks: Dict[str, AsyncTask] = {}

        # Управление
        self.lock = asyncio.Lock()
        self.is_running = False
        self.workers: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Статистика
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "average_execution_time": 0.0,
        }

        logger.info(f"Асинхронный процессор создан: workers={max_workers}, max_tasks={max_tasks}")

    async def start(self):
        """Запуск асинхронного процессора"""
        try:
            if self.is_running:
                logger.warning("Процессор уже запущен")
                return

            self.is_running = True

            # Запускаем воркеров
            for i in range(self.max_workers):
                worker = asyncio.create_task(self._worker(f"worker_{i}"))
                self.workers.append(worker)

            logger.info(f"Асинхронный процессор запущен с {self.max_workers} воркерами")

        except Exception as e:
            logger.error(f"Ошибка запуска процессора: {e}")
            raise

    async def stop(self):
        """Остановка асинхронного процессора"""
        try:
            if not self.is_running:
                logger.warning("Процессор уже остановлен")
                return

            self.is_running = False

            # Отменяем все воркеры
            for worker in self.workers:
                worker.cancel()

            # Ждем завершения воркеров
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()

            # Закрываем executor
            self.executor.shutdown(wait=True)

            logger.info("Асинхронный процессор остановлен")

        except Exception as e:
            logger.error(f"Ошибка остановки процессора: {e}")

    async def submit_task(
        self,
        function: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        task_id: Optional[str] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> str:
        """Отправка задачи на выполнение"""
        try:
            if not self.is_running:
                raise RuntimeError("Процессор не запущен")

            # Генерируем ID задачи
            if task_id is None:
                task_id = f"task_{int(time.time() * 1000)}_{id(function)}"

            # Проверяем лимит задач
            async with self.lock:
                if len(self.active_tasks) + len(self.completed_tasks) >= self.max_tasks:
                    raise RuntimeError("Достигнут лимит задач")

            # Создаем задачу
            task = AsyncTask(
                task_id=task_id,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority,
                status=TaskStatus.PENDING,
                created_at=time.time(),
                max_retries=max_retries,
            )

            # Добавляем в очередь
            priority_value = priority.value
            await self.task_queues[priority].put((priority_value, task))

            # Добавляем в активные задачи
            async with self.lock:
                self.active_tasks[task_id] = task
                self.stats["total_tasks"] += 1

            logger.info(f"Задача {task_id} отправлена с приоритетом {priority.name}")
            return task_id

        except Exception as e:
            logger.error(f"Ошибка отправки задачи: {e}")
            raise

    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Получение результата задачи"""
        try:
            start_time = time.time()

            while True:
                async with self.lock:
                    if task_id in self.completed_tasks:
                        task = self.completed_tasks[task_id]
                        if task.status == TaskStatus.COMPLETED:
                            return task.result
                        elif task.status == TaskStatus.FAILED:
                            raise task.error or Exception("Задача завершилась с ошибкой")
                        elif task.status == TaskStatus.CANCELLED:
                            raise asyncio.CancelledError("Задача была отменена")

                # Проверяем таймаут
                if timeout and (time.time() - start_time) > timeout:
                    raise asyncio.TimeoutError(f"Таймаут ожидания результата задачи {task_id}")

                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Ошибка получения результата задачи {task_id}: {e}")
            raise

    async def cancel_task(self, task_id: str) -> bool:
        """Отмена задачи"""
        try:
            async with self.lock:
                if task_id in self.active_tasks:
                    task = self.active_tasks[task_id]
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = time.time()

                    # Перемещаем в завершенные
                    self.completed_tasks[task_id] = task
                    del self.active_tasks[task_id]

                    self.stats["cancelled_tasks"] += 1
                    logger.info(f"Задача {task_id} отменена")
                    return True
                else:
                    logger.warning(f"Задача {task_id} не найдена в активных")
                    return False

        except Exception as e:
            logger.error(f"Ошибка отмены задачи {task_id}: {e}")
            return False

    async def _worker(self, worker_name: str):
        """Воркер для обработки задач"""
        logger.info(f"Воркер {worker_name} запущен")

        while self.is_running:
            try:
                # Получаем задачу из любой очереди (по приоритету)
                task = None
                for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]:
                    try:
                        _, task = await asyncio.wait_for(self.task_queues[priority].get(), timeout=1.0)
                        break
                    except asyncio.TimeoutError:
                        continue

                if task is None:
                    continue

                # Выполняем задачу
                await self._execute_task(task, worker_name)

            except asyncio.CancelledError:
                logger.info(f"Воркер {worker_name} отменен")
                break
            except Exception as e:
                logger.error(f"Ошибка в воркере {worker_name}: {e}")
                await asyncio.sleep(1)

        logger.info(f"Воркер {worker_name} завершен")

    async def _execute_task(self, task: AsyncTask, worker_name: str):
        """Выполнение задачи"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()

            logger.info(f"Воркер {worker_name} выполняет задачу {task.task_id}")

            # Выполняем функцию
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                # Выполняем синхронную функцию в executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, lambda: task.function(*task.args, **task.kwargs))

            # Задача выполнена успешно
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.result = result

            # Обновляем статистику
            execution_time = task.completed_at - task.started_at
            self._update_execution_time(execution_time)

            logger.info(f"Задача {task.task_id} выполнена за {execution_time:.2f}с")

        except Exception as e:
            # Обработка ошибок
            task.error = e
            task.retry_count += 1

            if task.retry_count <= task.max_retries:
                # Повторяем задачу
                task.status = TaskStatus.PENDING
                task.started_at = None
                priority_value = task.priority.value
                await self.task_queues[task.priority].put((priority_value, task))
                logger.info(f"Задача {task.task_id} будет повторена (попытка {task.retry_count})")
            else:
                # Задача провалена
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                self.stats["failed_tasks"] += 1
                logger.error(f"Задача {task.task_id} провалена после {task.max_retries} попыток: {e}")

        finally:
            # Перемещаем задачу в завершенные
            async with self.lock:
                if task.task_id in self.active_tasks:
                    self.completed_tasks[task.task_id] = task
                    del self.active_tasks[task.task_id]

                    if task.status == TaskStatus.COMPLETED:
                        self.stats["completed_tasks"] += 1

    def _update_execution_time(self, execution_time: float):
        """Обновление среднего времени выполнения"""
        try:
            completed = self.stats["completed_tasks"]
            if completed > 0:
                current_avg = self.stats["average_execution_time"]
                new_avg = (current_avg * (completed - 1) + execution_time) / completed
                self.stats["average_execution_time"] = new_avg
            else:
                self.stats["average_execution_time"] = execution_time
        except Exception as e:
            logger.error(f"Ошибка обновления времени выполнения: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики процессора"""
        try:
            async with self.lock:
                return {
                    "is_running": self.is_running,
                    "max_workers": self.max_workers,
                    "active_workers": len(self.workers),
                    "active_tasks": len(self.active_tasks),
                    "completed_tasks": len(self.completed_tasks),
                    "queue_sizes": {priority.name: q.qsize() for priority, q in self.task_queues.items()},
                    "stats": self.stats.copy(),
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}

    async def cleanup_completed_tasks(self, max_age: int = 3600):
        """Очистка старых завершенных задач"""
        try:
            current_time = time.time()
            old_tasks = []

            async with self.lock:
                for task_id, task in self.completed_tasks.items():
                    if (current_time - task.completed_at) > max_age:
                        old_tasks.append(task_id)

                for task_id in old_tasks:
                    del self.completed_tasks[task_id]

            if old_tasks:
                logger.info(f"Удалено {len(old_tasks)} старых завершенных задач")

        except Exception as e:
            logger.error(f"Ошибка очистки завершенных задач: {e}")


# Примеры асинхронных функций
async def async_vpn_connect(server_id: str, timeout: int = 30) -> Dict[str, Any]:
    """Асинхронное подключение к VPN"""
    logger.info(f"Подключение к VPN серверу {server_id}...")
    await asyncio.sleep(2)  # Имитация подключения

    return {
        "server_id": server_id,
        "status": "connected",
        "connection_time": time.time(),
        "protocol": "wireguard",
        "encryption": "aes-256-gcm",
    }


async def async_data_encrypt(data: bytes, key: str) -> bytes:
    """Асинхронное шифрование данных"""
    logger.info(f"Шифрование {len(data)} байт данных...")
    await asyncio.sleep(0.5)  # Имитация шифрования

    # Простая имитация шифрования
    encrypted = bytearray(data)
    for i in range(len(encrypted)):
        encrypted[i] ^= ord(key[i % len(key)])

    return bytes(encrypted)


def sync_heavy_computation(n: int) -> int:
    """Синхронная тяжелая вычисления"""
    logger.info(f"Выполнение тяжелых вычислений для n={n}...")
    time.sleep(1)  # Имитация тяжелых вычислений
    return sum(i * i for i in range(n))


# Пример использования
async def main():
    """Основная функция для тестирования"""
    processor = ALADDINAsyncProcessor(max_workers=3, max_tasks=100)

    print("=== АСИНХРОННЫЙ ПРОЦЕССОР ALADDIN VPN ===")

    # Запускаем процессор
    await processor.start()
    print("✅ Процессор запущен")

    try:
        # Отправляем асинхронные задачи
        task1 = await processor.submit_task(async_vpn_connect, "server_singapore", priority=TaskPriority.HIGH)
        print(f"✅ Задача подключения отправлена: {task1}")

        task2 = await processor.submit_task(
            async_data_encrypt, b"Hello ALADDIN VPN!", "secret_key", priority=TaskPriority.NORMAL
        )
        print(f"✅ Задача шифрования отправлена: {task2}")

        task3 = await processor.submit_task(sync_heavy_computation, 10000, priority=TaskPriority.LOW)
        print(f"✅ Задача вычислений отправлена: {task3}")

        # Получаем результаты
        result1 = await processor.get_task_result(task1)
        print(f"✅ Результат подключения: {result1}")

        result2 = await processor.get_task_result(task2)
        print(f"✅ Результат шифрования: {len(result2)} байт")

        result3 = await processor.get_task_result(task3)
        print(f"✅ Результат вычислений: {result3}")

        # Получаем статистику
        stats = await processor.get_stats()
        print("\n📊 Статистика процессора:")
        print(f"  Запущен: {stats['is_running']}")
        print(f"  Воркеров: {stats['active_workers']}")
        print(f"  Активных задач: {stats['active_tasks']}")
        print(f"  Завершенных задач: {stats['completed_tasks']}")
        print(f"  Размеры очередей: {stats['queue_sizes']}")
        print(f"  Общая статистика: {stats['stats']}")

    finally:
        # Останавливаем процессор
        await processor.stop()
        print("✅ Процессор остановлен")


if __name__ == "__main__":
    asyncio.run(main())
