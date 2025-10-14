# -*- coding: utf-8 -*-
"""
Улучшения для добавления async/await поддержки
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class AsyncIntrusionPreventionService:
    """Асинхронная версия сервиса предотвращения вторжений"""
    
    async def detect_intrusion_async(
        self, 
        event_data: Dict[str, Any], 
        user_id: Optional[str] = None, 
        user_age: Optional[int] = None
    ) -> List[Any]:
        """
        Асинхронное обнаружение попыток вторжения.
        
        Args:
            event_data: Данные события для анализа
            user_id: ID пользователя (опционально)
            user_age: Возраст пользователя (опционально)
            
        Returns:
            List[Any]: Список обнаруженных вторжений
            
        Example:
            >>> service = AsyncIntrusionPreventionService()
            >>> event = {'source_ip': '192.168.1.100', 'failed_logins': 5}
            >>> detections = await service.detect_intrusion_async(event, 'user123', 25)
        """
        # Асинхронная обработка для больших объемов данных
        await asyncio.sleep(0.001)  # Имитация асинхронной работы
        
        # Параллельная обработка паттернов
        tasks = []
        for pattern in self.intrusion_patterns.values():
            task = asyncio.create_task(
                self._check_pattern_async(event_data, pattern, user_id, user_age)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Фильтруем успешные результаты
        detections = [r for r in results if not isinstance(r, Exception)]
        return detections
    
    async def _check_pattern_async(
        self, 
        event_data: Dict[str, Any], 
        pattern: Any, 
        user_id: Optional[str], 
        user_age: Optional[int]
    ) -> Optional[Any]:
        """Асинхронная проверка паттерна"""
        try:
            # Асинхронная проверка индикаторов
            confidence = await self._calculate_confidence_async(event_data, pattern)
            if confidence >= pattern.confidence_threshold:
                return self._create_detection(event_data, pattern, confidence, user_id, user_age)
        except Exception as e:
            self.logger.error(f"Ошибка асинхронной проверки паттерна: {e}")
        return None
    
    async def _calculate_confidence_async(
        self, 
        event_data: Dict[str, Any], 
        pattern: Any
    ) -> float:
        """Асинхронный расчет уверенности"""
        # Имитация асинхронной работы
        await asyncio.sleep(0.0001)
        return self._calculate_pattern_confidence(event_data, pattern)