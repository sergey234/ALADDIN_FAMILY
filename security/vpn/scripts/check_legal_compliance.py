#!/usr/bin/env python3
"""
Скрипт проверки правового соответствия документов ALADDIN
Автоматически проверяет использование запрещенных терминов в документации
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class LegalComplianceChecker:
    """Проверяльщик правового соответствия документов"""
    
    def __init__(self):
        self.forbidden_terms = [
            "VPN сервис", "VPN-сервис", "VPN сервис",
            "обход блокировок", "обход цензуры",
            "анонимный интернет", "анонимность в сети",
            "смена IP адреса", "изменение IP",
            "изменение местоположения", "смена геолокации",
            "доступ к заблокированным сайтам",
            "приватный интернет", "приватность в сети",
            "скрытие IP", "маскировка IP",
            "анонимный браузинг",
            "обход DPI", "обход фильтрации"
        ]
        
        self.allowed_terms = [
            "система семейной безопасности",
            "защита персональных данных",
            "безопасный интернет для семьи",
            "защита от киберугроз",
            "кибербезопасность для семьи",
            "защита детей в интернете",
            "контроль доступа к интернету",
            "безопасное подключение к интернету",
            "защита данных в общественных сетях",
            "приватность и конфиденциальность",
            "защита от вирусов и вредоносного ПО",
            "блокировка опасных сайтов",
            "мониторинг активности детей",
            "контроль времени использования устройств"
        ]
        
        self.documents_to_check = [
            "docs/legal/privacy_policy_vpn.md",
            "docs/legal/consent_form_vpn.md", 
            "docs/legal/technical_description_vpn.md",
            "docs/legal/152_fz_compliance_vpn.md",
            "docs/legal/marketing_guidelines.md"
        ]
    
    def check_document(self, file_path: str) -> Dict[str, any]:
        """Проверка одного документа"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем запрещенные термины
            forbidden_found = []
            for term in self.forbidden_terms:
                if re.search(term, content, re.IGNORECASE):
                    # Исключение для marketing_guidelines.md - там запрещенные термины указаны как примеры
                    if "marketing_guidelines" in file_path and "НЕ ИСПОЛЬЗУЕМ" in content:
                        # Проверяем, что термин находится в разделе запрещенных терминов
                        lines = content.split('\n')
                        in_forbidden_section = False
                        for line in lines:
                            if "НЕ ИСПОЛЬЗУЕМ" in line:
                                in_forbidden_section = True
                            elif "ИСПОЛЬЗУЕМ:" in line or "ВНИМАНИЕ:" in line:
                                in_forbidden_section = False
                            elif in_forbidden_section and term.lower() in line.lower():
                                # Термин найден в разделе запрещенных - это нормально
                                break
                        else:
                            # Термин не найден в разделе запрещенных - это ошибка
                            forbidden_found.append(term)
                    else:
                        forbidden_found.append(term)
            
            # Проверяем разрешенные термины
            allowed_found = []
            for term in self.allowed_terms:
                if re.search(term, content, re.IGNORECASE):
                    allowed_found.append(term)
            
            # Определяем статус
            if forbidden_found:
                status = "NON_COMPLIANT"
            elif not allowed_found:
                status = "RISK"
            else:
                status = "COMPLIANT"
            
            return {
                "file": file_path,
                "status": status,
                "forbidden_found": forbidden_found,
                "allowed_found": allowed_found,
                "total_forbidden": len(forbidden_found),
                "total_allowed": len(allowed_found)
            }
            
        except Exception as e:
            return {
                "file": file_path,
                "status": "ERROR",
                "error": str(e),
                "forbidden_found": [],
                "allowed_found": [],
                "total_forbidden": 0,
                "total_allowed": 0
            }
    
    def check_all_documents(self) -> Dict[str, any]:
        """Проверка всех документов"""
        results = []
        
        for doc_path in self.documents_to_check:
            if os.path.exists(doc_path):
                result = self.check_document(doc_path)
                results.append(result)
            else:
                results.append({
                    "file": doc_path,
                    "status": "NOT_FOUND",
                    "error": "Файл не найден",
                    "forbidden_found": [],
                    "allowed_found": [],
                    "total_forbidden": 0,
                    "total_allowed": 0
                })
        
        # Подсчитываем общую статистику
        total_docs = len(results)
        compliant_docs = len([r for r in results if r["status"] == "COMPLIANT"])
        risk_docs = len([r for r in results if r["status"] == "RISK"])
        non_compliant_docs = len([r for r in results if r["status"] == "NON_COMPLIANT"])
        error_docs = len([r for r in results if r["status"] in ["ERROR", "NOT_FOUND"]])
        
        compliance_percentage = (compliant_docs / total_docs) * 100 if total_docs > 0 else 0
        
        return {
            "total_documents": total_docs,
            "compliant_documents": compliant_docs,
            "risk_documents": risk_docs,
            "non_compliant_documents": non_compliant_docs,
            "error_documents": error_docs,
            "compliance_percentage": compliance_percentage,
            "is_compliant": compliance_percentage >= 100,
            "results": results
        }
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """Генерация отчета о проверке"""
        report = []
        report.append("=" * 80)
        report.append("ОТЧЕТ О ПРОВЕРКЕ ПРАВОВОГО СООТВЕТСТВИЯ ДОКУМЕНТОВ ALADDIN")
        report.append("=" * 80)
        report.append("")
        
        # Общая статистика
        report.append(f"📊 ОБЩАЯ СТАТИСТИКА:")
        report.append(f"   Всего документов: {results['total_documents']}")
        report.append(f"   Соответствует: {results['compliant_documents']}")
        report.append(f"   Риск: {results['risk_documents']}")
        report.append(f"   Не соответствует: {results['non_compliant_documents']}")
        report.append(f"   Ошибки: {results['error_documents']}")
        report.append(f"   Процент соответствия: {results['compliance_percentage']:.1f}%")
        report.append("")
        
        # Статус
        if results['is_compliant']:
            report.append("✅ СТАТУС: ВСЕ ДОКУМЕНТЫ СООТВЕТСТВУЮТ ПРАВОВЫМ ТРЕБОВАНИЯМ")
        else:
            report.append("❌ СТАТУС: ТРЕБУЕТСЯ ДОРАБОТКА ДОКУМЕНТОВ")
        report.append("")
        
        # Детали по каждому документу
        report.append("📋 ДЕТАЛИ ПО ДОКУМЕНТАМ:")
        report.append("")
        
        for result in results['results']:
            status_icon = "✅" if result['status'] == 'COMPLIANT' else "⚠️" if result['status'] == 'RISK' else "❌"
            report.append(f"{status_icon} {result['file']}")
            
            if result['status'] == 'COMPLIANT':
                report.append(f"   Статус: Соответствует")
                report.append(f"   Разрешенных терминов: {result['total_allowed']}")
            elif result['status'] == 'RISK':
                report.append(f"   Статус: Риск (мало разрешенных терминов)")
                report.append(f"   Разрешенных терминов: {result['total_allowed']}")
            elif result['status'] == 'NON_COMPLIANT':
                report.append(f"   Статус: Не соответствует")
                report.append(f"   Запрещенных терминов: {result['total_forbidden']}")
                if result['forbidden_found']:
                    report.append(f"   Найденные запрещенные термины:")
                    for term in result['forbidden_found']:
                        report.append(f"     - {term}")
            elif result['status'] in ['ERROR', 'NOT_FOUND']:
                report.append(f"   Статус: Ошибка")
                report.append(f"   Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
            report.append("")
        
        # Рекомендации
        report.append("💡 РЕКОМЕНДАЦИИ:")
        if results['non_compliant_documents'] > 0:
            report.append("   • Удалите все запрещенные термины из документов")
            report.append("   • Замените их на разрешенные термины безопасности")
        if results['risk_documents'] > 0:
            report.append("   • Добавьте больше терминов, связанных с безопасностью")
            report.append("   • Усильте позиционирование как системы безопасности")
        if results['error_documents'] > 0:
            report.append("   • Исправьте ошибки в документах")
            report.append("   • Убедитесь, что все файлы существуют")
        
        if results['is_compliant']:
            report.append("   • Продолжайте соблюдать правовые требования")
            report.append("   • Регулярно проверяйте соответствие документов")
        
        return "\n".join(report)

def main():
    """Основная функция"""
    print("🔍 ЗАПУСК ПРОВЕРКИ ПРАВОВОГО СООТВЕТСТВИЯ ДОКУМЕНТОВ")
    print("=" * 60)
    
    checker = LegalComplianceChecker()
    results = checker.check_all_documents()
    report = checker.generate_report(results)
    
    print(report)
    
    # Сохраняем отчет в файл
    with open("legal_compliance_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 Отчет сохранен в файл: legal_compliance_report.txt")
    
    # Возвращаем код выхода
    return 0 if results['is_compliant'] else 1

if __name__ == "__main__":
    sys.exit(main())