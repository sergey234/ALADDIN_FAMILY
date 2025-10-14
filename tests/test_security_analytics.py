"""
Тесты для SecurityAnalytics
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from security.reactive.security_analytics import (
    SecurityAnalytics, AnalyticsType, MetricType, AlertLevel,
    SecurityMetric, AnalyticsReport, PerformanceMetrics, 
    SecurityMetrics, FamilyMetrics
)


class TestSecurityAnalytics:
    """Тесты для SecurityAnalytics"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.analytics = SecurityAnalytics()
    
    def test_initialization(self):
        """Тест инициализации"""
        assert self.analytics.service_name == "SecurityAnalytics"
        assert self.analytics.analytics_type == AnalyticsType.SECURITY
        assert isinstance(self.analytics.performance_metrics, PerformanceMetrics)
        assert isinstance(self.analytics.security_metrics, SecurityMetrics)
        assert isinstance(self.analytics.family_metrics, FamilyMetrics)
        assert len(self.analytics.analytics_history) == 0
        assert len(self.analytics.metrics_history) == 0
    
    def test_analytics_rules_initialization(self):
        """Тест инициализации правил аналитики"""
        assert "performance_monitoring" in self.analytics.analytics_rules
        assert "security_monitoring" in self.analytics.analytics_rules
        assert "family_monitoring" in self.analytics.analytics_rules
        
        assert self.analytics.analytics_rules["performance_monitoring"]["enabled"] is True
        assert self.analytics.analytics_rules["security_monitoring"]["enabled"] is True
        assert self.analytics.analytics_rules["family_monitoring"]["enabled"] is True
    
    def test_family_analytics_setup(self):
        """Тест настройки семейной аналитики"""
        assert "age_groups" in self.analytics.family_analytics
        assert "protection_categories" in self.analytics.family_analytics
        
        age_groups = self.analytics.family_analytics["age_groups"]
        assert "children" in age_groups
        assert "adults" in age_groups
        assert "elderly" in age_groups
        
        assert age_groups["children"]["protection_level"] == "high"
        assert age_groups["adults"]["protection_level"] == "medium"
        assert age_groups["elderly"]["protection_level"] == "high"
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_collect_performance_metrics(self, mock_net_io, mock_disk, mock_memory, mock_cpu):
        """Тест сбора метрик производительности"""
        # Настройка моков
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=67.8)
        mock_disk.return_value = Mock(percent=23.4)
        mock_net_io.return_value = Mock(bytes_sent=1000, bytes_recv=2000)
        
        # Выполнение
        metrics = self.analytics.collect_performance_metrics()
        
        # Проверки
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.cpu_usage == 45.5
        assert metrics.memory_usage == 67.8
        assert metrics.disk_usage == 23.4
        assert metrics.throughput == 3000
        
        # Проверка логирования
        events = self.analytics.get_security_events()
        assert len(events) > 0
        assert any(e.get('event_type') == 'performance_metrics_collected' for e in events)
    
    def test_collect_security_metrics_no_events(self):
        """Тест сбора метрик безопасности без событий"""
        metrics = self.analytics.collect_security_metrics()
        
        assert isinstance(metrics, SecurityMetrics)
        assert metrics.threats_detected == 0
        assert metrics.threats_blocked == 0
        assert metrics.security_score == 100.0
        assert metrics.risk_level == "low"
    
    def test_collect_security_metrics_with_events(self):
        """Тест сбора метрик безопасности с событиями"""
        # Добавление тестовых событий
        self.analytics.add_security_event(
            event_type="threat_detected",
            description="Тестовая угроза",
            severity="warning",
            source="TestSource"
        )
        self.analytics.add_security_event(
            event_type="threat_blocked",
            description="Блокировка угрозы",
            severity="info",
            source="TestSource"
        )
        
        # Выполнение
        metrics = self.analytics.collect_security_metrics()
        
        # Проверки
        assert metrics.threats_detected == 1
        assert metrics.threats_blocked == 1
        assert metrics.security_score == 100.0
        assert metrics.risk_level == "low"
    
    def test_collect_family_metrics_no_events(self):
        """Тест сбора семейных метрик без событий"""
        metrics = self.analytics.collect_family_metrics()
        
        assert isinstance(metrics, FamilyMetrics)
        assert metrics.active_users == 0
        assert metrics.parental_controls_active == 0
        assert metrics.child_activities_monitored == 0
        assert metrics.elderly_protection_active == 0
        assert metrics.family_security_score == 100.0
    
    def test_collect_family_metrics_with_events(self):
        """Тест сбора семейных метрик с событиями"""
        # Добавление тестовых семейных событий
        self.analytics.add_security_event(
            event_type="family_parental_control",
            description="Родительский контроль",
            severity="info",
            source="TestSource",
            metadata={"user_id": "parent1"}
        )
        self.analytics.add_security_event(
            event_type="family_child_activity",
            description="Детская активность",
            severity="info",
            source="TestSource",
            metadata={"user_id": "child1"}
        )
        self.analytics.add_security_event(
            event_type="family_elderly_protection",
            description="Защита пожилых",
            severity="info",
            source="TestSource",
            metadata={"user_id": "elderly1"}
        )
        
        # Выполнение
        metrics = self.analytics.collect_family_metrics()
        
        # Проверки
        assert metrics.active_users == 3
        assert metrics.parental_controls_active == 1
        assert metrics.child_activities_monitored == 1
        assert metrics.elderly_protection_active == 1
        assert metrics.family_security_score == 100.0
    
    def test_generate_analytics_report_performance(self):
        """Тест генерации отчета производительности"""
        with patch.object(self.analytics, 'collect_performance_metrics') as mock_collect:
            mock_metrics = PerformanceMetrics(
                cpu_usage=45.0, memory_usage=67.0, disk_usage=23.0,
                network_latency=10.0, response_time=100.0, throughput=1000.0,
                error_rate=2.0, availability=99.9
            )
            mock_collect.return_value = mock_metrics
            
            report = self.analytics.generate_analytics_report(AnalyticsType.PERFORMANCE, 24)
            
            assert isinstance(report, AnalyticsReport)
            assert report.report_type == AnalyticsType.PERFORMANCE
            assert "analytics_performance_" in report.report_id
            assert len(report.insights) > 0
            assert len(report.recommendations) > 0
            assert len(report.alerts) >= 0
            assert isinstance(report.family_impact, dict)
    
    def test_generate_analytics_report_security(self):
        """Тест генерации отчета безопасности"""
        with patch.object(self.analytics, 'collect_security_metrics') as mock_collect:
            mock_metrics = SecurityMetrics(
                threats_detected=5, threats_blocked=4, false_positives=1,
                false_negatives=0, security_score=80.0, compliance_score=85.0,
                risk_level="medium", protection_coverage=90.0
            )
            mock_collect.return_value = mock_metrics
            
            report = self.analytics.generate_analytics_report(AnalyticsType.SECURITY, 24)
            
            assert isinstance(report, AnalyticsReport)
            assert report.report_type == AnalyticsType.SECURITY
            assert "analytics_security_" in report.report_id
            assert len(report.insights) > 0
            assert len(report.recommendations) > 0
            assert len(report.alerts) >= 0
    
    def test_generate_analytics_report_family(self):
        """Тест генерации семейного отчета"""
        with patch.object(self.analytics, 'collect_family_metrics') as mock_collect:
            mock_metrics = FamilyMetrics(
                total_family_members=4, active_users=3, parental_controls_active=2,
                child_activities_monitored=1, elderly_protection_active=1,
                family_security_score=85.0, age_appropriate_protection={}
            )
            mock_collect.return_value = mock_metrics
            
            report = self.analytics.generate_analytics_report(AnalyticsType.FAMILY, 24)
            
            assert isinstance(report, AnalyticsReport)
            assert report.report_type == AnalyticsType.FAMILY
            assert "analytics_family_" in report.report_id
            assert len(report.insights) > 0
            assert len(report.recommendations) > 0
            assert len(report.alerts) >= 0
            assert "total_family_members" in report.family_impact
    
    def test_generate_insights_performance(self):
        """Тест генерации инсайтов производительности"""
        # Тест с высоким CPU
        high_cpu_metrics = PerformanceMetrics(
            cpu_usage=85.0, memory_usage=50.0, disk_usage=30.0,
            network_latency=10.0, response_time=100.0, throughput=1000.0,
            error_rate=2.0, availability=99.9
        )
        
        insights = self.analytics._generate_insights(AnalyticsType.PERFORMANCE, high_cpu_metrics)
        assert len(insights) > 0
        assert any("CPU" in insight for insight in insights)
        
        # Тест с высоким использованием памяти
        high_memory_metrics = PerformanceMetrics(
            cpu_usage=50.0, memory_usage=90.0, disk_usage=30.0,
            network_latency=10.0, response_time=100.0, throughput=1000.0,
            error_rate=2.0, availability=99.9
        )
        
        insights = self.analytics._generate_insights(AnalyticsType.PERFORMANCE, high_memory_metrics)
        assert len(insights) > 0
        assert any("памяти" in insight for insight in insights)
    
    def test_generate_insights_security(self):
        """Тест генерации инсайтов безопасности"""
        # Тест с низким показателем безопасности
        low_security_metrics = SecurityMetrics(
            threats_detected=10, threats_blocked=5, false_positives=2,
            false_negatives=1, security_score=50.0, compliance_score=60.0,
            risk_level="high", protection_coverage=70.0
        )
        
        insights = self.analytics._generate_insights(AnalyticsType.SECURITY, low_security_metrics)
        assert len(insights) > 0
        assert any("безопасности" in insight for insight in insights)
        assert any("риска" in insight for insight in insights)
    
    def test_generate_insights_family(self):
        """Тест генерации семейных инсайтов"""
        # Тест с низким семейным показателем
        low_family_metrics = FamilyMetrics(
            total_family_members=4, active_users=2, parental_controls_active=0,
            child_activities_monitored=0, elderly_protection_active=0,
            family_security_score=50.0, age_appropriate_protection={}
        )
        
        insights = self.analytics._generate_insights(AnalyticsType.FAMILY, low_family_metrics)
        assert len(insights) > 0
        assert any("Семейная" in insight for insight in insights)
        assert any("контроли" in insight for insight in insights)
    
    def test_generate_recommendations_performance(self):
        """Тест генерации рекомендаций производительности"""
        high_cpu_metrics = PerformanceMetrics(
            cpu_usage=85.0, memory_usage=50.0, disk_usage=30.0,
            network_latency=10.0, response_time=100.0, throughput=1000.0,
            error_rate=2.0, availability=99.9
        )
        
        recommendations = self.analytics._generate_recommendations(AnalyticsType.PERFORMANCE, high_cpu_metrics)
        assert len(recommendations) > 0
        assert any("CPU" in rec for rec in recommendations)
    
    def test_generate_recommendations_security(self):
        """Тест генерации рекомендаций безопасности"""
        low_security_metrics = SecurityMetrics(
            threats_detected=10, threats_blocked=5, false_positives=2,
            false_negatives=1, security_score=50.0, compliance_score=60.0,
            risk_level="high", protection_coverage=70.0
        )
        
        recommendations = self.analytics._generate_recommendations(AnalyticsType.SECURITY, low_security_metrics)
        assert len(recommendations) > 0
        assert any("безопасности" in rec for rec in recommendations)
    
    def test_generate_recommendations_family(self):
        """Тест генерации семейных рекомендаций"""
        low_family_metrics = FamilyMetrics(
            total_family_members=4, active_users=2, parental_controls_active=0,
            child_activities_monitored=0, elderly_protection_active=0,
            family_security_score=50.0, age_appropriate_protection={}
        )
        
        recommendations = self.analytics._generate_recommendations(AnalyticsType.FAMILY, low_family_metrics)
        assert len(recommendations) > 0
        assert any("семейные" in rec for rec in recommendations)
        assert any("контроли" in rec for rec in recommendations)
    
    def test_check_alerts_performance(self):
        """Тест проверки оповещений производительности"""
        high_cpu_metrics = PerformanceMetrics(
            cpu_usage=85.0, memory_usage=50.0, disk_usage=30.0,
            network_latency=10.0, response_time=100.0, throughput=1000.0,
            error_rate=2.0, availability=99.9
        )
        
        alerts = self.analytics._check_alerts(AnalyticsType.PERFORMANCE, high_cpu_metrics)
        assert len(alerts) > 0
        assert any(alert["metric"] == "cpu_usage" for alert in alerts)
        assert any(alert["level"] == AlertLevel.WARNING.value for alert in alerts)
    
    def test_check_alerts_security(self):
        """Тест проверки оповещений безопасности"""
        low_security_metrics = SecurityMetrics(
            threats_detected=10, threats_blocked=5, false_positives=2,
            false_negatives=1, security_score=50.0, compliance_score=60.0,
            risk_level="high", protection_coverage=70.0
        )
        
        alerts = self.analytics._check_alerts(AnalyticsType.SECURITY, low_security_metrics)
        assert len(alerts) > 0
        assert any(alert["metric"] == "security_score" for alert in alerts)
        assert any(alert["level"] == AlertLevel.CRITICAL.value for alert in alerts)
    
    def test_check_alerts_family(self):
        """Тест проверки семейных оповещений"""
        low_family_metrics = FamilyMetrics(
            total_family_members=4, active_users=2, parental_controls_active=0,
            child_activities_monitored=0, elderly_protection_active=0,
            family_security_score=50.0, age_appropriate_protection={}
        )
        
        alerts = self.analytics._check_alerts(AnalyticsType.FAMILY, low_family_metrics)
        assert len(alerts) > 0
        assert any(alert["metric"] == "family_security_score" for alert in alerts)
        assert any(alert["level"] == AlertLevel.WARNING.value for alert in alerts)
    
    def test_analyze_family_impact_family_type(self):
        """Тест анализа семейного воздействия для семейного типа"""
        family_metrics = FamilyMetrics(
            total_family_members=4, active_users=3, parental_controls_active=2,
            child_activities_monitored=1, elderly_protection_active=1,
            family_security_score=85.0, age_appropriate_protection={"children": 90.0}
        )
        
        impact = self.analytics._analyze_family_impact(AnalyticsType.FAMILY, family_metrics)
        
        assert "total_family_members" in impact
        assert "active_users" in impact
        assert "security_score" in impact
        assert "protection_coverage" in impact
        assert "recommendations" in impact
        assert impact["total_family_members"] == 4
        assert impact["active_users"] == 3
        assert impact["security_score"] == 85.0
    
    def test_analyze_family_impact_non_family_type(self):
        """Тест анализа семейного воздействия для не-семейного типа"""
        performance_metrics = PerformanceMetrics(
            cpu_usage=50.0, memory_usage=60.0, disk_usage=30.0,
            network_latency=10.0, response_time=100.0, throughput=1000.0,
            error_rate=2.0, availability=99.9
        )
        
        impact = self.analytics._analyze_family_impact(AnalyticsType.PERFORMANCE, performance_metrics)
        
        assert "impact_level" in impact
        assert "affected_members" in impact
        assert "recommendations" in impact
        assert impact["impact_level"] == "low"
        assert impact["affected_members"] == 0
    
    def test_generate_family_recommendations(self):
        """Тест генерации семейных рекомендаций"""
        low_family_metrics = FamilyMetrics(
            total_family_members=4, active_users=2, parental_controls_active=0,
            child_activities_monitored=0, elderly_protection_active=0,
            family_security_score=50.0, age_appropriate_protection={}
        )
        
        recommendations = self.analytics._generate_family_recommendations(low_family_metrics)
        assert len(recommendations) > 0
        assert any("семейные" in rec for rec in recommendations)
        assert any("контроли" in rec for rec in recommendations)
        assert any("пожилых" in rec for rec in recommendations)
        assert any("детской" in rec for rec in recommendations)
    
    def test_get_analytics_summary(self):
        """Тест получения сводки аналитики"""
        # Добавление тестового отчета
        report = AnalyticsReport(
            report_id="test_report",
            report_type=AnalyticsType.SECURITY,
            generated_at=datetime.now(),
            period_start=datetime.now() - timedelta(hours=24),
            period_end=datetime.now()
        )
        self.analytics.analytics_history.append(report)
        
        summary = self.analytics.get_analytics_summary()
        
        assert "total_reports" in summary
        assert "performance_metrics" in summary
        assert "security_metrics" in summary
        assert "family_metrics" in summary
        assert "last_updated" in summary
        assert summary["total_reports"] == 1
    
    def test_get_status(self):
        """Тест получения статуса"""
        status = self.analytics.get_status()
        
        assert "service_name" in status
        assert "status" in status
        assert "analytics_type" in status
        assert "total_reports" in status
        assert "performance_metrics" in status
        assert "security_metrics" in status
        assert "family_metrics" in status
        assert "alert_thresholds" in status
        assert "last_updated" in status
        
        assert status["service_name"] == "SecurityAnalytics"
        assert status["status"] == "active"
        assert status["analytics_type"] == AnalyticsType.SECURITY.value
    
    def test_error_handling_performance_metrics(self):
        """Тест обработки ошибок при сборе метрик производительности"""
        with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
            metrics = self.analytics.collect_performance_metrics()
            
            # Должны вернуться метрики по умолчанию
            assert isinstance(metrics, PerformanceMetrics)
            
            # Должно быть залогировано событие об ошибке
            events = self.analytics.get_security_events()
            assert any(e.get('event_type') == 'performance_metrics_error' for e in events)
    
    def test_error_handling_security_metrics(self):
        """Тест обработки ошибок при сборе метрик безопасности"""
        # Создаем новый экземпляр для тестирования ошибок
        analytics_with_error = SecurityAnalytics()
        
        with patch.object(analytics_with_error, 'get_security_events', side_effect=Exception("Test error")):
            metrics = analytics_with_error.collect_security_metrics()
            
            # Должны вернуться метрики по умолчанию
            assert isinstance(metrics, SecurityMetrics)
            
            # Проверяем, что событие об ошибке было добавлено в activity_log
            assert len(analytics_with_error.activity_log) > 0
            assert any('security_metrics_error' in str(event) for event in analytics_with_error.activity_log)
    
    def test_error_handling_family_metrics(self):
        """Тест обработки ошибок при сборе семейных метрик"""
        # Создаем новый экземпляр для тестирования ошибок
        analytics_with_error = SecurityAnalytics()
        
        with patch.object(analytics_with_error, 'get_security_events', side_effect=Exception("Test error")):
            metrics = analytics_with_error.collect_family_metrics()
            
            # Должны вернуться метрики по умолчанию
            assert isinstance(metrics, FamilyMetrics)
            
            # Проверяем, что событие об ошибке было добавлено в activity_log
            assert len(analytics_with_error.activity_log) > 0
            assert any('family_metrics_error' in str(event) for event in analytics_with_error.activity_log)
    
    def test_error_handling_report_generation(self):
        """Тест обработки ошибок при генерации отчета"""
        with patch.object(self.analytics, 'collect_security_metrics', side_effect=Exception("Test error")):
            report = self.analytics.generate_analytics_report(AnalyticsType.SECURITY, 24)
            
            # Должен вернуться None при ошибке
            assert report is None
            
            # Должно быть залогировано событие об ошибке
            events = self.analytics.get_security_events()
            assert any(e.get('event_type') == 'analytics_report_error' for e in events)
    
    def test_error_handling_summary(self):
        """Тест обработки ошибок при получении сводки"""
        # Создаем новый экземпляр для тестирования ошибок
        analytics_with_error = SecurityAnalytics()
        
        # Мокаем datetime.now() чтобы вызвать ошибку
        with patch('security.reactive.security_analytics.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("Test error")
            summary = analytics_with_error.get_analytics_summary()
            
            # Должен вернуться пустой словарь при ошибке
            assert summary == {}
            
            # Проверяем, что событие об ошибке было добавлено в activity_log
            assert len(analytics_with_error.activity_log) > 0
            assert any('analytics_summary_error' in str(event) for event in analytics_with_error.activity_log)
    
    def test_error_handling_status(self):
        """Тест обработки ошибок при получении статуса"""
        # Создаем новый экземпляр для тестирования ошибок
        analytics_with_error = SecurityAnalytics()
        
        # Мокаем datetime.now() чтобы вызвать ошибку
        with patch('security.reactive.security_analytics.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("Test error")
            status = analytics_with_error.get_status()
            
            # Должен вернуться словарь с ошибкой
            assert "error" in status
            
            # Проверяем, что событие об ошибке было добавлено в activity_log
            assert len(analytics_with_error.activity_log) > 0
            assert any('status_error' in str(event) for event in analytics_with_error.activity_log)