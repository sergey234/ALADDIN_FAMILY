#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система автоматического реагирования на инциденты
Автоматическое обнаружение, анализ и реагирование на угрозы
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Уровни серьезности инцидентов"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Статусы инцидентов"""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESPONDING = "responding"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ResponseAction(Enum):
    """Действия реагирования"""
    ISOLATE = "isolate"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ALERT = "alert"
    ESCALATE = "escalate"
    INVESTIGATE = "investigate"
    MONITOR = "monitor"
    RESTORE = "restore"

class ThreatType(Enum):
    """Типы угроз"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    INTRUSION = "intrusion"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    RANSOMWARE = "ransomware"

@dataclass
class Incident:
    """Инцидент безопасности"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    threat_type: ThreatType
    detected_at: datetime
    affected_systems: List[str]
    indicators: List[str]
    response_actions: List[ResponseAction]
    assigned_team: Optional[str] = None
    estimated_resolution: Optional[datetime] = None
    actual_resolution: Optional[datetime] = None
    impact_assessment: str = ""
    root_cause: str = ""
    lessons_learned: str = ""
    
    def __init__(self, title: str, description: str, severity: IncidentSeverity, threat_type: ThreatType, affected_systems: List[str], indicators: List[str]):
        self.incident_id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.severity = severity
        self.status = IncidentStatus.DETECTED
        self.threat_type = threat_type
        self.detected_at = datetime.now()
        self.affected_systems = affected_systems
        self.indicators = indicators
        self.response_actions = []
        self.assigned_team = None
        self.estimated_resolution = None
        self.actual_resolution = None
        self.impact_assessment = ""
        self.root_cause = ""
        self.lessons_learned = ""

@dataclass
class ResponsePlan:
    """План реагирования"""
    plan_id: str
    name: str
    threat_types: List[ThreatType]
    severity_levels: List[IncidentSeverity]
    actions: List[ResponseAction]
    escalation_rules: Dict[str, Any]
    time_constraints: Dict[str, int]  # минуты
    required_resources: List[str]
    success_criteria: List[str]
    
    def __init__(self, name: str, threat_types: List[ThreatType], severity_levels: List[IncidentSeverity], actions: List[ResponseAction]):
        self.plan_id = str(uuid.uuid4())
        self.name = name
        self.threat_types = threat_types
        self.severity_levels = severity_levels
        self.actions = actions
        self.escalation_rules = {}
        self.time_constraints = {}
        self.required_resources = []
        self.success_criteria = []

