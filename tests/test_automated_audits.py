#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для системы автоматических аудитов
Проверка функциональности аудитов, планировщика и мониторинга соответствия

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
Качество: A+
"""

import asyncio
import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Импорты для тестирования
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automated_audit_system import AutomatedAuditSystem, AuditType, AuditSeverity, ComplianceStandard, AuditResult
from audit_scheduler import AuditScheduler, AuditSchedule, NotificationConfig
from compliance_monitor import ComplianceMonitor, ComplianceStandard as CMComplianceStandard, ComplianceLevel

class TestAutomatedAuditSystem:
    """Тесты системы автоматических аудитов"""
    
    @pytest.fixture
    def audit_system(self):
        """Фикстура для системы аудитов"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        system = AutomatedAuditSystem(db_path)
        yield system
        
        # Очистка
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_audit_system_initialization(self, audit_system):
        """Тест инициализации системы аудитов"""
        assert audit_system is not None
        assert os.path.exists(audit_system.db_path)
        print("✅ Система аудитов инициализирована корректно")
    
    def test_audit_result_creation(self):
        """Тест создания результата аудита"""
        result = AuditResult(
            audit_id="test_audit_001",
            audit_type=AuditType.SECURITY,
            severity=AuditSeverity.HIGH,
            title="Test Security Audit",
            description="Test audit for security",
            status="passed",
            score=85.0,
            findings=[{"type": "test", "description": "Test finding"}],
            recommendations=["Test recommendation"],
            timestamp=datetime.now(),
            duration=1.5,
            compliance_standards=[ComplianceStandard.ISO_27001],
            metadata={"test": True}
        )
        
        assert result.audit_id == "test_audit_001"
        assert result.audit_type == AuditType.SECURITY
        assert result.severity == AuditSeverity.HIGH
        assert result.score == 85.0
        assert result.status == "passed"
        print("✅ Результат аудита создан корректно")
    
    def test_save_and_load_audit_result(self, audit_system):
        """Тест сохранения и загрузки результата аудита"""
        result = AuditResult(
            audit_id="test_save_001",
            audit_type=AuditType.SECURITY,
            severity=AuditSeverity.MEDIUM,
            title="Test Save Audit",
            description="Test saving audit result",
            status="warning",
            score=75.0,
            findings=[{"type": "test", "description": "Test finding"}],
            recommendations=["Test recommendation"],
            timestamp=datetime.now(),
            duration=2.0,
            compliance_standards=[ComplianceStandard.PCI_DSS],
            metadata={"test": True}
        )
        
        # Сохранение
        audit_system.save_audit_result(result)
        
        # Загрузка
        loaded_results = audit_system.get_audit_results()
        assert len(loaded_results) == 1
        
        loaded_result = loaded_results[0]
        assert loaded_result.audit_id == result.audit_id
        assert loaded_result.audit_type == result.audit_type
        assert loaded_result.score == result.score
        print("✅ Сохранение и загрузка результата аудита работает корректно")
    
    @pytest.mark.asyncio
    async def test_security_audit(self, audit_system):
        """Тест аудита безопасности"""
        result = await audit_system.run_security_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.SECURITY
        assert result.title == "Security Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит безопасности завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_compliance_audit(self, audit_system):
        """Тест аудита соответствия"""
        result = await audit_system.run_compliance_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.COMPLIANCE
        assert result.title == "Compliance Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит соответствия завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_performance_audit(self, audit_system):
        """Тест аудита производительности"""
        result = await audit_system.run_performance_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.PERFORMANCE
        assert result.title == "Performance Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит производительности завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_code_quality_audit(self, audit_system):
        """Тест аудита качества кода"""
        result = await audit_system.run_code_quality_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.CODE_QUALITY
        assert result.title == "Code Quality Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит качества кода завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_dependencies_audit(self, audit_system):
        """Тест аудита зависимостей"""
        result = await audit_system.run_dependencies_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.DEPENDENCIES
        assert result.title == "Dependencies Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит зависимостей завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_infrastructure_audit(self, audit_system):
        """Тест аудита инфраструктуры"""
        result = await audit_system.run_infrastructure_audit()
        
        assert result is not None
        assert result.audit_type == AuditType.INFRASTRUCTURE
        assert result.title == "Infrastructure Audit"
        assert 0 <= result.score <= 100
        assert result.status in ["passed", "warning", "failed"]
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
        assert result.duration > 0
        
        print(f"✅ Аудит инфраструктуры завершен: {result.status} ({result.score}%)")
    
    @pytest.mark.asyncio
    async def test_run_all_audits(self, audit_system):
        """Тест запуска всех аудитов"""
        results = await audit_system.run_all_audits()
        
        assert isinstance(results, list)
        assert len(results) == 6  # 6 типов аудитов
        
        # Проверяем, что все типы аудитов выполнены
        audit_types = {result.audit_type for result in results}
        expected_types = {
            AuditType.SECURITY,
            AuditType.COMPLIANCE,
            AuditType.PERFORMANCE,
            AuditType.CODE_QUALITY,
            AuditType.DEPENDENCIES,
            AuditType.INFRASTRUCTURE
        }
        assert audit_types == expected_types
        
        print(f"✅ Все {len(results)} аудитов выполнены успешно")
    
    def test_audit_report_generation(self, audit_system):
        """Тест генерации отчета по аудитам"""
        # Создаем тестовые результаты
        results = [
            AuditResult(
                audit_id="test_001",
                audit_type=AuditType.SECURITY,
                severity=AuditSeverity.HIGH,
                title="Test Security",
                description="Test",
                status="passed",
                score=85.0,
                findings=[],
                recommendations=[],
                timestamp=datetime.now(),
                duration=1.0,
                compliance_standards=[],
                metadata={}
            ),
            AuditResult(
                audit_id="test_002",
                audit_type=AuditType.COMPLIANCE,
                severity=AuditSeverity.MEDIUM,
                title="Test Compliance",
                description="Test",
                status="warning",
                score=75.0,
                findings=[{"severity": "medium"}],
                recommendations=[],
                timestamp=datetime.now(),
                duration=2.0,
                compliance_standards=[],
                metadata={}
            )
        ]
        
        report = audit_system.generate_audit_report(results)
        
        assert "summary" in report
        assert "audits" in report
        assert "timestamp" in report
        
        summary = report["summary"]
        assert summary["total_audits"] == 2
        assert summary["passed"] == 1
        assert summary["warning"] == 1
        assert summary["failed"] == 0
        assert summary["average_score"] == 80.0
        
        print("✅ Отчет по аудитам сгенерирован корректно")

