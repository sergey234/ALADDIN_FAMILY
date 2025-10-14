#!/usr/bin/env python3
"""
Комплексный тест работоспособности BusinessAnalytics
"""
import sys
import os
import asyncio
sys.path.append('.')

async def test_business_analytics():
    try:
        from analytics.business_analytics import BusinessAnalytics
        print("✅ Импорт модуля успешен")
        
        # Создаем экземпляр системы
        ba = BusinessAnalytics("TestAnalytics")
        print("✅ Создание экземпляра успешно")
        
        # Тестируем основные методы
        print(f"✅ Имя системы: {ba.name}")
        
        # Тест расчета бизнес-метрик (асинхронный)
        metrics = await ba.calculate_business_metrics()
        print(f"✅ Расчет бизнес-метрик: {type(metrics).__name__}")
        
        # Тест получения сводки метрик (синхронный)
        summary = ba.get_metrics_summary()
        print(f"✅ Получение сводки метрик: {type(summary).__name__}")
        
        # Тест анализа когорт (асинхронный)
        cohort_analysis = await ba.get_cohort_analysis()
        print(f"✅ Анализ когорт: {type(cohort_analysis).__name__}")
        
        # Тест прогноза выручки (асинхронный)
        revenue_forecast = await ba.get_revenue_forecast()
        print(f"✅ Прогноз выручки: {type(revenue_forecast).__name__}")
        
        # Тест ROI анализа (асинхронный)
        roi_analysis = await ba.get_roi_analysis()
        print(f"✅ ROI анализ: {type(roi_analysis).__name__}")
        
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_business_analytics())
