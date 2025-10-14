# -*- coding: utf-8 -*-
"""
Продолжение улучшенного AutoScalingEngine - приватные методы и вспомогательные функции
"""

    # Приватные методы для валидации
    def _validate_metric(self, metric: MetricData) -> bool:
        """
        Валидация метрики перед обработкой.
        
        Args:
            metric (MetricData): Метрика для валидации
        
        Returns:
            bool: True если метрика валидна, False иначе
        """
        try:
            if not isinstance(metric, MetricData):
                return False
            
            # Дополнительная валидация значений
            if not (0.0 <= metric.value <= 1.0):
                return False
            
            if not metric.service_id or not metric.service_id.strip():
                return False
            
            if not metric.metric_name or not metric.metric_name.strip():
                return False
            
            return True
        except Exception:
            return False

    def _validate_rule(self, rule: ScalingRule) -> bool:
        """
        Валидация правила масштабирования.
        
        Args:
            rule (ScalingRule): Правило для валидации
        
        Returns:
            bool: True если правило валидно, False иначе
        """
        try:
            if not isinstance(rule, ScalingRule):
                return False
            
            if not rule.rule_id or not rule.rule_id.strip():
                return False
            
            if not (0.0 <= rule.threshold <= 1.0):
                return False
            
            if rule.min_replicas < 1 or rule.max_replicas < rule.min_replicas:
                return False
            
            return True
        except Exception:
            return False

    # Кэширование
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Генерация ключа кэша"""
        return f"{prefix}_{hash(str(args))}"

    def _is_cache_valid(self, key: str, ttl_seconds: int = 300) -> bool:
        """Проверка валидности кэша"""
        if key not in self._cache_ttl:
            return False
        return (datetime.now() - self._cache_ttl[key]).total_seconds() < ttl_seconds

    def _invalidate_cache(self, pattern: str) -> None:
        """Инвалидация кэша по паттерну"""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)

    @lru_cache(maxsize=128)
    def _get_cached_metrics(self, service_id: str, hours: int = 1) -> List[MetricData]:
        """
        Кэшированные метрики для сервиса.
        
        Args:
            service_id (str): Идентификатор сервиса
            hours (int): Количество часов для выборки
        
        Returns:
            List[MetricData]: Список метрик
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metrics = []
        
        for key, metric_list in self.metric_history.items():
            if key.startswith(f"{service_id}_"):
                recent_metrics = [
                    m for m in metric_list 
                    if m.timestamp > cutoff_time
                ]
                metrics.extend(recent_metrics)
        
        return metrics

    # Асинхронное логирование
    async def _log_async(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """
        Асинхронное логирование с уровнями.
        
        Args:
            message (str): Сообщение для логирования
            level (LogLevel, optional): Уровень логирования. По умолчанию INFO.
        """
        try:
            log_message = f"[{self.name}] {message}"
            
            if level == LogLevel.DEBUG:
                logging.debug(log_message)
            elif level == LogLevel.INFO:
                logging.info(log_message)
            elif level == LogLevel.WARNING:
                logging.warning(log_message)
            elif level == LogLevel.ERROR:
                logging.error(log_message)
            elif level == LogLevel.CRITICAL:
                logging.critical(log_message)
            
            # Также используем базовый метод логирования
            self.log_activity(message, level.value)
            
        except Exception as e:
            # Fallback к базовому логированию
            self.log_activity(f"Ошибка логирования: {e}", "error")

    # Асинхронные приватные методы
    async def _initialize_ai_models_async(self) -> None:
        """Асинхронная инициализация AI моделей"""
        try:
            await self._log_async("Инициализация AI моделей", LogLevel.INFO)
            
            # Симуляция асинхронной инициализации AI моделей
            await asyncio.sleep(0.1)  # Имитация загрузки
            
            # Здесь должна быть реальная инициализация AI моделей
            self.ml_models = {
                "cpu_predictor": "initialized",
                "memory_predictor": "initialized", 
                "load_predictor": "initialized",
                "anomaly_detector": "initialized",
            }
            
            await self._log_async("AI модели инициализированы", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка инициализации AI моделей: {e}", LogLevel.ERROR)

    async def _load_scaling_rules_async(self) -> None:
        """Асинхронная загрузка правил масштабирования"""
        try:
            await self._log_async("Загрузка правил масштабирования", LogLevel.INFO)
            
            # Создание тестовых правил
            default_rules = [
                ScalingRule(
                    rule_id="cpu_scale_up",
                    name="CPU Scale Up",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_HIGH,
                    threshold=0.8,
                    action=ScalingAction.SCALE_UP,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=300,
                ),
                ScalingRule(
                    rule_id="cpu_scale_down",
                    name="CPU Scale Down",
                    service_id="threat-detection",
                    metric_name="cpu_usage",
                    trigger=ScalingTrigger.CPU_LOW,
                    threshold=0.3,
                    action=ScalingAction.SCALE_DOWN,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=600,
                ),
                ScalingRule(
                    rule_id="memory_scale_up",
                    name="Memory Scale Up",
                    service_id="threat-detection",
                    metric_name="memory_usage",
                    trigger=ScalingTrigger.MEMORY_HIGH,
                    threshold=0.85,
                    action=ScalingAction.SCALE_UP,
                    min_replicas=1,
                    max_replicas=10,
                    cooldown_period=300,
                ),
            ]

            for rule in default_rules:
                if self._validate_rule(rule):
                    self.scaling_rules[rule.rule_id] = rule

            self.scaling_metrics.active_rules = len(self.scaling_rules)
            await self._log_async(f"Загружено {len(default_rules)} правил масштабирования", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка загрузки правил масштабирования: {e}", LogLevel.ERROR)

    async def _start_background_tasks_async(self) -> None:
        """Асинхронный запуск фоновых задач"""
        try:
            await self._log_async("Запуск фоновых задач", LogLevel.INFO)
            
            # Запуск задачи мониторинга метрик
            asyncio.create_task(self._monitoring_task_async())
            
            # Запуск задачи принятия решений
            asyncio.create_task(self._decision_task_async())
            
            await self._log_async("Фоновые задачи запущены", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка запуска фоновых задач: {e}", LogLevel.ERROR)

    async def _stop_background_tasks_async(self) -> None:
        """Асинхронная остановка фоновых задач"""
        try:
            await self._log_async("Остановка фоновых задач", LogLevel.INFO)
            # Фоновые задачи остановятся автоматически при остановке движка
            await self._log_async("Фоновые задачи остановлены", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка остановки фоновых задач: {e}", LogLevel.ERROR)

    async def _get_service_metrics_async(self, service_id: str) -> List[MetricData]:
        """
        Асинхронное получение метрик сервиса.
        
        Args:
            service_id (str): Идентификатор сервиса
        
        Returns:
            List[MetricData]: Список метрик сервиса
        """
        try:
            # Проверяем кэш
            cache_key = self._get_cache_key("service_metrics", service_id)
            if self._is_cache_valid(cache_key, ttl_seconds=60):
                return self._cache.get(cache_key, [])
            
            metrics = []
            for key, metric_list in self.metric_history.items():
                if key.startswith(f"{service_id}_"):
                    # Берем последние метрики
                    recent_metrics = (
                        metric_list[-10:]
                        if len(metric_list) > 10
                        else metric_list
                    )
                    metrics.extend(recent_metrics)
            
            # Кэшируем результат
            self._cache[cache_key] = metrics
            self._cache_ttl[cache_key] = datetime.now()
            
            return metrics
        except Exception as e:
            await self._log_async(f"Ошибка получения метрик сервиса: {e}", LogLevel.ERROR)
            return []

    async def _evaluate_rule_async(
        self, rule: ScalingRule, metrics: List[MetricData]
    ) -> bool:
        """
        Асинхронная оценка правила масштабирования.
        
        Args:
            rule (ScalingRule): Правило для оценки
            metrics (List[MetricData]): Метрики для анализа
        
        Returns:
            bool: True если правило сработало, False иначе
        """
        try:
            # Проверяем период охлаждения
            if rule.last_triggered:
                time_since_trigger = datetime.now() - rule.last_triggered
                if time_since_trigger.total_seconds() < rule.cooldown_period:
                    return False

            # Фильтруем метрики по имени
            rule_metrics = [
                m for m in metrics if m.metric_name == rule.metric_name
            ]
            if not rule_metrics:
                return False

            # Получаем последнее значение
            latest_metric = max(rule_metrics, key=lambda x: x.timestamp)
            current_value = latest_metric.value

            # Проверяем условие
            if (
                rule.trigger == ScalingTrigger.CPU_HIGH
                and current_value > rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.CPU_LOW
                and current_value < rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.MEMORY_HIGH
                and current_value > rule.threshold
            ):
                return True
            elif (
                rule.trigger == ScalingTrigger.MEMORY_LOW
                and current_value < rule.threshold
            ):
                return True

            return False

        except Exception as e:
            await self._log_async(f"Ошибка оценки правила: {e}", LogLevel.ERROR)
            return False

    async def _calculate_confidence_async(
        self, rule: ScalingRule, metrics: List[MetricData]
    ) -> float:
        """
        Асинхронный расчет уверенности в решении.
        
        Args:
            rule (ScalingRule): Правило для расчета
            metrics (List[MetricData]): Метрики для анализа
        
        Returns:
            float: Уверенность от 0.0 до 1.0
        """
        try:
            # Базовая уверенность
            base_confidence = 0.7

            # Увеличиваем уверенность если правило срабатывало много раз
            if rule.trigger_count > 10:
                base_confidence += 0.1

            # Увеличиваем уверенность если метрика стабильна
            rule_metrics = [
                m for m in metrics if m.metric_name == rule.metric_name
            ]
            if len(rule_metrics) > 5:
                values = [m.value for m in rule_metrics[-5:]]
                if statistics.stdev(values) < 0.1:  # Низкая вариативность
                    base_confidence += 0.1

            return min(base_confidence, 1.0)

        except Exception as e:
            await self._log_async(f"Ошибка расчета уверенности: {e}", LogLevel.ERROR)
            return 0.5

    async def _make_final_decision_async(
        self,
        service_id: str,
        actions: List[ScalingAction],
        confidence_scores: List[float],
        triggered_rules: List[str],
        metrics: List[MetricData],
        force_decision: bool = False,
        confidence_threshold: float = 0.7
    ) -> Optional[ScalingDecision]:
        """
        Асинхронное принятие финального решения о масштабировании.
        
        Args:
            service_id (str): Идентификатор сервиса
            actions (List[ScalingAction]): Список действий
            confidence_scores (List[float]): Список уверенности
            triggered_rules (List[str]): Список сработавших правил
            metrics (List[MetricData]): Использованные метрики
            force_decision (bool): Принудительное принятие решения
            confidence_threshold (float): Порог уверенности
        
        Returns:
            Optional[ScalingDecision]: Решение о масштабировании или None
        """
        try:
            if not actions:
                return None

            # Рассчитываем среднюю уверенность
            avg_confidence = (
                statistics.mean(confidence_scores)
                if confidence_scores
                else 0.5
            )

            # Проверяем порог уверенности
            if not force_decision and avg_confidence < confidence_threshold:
                await self._log_async(
                    f"Низкая уверенность {avg_confidence:.2f} < {confidence_threshold}",
                    LogLevel.DEBUG
                )
                return None

            # Определяем доминирующее действие
            action_counts: Dict[ScalingAction, int] = {}
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1

            # Выбираем действие с наибольшим количеством голосов
            final_action = max(action_counts, key=lambda x: action_counts[x])

            # Определяем целевое количество реплик
            current_replicas = 3  # Симуляция текущего количества
            target_replicas = await self._calculate_target_replicas_async(
                service_id, final_action, current_replicas, avg_confidence
            )

            # Создаем решение
            decision = ScalingDecision(
                decision_id=f"decision-{int(time.time() * 1000)}",
                service_id=service_id,
                action=final_action,
                current_replicas=current_replicas,
                target_replicas=target_replicas,
                reason=(
                    f"Triggered by {len(triggered_rules)} rules with "
                    f"{avg_confidence:.2f} confidence"
                ),
                confidence=avg_confidence,
                triggered_rules=triggered_rules,
                timestamp=datetime.now(),
                metrics_used=metrics[-5:],  # Последние 5 метрик
            )

            return decision

        except Exception as e:
            await self._log_async(f"Ошибка принятия финального решения: {e}", LogLevel.ERROR)
            return None

    async def _calculate_target_replicas_async(
        self,
        service_id: str,
        action: ScalingAction,
        current_replicas: int,
        confidence: float,
    ) -> int:
        """
        Асинхронный расчет целевого количества реплик.
        
        Args:
            service_id (str): Идентификатор сервиса
            action (ScalingAction): Действие масштабирования
            current_replicas (int): Текущее количество реплик
            confidence (float): Уверенность в решении
        
        Returns:
            int: Целевое количество реплик
        """
        try:
            if action == ScalingAction.SCALE_UP:
                # Консервативное увеличение
                increase = max(1, int(current_replicas * 0.5 * confidence))
                return min(current_replicas + increase, 10)
            elif action == ScalingAction.SCALE_DOWN:
                # Осторожное уменьшение
                decrease = max(1, int(current_replicas * 0.3 * confidence))
                return max(current_replicas - decrease, 1)
            elif action == ScalingAction.EMERGENCY_SCALE_UP:
                # Экстренное увеличение
                return min(current_replicas * 2, 10)
            elif action == ScalingAction.EMERGENCY_SCALE_DOWN:
                # Экстренное уменьшение
                return max(current_replicas // 2, 1)
            else:
                return current_replicas

        except Exception as e:
            await self._log_async(f"Ошибка расчета целевых реплик: {e}", LogLevel.ERROR)
            return current_replicas

    async def _monitoring_task_async(self) -> None:
        """Асинхронная задача мониторинга метрик"""
        try:
            while self.status == ComponentStatus.RUNNING:
                await asyncio.sleep(self.monitoring_interval)

                # Симуляция сбора метрик
                await self._simulate_metric_collection_async()

        except Exception as e:
            await self._log_async(f"Ошибка задачи мониторинга: {e}", LogLevel.ERROR)

    async def _decision_task_async(self) -> None:
        """Асинхронная задача принятия решений"""
        try:
            while self.status == ComponentStatus.RUNNING:
                await asyncio.sleep(self.decision_interval)

                # Принимаем решения для всех сервисов
                service_ids = set(
                    rule.service_id for rule in self.scaling_rules.values()
                )
                for service_id in service_ids:
                    decision = await self.make_scaling_decision(service_id)
                    if decision:
                        await self._log_async(
                            f"Принято решение о масштабировании {service_id}: "
                            f"{decision.action.value} до "
                            f"{decision.target_replicas} реплик",
                            LogLevel.INFO,
                        )

        except Exception as e:
            await self._log_async(f"Ошибка задачи принятия решений: {e}", LogLevel.ERROR)

    async def _simulate_metric_collection_async(self) -> None:
        """Асинхронная симуляция сбора метрик"""
        try:
            # Симуляция метрик для тестовых сервисов
            services = [
                "threat-detection",
                "performance-optimization",
                "api-gateway",
            ]

            for service_id in services:
                # CPU метрика
                cpu_metric = MetricData(
                    metric_name="cpu_usage",
                    value=random.uniform(0.1, 0.9),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                await self.collect_metric(cpu_metric)

                # Memory метрика
                memory_metric = MetricData(
                    metric_name="memory_usage",
                    value=random.uniform(0.2, 0.8),
                    timestamp=datetime.now(),
                    service_id=service_id,
                    tags={"node": f"node-{random.randint(1, 3)}"},
                )
                await self.collect_metric(memory_metric)

        except Exception as e:
            await self._log_async(f"Ошибка симуляции сбора метрик: {e}", LogLevel.ERROR)

    async def _save_scaling_state_async(self) -> None:
        """Асинхронное сохранение состояния масштабирования"""
        try:
            import os

            os.makedirs("/tmp/aladdin_scaling", exist_ok=True)

            data_to_save = {
                "rules": {
                    k: v.to_dict() for k, v in self.scaling_rules.items()
                },
                "decisions": [
                    d.to_dict() for d in self.scaling_decisions[-100:]
                ],  # Последние 100
                "metrics": self.scaling_metrics.to_dict(),
                "performance_metrics": self.performance_metrics.to_dict(),
                "statistics": self.statistics,
                "saved_at": datetime.now().isoformat(),
            }

            with open(
                "/tmp/aladdin_scaling/last_state.json", "w", encoding="utf-8"
            ) as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            await self._log_async("Состояние масштабирования сохранено", LogLevel.INFO)
        except Exception as e:
            await self._log_async(f"Ошибка сохранения состояния масштабирования: {e}", LogLevel.ERROR)

    # Синхронные методы для обратной совместимости
    def initialize(self) -> bool:
        """
        Синхронная инициализация движка (для обратной совместимости).
        
        Returns:
            bool: True если инициализация успешна, False иначе
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.initialize())
        except RuntimeError:
            # Если нет event loop, создаем новый
            return asyncio.run(self.initialize())

    def stop(self) -> bool:
        """
        Синхронная остановка движка (для обратной совместимости).
        
        Returns:
            bool: True если остановка успешна, False иначе
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.stop())
        except RuntimeError:
            # Если нет event loop, создаем новый
            return asyncio.run(self.stop())

    def add_scaling_rule(self, rule: ScalingRule) -> bool:
        """
        Синхронное добавление правила (для обратной совместимости).
        
        Args:
            rule (ScalingRule): Правило для добавления
        
        Returns:
            bool: True если правило добавлено успешно, False иначе
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.add_scaling_rule(rule))
        except RuntimeError:
            return asyncio.run(self.add_scaling_rule(rule))

    def remove_scaling_rule(self, rule_id: str) -> bool:
        """
        Синхронное удаление правила (для обратной совместимости).
        
        Args:
            rule_id (str): Идентификатор правила
        
        Returns:
            bool: True если правило удалено успешно, False иначе
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.remove_scaling_rule(rule_id))
        except RuntimeError:
            return asyncio.run(self.remove_scaling_rule(rule_id))

    def collect_metric(self, metric: MetricData) -> bool:
        """
        Синхронный сбор метрики (для обратной совместимости).
        
        Args:
            metric (MetricData): Метрика для сбора
        
        Returns:
            bool: True если метрика собрана успешно, False иначе
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.collect_metric(metric))
        except RuntimeError:
            return asyncio.run(self.collect_metric(metric))

    def make_scaling_decision(self, service_id: str) -> Optional[ScalingDecision]:
        """
        Синхронное принятие решения (для обратной совместимости).
        
        Args:
            service_id (str): Идентификатор сервиса
        
        Returns:
            Optional[ScalingDecision]: Решение о масштабировании или None
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.make_scaling_decision(service_id))
        except RuntimeError:
            return asyncio.run(self.make_scaling_decision(service_id))

    def get_scaling_rules(self, service_id: Optional[str] = None) -> List[ScalingRule]:
        """
        Синхронное получение правил (для обратной совместимости).
        
        Args:
            service_id (Optional[str]): Фильтр по сервису
        
        Returns:
            List[ScalingRule]: Список правил
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_scaling_rules(service_id))
        except RuntimeError:
            return asyncio.run(self.get_scaling_rules(service_id))

    def get_scaling_decisions(
        self, service_id: Optional[str] = None, limit: int = 100
    ) -> List[ScalingDecision]:
        """
        Синхронное получение решений (для обратной совместимости).
        
        Args:
            service_id (Optional[str]): Фильтр по сервису
            limit (int): Максимальное количество решений
        
        Returns:
            List[ScalingDecision]: Список решений
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_scaling_decisions(service_id, limit))
        except RuntimeError:
            return asyncio.run(self.get_scaling_decisions(service_id, limit))

    def get_scaling_metrics(self) -> ScalingMetrics:
        """
        Синхронное получение метрик (для обратной совместимости).
        
        Returns:
            ScalingMetrics: Метрики масштабирования
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_scaling_metrics())
        except RuntimeError:
            return asyncio.run(self.get_scaling_metrics())

    def get_engine_status(self) -> Dict[str, Any]:
        """
        Синхронное получение статуса (для обратной совместимости).
        
        Returns:
            Dict[str, Any]: Статус движка
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_engine_status())
        except RuntimeError:
            return asyncio.run(self.get_engine_status())