class IncidentResponseSystem:
    """
    Система автоматического реагирования на инциденты
    """
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.response_plans: Dict[str, ResponsePlan] = {}
        self.automated_responses: Dict[str, List[ResponseAction]] = {}
        self.escalation_rules: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.IncidentResponseSystem")
        
    async def initialize(self):
        """Инициализация системы реагирования"""
        try:
            # Создаем базовые планы реагирования
            await self._create_default_response_plans()
            
            # Настраиваем правила эскалации
            self.escalation_rules = {
                "critical": {"escalate_immediately": True, "notify_executives": True},
                "high": {"escalate_after": 30, "notify_management": True},
                "medium": {"escalate_after": 120, "notify_team": True},
                "low": {"escalate_after": 480, "monitor": True}
            }
            
            self.logger.info("Система реагирования на инциденты инициализирована")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системы реагирования: {e}")
            return False
    
    async def detect_incident(self, title: str, description: str, severity: IncidentSeverity, threat_type: ThreatType, affected_systems: List[str], indicators: List[str]) -> str:
        """Обнаружение нового инцидента"""
        try:
            incident = Incident(title, description, severity, threat_type, affected_systems, indicators)
            self.incidents[incident.incident_id] = incident
            
            # Автоматический анализ и реагирование
            await self._analyze_incident(incident)
            await self._execute_automated_response(incident)
            
            self.logger.info(f"Инцидент {incident.incident_id} обнаружен: {title}")
            return incident.incident_id
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения инцидента: {e}")
            return None
    
    async def analyze_incident(self, incident_id: str) -> Dict[str, Any]:
        """Анализ инцидента"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.ANALYZING
            
            # Анализ угрозы
            threat_analysis = await self._analyze_threat(incident)
            
            # Анализ воздействия
            impact_analysis = await self._analyze_impact(incident)
            
            # Анализ корневой причины
            root_cause_analysis = await self._analyze_root_cause(incident)
            
            # Рекомендации по реагированию
            response_recommendations = await self._get_response_recommendations(incident)
            
            analysis_result = {
                "incident_id": incident_id,
                "threat_analysis": threat_analysis,
                "impact_analysis": impact_analysis,
                "root_cause_analysis": root_cause_analysis,
                "response_recommendations": response_recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Анализ инцидента {incident_id} завершен")
            return analysis_result
        except Exception as e:
            self.logger.error(f"Ошибка анализа инцидента {incident_id}: {e}")
            return {"error": str(e)}
    
    async def respond_to_incident(self, incident_id: str, actions: List[ResponseAction]) -> Dict[str, Any]:
        """Реагирование на инцидент"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.RESPONDING
            incident.response_actions.extend(actions)
            
            # Выполнение действий реагирования
            response_results = []
            for action in actions:
                result = await self._execute_response_action(incident, action)
                response_results.append({
                    "action": action.value,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Обновление статуса
            if all(r["result"]["success"] for r in response_results):
                incident.status = IncidentStatus.CONTAINED
                self.logger.info(f"Инцидент {incident_id} сдержан")
            else:
                self.logger.warning(f"Не все действия реагирования выполнены успешно для инцидента {incident_id}")
            
            return {
                "incident_id": incident_id,
                "actions_executed": len(actions),
                "response_results": response_results,
                "current_status": incident.status.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка реагирования на инцидент {incident_id}: {e}")
            return {"error": str(e)}
    
    async def resolve_incident(self, incident_id: str, resolution_notes: str, lessons_learned: str = "") -> Dict[str, Any]:
        """Разрешение инцидента"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.RESOLVED
            incident.actual_resolution = datetime.now()
            incident.lessons_learned = lessons_learned
            
            # Генерация отчета о разрешении
            resolution_report = await self._generate_resolution_report(incident)
            
            self.logger.info(f"Инцидент {incident_id} разрешен")
            
            return {
                "incident_id": incident_id,
                "status": "resolved",
                "resolution_time": incident.actual_resolution.isoformat(),
                "resolution_notes": resolution_notes,
                "lessons_learned": lessons_learned,
                "resolution_report": resolution_report
            }
        except Exception as e:
            self.logger.error(f"Ошибка разрешения инцидента {incident_id}: {e}")
            return {"error": str(e)}
    
    async def get_incident_status(self, incident_id: str) -> Dict[str, Any]:
        """Получение статуса инцидента"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            
            return {
                "incident_id": incident_id,
                "title": incident.title,
                "status": incident.status.value,
                "severity": incident.severity.value,
                "threat_type": incident.threat_type.value,
                "detected_at": incident.detected_at.isoformat(),
                "affected_systems": incident.affected_systems,
                "response_actions": [action.value for action in incident.response_actions],
                "assigned_team": incident.assigned_team,
                "estimated_resolution": incident.estimated_resolution.isoformat() if incident.estimated_resolution else None,
                "actual_resolution": incident.actual_resolution.isoformat() if incident.actual_resolution else None
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса инцидента {incident_id}: {e}")
            return {"error": str(e)}
    
    async def get_all_incidents(self, status_filter: Optional[IncidentStatus] = None, severity_filter: Optional[IncidentSeverity] = None) -> List[Dict[str, Any]]:
        """Получение всех инцидентов с фильтрацией"""
        try:
            incidents_list = []
            
            for incident in self.incidents.values():
                # Применяем фильтры
                if status_filter and incident.status != status_filter:
                    continue
                if severity_filter and incident.severity != severity_filter:
                    continue
                
                incidents_list.append({
                    "incident_id": incident.incident_id,
                    "title": incident.title,
                    "status": incident.status.value,
                    "severity": incident.severity.value,
                    "threat_type": incident.threat_type.value,
                    "detected_at": incident.detected_at.isoformat(),
                    "affected_systems_count": len(incident.affected_systems),
                    "response_actions_count": len(incident.response_actions)
                })
            
            # Сортируем по времени обнаружения (новые первыми)
            incidents_list.sort(key=lambda x: x["detected_at"], reverse=True)
            
            return incidents_list
        except Exception as e:
            self.logger.error(f"Ошибка получения списка инцидентов: {e}")
            return []
    
    async def create_response_plan(self, name: str, threat_types: List[ThreatType], severity_levels: List[IncidentSeverity], actions: List[ResponseAction]) -> str:
        """Создание плана реагирования"""
        try:
            plan = ResponsePlan(name, threat_types, severity_levels, actions)
            self.response_plans[plan.plan_id] = plan
            
            self.logger.info(f"План реагирования {plan.plan_id} создан: {name}")
            return plan.plan_id
        except Exception as e:
            self.logger.error(f"Ошибка создания плана реагирования: {e}")
            return None
    
    async def get_response_plan(self, plan_id: str) -> Optional[ResponsePlan]:
        """Получение плана реагирования"""
        return self.response_plans.get(plan_id)
    
    async def execute_automated_response(self, incident_id: str) -> Dict[str, Any]:
        """Выполнение автоматического реагирования"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            
            # Определяем подходящий план реагирования
            suitable_plan = await self._find_suitable_response_plan(incident)
            
            if not suitable_plan:
                return {"error": "Подходящий план реагирования не найден"}
            
            # Выполняем действия из плана
            executed_actions = []
            for action in suitable_plan.actions:
                result = await self._execute_response_action(incident, action)
                executed_actions.append({
                    "action": action.value,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "incident_id": incident_id,
                "plan_used": suitable_plan.name,
                "actions_executed": len(executed_actions),
                "execution_results": executed_actions,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка автоматического реагирования на инцидент {incident_id}: {e}")
            return {"error": str(e)}
    
    async def escalate_incident(self, incident_id: str, escalation_reason: str) -> Dict[str, Any]:
        """Эскалация инцидента"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            
            # Определяем уровень эскалации
            escalation_level = self._determine_escalation_level(incident)
            
            # Выполняем эскалацию
            escalation_result = await self._perform_escalation(incident, escalation_level, escalation_reason)
            
            return {
                "incident_id": incident_id,
                "escalation_level": escalation_level,
                "escalation_reason": escalation_reason,
                "escalation_result": escalation_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка эскалации инцидента {incident_id}: {e}")
            return {"error": str(e)}
    
    async def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Генерация отчета об инциденте"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Инцидент не найден"}
            
            incident = self.incidents[incident_id]
            
            # Собираем данные для отчета
            report_data = {
                "incident_summary": {
                    "id": incident.incident_id,
                    "title": incident.title,
                    "description": incident.description,
                    "severity": incident.severity.value,
                    "status": incident.status.value,
                    "threat_type": incident.threat_type.value,
                    "detected_at": incident.detected_at.isoformat(),
                    "resolved_at": incident.actual_resolution.isoformat() if incident.actual_resolution else None
                },
                "affected_systems": incident.affected_systems,
                "indicators": incident.indicators,
                "response_actions": [action.value for action in incident.response_actions],
                "timeline": await self._generate_incident_timeline(incident),
                "impact_assessment": incident.impact_assessment,
                "root_cause": incident.root_cause,
                "lessons_learned": incident.lessons_learned,
                "recommendations": await self._generate_recommendations(incident)
            }
            
            return report_data
        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета об инциденте {incident_id}: {e}")
            return {"error": str(e)}
    
    async def _create_default_response_plans(self):
        """Создание базовых планов реагирования"""
        # План для критических инцидентов
        critical_plan = ResponsePlan(
            "Критический инцидент",
            [ThreatType.MALWARE, ThreatType.RANSOMWARE, ThreatType.DATA_BREACH],
            [IncidentSeverity.CRITICAL],
            [ResponseAction.ISOLATE, ResponseAction.BLOCK, ResponseAction.ALERT, ResponseAction.ESCALATE]
        )
        critical_plan.time_constraints = {"isolate": 5, "block": 10, "alert": 2}
        critical_plan.required_resources = ["security_team", "network_admin", "executive_team"]
        critical_plan.success_criteria = ["threat_contained", "systems_isolated", "team_notified"]
        self.response_plans[critical_plan.plan_id] = critical_plan
        
        # План для высоких инцидентов
        high_plan = ResponsePlan(
            "Высокий инцидент",
            [ThreatType.PHISHING, ThreatType.INTRUSION, ThreatType.APT],
            [IncidentSeverity.HIGH],
            [ResponseAction.INVESTIGATE, ResponseAction.MONITOR, ResponseAction.ALERT]
        )
        high_plan.time_constraints = {"investigate": 30, "monitor": 60, "alert": 5}
        high_plan.required_resources = ["security_team", "analyst"]
        high_plan.success_criteria = ["threat_analyzed", "monitoring_enhanced", "team_alerted"]
        self.response_plans[high_plan.plan_id] = high_plan
        
        # План для средних инцидентов
        medium_plan = ResponsePlan(
            "Средний инцидент",
            [ThreatType.DDOS, ThreatType.INSIDER_THREAT],
            [IncidentSeverity.MEDIUM],
            [ResponseAction.MONITOR, ResponseAction.INVESTIGATE]
        )
        medium_plan.time_constraints = {"monitor": 120, "investigate": 240}
        medium_plan.required_resources = ["security_team"]
        medium_plan.success_criteria = ["threat_monitored", "investigation_started"]
        self.response_plans[medium_plan.plan_id] = medium_plan
    
    async def _analyze_incident(self, incident: Incident):
        """Анализ инцидента"""
        incident.status = IncidentStatus.ANALYZING
        
        # Анализ угрозы
        threat_analysis = await self._analyze_threat(incident)
        
        # Анализ воздействия
        impact_analysis = await self._analyze_impact(incident)
        
        # Обновляем инцидент
        incident.impact_assessment = impact_analysis.get("summary", "")
        incident.root_cause = threat_analysis.get("root_cause", "")
    
    async def _analyze_threat(self, incident: Incident) -> Dict[str, Any]:
        """Анализ угрозы"""
        threat_analysis = {
            "threat_type": incident.threat_type.value,
            "severity": incident.severity.value,
            "indicators": incident.indicators,
            "affected_systems": incident.affected_systems,
            "threat_level": "high" if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else "medium",
            "root_cause": "Unknown",
            "attack_vector": "Unknown",
            "confidence": 0.7
        }
        
        # Простая логика анализа на основе типа угрозы
        if incident.threat_type == ThreatType.MALWARE:
            threat_analysis["root_cause"] = "Malicious software detected"
            threat_analysis["attack_vector"] = "File-based infection"
        elif incident.threat_type == ThreatType.PHISHING:
            threat_analysis["root_cause"] = "Social engineering attack"
            threat_analysis["attack_vector"] = "Email-based phishing"
        elif incident.threat_type == ThreatType.DDOS:
            threat_analysis["root_cause"] = "Distributed denial of service"
            threat_analysis["attack_vector"] = "Network flooding"
        
        return threat_analysis
    
    async def _analyze_impact(self, incident: Incident) -> Dict[str, Any]:
        """Анализ воздействия"""
        impact_analysis = {
            "affected_systems_count": len(incident.affected_systems),
            "severity_impact": incident.severity.value,
            "business_impact": "Unknown",
            "data_impact": "Unknown",
            "operational_impact": "Unknown",
            "summary": f"Incident affects {len(incident.affected_systems)} systems"
        }
        
        # Простая логика оценки воздействия
        if incident.severity == IncidentSeverity.CRITICAL:
            impact_analysis["business_impact"] = "High"
            impact_analysis["data_impact"] = "Potential data breach"
            impact_analysis["operational_impact"] = "Service disruption"
        elif incident.severity == IncidentSeverity.HIGH:
            impact_analysis["business_impact"] = "Medium"
            impact_analysis["data_impact"] = "Limited data exposure"
            impact_analysis["operational_impact"] = "Reduced performance"
        else:
            impact_analysis["business_impact"] = "Low"
            impact_analysis["data_impact"] = "Minimal data impact"
            impact_analysis["operational_impact"] = "Minor disruption"
        
        return impact_analysis
    
    async def _analyze_root_cause(self, incident: Incident) -> Dict[str, Any]:
        """Анализ корневой причины"""
        root_cause_analysis = {
            "primary_cause": "Unknown",
            "contributing_factors": [],
            "timeline": [],
            "evidence": incident.indicators,
            "confidence": 0.5
        }
        
        # Простая логика определения корневой причины
        if incident.threat_type == ThreatType.MALWARE:
            root_cause_analysis["primary_cause"] = "Malicious software infection"
            root_cause_analysis["contributing_factors"] = ["Unpatched systems", "Weak endpoint protection"]
        elif incident.threat_type == ThreatType.PHISHING:
            root_cause_analysis["primary_cause"] = "Social engineering attack"
            root_cause_analysis["contributing_factors"] = ["User training gaps", "Email security weaknesses"]
        
        return root_cause_analysis
    
    async def _get_response_recommendations(self, incident: Incident) -> List[Dict[str, Any]]:
        """Получение рекомендаций по реагированию"""
        recommendations = []
        
        # Базовые рекомендации на основе серьезности
        if incident.severity == IncidentSeverity.CRITICAL:
            recommendations.extend([
                {"action": "immediate_isolation", "priority": "high", "description": "Немедленно изолировать затронутые системы"},
                {"action": "executive_notification", "priority": "high", "description": "Уведомить руководство"},
                {"action": "incident_team_activation", "priority": "high", "description": "Активировать команду реагирования на инциденты"}
            ])
        elif incident.severity == IncidentSeverity.HIGH:
            recommendations.extend([
                {"action": "enhanced_monitoring", "priority": "medium", "description": "Усилить мониторинг"},
                {"action": "security_team_notification", "priority": "medium", "description": "Уведомить команду безопасности"}
            ])
        else:
            recommendations.extend([
                {"action": "standard_monitoring", "priority": "low", "description": "Стандартный мониторинг"},
                {"action": "documentation", "priority": "low", "description": "Документировать инцидент"}
            ])
        
        return recommendations
    
    async def _execute_automated_response(self, incident: Incident):
        """Выполнение автоматического реагирования"""
        # Определяем подходящий план реагирования
        suitable_plan = await self._find_suitable_response_plan(incident)
        
        if suitable_plan:
            # Выполняем действия из плана
            for action in suitable_plan.actions:
                await self._execute_response_action(incident, action)
    
    async def _find_suitable_response_plan(self, incident: Incident) -> Optional[ResponsePlan]:
        """Поиск подходящего плана реагирования"""
        for plan in self.response_plans.values():
            if (incident.threat_type in plan.threat_types and 
                incident.severity in plan.severity_levels):
                return plan
        return None
    
    async def _execute_response_action(self, incident: Incident, action: ResponseAction) -> Dict[str, Any]:
        """Выполнение действия реагирования"""
        try:
            if action == ResponseAction.ISOLATE:
                result = await self._isolate_systems(incident.affected_systems)
            elif action == ResponseAction.BLOCK:
                result = await self._block_threats(incident.indicators)
            elif action == ResponseAction.QUARANTINE:
                result = await self._quarantine_affected_systems(incident.affected_systems)
            elif action == ResponseAction.ALERT:
                result = await self._send_alert(incident)
            elif action == ResponseAction.ESCALATE:
                result = await self._escalate_incident(incident)
            elif action == ResponseAction.INVESTIGATE:
                result = await self._investigate_incident(incident)
            elif action == ResponseAction.MONITOR:
                result = await self._monitor_incident(incident)
            elif action == ResponseAction.RESTORE:
                result = await self._restore_systems(incident.affected_systems)
            else:
                result = {"success": False, "message": f"Unknown action: {action.value}"}
            
            return {
                "action": action.value,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка выполнения действия {action.value}: {e}")
            return {
                "action": action.value,
                "success": False,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _isolate_systems(self, systems: List[str]) -> Dict[str, Any]:
        """Изоляция систем"""
        # Симуляция изоляции систем
        await asyncio.sleep(0.1)  # Имитация времени выполнения
        return {
            "success": True,
            "message": f"Systems {systems} isolated successfully",
            "isolated_systems": systems
        }
    
    async def _block_threats(self, indicators: List[str]) -> Dict[str, Any]:
        """Блокировка угроз"""
        # Симуляция блокировки угроз
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Threats {indicators} blocked successfully",
            "blocked_indicators": indicators
        }
    
    async def _quarantine_affected_systems(self, systems: List[str]) -> Dict[str, Any]:
        """Карантин затронутых систем"""
        # Симуляция карантина
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Systems {systems} quarantined successfully",
            "quarantined_systems": systems
        }
    
    async def _send_alert(self, incident: Incident) -> Dict[str, Any]:
        """Отправка алерта"""
        # Симуляция отправки алерта
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Alert sent for incident {incident.incident_id}",
            "alert_recipients": ["security_team", "management"]
        }
    
    async def _escalate_incident(self, incident: Incident) -> Dict[str, Any]:
        """Эскалация инцидента"""
        # Симуляция эскалации
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Incident {incident.incident_id} escalated",
            "escalation_level": "management"
        }
    
    async def _investigate_incident(self, incident: Incident) -> Dict[str, Any]:
        """Расследование инцидента"""
        # Симуляция расследования
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Investigation started for incident {incident.incident_id}",
            "investigation_team": "security_analysts"
        }
    
    async def _monitor_incident(self, incident: Incident) -> Dict[str, Any]:
        """Мониторинг инцидента"""
        # Симуляция мониторинга
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Monitoring activated for incident {incident.incident_id}",
            "monitoring_duration": "24 hours"
        }
    
    async def _restore_systems(self, systems: List[str]) -> Dict[str, Any]:
        """Восстановление систем"""
        # Симуляция восстановления
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "message": f"Systems {systems} restored successfully",
            "restored_systems": systems
        }
    
    def _determine_escalation_level(self, incident: Incident) -> str:
        """Определение уровня эскалации"""
        if incident.severity == IncidentSeverity.CRITICAL:
            return "executive"
        elif incident.severity == IncidentSeverity.HIGH:
            return "management"
        elif incident.severity == IncidentSeverity.MEDIUM:
            return "team_lead"
        else:
            return "team"
    
    async def _perform_escalation(self, incident: Incident, escalation_level: str, reason: str) -> Dict[str, Any]:
        """Выполнение эскалации"""
        # Симуляция эскалации
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "escalation_level": escalation_level,
            "reason": reason,
            "escalated_to": f"{escalation_level}_team"
        }
    
    async def _generate_resolution_report(self, incident: Incident) -> Dict[str, Any]:
        """Генерация отчета о разрешении"""
        return {
            "incident_id": incident.incident_id,
            "resolution_time": incident.actual_resolution.isoformat() if incident.actual_resolution else None,
            "response_actions_taken": [action.value for action in incident.response_actions],
            "systems_affected": incident.affected_systems,
            "threat_contained": True,
            "lessons_learned": incident.lessons_learned
        }
    
    async def _generate_incident_timeline(self, incident: Incident) -> List[Dict[str, Any]]:
        """Генерация временной шкалы инцидента"""
        timeline = [
            {
                "timestamp": incident.detected_at.isoformat(),
                "event": "Incident detected",
                "description": incident.description
            }
        ]
        
        # Добавляем события реагирования
        for i, action in enumerate(incident.response_actions):
            timeline.append({
                "timestamp": (incident.detected_at + timedelta(minutes=i*5)).isoformat(),
                "event": f"Response action: {action.value}",
                "description": f"Executed {action.value} response"
            })
        
        # Добавляем разрешение
        if incident.actual_resolution:
            timeline.append({
                "timestamp": incident.actual_resolution.isoformat(),
                "event": "Incident resolved",
                "description": "Incident successfully resolved"
            })
        
        return timeline
    
    async def _generate_recommendations(self, incident: Incident) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Рекомендации на основе типа угрозы
        if incident.threat_type == ThreatType.MALWARE:
            recommendations.extend([
                "Обновить антивирусные сигнатуры",
                "Провести сканирование всех систем",
                "Усилить мониторинг файловых операций"
            ])
        elif incident.threat_type == ThreatType.PHISHING:
            recommendations.extend([
                "Провести обучение пользователей",
                "Усилить фильтрацию электронной почты",
                "Внедрить двухфакторную аутентификацию"
            ])
        elif incident.threat_type == ThreatType.DDOS:
            recommendations.extend([
                "Настроить DDoS защиту",
                "Усилить мониторинг сетевого трафика",
                "Подготовить план масштабирования"
            ])
        
        # Общие рекомендации
        recommendations.extend([
            "Регулярно обновлять системы безопасности",
            "Проводить тестирование планов реагирования",
            "Улучшать мониторинг и обнаружение угроз"
        ])
        
        return recommendations

