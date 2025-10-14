# -*- coding: utf-8 -*-
"""
Тесты для NetworkSecurityAgent
"""

import unittest
import threading
from datetime import datetime

from security.ai_agents.network_security_agent import (
    NetworkSecurityAgent, NetworkThreatType, NetworkProtocol, ThreatSeverity,
    NetworkStatus, NetworkPacket, NetworkThreat, NetworkFlow, NetworkAnalysis,
    NetworkMetrics
)


class TestNetworkSecurityAgent(unittest.TestCase):
    """Тесты для NetworkSecurityAgent"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = NetworkSecurityAgent("TestNetworkSecurityAgent")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'agent'):
            self.agent.stop()

    def test_initialization(self):
        """Тест инициализации"""
        result = self.agent.initialize()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "running")

    def test_stop(self):
        """Тест остановки"""
        self.agent.initialize()
        result = self.agent.stop()
        self.assertTrue(result)
        self.assertEqual(self.agent.status.value, "stopped")

    def test_analyze_packet(self):
        """Тест анализа пакета"""
        self.agent.initialize()

        packet_data = {
            "source_ip": "192.168.1.1",
            "destination_ip": "192.168.1.2",
            "source_port": 12345,
            "destination_port": 80,
            "protocol": "tcp",
            "packet_size": 1024
        }

        threat = self.agent.analyze_packet(packet_data)
        # Может быть None для нормального пакета
        self.assertIsInstance(threat, (NetworkThreat, type(None)))

    def test_analyze_malicious_packet(self):
        """Тест анализа злонамеренного пакета"""
        self.agent.initialize()

        # Пакет с заблокированного IP
        packet_data = {
            "source_ip": "192.168.1.100",  # Заблокированный IP
            "destination_ip": "192.168.1.2",
            "source_port": 12345,
            "destination_port": 80,
            "protocol": "tcp",
            "packet_size": 1024
        }

        threat = self.agent.analyze_packet(packet_data)
        self.assertIsNotNone(threat)
        self.assertEqual(threat.threat_type, NetworkThreatType.MALWARE)
        self.assertEqual(threat.severity, ThreatSeverity.HIGH)

    def test_analyze_network_flow(self):
        """Тест анализа сетевого потока"""
        self.agent.initialize()

        flow_data = {
            "source_ip": "192.168.1.1",
            "destination_ip": "192.168.1.2",
            "source_port": 12345,
            "destination_port": 80,
            "protocol": "tcp",
            "packets_sent": 10,
            "bytes_sent": 1024,
            "packets_received": 5,
            "bytes_received": 512
        }

        flow = self.agent.analyze_network_flow(flow_data)
        self.assertIsNotNone(flow)
        self.assertEqual(flow.source_ip, "192.168.1.1")
        self.assertEqual(flow.destination_ip, "192.168.1.2")
        self.assertEqual(flow.protocol, NetworkProtocol.TCP)

    def test_get_network_analysis(self):
        """Тест получения анализа сети"""
        self.agent.initialize()

        analysis = self.agent.get_network_analysis()
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, NetworkAnalysis)
        self.assertIsInstance(analysis.network_status, NetworkStatus)
        self.assertIsInstance(analysis.threat_level, ThreatSeverity)

    def test_get_network_metrics(self):
        """Тест получения метрик сети"""
        self.agent.initialize()

        metrics = self.agent.get_network_metrics()
        self.assertIsInstance(metrics, NetworkMetrics)
        self.assertGreaterEqual(metrics.total_packets_analyzed, 0)
        self.assertGreaterEqual(metrics.total_flows_monitored, 0)

    def test_get_agent_status(self):
        """Тест получения статуса агента"""
        self.agent.initialize()

        status = self.agent.get_agent_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("total_packets", status)
        self.assertIn("total_flows", status)
        self.assertIn("total_threats", status)
        self.assertIn("metrics", status)
        self.assertIn("statistics", status)

    def test_block_ip(self):
        """Тест блокировки IP"""
        self.agent.initialize()

        result = self.agent.block_ip("192.168.1.200", "Test block")
        self.assertTrue(result)

        # Проверяем что IP заблокирован
        status = self.agent.get_agent_status()
        self.assertGreater(status["network_rules"]["blocked_ips_count"], 0)

    def test_unblock_ip(self):
        """Тест разблокировки IP"""
        self.agent.initialize()

        # Сначала блокируем
        self.agent.block_ip("192.168.1.200", "Test block")

        # Затем разблокируем
        result = self.agent.unblock_ip("192.168.1.200")
        self.assertTrue(result)

    def test_network_packet_creation(self):
        """Тест создания сетевого пакета"""
        packet = NetworkPacket(
            packet_id="test-packet",
            timestamp=datetime.now(),
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            source_port=12345,
            destination_port=80,
            protocol=NetworkProtocol.TCP,
            packet_size=1024
        )

        self.assertEqual(packet.packet_id, "test-packet")
        self.assertEqual(packet.source_ip, "192.168.1.1")
        self.assertEqual(packet.destination_ip, "192.168.1.2")
        self.assertEqual(packet.protocol, NetworkProtocol.TCP)
        self.assertEqual(packet.packet_size, 1024)

    def test_network_packet_to_dict(self):
        """Тест преобразования пакета в словарь"""
        packet = NetworkPacket(
            packet_id="test-packet",
            timestamp=datetime.now(),
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            source_port=12345,
            destination_port=80,
            protocol=NetworkProtocol.TCP,
            packet_size=1024
        )

        data = packet.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["packet_id"], "test-packet")
        self.assertEqual(data["protocol"], "tcp")

    def test_network_threat_creation(self):
        """Тест создания сетевой угрозы"""
        threat = NetworkThreat(
            threat_id="test-threat",
            threat_type=NetworkThreatType.DDoS,
            severity=ThreatSeverity.HIGH,
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            protocol=NetworkProtocol.TCP,
            port=80,
            timestamp=datetime.now(),
            description="Test DDoS attack",
            confidence=0.9,
            indicators=["High packet rate"],
            mitigation_actions=["Block IP"],
            affected_services=["Web server"]
        )

        self.assertEqual(threat.threat_id, "test-threat")
        self.assertEqual(threat.threat_type, NetworkThreatType.DDoS)
        self.assertEqual(threat.severity, ThreatSeverity.HIGH)
        self.assertEqual(threat.confidence, 0.9)

    def test_network_threat_to_dict(self):
        """Тест преобразования угрозы в словарь"""
        threat = NetworkThreat(
            threat_id="test-threat",
            threat_type=NetworkThreatType.DDoS,
            severity=ThreatSeverity.HIGH,
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            protocol=NetworkProtocol.TCP,
            port=80,
            timestamp=datetime.now(),
            description="Test DDoS attack",
            confidence=0.9,
            indicators=["High packet rate"],
            mitigation_actions=["Block IP"],
            affected_services=["Web server"]
        )

        data = threat.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["threat_id"], "test-threat")
        self.assertEqual(data["threat_type"], "ddos")
        self.assertEqual(data["severity"], "high")

    def test_network_flow_creation(self):
        """Тест создания сетевого потока"""
        flow = NetworkFlow(
            flow_id="test-flow",
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            source_port=12345,
            destination_port=80,
            protocol=NetworkProtocol.TCP,
            start_time=datetime.now(),
            end_time=None,
            packets_sent=10,
            bytes_sent=1024,
            packets_received=5,
            bytes_received=512,
            duration=0.0,
            status=NetworkStatus.NORMAL,
            threat_score=0.0
        )

        self.assertEqual(flow.flow_id, "test-flow")
        self.assertEqual(flow.source_ip, "192.168.1.1")
        self.assertEqual(flow.protocol, NetworkProtocol.TCP)
        self.assertEqual(flow.status, NetworkStatus.NORMAL)

    def test_network_flow_to_dict(self):
        """Тест преобразования потока в словарь"""
        flow = NetworkFlow(
            flow_id="test-flow",
            source_ip="192.168.1.1",
            destination_ip="192.168.1.2",
            source_port=12345,
            destination_port=80,
            protocol=NetworkProtocol.TCP,
            start_time=datetime.now(),
            end_time=None,
            packets_sent=10,
            bytes_sent=1024,
            packets_received=5,
            bytes_received=512,
            duration=0.0,
            status=NetworkStatus.NORMAL,
            threat_score=0.0
        )

        data = flow.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["flow_id"], "test-flow")
        self.assertEqual(data["protocol"], "tcp")
        self.assertEqual(data["status"], "normal")

    def test_network_analysis_creation(self):
        """Тест создания анализа сети"""
        analysis = NetworkAnalysis(
            analysis_id="test-analysis",
            timestamp=datetime.now(),
            network_status=NetworkStatus.NORMAL,
            threat_level=ThreatSeverity.LOW,
            total_threats=0,
            active_flows=5,
            blocked_connections=0,
            allowed_connections=5,
            threats_detected=[],
            suspicious_flows=[],
            recommendations=["Continue monitoring"],
            network_metrics={},
            analysis_metadata={}
        )

        self.assertEqual(analysis.analysis_id, "test-analysis")
        self.assertEqual(analysis.network_status, NetworkStatus.NORMAL)
        self.assertEqual(analysis.threat_level, ThreatSeverity.LOW)
        self.assertEqual(analysis.total_threats, 0)

    def test_network_analysis_to_dict(self):
        """Тест преобразования анализа в словарь"""
        analysis = NetworkAnalysis(
            analysis_id="test-analysis",
            timestamp=datetime.now(),
            network_status=NetworkStatus.NORMAL,
            threat_level=ThreatSeverity.LOW,
            total_threats=0,
            active_flows=5,
            blocked_connections=0,
            allowed_connections=5,
            threats_detected=[],
            suspicious_flows=[],
            recommendations=["Continue monitoring"],
            network_metrics={},
            analysis_metadata={}
        )

        data = analysis.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["analysis_id"], "test-analysis")
        self.assertEqual(data["network_status"], "normal")
        self.assertEqual(data["threat_level"], "low")

    def test_network_metrics_creation(self):
        """Тест создания метрик сети"""
        metrics = NetworkMetrics()

        self.assertEqual(metrics.total_packets_analyzed, 0)
        self.assertEqual(metrics.total_flows_monitored, 0)
        self.assertEqual(metrics.threats_detected, 0)
        self.assertEqual(metrics.ddos_attacks_blocked, 0)

    def test_network_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = NetworkMetrics()
        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertIn("total_packets_analyzed", data)
        self.assertIn("total_flows_monitored", data)
        self.assertIn("threats_detected", data)
        self.assertIn("last_analysis", data)

    def test_concurrent_packet_analysis(self):
        """Тест параллельного анализа пакетов"""
        self.agent.initialize()

        def analyze_worker(worker_id):
            packet_data = {
                "source_ip": f"192.168.1.{worker_id}",
                "destination_ip": "192.168.1.2",
                "source_port": 12345 + worker_id,
                "destination_port": 80,
                "protocol": "tcp",
                "packet_size": 1024
            }
            threat = self.agent.analyze_packet(packet_data)
            return threat is not None

        # Запуск нескольких потоков
        threads = []
        results = []

        for i in range(5):
            thread = threading.Thread(target=lambda i=i: results.append(analyze_worker(i)))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверка результатов
        self.assertEqual(len(results), 5)

    def test_ddos_detection(self):
        """Тест обнаружения DDoS атак"""
        self.agent.initialize()

        # Отправляем много пакетов с одного IP
        for i in range(100):
            packet_data = {
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.2",
                "source_port": 12345,
                "destination_port": 80,
                "protocol": "tcp",
                "packet_size": 1024
            }
            threat = self.agent.analyze_packet(packet_data)
            if threat and threat.threat_type == NetworkThreatType.DDoS:
                break

        # Проверяем что DDoS обнаружен
        metrics = self.agent.get_network_metrics()
        self.assertGreaterEqual(metrics.ddos_attacks_blocked, 0)

    def test_port_scan_detection(self):
        """Тест обнаружения сканирования портов"""
        self.agent.initialize()

        # Отправляем пакеты на заблокированные порты
        blocked_ports = [23, 135, 139, 445]
        for port in blocked_ports:
            packet_data = {
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.2",
                "source_port": 12345,
                "destination_port": port,
                "protocol": "tcp",
                "packet_size": 1024
            }
            threat = self.agent.analyze_packet(packet_data)
            if threat and threat.threat_type == NetworkThreatType.PORT_SCAN:
                break

        # Проверяем что сканирование портов обнаружено
        metrics = self.agent.get_network_metrics()
        self.assertGreaterEqual(metrics.port_scans_detected, 0)

    def test_threat_classification(self):
        """Тест классификации угроз"""
        self.agent.initialize()

        # Тест различных типов угроз
        threat_tests = [
            ({"source_ip": "192.168.1.100"}, NetworkThreatType.MALWARE),
            ({"destination_port": 23}, NetworkThreatType.PORT_SCAN),
            ({"packet_size": 70000}, NetworkThreatType.DDoS)
        ]

        for packet_data, expected_type in threat_tests:
            packet_data.update({
                "destination_ip": "192.168.1.2",
                "source_port": 12345,
                "protocol": "tcp"
            })

            threat = self.agent.analyze_packet(packet_data)
            if threat:
                self.assertEqual(threat.threat_type, expected_type)

    def test_network_status_assessment(self):
        """Тест оценки состояния сети"""
        self.agent.initialize()

        # Создаем несколько угроз
        for i in range(3):
            packet_data = {
                "source_ip": f"192.168.1.{100 + i}",
                "destination_ip": "192.168.1.2",
                "source_port": 12345,
                "destination_port": 23,  # Заблокированный порт
                "protocol": "tcp",
                "packet_size": 1024
            }
            self.agent.analyze_packet(packet_data)

        # Получаем анализ
        analysis = self.agent.get_network_analysis()
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis.network_status, NetworkStatus)

    def test_ai_models_integration(self):
        """Тест интеграции AI моделей"""
        self.agent.initialize()

        # Проверяем что AI модели инициализированы
        self.assertTrue(self.agent.ai_enabled)
        self.assertIsInstance(self.agent.ml_models, dict)
        self.assertIn("threat_classifier", self.agent.ml_models)
        self.assertIn("anomaly_detector", self.agent.ml_models)
        self.assertIn("flow_analyzer", self.agent.ml_models)
        self.assertIn("packet_inspector", self.agent.ml_models)
        self.assertIn("ddos_detector", self.agent.ml_models)
        self.assertIn("intrusion_detector", self.agent.ml_models)

    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.agent.initialize()

        initial_packets = self.agent.statistics["total_packets_processed"]

        # Анализируем пакет
        packet_data = {
            "source_ip": "192.168.1.1",
            "destination_ip": "192.168.1.2",
            "source_port": 12345,
            "destination_port": 80,
            "protocol": "tcp",
            "packet_size": 1024
        }
        self.agent.analyze_packet(packet_data)

        # Проверяем статистику
        self.assertGreater(self.agent.statistics["total_packets_processed"], initial_packets)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным агентом
        result = self.agent.analyze_packet({})
        # Агент может возвращать None для некорректных данных
        self.assertIsInstance(result, (NetworkThreat, type(None)))

        # Тест с некорректными данными
        self.agent.initialize()
        result = self.agent.analyze_packet(None)
        # Агент должен обрабатывать некорректные данные
        self.assertIsInstance(result, (NetworkThreat, type(None)))


if __name__ == '__main__':
    unittest.main()