class TestAuditScheduler:
    """Тесты планировщика аудитов"""
    
    @pytest.fixture
    def scheduler(self):
        """Фикстура для планировщика"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        sched = AuditScheduler(db_path)
        yield sched
        
        # Очистка
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_scheduler_initialization(self, scheduler):
        """Тест инициализации планировщика"""
        assert scheduler is not None
        assert os.path.exists(scheduler.db_path)
        print("✅ Планировщик аудитов инициализирован корректно")
    
    def test_add_schedule(self, scheduler):
        """Тест добавления расписания"""
        initial_count = len(scheduler.schedules)
        
        scheduler.add_schedule(AuditType.SECURITY, "daily", "02:00")
        
        assert len(scheduler.schedules) == initial_count + 1
        
        new_schedule = scheduler.schedules[-1]
        assert new_schedule.audit_type == AuditType.SECURITY
        assert new_schedule.frequency == "daily"
        assert new_schedule.time == "02:00"
        assert new_schedule.enabled == True
        assert new_schedule.next_run is not None
        
        print("✅ Расписание добавлено корректно")
    
    def test_schedule_status(self, scheduler):
        """Тест получения статуса расписаний"""
        # Добавляем тестовое расписание
        scheduler.add_schedule(AuditType.SECURITY, "daily", "02:00")
        
        status = scheduler.get_schedule_status()
        
        assert "total_schedules" in status
        assert "enabled_schedules" in status
        assert "disabled_schedules" in status
        assert "schedules" in status
        
        assert status["total_schedules"] >= 1
        assert len(status["schedules"]) >= 1
        
        schedule_info = status["schedules"][0]
        assert "audit_type" in schedule_info
        assert "frequency" in schedule_info
        assert "time" in schedule_info
        assert "enabled" in schedule_info
        assert "last_run" in schedule_info
        assert "next_run" in schedule_info
        assert "overdue" in schedule_info
        
        print("✅ Статус расписаний получен корректно")
    
    def test_notification_config(self, scheduler):
        """Тест конфигурации уведомлений"""
        config = scheduler.notification_config
        
        assert isinstance(config.email_enabled, bool)
        assert isinstance(config.slack_enabled, bool)
        assert isinstance(config.telegram_enabled, bool)
        
        print("✅ Конфигурация уведомлений корректна")

class TestComplianceMonitor:
    """Тесты монитора соответствия"""
    
    @pytest.fixture
    def monitor(self):
        """Фикстура для монитора соответствия"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        mon = ComplianceMonitor(db_path)
        yield mon
        
        # Очистка
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_monitor_initialization(self, monitor):
        """Тест инициализации монитора"""
        assert monitor is not None
        assert os.path.exists(monitor.db_path)
        print("✅ Монитор соответствия инициализирован корректно")
    
    def test_initialize_default_requirements(self, monitor):
        """Тест инициализации требований по умолчанию"""
        initial_count = len(monitor.requirements)
        
        monitor.initialize_default_requirements()
        
        assert len(monitor.requirements) > initial_count
        
        # Проверяем, что есть требования для разных стандартов
        standards = {req.standard for req in monitor.requirements}
        expected_standards = {
            CMComplianceStandard.GDPR,
            CMComplianceStandard.FEDERAL_152,
            CMComplianceStandard.PCI_DSS,
            CMComplianceStandard.ISO_27001
        }
        
        assert expected_standards.issubset(standards)
        print(f"✅ Инициализировано {len(monitor.requirements)} требований соответствия")
    
    @pytest.mark.asyncio
    async def test_assess_compliance(self, monitor):
        """Тест оценки соответствия"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        # Оцениваем соответствие GDPR
        assessment = await monitor.assess_compliance(CMComplianceStandard.GDPR)
        
        assert assessment is not None
        assert assessment.standard == CMComplianceStandard.GDPR
        assert 0 <= assessment.score <= 100
        assert assessment.overall_level in [ComplianceLevel.COMPLIANT, ComplianceLevel.PARTIALLY_COMPLIANT, ComplianceLevel.NON_COMPLIANT]
        assert assessment.requirements_total > 0
        assert isinstance(assessment.critical_issues, list)
        assert isinstance(assessment.recommendations, list)
        
        print(f"✅ Оценка соответствия GDPR: {assessment.overall_level.value} ({assessment.score}%)")
    
    @pytest.mark.asyncio
    async def test_assess_all_standards(self, monitor):
        """Тест оценки соответствия всем стандартам"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        assessments = await monitor.assess_all_standards()
        
        assert isinstance(assessments, list)
        assert len(assessments) > 0
        
        # Проверяем, что есть оценки для разных стандартов
        standards = {assessment.standard for assessment in assessments}
        assert len(standards) > 1
        
        print(f"✅ Оценка соответствия {len(assessments)} стандартам завершена")
    
    def test_compliance_dashboard(self, monitor):
        """Тест дашборда соответствия"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        dashboard = monitor.get_compliance_dashboard()
        
        assert "summary" in dashboard
        assert "standards" in dashboard
        assert "critical_issues" in dashboard
        assert "last_updated" in dashboard
        
        summary = dashboard["summary"]
        assert "total_assessments" in summary
        assert "compliant" in summary
        assert "partially_compliant" in summary
        assert "non_compliant" in summary
        assert "average_score" in summary
        assert "critical_issues_count" in summary
        
        print("✅ Дашборд соответствия сгенерирован корректно")
    
    def test_requirements_status(self, monitor):
        """Тест получения статуса требований"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        # Получаем все требования
        all_requirements = monitor.get_requirements_status()
        assert len(all_requirements) > 0
        
        # Получаем требования для GDPR
        gdpr_requirements = monitor.get_requirements_status(CMComplianceStandard.GDPR)
        assert len(gdpr_requirements) > 0
        
        # Проверяем структуру требования
        if gdpr_requirements:
            req = gdpr_requirements[0]
            assert "id" in req
            assert "standard" in req
            assert "title" in req
            assert "description" in req
            assert "category" in req
            assert "priority" in req
            assert "implementation_status" in req
        
        print(f"✅ Статус {len(all_requirements)} требований получен корректно")
    
    def test_update_requirement_status(self, monitor):
        """Тест обновления статуса требования"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        # Находим первое требование
        if monitor.requirements:
            req_id = monitor.requirements[0].id
            initial_status = monitor.requirements[0].implementation_status
            
            # Обновляем статус
            monitor.update_requirement_status(req_id, "implemented", ["test_evidence"], "Test notes")
            
            # Проверяем обновление
            updated_req = next((r for r in monitor.requirements if r.id == req_id), None)
            assert updated_req is not None
            assert updated_req.implementation_status == "implemented"
            assert "test_evidence" in updated_req.evidence
            assert "Test notes" in updated_req.notes
            
            print(f"✅ Статус требования {req_id} обновлен корректно")
    
    def test_generate_compliance_report(self, monitor):
        """Тест генерации отчета по соответствию"""
        # Инициализируем требования
        monitor.initialize_default_requirements()
        
        # Генерируем отчет для GDPR
        report = monitor.generate_compliance_report(CMComplianceStandard.GDPR)
        
        assert "standard" in report
        assert "requirements" in report
        assert "generated_at" in report
        
        assert report["standard"] == CMComplianceStandard.GDPR.value
        assert isinstance(report["requirements"], list)
        
        print("✅ Отчет по соответствию сгенерирован корректно")

class TestAuditIntegration:
    """Тесты интеграции систем аудитов"""
    
    @pytest.mark.asyncio
    async def test_full_audit_workflow(self):
        """Тест полного рабочего процесса аудитов"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Создаем системы
            audit_system = AutomatedAuditSystem(db_path)
            scheduler = AuditScheduler(db_path)
            monitor = ComplianceMonitor(db_path)
            
            # Инициализируем требования соответствия
            monitor.initialize_default_requirements()
            
            # Запускаем все аудиты
            audit_results = await audit_system.run_all_audits()
            assert len(audit_results) == 6
            
            # Оцениваем соответствие
            compliance_assessments = await monitor.assess_all_standards()
            assert len(compliance_assessments) > 0
            
            # Добавляем расписание
            scheduler.add_schedule(AuditType.SECURITY, "daily", "02:00")
            assert len(scheduler.schedules) >= 1
            
            # Генерируем отчеты
            audit_report = audit_system.generate_audit_report(audit_results)
            compliance_dashboard = monitor.get_compliance_dashboard()
            
            assert "summary" in audit_report
            assert "summary" in compliance_dashboard
            
            print("✅ Полный рабочий процесс аудитов выполнен успешно")
            
        finally:
            # Очистка
            try:
                os.unlink(db_path)
            except:
                pass
    
    def test_audit_data_consistency(self):
        """Тест согласованности данных аудитов"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            audit_system = AutomatedAuditSystem(db_path)
            
            # Создаем тестовый результат
            result = AuditResult(
                audit_id="consistency_test_001",
                audit_type=AuditType.SECURITY,
                severity=AuditSeverity.HIGH,
                title="Consistency Test",
                description="Test for data consistency",
                status="passed",
                score=90.0,
                findings=[{"type": "test", "severity": "medium"}],
                recommendations=["Test recommendation"],
                timestamp=datetime.now(),
                duration=1.5,
                compliance_standards=[ComplianceStandard.ISO_27001],
                metadata={"test": True, "consistency": "verified"}
            )
            
            # Сохраняем
            audit_system.save_audit_result(result)
            
            # Загружаем
            loaded_results = audit_system.get_audit_results()
            assert len(loaded_results) == 1
            
            loaded_result = loaded_results[0]
            
            # Проверяем согласованность
            assert loaded_result.audit_id == result.audit_id
            assert loaded_result.audit_type == result.audit_type
            assert loaded_result.severity == result.severity
            assert loaded_result.score == result.score
            assert loaded_result.status == result.status
            assert len(loaded_result.findings) == len(result.findings)
            assert len(loaded_result.recommendations) == len(result.recommendations)
            assert len(loaded_result.compliance_standards) == len(result.compliance_standards)
            
            print("✅ Согласованность данных аудитов проверена")
            
        finally:
            # Очистка
            try:
                os.unlink(db_path)
            except:
                pass

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])