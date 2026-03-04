from typing import Dict, Any, List
class ScalingRule:
    def __init__(self, rule_id, name, metric_name, condition, threshold, severity, cooldown=300):
        self.rule_id = rule_id
        self.name = name
        self.metric_name = metric_name
        self.condition = condition
        self.threshold = threshold
        self.severity = severity
        self.cooldown = cooldown

class AutoScalingEngine:
    def __init__(self, name="AutoScalingEngine"):
        self.name = name
        self.rules = {}
        self.metrics = {}
        self.status = initialized
    
    def initialize(self):
        self.status = running
        return True
    
    def stop(self):
        self.status = stopped
    
    def add_scaling_rule(self, rule):
        self.rules[rule.rule_id] = rule
    
    def get_scaling_rules(self):
        return list(self.rules.values())
    
    def get_engine_status(self):
        return {status: self.status, rules_count: len(self.rules)}
    
    def get_scaling_metrics(self):
        return self.metrics
    
    def collect_metric(self, metric):
        self.metrics[metric.metric_name] = metric.value
        return True

class MetricData:
    def __init__(self, metric_name, value, timestamp=None):
        self.metric_name = metric_name
        self.value = value
        self.timestamp = timestamp

class ScalingAction:
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    
    def __init__(self, action_type, target_value):
        self.action_type = action_type
        self.target_value = target_value

class ScalingTrigger:
    def __init__(self, rule_id, metric_value, threshold):
        self.rule_id = rule_id
        self.metric_value = metric_value
        self.threshold = threshold
