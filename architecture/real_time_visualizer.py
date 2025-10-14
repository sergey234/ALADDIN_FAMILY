#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Architecture Visualizer - Визуализатор архитектуры в реальном времени
Система безопасности ALADDIN
"""

import os
import sys
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import psutil
import requests

# Flask и связанные модули
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import docker

# Для создания графов
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Использование без GUI
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
import numpy as np

class RealTimeArchitectureVisualizer:
    """Визуализатор архитектуры системы ALADDIN в реальном времени"""
    
    def __init__(self, config_path: str = "architecture/visualizer_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Инициализация Docker клиента
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            self.logger.warning(f"Docker недоступен: {e}")
            self.docker_client = None
            self.docker_available = False
        
        # Создание Flask приложения
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.config['flask']['secret_key']
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Граф архитектуры
        self.graph = nx.DiGraph()
        self.metrics = {}
        self.is_running = False
        self.update_thread = None
        
        # Данные системы
        self.services = []
        self.connections = []
        self.system_metrics = {}
        
        self._setup_routes()
        self._setup_socketio_events()
        
    def _load_config(self) -> Dict:
        """Загрузка конфигурации"""
        default_config = {
            "flask": {
                "secret_key": "aladdin_visualizer_secret_key_2024",
                "host": "0.0.0.0",
                "port": 8007,
                "debug": False
            },
            "monitoring": {
                "update_interval": 2.0,  # секунды
                "metrics_history_size": 100,
                "enable_docker_monitoring": True,
                "enable_process_monitoring": True,
                "enable_network_monitoring": True
            },
            "visualization": {
                "layout": "spring",  # spring, circular, hierarchical
                "node_size": 3000,
                "edge_width": 2,
                "colors": {
                    "running": "#4CAF50",
                    "warning": "#FFC107", 
                    "error": "#F44336",
                    "stopped": "#9E9E9E",
                    "unknown": "#607D8B"
                }
            },
            "services": {
                "aladdin_services": [
                    "aladdin-sfm",
                    "aladdin-api-gateway",
                    "aladdin-monitoring",
                    "aladdin-security",
                    "aladdin-ai-agents",
                    "aladdin-bots"
                ],
                "external_services": [
                    "redis",
                    "postgresql",
                    "prometheus",
                    "grafana"
                ]
            },
            "api": {
                "aladdin_api_base": "http://localhost:8006",
                "timeout": 5.0
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить конфигурацию: {e}, используются настройки по умолчанию")
        
        return default_config
        
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/architecture_visualizer.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.__class__.__name__)
        
    def _setup_routes(self):
        """Настройка маршрутов Flask"""
        
        @self.app.route('/')
        def index():
            """Главная страница визуализатора"""
            return render_template('architecture.html', 
                                 title="ALADDIN Real-time Architecture",
                                 config=self.config)
        
        @self.app.route('/api/architecture')
        def get_architecture():
            """Получение данных архитектуры"""
            try:
                architecture_data = self._get_architecture_data()
                return jsonify(architecture_data)
            except Exception as e:
                self.logger.error(f"Ошибка получения архитектуры: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/metrics')
        def get_metrics():
            """Получение метрик системы"""
            try:
                metrics_data = self._get_system_metrics()
                return jsonify(metrics_data)
            except Exception as e:
                self.logger.error(f"Ошибка получения метрик: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/services')
        def get_services():
            """Получение списка сервисов"""
            try:
                services_data = self._scan_services()
                return jsonify(services_data)
            except Exception as e:
                self.logger.error(f"Ошибка получения сервисов: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/service/<service_name>')
        def get_service_details(service_name):
            """Получение детальной информации о сервисе"""
            try:
                service_details = self._get_service_details(service_name)
                return jsonify(service_details)
            except Exception as e:
                self.logger.error(f"Ошибка получения деталей сервиса {service_name}: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _setup_socketio_events(self):
        """Настройка WebSocket событий"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Обработка подключения клиента"""
            self.logger.info('Клиент подключился к визуализатору')
            emit('architecture_update', self._get_architecture_data())
            emit('metrics_update', self._get_system_metrics())
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Обработка отключения клиента"""
            self.logger.info('Клиент отключился от визуализатора')
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Обработка запроса обновления"""
            emit('architecture_update', self._get_architecture_data())
            emit('metrics_update', self._get_system_metrics())
        
        @self.socketio.on('service_click')
        def handle_service_click(service_name):
            """Обработка клика по сервису"""
            service_details = self._get_service_details(service_name)
            emit('service_details', service_details)
    
    def _scan_services(self) -> List[Dict]:
        """Сканирование сервисов системы"""
        services = []
        
        try:
            # Сканирование Docker контейнеров
            if self.docker_available:
                containers = self.docker_client.containers.list(all=True)
                
                for container in containers:
                    if any(service in container.name for service in self.config['services']['aladdin_services'] + self.config['services']['external_services']):
                        service = {
                            "id": container.id,
                            "name": container.name,
                            "status": container.status,
                            "image": container.image.tags[0] if container.image.tags else "unknown",
                            "created": container.attrs['Created'],
                            "type": "docker_container"
                        }
                        
                        # Получение метрик контейнера
                        if container.status == 'running':
                            try:
                                stats = container.stats(stream=False)
                                service.update({
                                    "cpu_usage": self._calculate_cpu_percent(stats),
                                    "memory_usage": self._calculate_memory_usage(stats),
                                    "network_io": self._calculate_network_io(stats)
                                })
                            except Exception as e:
                                self.logger.warning(f"Не удалось получить статистику контейнера {container.name}: {e}")
                                service.update({
                                    "cpu_usage": 0,
                                    "memory_usage": 0,
                                    "network_io": {"in": 0, "out": 0}
                                })
                        else:
                            service.update({
                                "cpu_usage": 0,
                                "memory_usage": 0,
                                "network_io": {"in": 0, "out": 0}
                            })
                        
                        services.append(service)
            
            # Сканирование процессов Python
            python_processes = self._scan_python_processes()
            services.extend(python_processes)
            
            # Сканирование ALADDIN процессов
            aladdin_processes = self._scan_aladdin_processes()
            services.extend(aladdin_processes)
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования сервисов: {e}")
        
        return services
    
    def _scan_python_processes(self) -> List[Dict]:
        """Сканирование Python процессов"""
        python_services = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'status']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        
                        # Поиск ALADDIN процессов
                        if 'aladdin' in cmdline.lower() or 'security' in cmdline.lower():
                            service = {
                                "id": f"proc_{proc.info['pid']}",
                                "name": f"Python: {os.path.basename(proc.info['cmdline'][0]) if proc.info['cmdline'] else 'unknown'}",
                                "status": "running" if proc.info['status'] == psutil.STATUS_RUNNING else "stopped",
                                "pid": proc.info['pid'],
                                "cpu_usage": proc.info['cpu_percent'],
                                "memory_usage": proc.info['memory_info'].rss / (1024 * 1024),  # MB
                                "type": "python_process",
                                "cmdline": cmdline
                            }
                            python_services.append(service)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Ошибка сканирования Python процессов: {e}")
        
        return python_services
    
    def _scan_aladdin_processes(self) -> List[Dict]:
        """Сканирование специфических ALADDIN процессов"""
        aladdin_services = []
        
        try:
            # Поиск процессов по портам ALADDIN
            aladdin_ports = [8006, 8007, 8008, 8009, 8010, 8011, 8012]
            
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port in aladdin_ports:
                    try:
                        proc = psutil.Process(conn.pid)
                        service = {
                            "id": f"aladdin_{conn.laddr.port}",
                            "name": f"ALADDIN Service (Port {conn.laddr.port})",
                            "status": "running",
                            "port": conn.laddr.port,
                            "pid": conn.pid,
                            "cpu_usage": proc.cpu_percent(),
                            "memory_usage": proc.memory_info().rss / (1024 * 1024),
                            "type": "aladdin_service"
                        }
                        aladdin_services.append(service)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            self.logger.error(f"Ошибка сканирования ALADDIN процессов: {e}")
        
        return aladdin_services
    
    def _get_service_details(self, service_name: str) -> Dict:
        """Получение детальной информации о сервисе"""
        try:
            # Поиск сервиса в списке
            service = None
            for s in self.services:
                if s['name'] == service_name or s['id'] == service_name:
                    service = s
                    break
            
            if not service:
                return {"error": "Сервис не найден"}
            
            # Дополнительная информация
            details = service.copy()
            
            # Проверка доступности API
            if service.get('port'):
                try:
                    response = requests.get(
                        f"http://localhost:{service['port']}/health",
                        timeout=self.config['api']['timeout']
                    )
                    details['api_status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
                except:
                    details['api_status'] = 'unreachable'
            
            # Логи сервиса
            details['logs'] = self._get_service_logs(service_name)
            
            # Метрики производительности
            details['performance'] = self._get_service_performance(service_name)
            
            return details
            
        except Exception as e:
            self.logger.error(f"Ошибка получения деталей сервиса {service_name}: {e}")
            return {"error": str(e)}
    
    def _get_service_logs(self, service_name: str) -> List[str]:
        """Получение логов сервиса"""
        logs = []
        
        try:
            # Поиск логов в директории logs
            log_files = []
            if os.path.exists('logs'):
                for file in os.listdir('logs'):
                    if service_name.lower().replace(' ', '_') in file.lower() and file.endswith('.log'):
                        log_files.append(os.path.join('logs', file))
            
            # Чтение последних 10 строк из каждого лог-файла
            for log_file in log_files[:3]:  # Максимум 3 файла
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        logs.extend(lines[-10:])  # Последние 10 строк
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Ошибка получения логов сервиса {service_name}: {e}")
        
        return logs[-20:]  # Максимум 20 строк
    
    def _get_service_performance(self, service_name: str) -> Dict:
        """Получение метрик производительности сервиса"""
        performance = {
            "response_time": 0,
            "throughput": 0,
            "error_rate": 0,
            "availability": 100
        }
        
        try:
            # Здесь можно добавить логику получения метрик из Prometheus или других источников
            # Пока возвращаем базовые метрики
            pass
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик производительности {service_name}: {e}")
        
        return performance
    
    def _build_architecture_graph(self, services: List[Dict]):
        """Построение графа архитектуры"""
        self.graph.clear()
        
        # Добавление узлов (сервисов)
        for service in services:
            node_color = self._get_service_color(service)
            self.graph.add_node(
                service['name'],
                **{
                    'status': service['status'],
                    'cpu_usage': service.get('cpu_usage', 0),
                    'memory_usage': service.get('memory_usage', 0),
                    'color': node_color,
                    'type': service.get('type', 'unknown'),
                    'details': service
                }
            )
        
        # Добавление связей между сервисами
        connections = self._discover_service_connections(services)
        for connection in connections:
            self.graph.add_edge(
                connection['source'],
                connection['target'],
                **connection
            )
    
    def _get_service_color(self, service: Dict) -> str:
        """Получение цвета сервиса на основе статуса"""
        status = service.get('status', 'unknown')
        cpu_usage = service.get('cpu_usage', 0)
        
        if status == 'running':
            if cpu_usage > 80:
                return self.config['visualization']['colors']['warning']
            else:
                return self.config['visualization']['colors']['running']
        elif status == 'stopped':
            return self.config['visualization']['colors']['stopped']
        elif status == 'error':
            return self.config['visualization']['colors']['error']
        else:
            return self.config['visualization']['colors']['unknown']
    
    def _discover_service_connections(self, services: List[Dict]) -> List[Dict]:
        """Обнаружение связей между сервисами"""
        connections = []
        
        try:
            # Анализ сетевых соединений
            for service in services:
                if service.get('status') == 'running':
                    # Получение сетевых соединений процесса
                    if service.get('pid'):
                        try:
                            proc = psutil.Process(service['pid'])
                            for conn in proc.connections():
                                if conn.status == 'ESTABLISHED' and conn.raddr:
                                    connection = {
                                        "source": service['name'],
                                        "target": f"external:{conn.raddr.ip}:{conn.raddr.port}",
                                        "type": "network",
                                        "protocol": "tcp",
                                        "status": "active",
                                        "weight": 1
                                    }
                                    connections.append(connection)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
            
            # Логические связи между ALADDIN сервисами
            aladdin_services = [s for s in services if 'aladdin' in s['name'].lower()]
            
            # SFM связан со всеми сервисами
            sfm_service = next((s for s in aladdin_services if 'sfm' in s['name'].lower()), None)
            if sfm_service:
                for service in aladdin_services:
                    if service['name'] != sfm_service['name']:
                        connections.append({
                            "source": sfm_service['name'],
                            "target": service['name'],
                            "type": "management",
                            "protocol": "internal",
                            "status": "active",
                            "weight": 2
                        })
            
            # API Gateway связан с основными сервисами
            gateway_service = next((s for s in aladdin_services if 'gateway' in s['name'].lower()), None)
            if gateway_service:
                for service in aladdin_services:
                    if 'gateway' not in service['name'].lower() and 'sfm' not in service['name'].lower():
                        connections.append({
                            "source": gateway_service['name'],
                            "target": service['name'],
                            "type": "api",
                            "protocol": "http",
                            "status": "active",
                            "weight": 1
                        })
                        
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения связей: {e}")
        
        return connections
    
    def _get_architecture_data(self) -> Dict:
        """Получение данных архитектуры"""
        try:
            # Сканирование сервисов
            self.services = self._scan_services()
            
            # Создание графа архитектуры
            self._build_architecture_graph(self.services)
            
            # Получение связей
            self.connections = self._discover_service_connections(self.services)
            
            # Получение метрик
            self.system_metrics = self._get_system_metrics()
            
            return {
                "services": self.services,
                "connections": self.connections,
                "graph_nodes": len(self.graph.nodes()),
                "graph_edges": len(self.graph.edges()),
                "metrics": self.system_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения данных архитектуры: {e}")
            return {
                "services": [],
                "connections": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_system_metrics(self) -> Dict:
        """Получение метрик системы"""
        try:
            # Системные метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Метрики ALADDIN
            aladdin_metrics = {
                "total_services": len(self.services),
                "running_services": len([s for s in self.services if s.get('status') == 'running']),
                "total_cpu_usage": sum(s.get('cpu_usage', 0) for s in self.services),
                "total_memory_usage": sum(s.get('memory_usage', 0) for s in self.services),
                "network_io": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available / (1024**3),  # GB
                    "disk_percent": disk.percent,
                    "disk_free": disk.free / (1024**3),  # GB
                },
                "aladdin": aladdin_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик системы: {e}")
            return {"error": str(e)}
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Расчет использования CPU для Docker контейнера"""
        try:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_count = stats['cpu_stats']['online_cpus']
            
            if system_delta > 0 and cpu_delta > 0:
                return (cpu_delta / system_delta) * cpu_count * 100.0
        except (KeyError, ZeroDivisionError):
            pass
        return 0.0
    
    def _calculate_memory_usage(self, stats: Dict) -> float:
        """Расчет использования памяти для Docker контейнера"""
        try:
            return stats['memory_stats']['usage'] / (1024 * 1024)  # MB
        except (KeyError, ZeroDivisionError):
            return 0.0
    
    def _calculate_network_io(self, stats: Dict) -> Dict:
        """Расчет сетевого I/O для Docker контейнера"""
        try:
            networks = stats.get('networks', {})
            rx_bytes = sum(net['rx_bytes'] for net in networks.values())
            tx_bytes = sum(net['tx_bytes'] for net in networks.values())
            
            return {
                "in": rx_bytes / 1024,  # KB
                "out": tx_bytes / 1024  # KB
            }
        except (KeyError, ZeroDivisionError):
            return {"in": 0, "out": 0}
    
    def _start_monitoring(self):
        """Запуск мониторинга в фоновом режиме"""
        self.is_running = True
        
        def monitoring_loop():
            while self.is_running:
                try:
                    # Получение обновленных данных
                    architecture_data = self._get_architecture_data()
                    metrics_data = self._get_system_metrics()
                    
                    # Отправка обновлений через WebSocket
                    self.socketio.emit('architecture_update', architecture_data)
                    self.socketio.emit('metrics_update', metrics_data)
                    
                    time.sleep(self.config['monitoring']['update_interval'])
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                    time.sleep(5)
        
        self.update_thread = threading.Thread(target=monitoring_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
    
    def start_server(self):
        """Запуск сервера визуализатора"""
        self.logger.info(f"Запуск Real-time Architecture Visualizer на порту {self.config['flask']['port']}")
        
        # Запуск мониторинга
        self._start_monitoring()
        
        try:
            # Запуск Flask-SocketIO сервера
            self.socketio.run(
                self.app,
                host=self.config['flask']['host'],
                port=self.config['flask']['port'],
                debug=self.config['flask']['debug'],
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки")
        finally:
            self._stop_monitoring()

def main():
    """Главная функция"""
    try:
        # Создание экземпляра визуализатора
        visualizer = RealTimeArchitectureVisualizer()
        
        # Запуск сервера
        visualizer.start_server()
        
    except KeyboardInterrupt:
        print("\\n🛑 Остановка Real-time Architecture Visualizer...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()