class IncidentResponseManager:
    """
    Менеджер системы реагирования на инциденты
    """
    
    def __init__(self):
        self.response_system = IncidentResponseSystem()
        self.is_initialized = False
        self.logger = logging.getLogger(f"{__name__}.IncidentResponseManager")
    
    async def initialize(self):
        """Инициализация менеджера"""
        try:
            self.is_initialized = await self.response_system.initialize()
            if self.is_initialized:
                self.logger.info("Менеджер реагирования на инциденты инициализирован")
            return self.is_initialized
        except Exception as e:
            self.logger.error(f"Ошибка инициализации менеджера реагирования: {e}")
            return False
    
    async def create_incident(self, title: str, description: str, severity: IncidentSeverity, threat_type: ThreatType, affected_systems: List[str], indicators: List[str]) -> str:
        """Создание нового инцидента"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.response_system.detect_incident(title, description, severity, threat_type, affected_systems, indicators)
    
    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Получение инцидента"""
        return self.response_system.incidents.get(incident_id)
    
    async def get_all_incidents(self, status_filter: Optional[IncidentStatus] = None, severity_filter: Optional[IncidentSeverity] = None) -> List[Dict[str, Any]]:
        """Получение всех инцидентов"""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.response_system.get_all_incidents(status_filter, severity_filter)
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья системы"""
        try:
            return {
                "status": "healthy" if self.is_initialized else "not_initialized",
                "incidents_count": len(self.response_system.incidents),
                "response_plans_count": len(self.response_system.response_plans),
                "active_incidents": len([i for i in self.response_system.incidents.values() if i.status != IncidentStatus.CLOSED]),
                "last_activity": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка health check: {e}")
            return {"status": "error", "error": str(e)}

# Экспорт основных классов
__all__ = [
    'IncidentResponseSystem',
    'IncidentResponseManager',
    'Incident',
    'ResponsePlan',
    'IncidentSeverity',
    'IncidentStatus',
    'ResponseAction',
    'ThreatType'
]