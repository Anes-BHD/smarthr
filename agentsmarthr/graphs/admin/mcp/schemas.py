from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ToolCallPlan:
    handled: bool
    tool_name: str
    action_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    reason: str = ""
