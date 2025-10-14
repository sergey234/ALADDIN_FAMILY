#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor - Мониторинг производительности в реальном времени
Отслеживание потребления ресурсов компонентами системы безопасности
"""

import psutil
import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetric:
    """Метрика производительности"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_threads: int
    load_average: List[float]
    python_processes: int
    log_files_size_mb: float


class PerformanceMonitor:
    """Монитор производительности системы"""
    
    def __init__(self, logs_dir: str = "logs", monitoring_interval: int = 30):
        """
        Инициализация монитора производительности
        
        Args:
            logs_dir: Директория с логами
            monitoring_interval: Интервал мониторинга в секундах
        """
        self.logs_dir = Path(logs_dir)
        self.monitoring_interval = monitoring_interval
        self.is_running = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.metrics_history: List[PerformanceMetric] = []
        self.max_history_size = 1000  # Максимум 1000 записей в памяти
        
        # Пороги для алертов
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        
        self.alerts = []
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        if self.is_running:
            print("⚠️ Мониторинг уже запущен")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("🚀 Мониторинг производительности запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Мониторинг производительности остановлен")
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.is_running:
            try:
                metric = self._collect_metrics()
                self.metrics_history.append(metric)
                
                # Ограничиваем размер истории
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # Проверяем пороги
                self._check_thresholds(metric)
                
                # Выводим текущую статистику
                self._print_current_stats(metric)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"❌ Ошибка мониторинга: {e}")
                time.sleep(5)
    
    def _collect_metrics(self) -> PerformanceMetric:
        """Сбор метрик производительности"""
        # CPU и память
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Диск
        disk = psutil.disk_usage('/')
        
        # Сеть
        network = psutil.net_io_counters()
        
        # Процессы
        python_processes = len([p for p in psutil.process_iter(['name']) 
                               if 'python' in p.info['name'].lower()])
        
        # Load average (только на Unix системах)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]
        
        # Размер лог-файлов
        log_size_mb = self._get_logs_size()
        
        return PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            active_threads=psutil.cpu_count(),
            load_average=load_avg,
            python_processes=python_processes,
            log_files_size_mb=log_size_mb
        )
    
    def _get_logs_size(self) -> float:
        """Получение размера лог-файлов в MB"""
        if not self.logs_dir.exists():
            return 0.0
        
        total_size = 0
        for log_file in self.logs_dir.glob("*.log"):
            total_size += log_file.stat().st_size
        
        return total_size / 1024 / 1024
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """Проверка порогов и генерация алертов"""
        alerts = []
        
        if metric.cpu_percent > self.cpu_threshold:
            alerts.append(f"🚨 ВЫСОКАЯ НАГРУЗКА CPU: {metric.cpu_percent:.1f}%")
        
        if metric.memory_percent > self.memory_threshold:
            alerts.append(f"🚨 ВЫСОКОЕ ПОТРЕБЛЕНИЕ ПАМЯТИ: {metric.memory_percent:.1f}%")
        
        if metric.disk_usage_percent > self.disk_threshold:
            alerts.append(f"🚨 МАЛО МЕСТА НА ДИСКЕ: {metric.disk_usage_percent:.1f}%")
        
        if metric.log_files_size_mb > 100:  # 100 MB логов
            alerts.append(f"🚨 БОЛЬШОЙ РАЗМЕР ЛОГОВ: {metric.log_files_size_mb:.1f} MB")
        
        if alerts:
            for alert in alerts:
                print(alert)
                self.alerts.append({
                    "timestamp": metric.timestamp,
                    "message": alert,
                    "metric": asdict(metric)
                })
    
    def _print_current_stats(self, metric: PerformanceMetric):
        """Вывод текущей статистики"""
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] Производительность:")
        print(f"   CPU: {metric.cpu_percent:.1f}% | "
              f"RAM: {metric.memory_percent:.1f}% ({metric.memory_used_mb:.0f}MB) | "
              f"Диск: {metric.disk_usage_percent:.1f}%")
        print(f"   Python процессов: {metric.python_processes} | "
              f"Логи: {metric.log_files_size_mb:.1f}MB | "
              f"Load: {metric.load_average[0]:.2f}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Получение отчета о производительности"""
        if not self.metrics_history:
            return {"error": "Нет данных мониторинга"}
        
        latest = self.metrics_history[-1]
        
        # Статистика за последний час
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp) > hour_ago
        ]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            max_cpu = max(m.cpu_percent for m in recent_metrics)
            max_memory = max(m.memory_percent for m in recent_metrics)
        else:
            avg_cpu = latest.cpu_percent
            avg_memory = latest.memory_percent
            max_cpu = latest.cpu_percent
            max_memory = latest.memory_percent
        
        return {
            "current": asdict(latest),
            "statistics": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory,
                "max_cpu_percent": max_cpu,
                "max_memory_percent": max_memory,
                "total_alerts": len(self.alerts),
                "monitoring_duration_minutes": len(self.metrics_history) * self.monitoring_interval / 60
            },
            "alerts": self.alerts[-10:],  # Последние 10 алертов
            "recommendations": self._get_recommendations(latest)
        }
    
    def _get_recommendations(self, metric: PerformanceMetric) -> List[str]:
        """Получение рекомендаций по оптимизации"""
        recommendations = []
        
        if metric.cpu_percent > 70:
            recommendations.append("🔧 Рассмотрите оптимизацию CPU-интенсивных процессов")
        
        if metric.memory_percent > 80:
            recommendations.append("🔧 Увеличьте RAM или оптимизируйте использование памяти")
        
        if metric.disk_usage_percent > 85:
            recommendations.append("🔧 Очистите диск или увеличьте объем хранилища")
        
        if metric.log_files_size_mb > 50:
            recommendations.append("🔧 Настройте ротацию логов для экономии места")
        
        if metric.python_processes > 10:
            recommendations.append("🔧 Проверьте количество запущенных Python процессов")
        
        if not recommendations:
            recommendations.append("✅ Система работает в нормальном режиме")
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """Сохранение отчета в файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = self.get_performance_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Отчет сохранен: {filename}")


def main():
    """Основная функция"""
    print("🚀 Запуск мониторинга производительности ALADDIN")
    print("=" * 60)
    
    monitor = PerformanceMonitor(monitoring_interval=30)
    
    try:
        monitor.start_monitoring()
        
        print("📊 Мониторинг запущен. Нажмите Ctrl+C для остановки")
        print("=" * 60)
        
        # Мониторим до прерывания
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка мониторинга...")
        monitor.stop_monitoring()
        
        # Сохраняем отчет
        monitor.save_report()
        
        print("✅ Мониторинг остановлен")


if __name__ == "__main__":
    main()