#!/usr/bin/env python3
"""
Система отчётов о проблемах реестра функций ALADDIN
Анализирует логи и создаёт детальные отчёты
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/registry_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RegistryProblemReporter:
    """Система создания отчётов о проблемах реестра"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.reports_dir = Path("reports/registry")
        
        # Создаём необходимые директории
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Пути к логам
        self.protection_log = self.logs_dir / "registry_protection.log"
        self.validation_log = self.logs_dir / "registry_validation.log"
        self.monitor_log = self.logs_dir / "registry_monitor.log"
        self.alert_log = self.logs_dir / "registry_alerts.log"
        
        logger.info("📋 Система отчётов о проблемах инициализирована")
    
    def _read_log_file(self, log_path: Path) -> List[Dict[str, Any]]:
        """Чтение лог-файла"""
        try:
            if not log_path.exists():
                return []
            
            entries = []
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Пытаемся парсить как JSON
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        # Если не JSON, создаём текстовую запись
                        entries.append({
                            "timestamp": datetime.now().isoformat(),
                            "message": line,
                            "type": "text_log"
                        })
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Ошибка чтения лога {log_path}: {e}")
            return []
    
    def _analyze_protection_log(self) -> Dict[str, Any]:
        """Анализ лога защиты реестра"""
        entries = self._read_log_file(self.protection_log)
        
        analysis = {
            "total_entries": len(entries),
            "registry_updates": 0,
            "functions_deleted": 0,
            "functions_added": 0,
            "backups_created": 0,
            "protection_violations": 0,
            "recent_activities": []
        }
        
        for entry in entries:
            if entry.get("action") == "registry_update":
                analysis["registry_updates"] += 1
                
                changes = entry.get("changes", {})
                analysis["functions_deleted"] += changes.get("deleted_count", 0)
                analysis["functions_added"] += changes.get("added_count", 0)
                
                if changes.get("deleted_count", 0) > 0:
                    analysis["protection_violations"] += 1
                
                # Добавляем в недавние активности
                analysis["recent_activities"].append({
                    "timestamp": entry.get("timestamp"),
                    "action": "registry_update",
                    "deleted": changes.get("deleted_count", 0),
                    "added": changes.get("added_count", 0)
                })
        
        return analysis
    
    def _analyze_validation_log(self) -> Dict[str, Any]:
        """Анализ лога валидации"""
        entries = self._read_log_file(self.validation_log)
        
        analysis = {
            "total_validations": len(entries),
            "successful_validations": 0,
            "failed_validations": 0,
            "total_errors": 0,
            "common_errors": Counter(),
            "validation_trends": []
        }
        
        for entry in entries:
            if entry.get("action") == "format_validation":
                errors_count = entry.get("errors_count", 0)
                analysis["total_errors"] += errors_count
                
                if errors_count == 0:
                    analysis["successful_validations"] += 1
                else:
                    analysis["failed_validations"] += 1
                
                # Анализ ошибок
                for error in entry.get("errors", []):
                    analysis["common_errors"][error] += 1
                
                # Тренды валидации
                analysis["validation_trends"].append({
                    "timestamp": entry.get("timestamp"),
                    "errors_count": errors_count,
                    "functions_count": entry.get("functions_count", 0)
                })
        
        return analysis
    
    def _analyze_monitor_log(self) -> Dict[str, Any]:
        """Анализ лога мониторинга"""
        entries = self._read_log_file(self.monitor_log)
        
        analysis = {
            "total_events": len(entries),
            "file_changes": 0,
            "function_count_changes": 0,
            "size_changes": 0,
            "monitoring_uptime": 0,
            "recent_events": []
        }
        
        for entry in entries:
            changes = entry.get("changes", [])
            analysis["file_changes"] += len([c for c in changes if c.get("type") in ["file_created", "file_deleted"]])
            analysis["function_count_changes"] += len([c for c in changes if c.get("type") in ["functions_added", "functions_removed"]])
            analysis["size_changes"] += len([c for c in changes if c.get("type") == "size_changed"])
            
            # Недавние события
            if changes:
                analysis["recent_events"].append({
                    "timestamp": entry.get("timestamp"),
                    "changes": changes,
                    "functions_count": entry.get("current_functions_count", 0)
                })
        
        return analysis
    
    def _analyze_alert_log(self) -> Dict[str, Any]:
        """Анализ лога предупреждений"""
        entries = self._read_log_file(self.alert_log)
        
        analysis = {
            "total_alerts": len(entries),
            "critical_alerts": 0,
            "warning_alerts": 0,
            "info_alerts": 0,
            "alert_types": Counter(),
            "alert_timeline": []
        }
        
        for entry in entries:
            severity = entry.get("severity", "unknown")
            alert_type = entry.get("type", "unknown")
            
            analysis["alert_types"][alert_type] += 1
            
            if severity == "critical":
                analysis["critical_alerts"] += 1
            elif severity == "warning":
                analysis["warning_alerts"] += 1
            elif severity == "info":
                analysis["info_alerts"] += 1
            
            analysis["alert_timeline"].append({
                "timestamp": entry.get("timestamp"),
                "type": alert_type,
                "severity": severity,
                "message": entry.get("message", "")
            })
        
        return analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Генерация комплексного отчёта"""
        logger.info("📊 Генерация комплексного отчёта о проблемах реестра")
        
        # Анализ всех логов
        protection_analysis = self._analyze_protection_log()
        validation_analysis = self._analyze_validation_log()
        monitor_analysis = self._analyze_monitor_log()
        alert_analysis = self._analyze_alert_log()
        
        # Общая статистика
        total_problems = (
            protection_analysis["protection_violations"] +
            validation_analysis["failed_validations"] +
            alert_analysis["critical_alerts"]
        )
        
        # Оценка здоровья системы
        health_score = self._calculate_health_score(
            protection_analysis,
            validation_analysis,
            monitor_analysis,
            alert_analysis
        )
        
        # Рекомендации
        recommendations = self._generate_recommendations(
            protection_analysis,
            validation_analysis,
            monitor_analysis,
            alert_analysis
        )
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_registry_analysis",
                "analysis_period": "all_time"
            },
            "system_health": {
                "health_score": health_score,
                "total_problems": total_problems,
                "status": self._get_health_status(health_score)
            },
            "protection_analysis": protection_analysis,
            "validation_analysis": validation_analysis,
            "monitoring_analysis": monitor_analysis,
            "alert_analysis": alert_analysis,
            "recommendations": recommendations,
            "summary": self._generate_summary(
                protection_analysis,
                validation_analysis,
                monitor_analysis,
                alert_analysis,
                health_score
            )
        }
        
        return report
    
    def _calculate_health_score(self, protection: Dict, validation: Dict, monitor: Dict, alerts: Dict) -> int:
        """Расчёт оценки здоровья системы (0-100)"""
        score = 100
        
        # Штрафы за проблемы
        score -= protection["protection_violations"] * 10  # -10 за каждое нарушение защиты
        score -= validation["failed_validations"] * 5      # -5 за каждую неудачную валидацию
        score -= alerts["critical_alerts"] * 15            # -15 за каждое критическое предупреждение
        score -= alerts["warning_alerts"] * 3              # -3 за каждое предупреждение
        
        # Бонусы за хорошую работу
        if protection["registry_updates"] > 0:
            score += min(10, protection["registry_updates"])  # +1 за каждое обновление (макс +10)
        
        if validation["successful_validations"] > validation["failed_validations"]:
            score += 5  # +5 если успешных валидаций больше
        
        return max(0, min(100, score))
    
    def _get_health_status(self, score: int) -> str:
        """Получение статуса здоровья системы"""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        elif score >= 30:
            return "poor"
        else:
            return "critical"
    
    def _generate_recommendations(self, protection: Dict, validation: Dict, monitor: Dict, alerts: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        
        # Рекомендации по защите
        if protection["protection_violations"] > 0:
            recommendations.append("🚨 Критично: Обнаружены нарушения защиты реестра. Проверьте логи и настройте более строгие правила.")
        
        if protection["functions_deleted"] > 0:
            recommendations.append("⚠️ Внимание: Удалены функции из реестра. Убедитесь, что это было намеренно.")
        
        # Рекомендации по валидации
        if validation["failed_validations"] > validation["successful_validations"]:
            recommendations.append("🔧 Рекомендация: Много неудачных валидаций. Проверьте формат данных в реестре.")
        
        if validation["common_errors"]:
            most_common_error = validation["common_errors"].most_common(1)[0]
            recommendations.append(f"🔍 Частая ошибка: '{most_common_error[0]}' встречается {most_common_error[1]} раз. Исправьте формат данных.")
        
        # Рекомендации по мониторингу
        if alerts["critical_alerts"] > 0:
            recommendations.append("🚨 Критично: Обнаружены критические предупреждения. Немедленно проверьте систему.")
        
        if alerts["warning_alerts"] > 5:
            recommendations.append("⚠️ Внимание: Много предупреждений. Рассмотрите настройку фильтров мониторинга.")
        
        # Общие рекомендации
        if not recommendations:
            recommendations.append("✅ Система работает стабильно. Продолжайте мониторинг.")
        
        return recommendations
    
    def _generate_summary(self, protection: Dict, validation: Dict, monitor: Dict, alerts: Dict, health_score: int) -> str:
        """Генерация краткого резюме"""
        total_functions = protection.get("functions_added", 0) - protection.get("functions_deleted", 0)
        
        summary_parts = [
            f"Система реестра функций работает с оценкой {health_score}/100.",
            f"Всего обновлений реестра: {protection['registry_updates']}",
            f"Валидаций выполнено: {validation['total_validations']}",
            f"Предупреждений получено: {alerts['total_alerts']}"
        ]
        
        if protection["functions_deleted"] > 0:
            summary_parts.append(f"⚠️ Удалено функций: {protection['functions_deleted']}")
        
        if alerts["critical_alerts"] > 0:
            summary_parts.append(f"🚨 Критических предупреждений: {alerts['critical_alerts']}")
        
        return " ".join(summary_parts)
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Сохранение отчёта в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"registry_problems_report_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Отчёт сохранён: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения отчёта: {e}")
            return ""
    
    def generate_and_save_report(self) -> str:
        """Генерация и сохранение отчёта"""
        report = self.generate_comprehensive_report()
        return self.save_report(report)

def main():
    """Тестирование системы отчётов"""
    print("📋 ТЕСТИРОВАНИЕ СИСТЕМЫ ОТЧЁТОВ О ПРОБЛЕМАХ")
    print("=" * 50)
    
    # Инициализация системы отчётов
    reporter = RegistryProblemReporter()
    
    # Генерация отчёта
    report_path = reporter.generate_and_save_report()
    
    if report_path:
        print(f"✅ Отчёт сгенерирован: {report_path}")
        
        # Показываем краткую сводку
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"\n📊 Краткая сводка:")
        print(f"   • Оценка здоровья: {report['system_health']['health_score']}/100")
        print(f"   • Статус: {report['system_health']['status']}")
        print(f"   • Всего проблем: {report['system_health']['total_problems']}")
        
        print(f"\n🔍 Рекомендации:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📄 Полный отчёт: {report_path}")
    else:
        print("❌ Ошибка генерации отчёта")

if __name__ == "__main__":
    main()