from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class FamilyRole(str, Enum):
    PARENT = "parent"
    CHILD = "child"
    ELDERLY = "elderly"

class AgeGroup(str, Enum):
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    ELDERLY = "elderly"

class FamilyProfileManager:
    def __init__(self):
        self.families = {}
        self.control_rules = {}

class ChildProtection:
    def __init__(self):
        self.active_filters = {}

class ElderlyProtection:
    def __init__(self):
        self.monitoring_enabled = False

class SecurityEvent(BaseModel):
    id: str
    timestamp: str
    severity: str
    description: str

class ThreatData(BaseModel):
    threat_id: str
    threat_type: str
    level: str

class ScanResult(BaseModel):
    scanned_files: int
    threats_found: int
    duration_seconds: float
