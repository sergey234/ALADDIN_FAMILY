"""
Пакет дополнительных функций для ALADDIN VPN
Включает Split Tunneling, Multi-hop подключения и автоматическое переподключение
"""

from .auto_reconnect import (
    ALADDINAutoReconnect,
    ConnectionQuality,
    ReconnectConfig,
    ReconnectStats,
    ReconnectStrategy,
)
from .multi_hop import ALADDINMultiHop, HopStatus, HopType, MultiHopChain, VPNHop
from .split_tunneling import (
    ALADDINSplitTunneling,
    RoutingRule,
    SplitTunnelRule,
    TrafficStats,
    TrafficType,
)

__all__ = [
    # Split Tunneling
    "ALADDINSplitTunneling",
    "SplitTunnelRule",
    "RoutingRule",
    "TrafficType",
    "TrafficStats",
    # Multi-hop
    "ALADDINMultiHop",
    "MultiHopChain",
    "VPNHop",
    "HopType",
    "HopStatus",
    # Auto Reconnect
    "ALADDINAutoReconnect",
    "ReconnectConfig",
    "ReconnectStats",
    "ReconnectStrategy",
    "ConnectionQuality",
]
