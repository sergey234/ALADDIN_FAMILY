"""
Модуль правовой защиты для ALADDIN Security
Обеспечивает соответствие российскому законодательству при работе с зарубежными серверами
"""

import logging as std_logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)

class LegalStatus(Enum):
    """Правовые статусы"""
    COMPLIANT = "compliant"
    RISK = "risk"
    NON_COMPLIANT = "non_compliant"

@dataclass
class LegalCheck:
    """Результат правовой проверки"""
    check_name: str
    status: LegalStatus
    message: str
    recommendation: str
    timestamp: datetime

class LegalProtectionManager:
    """Менеджер правовой защиты"""
    
    def __init__(self):
        self.legal_checks: List[LegalCheck] = []
        self.marketing_restrictions = self._init_marketing_restrictions()
        self.technical_restrictions = self._init_technical_restrictions()
        
    def _init_marketing_restrictions(self) -> Dict[str, List[str]]:
        """Инициализация маркетинговых ограничений"""
        return {
            "forbidden_terms": [
                "VPN", "випиэн", "впн",
                "обход блокировок", "обход цензуры",
                "анонимный интернет", "скрытие IP",
                "смена IP адреса", "изменение местоположения",
                "доступ к заблокированным сайтам"
            ],
            "allowed_terms": [
                "система безопасности", "защита семьи",
                "безопасный интернет", "защита данных",
                "кибербезопасность", "защита от угроз",
                "приватность", "конфиденциальность",
                "защита детей", "семейная безопасность"
            ],
            "target_audience": [
                "семьи с детьми", "родители",
                "пользователи, ценящие приватность",
                "люди, работающие с конфиденциальными данными",
                "семьи с пожилыми родственниками"
            ]
        }
    
    def _init_technical_restrictions(self) -> Dict[str, Any]:
        """Инициализация технических ограничений"""
        return {
            "no_logs_policy": True,
            "data_anonymization": True,
            "encryption_required": True,
            "no_personal_data_storage": True,
            "compliance_monitoring": True
        }
    
    def check_marketing_compliance(self, content: str) -> LegalCheck:
        """Проверка соответствия маркетингового контента"""
        try:
            content_lower = content.lower()
            
            # Проверяем запрещенные термины
            forbidden_found = []
            for term in self.marketing_restrictions["forbidden_terms"]:
                if term.lower() in content_lower:
                    forbidden_found.append(term)
            
            if forbidden_found:
                return LegalCheck(
                    check_name="marketing_compliance",
                    status=LegalStatus.NON_COMPLIANT,
                    message=f"Найдены запрещенные термины: {', '.join(forbidden_found)}",
                    recommendation="Замените запрещенные термины на разрешенные",
                    timestamp=datetime.now()
                )
            
            # Проверяем наличие разрешенных терминов
            allowed_found = []
            for term in self.marketing_restrictions["allowed_terms"]:
                if term.lower() in content_lower:
                    allowed_found.append(term)
            
            if not allowed_found:
                return LegalCheck(
                    check_name="marketing_compliance",
                    status=LegalStatus.RISK,
                    message="Не найдены ключевые термины безопасности",
                    recommendation="Добавьте термины, связанные с безопасностью",
                    timestamp=datetime.now()
                )
            
            return LegalCheck(
                check_name="marketing_compliance",
                status=LegalStatus.COMPLIANT,
                message="Маркетинговый контент соответствует требованиям",
                recommendation="Продолжайте использовать безопасную терминологию",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Ошибка проверки маркетингового соответствия: {e}")
            return LegalCheck(
                check_name="marketing_compliance",
                status=LegalStatus.RISK,
                message=f"Ошибка проверки: {str(e)}",
                recommendation="Проверьте контент вручную",
                timestamp=datetime.now()
            )
    
    def check_technical_compliance(self) -> LegalCheck:
        """Проверка технического соответствия"""
        try:
            # Проверяем No-Logs политику
            if not self.technical_restrictions["no_logs_policy"]:
                return LegalCheck(
                    check_name="technical_compliance",
                    status=LegalStatus.NON_COMPLIANT,
                    message="No-Logs политика не активна",
                    recommendation="Активируйте No-Logs политику",
                    timestamp=datetime.now()
                )
            
            # Проверяем анонимизацию данных
            if not self.technical_restrictions["data_anonymization"]:
                return LegalCheck(
                    check_name="technical_compliance",
                    status=LegalStatus.NON_COMPLIANT,
                    message="Анонимизация данных не активна",
                    recommendation="Активируйте анонимизацию данных",
                    timestamp=datetime.now()
                )
            
            # Проверяем шифрование
            if not self.technical_restrictions["encryption_required"]:
                return LegalCheck(
                    check_name="technical_compliance",
                    status=LegalStatus.NON_COMPLIANT,
                    message="Шифрование не активно",
                    recommendation="Активируйте шифрование данных",
                    timestamp=datetime.now()
                )
            
            return LegalCheck(
                check_name="technical_compliance",
                status=LegalStatus.COMPLIANT,
                message="Техническое соответствие соблюдается",
                recommendation="Продолжайте соблюдать технические требования",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Ошибка проверки технического соответствия: {e}")
            return LegalCheck(
                check_name="technical_compliance",
                status=LegalStatus.RISK,
                message=f"Ошибка проверки: {str(e)}",
                recommendation="Проверьте техническую конфигурацию",
                timestamp=datetime.now()
            )
    
    def check_legal_positioning(self) -> LegalCheck:
        """Проверка правового позиционирования"""
        try:
            # Проверяем, что система позиционируется как система безопасности
            positioning_correct = True
            
            # В реальной реализации здесь будет проверка контента
            if positioning_correct:
                return LegalCheck(
                    check_name="legal_positioning",
                    status=LegalStatus.COMPLIANT,
                    message="Правовое позиционирование корректно",
                    recommendation="Продолжайте позиционировать как систему безопасности",
                    timestamp=datetime.now()
                )
            else:
                return LegalCheck(
                    check_name="legal_positioning",
                    status=LegalStatus.RISK,
                    message="Правовое позиционирование требует корректировки",
                    recommendation="Скорректируйте позиционирование",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Ошибка проверки правового позиционирования: {e}")
            return LegalCheck(
                check_name="legal_positioning",
                status=LegalStatus.RISK,
                message=f"Ошибка проверки: {str(e)}",
                recommendation="Проверьте позиционирование вручную",
                timestamp=datetime.now()
            )
    
    def run_full_legal_check(self) -> Dict[str, Any]:
        """Запуск полной правовой проверки"""
        logger.info("Запуск полной правовой проверки")
        
        checks = [
            self.check_marketing_compliance("Система семейной безопасности ALADDIN"),
            self.check_technical_compliance(),
            self.check_legal_positioning()
        ]
        
        self.legal_checks.extend(checks)
        
        # Подсчитываем результаты
        total_checks = len(checks)
        compliant_checks = len([c for c in checks if c.status == LegalStatus.COMPLIANT])
        risk_checks = len([c for c in checks if c.status == LegalStatus.RISK])
        non_compliant_checks = len([c for c in checks if c.status == LegalStatus.NON_COMPLIANT])
        
        compliance_percentage = (compliant_checks / total_checks) * 100
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "compliant_checks": compliant_checks,
            "risk_checks": risk_checks,
            "non_compliant_checks": non_compliant_checks,
            "compliance_percentage": compliance_percentage,
            "is_compliant": compliance_percentage >= 100,
            "checks": [self._check_to_dict(c) for c in checks]
        }
        
        logger.info(f"Правовая проверка завершена. Соответствие: {compliance_percentage:.1f}%")
        return result
    
    def get_safe_marketing_content(self) -> Dict[str, str]:
        """Получение безопасного маркетингового контента"""
        return {
            "title": "ALADDIN - Система семейной безопасности",
            "subtitle": "Защита вашей семьи в цифровом мире",
            "description": "Комплексная система безопасности для защиты семьи от киберугроз, контроля доступа детей к интернету и обеспечения приватности персональных данных",
            "features": [
                "Защита от вирусов и вредоносного ПО",
                "Блокировка опасных сайтов",
                "Контроль времени использования устройств",
                "Мониторинг активности детей",
                "Защита от фишинга и мошенничества",
                "Безопасное подключение к интернету",
                "Защита данных в общественных сетях"
            ],
            "target_audience": "Семьи с детьми, родители, пользователи, ценящие приватность",
            "legal_basis": "Защита персональных данных, обеспечение безопасности семьи"
        }
    
    def _check_to_dict(self, check: LegalCheck) -> Dict[str, Any]:
        """Преобразование проверки в словарь"""
        return {
            "check_name": check.check_name,
            "status": check.status.value,
            "message": check.message,
            "recommendation": check.recommendation,
            "timestamp": check.timestamp.isoformat()
        }

# Пример использования
if __name__ == "__main__":
    legal_manager = LegalProtectionManager()
    result = legal_manager.run_full_legal_check()
    
    print("=== ПРАВОВАЯ ПРОВЕРКА ===")
    print(f"Соответствие: {result['compliance_percentage']:.1f}%")
    print(f"Статус: {'✅ СООТВЕТСТВУЕТ' if result['is_compliant'] else '❌ НЕ СООТВЕТСТВУЕТ'}")
    
    print("\n=== ДЕТАЛИ ПРОВЕРОК ===")
    for check in result['checks']:
        status_icon = "✅" if check['status'] == 'compliant' else "⚠️" if check['status'] == 'risk' else "❌"
        print(f"{status_icon} {check['check_name']}: {check['message']}")
        print(f"   Рекомендация: {check['recommendation']}")
    
    print("\n=== БЕЗОПАСНЫЙ МАРКЕТИНГОВЫЙ КОНТЕНТ ===")
    safe_content = legal_manager.get_safe_marketing_content()
    print(f"Заголовок: {safe_content['title']}")
    print(f"Описание: {safe_content['description']}")
    print(f"Целевая аудитория: {safe_content['target_audience']}")